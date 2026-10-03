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
