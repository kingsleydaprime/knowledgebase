"""histogram.py — record latencies in a real Prometheus histogram, then estimate percentiles
from its buckets the way Prometheus's histogram_quantile() does."""
from prometheus_client import CollectorRegistry, Histogram, generate_latest

BUCKETS_MS = (25, 50, 100, 250, 500, 1000, 2500, 5000)


def record(latencies_ms: list[float]) -> CollectorRegistry:
    registry = CollectorRegistry()
    h = Histogram("request_duration_ms", "Request latency", buckets=BUCKETS_MS, registry=registry)
    for ms in latencies_ms:
        h.observe(ms)
    return registry


def cumulative_buckets(registry: CollectorRegistry) -> list[tuple[float, float]]:
    """[(upper_bound, cumulative_count), ...], the way Prometheus stores them."""
    samples = next(iter(registry.collect())).samples
    return [(float(s.labels["le"]), s.value) for s in samples if s.name.endswith("_bucket")]


def estimate_quantile(q: float, buckets: list[tuple[float, float]]) -> float:
    """Find the bucket holding rank q × total; assume values are spread evenly inside it."""
    total = buckets[-1][1]
    rank = q * total
    lower_bound, lower_count = 0.0, 0.0
    for upper_bound, count in buckets:
        if count >= rank:
            if upper_bound == float("inf"):
                return lower_bound  # Prometheus returns the last finite bound here
            return lower_bound + (upper_bound - lower_bound) * (rank - lower_count) / (count - lower_count)
        lower_bound, lower_count = upper_bound, count
    return lower_bound


def exposition(registry: CollectorRegistry) -> str:
    """What a Prometheus server scrapes from /metrics."""
    return generate_latest(registry).decode()
