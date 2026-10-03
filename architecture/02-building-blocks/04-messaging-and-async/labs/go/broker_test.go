package messaging

import (
	"slices"
	"strconv"
	"strings"
	"sync/atomic"
	"testing"
	"testing/synctest"
)

func broker(now *int64) *Broker {
	return NewBroker(func() int64 { return *now }, 30_000, 3)
}

func TestQueueGivesEachMessageToOneConsumerTopicCopiesIt(t *testing.T) {
	var now int64
	b := broker(&now)
	b.Subscribe("orders", "invoices")
	b.Subscribe("orders", "analytics")
	b.Publish("orders", "order 1", "")
	b.Publish("orders", "order 2", "")
	first, _ := b.Receive("invoices")
	second, _ := b.Receive("invoices")
	_, more := b.Receive("invoices")
	if first.Body != "order 1" || second.Body != "order 2" || more {
		t.Fatal(first, second, more)
	}
	a1, _ := b.Receive("analytics")
	a2, _ := b.Receive("analytics")
	b.Publish("refunds", "refund 1", "")
	if a1.Body != "order 1" || a2.Body != "order 2" || b.Depth("invoices")+b.Depth("analytics") != 4 {
		t.Fatal(a1, a2)
	}
}

func TestUnacknowledgedComesBackThenGoesToTheDeadLetterQueue(t *testing.T) {
	var now int64
	b := broker(&now)
	b.Subscribe("orders", "invoices")
	b.Publish("orders", "order 1", "")
	if d, _ := b.Receive("invoices"); d.Attempt != 1 {
		t.Fatal(d)
	}
	if _, ok := b.Receive("invoices"); ok {
		t.Fatal("delivered while hidden")
	}
	for _, c := range []struct {
		now     int64
		attempt int
	}{{30_000, 2}, {60_000, 3}} {
		now = c.now
		if d, _ := b.Receive("invoices"); d.Attempt != c.attempt {
			t.Fatal(d)
		}
	}
	now = 90_000
	if _, ok := b.Receive("invoices"); ok || !slices.Equal(b.DeadLetters("invoices"), []string{"order 1"}) || b.Depth("invoices") != 0 {
		t.Fatal(b.DeadLetters("invoices"))
	}
}

func TestCrashBeforeAckChargesTwiceUnlessIdempotent(t *testing.T) {
	for _, safe := range []bool{false, true} {
		var now int64
		b := broker(&now)
		b.Subscribe("orders", "payments")
		b.Publish("orders", "charge £40 for order 1", "")
		charges := 0
		charge := func(string) { charges++ }
		handle := func(d Delivery) { charge(d.Body) }
		if safe {
			once := Idempotent(charge, map[string]bool{})
			handle = func(d Delivery) { once(d) }
		}
		d, _ := b.Receive("payments")
		handle(d) // charged, then the consumer crashes before acknowledging
		now = 30_000
		again, _ := b.Receive("payments")
		handle(again)
		b.Ack("payments", again.ID)
		if want := map[bool]int{false: 2, true: 1}[safe]; charges != want {
			t.Fatalf("safe=%v: %d charges", safe, charges)
		}
	}
}

func TestAQueueAbsorbsASaleSpike(t *testing.T) {
	spike := append(slices.Repeat([]int{300}, 10), slices.Repeat([]int{20}, 50)...)
	if got := LevelLoad(spike, 100); got != (Levelled{2_000, 2_000, 2_000, 35, 20}) {
		t.Fatal(got)
	}
	if got := LevelLoad(spike, 200); got.PeakDepth != 1_000 || got.ClearedAfterSeconds != 16 || got.MaxWaitSeconds != 5 {
		t.Fatal(got)
	}
}

func TestRedeliveryReordersAPartitionKeepsOrderANewGroupReplays(t *testing.T) {
	var now int64
	b := broker(&now)
	b.Subscribe("orders", "shipping")
	for _, e := range []string{"created", "paid", "shipped"} {
		b.Publish("orders", "order 7 "+e, "order-7")
	}
	var seen []string
	for _, fail := range []bool{false, true, false} {
		d, _ := b.Receive("shipping")
		if !fail {
			seen = append(seen, d.Body)
			b.Ack("shipping", d.ID)
		}
	}
	now = 30_000
	paid, _ := b.Receive("shipping")
	seen = append(seen, paid.Body)
	if !slices.Equal(seen, []string{"order 7 created", "order 7 shipped", "order 7 paid"}) {
		t.Fatal(seen)
	}

	log := NewPartitionedLog(4)
	for _, e := range []string{"created", "paid", "shipped"} {
		log.Append("order-7", "order 7 "+e)
	}
	p := PartitionFor("order-7", 4)
	var inOrder []string
	failedOnce := false
	for m, ok := log.Poll("shipping", p); ok; m, ok = log.Poll("shipping", p) {
		if strings.HasSuffix(m, "paid") && !failedOnce {
			failedOnce = true // no commit: the same message comes back
			continue
		}
		inOrder = append(inOrder, m)
		log.Commit("shipping", p)
	}
	first, _ := log.Poll("analytics", p)
	if !slices.Equal(inOrder, []string{"order 7 created", "order 7 paid", "order 7 shipped"}) || first != "order 7 created" {
		t.Fatal(inOrder, first)
	}
}

func TestAKeyAlwaysLandsInTheSamePartition(t *testing.T) {
	counts := make([]int, 4)
	for i := range 10_000 {
		counts[PartitionFor("order-"+strconv.Itoa(i), 4)]++
	}
	for _, n := range counts {
		if n < 2_300 || n > 2_700 {
			t.Fatal(counts)
		}
	}
}

func TestABufferedChannelPushesBack(t *testing.T) {
	q := make(chan int, 3)
	var got []bool
	for n := 1; n <= 4; n++ {
		got = append(got, TryPut(q, n))
	}
	if !slices.Equal(got, []bool{true, true, true, false}) || <-q != 1 || <-q != 2 || <-q != 3 {
		t.Fatal(got)
	}
	synctest.Test(t, func(t *testing.T) {
		q := make(chan int, 3) // made inside the bubble, so synctest can tell when a send on it is blocked
		var puts atomic.Int32
		done := make(chan struct{})
		go func() {
			for n := 1; n <= 5; n++ {
				q <- n // blocks while the channel is full
				puts.Add(1)
			}
			close(done)
		}()
		synctest.Wait() // the producer is blocked
		if puts.Load() != 3 {
			t.Fatal("puts before any take:", puts.Load())
		}
		<-q
		synctest.Wait()
		if puts.Load() != 4 {
			t.Fatal("puts after one take:", puts.Load())
		}
		for range 4 {
			<-q
		}
		<-done
	})
}
