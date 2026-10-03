# Caching in Other Languages

> **[Intermediate]** · A companion to [[architecture/02-building-blocks/02-caching/index|caching]], which builds an LRU cache with expiry, puts it in front of a slow store with cache-aside, measures hit ratios under skewed traffic, and plays out the stale-read race and the stampede. This page does the same in Python, Go, Java, Rust and C#, with the same numbers in every language. Each language has a different tool for keeping entries in order of use. Two things change more: coalescing, which means getting a hundred concurrent misses to share one load, and testing a race without the test itself being flaky.

## Before you start

You can already:

- Explain cache-aside, LRU eviction, TTLs, the stale-read race and the stampede → [[architecture/02-building-blocks/02-caching/index|the main lesson]].
- Start concurrent work in your language: tasks, goroutines or threads.

After this lesson you will be able to:

1. Name the data structure your language offers for an LRU cache, and the library you'd use instead in production.
2. Make concurrent misses for one key share a single load, with your language's tool for "one caller does the work, the rest wait for its answer".
3. Test a race deterministically, by holding one side at a gate until the other side has done its part.

## The kid version

A class shares one dictionary on the teacher's desk. When a word is asked for, the first child to go to the library to look it up shouts "I'm getting it!", and everyone else who wants the same word waits for them instead of all running to the library. Each class organises the waiting differently. In one, children write their names on a list. In another, the first child is given a ticket that the others watch. In a third, the dictionary itself has a "being fetched" page that makes everyone wait.

**Where the analogy stops working.** In a classroom you'd see two children set off at once. In a program, two threads can both check "is anyone fetching?" in the same microsecond and both see "no", unless checking and claiming happen as one indivisible step. Each language's tool exists to make that one step.

## 1. The tools, by ecosystem

| Language | Ordered map for LRU | Production cache | One load for concurrent misses | Shared cache client |
|---|---|---|---|---|
| TypeScript | `Map` (insertion order) | `lru-cache` | a map of promises (the main lesson) | `ioredis`, `node-redis` |
| Python | `OrderedDict` (`move_to_end`) | `functools.lru_cache`, `cachetools` | a dict of futures, with `asyncio.shield` | `redis-py` |
| Go | `container/list` plus a map | `hashicorp/golang-lru`, `ristretto` | `golang.org/x/sync/singleflight` | `go-redis` |
| Java | `LinkedHashMap` in access order | **Caffeine** | `ConcurrentHashMap` of `CompletableFuture` (Caffeine does this for you) | Lettuce, Jedis |
| Rust | none in std | `lru`, **`moka`** | `OnceLock` per key (moka's `get_with` does this) | `redis` crate |
| C# | `LinkedList` plus `Dictionary` | `MemoryCache`, `HybridCache` | `ConcurrentDictionary` of `Lazy<Task>` (HybridCache does this) | StackExchange.Redis |

The libraries in bold coalesce misses for you, and Caffeine and moka use eviction rules smarter than LRU, based on how often keys are used as well as how recently. .NET's `MemoryCache` has no LRU: when it's over its size limit it compacts by priority and age. `HybridCache`, new in .NET 9, adds coalescing and a shared second level such as Redis. C and C++ would build LRU from a list and a hash map (`std::list` with `splice` plus `std::unordered_map` in C++), but caches in front of databases are rarely written in either, so they have no lab here.

## 2. What changes between languages

### Keeping entries in order of use

LRU needs two things at once: find an entry by key quickly, and know which entry was used longest ago. Every language solves it with a hash map plus something ordered:

- **Python's** `OrderedDict` and **Java's** `LinkedHashMap` are both: a hash map whose entries are also on a linked list. `move_to_end` and an access-ordered `LinkedHashMap` move a key to the back in constant time. Java's `removeEldestEntry` evicts as you insert. In access order, even `get` changes the list, so reads need the lock too.
- **Go** and **C#** pair a map with a doubly linked list (`container/list`, `LinkedList<T>`), storing each key's list node in the map so it can be moved without a search.
- **Rust's** standard library has no linked list you'd use for this, so the lab pairs a `HashMap` with a `BTreeMap` from "time of last use" to key: the first entry of the `BTreeMap` is the least recently used. That's O(log n) rather than O(1), which is fine for a lab; the `lru` crate gives O(1).

### One load for many misses

The main lesson keeps a map of loads in progress, and a miss that finds one waits for it. In JavaScript that's safe without a lock, because nothing else runs between "is it in the map?" and "put mine in". With threads, two callers can both see "not there" and both start a load, so checking and claiming must be one step:

- **Go** locks a mutex around the map, and waiters block on a channel that's closed when the load finishes. That's the design of `x/sync/singleflight`.
- **Java's** `putIfAbsent` on a `ConcurrentHashMap` is atomic: exactly one caller's `CompletableFuture` goes in, and everyone else gets that one back and waits on it with `join`.
- **Rust's** `OnceLock::get_or_init` runs exactly one initialiser even when many threads call it at once; the others block until it's done. The lab keeps one `OnceLock` per key in a map.
- **C#'s** `ConcurrentDictionary.GetOrAdd` may build more than one value under a race, but stores only one. Wrapping the load in `Lazy<Task<V>>` means a `Lazy` that loses the race is thrown away without ever starting.
- **Python's** asyncio is single-threaded like JavaScript, so a dict of futures needs no lock. It adds `asyncio.shield`, so that one waiter being cancelled doesn't cancel the load everyone else is waiting for.

### Testing a race without a flaky test

The stampede test needs 100 callers to miss *before* the first load finishes. With JavaScript's and Python's event loops, that happens naturally: every caller runs up to its first `await` before any load completes. With threads, it depends on scheduling: on a fast machine, the first load can finish before the hundredth thread even starts, and the test passes or fails by luck. So:

- **Go** runs the test inside `testing/synctest`, where time is fake and moves only when every goroutine is blocked. The load's `time.Sleep` therefore can't end until all 100 goroutines have missed and are waiting.
- **Java**, **Rust** and **C#** hold each load at a gate (a `CountDownLatch`, a hand-made `Mutex` and `Condvar` gate, a `TaskCompletionSource`) and open it only once the miss counter reaches 100. To make that safe, coalescing counts a miss *after* joining the load in progress, so 100 misses means 100 callers are already waiting.

The stale-read race uses the same idea: the reader signals once it has read 10 and then waits at a gate, so the write is guaranteed to land in the gap.

### "Forever" without overflow

The Zipf test caches entries with no expiry. TypeScript passes `Infinity`, and its clock is a float. Java and C# use `long` milliseconds, where `now + Long.MAX_VALUE` wraps to a negative number, so every entry would be instantly expired. They treat `MAX_VALUE` as "never". Rust uses `saturating_add`, which stops at the maximum instead of wrapping.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| LRU of 3 after a, b, c, read a, add d | keys c, a, d; b evicted |
| TTL of 60 s | served at 59,999 ms, a miss at 60,000 |
| five reads through cache-aside | 1 load, 4 hits, 1 miss: hit ratio 0.8 |
| database reads a second at hit ratios 0.8, 0.9, 0.99 | 1,000, 500, 50 |
| average read at hit ratios 0, 0.8, 0.99 | 21.0, 5.0, 1.2 ms |
| Zipf hit ratio, caches of 1, 5, 10, 20% | 0.48, 0.65, 0.72, 0.80 |
| 100 concurrent misses for one expired key | 100 loads, or 1 with coalescing |
| the stale-read race | 10 cached after the write of 12; 12 after the TTL |
| 1,000 TTLs of 60 s ± 10% | all within 54–66 s, under 120 in any one second |

## Terms used in this lesson

1. **Coalescing**: This is also known as **single flight**. It means letting concurrent requests for the same thing share one piece of work and its result.
2. **Atomic operation**: This is an operation that other threads see as either not started or finished, never half-done. "Insert this key if it's absent" must be atomic for coalescing to work.
3. **Future**: This is also called a **promise** or a **task**. It's an object standing for a result that isn't ready yet, which other code can wait on.
4. **Gate**: In a test, this is a one-time signal that blocked threads wait at until the test opens it, so the test controls the order events happen in.
5. **Fake clock**: This is a test clock that moves only when the test, or the test runtime, moves it, so waits and timeouts happen in the same order on every run.
6. **Saturating arithmetic**: This is arithmetic that stops at the largest or smallest value instead of wrapping round.

## 4. Python

`LruCache` is an `OrderedDict` with `move_to_end` and `popitem(last=False)`. The clock defaults to `time.monotonic`, which never jumps back when the system clock is changed. `CacheAside` is async, like TypeScript's; coalescing stores the load as a task, removes it in a done callback, and has every waiter await it through `asyncio.shield`. A cached value of `None` would read as a miss, which is a limit worth knowing. The stampede test uses `asyncio.gather`, and the race test uses an `asyncio.Event` as the gate.

```python
"""A cache in front of a slow store: an LRU cache with expiry, cache-aside with request coalescing, and the
arithmetic that says how much a cache takes off the database. The same numbers as the TypeScript lab."""
import asyncio
import bisect
import math
import time
from collections import OrderedDict
from typing import Awaitable, Callable, Generic, TypeVar

V = TypeVar("V")
MASK = 0xFFFFFFFF


class LruCache(Generic[V]):
    """At most `max_entries`; evicts the least recently used. OrderedDict keeps order and moves a key in O(1)."""

    def __init__(self, max_entries: int, now: Callable[[], float] = lambda: time.monotonic() * 1000):
        if max_entries < 1:
            raise ValueError("a cache needs room for at least one entry")
        self._max = max_entries
        self._now = now
        self._entries: OrderedDict[str, tuple[V, float]] = OrderedDict()  # value, expiry time

    def get(self, key: str) -> V | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        value, expires = entry
        if self._now() >= expires:
            del self._entries[key]
            return None
        self._entries.move_to_end(key)  # now the most recently used
        return value

    def set(self, key: str, value: V, ttl_ms: float) -> None:
        self._entries[key] = (value, self._now() + ttl_ms)
        self._entries.move_to_end(key)
        if len(self._entries) > self._max:
            self._entries.popitem(last=False)  # the front is the least recently used

    def delete(self, key: str) -> None:
        self._entries.pop(key, None)

    def keys(self) -> list[str]:
        return list(self._entries)


class CacheAside(Generic[V]):
    """Check the cache; on a miss, load and fill it. With coalesce, concurrent misses share one load."""

    def __init__(self, cache: LruCache[V], load: Callable[[str], Awaitable[V]], ttl_ms: float, coalesce: bool = False):
        self._cache, self._load, self._ttl_ms, self._coalesce = cache, load, ttl_ms, coalesce
        self._in_flight: dict[str, asyncio.Future[V]] = {}
        self.hits = self.misses = 0

    async def get(self, key: str) -> V:
        cached = self._cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        if self._coalesce:
            pending = self._in_flight.get(key)
            if pending is not None:
                return await asyncio.shield(pending)  # shield: one waiter giving up doesn't cancel everyone's load
            task = asyncio.ensure_future(self._load_and_fill(key))
            self._in_flight[key] = task
            task.add_done_callback(lambda _: self._in_flight.pop(key, None))
            return await asyncio.shield(task)
        return await self._load_and_fill(key)

    async def _load_and_fill(self, key: str) -> V:
        value = await self._load(key)
        self._cache.set(key, value, self._ttl_ms)
        return value

    async def write(self, key: str, value: V, save: Callable[[str, V], Awaitable[None]]) -> None:
        await save(key, value)
        self._cache.delete(key)


def hit_ratio(hits: int, misses: int) -> float:
    return hits / (hits + misses)


def average_read_ms(ratio: float, cache_ms: float, store_ms: float) -> float:
    return cache_ms + (1 - ratio) * store_ms


def store_reads_per_second(reads_per_second: float, ratio: float) -> float:
    return reads_per_second * (1 - ratio)


def jittered(ttl_ms: float, spread: float, random: Callable[[], float]) -> float:
    return ttl_ms * (1 - spread + 2 * spread * random())


def zipf(keys: int, s: float, random: Callable[[], float]) -> Callable[[], int]:
    """Key k is requested in proportion to 1/(k+1)^s."""
    cumulative, total = [], 0.0
    for k in range(keys):
        total += 1 / (k + 1) ** s
        cumulative.append(total)
    return lambda: bisect.bisect_left(cumulative, random() * total)  # the first index whose total reaches the target


def seeded(seed: int) -> Callable[[], float]:
    """mulberry32, the same generator as week 1's lab."""
    a = seed & MASK

    def next_random() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & MASK
        t = ((a ^ (a >> 15)) * (a | 1)) & MASK
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & MASK)) & MASK
        return (t ^ (t >> 14)) / 4294967296

    return next_random


INF = math.inf
```

```python
import asyncio
import unittest

from cache import INF, CacheAside, LruCache, average_read_ms, hit_ratio, jittered, seeded, store_reads_per_second, zipf


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class Caching(unittest.IsolatedAsyncioTestCase):
    def test_a_full_lru_cache_evicts_the_entry_used_longest_ago(self):
        cache = LruCache(3, Clock())
        for key in "abc":
            cache.set(key, key.upper(), 1_000)
        cache.get("a")
        cache.set("d", "D", 1_000)
        self.assertEqual(cache.keys(), ["c", "a", "d"])
        self.assertIsNone(cache.get("b"))

    def test_an_entry_expires_after_its_ttl(self):
        clock = Clock()
        cache = LruCache(10, clock)
        cache.set("price:42", 10, 60_000)
        clock.now = 59_999
        self.assertEqual(cache.get("price:42"), 10)
        clock.now = 60_000
        self.assertIsNone(cache.get("price:42"))

    async def test_cache_aside_first_read_misses_the_rest_hit(self):
        loads = 0

        async def load(key):
            nonlocal loads
            loads += 1
            return "kettle"

        products = CacheAside(LruCache(100, Clock()), load, ttl_ms=60_000)
        for _ in range(5):
            self.assertEqual(await products.get("product:7"), "kettle")
        self.assertEqual((loads, products.hits, products.misses), (1, 4, 1))
        self.assertEqual(hit_ratio(products.hits, products.misses), 0.8)

    def test_the_hit_ratio_decides_what_the_database_sees(self):
        self.assertEqual([round(store_reads_per_second(5_000, h)) for h in [0.8, 0.9, 0.99]], [1_000, 500, 50])
        self.assertEqual([f"{average_read_ms(h, 1, 20):.1f}" for h in [0, 0.8, 0.99]], ["21.0", "5.0", "1.2"])
        self.assertEqual(store_reads_per_second(5_000, 0), 5_000)

    def test_skewed_traffic_a_small_cache_answers_most_reads(self):
        ratios = []
        for size in [500, 2_500, 5_000, 10_000]:
            next_key = zipf(50_000, 1, seeded(1))
            cache, hits, misses = LruCache(size, Clock()), 0, 0
            for i in range(200_000):
                key = str(next_key())
                hit = cache.get(key) is not None
                if not hit:
                    cache.set(key, True, INF)
                if i >= 50_000:
                    hits, misses = hits + hit, misses + (not hit)
            ratios.append(f"{hit_ratio(hits, misses):.2f}")
        self.assertEqual(ratios, ["0.48", "0.65", "0.72", "0.80"])

    async def test_a_stampede_unless_misses_share_one_load(self):
        for coalesce in [False, True]:
            clock, loads = Clock(), 0

            async def load(key):
                nonlocal loads
                loads += 1
                await asyncio.sleep(0.005)
                return "kettle"

            products = CacheAside(LruCache(100, clock), load, ttl_ms=60_000, coalesce=coalesce)
            await products.get("product:7")
            clock.now, loads = 60_000, 0
            names = await asyncio.gather(*(products.get("product:7") for _ in range(100)))
            self.assertTrue(all(n == "kettle" for n in names))
            self.assertEqual(loads, 1 if coalesce else 100)

    async def test_delete_on_write_can_still_leave_a_stale_value(self):
        clock, db = Clock(), {"price:42": 10}
        slow_read, first = asyncio.Event(), [True]

        async def load(key):
            value = db[key]  # the read happens now...
            if first[0]:
                first[0] = False
                await slow_read.wait()  # ...but the answer is delayed
            return value

        async def save(key, value):
            db[key] = value

        prices = CacheAside(LruCache(100, clock), load, ttl_ms=60_000)
        reader = asyncio.ensure_future(prices.get("price:42"))
        await asyncio.sleep(0)  # let the reader start and read 10
        await prices.write("price:42", 12, save)
        slow_read.set()
        self.assertEqual(await reader, 10)
        self.assertEqual(await prices.get("price:42"), 10)  # stale
        clock.now = 60_000
        self.assertEqual(await prices.get("price:42"), 12)

    def test_jitter_spreads_out_expiry(self):
        random = seeded(3)
        expiries = [jittered(60_000, 0.1, random) for _ in range(1_000)]
        self.assertTrue(min(expiries) >= 54_000 and max(expiries) <= 66_000)
        per_second: dict[int, int] = {}
        for ms in expiries:
            per_second[int(ms // 1_000)] = per_second.get(int(ms // 1_000), 0) + 1
        self.assertLess(max(per_second.values()), 120)


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/02-caching/labs/python). `python3 labs/run.py caching/python`.

## 5. Go

`LruCache` is generic and guarded by a mutex, with `container/list` for the order. `CacheAside` returns `(V, error)`; a failed load is shared with its waiters but not cached, so the next miss tries again. Coalescing is a small singleflight: a map of `*call` under a mutex, with waiters blocking on `done`. The stampede and race tests run inside `synctest.Test`, and the lab runs with `-race`.

```go
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
```

```go
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
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/02-caching/labs/go). `python3 labs/run.py caching/go`.

## 6. Java

`LruCache` is an access-ordered `LinkedHashMap` with `removeEldestEntry`, and every method is `synchronized`, because in access order `get` changes the map. `CacheAside` coalesces with `putIfAbsent` and a `CompletableFuture`, and removes it with `remove(key, mine)`, which only removes it if it's still this load. `Loader` is a small functional interface whose `load` may throw `InterruptedException`. The checks run on virtual threads and use `CountDownLatch` gates.

```java
package caching;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.DoubleSupplier;
import java.util.function.IntSupplier;
import java.util.function.LongSupplier;

/** A cache in front of a slow store. The same numbers as the TypeScript lab. */
public final class Caching {
    private Caching() {}

    private record Entry<V>(V value, long expires) {}

    /**
     * At most {@code max} entries, evicting the least recently used. A LinkedHashMap in access order does the
     * bookkeeping: every get moves the key to the end, and removeEldestEntry drops the front when it's full.
     * A get changes that order, so even reads must hold the lock.
     */
    public static final class LruCache<V> {
        private final LongSupplier now; // milliseconds
        private final LinkedHashMap<String, Entry<V>> entries;

        public LruCache(int max, LongSupplier now) {
            if (max < 1) throw new IllegalArgumentException("a cache needs room for at least one entry");
            this.now = now;
            this.entries = new LinkedHashMap<>(16, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<String, Entry<V>> eldest) {
                    return size() > max;
                }
            };
        }

        public synchronized V get(String key) {
            Entry<V> e = entries.get(key);
            if (e == null) return null;
            if (now.getAsLong() >= e.expires()) {
                entries.remove(key);
                return null;
            }
            return e.value();
        }

        public synchronized void set(String key, V value, long ttlMs) {
            long expires = ttlMs == Long.MAX_VALUE ? Long.MAX_VALUE : now.getAsLong() + ttlMs; // "forever" mustn't overflow
            entries.remove(key); // so a re-set key counts as newly used
            entries.put(key, new Entry<>(value, expires));
        }

        public synchronized void delete(String key) {
            entries.remove(key);
        }

        /** Least recently used first. */
        public synchronized List<String> keys() {
            return new ArrayList<>(entries.keySet());
        }
    }

    @FunctionalInterface
    public interface Loader<V> {
        V load(String key) throws InterruptedException;
    }

    /** Check the cache; on a miss, load and fill it. With coalesce, concurrent misses share one load. */
    public static final class CacheAside<V> {
        private final LruCache<V> cache;
        private final Loader<V> load;
        private final long ttlMs;
        private final boolean coalesce;
        private final ConcurrentHashMap<String, CompletableFuture<V>> inFlight = new ConcurrentHashMap<>();
        public final AtomicLong hits = new AtomicLong();
        public final AtomicLong misses = new AtomicLong();

        public CacheAside(LruCache<V> cache, Loader<V> load, long ttlMs, boolean coalesce) {
            this.cache = cache;
            this.load = load;
            this.ttlMs = ttlMs;
            this.coalesce = coalesce;
        }

        public V get(String key) throws InterruptedException {
            V cached = cache.get(key);
            if (cached != null) {
                hits.incrementAndGet();
                return cached;
            }
            if (!coalesce) {
                misses.incrementAndGet();
                return loadAndFill(key);
            }
            var mine = new CompletableFuture<V>();
            var pending = inFlight.putIfAbsent(key, mine); // atomic: exactly one caller's future goes in
            misses.incrementAndGet();
            if (pending != null) return pending.join(); // someone is already loading this key: wait for their answer
            try {
                V value = loadAndFill(key);
                mine.complete(value);
                return value;
            } catch (InterruptedException | RuntimeException e) {
                mine.completeExceptionally(e);
                throw e;
            } finally {
                inFlight.remove(key, mine); // a failed load isn't kept: the next miss retries
            }
        }

        private V loadAndFill(String key) throws InterruptedException {
            V value = load.load(key);
            cache.set(key, value, ttlMs);
            return value;
        }

        /** Write to the store first, then delete the cached copy. */
        public void write(String key, V value, java.util.function.BiConsumer<String, V> save) {
            save.accept(key, value);
            cache.delete(key);
        }
    }

    public static double hitRatio(long hits, long misses) {
        return (double) hits / (hits + misses);
    }

    public static double averageReadMs(double ratio, double cacheMs, double storeMs) {
        return cacheMs + (1 - ratio) * storeMs;
    }

    public static double storeReadsPerSecond(double readsPerSecond, double ratio) {
        return readsPerSecond * (1 - ratio);
    }

    public static double jittered(double ttlMs, double spread, DoubleSupplier random) {
        return ttlMs * (1 - spread + 2 * spread * random.getAsDouble());
    }

    /** Key k is requested in proportion to 1/(k+1)^s. */
    public static IntSupplier zipf(int keys, double s, DoubleSupplier random) {
        double[] cumulative = new double[keys];
        double total = 0;
        for (int k = 0; k < keys; k++) cumulative[k] = total += 1 / Math.pow(k + 1, s);
        double sum = total;
        return () -> {
            int i = Arrays.binarySearch(cumulative, random.getAsDouble() * sum);
            return i >= 0 ? i : -i - 1; // not found: binarySearch returns -(insertion point) - 1
        };
    }

    /** mulberry32, the same generator as week 1's lab. */
    public static DoubleSupplier seeded(int seed) {
        int[] a = {seed};
        return () -> {
            a[0] += 0x6d2b79f5;
            int t = a[0];
            t = (t ^ (t >>> 15)) * (t | 1);
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            return Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
        };
    }
}
```

```java
package caching;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.DoubleSupplier;
import java.util.function.IntSupplier;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class CachingCheck {
    private CachingCheck() {}

    private static String fixed(double x, int places) {
        return String.format(Locale.ROOT, "%." + places + "f", x);
    }

    /** Waits, without a fixed sleep, until another thread has done something. */
    private static void until(java.util.function.BooleanSupplier done) throws InterruptedException {
        while (!done.getAsBoolean()) Thread.sleep(1);
    }

    public static void main(String[] args) throws Exception {
        // A full LRU cache evicts the entry used longest ago.
        var lru = new Caching.LruCache<String>(3, () -> 0);
        for (String k : List.of("a", "b", "c")) lru.set(k, k.toUpperCase(Locale.ROOT), 1_000);
        lru.get("a");
        lru.set("d", "D", 1_000);
        assert lru.keys().equals(List.of("c", "a", "d")) : lru.keys();
        assert lru.get("b") == null;

        // An entry is served until its TTL runs out.
        var clock = new AtomicLong();
        var prices = new Caching.LruCache<Integer>(10, clock::get);
        prices.set("price:42", 10, 60_000);
        clock.set(59_999);
        assert prices.get("price:42") == 10;
        clock.set(60_000);
        assert prices.get("price:42") == null;

        // Cache-aside: the first read misses and loads, the rest hit.
        var loads = new AtomicInteger();
        var products = new Caching.CacheAside<String>(new Caching.LruCache<>(100, () -> 0), key -> {
            loads.incrementAndGet();
            return "kettle";
        }, 60_000, false);
        for (int i = 0; i < 5; i++) assert products.get("product:7").equals("kettle");
        assert loads.get() == 1 && products.hits.get() == 4 && products.misses.get() == 1;
        assert Caching.hitRatio(products.hits.get(), products.misses.get()) == 0.8;

        // The hit ratio decides what the database sees.
        List<String> reads = new ArrayList<>();
        for (double h : new double[] {0.8, 0.9, 0.99}) reads.add(fixed(Caching.storeReadsPerSecond(5_000, h), 0));
        assert reads.equals(List.of("1000", "500", "50")) : reads;
        List<String> avg = new ArrayList<>();
        for (double h : new double[] {0, 0.8, 0.99}) avg.add(fixed(Caching.averageReadMs(h, 1, 20), 1));
        assert avg.equals(List.of("21.0", "5.0", "1.2")) : avg;
        assert Caching.storeReadsPerSecond(5_000, 0) == 5_000;

        // Skewed traffic: a small cache answers most reads.
        List<String> ratios = new ArrayList<>();
        for (int size : new int[] {500, 2_500, 5_000, 10_000}) {
            IntSupplier next = Caching.zipf(50_000, 1, Caching.seeded(1));
            var cache = new Caching.LruCache<Boolean>(size, () -> 0);
            long hits = 0;
            long misses = 0;
            for (int i = 0; i < 200_000; i++) {
                String key = Integer.toString(next.getAsInt());
                boolean hit = cache.get(key) != null;
                if (!hit) cache.set(key, true, Long.MAX_VALUE);
                if (i >= 50_000) {
                    if (hit) hits++;
                    else misses++;
                }
            }
            ratios.add(fixed(Caching.hitRatio(hits, misses), 2));
        }
        assert ratios.equals(List.of("0.48", "0.65", "0.72", "0.80")) : ratios;

        // A stampede: every waiting request loads, unless they share one load. Each load is held at a gate until
        // all 100 callers have missed, so the count doesn't depend on how the threads happen to be scheduled.
        for (boolean coalesce : new boolean[] {false, true}) {
            var now = new AtomicLong();
            var count = new AtomicInteger();
            var gate = new CountDownLatch(1);
            var cache = new Caching.LruCache<String>(100, now::get);
            var hot = new Caching.CacheAside<String>(cache, key -> {
                count.incrementAndGet();
                gate.await(); // the database takes a while
                return "kettle";
            }, 60_000, coalesce);
            cache.set("product:7", "kettle", 60_000);
            now.set(60_000); // the entry expires...
            try (var threads = Executors.newVirtualThreadPerTaskExecutor()) {
                List<Future<String>> results = new ArrayList<>();
                for (int i = 0; i < 100; i++) results.add(threads.submit(() -> hot.get("product:7"))); // ...as 100 arrive
                until(() -> hot.misses.get() == 100);
                gate.countDown();
                for (var r : results) assert r.get().equals("kettle");
            }
            assert count.get() == (coalesce ? 1 : 100) : coalesce + ": " + count.get() + " loads";
        }

        // Delete-on-write can still leave a stale value, until the TTL runs out.
        var time = new AtomicLong();
        var db = new ConcurrentHashMap<>(new HashMap<>(java.util.Map.of("price:42", 10)));
        var hasRead = new CountDownLatch(1);
        var slowRead = new CountDownLatch(1);
        var firstLoad = new java.util.concurrent.atomic.AtomicBoolean(true);
        var cachedPrices = new Caching.CacheAside<Integer>(new Caching.LruCache<>(100, time::get), key -> {
            int value = db.get(key); // the read happens now...
            if (firstLoad.getAndSet(false)) {
                hasRead.countDown();
                slowRead.await(); // ...but the answer is delayed
            }
            return value;
        }, 60_000, false);
        try (var threads = Executors.newVirtualThreadPerTaskExecutor()) {
            var reader = threads.submit(() -> cachedPrices.get("price:42"));
            hasRead.await(); // 1. the reader has read 10
            cachedPrices.write("price:42", 12, db::put); // 2. the writer saves 12 and deletes (nothing)
            slowRead.countDown();
            assert reader.get() == 10; // 3. the reader caches the old 10
        }
        assert cachedPrices.get("price:42") == 10; // stale
        time.set(60_000);
        assert cachedPrices.get("price:42") == 12;

        // Jitter spreads out expiry.
        DoubleSupplier random = Caching.seeded(3);
        var perSecond = new HashMap<Integer, Integer>();
        double lo = Double.MAX_VALUE;
        double hi = 0;
        for (int i = 0; i < 1_000; i++) {
            double ms = Caching.jittered(60_000, 0.1, random);
            lo = Math.min(lo, ms);
            hi = Math.max(hi, ms);
            perSecond.merge((int) (ms / 1_000), 1, Integer::sum);
        }
        int busiest = perSecond.values().stream().mapToInt(Integer::intValue).max().orElseThrow();
        assert lo >= 54_000 && hi <= 66_000 && busiest < 120 : busiest;
        System.out.println("all caching checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/02-caching/labs/java). `python3 labs/run.py caching/java`.

## 7. Rust

`LruCache` keeps a `HashMap` of entries and a `BTreeMap` of last-use times behind one `Mutex`. `CacheAside` coalesces with an `Arc<OnceLock<V>>` per key: `get_or_init` guarantees one load, and the thread that ran it removes the cell from the map. `OnceLock` can't hold a failure, so this loader can't fail; a fallible version needs `Result` inside the cell, or moka. The tests use `std::thread::scope`, so threads can borrow the cache without `Arc`, and a `Gate` made from a `Mutex<bool>` and a `Condvar`.

```rust
//! A cache in front of a slow store: an LRU cache with expiry, cache-aside with request coalescing, and the
//! arithmetic that says how much a cache takes off the database. The same numbers as the TypeScript lab.
use std::collections::{BTreeMap, HashMap};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, OnceLock};

pub type Clock = Arc<dyn Fn() -> u64 + Send + Sync>; // milliseconds

struct Entry<V> {
    value: V,
    expires: u64,
    used: u64, // when it was last used, as a position in `order`
}

struct Inner<V> {
    entries: HashMap<String, Entry<V>>,
    order: BTreeMap<u64, String>, // last use → key; the first entry is the least recently used
    tick: u64,
}

/// At most `max` entries, evicting the least recently used. The standard library has no LRU (crates such as
/// `lru` and `moka` do), so a HashMap finds entries and a BTreeMap keeps them in order of last use.
pub struct LruCache<V> {
    max: usize,
    now: Clock,
    inner: Mutex<Inner<V>>,
}

impl<V: Clone> LruCache<V> {
    pub fn new(max: usize, now: Clock) -> Self {
        assert!(max >= 1, "a cache needs room for at least one entry");
        LruCache {
            max,
            now,
            inner: Mutex::new(Inner {
                entries: HashMap::new(),
                order: BTreeMap::new(),
                tick: 0,
            }),
        }
    }

    pub fn get(&self, key: &str) -> Option<V> {
        let mut inner = self.inner.lock().unwrap();
        let Inner {
            entries,
            order,
            tick,
        } = &mut *inner;
        let entry = entries.get_mut(key)?;
        order.remove(&entry.used);
        if (self.now)() >= entry.expires {
            entries.remove(key); // expired: treat it as a miss
            return None;
        }
        *tick += 1;
        entry.used = *tick; // now the most recently used
        order.insert(*tick, key.to_string());
        Some(entry.value.clone())
    }

    pub fn set(&self, key: &str, value: V, ttl_ms: u64) {
        let mut inner = self.inner.lock().unwrap();
        let Inner {
            entries,
            order,
            tick,
        } = &mut *inner;
        *tick += 1;
        let expires = (self.now)().saturating_add(ttl_ms); // u64::MAX means "never", and mustn't wrap round
        if let Some(old) = entries.insert(
            key.to_string(),
            Entry {
                value,
                expires,
                used: *tick,
            },
        ) {
            order.remove(&old.used);
        }
        order.insert(*tick, key.to_string());
        if entries.len() > self.max {
            let (_, oldest) = order.pop_first().expect("not empty");
            entries.remove(&oldest);
        }
    }

    pub fn delete(&self, key: &str) {
        let mut inner = self.inner.lock().unwrap();
        if let Some(old) = inner.entries.remove(key) {
            inner.order.remove(&old.used);
        }
    }

    /// Least recently used first.
    pub fn keys(&self) -> Vec<String> {
        self.inner.lock().unwrap().order.values().cloned().collect()
    }
}

pub type Loader<V> = Box<dyn Fn(&str) -> V + Send + Sync>;

/// Check the cache; on a miss, load and fill it. With `coalesce`, concurrent misses share one load.
pub struct CacheAside<V> {
    cache: Arc<LruCache<V>>,
    load: Loader<V>,
    ttl_ms: u64,
    coalesce: bool,
    in_flight: Mutex<HashMap<String, Arc<OnceLock<V>>>>,
    pub hits: AtomicU64,
    pub misses: AtomicU64,
}

impl<V: Clone> CacheAside<V> {
    pub fn new(cache: Arc<LruCache<V>>, load: Loader<V>, ttl_ms: u64, coalesce: bool) -> Self {
        let (hits, misses) = (AtomicU64::new(0), AtomicU64::new(0));
        CacheAside {
            cache,
            load,
            ttl_ms,
            coalesce,
            in_flight: Mutex::new(HashMap::new()),
            hits,
            misses,
        }
    }

    pub fn get(&self, key: &str) -> V {
        if let Some(value) = self.cache.get(key) {
            self.hits.fetch_add(1, Ordering::Relaxed);
            return value;
        }
        if !self.coalesce {
            self.misses.fetch_add(1, Ordering::Relaxed);
            return self.load_and_fill(key);
        }
        let cell = self
            .in_flight
            .lock()
            .unwrap()
            .entry(key.to_string())
            .or_default()
            .clone();
        self.misses.fetch_add(1, Ordering::Relaxed);
        // get_or_init runs exactly one initialiser; every other caller blocks until it's done, then shares the value.
        let mut loaded_here = false;
        let value = cell
            .get_or_init(|| {
                loaded_here = true;
                self.load_and_fill(key)
            })
            .clone();
        if loaded_here {
            self.in_flight.lock().unwrap().remove(key);
        }
        value
    }

    fn load_and_fill(&self, key: &str) -> V {
        let value = (self.load)(key);
        self.cache.set(key, value.clone(), self.ttl_ms);
        value
    }

    /// Write to the store first, then delete the cached copy.
    pub fn write(&self, key: &str, value: V, save: impl FnOnce(&str, V)) {
        save(key, value);
        self.cache.delete(key);
    }
}

pub fn hit_ratio(hits: u64, misses: u64) -> f64 {
    hits as f64 / (hits + misses) as f64
}

pub fn average_read_ms(ratio: f64, cache_ms: f64, store_ms: f64) -> f64 {
    cache_ms + (1.0 - ratio) * store_ms
}

pub fn store_reads_per_second(reads_per_second: f64, ratio: f64) -> f64 {
    reads_per_second * (1.0 - ratio)
}

pub fn jittered(ttl_ms: f64, spread: f64, random: &mut impl FnMut() -> f64) -> f64 {
    ttl_ms * (1.0 - spread + 2.0 * spread * random())
}

/// Key k is requested in proportion to 1/(k+1)^s.
pub fn zipf(keys: usize, s: f64, mut random: impl FnMut() -> f64) -> impl FnMut() -> usize {
    let mut total = 0.0;
    let cumulative: Vec<f64> = (0..keys)
        .map(|k| {
            total += 1.0 / ((k + 1) as f64).powf(s);
            total
        })
        .collect();
    move || {
        let target = random() * total;
        cumulative.partition_point(|&c| c < target) // the first total at or above the target
    }
}

/// mulberry32, the same generator as week 1's lab.
pub fn seeded(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = (a ^ (a >> 15)).wrapping_mul(a | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4_294_967_296.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Condvar;
    use std::sync::atomic::AtomicBool;

    fn clock() -> (Arc<AtomicU64>, Clock) {
        let now = Arc::new(AtomicU64::new(0));
        let read = now.clone();
        (now, Arc::new(move || read.load(Ordering::SeqCst)))
    }

    /// A one-time gate: threads wait at it until the test opens it. Rust's standard library has no latch.
    #[derive(Default)]
    struct Gate {
        open: Mutex<bool>,
        opened: Condvar,
    }

    impl Gate {
        fn wait(&self) {
            let _open = self
                .opened
                .wait_while(self.open.lock().unwrap(), |open| !*open)
                .unwrap();
        }
        fn open(&self) {
            *self.open.lock().unwrap() = true;
            self.opened.notify_all();
        }
    }

    #[test]
    fn a_full_lru_cache_evicts_the_entry_used_longest_ago() {
        let cache = LruCache::new(3, clock().1);
        for k in ["a", "b", "c"] {
            cache.set(k, k.to_uppercase(), 1_000);
        }
        cache.get("a");
        cache.set("d", "D".into(), 1_000);
        assert_eq!(cache.keys(), ["c", "a", "d"]);
        assert_eq!(cache.get("b"), None);
    }

    #[test]
    fn an_entry_expires_after_its_ttl() {
        let (now, clock) = clock();
        let cache = LruCache::new(10, clock);
        cache.set("price:42", 10, 60_000);
        now.store(59_999, Ordering::SeqCst);
        assert_eq!(cache.get("price:42"), Some(10));
        now.store(60_000, Ordering::SeqCst);
        assert_eq!(cache.get("price:42"), None);
    }

    #[test]
    fn cache_aside_first_read_misses_the_rest_hit() {
        let loads = Arc::new(AtomicU64::new(0));
        let counted = loads.clone();
        let load: Loader<String> = Box::new(move |_| {
            counted.fetch_add(1, Ordering::SeqCst);
            "kettle".into()
        });
        let products =
            CacheAside::new(Arc::new(LruCache::new(100, clock().1)), load, 60_000, false);
        for _ in 0..5 {
            assert_eq!(products.get("product:7"), "kettle");
        }
        let (hits, misses) = (
            products.hits.load(Ordering::SeqCst),
            products.misses.load(Ordering::SeqCst),
        );
        assert_eq!((loads.load(Ordering::SeqCst), hits, misses), (1, 4, 1));
        assert_eq!(hit_ratio(hits, misses), 0.8);
    }

    #[test]
    fn the_hit_ratio_decides_what_the_database_sees() {
        assert_eq!(
            [0.8, 0.9, 0.99].map(|h| store_reads_per_second(5_000.0, h).round()),
            [1_000.0, 500.0, 50.0]
        );
        assert_eq!(
            [0.0, 0.8, 0.99].map(|h| format!("{:.1}", average_read_ms(h, 1.0, 20.0))),
            ["21.0", "5.0", "1.2"]
        );
        assert_eq!(store_reads_per_second(5_000.0, 0.0), 5_000.0);
    }

    #[test]
    fn skewed_traffic_a_small_cache_answers_most_reads() {
        let ratios = [500, 2_500, 5_000, 10_000].map(|size| {
            let mut next = zipf(50_000, 1.0, seeded(1));
            let cache = LruCache::new(size, clock().1);
            let (mut hits, mut misses) = (0, 0);
            for i in 0..200_000 {
                let key = next().to_string();
                let hit = cache.get(&key).is_some();
                if !hit {
                    cache.set(&key, true, u64::MAX);
                }
                if i >= 50_000 {
                    if hit { hits += 1 } else { misses += 1 }
                }
            }
            format!("{:.2}", hit_ratio(hits, misses))
        });
        assert_eq!(ratios, ["0.48", "0.65", "0.72", "0.80"]);
    }

    #[test]
    fn a_stampede_unless_misses_share_one_load() {
        for coalesce in [false, true] {
            let (now, clock) = clock();
            let (loads, gate) = (Arc::new(AtomicU64::new(0)), Arc::new(Gate::default()));
            let (counted, held) = (loads.clone(), gate.clone());
            let load: Loader<String> = Box::new(move |_| {
                counted.fetch_add(1, Ordering::SeqCst);
                held.wait(); // the database takes a while: held until all 100 callers have missed
                "kettle".into()
            });
            let cache = Arc::new(LruCache::new(100, clock));
            cache.set("product:7", "kettle".into(), 60_000);
            now.store(60_000, Ordering::SeqCst); // the entry expires as 100 reads arrive
            let products = CacheAside::new(cache, load, 60_000, coalesce);
            std::thread::scope(|s| {
                let readers: Vec<_> = (0..100)
                    .map(|_| s.spawn(|| products.get("product:7")))
                    .collect();
                while products.misses.load(Ordering::SeqCst) < 100 {
                    std::thread::yield_now();
                }
                gate.open();
                assert!(readers.into_iter().all(|r| r.join().unwrap() == "kettle"));
            });
            assert_eq!(loads.load(Ordering::SeqCst), if coalesce { 1 } else { 100 });
        }
    }

    #[test]
    fn delete_on_write_can_still_leave_a_stale_value() {
        let (now, clock) = clock();
        let db = Arc::new(Mutex::new(HashMap::from([("price:42".to_string(), 10)])));
        let (has_read, slow_read) = (Arc::new(Gate::default()), Arc::new(Gate::default()));
        let first = Arc::new(AtomicBool::new(true));
        let (store, signal, held) = (db.clone(), has_read.clone(), slow_read.clone());
        let load: Loader<i32> = Box::new(move |key| {
            let value = store.lock().unwrap()[key]; // the read happens now...
            if first.swap(false, Ordering::SeqCst) {
                signal.open();
                held.wait(); // ...but the answer is delayed
            }
            value
        });
        let prices = CacheAside::new(Arc::new(LruCache::new(100, clock)), load, 60_000, false);
        std::thread::scope(|s| {
            let reader = s.spawn(|| prices.get("price:42"));
            has_read.wait(); // 1. the reader has read 10
            prices.write("price:42", 12, |k, v| {
                db.lock().unwrap().insert(k.to_string(), v); // 2. the writer saves 12 and deletes (nothing)
            });
            slow_read.open();
            assert_eq!(reader.join().unwrap(), 10); // 3. the reader caches the old 10
        });
        assert_eq!(prices.get("price:42"), 10); // stale
        now.store(60_000, Ordering::SeqCst);
        assert_eq!(prices.get("price:42"), 12);
    }

    #[test]
    fn jitter_spreads_out_expiry() {
        let mut random = seeded(3);
        let expiries: Vec<f64> = (0..1_000)
            .map(|_| jittered(60_000.0, 0.1, &mut random))
            .collect();
        assert!(
            expiries
                .iter()
                .all(|&ms| (54_000.0..=66_000.0).contains(&ms))
        );
        let mut per_second = HashMap::new();
        for ms in &expiries {
            *per_second.entry((ms / 1_000.0) as u64).or_insert(0) += 1;
        }
        assert!(per_second.values().max().unwrap() < &120);
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/02-caching/labs/rust). `python3 labs/run.py caching/rust`.

## 8. C#

`LruCache` pairs `LinkedList<Entry>` with a `Dictionary` of nodes under C# 13's `Lock`, and uses the `TryGet(key, out value)` pattern, so a cached `default` can't be mistaken for a miss. `CacheAside` is async, and coalesces with `GetOrAdd` and `Lazy<Task<V>>`. The checks hold loads with `TaskCompletionSource` gates created with `RunContinuationsAsynchronously`, so opening a gate doesn't run the waiters' code on the opener's thread. It runs in the .NET SDK container.

```csharp
// A cache in front of a slow store: an LRU cache with expiry, cache-aside with request coalescing, and the
// arithmetic that says how much a cache takes off the database. The same numbers as the TypeScript lab.
using System.Collections.Concurrent;

/// <summary>
/// At most <c>max</c> entries, evicting the least recently used. .NET's MemoryCache has no LRU (it compacts by
/// priority), so a LinkedList keeps the order and a Dictionary finds each key's node in O(1).
/// </summary>
public sealed class LruCache<V>
{
    private readonly record struct Entry(string Key, V Value, long Expires);

    private readonly int _max;
    private readonly Func<long> _now; // milliseconds
    private readonly LinkedList<Entry> _order = new(); // first: least recently used
    private readonly Dictionary<string, LinkedListNode<Entry>> _entries = [];
    private readonly Lock _lock = new();

    public LruCache(int max, Func<long> now)
    {
        ArgumentOutOfRangeException.ThrowIfLessThan(max, 1);
        (_max, _now) = (max, now);
    }

    public bool TryGet(string key, out V value)
    {
        lock (_lock)
        {
            value = default!;
            if (!_entries.TryGetValue(key, out var node)) return false;
            _order.Remove(node);
            if (_now() >= node.Value.Expires)
            {
                _entries.Remove(key); // expired: treat it as a miss
                return false;
            }
            _order.AddLast(node); // now the most recently used
            value = node.Value.Value;
            return true;
        }
    }

    public void Set(string key, V value, long ttlMs)
    {
        lock (_lock)
        {
            if (_entries.Remove(key, out var old)) _order.Remove(old);
            var expires = ttlMs == long.MaxValue ? long.MaxValue : _now() + ttlMs; // "never" mustn't overflow
            _entries[key] = _order.AddLast(new Entry(key, value, expires));
            if (_entries.Count > _max)
            {
                _entries.Remove(_order.First!.Value.Key);
                _order.RemoveFirst();
            }
        }
    }

    public void Delete(string key)
    {
        lock (_lock)
        {
            if (_entries.Remove(key, out var node)) _order.Remove(node);
        }
    }

    /// <summary>Least recently used first.</summary>
    public string[] Keys()
    {
        lock (_lock) return _order.Select(e => e.Key).ToArray();
    }
}

/// <summary>Check the cache; on a miss, load and fill it. With coalesce, concurrent misses share one load.</summary>
public sealed class CacheAside<V>(LruCache<V> cache, Func<string, Task<V>> load, long ttlMs, bool coalesce = false)
{
    private readonly ConcurrentDictionary<string, Lazy<Task<V>>> _inFlight = new();
    private long _hits, _misses;
    public long Hits => Interlocked.Read(ref _hits);
    public long Misses => Interlocked.Read(ref _misses);

    public async Task<V> Get(string key)
    {
        if (cache.TryGet(key, out var cached))
        {
            Interlocked.Increment(ref _hits);
            return cached;
        }
        if (!coalesce)
        {
            Interlocked.Increment(ref _misses);
            return await LoadAndFill(key);
        }
        // GetOrAdd may build more than one Lazy under a race, but only the one it stores is ever started.
        var mine = new Lazy<Task<V>>(() => LoadAndFill(key));
        var shared = _inFlight.GetOrAdd(key, mine);
        Interlocked.Increment(ref _misses);
        try
        {
            return await shared.Value;
        }
        finally
        {
            _inFlight.TryRemove(new KeyValuePair<string, Lazy<Task<V>>>(key, shared)); // only if it's still this load
        }
    }

    private async Task<V> LoadAndFill(string key)
    {
        var value = await load(key);
        cache.Set(key, value, ttlMs);
        return value;
    }

    /// <summary>Write to the store first, then delete the cached copy.</summary>
    public async Task Write(string key, V value, Func<string, V, Task> save)
    {
        await save(key, value);
        cache.Delete(key);
    }
}

public static class CacheMath
{
    public static double HitRatio(long hits, long misses) => (double)hits / (hits + misses);

    public static double AverageReadMs(double ratio, double cacheMs, double storeMs) => cacheMs + (1 - ratio) * storeMs;

    public static double StoreReadsPerSecond(double readsPerSecond, double ratio) => readsPerSecond * (1 - ratio);

    public static double Jittered(double ttlMs, double spread, Func<double> random) => ttlMs * (1 - spread + 2 * spread * random());

    /// <summary>Key k is requested in proportion to 1/(k+1)^s.</summary>
    public static Func<int> Zipf(int keys, double s, Func<double> random)
    {
        var cumulative = new double[keys];
        var total = 0.0;
        for (var k = 0; k < keys; k++) cumulative[k] = total += 1 / Math.Pow(k + 1, s);
        return () =>
        {
            var i = Array.BinarySearch(cumulative, random() * total);
            return i >= 0 ? i : ~i; // not found: BinarySearch returns the complement of the insertion point
        };
    }

    /// <summary>mulberry32, the same generator as week 1's lab.</summary>
    public static Func<double> Seeded(uint seed)
    {
        var a = seed;
        return () =>
        {
            a += 0x6d2b79f5;
            var t = (a ^ (a >> 15)) * (a | 1);
            t ^= t + (t ^ (t >> 7)) * (t | 61);
            return (t ^ (t >> 14)) / 4294967296.0;
        };
    }
}
```

```csharp
// Checks: the same numbers as every other language.
using System.Globalization;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static string Fixed(double x, int places) => x.ToString("F" + places, CultureInfo.InvariantCulture);

// A full LRU cache evicts the entry used longest ago.
var lru = new LruCache<string>(3, () => 0);
foreach (var k in new[] { "a", "b", "c" }) lru.Set(k, k.ToUpperInvariant(), 1_000);
lru.TryGet("a", out _);
lru.Set("d", "D", 1_000);
Check(lru.Keys().SequenceEqual(["c", "a", "d"]) && !lru.TryGet("b", out _), string.Join(",", lru.Keys()));

// An entry is served until its TTL runs out.
long now = 0;
var prices = new LruCache<int>(10, () => Interlocked.Read(ref now));
prices.Set("price:42", 10, 60_000);
now = 59_999;
Check(prices.TryGet("price:42", out var p) && p == 10, "before expiry");
now = 60_000;
Check(!prices.TryGet("price:42", out _), "after expiry");

// Cache-aside: the first read misses and loads, the rest hit.
var loads = 0;
var products = new CacheAside<string>(new LruCache<string>(100, () => 0), _ => { loads++; return Task.FromResult("kettle"); }, 60_000);
for (var i = 0; i < 5; i++) Check(await products.Get("product:7") == "kettle", "kettle");
Check(loads == 1 && products.Hits == 4 && products.Misses == 1 && CacheMath.HitRatio(products.Hits, products.Misses) == 0.8, (loads, products.Hits));

// The hit ratio decides what the database sees.
Check(new[] { 0.8, 0.9, 0.99 }.Select(h => Fixed(CacheMath.StoreReadsPerSecond(5_000, h), 0)).SequenceEqual(["1000", "500", "50"]), "reads");
Check(new[] { 0, 0.8, 0.99 }.Select(h => Fixed(CacheMath.AverageReadMs(h, 1, 20), 1)).SequenceEqual(["21.0", "5.0", "1.2"]), "average");
Check(CacheMath.StoreReadsPerSecond(5_000, 0) == 5_000, "cache down");

// Skewed traffic: a small cache answers most reads.
var ratios = new[] { 500, 2_500, 5_000, 10_000 }.Select(size =>
{
    var next = CacheMath.Zipf(50_000, 1, CacheMath.Seeded(1));
    var cache = new LruCache<bool>(size, () => 0);
    long hits = 0, misses = 0;
    for (var i = 0; i < 200_000; i++)
    {
        var key = next().ToString(CultureInfo.InvariantCulture);
        var hit = cache.TryGet(key, out _);
        if (!hit) cache.Set(key, true, long.MaxValue);
        if (i >= 50_000) _ = hit ? hits++ : misses++;
    }
    return Fixed(CacheMath.HitRatio(hits, misses), 2);
}).ToArray();
Check(ratios.SequenceEqual(["0.48", "0.65", "0.72", "0.80"]), string.Join(", ", ratios));

// A stampede: every waiting request loads, unless they share one load. Each load is held until all 100 callers
// have missed, so the count doesn't depend on how the tasks happen to be scheduled.
foreach (var coalesce in new[] { false, true })
{
    long clock = 0;
    var count = 0;
    var gate = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    var cache = new LruCache<string>(100, () => Interlocked.Read(ref clock));
    var hot = new CacheAside<string>(cache, async _ =>
    {
        Interlocked.Increment(ref count);
        await gate.Task; // the database takes a while
        return "kettle";
    }, 60_000, coalesce);
    cache.Set("product:7", "kettle", 60_000);
    Interlocked.Exchange(ref clock, 60_000); // the entry expires as 100 reads arrive
    var readers = Enumerable.Range(0, 100).Select(_ => Task.Run(() => hot.Get("product:7"))).ToArray();
    while (hot.Misses < 100) await Task.Delay(1);
    gate.SetResult();
    Check((await Task.WhenAll(readers)).All(n => n == "kettle"), "all kettle");
    Check(count == (coalesce ? 1 : 100), (coalesce, count));
}

// Delete-on-write can still leave a stale value, until the TTL runs out.
long t = 0;
var db = new System.Collections.Concurrent.ConcurrentDictionary<string, int> { ["price:42"] = 10 };
var hasRead = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
var slowRead = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
var first = 1;
var cachedPrices = new CacheAside<int>(new LruCache<int>(100, () => Interlocked.Read(ref t)), async key =>
{
    var value = db[key]; // the read happens now...
    if (Interlocked.Exchange(ref first, 0) == 1)
    {
        hasRead.SetResult();
        await slowRead.Task; // ...but the answer is delayed
    }
    return value;
}, 60_000);
var reader = cachedPrices.Get("price:42");
await hasRead.Task; // 1. the reader has read 10
await cachedPrices.Write("price:42", 12, (k, v) => { db[k] = v; return Task.CompletedTask; }); // 2. saves 12, deletes (nothing)
slowRead.SetResult();
Check(await reader == 10, "the reader caches the old 10"); // 3.
Check(await cachedPrices.Get("price:42") == 10, "stale");
Interlocked.Exchange(ref t, 60_000);
Check(await cachedPrices.Get("price:42") == 12, "fresh after the TTL");

// Jitter spreads out expiry.
var random = CacheMath.Seeded(3);
var expiries = Enumerable.Range(0, 1_000).Select(_ => CacheMath.Jittered(60_000, 0.1, random)).ToArray();
var busiest = expiries.CountBy(ms => (int)(ms / 1_000)).Max(g => g.Value);
Check(expiries.Min() >= 54_000 && expiries.Max() <= 66_000 && busiest < 120, busiest);
Console.WriteLine("all caching checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/02-caching/labs/csharp). `python3 labs/run.py caching/csharp`.

## Common pitfalls

1. **Check-then-insert on a shared map.** `if (!map.containsKey(k)) map.put(k, load())` lets two threads both load. Use the atomic operation: `putIfAbsent`, `GetOrAdd`, a mutex around both steps.
2. **Reading an access-ordered `LinkedHashMap` without a lock.** `get` reorders the list; two unsynchronised reads can corrupt it.
3. **Testing a race with sleeps.** A test that sleeps 10 ms "so the threads start" passes on your laptop and fails in CI. Use gates, or a fake clock.
4. **Caching a failure.** A coalesced load that fails must not stay in the in-progress map, or every later caller gets the same error. Every lab removes the load when it finishes, success or not.
5. **`now + MAX_VALUE` for "never".** It wraps negative in Java and C#. Treat the maximum as a special case, or use saturating arithmetic.
6. **Writing your own in production.** Caffeine, moka, `HybridCache` and `lru-cache` handle coalescing, size limits and smarter eviction. The labs build one to show how.

## Check your understanding

1. Why does the TypeScript lab need no lock around its in-progress map, while the Go lab does?
2. `ConcurrentDictionary.GetOrAdd(key, _ => LoadAsync(key))` without `Lazy`: what can go wrong?
3. Why does the Python lab use `asyncio.shield` when awaiting a shared load?
4. In the Java and C# stampede checks, why does `get` count a miss *after* joining the load in progress?
5. Why must Java's `LruCache.get` be `synchronized` when it only reads?

<details>
<summary>Answers — after your attempt</summary>

1. JavaScript runs one piece of code at a time on its event loop: between checking the map and inserting into it there's no `await`, so nothing else can run in between. Go's goroutines run in parallel on several cores, so two can check the map at the same instant.
2. `GetOrAdd` may call the factory more than once under a race, keeping only one result. Each call starts `LoadAsync`, so two or more loads hit the database, which is what coalescing was meant to stop. With `Lazy`, the extra `Lazy` objects are created but never asked for their value, so nothing extra starts.
3. If the caller who started the load is cancelled, for example by a timeout, cancelling its await would cancel the shared task, and every other waiter would get a cancellation. `shield` cancels only that caller's wait and lets the load carry on.
4. The test opens the gate when the miss count reaches 100. If a miss were counted before joining, a caller could be counted, then paused before it joins; the gate opens, the load finishes and leaves the map, and the late caller starts a second load. Counting after joining means 100 counted misses are 100 callers already waiting.
5. In access order, `get` moves the entry to the end of the linked list, which is a write. Two threads doing that at once can corrupt the list.

</details>

## Practice — independent task

**Add a failing load to your language's coalescing test.**

1. Give the load a way to fail: an exception, an `Err`, an `error`, depending on the language.
2. Write a test where the first load fails while 10 callers wait on it. Every waiter must see the failure, and the next `get` after it must start a fresh load, not get the old failure.
3. Rust: `OnceLock` can't hold a failure. Store a `Result` in it, or switch the in-flight map to something that can. Explain your choice.

**Done when:** your test passes several times in a row, and you can say in one sentence what would happen to every later caller if the in-progress entry weren't removed after a failure.

## Before moving on

You can name your language's LRU structure and production cache, make concurrent misses share one load with an atomic step, and test a race with a gate or a fake clock instead of a sleep.

**Recap.** Every language builds LRU from a hash map plus an order of use: `OrderedDict`, `LinkedHashMap`, a linked list beside a map, or, in Rust, a `BTreeMap` of use times. Coalescing needs "insert if absent" to be one atomic step: a mutex in Go, `putIfAbsent` in Java, `OnceLock` in Rust, `GetOrAdd` with `Lazy` in C#; JavaScript and asyncio get it for free from their event loops. Threaded tests hold work at a gate until the race is set up, or use Go's fake clock. In production, use Caffeine, moka, `HybridCache` or `lru-cache`, which do all of this.

## Related

- [[architecture/02-building-blocks/02-caching/index|Caching]]: the main lesson
- [[architecture/02-building-blocks/01-load-balancing-and-proxies/in-other-languages|Load balancing in other languages]]: hashing keys onto cache nodes in the same languages
- [[architecture/03-architectural-patterns/02-resilience-patterns/in-other-languages|Resilience patterns in other languages]]: fairness and giving up, in the same concurrency tools
