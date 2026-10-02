"""rates.py — decorators as Python decorators: functions that wrap functions."""
import functools


class FlakyApi:
    """Stands in for a slow, flaky HTTP API: fails its first `failures` calls."""

    def __init__(self, failures: int):
        self.calls = 0
        self.failures = failures

    def rate(self, base: str, quote: str) -> int:
        self.calls += 1
        if self.calls <= self.failures:
            raise ConnectionError("503 from rates API")
        return 2000 if (base, quote) == ("GBP", "NGN") else 1


def retrying(attempts: int):
    """A decorator factory: @retrying(3) adds retries to any function."""
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args):
            for attempt in range(attempts):
                try:
                    return fn(*args)
                except ConnectionError:
                    if attempt == attempts - 1:
                        raise
        return wrapper
    return decorate


def logged(log: list):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args):
            value = fn(*args)
            log.append(f"{'->'.join(args)} = {value}")
            return value
        return wrapper
    return decorate


def build(api: FlakyApi, log: list):
    """Stack them: log(cache(retry(api))). functools.cache is a ready-made caching proxy."""
    @logged(log)
    @functools.cache
    @retrying(3)
    def rate(base: str, quote: str) -> int:
        return api.rate(base, quote)
    return rate
