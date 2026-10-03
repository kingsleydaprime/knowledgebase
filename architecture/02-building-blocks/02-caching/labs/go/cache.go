// Package caching: a cache in front of a slow store. An LRU cache with expiry, cache-aside with request
// coalescing, and the arithmetic that says how much a cache takes off the database.
// The same numbers as the TypeScript lab.
package caching

import (
	"container/list"
	"errors"
	"math"
	"slices"
	"sync"
	"sync/atomic"
)

type entry[V any] struct {
	key     string
	value   V
	expires float64
}

// LruCache holds at most max entries, evicting the least recently used. Safe for concurrent use.
// container/list keeps the order; the map finds a key's place in the list in O(1).
type LruCache[V any] struct {
	mu      sync.Mutex
	max     int
	now     func() float64 // milliseconds
	order   *list.List     // front: most recently used
	entries map[string]*list.Element
}

func NewLruCache[V any](max int, now func() float64) (*LruCache[V], error) {
	if max < 1 {
		return nil, errors.New("a cache needs room for at least one entry")
	}
	return &LruCache[V]{max: max, now: now, order: list.New(), entries: map[string]*list.Element{}}, nil
}

func (c *LruCache[V]) Get(key string) (V, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	var zero V
	el, ok := c.entries[key]
	if !ok {
		return zero, false
	}
	e := el.Value.(*entry[V])
	if c.now() >= e.expires {
		c.order.Remove(el)
		delete(c.entries, key)
		return zero, false
	}
	c.order.MoveToFront(el)
	return e.value, true
}

func (c *LruCache[V]) Set(key string, value V, ttlMs float64) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if el, ok := c.entries[key]; ok {
		c.order.Remove(el)
	}
	c.entries[key] = c.order.PushFront(&entry[V]{key, value, c.now() + ttlMs})
	if c.order.Len() > c.max {
		oldest := c.order.Back()
		c.order.Remove(oldest)
		delete(c.entries, oldest.Value.(*entry[V]).key)
	}
}

func (c *LruCache[V]) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if el, ok := c.entries[key]; ok {
		c.order.Remove(el)
		delete(c.entries, key)
	}
}

// Keys lists least recently used first.
func (c *LruCache[V]) Keys() []string {
	c.mu.Lock()
	defer c.mu.Unlock()
	var keys []string
	for el := c.order.Back(); el != nil; el = el.Prev() {
		keys = append(keys, el.Value.(*entry[V]).key)
	}
	return keys
}

// call is one load in progress; waiters block on done. It's the idea behind golang.org/x/sync/singleflight.
type call[V any] struct {
	done  chan struct{}
	value V
	err   error
}

// CacheAside checks the cache; on a miss it loads and fills it. With Coalesce, concurrent misses share one load.
type CacheAside[V any] struct {
	Cache        *LruCache[V]
	Load         func(key string) (V, error)
	TTLMs        float64
	Coalesce     bool
	hits, misses atomic.Int64
	mu           sync.Mutex
	inFlight     map[string]*call[V]
}

func (a *CacheAside[V]) Hits() int64   { return a.hits.Load() }
func (a *CacheAside[V]) Misses() int64 { return a.misses.Load() }

func (a *CacheAside[V]) Get(key string) (V, error) {
	if v, ok := a.Cache.Get(key); ok {
		a.hits.Add(1)
		return v, nil
	}
	a.misses.Add(1)
	if !a.Coalesce {
		return a.loadAndFill(key)
	}
	a.mu.Lock()
	if c, ok := a.inFlight[key]; ok {
		a.mu.Unlock()
		<-c.done // someone is already loading this key: wait for their answer
		return c.value, c.err
	}
	if a.inFlight == nil {
		a.inFlight = map[string]*call[V]{}
	}
	c := &call[V]{done: make(chan struct{})}
	a.inFlight[key] = c
	a.mu.Unlock()
	c.value, c.err = a.loadAndFill(key)
	a.mu.Lock()
	delete(a.inFlight, key) // a failed load isn't kept: the next miss retries
	a.mu.Unlock()
	close(c.done)
	return c.value, c.err
}

func (a *CacheAside[V]) loadAndFill(key string) (V, error) {
	v, err := a.Load(key)
	if err == nil {
		a.Cache.Set(key, v, a.TTLMs)
	}
	return v, err
}

// Write saves to the store first, then deletes the cached copy.
func (a *CacheAside[V]) Write(key string, value V, save func(string, V) error) error {
	if err := save(key, value); err != nil {
		return err
	}
	a.Cache.Delete(key)
	return nil
}

func HitRatio(hits, misses int64) float64 { return float64(hits) / float64(hits+misses) }

func AverageReadMs(ratio, cacheMs, storeMs float64) float64 { return cacheMs + (1-ratio)*storeMs }

func StoreReadsPerSecond(readsPerSecond, ratio float64) float64 { return readsPerSecond * (1 - ratio) }

func Jittered(ttlMs, spread float64, random func() float64) float64 {
	return ttlMs * (1 - spread + 2*spread*random())
}

// Zipf picks key k in proportion to 1/(k+1)^s.
func Zipf(keys int, s float64, random func() float64) func() int {
	cumulative := make([]float64, keys)
	total := 0.0
	for k := range keys {
		total += 1 / math.Pow(float64(k+1), s)
		cumulative[k] = total
	}
	return func() int {
		i, _ := slices.BinarySearch(cumulative, random()*total) // the first total at or above the target
		return i
	}
}

// Seeded is mulberry32, the same generator as week 1's lab.
func Seeded(seed uint32) func() float64 {
	a := seed
	return func() float64 {
		a += 0x6d2b79f5
		t := (a ^ a>>15) * (a | 1)
		t ^= t + (t^t>>7)*(t|61)
		return float64(t^t>>14) / 4294967296
	}
}
