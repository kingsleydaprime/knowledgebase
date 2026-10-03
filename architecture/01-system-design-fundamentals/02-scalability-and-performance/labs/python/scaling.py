"""The arithmetic behind performance and scalability: percentiles, how waiting grows as a server fills up,
the bottleneck that sets a system's throughput, and why adding machines stops helping. The same numbers as
the TypeScript lab, because the random number generator is the same one, bit for bit."""
import math
from typing import Callable, Iterable

MASK = 0xFFFFFFFF  # Python ints never overflow, so 32-bit wrap-around has to be asked for


def percentile(samples: Iterable[float], p: float) -> float:
    """Nearest rank: p99 of 1,000 samples is the 990th smallest. (numpy.percentile interpolates by default.)"""
    ordered = sorted(samples)
    if not ordered:
        raise ValueError("no samples")
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


def mean(samples: list[float]) -> float:
    total = 0.0
    for x in samples:  # a plain loop: sum() compensates for rounding since 3.12, which TypeScript doesn't
        total += x
    return total / len(samples)


def seeded(seed: int) -> Callable[[], float]:
    """mulberry32, the same generator as the TypeScript lab."""
    a = seed & MASK

    def imul(x: int, y: int) -> int:
        return (x * y) & MASK

    def next_random() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & MASK
        t = imul(a ^ (a >> 15), a | 1)
        t ^= (t + imul(t ^ (t >> 7), t | 61)) & MASK
        return (t ^ (t >> 14)) / 4294967296

    return next_random


def exponential(random: Callable[[], float], mean_value: float) -> float:
    return -mean_value * math.log(1 - random())


def response_time(service_ms: float, utilisation: float) -> float:
    """M/M/1: service time ÷ (1 − utilisation)."""
    return math.inf if utilisation >= 1 else service_ms / (1 - utilisation)


def simulate_server(service_ms: float, utilisation: float, requests: int, seed: int) -> dict:
    random = seeded(seed)
    gap_ms = service_ms / utilisation
    arrives = free = 0.0
    times = []
    for _ in range(requests):
        arrives += exponential(random, gap_ms)
        starts = max(arrives, free)
        free = starts + exponential(random, service_ms)
        times.append(free - arrives)
    return {"mean": mean(times), "p50": percentile(times, 50), "p99": percentile(times, 99)}


def throughput(stages: list[tuple[str, float]]) -> tuple[float, str]:
    """A request passes every stage, so the system handles only as many as its slowest."""
    name, per_second = min(stages, key=lambda s: s[1])
    return per_second, name


def amdahl(n: float, serial: float) -> float:
    return 1 / (serial + (1 - serial) / n)


def usl(n: float, alpha: float, beta: float) -> float:
    return n / (1 + alpha * (n - 1) + beta * n * (n - 1))


def usl_peak(alpha: float, beta: float) -> float:
    return math.sqrt((1 - alpha) / beta)
