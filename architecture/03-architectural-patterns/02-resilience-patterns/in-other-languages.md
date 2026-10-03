# Resilience Patterns in Other Languages

> **[Intermediate]** · A companion to [[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]], which simulates a cascade, a timeout that fails to stop it and bulkheads that contain it, and builds a bulkhead in TypeScript, including a bug where a latecomer barges in. This page does the same in Python, Go, Java, Rust, C, C++ and C#, with the same simulation numbers in every language. The simulation is plain arithmetic and translates line for line. The bulkhead is where the languages really differ: each has its own way to limit concurrent work, and they disagree on whether the longest waiter gets the next free place.

## Before you start

You can already:

- Explain the cascade, Little's law and the bulkhead race → [[architecture/03-architectural-patterns/02-resilience-patterns/index|the main lesson]].
- Start concurrent work in your language: tasks, goroutines or threads.

After this lesson you will be able to:

1. Name your language's tool for limiting concurrent work, and say whether it's fair.
2. Add a queue limit to a semaphore that doesn't have one.
3. Make a caller who gives up leave the queue without taking a place with them.

## The kid version

A bouncy castle allows five children at a time, with a short line outside. When a child comes out, the one at the front of the line goes in next. Seven helpers each run the same castle with their own rules. Some hand the free spot straight to the front of the line. Others just shout "there's a space!", and whoever is nearest runs in, which might be a child who has only just arrived and pushed past the line.

**Where the analogy stops working.** At a real castle you'd notice someone pushing in. In a program, it happens in microseconds and only under load, which is why each lab tests for it on purpose.

## 1. The tools, by ecosystem

| Language | Limit concurrent work | Fair? | Queue limit built in? | Resilience libraries |
|---|---|---|---|---|
| TypeScript | written by hand (the main lesson) | as written | as written | cockatiel, opossum |
| Python | `asyncio.Semaphore` | no promise | no | tenacity (retries), pybreaker |
| Go | a **buffered channel**, or `x/sync/semaphore` | yes, both | no | gobreaker, failsafe-go |
| Java | **`new Semaphore(n, true)`** | only with `true` | no | **Resilience4j** |
| Rust | **tokio `Semaphore`** | yes | no | **tower** layers |
| C | POSIX `sem_t`, or a mutex and condition variable | no promise | no | none standard |
| C++ | `std::counting_semaphore` | no promise | no | none standard |
| C# | **`ConcurrencyLimiter`** | with `OldestFirst` | **yes** | **Polly** |

**Fair** means a freed place goes to whoever has waited longest. An unfair semaphore can hand it to a newcomer, which is the bug from the main lesson. Unfair semaphores are faster, which is why it's often the default. For a service, use the library in bold. Resilience4j and Polly both provide a bulkhead, a circuit breaker, retries and timeouts. tower provides concurrency-limit, timeout and load-shed layers. The labs write the bulkhead themselves so you can see how it works.

## 2. What changes between languages

### Fairness, and who gets the next place

Four labs use a tool that's already fair. Go's channel hands a freed slot straight to the goroutine that has waited longest. Java needs `true` in the constructor, plus care: even on a fair `Semaphore`, the no-argument `tryAcquire()` jumps the queue on purpose. The lab uses `tryAcquire(0, MILLISECONDS)`, which waits its turn. Rust's tokio `Semaphore` is fair by design. C#'s `ConcurrencyLimiter` with `QueueProcessingOrder.OldestFirst` serves its queue first.

The other three have no fair tool, so their labs write the hand-off out, as the main lesson's fix does. Python passes a future from a queue to the next waiter. C uses a ticket number, like a deli counter, and C++ uses a list of waiters.

### A queue limit

Only C#'s `ConcurrencyLimiter` has a queue limit built in. Everywhere else, a semaphore lets any number of callers wait, which is the unbounded queue the main lesson warns about. Each lab therefore keeps a count of waiters and turns a caller away at once when the count is at its limit.

### A caller who gives up

In the simulation, callers give up after 2 seconds. In real code, a caller that stops waiting must leave the queue, or a later free place could be handed to someone who has already gone, and lost. Each language cancels in its own way:

- Go selects on `ctx.Done()`.
- Java uses a timed `tryAcquire`.
- Rust drops the future, wrapped in `tokio::time::timeout`.
- C# passes a `CancellationToken`.
- C++ uses `condition_variable::wait_for`.
- Python's bulkhead skips waiters whose futures were cancelled.

The C lab doesn't support giving up. Leaving a ticket queue means marking the ticket as abandoned so it's skipped later, which is worth trying as practice.

### Testing timing without waiting

Concurrency tests that sleep are slow, and they fail when the machine is busy. Go's `testing/synctest` and tokio's `start_paused` replace the clock with a fake one. A 5-second wait then takes no real time, and `synctest.Wait()` returns once every goroutine is blocked, so the test knows exactly when the queue is full. Python's tests step the event loop with `asyncio.sleep(0)`. Java, C and C++ use real threads and wait for a counter to change.

## 3. The same numbers, in every language

| Run (60 seconds, 100 ms ticks) | Expected in every language |
|---|---|
| healthy, one pool of 50 | search 1,196 ok, profile 1,797 ok |
| search slow (5 s), no timeout | profile 72 ok, 1,668 timed out |
| with a 3-second timeout | profile 270 ok |
| with a 1-second timeout | profile 1,797 ok, 1,180 searches failed |
| bulkheads (20 for search, 30 for profile, queue 10) | profile 1,797 ok; search 380 failed, 190 timed out, 600 rejected, 30 unfinished |

Every lab also checks the bulkhead: two running and one waiting means the next caller is turned away at once; a freed place goes to the waiter before a latecomer; and nothing ever runs more than the limit at once, however the work interleaves.

## Terms used in this lesson

1. **Semaphore**: This is a counter of free places. Taking a place lowers it; giving one back raises it. A caller who finds it at zero waits.
2. **Fair (semaphore)**: This is a semaphore that gives a freed place to whoever has waited longest, in the order they asked.
3. **Barging**: This is a newcomer taking a freed place before a caller who was already waiting. It's the bug from the main lesson, and what an unfair semaphore allows.
4. **Hand-off**: This is passing a place from a finishing call straight to the next waiter, without ever marking it free, so nobody can slip in between.
5. **Condition variable**: This is a way for a thread to sleep until another thread tells it something has changed. It's always used with a mutex, and the sleeping thread must check its condition again when it wakes.
6. **Spurious wakeup**: This is a thread waking from a condition variable when nobody signalled it. It's allowed by the standard, which is why the C and C++ labs wait in a loop.
7. **Fake clock**: This is a test clock that moves only when every task is blocked, so timeouts and sleeps take no real time and happen in the same order every run.

## 4. Python

The simulation uses the same dictionary keys as the TypeScript lab's objects, in snake_case. Python dictionaries keep insertion order, so the pools start work in the order they're listed, as in TypeScript. `asyncio.Semaphore` makes no promise about who goes next and has no queue limit, so `Bulkhead` keeps a `deque` of futures. A finishing call hands its place to the first waiter whose caller hasn't given up. The tests step the event loop with `await asyncio.sleep(0)`. The fourth test gives up with `asyncio.wait_for` and checks the place comes back.

```python
"""A tick-by-tick simulation of a cascade, Little's law, and a bulkhead that hands places to waiters.
The same numbers as the TypeScript lab. One tick is 100 ms."""
import asyncio
import math
from collections import deque

INF = math.inf


def simulate(config: dict, load: dict) -> dict:
    counts = {kind: dict.fromkeys(["ok", "failed", "timedOut", "rejected", "unfinished"], 0) for kind in ("search", "profile")}
    queues = {pool: deque() for pool in config["sizes"]}  # dicts keep the order pools were listed in
    running = {pool: [] for pool in config["sizes"]}
    for t in range(load["ticks"]):
        for pool, busy in running.items():  # 1. finished work frees its worker
            for r in [r for r in busy if r["ends_at"] <= t]:
                counts[r["kind"]][r["outcome"]] += 1
            running[pool] = [r for r in busy if r["ends_at"] > t]
        for pool, queue in queues.items():  # 2. callers who waited too long give up
            for r in [r for r in queue if t - r["arrived"] >= load["client_timeout_ticks"]]:
                counts[r["kind"]]["timedOut"] += 1
            queues[pool] = deque(r for r in queue if t - r["arrived"] < load["client_timeout_ticks"])
        for kind in ("search", "profile"):  # 3. new requests arrive, or are turned away
            queue = queues[config["pools"][kind]]
            for _ in range(load["arrivals_per_tick"][kind]):
                if len(queue) >= config["queue_limit"]:
                    counts[kind]["rejected"] += 1  # load shedding: a fast "no" beats a slow one
                else:
                    queue.append({"kind": kind, "arrived": t})
        for pool, queue in queues.items():  # 4. free workers take requests, oldest first
            busy = running[pool]
            while len(busy) < config["sizes"][pool] and queue:
                r = queue.popleft()
                needs = load["service_ticks"][r["kind"]]
                limit = config["dependency_timeout_ticks"] if r["kind"] == "search" else INF
                r["ends_at"], r["outcome"] = t + min(needs, limit), "failed" if needs > limit else "ok"
                busy.append(r)
    for r in [r for q in queues.values() for r in q] + [r for b in running.values() for r in b]:
        counts[r["kind"]]["unfinished"] += 1
    return counts


def workers_needed(per_second: float, seconds: float) -> float:
    """Little's law: requests in the system = arrival rate × time each one stays."""
    return per_second * seconds


class BulkheadFull(Exception):
    pass


class Bulkhead:
    """At most max_concurrent calls at once, at most max_queue waiting, an immediate BulkheadFull beyond that.
    asyncio.Semaphore has no queue limit, so this is written out, with the place handed straight to a waiter."""

    def __init__(self, max_concurrent: int, max_queue: int):
        self.max_concurrent, self.max_queue = max_concurrent, max_queue
        self.active, self.waiting = 0, deque()

    async def run(self, fn):
        if self.active < self.max_concurrent:
            self.active += 1
        elif len(self.waiting) < self.max_queue:
            woken = asyncio.get_running_loop().create_future()
            self.waiting.append(woken)
            await woken  # woken holding a place already counted
        else:
            raise BulkheadFull(f"{self.active} running and {len(self.waiting)} waiting")
        try:
            return await fn()
        finally:
            while self.waiting and self.waiting[0].done():
                self.waiting.popleft()  # a waiter whose caller gave up (was cancelled)
            if self.waiting:
                self.waiting.popleft().set_result(None)  # hand the place over without freeing it
            else:
                self.active -= 1
```

```python
import asyncio
import unittest

from resilience import INF, Bulkhead, BulkheadFull, simulate, workers_needed

HEALTHY = {"ticks": 600, "arrivals_per_tick": {"search": 2, "profile": 3}, "service_ticks": {"search": 2, "profile": 1}, "client_timeout_ticks": 20}
DEGRADED = {**HEALTHY, "service_ticks": {"search": 50, "profile": 1}}  # search's dependency now takes 5 s
SHARED = {"pools": {"search": "shared", "profile": "shared"}, "sizes": {"shared": 50}}
BULKHEADS = {"pools": {"search": "search", "profile": "profile"}, "sizes": {"search": 20, "profile": 30}, "queue_limit": 10, "dependency_timeout_ticks": 30}


class Resilience(unittest.IsolatedAsyncioTestCase):
    def test_littles_law(self):
        self.assertEqual([workers_needed(20, 0.2) + workers_needed(30, 0.1), workers_needed(20, 5), workers_needed(20, 3), workers_needed(20, 1)],
                         [7, 100, 60, 20])

    def test_the_same_numbers_as_typescript(self):
        healthy = simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": INF}, HEALTHY)
        self.assertEqual((healthy["search"]["ok"], healthy["profile"]["ok"]), (1196, 1797))
        cascade = simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": INF}, DEGRADED)
        self.assertEqual((cascade["profile"]["ok"], cascade["profile"]["timedOut"]), (72, 1668))
        self.assertEqual(simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": 30}, DEGRADED)["profile"]["ok"], 270)
        one = simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": 10}, DEGRADED)
        self.assertEqual((one["profile"]["ok"], one["search"]["failed"]), (1797, 1180))
        walls = simulate(BULKHEADS, DEGRADED)
        self.assertEqual((walls["profile"]["ok"], walls["search"]["failed"], walls["search"]["timedOut"], walls["search"]["rejected"]), (1797, 380, 190, 600))

    async def test_a_limit_a_short_queue_and_an_immediate_no(self):
        bulkhead, gates = Bulkhead(2, 1), []

        async def work():
            gate = asyncio.Event()
            gates.append(gate)
            await gate.wait()
            return "done"

        tasks = [asyncio.create_task(bulkhead.run(work)) for _ in range(3)]
        await asyncio.sleep(0)
        self.assertEqual((bulkhead.active, len(bulkhead.waiting)), (2, 1))
        with self.assertRaises(BulkheadFull):
            await bulkhead.run(work)
        while gates or not all(t.done() for t in tasks):
            if gates:
                gates.pop(0).set()
            await asyncio.sleep(0)
        self.assertEqual([await t for t in tasks], ["done"] * 3)
        self.assertEqual((bulkhead.active, len(bulkhead.waiting)), (0, 0))

    async def test_a_freed_place_goes_to_the_waiter_not_a_latecomer(self):
        bulkhead, running, most, gates = Bulkhead(1, 1), 0, 0, []

        async def work():
            nonlocal running, most
            running += 1
            most = max(most, running)
            gate = asyncio.Event()
            gates.append(gate)
            await gate.wait()
            running -= 1

        first = asyncio.create_task(bulkhead.run(work))
        waiter = asyncio.create_task(bulkhead.run(work))
        await asyncio.sleep(0)
        gates.pop(0).set()  # first finishes...
        latecomer = asyncio.create_task(bulkhead.run(work))  # ...and someone arrives at the same moment
        for _ in range(5):
            await asyncio.sleep(0)
        self.assertEqual(most, 1)
        while gates or not all(t.done() for t in (first, waiter, latecomer)):
            if gates:
                gates.pop(0).set()
            await asyncio.sleep(0)
        self.assertEqual((bulkhead.active, len(bulkhead.waiting)), (0, 0))

    async def test_a_caller_who_gives_up_does_not_take_a_place_with_them(self):
        bulkhead, gate = Bulkhead(1, 1), asyncio.Event()
        first = asyncio.create_task(bulkhead.run(gate.wait))
        await asyncio.sleep(0)
        with self.assertRaises(TimeoutError):
            await asyncio.wait_for(bulkhead.run(gate.wait), timeout=0.01)  # the client gives up
        gate.set()
        await first
        self.assertEqual(bulkhead.active, 0)  # the place came back instead of going to the caller who left


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/python). `python3 labs/run.py resilience-patterns/python`.

## 5. Go

A buffered channel of capacity *n* is a semaphore: a send takes a place, a receive gives it back. When a place frees up and goroutines are blocked sending, the runtime moves the longest waiter's value in directly, so the hand-off is built in. A `select` with `default` tries without waiting, and an atomic counter adds the queue limit. `Config` carries the pool order as a slice, because Go maps have no order. The tests run inside `synctest.Test`, so `time.Sleep(time.Second)` takes no real time. `synctest.Wait()` returns once every goroutine is blocked, so the tests know when the queue is full. The lab runs with `-race` as well.

```go
// Package resilience: a tick-by-tick simulation of a cascade, Little's law, and a bulkhead.
// The same numbers as the TypeScript lab. One tick is 100 ms.
package resilience

import (
	"context"
	"errors"
	"math"
	"slices"
	"sync/atomic"
)

type Counts struct{ OK, Failed, TimedOut, Rejected, Unfinished int }

type Config struct {
	Pools                  map[string]string // endpoint → pool; the same pool name means a shared pool
	Order                  []string          // pool names in order: Go maps have none, and the order decides who starts first
	Sizes                  map[string]int
	QueueLimit             int // waiting requests per pool before new ones are turned away
	DependencyTimeoutTicks int
}

type Load struct {
	Ticks, ClientTimeoutTicks int
	ArrivalsPerTick           map[string]int
	ServiceTicks              map[string]int
}

type request struct {
	kind            string
	arrived, endsAt int
	failed          bool
}

var kinds = []string{"search", "profile"}

func Simulate(c Config, l Load) map[string]*Counts {
	counts := map[string]*Counts{"search": {}, "profile": {}}
	queues, running := map[string][]request{}, map[string][]request{}
	for t := range l.Ticks {
		for _, pool := range c.Order { // 1. finished work frees its worker
			running[pool] = slices.DeleteFunc(running[pool], func(r request) bool {
				if r.endsAt > t {
					return false
				}
				if r.failed {
					counts[r.kind].Failed++
				} else {
					counts[r.kind].OK++
				}
				return true
			})
		}
		for _, pool := range c.Order { // 2. callers who waited too long give up
			queues[pool] = slices.DeleteFunc(queues[pool], func(r request) bool {
				gaveUp := t-r.arrived >= l.ClientTimeoutTicks
				if gaveUp {
					counts[r.kind].TimedOut++
				}
				return gaveUp
			})
		}
		for _, kind := range kinds { // 3. new requests arrive, or are turned away
			pool := c.Pools[kind]
			for range l.ArrivalsPerTick[kind] {
				if len(queues[pool]) >= c.QueueLimit {
					counts[kind].Rejected++ // load shedding
				} else {
					queues[pool] = append(queues[pool], request{kind: kind, arrived: t})
				}
			}
		}
		for _, pool := range c.Order { // 4. free workers take requests, oldest first
			for len(running[pool]) < c.Sizes[pool] && len(queues[pool]) > 0 {
				r := queues[pool][0]
				queues[pool] = queues[pool][1:]
				needs, limit := l.ServiceTicks[r.kind], math.MaxInt
				if r.kind == "search" {
					limit = c.DependencyTimeoutTicks
				}
				r.endsAt, r.failed = t+min(needs, limit), needs > limit
				running[pool] = append(running[pool], r)
			}
		}
	}
	for _, pool := range c.Order {
		for _, r := range append(queues[pool], running[pool]...) {
			counts[r.kind].Unfinished++
		}
	}
	return counts
}

// WorkersNeeded is Little's law: requests in the system = arrival rate × time each one stays.
func WorkersNeeded(perSecond, seconds float64) float64 { return perSecond * seconds }

var ErrBulkheadFull = errors.New("bulkhead full")

// Bulkhead is a buffered channel used as a semaphore: a send takes a place, a receive gives it back.
// When a place frees up and a goroutine is blocked sending, the runtime hands the place straight to
// it, so a latecomer can't slip in: the bug from the main lesson can't happen here.
type Bulkhead struct {
	places   chan struct{}
	waiting  atomic.Int64
	maxQueue int64
}

func NewBulkhead(maxConcurrent, maxQueue int) *Bulkhead {
	return &Bulkhead{places: make(chan struct{}, maxConcurrent), maxQueue: int64(maxQueue)}
}

func (b *Bulkhead) Run(ctx context.Context, fn func() error) error {
	select {
	case b.places <- struct{}{}: // a free place, at once
	default:
		if b.waiting.Add(1) > b.maxQueue {
			b.waiting.Add(-1)
			return ErrBulkheadFull // a fast "no" now beats a slow failure later
		}
		select {
		case b.places <- struct{}{}:
			b.waiting.Add(-1)
		case <-ctx.Done(): // a caller who stops waiting leaves the queue
			b.waiting.Add(-1)
			return ctx.Err()
		}
	}
	defer func() { <-b.places }()
	return fn()
}
```

```go
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
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/go). `python3 labs/run.py resilience-patterns/go`.

## 6. Java

`new Semaphore(n, true)` is fair: places go to threads in the order they asked. Fairness only holds for the timed `tryAcquire(timeout, unit)` and `acquire`. The no-argument `tryAcquire()` takes a free place even with threads waiting, which is barging on purpose. A `LinkedHashMap` keeps the pool order. The checks use **virtual threads** (`Executors.newVirtualThreadPerTaskExecutor()`), so 200 concurrent calls cost 200 small objects rather than 200 operating-system threads.

```java
package resilience;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/** A tick-by-tick simulation of a cascade, Little's law, and a bulkhead. The same numbers as the TypeScript lab. One tick is 100 ms. */
public final class Resilience {
    private Resilience() {}

    public enum Kind { SEARCH, PROFILE }

    public static final class Counts {
        public int ok, failed, timedOut, rejected, unfinished;

        @Override public String toString() {
            return "ok=%d failed=%d timedOut=%d rejected=%d unfinished=%d".formatted(ok, failed, timedOut, rejected, unfinished);
        }
    }

    /** pools: endpoint → pool name (the same name means a shared pool). sizes is a LinkedHashMap: its order decides who starts first. */
    public record Config(Map<Kind, String> pools, LinkedHashMap<String, Integer> sizes, int queueLimit, int dependencyTimeoutTicks) {}

    public record Load(int ticks, Map<Kind, Integer> arrivalsPerTick, Map<Kind, Integer> serviceTicks, int clientTimeoutTicks) {}

    private static final class Request {
        final Kind kind;
        final int arrived;
        int endsAt;
        boolean failed;

        Request(Kind kind, int arrived) { this.kind = kind; this.arrived = arrived; }
    }

    public static Map<Kind, Counts> simulate(Config c, Load l) {
        var counts = new EnumMap<Kind, Counts>(Kind.class);
        for (var k : Kind.values()) counts.put(k, new Counts());
        var queues = new LinkedHashMap<String, ArrayDeque<Request>>();
        var running = new LinkedHashMap<String, List<Request>>();
        c.sizes().keySet().forEach(pool -> { queues.put(pool, new ArrayDeque<>()); running.put(pool, new ArrayList<>()); });
        for (int t = 0; t < l.ticks(); t++) {
            final int now = t;
            running.values().forEach(busy -> busy.removeIf(r -> { // 1. finished work frees its worker
                if (r.endsAt > now) return false;
                if (r.failed) counts.get(r.kind).failed++; else counts.get(r.kind).ok++;
                return true;
            }));
            queues.values().forEach(queue -> queue.removeIf(r -> { // 2. callers who waited too long give up
                boolean gaveUp = now - r.arrived >= l.clientTimeoutTicks();
                if (gaveUp) counts.get(r.kind).timedOut++;
                return gaveUp;
            }));
            for (var kind : Kind.values()) { // 3. new requests arrive, or are turned away
                var queue = queues.get(c.pools().get(kind));
                for (int i = 0; i < l.arrivalsPerTick().get(kind); i++) {
                    if (queue.size() >= c.queueLimit()) counts.get(kind).rejected++; // load shedding
                    else queue.add(new Request(kind, t));
                }
            }
            for (var pool : c.sizes().keySet()) { // 4. free workers take requests, oldest first
                var queue = queues.get(pool);
                var busy = running.get(pool);
                while (busy.size() < c.sizes().get(pool) && !queue.isEmpty()) {
                    var r = queue.poll();
                    int needs = l.serviceTicks().get(r.kind);
                    int limit = r.kind == Kind.SEARCH ? c.dependencyTimeoutTicks() : Integer.MAX_VALUE;
                    r.endsAt = t + Math.min(needs, limit);
                    r.failed = needs > limit;
                    busy.add(r);
                }
            }
        }
        queues.values().forEach(q -> q.forEach(r -> counts.get(r.kind).unfinished++));
        running.values().forEach(b -> b.forEach(r -> counts.get(r.kind).unfinished++));
        return counts;
    }

    /** Little's law: requests in the system = arrival rate × time each one stays. */
    public static double workersNeeded(double perSecond, double seconds) { return perSecond * seconds; }

    public static final class BulkheadFull extends RuntimeException {
        private static final long serialVersionUID = 1L;
        BulkheadFull(String message) { super(message); }
    }

    /**
     * A fair Semaphore: when a place frees up it goes to the thread that has waited longest, so a latecomer can't barge in.
     * (new Semaphore(n) without "true" is unfair on purpose: faster, but a waiter can be passed over.)
     * Semaphore has no queue limit, so a counter turns away callers beyond maxQueue.
     */
    public static final class Bulkhead {
        private final Semaphore places;
        private final AtomicInteger waiting = new AtomicInteger();
        private final int maxQueue;

        public Bulkhead(int maxConcurrent, int maxQueue) {
            this.places = new Semaphore(maxConcurrent, true);
            this.maxQueue = maxQueue;
        }

        public <T> T run(Callable<T> fn, long maxWaitMillis) throws Exception {
            if (!places.tryAcquire(0, TimeUnit.MILLISECONDS)) { // the timed form respects fairness; plain tryAcquire() barges
                if (waiting.incrementAndGet() > maxQueue) {
                    waiting.decrementAndGet();
                    throw new BulkheadFull("%d waiting already".formatted(maxQueue)); // a fast "no" beats a slow failure
                }
                try {
                    if (!places.tryAcquire(maxWaitMillis, TimeUnit.MILLISECONDS)) throw new BulkheadFull("no place within " + maxWaitMillis + " ms");
                } finally {
                    waiting.decrementAndGet();
                }
            }
            try {
                return fn.call();
            } finally {
                places.release();
            }
        }

        public int waiting() { return waiting.get(); }
        public int free() { return places.availablePermits(); }
    }
}
```

```java
package resilience;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import resilience.Resilience.Bulkhead;
import resilience.Resilience.BulkheadFull;
import resilience.Resilience.Config;
import resilience.Resilience.Kind;
import resilience.Resilience.Load;

/** Checks, run with `java -ea`. The same numbers as every other language. */
public final class ResilienceCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static final int NONE = Integer.MAX_VALUE;
    static final Load HEALTHY = new Load(600, Map.of(Kind.SEARCH, 2, Kind.PROFILE, 3), Map.of(Kind.SEARCH, 2, Kind.PROFILE, 1), 20);
    static final Load DEGRADED = new Load(600, HEALTHY.arrivalsPerTick(), Map.of(Kind.SEARCH, 50, Kind.PROFILE, 1), 20);

    static <V> LinkedHashMap<String, V> ordered(String k1, V v1, String k2, V v2) {
        var m = new LinkedHashMap<String, V>();
        m.put(k1, v1);
        if (k2 != null) m.put(k2, v2);
        return m;
    }

    static Config shared(int timeout) {
        return new Config(Map.of(Kind.SEARCH, "shared", Kind.PROFILE, "shared"), ordered("shared", 50, null, null), NONE, timeout);
    }

    public static void main(String[] args) throws Exception {
        check(Resilience.workersNeeded(20, 0.2) + Resilience.workersNeeded(30, 0.1) == 7 && Resilience.workersNeeded(20, 5) == 100, "little");

        var healthy = Resilience.simulate(shared(NONE), HEALTHY);
        check(healthy.get(Kind.SEARCH).ok == 1196 && healthy.get(Kind.PROFILE).ok == 1797, healthy);
        var cascade = Resilience.simulate(shared(NONE), DEGRADED).get(Kind.PROFILE);
        check(cascade.ok == 72 && cascade.timedOut == 1668, cascade);
        check(Resilience.simulate(shared(30), DEGRADED).get(Kind.PROFILE).ok == 270, "3 s timeout");
        var one = Resilience.simulate(shared(10), DEGRADED);
        check(one.get(Kind.PROFILE).ok == 1797 && one.get(Kind.SEARCH).failed == 1180, one);
        var walls = new Config(Map.of(Kind.SEARCH, "search", Kind.PROFILE, "profile"), ordered("search", 20, "profile", 30), 10, 30);
        var w = Resilience.simulate(walls, DEGRADED);
        check(w.get(Kind.PROFILE).ok == 1797 && w.get(Kind.SEARCH).toString().equals("ok=0 failed=380 timedOut=190 rejected=600 unfinished=30"), w);

        try (var pool = Executors.newVirtualThreadPerTaskExecutor()) { // a thread per call is cheap with virtual threads
            // A limit, a short queue, and an immediate no.
            var bulkhead = new Bulkhead(2, 1);
            var release = new CountDownLatch(1);
            var started = new CountDownLatch(2);
            var calls = new ArrayList<Future<String>>();
            for (int i = 0; i < 3; i++) calls.add(pool.submit(() -> bulkhead.run(() -> { started.countDown(); release.await(); return "done"; }, 5_000)));
            started.await();
            while (bulkhead.waiting() < 1) Thread.onSpinWait();
            try {
                bulkhead.run(() -> "never", 5_000);
                check(false, "a fourth call should be turned away");
            } catch (BulkheadFull expected) {
                // turned away at once, without waiting
            }
            release.countDown();
            for (var call : calls) check(call.get().equals("done"), "done");
            check(bulkhead.free() == 2 && bulkhead.waiting() == 0, "all places back");

            // Never more than the limit, however the threads interleave.
            var three = new Bulkhead(3, 1000);
            var running = new AtomicInteger();
            var most = new AtomicInteger();
            var all = new ArrayList<Future<Integer>>();
            for (int i = 0; i < 200; i++) {
                all.add(pool.submit(() -> three.run(() -> {
                    most.accumulateAndGet(running.incrementAndGet(), Math::max);
                    Thread.sleep(1);
                    return running.decrementAndGet();
                }, 60_000)));
            }
            for (var f : all) f.get();
            check(most.get() <= 3, most.get() + " ran at once in a bulkhead of three");

            // A caller who stops waiting leaves the queue and doesn't take a place with them.
            var small = new Bulkhead(1, 1);
            var hold = new CountDownLatch(1);
            var first = pool.submit(() -> small.run(() -> { hold.await(); return "first"; }, 5_000));
            while (small.free() == 1) Thread.onSpinWait();
            try {
                small.run(() -> "never", 20);
                check(false, "should give up");
            } catch (BulkheadFull expected) {
                check(small.waiting() == 0, "left the queue");
            }
            hold.countDown();
            check(first.get().equals("first") && small.free() == 1, "the place came back");
        }
        System.out.println("all resilience checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/java). `python3 labs/run.py resilience-patterns/java`.

## 7. Rust

tokio's `Semaphore` is fair by design, and `acquire` returns a **permit** that gives the place back when it's dropped, even if the work panics. Wrapping `acquire` in `tokio::time::timeout` handles giving up: on timeout the acquire future is dropped, which takes the caller out of the queue. The simulation keeps its counts in an array indexed by `kind as usize`. A closure returning `&mut` into captured counts wouldn't compile, because the borrow would outlive the call. The tests use `#[tokio::test(start_paused = true)]`, a fake clock under which the 1-second jobs finish in no real time and in a fixed order.

```rust
//! A tick-by-tick simulation of a cascade, Little's law, and a bulkhead.
//! The same numbers as the TypeScript lab. One tick is 100 ms.
use std::collections::VecDeque;
use std::future::Future;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;
use tokio::sync::Semaphore;

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Kind {
    Search,
    Profile,
}
const KINDS: [Kind; 2] = [Kind::Search, Kind::Profile];

#[derive(Default, Debug, PartialEq)]
pub struct Counts {
    pub ok: usize,
    pub failed: usize,
    pub timed_out: usize,
    pub rejected: usize,
    pub unfinished: usize,
}

pub struct Config {
    /// The pool each kind uses, as an index into `sizes`: the same index means a shared pool.
    pub pool_of: fn(Kind) -> usize,
    /// Workers per pool, in the order pools start work.
    pub sizes: Vec<usize>,
    pub queue_limit: usize,
    pub dependency_timeout_ticks: usize,
}

pub struct Load {
    pub ticks: usize,
    pub arrivals_per_tick: fn(Kind) -> usize,
    pub service_ticks: fn(Kind) -> usize,
    pub client_timeout_ticks: usize,
}

struct Request {
    kind: Kind,
    arrived: usize,
    ends_at: usize,
    failed: bool,
}

/// Returns (search, profile) counts.
pub fn simulate(c: &Config, l: &Load) -> (Counts, Counts) {
    let mut counts: [Counts; 2] = Default::default(); // indexed by `kind as usize`
    let mut queues: Vec<VecDeque<Request>> = c.sizes.iter().map(|_| VecDeque::new()).collect();
    let mut running: Vec<Vec<Request>> = c.sizes.iter().map(|_| Vec::new()).collect();
    for t in 0..l.ticks {
        for busy in &mut running {
            // 1. finished work frees its worker
            busy.retain(|r| {
                if r.ends_at > t {
                    return true;
                }
                if r.failed {
                    counts[r.kind as usize].failed += 1;
                } else {
                    counts[r.kind as usize].ok += 1;
                }
                false
            });
        }
        for queue in &mut queues {
            // 2. callers who waited too long give up
            queue.retain(|r| {
                let gave_up = t - r.arrived >= l.client_timeout_ticks;
                if gave_up {
                    counts[r.kind as usize].timed_out += 1;
                }
                !gave_up
            });
        }
        for kind in KINDS {
            // 3. new requests arrive, or are turned away
            let queue = &mut queues[(c.pool_of)(kind)];
            for _ in 0..(l.arrivals_per_tick)(kind) {
                if queue.len() >= c.queue_limit {
                    counts[kind as usize].rejected += 1; // load shedding
                } else {
                    queue.push_back(Request {
                        kind,
                        arrived: t,
                        ends_at: 0,
                        failed: false,
                    });
                }
            }
        }
        for (pool, queue) in queues.iter_mut().enumerate() {
            // 4. free workers take requests, oldest first
            while running[pool].len() < c.sizes[pool] {
                let Some(mut r) = queue.pop_front() else {
                    break;
                };
                let needs = (l.service_ticks)(r.kind);
                let limit = if r.kind == Kind::Search {
                    c.dependency_timeout_ticks
                } else {
                    usize::MAX
                };
                (r.ends_at, r.failed) = (t + needs.min(limit), needs > limit);
                running[pool].push(r);
            }
        }
    }
    for r in queues.iter().flatten().chain(running.iter().flatten()) {
        counts[r.kind as usize].unfinished += 1;
    }
    let [search, profile] = counts;
    (search, profile)
}

/// Little's law: requests in the system = arrival rate × time each one stays.
pub fn workers_needed(per_second: f64, seconds: f64) -> f64 {
    per_second * seconds
}

#[derive(Debug, PartialEq)]
pub enum Refused {
    Full,
    WaitedTooLong,
}

/// tokio's Semaphore is fair: places go to waiters in the order they asked, so a latecomer can't barge in.
/// It has no queue limit, so a counter turns away callers beyond `max_queue`.
pub struct Bulkhead {
    places: Semaphore,
    waiting: AtomicUsize,
    max_queue: usize,
}

impl Bulkhead {
    pub fn new(max_concurrent: usize, max_queue: usize) -> Self {
        Self {
            places: Semaphore::new(max_concurrent),
            waiting: AtomicUsize::new(0),
            max_queue,
        }
    }

    pub async fn run<T>(
        &self,
        max_wait: Duration,
        f: impl Future<Output = T>,
    ) -> Result<T, Refused> {
        let _place = match self.places.try_acquire() {
            Ok(place) => place,
            Err(_) => {
                if self.waiting.fetch_add(1, Ordering::SeqCst) >= self.max_queue {
                    self.waiting.fetch_sub(1, Ordering::SeqCst);
                    return Err(Refused::Full); // a fast "no" beats a slow failure
                }
                // Dropping the acquire future on timeout takes the caller out of the queue.
                let got = tokio::time::timeout(max_wait, self.places.acquire()).await;
                self.waiting.fetch_sub(1, Ordering::SeqCst);
                got.map_err(|_| Refused::WaitedTooLong)?
                    .expect("never closed")
            }
        };
        Ok(f.await) // the place goes back when _place is dropped, even if f panics
    }

    pub fn free(&self) -> usize {
        self.places.available_permits()
    }

    pub fn waiting(&self) -> usize {
        self.waiting.load(Ordering::SeqCst)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use tokio::sync::Notify;

    const NONE: usize = usize::MAX;
    fn healthy() -> Load {
        Load {
            ticks: 600,
            arrivals_per_tick: |k| if k == Kind::Search { 2 } else { 3 },
            service_ticks: |k| if k == Kind::Search { 2 } else { 1 },
            client_timeout_ticks: 20,
        }
    }
    fn degraded() -> Load {
        Load {
            service_ticks: |k| if k == Kind::Search { 50 } else { 1 },
            ..healthy()
        }
    }
    fn shared(timeout: usize) -> Config {
        Config {
            pool_of: |_| 0,
            sizes: vec![50],
            queue_limit: NONE,
            dependency_timeout_ticks: timeout,
        }
    }

    #[test]
    fn littles_law() {
        assert_eq!(workers_needed(20.0, 0.2) + workers_needed(30.0, 0.1), 7.0);
        assert_eq!(workers_needed(20.0, 5.0), 100.0);
    }

    #[test]
    fn the_same_numbers_as_typescript() {
        let (search, profile) = simulate(&shared(NONE), &healthy());
        assert_eq!((search.ok, profile.ok), (1196, 1797));
        let (_, profile) = simulate(&shared(NONE), &degraded());
        assert_eq!((profile.ok, profile.timed_out), (72, 1668));
        assert_eq!(simulate(&shared(30), &degraded()).1.ok, 270);
        let (search, profile) = simulate(&shared(10), &degraded());
        assert_eq!((profile.ok, search.failed), (1797, 1180));
        let walls = Config {
            pool_of: |k| if k == Kind::Search { 0 } else { 1 },
            sizes: vec![20, 30],
            queue_limit: 10,
            dependency_timeout_ticks: 30,
        };
        let (search, profile) = simulate(&walls, &degraded());
        assert_eq!(profile.ok, 1797);
        assert_eq!(
            search,
            Counts {
                ok: 0,
                failed: 380,
                timed_out: 190,
                rejected: 600,
                unfinished: 30
            }
        );
    }

    #[tokio::test(start_paused = true)] // a fake clock: the waits below take no real time
    async fn a_limit_a_short_queue_and_an_immediate_no() {
        let bulkhead = Arc::new(Bulkhead::new(2, 1));
        let release = Arc::new(Notify::new());
        let calls: Vec<_> = (0..3)
            .map(|_| {
                let (b, r) = (bulkhead.clone(), release.clone());
                tokio::spawn(async move { b.run(Duration::from_secs(5), r.notified()).await })
            })
            .collect();
        while bulkhead.waiting() < 1 {
            tokio::task::yield_now().await;
        }
        assert_eq!(
            bulkhead.run(Duration::from_secs(5), async {}).await,
            Err(Refused::Full)
        );
        for _ in 0..3 {
            release.notify_one();
            tokio::task::yield_now().await;
        }
        for call in calls {
            assert_eq!(call.await.unwrap(), Ok(()));
        }
        assert_eq!((bulkhead.free(), bulkhead.waiting()), (2, 0));
    }

    #[tokio::test(start_paused = true)]
    async fn a_freed_place_goes_to_the_waiter_not_a_latecomer() {
        let bulkhead = Arc::new(Bulkhead::new(1, 2));
        let order = Arc::new(std::sync::Mutex::new(Vec::new()));
        let call = |name: &'static str, delay_ms: u64| {
            let (b, o) = (bulkhead.clone(), order.clone());
            tokio::spawn(async move {
                tokio::time::sleep(Duration::from_millis(delay_ms)).await;
                b.run(Duration::from_secs(5), async {
                    o.lock().unwrap().push(name);
                    tokio::time::sleep(Duration::from_secs(1)).await;
                })
                .await
            })
        };
        let calls = [
            call("first", 0),
            call("waiter", 10),
            call("latecomer", 1000),
        ]; // arrives as first finishes
        for c in calls {
            c.await.unwrap().unwrap();
        }
        assert_eq!(*order.lock().unwrap(), ["first", "waiter", "latecomer"]);
    }

    #[tokio::test(start_paused = true)]
    async fn a_caller_who_stops_waiting_leaves_the_queue() {
        let bulkhead = Arc::new(Bulkhead::new(1, 1));
        let release = Arc::new(Notify::new());
        let (b, r) = (bulkhead.clone(), release.clone());
        let first = tokio::spawn(async move { b.run(Duration::from_secs(5), r.notified()).await });
        tokio::task::yield_now().await;
        assert_eq!(
            bulkhead.run(Duration::from_secs(2), async {}).await,
            Err(Refused::WaitedTooLong)
        );
        assert_eq!(bulkhead.waiting(), 0);
        release.notify_one();
        first.await.unwrap().unwrap();
        assert_eq!(bulkhead.free(), 1); // the place came back instead of going to the caller who left
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/rust). `python3 labs/run.py resilience-patterns/rust`.

## 8. C

POSIX `sem_t` makes no promise about order, so the bulkhead is a mutex and a condition variable with **tickets**. Each waiter takes the next number. A finishing call doesn't free its place: it calls the next number and wakes everyone, and only the waiter holding that number goes. The waiter checks in a `while` loop, because condition variables can wake spuriously. The simulation uses fixed-size arrays and a ring buffer, with no allocation. Plain C17 has no sleep function, so the file asks for POSIX with `_POSIX_C_SOURCE` and uses `nanosleep`.

```c
// A tick-by-tick simulation of a cascade, and a bulkhead that serves waiters in order.
// The same numbers as the TypeScript lab. One tick is 100 ms. Checks run in main.
#define _POSIX_C_SOURCE 200809L // for nanosleep: plain C17 has no way to sleep
#include <assert.h>
#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <time.h>

enum kind { SEARCH, PROFILE, KINDS };
struct counts { int ok, failed, timed_out, rejected, unfinished; };
struct config { int pool_of[KINDS], pools, sizes[2], queue_limit, dependency_timeout_ticks; };
struct load { int ticks, arrivals_per_tick[KINDS], service_ticks[KINDS], client_timeout_ticks; };
struct request { enum kind kind; int arrived, ends_at, failed; };

#define MAX_QUEUE 4096 // more than 600 ticks × 5 arrivals: no request is ever dropped for lack of room

struct pool {
    struct request queue[MAX_QUEUE], running[64];
    int head, len, busy; // the queue is queue[head .. head+len)
};

static void simulate(const struct config *c, const struct load *l, struct counts out[KINDS]) {
    static struct pool pools[2]; // too big for the stack
    for (int p = 0; p < c->pools; p++) pools[p].head = pools[p].len = pools[p].busy = 0;
    for (int k = 0; k < KINDS; k++) out[k] = (struct counts){0};
    for (int t = 0; t < l->ticks; t++) {
        for (int p = 0; p < c->pools; p++) { // 1. finished work frees its worker
            struct pool *pl = &pools[p];
            int kept = 0;
            for (int i = 0; i < pl->busy; i++) {
                struct request r = pl->running[i];
                if (r.ends_at > t) pl->running[kept++] = r;
                else if (r.failed) out[r.kind].failed++;
                else out[r.kind].ok++;
            }
            pl->busy = kept;
        }
        for (int p = 0; p < c->pools; p++) { // 2. callers who waited too long give up (the oldest are at the front)
            struct pool *pl = &pools[p];
            while (pl->len > 0 && t - pl->queue[pl->head].arrived >= l->client_timeout_ticks) {
                out[pl->queue[pl->head].kind].timed_out++;
                pl->head = (pl->head + 1) % MAX_QUEUE, pl->len--;
            }
        }
        for (int k = 0; k < KINDS; k++) { // 3. new requests arrive, or are turned away
            struct pool *pl = &pools[c->pool_of[k]];
            for (int i = 0; i < l->arrivals_per_tick[k]; i++) {
                if (pl->len >= c->queue_limit) out[k].rejected++; // load shedding
                else pl->queue[(pl->head + pl->len++) % MAX_QUEUE] = (struct request){k, t, 0, 0};
            }
        }
        for (int p = 0; p < c->pools; p++) { // 4. free workers take requests, oldest first
            struct pool *pl = &pools[p];
            while (pl->busy < c->sizes[p] && pl->len > 0) {
                struct request r = pl->queue[pl->head];
                pl->head = (pl->head + 1) % MAX_QUEUE, pl->len--;
                int needs = l->service_ticks[r.kind], limit = r.kind == SEARCH ? c->dependency_timeout_ticks : INT_MAX;
                r.ends_at = t + (needs < limit ? needs : limit), r.failed = needs > limit;
                pl->running[pl->busy++] = r;
            }
        }
    }
    for (int p = 0; p < c->pools; p++) {
        for (int i = 0; i < pools[p].len; i++) out[pools[p].queue[(pools[p].head + i) % MAX_QUEUE].kind].unfinished++;
        for (int i = 0; i < pools[p].busy; i++) out[pools[p].running[i].kind].unfinished++;
    }
}

// A bulkhead: at most max_concurrent at once, at most max_queue waiting, an immediate "no" beyond that.
// Each waiter takes a ticket, like at a deli counter. A finishing call doesn't free its place: it calls
// the next ticket, so the place passes straight to the longest waiter and a latecomer can't barge in.
struct bulkhead {
    pthread_mutex_t lock;
    pthread_cond_t called;
    int max_concurrent, max_queue, active, waiting;
    unsigned long next_ticket, now_serving;
};

#define BULKHEAD_INIT(n, q) {PTHREAD_MUTEX_INITIALIZER, PTHREAD_COND_INITIALIZER, (n), (q), 0, 0, 0, 0}

// Returns 0 and runs fn, or returns -1 at once if the bulkhead is full.
static int bulkhead_run(struct bulkhead *b, void (*fn)(void *), void *arg) {
    pthread_mutex_lock(&b->lock);
    if (b->active < b->max_concurrent) {
        b->active++;
    } else if (b->waiting < b->max_queue) {
        unsigned long mine = b->next_ticket++;
        b->waiting++;
        while (b->now_serving <= mine) pthread_cond_wait(&b->called, &b->lock); // woken spuriously? wait again
    } else {
        pthread_mutex_unlock(&b->lock);
        return -1; // a fast "no" beats a slow failure
    }
    pthread_mutex_unlock(&b->lock);
    fn(arg);
    pthread_mutex_lock(&b->lock);
    if (b->waiting > 0) {
        b->waiting--;
        b->now_serving++; // hand the place over: active stays the same
        pthread_cond_broadcast(&b->called); // every waiter checks; only the one called goes
    } else {
        b->active--;
    }
    pthread_mutex_unlock(&b->lock);
    return 0;
}

static int waiting(struct bulkhead *b) {
    pthread_mutex_lock(&b->lock);
    int w = b->waiting;
    pthread_mutex_unlock(&b->lock);
    return w;
}

static void nap(long microseconds) {
    nanosleep(&(struct timespec){0, microseconds * 1000}, NULL);
}

// Test helpers: a call that holds its place until released, and records the order calls started in.
static atomic_int release_count, running_now, most, started_order[8], started;

static void hold(void *name) {
    started_order[atomic_fetch_add(&started, 1)] = (int)(long)name;
    int n = atomic_fetch_add(&running_now, 1) + 1;
    for (int m = atomic_load(&most); n > m && !atomic_compare_exchange_weak(&most, &m, n);) {}
    for (int r;;) { // wait to be released, taking one release
        r = atomic_load(&release_count);
        if (r > 0 && atomic_compare_exchange_weak(&release_count, &r, r - 1)) break;
        nap(100);
    }
    atomic_fetch_sub(&running_now, 1);
}

struct call { struct bulkhead *b; long name; int result; };
static void *caller(void *arg) {
    struct call *c = arg;
    c->result = bulkhead_run(c->b, hold, (void *)c->name);
    return NULL;
}

static void quick(void *arg) {
    int n = atomic_fetch_add(&running_now, 1) + 1;
    for (int m = atomic_load(&most); n > m && !atomic_compare_exchange_weak(&most, &m, n);) {}
    nap(50);
    atomic_fetch_sub(&running_now, 1);
    (void)arg;
}
static void *quick_caller(void *b) {
    while (bulkhead_run(b, quick, NULL) != 0) nap(10); // full? try again shortly
    return NULL;
}

int main(void) {
    const struct load healthy = {600, {2, 3}, {2, 1}, 20}, degraded = {600, {2, 3}, {50, 1}, 20};
    struct config shared = {{0, 0}, 1, {50}, INT_MAX, INT_MAX};
    struct counts out[KINDS];

    simulate(&shared, &healthy, out);
    assert(out[SEARCH].ok == 1196 && out[PROFILE].ok == 1797);
    simulate(&shared, &degraded, out);
    assert(out[PROFILE].ok == 72 && out[PROFILE].timed_out == 1668); // the cascade
    shared.dependency_timeout_ticks = 30;
    simulate(&shared, &degraded, out);
    assert(out[PROFILE].ok == 270);
    shared.dependency_timeout_ticks = 10;
    simulate(&shared, &degraded, out);
    assert(out[PROFILE].ok == 1797 && out[SEARCH].failed == 1180);
    const struct config walls = {{0, 1}, 2, {20, 30}, 10, 30};
    simulate(&walls, &degraded, out);
    assert(out[PROFILE].ok == 1797);
    assert(out[SEARCH].failed == 380 && out[SEARCH].timed_out == 190 && out[SEARCH].rejected == 600 && out[SEARCH].unfinished == 30);

    // A limit, a short queue, an immediate no, and waiters served in the order they came.
    struct bulkhead b = BULKHEAD_INIT(1, 2);
    struct call calls[3] = {{&b, 1, 9}, {&b, 2, 9}, {&b, 3, 9}};
    pthread_t threads[3];
    pthread_create(&threads[0], NULL, caller, &calls[0]);
    while (atomic_load(&started) < 1) nap(100);
    for (int i = 1; i < 3; i++) { // queue 2, then 3, in that order
        pthread_create(&threads[i], NULL, caller, &calls[i]);
        while (waiting(&b) < i) nap(100);
    }
    struct call fourth = {&b, 4, 9};
    caller(&fourth);
    assert(fourth.result == -1);
    atomic_store(&release_count, 3);
    for (int i = 0; i < 3; i++) pthread_join(threads[i], NULL), assert(calls[i].result == 0);
    assert(started_order[0] == 1 && started_order[1] == 2 && started_order[2] == 3);
    assert(b.active == 0 && b.waiting == 0);

    // Never more than the limit, however the threads interleave.
    struct bulkhead three = BULKHEAD_INIT(3, 5);
    pthread_t many[40];
    atomic_store(&most, 0);
    for (int i = 0; i < 40; i++) pthread_create(&many[i], NULL, quick_caller, &three);
    for (int i = 0; i < 40; i++) pthread_join(many[i], NULL);
    assert(atomic_load(&most) <= 3 && three.active == 0);

    puts("all resilience checks passed");
}
```

**Lab:** [`labs/c/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/c). `python3 labs/run.py resilience-patterns/c`.

## 9. C++

`std::counting_semaphore` makes no promise about order either. Instead of tickets, this bulkhead keeps a `std::list` of waiter flags. A list entry stays put while others come and go, so a waiter who gives up can erase its own entry. A finishing call marks the first unmarked entry as called. `wait_for` with a predicate handles spurious wakeups and the timeout in one call. The place is given back in a destructor, so it comes back even if the work throws. The test threads are `std::jthread`, which join themselves when they go out of scope.

```cpp
// A tick-by-tick simulation of a cascade, and a bulkhead that hands places to waiters in order.
// The same numbers as the TypeScript lab. One tick is 100 ms. Checks run in main.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <climits>
#include <condition_variable>
#include <deque>
#include <iostream>
#include <list>
#include <map>
#include <mutex>
#include <string>
#include <thread>
#include <variant>
#include <vector>

enum class Kind { search, profile };
struct Counts {
    int ok = 0, failed = 0, timed_out = 0, rejected = 0, unfinished = 0;
    bool operator==(const Counts &) const = default;
};
struct Config {
    std::map<Kind, int> pool_of; // the pool each kind uses: the same number means a shared pool
    std::vector<int> sizes;      // workers per pool, in the order pools start work
    int queue_limit, dependency_timeout_ticks;
};
struct Load {
    int ticks;
    std::map<Kind, int> arrivals_per_tick, service_ticks;
    int client_timeout_ticks;
};

std::map<Kind, Counts> simulate(const Config &c, const Load &l) {
    struct Request { Kind kind; int arrived, ends_at = 0; bool failed = false; };
    std::map<Kind, Counts> counts{{Kind::search, {}}, {Kind::profile, {}}};
    std::vector<std::deque<Request>> queues(c.sizes.size());
    std::vector<std::vector<Request>> running(c.sizes.size());
    for (int t = 0; t < l.ticks; t++) {
        for (auto &busy : running) // 1. finished work frees its worker
            std::erase_if(busy, [&](const Request &r) {
                if (r.ends_at > t) return false;
                (r.failed ? counts[r.kind].failed : counts[r.kind].ok)++;
                return true;
            });
        for (auto &queue : queues) // 2. callers who waited too long give up
            std::erase_if(queue, [&](const Request &r) {
                bool gave_up = t - r.arrived >= l.client_timeout_ticks;
                if (gave_up) counts[r.kind].timed_out++;
                return gave_up;
            });
        for (Kind kind : {Kind::search, Kind::profile}) { // 3. new requests arrive, or are turned away
            auto &queue = queues[c.pool_of.at(kind)];
            for (int i = 0; i < l.arrivals_per_tick.at(kind); i++) {
                if (std::ssize(queue) >= c.queue_limit) counts[kind].rejected++; // load shedding
                else queue.push_back({kind, t});
            }
        }
        for (size_t pool = 0; pool < queues.size(); pool++) { // 4. free workers take requests, oldest first
            while (std::ssize(running[pool]) < c.sizes[pool] && !queues[pool].empty()) {
                Request r = queues[pool].front();
                queues[pool].pop_front();
                int needs = l.service_ticks.at(r.kind), limit = r.kind == Kind::search ? c.dependency_timeout_ticks : INT_MAX;
                r.ends_at = t + std::min(needs, limit), r.failed = needs > limit;
                running[pool].push_back(r);
            }
        }
    }
    for (auto &q : queues) for (auto &r : q) counts[r.kind].unfinished++;
    for (auto &b : running) for (auto &r : b) counts[r.kind].unfinished++;
    return counts;
}

// A bulkhead: at most max_concurrent at once, at most max_queue waiting, an immediate "no" beyond that.
// std::counting_semaphore makes no promise about who goes next, so this keeps its own line of waiters.
// A finishing call doesn't free its place: it gives it to the front of the line, so no latecomer barges in.
class Bulkhead {
    std::mutex lock_;
    std::condition_variable called_;
    std::list<bool> line_; // one entry per waiter: true once it has been given a place
    int max_concurrent_, max_queue_, active_ = 0;

public:
    Bulkhead(int max_concurrent, int max_queue) : max_concurrent_(max_concurrent), max_queue_(max_queue) {}

    enum class Refused { full, waited_too_long };

    // The result of fn, or why the call was refused.
    template <class F>
    std::variant<std::invoke_result_t<F>, Refused> run(F fn, std::chrono::milliseconds max_wait) {
        {
            std::unique_lock held(lock_);
            if (active_ < max_concurrent_) {
                active_++;
            } else if (std::ssize(line_) < max_queue_) {
                auto mine = line_.insert(line_.end(), false);
                if (!called_.wait_for(held, max_wait, [&] { return *mine; })) { // false: timed out, still not called
                    line_.erase(mine); // leave the line; no place to give back
                    return Refused::waited_too_long;
                }
                line_.erase(mine); // called: the place passed from the finishing call is ours
            } else {
                return Refused::full; // a fast "no" beats a slow failure
            }
        }
        struct Release { // gives the place back even if fn throws
            Bulkhead *b;
            ~Release() {
                std::lock_guard held(b->lock_);
                auto next = std::find(b->line_.begin(), b->line_.end(), false);
                if (next != b->line_.end()) {
                    *next = true; // hand the place over: active_ stays the same
                    b->called_.notify_all(); // every waiter checks its own entry; only the one called goes
                } else {
                    b->active_--;
                }
            }
        } release{this};
        return fn();
    }

    std::pair<int, int> active_and_waiting() {
        std::lock_guard held(lock_);
        return {active_, static_cast<int>(std::count(line_.begin(), line_.end(), false))};
    }
};

int main() {
    using namespace std::chrono_literals;
    const Load healthy{600, {{Kind::search, 2}, {Kind::profile, 3}}, {{Kind::search, 2}, {Kind::profile, 1}}, 20};
    Load degraded = healthy;
    degraded.service_ticks[Kind::search] = 50;
    auto shared = [](int timeout) { return Config{{{Kind::search, 0}, {Kind::profile, 0}}, {50}, INT_MAX, timeout}; };

    auto h = simulate(shared(INT_MAX), healthy);
    assert(h[Kind::search].ok == 1196 && h[Kind::profile].ok == 1797);
    auto cascade = simulate(shared(INT_MAX), degraded)[Kind::profile];
    assert(cascade.ok == 72 && cascade.timed_out == 1668);
    assert(simulate(shared(30), degraded)[Kind::profile].ok == 270);
    auto one = simulate(shared(10), degraded);
    assert(one[Kind::profile].ok == 1797 && one[Kind::search].failed == 1180);
    auto walls = simulate({{{Kind::search, 0}, {Kind::profile, 1}}, {20, 30}, 10, 30}, degraded);
    assert(walls[Kind::profile].ok == 1797 && (walls[Kind::search] == Counts{0, 380, 190, 600, 30}));

    { // A limit, a short queue, an immediate no, and waiters served in the order they came.
        Bulkhead b(1, 2);
        std::atomic<bool> release = false;
        std::mutex order_lock;
        std::vector<std::string> order;
        auto call = [&](std::string name) {
            return std::jthread([&, name] {
                auto result = b.run([&] {
                    { std::lock_guard held(order_lock); order.push_back(name); }
                    while (!release) std::this_thread::sleep_for(1ms);
                    return 0;
                }, 5s);
                assert(std::holds_alternative<int>(result));
            });
        };
        auto first = call("first");
        while (b.active_and_waiting().first < 1) std::this_thread::sleep_for(1ms);
        auto second = call("second");
        while (b.active_and_waiting().second < 1) std::this_thread::sleep_for(1ms);
        auto third = call("third");
        while (b.active_and_waiting().second < 2) std::this_thread::sleep_for(1ms);
        assert(std::get<Bulkhead::Refused>(b.run([] { return 0; }, 5s)) == Bulkhead::Refused::full);
        release = true;
        first.join(), second.join(), third.join();
        assert((order == std::vector<std::string>{"first", "second", "third"}));
        assert((b.active_and_waiting() == std::pair{0, 0}));
    }
    { // A caller who stops waiting leaves the line and doesn't take a place with them.
        Bulkhead b(1, 1);
        std::atomic<bool> release = false;
        std::jthread first([&] { b.run([&] { while (!release) std::this_thread::sleep_for(1ms); return 0; }, 5s); });
        while (b.active_and_waiting().first < 1) std::this_thread::sleep_for(1ms);
        assert(std::get<Bulkhead::Refused>(b.run([] { return 0; }, 20ms)) == Bulkhead::Refused::waited_too_long);
        release = true;
        first.join();
        assert((b.active_and_waiting() == std::pair{0, 0}));
    }
    { // Never more than the limit, however the threads interleave.
        Bulkhead b(3, 100);
        std::atomic<int> running = 0, most = 0;
        {
            std::vector<std::jthread> callers;
            for (int i = 0; i < 40; i++)
                callers.emplace_back([&] {
                    b.run([&] {
                        int n = ++running;
                        for (int m = most; n > m && !most.compare_exchange_weak(m, n);) {}
                        std::this_thread::sleep_for(50us);
                        return --running;
                    }, 10s);
                });
        } // jthreads join here
        assert(most <= 3 && (b.active_and_waiting() == std::pair{0, 0}));
    }
    std::cout << "all resilience checks passed\n";
}
```

**Lab:** [`labs/cpp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/cpp). `python3 labs/run.py resilience-patterns/cpp`.

## 10. C#

.NET has a bulkhead built in. `ConcurrencyLimiter`, from the `System.Threading.RateLimiting` package, takes a permit limit, a queue limit and a queue order. With `OldestFirst`, a freed permit goes to the queue before any newcomer. When the queue is full, the lease comes back with `IsAcquired` false, at once. `NewestFirst` would instead push the oldest waiter out to make room. Cancelling the token removes a waiter from the queue. `SemaphoreSlim`, the usual choice for limiting async work, promises no order and has no queue limit. The counts are immutable records updated with `with`.

```csharp
// A tick-by-tick simulation of a cascade, Little's law, and a bulkhead.
// The same numbers as the TypeScript lab. One tick is 100 ms.
using System.Threading.RateLimiting;

public enum Kind { Search, Profile }

public sealed record Counts(int Ok = 0, int Failed = 0, int TimedOut = 0, int Rejected = 0, int Unfinished = 0);

/// <param name="Pools">The pool each kind uses: the same name means a shared pool.</param>
/// <param name="Sizes">Workers per pool, in the order pools start work.</param>
public sealed record Config(Dictionary<Kind, string> Pools, (string Pool, int Size)[] Sizes, int QueueLimit, int DependencyTimeoutTicks);

public sealed record Load(int Ticks, Dictionary<Kind, int> ArrivalsPerTick, Dictionary<Kind, int> ServiceTicks, int ClientTimeoutTicks);

public static class Resilience
{
    sealed class Request(Kind kind, int arrived)
    {
        public Kind Kind = kind;
        public int Arrived = arrived, EndsAt;
        public bool Failed;
    }

    public static Dictionary<Kind, Counts> Simulate(Config c, Load l)
    {
        var counts = new Dictionary<Kind, Counts> { [Kind.Search] = new(), [Kind.Profile] = new() };
        var queues = c.Sizes.ToDictionary(s => s.Pool, _ => new LinkedList<Request>());
        var running = c.Sizes.ToDictionary(s => s.Pool, _ => new List<Request>());
        for (var t = 0; t < l.Ticks; t++)
        {
            foreach (var busy in running.Values) // 1. finished work frees its worker
                busy.RemoveAll(r =>
                {
                    if (r.EndsAt > t) return false;
                    counts[r.Kind] = r.Failed ? counts[r.Kind] with { Failed = counts[r.Kind].Failed + 1 } : counts[r.Kind] with { Ok = counts[r.Kind].Ok + 1 };
                    return true;
                });
            foreach (var queue in queues.Values) // 2. callers who waited too long give up (the oldest are at the front)
                while (queue.First is { } oldest && t - oldest.Value.Arrived >= l.ClientTimeoutTicks)
                {
                    counts[oldest.Value.Kind] = counts[oldest.Value.Kind] with { TimedOut = counts[oldest.Value.Kind].TimedOut + 1 };
                    queue.RemoveFirst();
                }
            foreach (var kind in (Kind[])[Kind.Search, Kind.Profile]) // 3. new requests arrive, or are turned away
            {
                var queue = queues[c.Pools[kind]];
                for (var i = 0; i < l.ArrivalsPerTick[kind]; i++)
                    if (queue.Count >= c.QueueLimit) counts[kind] = counts[kind] with { Rejected = counts[kind].Rejected + 1 }; // load shedding
                    else queue.AddLast(new Request(kind, t));
            }
            foreach (var (pool, size) in c.Sizes) // 4. free workers take requests, oldest first
                while (running[pool].Count < size && queues[pool].First is { } next)
                {
                    queues[pool].RemoveFirst();
                    var r = next.Value;
                    int needs = l.ServiceTicks[r.Kind], limit = r.Kind == Kind.Search ? c.DependencyTimeoutTicks : int.MaxValue;
                    (r.EndsAt, r.Failed) = (t + Math.Min(needs, limit), needs > limit);
                    running[pool].Add(r);
                }
        }
        foreach (var r in queues.Values.SelectMany(q => q).Concat(running.Values.SelectMany(b => b)))
            counts[r.Kind] = counts[r.Kind] with { Unfinished = counts[r.Kind].Unfinished + 1 };
        return counts;
    }

    /// <summary>Little's law: requests in the system = arrival rate × time each one stays.</summary>
    public static double WorkersNeeded(double perSecond, double seconds) => perSecond * seconds;
}

public sealed class BulkheadFull(string message) : Exception(message);

/// <summary>
/// .NET has a bulkhead built in: ConcurrencyLimiter. OldestFirst serves waiters in the order they came, and a freed
/// place goes to the queue before any newcomer. (SemaphoreSlim makes no such promise, and has no queue limit.)
/// </summary>
public sealed class Bulkhead(int maxConcurrent, int maxQueue) : IDisposable
{
    readonly ConcurrencyLimiter limiter = new(new ConcurrencyLimiterOptions
    {
        PermitLimit = maxConcurrent,
        QueueLimit = maxQueue,
        QueueProcessingOrder = QueueProcessingOrder.OldestFirst, // NewestFirst would push the oldest waiter out instead
    });

    public async Task<T> Run<T>(Func<Task<T>> fn, TimeSpan maxWait)
    {
        using var gaveUp = new CancellationTokenSource(maxWait);
        RateLimitLease lease;
        try
        {
            lease = await limiter.AcquireAsync(1, gaveUp.Token);
        }
        catch (OperationCanceledException)
        {
            throw new BulkheadFull($"no place within {maxWait.TotalMilliseconds} ms"); // cancelling took us out of the queue
        }
        using (lease) // the place goes back when the lease is disposed, even if fn throws
        {
            if (!lease.IsAcquired) throw new BulkheadFull("the queue is full"); // a fast "no" beats a slow failure
            return await fn();
        }
    }

    public (long Free, long Waiting) Stats() => limiter.GetStatistics() is { } s ? (s.CurrentAvailablePermits, s.CurrentQueuedCount) : (0, 0);

    public void Dispose() => limiter.Dispose();
}
```

```csharp
// Checks: the same numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

const int None = int.MaxValue;
var healthy = new Load(600, new() { [Kind.Search] = 2, [Kind.Profile] = 3 }, new() { [Kind.Search] = 2, [Kind.Profile] = 1 }, 20);
var degraded = healthy with { ServiceTicks = new() { [Kind.Search] = 50, [Kind.Profile] = 1 } };
Config Shared(int timeout) => new(new() { [Kind.Search] = "shared", [Kind.Profile] = "shared" }, [("shared", 50)], None, timeout);

Check(Resilience.WorkersNeeded(20, 0.2) + Resilience.WorkersNeeded(30, 0.1) == 7 && Resilience.WorkersNeeded(20, 5) == 100, "little");
var h = Resilience.Simulate(Shared(None), healthy);
Check(h[Kind.Search].Ok == 1196 && h[Kind.Profile].Ok == 1797, h[Kind.Search]);
var cascade = Resilience.Simulate(Shared(None), degraded)[Kind.Profile];
Check(cascade.Ok == 72 && cascade.TimedOut == 1668, cascade);
Check(Resilience.Simulate(Shared(30), degraded)[Kind.Profile].Ok == 270, "3 s timeout");
var one = Resilience.Simulate(Shared(10), degraded);
Check(one[Kind.Profile].Ok == 1797 && one[Kind.Search].Failed == 1180, one[Kind.Search]);
var walls = Resilience.Simulate(new(new() { [Kind.Search] = "search", [Kind.Profile] = "profile" }, [("search", 20), ("profile", 30)], 10, 30), degraded);
Check(walls[Kind.Profile].Ok == 1797 && walls[Kind.Search] == new Counts(0, 380, 190, 600, 30), walls[Kind.Search]);

// A limit, a short queue, an immediate no, and a freed place going to the waiter, not a latecomer.
using (var bulkhead = new Bulkhead(1, 2))
{
    var order = new List<string>();
    var gates = new System.Collections.Concurrent.ConcurrentDictionary<string, TaskCompletionSource<string>>(); // read from other threads
    Task<string> Call(string name)
    {
        gates[name] = new(TaskCreationOptions.RunContinuationsAsynchronously);
        return bulkhead.Run(() => { lock (order) order.Add(name); return gates[name].Task; }, TimeSpan.FromSeconds(5));
    }
    bool Started(string name) { lock (order) return order.Contains(name); }
    var first = Call("first");
    var waiter = Call("waiter");
    var other = Call("other");
    Check(bulkhead.Stats() == (0, 2), bulkhead.Stats());
    try
    {
        await bulkhead.Run(() => Task.FromResult("never"), TimeSpan.FromSeconds(5));
        Check(false, "a fourth call should be turned away");
    }
    catch (BulkheadFull) { }
    gates["first"].SetResult("done");
    await first;
    var latecomer = Call("latecomer"); // arrives just as first finishes
    foreach (var name in (string[])["waiter", "other", "latecomer"])
    {
        while (!Started(name)) await Task.Delay(1);
        gates[name].SetResult("done");
    }
    await Task.WhenAll(waiter, other, latecomer);
    Check(order.SequenceEqual(["first", "waiter", "other", "latecomer"]), string.Join(",", order));
    Check(bulkhead.Stats() == (1, 0), bulkhead.Stats());
}

// A caller who stops waiting leaves the queue and doesn't take a place with them.
using (var bulkhead = new Bulkhead(1, 1))
{
    var hold = new TaskCompletionSource<int>();
    var first = bulkhead.Run(() => hold.Task, TimeSpan.FromSeconds(5));
    try
    {
        await bulkhead.Run(() => Task.FromResult(0), TimeSpan.FromMilliseconds(20));
        Check(false, "should give up");
    }
    catch (BulkheadFull) { Check(bulkhead.Stats() == (0, 0), bulkhead.Stats()); }
    hold.SetResult(1);
    await first;
    Check(bulkhead.Stats() == (1, 0), "the place came back");
}

// Never more than the limit, however the tasks interleave.
using (var bulkhead = new Bulkhead(3, 1000))
{
    int running = 0, most = 0;
    await Task.WhenAll(Enumerable.Range(0, 200).Select(_ => Task.Run(() => bulkhead.Run(async () =>
    {
        var n = Interlocked.Increment(ref running);
        for (var m = most; n > m && Interlocked.CompareExchange(ref most, n, m) != m; m = most) { }
        await Task.Delay(1);
        return Interlocked.Decrement(ref running);
    }, TimeSpan.FromMinutes(1)))));
    Check(most <= 3, $"{most} ran at once in a bulkhead of three");
}

Console.WriteLine("all resilience checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/csharp). `container.sh` runs it in the .NET SDK container with the NuGet cache mounted. `python3 labs/run.py resilience-patterns/csharp` (needs Podman).

## Common pitfalls

1. **Assuming a semaphore is fair.** Python's, C's, C++'s and C#'s `SemaphoreSlim` make no promise; Java's is unfair unless you pass `true`.
2. **Java's `tryAcquire()` on a fair semaphore.** The no-argument form barges anyway. Use the timed form.
3. **No queue limit.** A semaphore lets any number wait. Count waiters and turn callers away past the limit.
4. **Waking one thread with a shared condition variable.** With tickets or a list, the thread you wake may not be the one called. Wake all, and let each check its own turn.
5. **Forgetting the caller who gave up.** A place handed to a cancelled waiter is lost for good. Remove or skip cancelled waiters.
6. **Testing concurrency with real sleeps.** Slow, and they fail when the machine is busy. Use a fake clock where your language has one.

## Check your understanding

1. Why does a Go buffered channel make a fair bulkhead without extra code?
2. A Java bulkhead uses `new Semaphore(10, true)` and `tryAcquire()`. Is it fair? Why?
3. Why does the C lab use `pthread_cond_broadcast` rather than `pthread_cond_signal`?
4. What goes wrong if a caller times out but stays in the bulkhead's queue?
5. What does `QueueProcessingOrder.NewestFirst` do when the queue is full, and when might you want that?
6. Why can the C++ bulkhead let a waiter give up when the C one can't?

<details>
<summary>Answers — after your attempt</summary>

1. When a place frees up and goroutines are blocked sending, the runtime gives it to the one that has waited longest. A newcomer's send finds the buffer still full and waits behind them.
2. No. The no-argument `tryAcquire()` takes a free permit even when other threads are waiting, on fair semaphores too. Use `tryAcquire(timeout, unit)`, which respects the queue.
3. Every waiter sleeps on the same condition variable, but only one holds the ticket being called. `signal` might wake a different waiter, who would go back to sleep, leaving the called one asleep with a place reserved for it. `broadcast` wakes them all, and the right one goes.
4. A freed place might be handed to it, but nobody is there to use it, so the bulkhead permanently has one fewer place. After enough timeouts it has none.
5. It turns away the oldest waiter to make room for the newcomer. That suits work where fresh requests matter more than stale ones, such as live updates, where an old request's answer may no longer be wanted.
6. Each C++ waiter has its own list entry, which it can erase when it gives up, so the next call skips it. A C waiter has only a number in a sequence. If it left, the finishing call would still call its number, and the place would be lost, unless abandoned numbers were tracked and skipped.

</details>

## Practice — independent task

**Let a C waiter give up.**

1. Add a `bulkhead_run_for(b, fn, arg, max_wait)` to the C lab, using `pthread_cond_timedwait` with an absolute deadline from `clock_gettime(CLOCK_REALTIME)`.
2. When a waiter times out, record its ticket as abandoned. When a finishing call calls the next number, skip abandoned tickets, and free the place if nobody real is left.
3. Add a test like the other languages' "a caller who stops waiting leaves the queue": the place must come back after the caller has given up.

**Done when:** your test passes, and the existing tests still pass on several runs in a row.

## Before moving on

You can choose your language's tool for limiting concurrent work, say whether it's fair, add a queue limit and make giving up safe.

**Recap.** The simulation is arithmetic and comes out the same everywhere, provided pools start work in the same order: Go needs an order slice because its maps have none. Bulkheads differ. Go's channels, tokio's `Semaphore`, Java's `Semaphore(n, true)` and C#'s `ConcurrencyLimiter` with `OldestFirst` are fair. Python's, C's and C++'s tools make no promise, so those labs hand places over themselves. Only C# has a queue limit built in. Make a caller who gives up leave the queue, and test with a fake clock where you can.

## Related
- [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience patterns]] — the main lesson
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/in-other-languages|Reliability and plumbing in other languages]] — timeouts, retries and breakers in the same languages
- [[languages/02-go/08-context|Go context]] — cancellation, which Go's bulkhead uses
