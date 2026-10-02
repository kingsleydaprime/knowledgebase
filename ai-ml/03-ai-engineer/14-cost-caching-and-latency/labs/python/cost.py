"""Pricing, prefix diagnosis, canonical JSON, a cascade and latency percentiles, with money as Decimal.
The same numbers as the TypeScript lab."""
import json
import math
import os
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Price:
    """US dollars per million tokens, as exact decimals: 0.1 + 0.2 is 0.3 here."""
    input: Decimal
    output: Decimal
    cache_write: Decimal
    cache_read: Decimal


def price(*values: str) -> Price:
    return Price(*map(Decimal, values))


# Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them.
PRICES = {
    "claude-haiku-4-5": price("1", "5", "1.25", "0.1"),
    "claude-sonnet-5-5": price("2", "10", "2.5", "0.2"),
    "claude-opus-5-5": price("4", "20", "5", "0.2"),
    "local": price("0", "0", "0", "0"),
}


def cost(p: Price, input_tokens: int = 0, output_tokens: int = 0, cache_write_tokens: int = 0,
         cache_read_tokens: int = 0) -> Decimal:
    """`input_tokens` counts only input that was neither written to nor read from the cache."""
    return (input_tokens * p.input + output_tokens * p.output + cache_write_tokens * p.cache_write
            + cache_read_tokens * p.cache_read) / 1_000_000


def break_even_calls(p: Price) -> int:
    """Caching n calls costs write + (n − 1) × read; not caching costs n × input."""
    return math.floor((p.cache_write - p.cache_read) / (p.input - p.cache_read)) + 1


def shared_prefix(a: str, b: str) -> int:
    return len(os.path.commonprefix([a, b]))  # works on any two strings, not only paths


def stable_json(value) -> str:
    """Sorted keys and no spaces. json.dumps's defaults put a space after every comma and colon,
    and keep keys in insertion order, so two equal dicts can still give different bytes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Tier:
    name: str
    cost: Decimal  # per call
    answer: Callable[[str], str]
    accept: Callable[[str], bool]  # the last tier's answer is used whatever this says


def cascade(text: str, tiers: list[Tier]) -> tuple[str, str, Decimal]:
    spent = Decimal(0)
    for i, tier in enumerate(tiers):
        answer = tier.answer(text)
        spent += tier.cost  # a rejected answer was still paid for
        if i == len(tiers) - 1 or tier.accept(answer):
            return answer, tier.name, spent
    raise ValueError("a cascade needs at least one tier")


def percentile(values: list[float], p: float) -> float:
    """Nearest rank: the smallest value that at least p% of the values are less than or equal to.
    statistics.quantiles and numpy.percentile interpolate instead, and give different numbers."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)]


async def time_stream(chunks: AsyncIterator[str], now: Callable[[], float]) -> tuple[str, float, float]:
    """Read a stream to the end; return the text, the time to first token and the total, in ms."""
    started, first, text = now(), None, ""
    async for chunk in chunks:
        if first is None:
            first = now() - started
        text += chunk
    total = now() - started
    return text, total if first is None else first, total
