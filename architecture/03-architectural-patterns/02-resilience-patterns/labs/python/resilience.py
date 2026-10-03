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
