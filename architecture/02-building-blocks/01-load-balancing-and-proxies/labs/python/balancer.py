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
