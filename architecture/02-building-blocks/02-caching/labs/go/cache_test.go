package caching

import (
	"fmt"
	"math"
	"slices"
	"sync"
	"testing"
	"testing/synctest"
	"time"
)

type clock struct {
	mu  sync.Mutex
	now float64
}

func (c *clock) Now() float64   { c.mu.Lock(); defer c.mu.Unlock(); return c.now }
func (c *clock) Set(ms float64) { c.mu.Lock(); defer c.mu.Unlock(); c.now = ms }

func TestFullLruCacheEvictsTheEntryUsedLongestAgo(t *testing.T) {
	c, _ := NewLruCache[string](3, (&clock{}).Now)
	for _, k := range []string{"a", "b", "c"} {
		c.Set(k, k, 1_000)
	}
	c.Get("a")
	c.Set("d", "d", 1_000)
	if _, ok := c.Get("b"); !slices.Equal(c.Keys(), []string{"c", "a", "d"}) || ok {
		t.Fatal(c.Keys())
	}
}

func TestAnEntryExpiresAfterItsTTL(t *testing.T) {
	clk := &clock{}
	c, _ := NewLruCache[int](10, clk.Now)
	c.Set("price:42", 10, 60_000)
	clk.Set(59_999)
	if v, ok := c.Get("price:42"); !ok || v != 10 {
		t.Fatal(v, ok)
	}
	clk.Set(60_000)
	if _, ok := c.Get("price:42"); ok {
		t.Fatal("served after its TTL")
	}
}

func TestCacheAsideFirstReadMissesTheRestHit(t *testing.T) {
	loads := 0
	c, _ := NewLruCache[string](100, (&clock{}).Now)
	products := &CacheAside[string]{Cache: c, TTLMs: 60_000, Load: func(string) (string, error) { loads++; return "kettle", nil }}
	for range 5 {
		if v, _ := products.Get("product:7"); v != "kettle" {
			t.Fatal(v)
		}
	}
	if loads != 1 || products.Hits() != 4 || products.Misses() != 1 || HitRatio(products.Hits(), products.Misses()) != 0.8 {
		t.Fatal(loads, products.Hits(), products.Misses())
	}
}

func TestTheHitRatioDecidesWhatTheDatabaseSees(t *testing.T) {
	var reads, avg []string
	for _, h := range []float64{0.8, 0.9, 0.99} {
		reads = append(reads, fmt.Sprintf("%.0f", StoreReadsPerSecond(5_000, h)))
	}
	for _, h := range []float64{0, 0.8, 0.99} {
		avg = append(avg, fmt.Sprintf("%.1f", AverageReadMs(h, 1, 20)))
	}
	if !slices.Equal(reads, []string{"1000", "500", "50"}) || !slices.Equal(avg, []string{"21.0", "5.0", "1.2"}) || StoreReadsPerSecond(5_000, 0) != 5_000 {
		t.Fatal(reads, avg)
	}
}

func TestSkewedTrafficASmallCacheAnswersMostReads(t *testing.T) {
	var ratios []string
	for _, size := range []int{500, 2_500, 5_000, 10_000} {
		next := Zipf(50_000, 1, Seeded(1))
		c, _ := NewLruCache[bool](size, (&clock{}).Now)
		var hits, misses int64
		for i := range 200_000 {
			key := fmt.Sprint(next())
			_, hit := c.Get(key)
			if !hit {
				c.Set(key, true, math.Inf(1))
			}
			if i >= 50_000 {
				if hit {
					hits++
				} else {
					misses++
				}
			}
		}
		ratios = append(ratios, fmt.Sprintf("%.2f", HitRatio(hits, misses)))
	}
	if !slices.Equal(ratios, []string{"0.48", "0.65", "0.72", "0.80"}) {
		t.Fatal(ratios)
	}
}

func TestAStampedeUnlessMissesShareOneLoad(t *testing.T) {
	for _, coalesce := range []bool{false, true} {
		synctest.Test(t, func(t *testing.T) { // a fake clock: the 5 ms sleep takes no real time
			clk := &clock{}
			var mu sync.Mutex
			loads := 0
			c, _ := NewLruCache[string](100, clk.Now)
			products := &CacheAside[string]{Cache: c, TTLMs: 60_000, Coalesce: coalesce, Load: func(string) (string, error) {
				mu.Lock()
				loads++
				mu.Unlock()
				time.Sleep(5 * time.Millisecond) // fake time moves only when every goroutine is blocked: all 100 miss first
				return "kettle", nil
			}}
			products.Get("product:7")
			clk.Set(60_000)
			loads = 0
			var wg sync.WaitGroup
			for range 100 {
				wg.Go(func() {
					if v, _ := products.Get("product:7"); v != "kettle" {
						t.Error(v)
					}
				})
			}
			wg.Wait()
			if want := map[bool]int{false: 100, true: 1}[coalesce]; loads != want {
				t.Fatalf("coalesce %v: %d loads, want %d", coalesce, loads, want)
			}
		})
	}
}

func TestDeleteOnWriteCanStillLeaveAStaleValue(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		clk := &clock{}
		var mu sync.Mutex
		db := map[string]int{"price:42": 10}
		slowRead := make(chan struct{})
		first := true
		c, _ := NewLruCache[int](100, clk.Now)
		prices := &CacheAside[int]{Cache: c, TTLMs: 60_000, Load: func(key string) (int, error) {
			mu.Lock()
			value, wait := db[key], first // the read happens now...
			first = false
			mu.Unlock()
			if wait {
				<-slowRead // ...but the answer is delayed
			}
			return value, nil
		}}
		reader := make(chan int)
		go func() { v, _ := prices.Get("price:42"); reader <- v }()
		synctest.Wait() // the reader has read 10 and is blocked
		prices.Write("price:42", 12, func(k string, v int) error { mu.Lock(); db[k] = v; mu.Unlock(); return nil })
		close(slowRead)
		if v := <-reader; v != 10 {
			t.Fatal(v)
		}
		if v, _ := prices.Get("price:42"); v != 10 {
			t.Fatal("expected the stale 10, got", v)
		}
		clk.Set(60_000)
		if v, _ := prices.Get("price:42"); v != 12 {
			t.Fatal(v)
		}
	})
}

func TestJitterSpreadsOutExpiry(t *testing.T) {
	random := Seeded(3)
	perSecond := map[int]int{}
	lo, hi := math.Inf(1), math.Inf(-1)
	for range 1_000 {
		ms := Jittered(60_000, 0.1, random)
		lo, hi = min(lo, ms), max(hi, ms)
		perSecond[int(ms/1_000)]++
	}
	busiest := 0
	for _, n := range perSecond {
		busiest = max(busiest, n)
	}
	if lo < 54_000 || hi > 66_000 || busiest >= 120 {
		t.Fatal(lo, hi, busiest)
	}
}
