# Load Balancing & Proxies in Other Languages

> **[Intermediate]** · A companion to [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|load balancing and proxies]], which simulates round-robin, random, least-outstanding and two-choices balancing, tracks health checks with fall and rise thresholds, and places keys on cache nodes with a hash ring. This page does the same in Python, Go, Java, Rust and C#, with the same numbers in every language, down to the simulation's 1,158 ms. Most of it translates directly. The differences are in hashing: each language's built-in string hash is the wrong tool for placing keys, Java has no unsigned integers to hold a hash in, and a stable sort matters more than it looks.

## Before you start

You can already:

- Explain least-outstanding and two-choices balancing, fall and rise, and why a hash ring moves about a fifth of keys where mod N moves four-fifths → [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|the main lesson]].
- Run tests in at least one of the languages here.

After this lesson you will be able to:

1. Say why your language's built-in string hash can't decide which server holds a key, and what to use instead.
2. Hold, compare and divide a 32-bit hash correctly in a language without unsigned integers.
3. Name the load balancer or balancing library people use in your language, and its default algorithm.

## The kid version

A class shares out library books by the first letter of each title: A to F on shelf 1, G to M on shelf 2, and so on. Everyone has to use the same rule, or someone looks on the wrong shelf. Now imagine each child's rule changed every morning. On Monday "Zebra" is on shelf 4, on Tuesday shelf 1. Nobody could find anything. Some languages' built-in "which shelf?" rules really do change every time the program starts, on purpose.

**Where the analogy stops working.** A class can agree a rule by talking. Servers written in different languages, or even two copies of one program, agree only if they run exactly the same hash function, bit for bit. That's why the labs write FNV-1a out by hand instead of using what the language provides.

## 1. The tools, by ecosystem

| Language | Balancers and libraries written in it | Default algorithm | Built-in string hash usable for placement? |
|---|---|---|---|
| TypeScript | `http-proxy`; usually Nginx or a cloud balancer in front | — | no built-in string hash |
| Python | rarely a balancer itself; runs behind Nginx, HAProxy or a cloud balancer | — | no: `hash()` is randomised per process |
| Go | **Traefik**, **Caddy**, `httputil.ReverseProxy`; gRPC's client-side balancing | Caddy: random; gRPC: pick first | no: `hash/maphash` is seeded randomly |
| Java | Spring Cloud LoadBalancer (client-side), Netty, gRPC | Spring: round-robin | stable but weak: `String.hashCode` mixes poorly |
| Rust | **Pingora** (Cloudflare), **tower**'s `balance` layer, Linkerd's proxy | tower: power of two choices | no: `HashMap` hashing is randomly seeded |
| C# | **YARP** | **power of two choices** | no: `string.GetHashCode()` is randomised per process |

Many real balancers are written in Go and Rust, where one process can handle a lot of concurrent connections with little memory. YARP's default and tower's balancer both use two random choices, which is the main lesson's section 5 in production. C and C++ are where Nginx, HAProxy and Envoy are written, but those are configured rather than programmed for these algorithms, so there's no lab for them here.

## 2. What changes between languages

### The built-in hash is the wrong tool

Python's `hash("user:1")`, C#'s `"user:1".GetHashCode()` and Rust's default `HashMap` hasher give a different number every time the program starts. That's deliberate: if an attacker could predict where keys land in a hash table, they could send thousands of keys that collide and make every lookup slow. Go's `maphash` is seeded randomly for the same reason. For a hash table that's right. For placing keys on servers it's useless: two app servers would put the same key on different cache nodes, and every restart would move every key.

Java's `String.hashCode` is the exception: it's fixed by the language specification, so it's stable. But it's a simple sum of characters times powers of 31, so similar keys such as `user:1` and `user:2` get nearby values and cluster on the ring. Every lab writes the same FNV-1a with a final mixing step, so all six languages place every key identically.

### A 32-bit hash with no unsigned type

The hash is a 32-bit unsigned number: 0 to about 4.3 billion. Go, Rust and C# have `uint32`/`u32`/`uint`, and Python masks with `& 0xFFFFFFFF`. Java has only a signed `int`, so the same bits mean −2,147,483,648 to 2,147,483,647, and half of all hashes look negative. The bits are right. What goes wrong is using them:

- `hash % servers` can be negative, which isn't an index. The lab uses `Integer.remainderUnsigned`.
- Ordering points on the ring with `<` puts every "negative" hash before every positive one, a different ring from every other language. The lab compares with `Integer.compareUnsigned`.

### Bytes or characters

FNV-1a hashes one unit of text at a time. TypeScript's `charCodeAt` and Java's and C#'s string indexing give UTF-16 code units; Go's and Rust's strings are UTF-8 bytes; Python's `ord` gives whole code points. For ASCII keys like `user:42`, all three are the same numbers. For `café`, they differ, and two services in different languages would place it on different servers. If keys can contain any text, agree to hash the UTF-8 bytes.

### Sorting points the same way

`HashRing` sorts its points by hash after each `add`. If two servers' points ever hash to the same value, a stable sort keeps them in the order added, and an unstable one may not, so two implementations could disagree about which server owns that point. JavaScript's, Python's, Java's `List.sort` and Rust's `sort_by_key` are stable. Go's `slices.SortFunc` and C#'s `List.Sort` aren't, so the Go lab uses `slices.SortStableFunc` and the C# lab LINQ's `OrderBy`, which is stable. With 32-bit hashes and a few hundred points a collision is unlikely, but "unlikely" is a bad thing for a placement rule to depend on.

### Exactly the same simulation, in six languages

The simulation draws exponential gaps with `log`, and Go, Java and JavaScript each compute `log` with their own code rather than the system's maths library. They could differ in the last bit, and that could tip one request's comparison and shift a percentile. In practice all six labs give mean 214, p50 138 and p99 1,158 ms for round-robin. The labs check exact numbers because they agree. If they didn't, the right fix would be to compare with a tolerance, not to change the model.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| round-robin over three servers, six picks | 0, 1, 2, 0, 1, 2; least-outstanding of [5, 0, 0] is 1 |
| smooth weighted, a 5, b 1, c 1 | a a b a c a a |
| 4 servers, 80% busy: mean, p50, p99 (ms) | round-robin 214, 138, 1,158; random 255, 159, 1,588; least-outstanding 68, 17, 466; two choices 96, 25, 495 |
| fail, fail, pass, fail, fail, fail, pass, pass (fall 3, rise 2) | down after the 6th check, up after the 8th |
| app-2 down; picks 0–3 | app-1, app-3, app-1, app-3; all down: an error |
| 10,000 keys, a 5th cache node | mod N moves about 8,000; the ring about 2,000, all to cache-e |
| busiest node's share, 1 point vs 100 per node | over 1.4 times fair, then under 1.2 |

## Terms used in this lesson

1. **Hash flooding**: This is an attack that sends many keys chosen to land in the same hash-table slot, so every lookup becomes slow. Randomly seeded hash functions are the defence.
2. **Stable hash**: This is a hash function that gives the same output for the same input in every process, on every machine, every time. Placement needs one.
3. **FNV-1a**: The name comes from its authors, Fowler, Noll and Vo. It's a simple, fast, non-cryptographic hash that multiplies and mixes in one byte or character at a time.
4. **Stable sort**: This is a sort that keeps items with equal keys in the order they were in before sorting.
5. **Code unit**: This is one fixed-size piece of an encoded string: 8 bits in UTF-8, 16 bits in UTF-16. One character can take several.
6. **Client-side load balancing**: This means the caller picks which server to send each request to, from a list it keeps, instead of going through a separate balancer. gRPC libraries and Spring Cloud LoadBalancer work this way.

## 4. Python

`Pick` is a type alias for a callable. `round_robin` keeps its turn in a closure with `nonlocal`. The hash masks every multiplication to 32 bits. `HashRing.server_for` uses `bisect_left` with a `key` function (Python 3.10 and later) to find the first point at or after the key's hash. The simulation's queues are lists, and popping from the front of a list is slow for long queues, but these stay short. `smooth_weighted` relies on dicts keeping insertion order, and on `max` returning the first of equal values.

```python
"""How a load balancer picks a server, health checks that take a failing server out and put it back, and
consistent hashing. The same numbers as the TypeScript lab."""
import bisect
import math
from typing import Callable, Sequence

MASK = 0xFFFFFFFF
Pick = Callable[[Sequence[int], Callable[[], float]], int]  # (outstanding per server, random) → server index


def round_robin() -> Pick:
    turn = 0

    def pick(outstanding, _random):
        nonlocal turn
        chosen = turn % len(outstanding)
        turn += 1
        return chosen

    return pick


def least_outstanding(outstanding, _random) -> int:
    return outstanding.index(min(outstanding))  # ties go to the lowest number


def random_pick(outstanding, rand) -> int:
    return math.floor(rand() * len(outstanding))


def two_choices(outstanding, rand) -> int:
    a = math.floor(rand() * len(outstanding))
    b = math.floor(rand() * len(outstanding))
    return b if outstanding[b] < outstanding[a] else a


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


def percentile(samples: list[float], p: float) -> float:
    ordered = sorted(samples)
    return ordered[max(1, math.ceil(p / 100 * len(ordered))) - 1]


def simulate(pick: Pick, servers: int, busy: float, requests: int, seed: int) -> dict:
    """Random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms, the rest 10."""
    rand = seeded(seed)
    mean_work_ms = 0.95 * 10 + 0.05 * 200
    gap_ms = mean_work_ms / (busy * servers)
    finishes: list[list[float]] = [[] for _ in range(servers)]  # per server: when each queued request ends
    now, times = 0.0, []
    for _ in range(requests):
        now += -gap_ms * math.log(1 - rand())
        for queue in finishes:
            while queue and queue[0] <= now:
                queue.pop(0)  # short queues: a list is fine; use collections.deque for long ones
        s = pick([len(q) for q in finishes], rand)
        work_ms = 200 if rand() < 0.05 else 10
        ends = max(now, finishes[s][-1] if finishes[s] else 0) + work_ms
        finishes[s].append(ends)
        times.append(ends - now)
    total = 0.0
    for t in times:
        total += t
    js_round = lambda x: math.floor(x + 0.5)  # round() sends halves to the even number; JavaScript goes up
    return {"mean": js_round(total / len(times)), "p50": js_round(percentile(times, 50)), "p99": js_round(percentile(times, 99))}


def smooth_weighted(weights: dict[str, int]) -> Callable[[], str]:
    """nginx's smooth weighted round-robin: each server gains its weight; the highest is chosen and pays the total."""
    total = sum(weights.values())
    current = dict.fromkeys(weights, 0)

    def pick() -> str:
        for name, weight in weights.items():
            current[name] += weight
        best = max(current, key=current.get)  # max keeps the first of equals, as the TypeScript reduce does
        current[best] -= total
        return best

    return pick


class Health:
    """`fall` failures in a row mark a server down; `rise` successes in a row bring it back."""

    def __init__(self, fall: int = 3, rise: int = 2):
        self.up, self._fall, self._rise, self._streak = True, fall, rise, 0

    def record(self, ok: bool) -> None:
        if ok == self.up:
            self._streak = 0
            return
        self._streak += 1
        if self._streak >= (self._fall if self.up else self._rise):
            self.up, self._streak = not self.up, 0


class NoHealthyServers(Exception):
    pass


def pick_healthy(servers: list[tuple[str, Health]], turn: int) -> str:
    up = [name for name, health in servers if health.up]
    if not up:
        raise NoHealthyServers("no healthy servers: answer 503")
    return up[turn % len(up)]


def fnv_hash(text: str) -> int:
    """FNV-1a, then a mixing step. Python's own hash() of a string changes every run, so it can't place keys."""
    h = 0x811C9DC5
    for ch in text:
        h = ((h ^ ord(ch)) * 0x01000193) & MASK
    h = ((h ^ (h >> 16)) * 0x85EBCA6B) & MASK
    h = ((h ^ (h >> 13)) * 0xC2B2AE35) & MASK
    return h ^ (h >> 16)


def modulo(key: str, servers: Sequence[str]) -> str:
    return servers[fnv_hash(key) % len(servers)]


class HashRing:
    """Servers and keys on one circle of hash values; a key belongs to the first server clockwise from it."""

    def __init__(self, servers: Sequence[str], replicas: int = 100):
        self._replicas = replicas
        self._points: list[tuple[int, str]] = []  # sorted by position
        for s in servers:
            self.add(s)

    def add(self, server: str) -> None:
        self._points += [(fnv_hash(f"{server}#{r}"), server) for r in range(self._replicas)]
        self._points.sort(key=lambda p: p[0])  # sort is stable, like JavaScript's

    def remove(self, server: str) -> None:
        self._points = [p for p in self._points if p[1] != server]

    def server_for(self, key: str) -> str:
        if not self._points:
            raise LookupError("the ring is empty")
        i = bisect.bisect_left(self._points, fnv_hash(key), key=lambda p: p[0])
        return self._points[i % len(self._points)][1]  # past the last point, wrap round to the first
```

```python
import unittest

from balancer import (Health, HashRing, NoHealthyServers, least_outstanding, modulo, pick_healthy, random_pick,
                      round_robin, simulate, smooth_weighted, two_choices)

KEYS = [f"user:{i}" for i in range(10_000)]
FOUR = ["cache-a", "cache-b", "cache-c", "cache-d"]


class Balancing(unittest.TestCase):
    def test_round_robin_takes_turns_least_outstanding_looks(self):
        pick, queues = round_robin(), [5, 0, 0]
        self.assertEqual([pick(queues, None) for _ in range(6)], [0, 1, 2, 0, 1, 2])
        self.assertEqual(least_outstanding(queues, None), 1)

    def test_smooth_weighted_round_robin(self):
        pick = smooth_weighted({"a": 5, "b": 1, "c": 1})
        self.assertEqual("".join(pick() for _ in range(7)), "aabacaa")

    def test_algorithms_that_look_at_queues_win_in_the_tail(self):
        run = lambda pick: simulate(pick, 4, 0.8, 100_000, 7)
        self.assertEqual(run(round_robin()), {"mean": 214, "p50": 138, "p99": 1_158})
        self.assertEqual(run(random_pick), {"mean": 255, "p50": 159, "p99": 1_588})
        self.assertEqual(run(least_outstanding), {"mean": 68, "p50": 17, "p99": 466})
        self.assertEqual(run(two_choices), {"mean": 96, "p50": 25, "p99": 495})

    def test_three_failures_to_go_down_two_successes_to_come_back(self):
        health = Health(3, 2)
        for ok in [False, False, True, False, False]:
            health.record(ok)
        self.assertTrue(health.up)
        health.record(False)
        self.assertFalse(health.up)
        health.record(True)
        self.assertFalse(health.up)
        health.record(True)
        self.assertTrue(health.up)

    def test_skips_down_servers_and_fails_when_all_are_down(self):
        servers = [(name, Health(3, 2)) for name in ["app-1", "app-2", "app-3"]]
        for _ in range(3):
            servers[1][1].record(False)
        self.assertEqual([pick_healthy(servers, t) for t in range(4)], ["app-1", "app-3", "app-1", "app-3"])
        for _, health in servers:
            for _ in range(3):
                health.record(False)
        with self.assertRaises(NoHealthyServers):
            pick_healthy(servers, 0)

    def test_modulo_moves_four_in_five_a_ring_about_one_in_five(self):
        five = FOUR + ["cache-e"]
        moved_by_modulo = sum(modulo(k, FOUR) != modulo(k, five) for k in KEYS)
        self.assertLess(abs(moved_by_modulo - 8_000), 200)
        ring = HashRing(FOUR, 100)
        before = [ring.server_for(k) for k in KEYS]
        ring.add("cache-e")
        moved = [k for k, b in zip(KEYS, before) if ring.server_for(k) != b]
        self.assertLess(abs(len(moved) - 2_000), 300)
        self.assertTrue(all(ring.server_for(k) == "cache-e" for k in moved))
        ring.remove("cache-e")
        self.assertEqual([ring.server_for(k) for k in KEYS], before)

    def test_virtual_nodes_even_out_the_keys(self):
        def busiest(replicas):
            ring, counts = HashRing(FOUR, replicas), {}
            for k in KEYS:
                counts[ring.server_for(k)] = counts.get(ring.server_for(k), 0) + 1
            return max(counts.values()) / (len(KEYS) / 4)

        self.assertGreater(busiest(1), 1.4)
        self.assertLess(busiest(100), 1.2)


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/01-load-balancing-and-proxies/labs/python). `python3 labs/run.py load-balancing-and-proxies/python`.

## 5. Go

`Pick` is a function type, so `LeastOutstanding` and a closure from `RoundRobin()` both fit it. `SmoothWeighted` takes a slice, not a map, because Go's map order is randomised and the order breaks ties. `uint32` multiplication wraps by itself, so `Hash` needs no masking. The ring sorts with `slices.SortStableFunc` and searches with `slices.BinarySearchFunc`. `PickHealthy` returns `ErrNoHealthyServers`, which callers test with `errors.Is`.

```go
// Package balancing: how a load balancer picks a server, health checks that take a failing server out and put it
// back, and consistent hashing. The same numbers as the TypeScript lab.
package balancing

import (
	"cmp"
	"errors"
	"fmt"
	"math"
	"slices"
)

// Pick chooses a server from how many requests each is still working on.
type Pick func(outstanding []int, random func() float64) int

func RoundRobin() Pick {
	next := 0
	return func(outstanding []int, _ func() float64) int {
		chosen := next % len(outstanding)
		next++
		return chosen
	}
}

// LeastOutstanding picks the server with the fewest requests in progress; ties go to the lowest number.
func LeastOutstanding(outstanding []int, _ func() float64) int {
	return slices.Index(outstanding, slices.Min(outstanding))
}

func Random(outstanding []int, random func() float64) int {
	return int(random() * float64(len(outstanding)))
}

// TwoChoices picks two servers at random and takes the less busy one.
func TwoChoices(outstanding []int, random func() float64) int {
	a := int(random() * float64(len(outstanding)))
	b := int(random() * float64(len(outstanding)))
	if outstanding[b] < outstanding[a] {
		return b
	}
	return a
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

func percentile(sorted []float64, p float64) float64 {
	return sorted[max(1, int(math.Ceil(p/100*float64(len(sorted)))))-1]
}

type Latency struct{ Mean, P50, P99 float64 }

// Simulate sends random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms.
func Simulate(pick Pick, servers int, busy float64, requests int, seed uint32) Latency {
	random := Seeded(seed)
	meanWorkMs := 0.95*10 + 0.05*200
	gapMs := meanWorkMs / (busy * float64(servers))
	finishes := make([][]float64, servers) // per server: when each queued request ends
	outstanding := make([]int, servers)
	now, total := 0.0, 0.0
	times := make([]float64, 0, requests)
	for range requests {
		now += -gapMs * math.Log(1-random())
		for s, queue := range finishes {
			for len(queue) > 0 && queue[0] <= now {
				queue = queue[1:]
			}
			finishes[s], outstanding[s] = queue, len(queue)
		}
		s := pick(outstanding, random)
		workMs := 10.0
		if random() < 0.05 {
			workMs = 200
		}
		start := now
		if n := len(finishes[s]); n > 0 {
			start = max(now, finishes[s][n-1])
		}
		ends := start + workMs
		finishes[s] = append(finishes[s], ends)
		times = append(times, ends-now)
		total += ends - now
	}
	slices.Sort(times)
	return Latency{math.Round(total / float64(len(times))), math.Round(percentile(times, 50)), math.Round(percentile(times, 99))}
}

type Weighted struct {
	Name   string
	Weight int
}

// SmoothWeighted is nginx's method: each server gains its weight; the highest is chosen and pays the total.
// It takes a slice, not a map: Go maps have no order, and the order breaks ties.
func SmoothWeighted(servers []Weighted) func() string {
	total := 0
	for _, s := range servers {
		total += s.Weight
	}
	current := make([]int, len(servers))
	return func() string {
		best := 0
		for i, s := range servers {
			current[i] += s.Weight
			if current[i] > current[best] {
				best = i
			}
		}
		current[best] -= total
		return servers[best].Name
	}
}

// Health takes Fall failures in a row to mark a server down, and Rise successes in a row to bring it back.
type Health struct {
	Up         bool
	fall, rise int
	streak     int
}

func NewHealth(fall, rise int) *Health { return &Health{Up: true, fall: fall, rise: rise} }

func (h *Health) Record(ok bool) {
	if ok == h.Up {
		h.streak = 0
		return
	}
	h.streak++
	limit := h.rise
	if h.Up {
		limit = h.fall
	}
	if h.streak >= limit {
		h.Up, h.streak = !h.Up, 0
	}
}

type Server struct {
	Name   string
	Health *Health
}

var ErrNoHealthyServers = errors.New("no healthy servers: answer 503")

func PickHealthy(servers []Server, turn int) (string, error) {
	var up []string
	for _, s := range servers {
		if s.Health.Up {
			up = append(up, s.Name)
		}
	}
	if len(up) == 0 {
		return "", ErrNoHealthyServers
	}
	return up[turn%len(up)], nil
}

// Hash is FNV-1a then a mixing step. hash/fnv has FNV-1a too, but over bytes; this matches the other labs exactly.
func Hash(text string) uint32 {
	h := uint32(0x811c9dc5)
	for i := 0; i < len(text); i++ { // bytes, which for these ASCII keys are JavaScript's UTF-16 code units
		h = (h ^ uint32(text[i])) * 0x01000193
	}
	h = (h ^ h>>16) * 0x85ebca6b
	h = (h ^ h>>13) * 0xc2b2ae35
	return h ^ h>>16
}

func Modulo(key string, servers []string) string {
	return servers[Hash(key)%uint32(len(servers))]
}

type point struct {
	at     uint32
	server string
}

// HashRing places servers and keys on one circle of hash values; a key belongs to the first server clockwise.
type HashRing struct {
	points   []point
	replicas int
}

func NewHashRing(servers []string, replicas int) *HashRing {
	r := &HashRing{replicas: replicas}
	for _, s := range servers {
		r.Add(s)
	}
	return r
}

func (r *HashRing) Add(server string) {
	for i := range r.replicas {
		r.points = append(r.points, point{Hash(fmt.Sprintf("%s#%d", server, i)), server})
	}
	slices.SortStableFunc(r.points, func(a, b point) int { return cmp.Compare(a.at, b.at) })
}

func (r *HashRing) Remove(server string) {
	r.points = slices.DeleteFunc(r.points, func(p point) bool { return p.server == server })
}

func (r *HashRing) ServerFor(key string) string {
	h := Hash(key)
	i, _ := slices.BinarySearchFunc(r.points, h, func(p point, h uint32) int { return cmp.Compare(p.at, h) })
	return r.points[i%len(r.points)].server // past the last point, wrap round to the first
}
```

```go
package balancing

import (
	"errors"
	"fmt"
	"slices"
	"testing"
)

var four = []string{"cache-a", "cache-b", "cache-c", "cache-d"}

func keys() []string {
	ks := make([]string, 10_000)
	for i := range ks {
		ks[i] = fmt.Sprintf("user:%d", i)
	}
	return ks
}

func TestRoundRobinTakesTurnsLeastOutstandingLooks(t *testing.T) {
	pick, queues := RoundRobin(), []int{5, 0, 0}
	var got []int
	for range 6 {
		got = append(got, pick(queues, nil))
	}
	if !slices.Equal(got, []int{0, 1, 2, 0, 1, 2}) || LeastOutstanding(queues, nil) != 1 {
		t.Fatal(got)
	}
}

func TestSmoothWeightedRoundRobin(t *testing.T) {
	pick := SmoothWeighted([]Weighted{{"a", 5}, {"b", 1}, {"c", 1}})
	got := ""
	for range 7 {
		got += pick()
	}
	if got != "aabacaa" {
		t.Fatal(got)
	}
}

func TestAlgorithmsThatLookAtQueuesWinInTheTail(t *testing.T) {
	for _, c := range []struct {
		pick Pick
		want Latency
	}{
		{RoundRobin(), Latency{214, 138, 1_158}},
		{Random, Latency{255, 159, 1_588}},
		{LeastOutstanding, Latency{68, 17, 466}},
		{TwoChoices, Latency{96, 25, 495}},
	} {
		if got := Simulate(c.pick, 4, 0.8, 100_000, 7); got != c.want {
			t.Errorf("got %v, want %v", got, c.want)
		}
	}
}

func TestThreeFailuresToGoDownTwoSuccessesToComeBack(t *testing.T) {
	h := NewHealth(3, 2)
	var states []bool
	for _, ok := range []bool{false, false, true, false, false, false, true, true} {
		h.Record(ok)
		states = append(states, h.Up)
	}
	if !slices.Equal(states, []bool{true, true, true, true, true, false, false, true}) {
		t.Fatal(states)
	}
}

func TestSkipsDownServersAndFailsWhenAllAreDown(t *testing.T) {
	servers := []Server{{"app-1", NewHealth(3, 2)}, {"app-2", NewHealth(3, 2)}, {"app-3", NewHealth(3, 2)}}
	for range 3 {
		servers[1].Health.Record(false)
	}
	var got []string
	for turn := range 4 {
		name, _ := PickHealthy(servers, turn)
		got = append(got, name)
	}
	if !slices.Equal(got, []string{"app-1", "app-3", "app-1", "app-3"}) {
		t.Fatal(got)
	}
	for _, s := range servers {
		for range 3 {
			s.Health.Record(false)
		}
	}
	if _, err := PickHealthy(servers, 0); !errors.Is(err, ErrNoHealthyServers) {
		t.Fatal(err)
	}
}

func TestModuloMovesFourInFiveARingAboutOneInFive(t *testing.T) {
	ks, five := keys(), append(slices.Clone(four), "cache-e")
	movedByModulo := 0
	for _, k := range ks {
		if Modulo(k, four) != Modulo(k, five) {
			movedByModulo++
		}
	}
	ring := NewHashRing(four, 100)
	before := make([]string, len(ks))
	for i, k := range ks {
		before[i] = ring.ServerFor(k)
	}
	ring.Add("cache-e")
	moved := 0
	for i, k := range ks {
		if now := ring.ServerFor(k); now != before[i] {
			moved++
			if now != "cache-e" {
				t.Fatal(k, "moved to", now)
			}
		}
	}
	if abs(movedByModulo-8_000) >= 200 || abs(moved-2_000) >= 300 {
		t.Fatal(movedByModulo, moved)
	}
	ring.Remove("cache-e")
	for i, k := range ks {
		if ring.ServerFor(k) != before[i] {
			t.Fatal(k, "didn't go back")
		}
	}
}

func TestVirtualNodesEvenOutTheKeys(t *testing.T) {
	busiest := func(replicas int) float64 {
		ring, counts := NewHashRing(four, replicas), map[string]int{}
		for _, k := range keys() {
			counts[ring.ServerFor(k)]++
		}
		most := 0
		for _, n := range counts {
			most = max(most, n)
		}
		return float64(most) / (10_000 / 4)
	}
	if one, hundred := busiest(1), busiest(100); one <= 1.4 || hundred >= 1.2 {
		t.Fatal(one, hundred)
	}
}

func abs(n int) int { return max(n, -n) }
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/01-load-balancing-and-proxies/labs/go). `python3 labs/run.py load-balancing-and-proxies/go`.

## 6. Java

`Pick` is a functional interface, so the algorithms are lambdas held in constants. `hash` returns an `int` with the right bits; `modulo` uses `Integer.remainderUnsigned`, and the ring sorts and searches with `Integer.compareUnsigned`. Leaving either out gives a ring in a different order from every other language. `smoothWeighted` takes a `LinkedHashMap` so the servers keep the order given. The simulation's queues are `ArrayDeque`s, which can look at both ends.

```java
package balancing;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.function.DoubleSupplier;
import java.util.function.Supplier;

/** How a load balancer picks a server, health checks, and consistent hashing. The same numbers as the TypeScript lab. */
public final class Balancing {
    private Balancing() {}

    /** Chooses a server from how many requests each is still working on. */
    @FunctionalInterface
    public interface Pick {
        int pick(int[] outstanding, DoubleSupplier random);
    }

    public static Pick roundRobin() {
        int[] next = {0};
        return (outstanding, random) -> next[0]++ % outstanding.length;
    }

    /** The fewest requests in progress; ties go to the lowest number. */
    public static final Pick LEAST_OUTSTANDING = (outstanding, random) -> {
        int best = 0;
        for (int i = 1; i < outstanding.length; i++) if (outstanding[i] < outstanding[best]) best = i;
        return best;
    };

    public static final Pick RANDOM = (outstanding, random) -> (int) (random.getAsDouble() * outstanding.length);

    /** Two servers at random, and the less busy of the two. */
    public static final Pick TWO_CHOICES = (outstanding, random) -> {
        int a = (int) (random.getAsDouble() * outstanding.length);
        int b = (int) (random.getAsDouble() * outstanding.length);
        return outstanding[b] < outstanding[a] ? b : a;
    };

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

    public record Latency(long mean, long p50, long p99) {}

    /** Random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms. */
    public static Latency simulate(Pick pick, int servers, double busy, int requests, int seed) {
        DoubleSupplier random = seeded(seed);
        double meanWorkMs = 0.95 * 10 + 0.05 * 200;
        double gapMs = meanWorkMs / (busy * servers);
        List<java.util.ArrayDeque<Double>> finishes = new ArrayList<>(); // per server: when each queued request ends
        for (int s = 0; s < servers; s++) finishes.add(new java.util.ArrayDeque<>());
        int[] outstanding = new int[servers];
        double now = 0;
        double total = 0;
        double[] times = new double[requests];
        for (int i = 0; i < requests; i++) {
            now += -gapMs * Math.log(1 - random.getAsDouble());
            for (int s = 0; s < servers; s++) {
                var queue = finishes.get(s);
                while (!queue.isEmpty() && queue.peekFirst() <= now) queue.pollFirst();
                outstanding[s] = queue.size();
            }
            int s = pick.pick(outstanding, random);
            double workMs = random.getAsDouble() < 0.05 ? 200 : 10;
            var queue = finishes.get(s);
            double ends = Math.max(now, queue.isEmpty() ? 0 : queue.peekLast()) + workMs;
            queue.addLast(ends);
            times[i] = ends - now;
            total += ends - now;
        }
        Arrays.sort(times);
        return new Latency(Math.round(total / requests), Math.round(percentile(times, 50)), Math.round(percentile(times, 99)));
    }

    private static double percentile(double[] sorted, double p) {
        return sorted[Math.max(1, (int) Math.ceil(p / 100 * sorted.length)) - 1];
    }

    /** nginx's smooth weighted round-robin. A LinkedHashMap keeps the servers in the order given, which breaks ties. */
    public static Supplier<String> smoothWeighted(LinkedHashMap<String, Integer> weights) {
        int total = weights.values().stream().mapToInt(Integer::intValue).sum();
        var current = new LinkedHashMap<String, Integer>();
        weights.keySet().forEach(name -> current.put(name, 0));
        return () -> {
            weights.forEach((name, weight) -> current.merge(name, weight, Integer::sum));
            String best = null;
            for (var e : current.entrySet()) if (best == null || e.getValue() > current.get(best)) best = e.getKey();
            current.merge(best, -total, Integer::sum);
            return best;
        };
    }

    /** {@code fall} failures in a row mark a server down; {@code rise} successes in a row bring it back. */
    public static final class Health {
        private boolean up = true;
        private final int fall;
        private final int rise;
        private int streak;

        public Health(int fall, int rise) {
            this.fall = fall;
            this.rise = rise;
        }

        public boolean up() {
            return up;
        }

        public void record(boolean ok) {
            if (ok == up) {
                streak = 0;
                return;
            }
            if (++streak >= (up ? fall : rise)) {
                up = !up;
                streak = 0;
            }
        }
    }

    public record Server(String name, Health health) {}

    public static String pickHealthy(List<Server> servers, int turn) {
        var up = servers.stream().filter(s -> s.health().up()).toList();
        if (up.isEmpty()) throw new IllegalStateException("no healthy servers: answer 503");
        return up.get(turn % up.size()).name();
    }

    /**
     * FNV-1a, then a mixing step. Java has no unsigned int: the bits are the same as the other languages', but
     * comparing and dividing them must use the unsigned methods, or half the values count as negative.
     */
    public static int hash(String text) {
        int h = 0x811c9dc5;
        for (int i = 0; i < text.length(); i++) h = (h ^ text.charAt(i)) * 0x01000193; // charAt is a UTF-16 unit, like JavaScript's
        h = (h ^ (h >>> 16)) * 0x85ebca6b;
        h = (h ^ (h >>> 13)) * 0xc2b2ae35;
        return h ^ (h >>> 16);
    }

    public static String modulo(String key, List<String> servers) {
        return servers.get(Integer.remainderUnsigned(hash(key), servers.size())); // hash(key) % n can be negative
    }

    private record Point(int at, String server) {}

    /** Servers and keys on one circle of hash values; a key belongs to the first server clockwise from it. */
    public static final class HashRing {
        private static final Comparator<Point> BY_POSITION = (a, b) -> Integer.compareUnsigned(a.at(), b.at());
        private final List<Point> points = new ArrayList<>();
        private final int replicas;

        public HashRing(List<String> servers, int replicas) {
            this.replicas = replicas;
            servers.forEach(this::add);
        }

        public void add(String server) {
            for (int r = 0; r < replicas; r++) points.add(new Point(hash(server + "#" + r), server));
            points.sort(BY_POSITION); // List.sort is stable, like JavaScript's
        }

        public void remove(String server) {
            points.removeIf(p -> p.server().equals(server));
        }

        public String serverFor(String key) {
            if (points.isEmpty()) throw new IllegalStateException("the ring is empty");
            int h = hash(key);
            int lo = 0;
            int hi = points.size(); // binary search for the first point at or after h
            while (lo < hi) {
                int mid = (lo + hi) >>> 1;
                if (Integer.compareUnsigned(points.get(mid).at(), h) < 0) lo = mid + 1;
                else hi = mid;
            }
            return points.get(lo % points.size()).server(); // past the last point, wrap round to the first
        }
    }
}
```

```java
package balancing;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.function.Supplier;
import java.util.stream.IntStream;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class BalancingCheck {
    private BalancingCheck() {}

    static final List<String> KEYS = IntStream.range(0, 10_000).mapToObj(i -> "user:" + i).toList();
    static final List<String> FOUR = List.of("cache-a", "cache-b", "cache-c", "cache-d");

    public static void main(String[] args) {
        var pick = Balancing.roundRobin();
        int[] queues = {5, 0, 0};
        List<Integer> turns = new ArrayList<>();
        for (int i = 0; i < 6; i++) turns.add(pick.pick(queues, null));
        assert turns.equals(List.of(0, 1, 2, 0, 1, 2)) && Balancing.LEAST_OUTSTANDING.pick(queues, null) == 1;

        var weights = new LinkedHashMap<String, Integer>();
        weights.put("a", 5);
        weights.put("b", 1);
        weights.put("c", 1);
        Supplier<String> weighted = Balancing.smoothWeighted(weights);
        var order = new StringBuilder();
        for (int i = 0; i < 7; i++) order.append(weighted.get());
        assert order.toString().equals("aabacaa") : order;

        assert Balancing.simulate(Balancing.roundRobin(), 4, 0.8, 100_000, 7).equals(new Balancing.Latency(214, 138, 1_158));
        assert Balancing.simulate(Balancing.RANDOM, 4, 0.8, 100_000, 7).equals(new Balancing.Latency(255, 159, 1_588));
        assert Balancing.simulate(Balancing.LEAST_OUTSTANDING, 4, 0.8, 100_000, 7).equals(new Balancing.Latency(68, 17, 466));
        var two = Balancing.simulate(Balancing.TWO_CHOICES, 4, 0.8, 100_000, 7);
        assert two.equals(new Balancing.Latency(96, 25, 495)) : two;

        var health = new Balancing.Health(3, 2);
        List<Boolean> states = new ArrayList<>();
        for (boolean ok : new boolean[] {false, false, true, false, false, false, true, true}) {
            health.record(ok);
            states.add(health.up());
        }
        assert states.equals(List.of(true, true, true, true, true, false, false, true)) : states;

        var servers = List.of(new Balancing.Server("app-1", new Balancing.Health(3, 2)),
                new Balancing.Server("app-2", new Balancing.Health(3, 2)), new Balancing.Server("app-3", new Balancing.Health(3, 2)));
        for (int i = 0; i < 3; i++) servers.get(1).health().record(false);
        List<String> picked = new ArrayList<>();
        for (int t = 0; t < 4; t++) picked.add(Balancing.pickHealthy(servers, t));
        assert picked.equals(List.of("app-1", "app-3", "app-1", "app-3")) : picked;
        for (var s : servers) for (int i = 0; i < 3; i++) s.health().record(false);
        try {
            Balancing.pickHealthy(servers, 0);
            throw new AssertionError("expected no healthy servers");
        } catch (IllegalStateException expected) {
            // answer 503
        }

        var five = new ArrayList<>(FOUR);
        five.add("cache-e");
        long movedByModulo = KEYS.stream().filter(k -> !Balancing.modulo(k, FOUR).equals(Balancing.modulo(k, five))).count();
        assert Math.abs(movedByModulo - 8_000) < 200 : movedByModulo;
        var ring = new Balancing.HashRing(FOUR, 100);
        var before = KEYS.stream().map(ring::serverFor).toList();
        ring.add("cache-e");
        var moved = IntStream.range(0, KEYS.size()).filter(i -> !ring.serverFor(KEYS.get(i)).equals(before.get(i))).boxed().toList();
        assert Math.abs(moved.size() - 2_000) < 300 : moved.size();
        assert moved.stream().allMatch(i -> ring.serverFor(KEYS.get(i)).equals("cache-e"));
        ring.remove("cache-e");
        assert KEYS.stream().map(ring::serverFor).toList().equals(before);

        assert busiest(1) > 1.4 && busiest(100) < 1.2 : busiest(1) + " " + busiest(100);
        System.out.println("all balancing checks passed");
    }

    private static double busiest(int replicas) {
        var ring = new Balancing.HashRing(FOUR, replicas);
        var counts = new HashMap<String, Integer>();
        for (String k : KEYS) counts.merge(ring.serverFor(k), 1, Integer::sum);
        return counts.values().stream().mapToInt(Integer::intValue).max().orElseThrow() / (KEYS.size() / 4.0);
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/01-load-balancing-and-proxies/labs/java). `python3 labs/run.py load-balancing-and-proxies/java`.

## 7. Rust

`Pick` is a trait for any `FnMut` with the right signature, so `simulate` accepts a plain function such as `least_outstanding` or a closure with state from `round_robin()`. The random generator is passed as `&mut dyn FnMut() -> f64`. The hash uses `wrapping_mul` over the string's bytes, and the ring finds its point with `partition_point`. `pick_healthy` returns a `Result` whose names borrow from the input.

```rust
//! How a load balancer picks a server, health checks that take a failing server out and put it back, and
//! consistent hashing. The same numbers as the TypeScript lab.
use std::collections::VecDeque;

/// Chooses a server from how many requests each is still working on. FnMut, because round-robin keeps a turn.
pub trait Pick: FnMut(&[usize], &mut dyn FnMut() -> f64) -> usize {}
impl<F: FnMut(&[usize], &mut dyn FnMut() -> f64) -> usize> Pick for F {}

pub fn round_robin() -> impl Pick {
    let mut next = 0;
    move |outstanding: &[usize], _: &mut dyn FnMut() -> f64| {
        let chosen = next % outstanding.len();
        next += 1;
        chosen
    }
}

/// The fewest requests in progress; ties go to the lowest number.
pub fn least_outstanding(outstanding: &[usize], _: &mut dyn FnMut() -> f64) -> usize {
    let min = outstanding.iter().min().expect("at least one server");
    outstanding
        .iter()
        .position(|n| n == min)
        .expect("the minimum is in the list")
}

pub fn random(outstanding: &[usize], rand: &mut dyn FnMut() -> f64) -> usize {
    (rand() * outstanding.len() as f64) as usize
}

/// Two servers at random, and the less busy of the two.
pub fn two_choices(outstanding: &[usize], rand: &mut dyn FnMut() -> f64) -> usize {
    let a = (rand() * outstanding.len() as f64) as usize;
    let b = (rand() * outstanding.len() as f64) as usize;
    if outstanding[b] < outstanding[a] {
        b
    } else {
        a
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

#[derive(Debug, PartialEq)]
pub struct Latency {
    pub mean: f64,
    pub p50: f64,
    pub p99: f64,
}

/// Random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms.
pub fn simulate(
    mut pick: impl Pick,
    servers: usize,
    busy: f64,
    requests: usize,
    seed: u32,
) -> Latency {
    let mut rand = seeded(seed);
    let mean_work_ms = 0.95 * 10.0 + 0.05 * 200.0;
    let gap_ms = mean_work_ms / (busy * servers as f64);
    let mut finishes: Vec<VecDeque<f64>> = vec![VecDeque::new(); servers]; // per server: when each queued request ends
    let (mut now, mut total) = (0.0_f64, 0.0);
    let mut times = Vec::with_capacity(requests);
    for _ in 0..requests {
        now += -gap_ms * (1.0 - rand()).ln();
        for queue in &mut finishes {
            while queue.front().is_some_and(|&ends| ends <= now) {
                queue.pop_front();
            }
        }
        let outstanding: Vec<usize> = finishes.iter().map(VecDeque::len).collect();
        let s = pick(&outstanding, &mut rand);
        let work_ms = if rand() < 0.05 { 200.0 } else { 10.0 };
        let ends = now.max(finishes[s].back().copied().unwrap_or(0.0)) + work_ms;
        finishes[s].push_back(ends);
        times.push(ends - now);
        total += ends - now;
    }
    times.sort_by(f64::total_cmp);
    let percentile = |p: f64| times[((p / 100.0 * times.len() as f64).ceil() as usize).max(1) - 1];
    Latency {
        mean: (total / requests as f64).round(),
        p50: percentile(50.0).round(),
        p99: percentile(99.0).round(),
    }
}

/// nginx's smooth weighted round-robin: each server gains its weight; the highest is chosen and pays the total.
pub fn smooth_weighted(weights: &[(&'static str, i32)]) -> impl FnMut() -> &'static str {
    let weights = weights.to_vec();
    let total: i32 = weights.iter().map(|w| w.1).sum();
    let mut current = vec![0; weights.len()];
    move || {
        let mut best = 0;
        for (i, (_, weight)) in weights.iter().enumerate() {
            current[i] += weight;
            if current[i] > current[best] {
                best = i;
            }
        }
        current[best] -= total;
        weights[best].0
    }
}

/// `fall` failures in a row mark a server down; `rise` successes in a row bring it back.
pub struct Health {
    pub up: bool,
    fall: u32,
    rise: u32,
    streak: u32,
}

impl Health {
    pub fn new(fall: u32, rise: u32) -> Self {
        Health {
            up: true,
            fall,
            rise,
            streak: 0,
        }
    }

    pub fn record(&mut self, ok: bool) {
        if ok == self.up {
            self.streak = 0;
            return;
        }
        self.streak += 1;
        if self.streak >= if self.up { self.fall } else { self.rise } {
            self.up = !self.up;
            self.streak = 0;
        }
    }
}

pub fn pick_healthy<'a>(
    servers: &'a [(&'a str, Health)],
    turn: usize,
) -> Result<&'a str, &'static str> {
    let up: Vec<&str> = servers
        .iter()
        .filter(|(_, h)| h.up)
        .map(|(name, _)| *name)
        .collect();
    if up.is_empty() {
        return Err("no healthy servers: answer 503");
    }
    Ok(up[turn % up.len()])
}

/// FNV-1a, then a mixing step. Over bytes, which for these ASCII keys are JavaScript's UTF-16 code units.
/// std's HashMap hasher is randomly seeded per process, so it can't be used to place keys on servers.
pub fn hash(text: &str) -> u32 {
    let mut h: u32 = 0x811c9dc5;
    for byte in text.bytes() {
        h = (h ^ u32::from(byte)).wrapping_mul(0x01000193);
    }
    h = (h ^ (h >> 16)).wrapping_mul(0x85ebca6b);
    h = (h ^ (h >> 13)).wrapping_mul(0xc2b2ae35);
    h ^ (h >> 16)
}

pub fn modulo<'a>(key: &str, servers: &[&'a str]) -> &'a str {
    servers[hash(key) as usize % servers.len()]
}

/// Servers and keys on one circle of hash values; a key belongs to the first server clockwise from it.
pub struct HashRing {
    points: Vec<(u32, String)>, // sorted by position
    replicas: usize,
}

impl HashRing {
    pub fn new(servers: &[&str], replicas: usize) -> Self {
        let mut ring = HashRing {
            points: Vec::new(),
            replicas,
        };
        for s in servers {
            ring.add(s);
        }
        ring
    }

    pub fn add(&mut self, server: &str) {
        self.points.extend(
            (0..self.replicas).map(|r| (hash(&format!("{server}#{r}")), server.to_string())),
        );
        self.points.sort_by_key(|p| p.0); // sort_by_key is stable, like JavaScript's sort
    }

    pub fn remove(&mut self, server: &str) {
        self.points.retain(|p| p.1 != server);
    }

    pub fn server_for(&self, key: &str) -> &str {
        assert!(!self.points.is_empty(), "the ring is empty");
        let h = hash(key);
        let i = self.points.partition_point(|p| p.0 < h); // the first point at or after h
        &self.points[i % self.points.len()].1 // past the last point, wrap round to the first
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    const FOUR: [&str; 4] = ["cache-a", "cache-b", "cache-c", "cache-d"];

    fn keys() -> Vec<String> {
        (0..10_000).map(|i| format!("user:{i}")).collect()
    }

    #[test]
    fn round_robin_takes_turns_least_outstanding_looks() {
        let (mut pick, queues) = (round_robin(), [5, 0, 0]);
        let mut never = || 0.0;
        let turns: Vec<usize> = (0..6).map(|_| pick(&queues, &mut never)).collect();
        assert_eq!(turns, [0, 1, 2, 0, 1, 2]);
        assert_eq!(least_outstanding(&queues, &mut never), 1);
    }

    #[test]
    fn smooth_weighted_round_robin() {
        let mut pick = smooth_weighted(&[("a", 5), ("b", 1), ("c", 1)]);
        assert_eq!((0..7).map(|_| pick()).collect::<String>(), "aabacaa");
    }

    #[test]
    fn algorithms_that_look_at_queues_win_in_the_tail() {
        let latency = |mean, p50, p99| Latency { mean, p50, p99 };
        assert_eq!(
            simulate(round_robin(), 4, 0.8, 100_000, 7),
            latency(214.0, 138.0, 1_158.0)
        );
        assert_eq!(
            simulate(random, 4, 0.8, 100_000, 7),
            latency(255.0, 159.0, 1_588.0)
        );
        assert_eq!(
            simulate(least_outstanding, 4, 0.8, 100_000, 7),
            latency(68.0, 17.0, 466.0)
        );
        assert_eq!(
            simulate(two_choices, 4, 0.8, 100_000, 7),
            latency(96.0, 25.0, 495.0)
        );
    }

    #[test]
    fn three_failures_to_go_down_two_successes_to_come_back() {
        let mut health = Health::new(3, 2);
        let states: Vec<bool> = [false, false, true, false, false, false, true, true]
            .iter()
            .map(|&ok| {
                health.record(ok);
                health.up
            })
            .collect();
        assert_eq!(states, [true, true, true, true, true, false, false, true]);
    }

    #[test]
    fn skips_down_servers_and_fails_when_all_are_down() {
        let mut servers = ["app-1", "app-2", "app-3"].map(|name| (name, Health::new(3, 2)));
        for _ in 0..3 {
            servers[1].1.record(false);
        }
        let picked: Vec<&str> = (0..4)
            .map(|turn| pick_healthy(&servers, turn).unwrap())
            .collect();
        assert_eq!(picked, ["app-1", "app-3", "app-1", "app-3"]);
        for (_, health) in &mut servers {
            for _ in 0..3 {
                health.record(false);
            }
        }
        assert!(pick_healthy(&servers, 0).is_err());
    }

    #[test]
    fn modulo_moves_four_in_five_a_ring_about_one_in_five() {
        let (keys, five) = (keys(), [FOUR.as_slice(), &["cache-e"]].concat());
        let moved_by_modulo = keys
            .iter()
            .filter(|k| modulo(k, &FOUR) != modulo(k, &five))
            .count();
        assert!(moved_by_modulo.abs_diff(8_000) < 200, "{moved_by_modulo}");
        let mut ring = HashRing::new(&FOUR, 100);
        let before: Vec<String> = keys
            .iter()
            .map(|k| ring.server_for(k).to_string())
            .collect();
        ring.add("cache-e");
        let moved: Vec<&String> = keys
            .iter()
            .zip(&before)
            .filter(|(k, b)| ring.server_for(k) != *b)
            .map(|(k, _)| k)
            .collect();
        assert!(moved.len().abs_diff(2_000) < 300, "{}", moved.len());
        assert!(moved.iter().all(|k| ring.server_for(k) == "cache-e"));
        ring.remove("cache-e");
        assert!(
            keys.iter()
                .zip(&before)
                .all(|(k, b)| ring.server_for(k) == b)
        );
    }

    #[test]
    fn virtual_nodes_even_out_the_keys() {
        let busiest = |replicas| {
            let ring = HashRing::new(&FOUR, replicas);
            let mut counts: HashMap<&str, usize> = HashMap::new();
            for k in keys() {
                *counts.entry(ring.server_for(&k)).or_default() += 1;
            }
            *counts.values().max().unwrap() as f64 / (10_000.0 / 4.0)
        };
        assert!(busiest(1) > 1.4, "{}", busiest(1));
        assert!(busiest(100) < 1.2, "{}", busiest(100));
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/01-load-balancing-and-proxies/labs/rust). `python3 labs/run.py load-balancing-and-proxies/rust`.

## 8. C#

`Pick` is a delegate type, so method groups such as `Balancer.LeastOutstanding` convert to it. `Queue<T>` can't look at its last item, so the simulation keeps each server's last finish time beside its queue. `HashRing` re-sorts with `OrderBy`, which is stable. `Simulate` rounds with `MidpointRounding.AwayFromZero` to match JavaScript. The checks use `CountBy`, new in .NET 9, to count keys per server. It runs in the .NET SDK container.

```csharp
// How a load balancer picks a server, health checks that take a failing server out and put it back, and
// consistent hashing. The same numbers as the TypeScript lab.

/// <summary>Chooses a server from how many requests each is still working on.</summary>
public delegate int Pick(int[] outstanding, Func<double> random);

public static class Balancer
{
    public static Pick RoundRobin()
    {
        var next = 0;
        return (outstanding, _) => next++ % outstanding.Length;
    }

    /// <summary>The fewest requests in progress; ties go to the lowest number.</summary>
    public static int LeastOutstanding(int[] outstanding, Func<double> _) => Array.IndexOf(outstanding, outstanding.Min());

    public static int Random(int[] outstanding, Func<double> random) => (int)(random() * outstanding.Length);

    /// <summary>Two servers at random, and the less busy of the two.</summary>
    public static int TwoChoices(int[] outstanding, Func<double> random)
    {
        var a = (int)(random() * outstanding.Length);
        var b = (int)(random() * outstanding.Length);
        return outstanding[b] < outstanding[a] ? b : a;
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

    public record Latency(double Mean, double P50, double P99);

    /// <summary>Random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms.</summary>
    public static Latency Simulate(Pick pick, int servers, double busy, int requests, uint seed)
    {
        var random = Seeded(seed);
        var meanWorkMs = 0.95 * 10 + 0.05 * 200;
        var gapMs = meanWorkMs / (busy * servers);
        var finishes = Enumerable.Range(0, servers).Select(_ => new Queue<double>()).ToArray(); // when each queued request ends
        var lastEnds = new double[servers];
        double now = 0, total = 0;
        var times = new double[requests];
        for (var i = 0; i < requests; i++)
        {
            now += -gapMs * Math.Log(1 - random());
            foreach (var queue in finishes)
                while (queue.Count > 0 && queue.Peek() <= now) queue.Dequeue();
            var s = pick(finishes.Select(q => q.Count).ToArray(), random);
            var workMs = random() < 0.05 ? 200 : 10;
            var ends = Math.Max(now, finishes[s].Count > 0 ? lastEnds[s] : 0) + workMs; // Queue<T> can't peek at its back
            finishes[s].Enqueue(ends);
            lastEnds[s] = ends;
            times[i] = ends - now;
            total += ends - now;
        }
        Array.Sort(times);
        double Percentile(double p) => times[Math.Max(1, (int)Math.Ceiling(p / 100 * times.Length)) - 1];
        static double Round(double x) => Math.Round(x, MidpointRounding.AwayFromZero); // the default rounds halves to even
        return new(Round(total / requests), Round(Percentile(50)), Round(Percentile(99)));
    }

    /// <summary>nginx's smooth weighted round-robin. An array of pairs, so the order that breaks ties is fixed.</summary>
    public static Func<string> SmoothWeighted(params (string Name, int Weight)[] servers)
    {
        var total = servers.Sum(s => s.Weight);
        var current = new int[servers.Length];
        return () =>
        {
            var best = 0;
            for (var i = 0; i < servers.Length; i++)
            {
                current[i] += servers[i].Weight;
                if (current[i] > current[best]) best = i;
            }
            current[best] -= total;
            return servers[best].Name;
        };
    }

    public static string PickHealthy(IEnumerable<(string Name, Health Health)> servers, int turn)
    {
        var up = servers.Where(s => s.Health.Up).Select(s => s.Name).ToArray();
        if (up.Length == 0) throw new InvalidOperationException("no healthy servers: answer 503");
        return up[turn % up.Length];
    }

    /// <summary>
    /// FNV-1a, then a mixing step, over UTF-16 code units like JavaScript. string.GetHashCode() can't place keys:
    /// it's randomised per process, so two servers would disagree.
    /// </summary>
    public static uint Hash(string text)
    {
        var h = 0x811c9dc5u;
        foreach (var c in text) h = (h ^ c) * 0x01000193;
        h = (h ^ (h >> 16)) * 0x85ebca6b;
        h = (h ^ (h >> 13)) * 0xc2b2ae35;
        return h ^ (h >> 16);
    }

    public static string Modulo(string key, IReadOnlyList<string> servers) => servers[(int)(Hash(key) % (uint)servers.Count)];
}

/// <summary><c>fall</c> failures in a row mark a server down; <c>rise</c> successes in a row bring it back.</summary>
public sealed class Health(int fall = 3, int rise = 2)
{
    private int _streak;
    public bool Up { get; private set; } = true;

    public void Record(bool ok)
    {
        if (ok == Up)
        {
            _streak = 0;
            return;
        }
        if (++_streak >= (Up ? fall : rise))
        {
            Up = !Up;
            _streak = 0;
        }
    }
}

/// <summary>Servers and keys on one circle of hash values; a key belongs to the first server clockwise from it.</summary>
public sealed class HashRing
{
    private List<(uint At, string Server)> _points = [];
    private readonly int _replicas;

    public HashRing(IEnumerable<string> servers, int replicas = 100)
    {
        _replicas = replicas;
        foreach (var s in servers) Add(s);
    }

    public void Add(string server)
    {
        var added = Enumerable.Range(0, _replicas).Select(r => (At: Balancer.Hash($"{server}#{r}"), Server: server));
        _points = _points.Concat(added).OrderBy(p => p.At).ToList(); // OrderBy is stable; List.Sort isn't
    }

    public void Remove(string server) => _points.RemoveAll(p => p.Server == server);

    public string ServerFor(string key)
    {
        if (_points.Count == 0) throw new InvalidOperationException("the ring is empty");
        var h = Balancer.Hash(key);
        int lo = 0, hi = _points.Count; // binary search for the first point at or after h
        while (lo < hi)
        {
            var mid = (lo + hi) / 2;
            if (_points[mid].At < h) lo = mid + 1;
            else hi = mid;
        }
        return _points[lo % _points.Count].Server; // past the last point, wrap round to the first
    }
}
```

```csharp
// Checks: the same numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var keys = Enumerable.Range(0, 10_000).Select(i => $"user:{i}").ToArray();
string[] four = ["cache-a", "cache-b", "cache-c", "cache-d"];

var pick = Balancer.RoundRobin();
int[] queues = [5, 0, 0];
Check(Enumerable.Range(0, 6).Select(_ => pick(queues, () => 0)).SequenceEqual([0, 1, 2, 0, 1, 2]), "round-robin");
Check(Balancer.LeastOutstanding(queues, () => 0) == 1, "least outstanding");

var weighted = Balancer.SmoothWeighted(("a", 5), ("b", 1), ("c", 1));
var order = string.Concat(Enumerable.Range(0, 7).Select(_ => weighted()));
Check(order == "aabacaa", order);

Check(Balancer.Simulate(Balancer.RoundRobin(), 4, 0.8, 100_000, 7) == new Balancer.Latency(214, 138, 1_158), "round-robin");
Check(Balancer.Simulate(Balancer.Random, 4, 0.8, 100_000, 7) == new Balancer.Latency(255, 159, 1_588), "random");
Check(Balancer.Simulate(Balancer.LeastOutstanding, 4, 0.8, 100_000, 7) == new Balancer.Latency(68, 17, 466), "least");
var two = Balancer.Simulate(Balancer.TwoChoices, 4, 0.8, 100_000, 7);
Check(two == new Balancer.Latency(96, 25, 495), two);

var health = new Health(3, 2);
var states = new[] { false, false, true, false, false, false, true, true }.Select(ok => { health.Record(ok); return health.Up; });
Check(states.SequenceEqual([true, true, true, true, true, false, false, true]), "fall and rise");

var servers = new[] { "app-1", "app-2", "app-3" }.Select(name => (Name: name, Health: new Health(3, 2))).ToArray();
for (var i = 0; i < 3; i++) servers[1].Health.Record(false);
Check(Enumerable.Range(0, 4).Select(t => Balancer.PickHealthy(servers, t)).SequenceEqual(["app-1", "app-3", "app-1", "app-3"]), "skips app-2");
foreach (var s in servers) for (var i = 0; i < 3; i++) s.Health.Record(false);
try
{
    Balancer.PickHealthy(servers, 0);
    Check(false, "expected no healthy servers");
}
catch (InvalidOperationException)
{
    // answer 503
}

string[] five = [.. four, "cache-e"];
var movedByModulo = keys.Count(k => Balancer.Modulo(k, four) != Balancer.Modulo(k, five));
Check(Math.Abs(movedByModulo - 8_000) < 200, movedByModulo);
var ring = new HashRing(four, 100);
var before = keys.Select(ring.ServerFor).ToArray();
ring.Add("cache-e");
var moved = keys.Where((k, i) => ring.ServerFor(k) != before[i]).ToArray();
Check(Math.Abs(moved.Length - 2_000) < 300 && moved.All(k => ring.ServerFor(k) == "cache-e"), moved.Length);
ring.Remove("cache-e");
Check(keys.Select(ring.ServerFor).SequenceEqual(before), "removing it puts the keys back");

double Busiest(int replicas)
{
    var r = new HashRing(four, replicas);
    return keys.CountBy(r.ServerFor).Max(g => g.Value) / (keys.Length / 4.0);
}
Check(Busiest(1) > 1.4 && Busiest(100) < 1.2, (Busiest(1), Busiest(100)));
Console.WriteLine("all balancing checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/01-load-balancing-and-proxies/labs/csharp). `python3 labs/run.py load-balancing-and-proxies/csharp`.

## Common pitfalls

1. **Placing keys with the language's own hash.** Randomised per process in Python, Rust, Go and C#, so every server, and every restart, disagrees. Use a stable hash.
2. **Signed hashes in Java.** `hash % n` goes negative and `<` orders the ring wrongly. Use the unsigned methods.
3. **Hashing text by whatever unit the language gives.** UTF-16 units, UTF-8 bytes and code points differ outside ASCII. Agree on UTF-8 bytes when services in different languages must agree.
4. **An unstable sort for ring points.** Rare collisions then resolve differently in different implementations.
5. **Iterating a Go map where order matters.** Weighted round-robin breaks ties by order; Go randomises map order on purpose.

## Check your understanding

1. Why do Python, Rust and C# randomise their string hashes, and why does that make them useless for a hash ring?
2. In Java, `hash("user:7") % 4` returns −3. What happened, and what's the fix?
3. Java's `String.hashCode` is stable. Why not use it for the ring anyway?
4. Two services, one in Go and one in Java, hash the key `café` with the labs' FNV-1a. Will they put it on the same server? Why?
5. Why does C#'s ring use `OrderBy` rather than `List.Sort`?

<details>
<summary>Answers — after your attempt</summary>

1. To defend against hash flooding: if attackers can't predict the hash, they can't choose keys that all collide. Placement needs the same hash for the same key in every process, every time, and a randomised hash gives a different one per process.
2. The hash's top bit was set, so Java's signed `int` read it as negative, and `%` keeps the sign of the left side. Use `Integer.remainderUnsigned(hash, 4)`.
3. It's a polynomial in the characters with multiplier 31, so keys that differ only in their last character get values close together, and they bunch up on the ring instead of spreading out. The lab's hash adds a mixing step for the same reason.
4. No. Go hashes the UTF-8 bytes, and é is two bytes there. Java hashes UTF-16 code units, where é is one. Different inputs give different hashes. Converting to UTF-8 bytes in Java (`getBytes(StandardCharsets.UTF_8)`) would make them agree.
5. `List.Sort` isn't stable, so points with equal hashes could end up in either order. `OrderBy` is stable, so they stay in the order added, which matches the other languages.

</details>

## Practice — independent task

**Make your language's ring agree with another language's.**

1. Change your lab's `hash` to work on UTF-8 bytes (Java: `getBytes(StandardCharsets.UTF_8)`; C#: `Encoding.UTF8.GetBytes`; Python: `.encode()`; Go and Rust already do).
2. Add a test with ten keys that include `café`, `naïve` and an emoji. Print which of four servers each goes to.
3. Run the same keys through a second language's lab, changed the same way, and compare.

**Done when:** both languages put all ten keys on the same servers, the original 10,000 ASCII keys still give the same counts as before, and you can say why the ASCII keys didn't change.

## Before moving on

You can say why the built-in string hash can't place keys, handle a 32-bit hash in Java, and name the balancers written in your language and their default algorithms.

**Recap.** The algorithms translate line for line, and all six labs produce the same simulation numbers. Placement is where languages differ. Built-in string hashes are randomised against hash flooding (Python, Rust, Go, C#) or weak (Java), so write a stable hash such as FNV-1a. Java needs `remainderUnsigned` and `compareUnsigned` to treat a hash as unsigned. Agree on UTF-8 bytes when text can be non-ASCII, and sort ring points stably. In production, Go and Rust host many real balancers (Traefik, Caddy, Pingora, tower), and YARP and tower default to two random choices.

## Related

- [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|Load balancing and proxies]]: the main lesson
- [[architecture/02-building-blocks/02-caching/in-other-languages|Caching in other languages]]: the cache nodes these rings place keys on
- [[architecture/01-system-design-fundamentals/02-scalability-and-performance/in-other-languages|Scalability in other languages]]: the seeded generator and percentiles in the same languages
