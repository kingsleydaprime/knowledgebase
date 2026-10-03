package resilience

import (
	"context"
	"errors"
	"math"
	"sync/atomic"
	"testing"
	"testing/synctest"
	"time"
)

var (
	healthy  = Load{Ticks: 600, ClientTimeoutTicks: 20, ArrivalsPerTick: map[string]int{"search": 2, "profile": 3}, ServiceTicks: map[string]int{"search": 2, "profile": 1}}
	degraded = Load{Ticks: 600, ClientTimeoutTicks: 20, ArrivalsPerTick: map[string]int{"search": 2, "profile": 3}, ServiceTicks: map[string]int{"search": 50, "profile": 1}}
)

func shared(timeout int) Config {
	return Config{Pools: map[string]string{"search": "shared", "profile": "shared"}, Order: []string{"shared"},
		Sizes: map[string]int{"shared": 50}, QueueLimit: math.MaxInt, DependencyTimeoutTicks: timeout}
}

func TestLittlesLaw(t *testing.T) {
	if WorkersNeeded(20, 0.2)+WorkersNeeded(30, 0.1) != 7 || WorkersNeeded(20, 5) != 100 || WorkersNeeded(20, 3) != 60 || WorkersNeeded(20, 1) != 20 {
		t.Error("little's law")
	}
}

func TestTheSameNumbersAsTypeScript(t *testing.T) {
	if h := Simulate(shared(math.MaxInt), healthy); h["search"].OK != 1196 || h["profile"].OK != 1797 {
		t.Error("healthy", *h["search"], *h["profile"])
	}
	if c := Simulate(shared(math.MaxInt), degraded); c["profile"].OK != 72 || c["profile"].TimedOut != 1668 {
		t.Error("cascade", *c["profile"])
	}
	if c := Simulate(shared(30), degraded); c["profile"].OK != 270 {
		t.Error("3 s timeout", *c["profile"])
	}
	if c := Simulate(shared(10), degraded); c["profile"].OK != 1797 || c["search"].Failed != 1180 {
		t.Error("1 s timeout", *c["profile"], *c["search"])
	}
	walls := Config{Pools: map[string]string{"search": "search", "profile": "profile"}, Order: []string{"search", "profile"},
		Sizes: map[string]int{"search": 20, "profile": 30}, QueueLimit: 10, DependencyTimeoutTicks: 30}
	if c := Simulate(walls, degraded); c["profile"].OK != 1797 || *c["search"] != (Counts{Failed: 380, TimedOut: 190, Rejected: 600, Unfinished: 30}) {
		t.Error("bulkheads", *c["profile"], *c["search"])
	}
}

func TestALimitAShortQueueAndAnImmediateNo(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		b := NewBulkhead(2, 1)
		release := make(chan struct{})
		work := func() error { <-release; return nil }
		for range 3 {
			go b.Run(t.Context(), work)
		}
		synctest.Wait() // every goroutine is now running or blocked
		if err := b.Run(t.Context(), work); !errors.Is(err, ErrBulkheadFull) {
			t.Fatal(err)
		}
		close(release)
	})
}

func TestNeverMoreThanTheLimitAndWaitersGoFirst(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		b := NewBulkhead(1, 1)
		var running, most atomic.Int64
		work := func() error {
			most.Store(max(most.Load(), running.Add(1)))
			time.Sleep(time.Second)
			running.Add(-1)
			return nil
		}
		done := make(chan error, 3)
		go func() { done <- b.Run(t.Context(), work) }() // first
		synctest.Wait()
		go func() { done <- b.Run(t.Context(), work) }() // the waiter
		synctest.Wait()
		time.Sleep(time.Second)                          // first finishes; the place goes straight to the waiter...
		go func() { done <- b.Run(t.Context(), work) }() // ...so the latecomer queues behind it
		for range 3 {
			if err := <-done; err != nil {
				t.Error(err)
			}
		}
		if most.Load() != 1 {
			t.Errorf("%d ran at once in a bulkhead of one", most.Load())
		}
	})
}

func TestACallerWhoStopsWaitingLeavesTheQueue(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		b := NewBulkhead(1, 1)
		release := make(chan struct{})
		go b.Run(t.Context(), func() error { <-release; return nil })
		synctest.Wait()
		ctx, cancel := context.WithTimeout(t.Context(), 2*time.Second) // the client gives up after 2 s
		defer cancel()
		if err := b.Run(ctx, func() error { return nil }); !errors.Is(err, context.DeadlineExceeded) || b.waiting.Load() != 0 {
			t.Error(err, b.waiting.Load())
		}
		close(release)
	})
}
