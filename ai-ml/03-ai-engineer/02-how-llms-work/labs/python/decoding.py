"""Decoding: from a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab."""
import math
from collections.abc import Callable

Dist = list[tuple[str, float]]  # (token, probability), in a fixed order so sampling is reproducible


def seeded_random(seed: int) -> Callable[[], float]:
    """mulberry32: a tiny seeded generator. Python's random.Random(seed) would also do, but this
    one gives the same numbers in every language in this companion."""
    a = seed & 0xFFFFFFFF

    def next_float() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = a
        t = _imul(t ^ (t >> 15), t | 1)
        t ^= (t + _imul(t ^ (t >> 7), t | 61)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return next_float


def _imul(x: int, y: int) -> int:
    return (x * y) & 0xFFFFFFFF  # 32-bit multiply, like JavaScript's Math.imul (unsigned)


def softmax(scores: list[tuple[str, float]], temperature: float) -> Dist:
    scaled = [(tok, s / temperature) for tok, s in scores]
    top = max(s for _, s in scaled)  # subtract the max so exp() can't overflow
    exps = [(tok, math.exp(s - top)) for tok, s in scaled]
    total = sum(e for _, e in exps)
    return [(tok, e / total) for tok, e in exps]


def top_k(dist: Dist, k: int) -> Dist:
    return _renormalise(sorted(dist, key=lambda e: -e[1])[:k])


def top_p(dist: Dist, p: float) -> Dist:
    kept, cumulative = [], 0.0
    for entry in sorted(dist, key=lambda e: -e[1]):
        kept.append(entry)
        cumulative += entry[1]
        if cumulative >= p:
            break
    return _renormalise(kept)


def _renormalise(entries: Dist) -> Dist:
    total = sum(p for _, p in entries)
    return [(tok, p / total) for tok, p in entries]


def sample(dist: Dist, random: Callable[[], float]) -> str:
    r = random()
    for tok, p in dist:
        r -= p
        if r < 0:
            return tok
    return dist[-1][0]


def greedy(dist: Dist) -> str:
    return max(dist, key=lambda e: e[1])[0]
