"""A small in-memory message broker: queues, topics, redelivery, a dead-letter queue, a partitioned log, and
load levelling. The same numbers as the TypeScript lab. The bounded queue is asyncio's own."""
from dataclasses import dataclass
from typing import Callable

MASK = 0xFFFFFFFF


@dataclass
class Delivery:
    id: str
    body: str
    key: str | None
    attempt: int


@dataclass
class _Stored:
    id: str
    body: str
    key: str | None
    attempts: int = 0
    visible_at: float = 0


class Broker:
    """Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery."""

    def __init__(self, now: Callable[[], float], visibility_ms: float, max_attempts: int):
        self._now, self._visibility_ms, self._max_attempts = now, visibility_ms, max_attempts
        self._subscribers: dict[str, list[str]] = {}
        self._queues: dict[str, list[_Stored]] = {}
        self._dead: dict[str, list[_Stored]] = {}
        self._next_id = 1

    def subscribe(self, topic: str, subscription: str) -> None:
        self._subscribers.setdefault(topic, []).append(subscription)
        self._queues[subscription], self._dead[subscription] = [], []

    def publish(self, topic: str, body: str, key: str | None = None) -> str:
        id_ = f"m{self._next_id}"
        self._next_id += 1
        for s in self._subscribers.get(topic, []):  # no subscribers: nobody keeps it
            self._queues[s].append(_Stored(id_, body, key))
        return id_

    def receive(self, subscription: str) -> Delivery | None:
        queue = self._queues[subscription]
        i = 0
        while i < len(queue):
            m = queue[i]
            if m.visible_at > self._now():
                i += 1  # a consumer has it
            elif m.attempts >= self._max_attempts:
                self._dead[subscription].append(queue.pop(i))  # poison: stop retrying it
            else:
                m.attempts += 1
                m.visible_at = self._now() + self._visibility_ms
                return Delivery(m.id, m.body, m.key, m.attempts)
        return None

    def ack(self, subscription: str, id_: str) -> None:
        self._queues[subscription] = [m for m in self._queues[subscription] if m.id != id_]

    def depth(self, subscription: str) -> int:
        return len(self._queues[subscription])

    def dead_letters(self, subscription: str) -> list[str]:
        return [m.body for m in self._dead[subscription]]


def idempotent(handle: Callable[[str], None], seen: set[str]) -> Callable[[Delivery], str]:
    def run(d: Delivery) -> str:
        if d.id in seen:
            return "duplicate"
        handle(d.body)
        seen.add(d.id)
        return "processed"

    return run


def partition_for(key: str, partitions: int) -> int:
    """The same stable hash as the TypeScript lab. Python's hash() changes every run, so it can't choose partitions."""
    h = 0x811C9DC5
    for ch in key:
        h = ((h ^ ord(ch)) * 0x01000193) & MASK
    h = ((h ^ (h >> 16)) * 0x85EBCA6B) & MASK
    h = ((h ^ (h >> 13)) * 0xC2B2AE35) & MASK
    return (h ^ (h >> 16)) % partitions


class PartitionedLog:
    """Kafka-like: messages are kept; each consumer group has its own offset per partition."""

    def __init__(self, partitions: int):
        self._partitions: list[list[str]] = [[] for _ in range(partitions)]
        self._offsets: dict[str, list[int]] = {}

    def append(self, key: str, body: str) -> int:
        p = partition_for(key, len(self._partitions))
        self._partitions[p].append(body)
        return p

    def poll(self, group: str, partition: int) -> str | None:
        offset = self._offsets_for(group)[partition]
        messages = self._partitions[partition]
        return messages[offset] if offset < len(messages) else None

    def commit(self, group: str, partition: int) -> None:
        self._offsets_for(group)[partition] += 1

    def _offsets_for(self, group: str) -> list[int]:
        return self._offsets.setdefault(group, [0] * len(self._partitions))  # a new group starts at the beginning


def level_load(arrivals: list[int], per_second: int) -> dict:
    served = sum(min(a, per_second) for a in arrivals)
    rejected = sum(max(0, a - per_second) for a in arrivals)
    waiting: list[list[int]] = []  # [arrival second, count], oldest first
    depth = peak_depth = max_wait = cleared_after = 0
    second = 0
    while second < len(arrivals) or depth > 0:
        a = arrivals[second] if second < len(arrivals) else 0
        if a > 0:
            waiting.append([second, a])
        depth += a
        capacity = per_second
        while capacity > 0 and waiting:
            oldest = waiting[0]
            n = min(capacity, oldest[1])
            oldest[1] -= n
            capacity -= n
            depth -= n
            max_wait = max(max_wait, second - oldest[0])
            if oldest[1] == 0:
                waiting.pop(0)
        peak_depth = max(peak_depth, depth)
        if depth > 0:
            cleared_after = second + 2
        second += 1
    return {"sync": {"served": served, "rejected": rejected},
            "queued": {"peak_depth": peak_depth, "cleared_after_seconds": cleared_after, "max_wait_seconds": max_wait}}
