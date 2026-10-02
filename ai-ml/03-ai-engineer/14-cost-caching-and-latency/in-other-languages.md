# Cost, Caching and Latency in Other Languages

> **[Intermediate]** · A companion to [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|cost, caching and latency]], which prices calls from their token counts, finds what breaks a prompt cache, cascades from keyword rules to a model and measures p95 and time to first token in TypeScript. This page does the same in Python, Go, Java, Rust and C#, and every lab gets **the same numbers**: $13.30 against $2.5138 for the cached classifier, a 27-character shared prefix, the same six escalated tickets, a p95 of 9000 ms. Getting there exposed the three places where languages genuinely differ for this topic: how they add up money, what bytes their JSON produces, and what they mean by "p95".

## Before you start

You can already:

- Price a call, explain the prefix rule and silent invalidators, build a cascade and read percentiles → [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Add up model costs exactly in your language, and say why a `double` isn't good enough.
2. Produce the same JSON bytes for the same data every time, so a prompt cache can hit.
3. Say which definition of p95 your language's statistics functions use, and what it does to a dashboard.

## The kid version

Six shopkeepers add up the same thousand tiny sales. Five of them get exactly $2.5138. The sixth uses a calculator that rounds every sale a tiny bit, and gets $2.513799999999958: too small a difference to notice on one receipt, but it means the books never quite match. Then all six copy out the same shopping list. Each one writes it a little differently: one puts spaces after the commas, one sorts the items, one writes "<" as a code. Every list says the same thing, but a machine that only recognises lists it has seen *letter for letter* treats each one as new.

**Where the analogy stops working.** The rounding calculator isn't broken: computers store most decimal fractions as the nearest binary fraction, so the tiny error is built into how ordinary numbers work, not a fault in one machine.

## 1. The tools, by ecosystem

| Language | Exact money | Same JSON bytes every time | Percentiles in the standard library | A stream of chunks |
|---|---|---|---|---|
| TypeScript | none built in: integer minor units, or a decimal library | `JSON.stringify` keeps insertion order: sort the keys yourself | none | async iterator over a `ReadableStream` |
| Python | **`decimal.Decimal`** | `json.dumps(…, sort_keys=True, separators=(",", ":"))` | `statistics.quantiles` (interpolates); numpy's `percentile` | async generator |
| Go | integer minor units (`shopspring/decimal` if you need more) | `encoding/json` sorts map keys already, but **escapes `<` and `>`** | none | a channel, or `bufio.Scanner` over the body |
| Java | **`BigDecimal`** (compare with `compareTo`) | Jackson's `ORDER_MAP_ENTRIES_BY_KEYS` and `SORT_PROPERTIES_ALPHABETICALLY` | none (Apache Commons Math) | `Stream<String>` from `BodyHandlers.ofLines()` |
| Rust | integer newtype (`rust_decimal` if you need more) | `serde_json::Value` is sorted already; a `HashMap` is **random per run** | none | a `Stream`, or a channel receiver |
| C# | **`decimal`**, built into the language | `System.Text.Json` keeps insertion order, has no sort option, and **escapes `<` and `>`** | none | `IAsyncEnumerable<string>` |
| C, C++ | — | — | — | — |

The provider SDKs all report the same usage fields (input, output, cache write and cache read tokens) in every language, so the pricing code is the same everywhere. What isn't the same is in the next section. There's no C or C++ section, for the same reason as in the other AI-engineering companions: the application that calls the model and pays the bill is almost never written in C or C++.

## 2. Three things that change between languages

### Money: floats drift, so use exact types

Most languages store `0.2` as the nearest binary fraction, which is very slightly wrong. One call's cost is fine. Add up 1,000 calls one at a time, as a log aggregator does, and the errors pile up: in floating point, the cached classifier's 1,000 calls come to **$2.513799999999958** instead of $2.5138. That's harmless on one dashboard and a problem the moment two systems must agree, such as your cost report and the provider's invoice.

The fix is a type that stores decimal fractions exactly. Python has `Decimal`, Java `BigDecimal` and C# `decimal`. Go and Rust have no decimal type in the standard library, so their labs count in **picodollars**, millionths of a millionth of a dollar. A token count times a price in micro-dollars per million tokens is then a whole number, and integers add up exactly. The TypeScript lab used plain numbers and rounded to cents before comparing; for real billing code in TypeScript, use integer minor units in the same way.

One trap: Java's `BigDecimal.equals` compares the scale as well as the value, so `2.5138` and `2.51380000000` are "not equal". Compare money with `compareTo`.

### Prompt bytes: the same data, different JSON

A prompt cache matches bytes, and so does a recorded cassette. If a prompt contains JSON (tool definitions, a user's settings, retrieved records), every language turns the same data into slightly different text:

| Language | Key order | Spaces | `<` in a string |
|---|---|---|---|
| TypeScript | insertion order | none | `<` |
| Python, `json.dumps` defaults | insertion order | after every `,` and `:` | `<` |
| Go, `json.Marshal` | maps sorted; struct fields in declared order | none | `\u003c` |
| Java, Jackson defaults | a `HashMap`'s arbitrary order; fields in declared order | none | `<` |
| Rust, `serde_json` | `Value` sorted; a `HashMap` in a random order each run | none | `<` |
| C#, `System.Text.Json` | insertion order | none | `\u003C` |

So two services, one in Python and one in Go, building "the same" prompt don't share a cache entry. A Rust service that puts a `HashMap` into its system prompt misses its own cache every time it restarts. Every lab here has a `stable_json` that gives `{"tools":["search"],"user":{"id":7,"tier":"pro"}}`, byte for byte, for the same data: sorted keys, no spaces, and `<` left alone.

### Percentiles: "p95" means several different numbers

The main lesson's ten latencies have a p95 of **9000 ms** by nearest rank, the definition every lab here uses: the smallest value that at least 95% of the values are no greater than. On the same ten numbers:

- numpy's `percentile` and Python's `statistics.quantiles(…, method="inclusive")` interpolate between the two slowest calls and give **5490 ms**;
- `statistics.quantiles` with its default method gives **12,510 ms**, more than the slowest call that actually happened;
- `statistics.median` gives **1010 ms**, halfway between 1000 and 1020, where nearest rank gives 1000.

None of these is wrong; they're different definitions, and with few samples they differ a lot. Before you compare a p95 from your logs with one from a monitoring tool, find out which definition each uses. With thousands of samples, the definitions converge.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| 2,000 input and 500 output tokens on Sonnet 5.5 | $0.009 |
| 1,000 calls, 6,000-token prefix, uncached / cached | $13.30 / $2.5138, exactly |
| answers' share of the cached bill | 40% |
| calls before caching pays, 5-minute / 1-hour TTL | 2 / 3 |
| shared prefix with a timestamp at the front | 27 characters |
| canonical JSON | `{"tools":["search"],"user":{"id":7,"tier":"pro"}}` |
| cascade on the golden set | escalated t04, t10, t12, t14, t17, t19; wrong t15, t20; $0.012 |
| p50 / p95 of the ten latencies | 1000 / 9000 ms |
| time to first token / total | 800 / 1300 ms |

The cascades read the evals lab's golden set and use that lab's keyword rules in the same language, imported rather than copied.

## Terms used in this lesson

1. **Floating point**: This is how most languages store non-whole numbers by default (`number`, `float`, `double`, `f64`): as a binary fraction, which can't represent most decimal fractions such as 0.1 exactly.
2. **Decimal type**: This is a number type that stores decimal digits exactly, such as Python's `Decimal`, Java's `BigDecimal` and C#'s `decimal`. It is slower than floating point and exact for money.
3. **Minor units**: This means storing money as a whole number of the smallest unit you need: cents for a shop, picodollars for token prices.
4. **Canonical JSON**: This is a single agreed way of writing a piece of data as JSON, such as sorted keys and no spaces, so the same data always gives the same bytes.
5. **Nearest-rank percentile**: This is a percentile that is always one of the measured values: sort them and take the value at position ⌈p/100 × n⌉.
6. **Interpolated percentile**: This is a percentile computed between two measured values, in proportion to where the rank falls. Most statistics libraries use one of several such methods by default.

## 4. Python

Python's `Decimal` makes the money exact with no extra work: build prices from strings (`Decimal("0.2")`, never `Decimal(0.2)`, which copies the float's error) and every sum stays exact. The test also shows the float version drifting. `os.path.commonprefix` finds a shared prefix of any two strings, not only paths. `json.dumps` needs two arguments to be canonical, because its default separators add spaces. And the percentile test shows the three answers from §2 side by side.

```python
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
```

```python
import json
import statistics
import sys
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from cost import (PRICES, Tier, break_even_calls, cascade, cost, percentile, shared_prefix, stable_json,
                  time_stream)

sys.path.insert(0, str(Path(__file__).parents[3] / "12-evals" / "labs" / "python"))
from evals import keywords, load_golden  # noqa: E402  the shared golden set and the keyword rules

SONNET = PRICES["claude-sonnet-5-5"]


class Cost(unittest.IsolatedAsyncioTestCase):
    def test_output_costs_five_times_input(self):
        self.assertEqual(cost(SONNET, input_tokens=2000, output_tokens=500), Decimal("0.009"))

    def test_caching_a_6000_token_prefix_across_1000_calls(self):
        uncached = 1000 * cost(SONNET, input_tokens=6150, output_tokens=100)
        first = cost(SONNET, cache_write_tokens=6000, input_tokens=150, output_tokens=100)
        each = cost(SONNET, cache_read_tokens=6000, input_tokens=150, output_tokens=100)
        cached = first + sum([each] * 999)
        self.assertEqual((uncached, cached), (Decimal("13.30"), Decimal("2.5138")))  # exact, to the last digit
        self.assertEqual(round(1000 * cost(SONNET, output_tokens=100) / cached * 100), 40)

        # The same sum in floats drifts: a running total of 999 small amounts isn't 2.5138.
        float_total = float(first) + sum([float(each)] * 999)
        self.assertNotEqual(float_total, 2.5138)
        self.assertAlmostEqual(float_total, 2.5138, places=9)

    def test_a_cache_write_pays_for_itself_on_the_second_call(self):
        self.assertEqual(break_even_calls(SONNET), 2)
        one_hour = replace(SONNET, cache_write=Decimal("4"))  # 1-hour entries cost 2× to write
        self.assertEqual(break_even_calls(one_hour), 3)

    def test_a_timestamp_at_the_front_leaves_nothing_to_cache(self):
        system = "You classify support tickets. Label by what the team has to do next. " * 20
        front = lambda date: f"Today is {date}.\n{system}\nhelp"  # noqa: E731
        end = lambda date: f"{system}\nToday is {date}.\nhelp"  # noqa: E731
        a, b = "2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z"
        self.assertEqual(shared_prefix(front(a), front(b)), 27)
        self.assertEqual(shared_prefix(end(a), end(b)), len(system) + 28)

    def test_unsorted_json_changes_the_bytes(self):
        a = {"tools": ["search"], "user": {"tier": "pro", "id": 7}}
        b = {"user": {"id": 7, "tier": "pro"}, "tools": ["search"]}
        self.assertNotEqual(json.dumps(a), json.dumps(b))
        self.assertEqual(json.dumps(b, sort_keys=True), '{"tools": ["search"], "user": {"id": 7, "tier": "pro"}}')  # spaces
        self.assertEqual(stable_json(a), stable_json(b))
        self.assertEqual(stable_json(b), '{"tools":["search"],"user":{"id":7,"tier":"pro"}}')  # byte for byte what TypeScript gives

    def test_a_cascade_from_keywords_to_a_big_model(self):
        golden = load_golden()
        label = {c["ticket"]: c["label"] for c in golden}
        big = Tier("big", Decimal("0.002"), label.__getitem__, lambda a: True)  # a stand-in that is always right
        cheap = Tier("keywords", Decimal(0), keywords, lambda a: a != "other")
        results = [(c, *cascade(c["ticket"], [cheap, big])) for c in golden]
        self.assertEqual([c["id"] for c, _, by, _ in results if by == "big"], ["t04", "t10", "t12", "t14", "t17", "t19"])
        self.assertEqual([c["id"] for c, answer, _, _ in results if answer != c["label"]], ["t15", "t20"])
        self.assertEqual(sum(spent for *_, spent in results), Decimal("0.012"))

    def test_p95_and_why_libraries_disagree(self):
        ms = [1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000]
        self.assertEqual((percentile(ms, 50), percentile(ms, 95), statistics.mean(ms)), (1000, 9000, 1819))
        # Same data, other definitions of "p95". Say which one a dashboard uses.
        self.assertEqual(statistics.quantiles(ms, n=20)[-1], 12510)  # the default extrapolates past the slowest call
        self.assertAlmostEqual(statistics.quantiles(ms, n=20, method="inclusive")[-1], 5490)  # numpy's default too
        self.assertEqual(statistics.median(ms), 1010)  # the median interpolates between 1000 and 1020

    async def test_time_to_first_token_is_measured_apart(self):
        clock = {"t": 0}

        async def stream():
            clock["t"] += 800
            yield "Your"
            for word in [" refund", " is", " on", " its", " way."]:
                clock["t"] += 100
                yield word

        self.assertEqual(await time_stream(stream(), lambda: clock["t"]), ("Your refund is on its way.", 800, 1300))


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/14-cost-caching-and-latency/labs/python). `python3 labs/run.py cost-caching-and-latency/python` from the vault root.

## 5. Go

Go counts money in a `Picodollars` type, an `int64` with its own `String` method, so a cost can't be added to a token count by mistake and prints as dollars. Integer division also gives the break-even floor directly. `encoding/json` already sorts map keys, but it escapes `<`, `>` and `&` as `\u003c` and so on by default, a choice made so JSON could be pasted into HTML safely. Prompts often contain `<ticket>`-style tags, so `StableJSON` turns that off with `SetEscapeHTML(false)`. The stream is a channel, and the test runs inside `testing/synctest`, so the 800 ms "wait for the first token" takes no real time.

```go
// Package cost: pricing in exact integer money, prefix diagnosis, canonical JSON, a cascade and
// latency percentiles. The same numbers as the TypeScript lab.
package cost

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math"
	"slices"
	"strings"
	"time"
)

// Picodollars are millionths of a millionth of a dollar. A token count times a price in
// micro-dollars per million tokens is a whole number of them, so sums are exact.
type Picodollars int64

func (p Picodollars) String() string { // dollars, without trailing zeros
	whole, frac := p/1e12, p%1e12
	return strings.TrimRight(strings.TrimRight(fmt.Sprintf("%d.%012d", whole, frac), "0"), ".")
}

// Price is in micro-dollars per million tokens: $2.50 is 2_500_000.
type Price struct{ Input, Output, CacheWrite, CacheRead int64 }

// Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them.
var Prices = map[string]Price{
	"claude-haiku-4-5":  {1_000_000, 5_000_000, 1_250_000, 100_000},
	"claude-sonnet-5-5": {2_000_000, 10_000_000, 2_500_000, 200_000},
	"claude-opus-5-5":   {4_000_000, 20_000_000, 5_000_000, 200_000},
	"local":             {},
}

// Usage: Input counts only input that was neither written to nor read from the cache.
type Usage struct{ Input, Output, CacheWrite, CacheRead int64 }

func Cost(u Usage, p Price) Picodollars {
	return Picodollars(u.Input*p.Input + u.Output*p.Output + u.CacheWrite*p.CacheWrite + u.CacheRead*p.CacheRead)
}

// BreakEvenCalls: caching n calls costs write + (n − 1) × read; not caching costs n × input.
func BreakEvenCalls(p Price) int64 {
	return (p.CacheWrite-p.CacheRead)/(p.Input-p.CacheRead) + 1 // integer division is the floor here
}

func SharedPrefix(a, b string) int {
	i := 0
	for i < len(a) && i < len(b) && a[i] == b[i] {
		i++
	}
	return i
}

// StableJSON: encoding/json already sorts map keys (struct fields keep their declared order).
// What it adds is HTML escaping: by default "<ticket>" becomes "\u003cticket\u003e", which Python and
// JavaScript don't do. Turn that off, and drop the newline Encode adds.
func StableJSON(value any) (string, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(value); err != nil {
		return "", err
	}
	return strings.TrimSuffix(buf.String(), "\n"), nil
}

type Tier struct {
	Name   string
	Cost   Picodollars // per call
	Answer func(input string) (string, error)
	Accept func(answer string) bool // the last tier's answer is used whatever this says
}

func Cascade(input string, tiers []Tier) (answer, by string, spent Picodollars, err error) {
	for i, t := range tiers {
		if answer, err = t.Answer(input); err != nil {
			return "", t.Name, spent, err
		}
		spent += t.Cost // a rejected answer was still paid for
		if i == len(tiers)-1 || t.Accept(answer) {
			return answer, t.Name, spent, nil
		}
	}
	return "", "", 0, fmt.Errorf("a cascade needs at least one tier")
}

// Percentile by nearest rank: the smallest value that at least p% of the values are less than or equal to.
func Percentile(values []time.Duration, p float64) time.Duration {
	sorted := slices.Sorted(slices.Values(values))
	return sorted[max(0, int(math.Ceil(p/100*float64(len(sorted))))-1)]
}

// TimeStream reads chunks until the channel closes, timing the first one separately.
func TimeStream(chunks <-chan string) (text string, ttft, total time.Duration) {
	started := time.Now()
	var b strings.Builder
	for chunk := range chunks {
		if b.Len() == 0 {
			ttft = time.Since(started)
		}
		b.WriteString(chunk)
	}
	return b.String(), ttft, time.Since(started)
}
```

```go
package cost

import (
	"encoding/json"
	"slices"
	"strings"
	"testing"
	"testing/synctest"
	"time"

	"evals" // the shared golden set and the keyword rules
)

var sonnet = Prices["claude-sonnet-5-5"]

func TestOutputCostsFiveTimesInput(t *testing.T) {
	if got := Cost(Usage{Input: 2000, Output: 500}, sonnet).String(); got != "0.009" {
		t.Error(got)
	}
}

func TestCachingA6000TokenPrefixAcross1000Calls(t *testing.T) {
	uncached := 1000 * Cost(Usage{Input: 6150, Output: 100}, sonnet)
	cached := Cost(Usage{CacheWrite: 6000, Input: 150, Output: 100}, sonnet)
	for range 999 {
		cached += Cost(Usage{CacheRead: 6000, Input: 150, Output: 100}, sonnet)
	}
	if uncached.String() != "13.3" || cached.String() != "2.5138" { // exact, however many calls are added up
		t.Errorf("%s %s", uncached, cached)
	}
	if share := 1000 * Cost(Usage{Output: 100}, sonnet) * 100 / cached; share != 39 { // integer division: 39.78 → 39
		t.Error(share)
	}
}

func TestACacheWritePaysForItselfOnTheSecondCall(t *testing.T) {
	oneHour := sonnet
	oneHour.CacheWrite = 4_000_000 // 1-hour entries cost 2× to write
	if BreakEvenCalls(sonnet) != 2 || BreakEvenCalls(oneHour) != 3 {
		t.Error(BreakEvenCalls(sonnet), BreakEvenCalls(oneHour))
	}
}

func TestATimestampAtTheFrontLeavesNothingToCache(t *testing.T) {
	system := strings.Repeat("You classify support tickets. Label by what the team has to do next. ", 20)
	front := func(date string) string { return "Today is " + date + ".\n" + system + "\nhelp" }
	end := func(date string) string { return system + "\nToday is " + date + ".\nhelp" }
	a, b := "2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z"
	if SharedPrefix(front(a), front(b)) != 27 || SharedPrefix(end(a), end(b)) != len(system)+28 {
		t.Error(SharedPrefix(front(a), front(b)), SharedPrefix(end(a), end(b)))
	}
}

func TestJSONBytes(t *testing.T) {
	b := map[string]any{"user": map[string]any{"id": 7, "tier": "pro"}, "tools": []string{"search"}}
	if got, _ := StableJSON(b); got != `{"tools":["search"],"user":{"id":7,"tier":"pro"}}` { // maps come out sorted
		t.Error(got)
	}
	escaped, _ := json.Marshal("<ticket>")
	plain, _ := StableJSON("<ticket>")
	if string(escaped) != `"\u003cticket\u003e"` || plain != `"<ticket>"` {
		t.Error(string(escaped), plain)
	}
}

func TestACascadeFromKeywordsToABigModel(t *testing.T) {
	golden, err := evals.LoadGolden("../../../12-evals/labs/shared/golden.jsonl")
	if err != nil {
		t.Fatal(err)
	}
	label := map[string]string{}
	for _, c := range golden {
		label[c.Ticket] = c.Label
	}
	big := Tier{"big", 2_000_000_000, func(t string) (string, error) { return label[t], nil }, func(string) bool { return true }} // $0.002, always right
	cheap := Tier{"keywords", 0, evals.Keywords, func(a string) bool { return a != "other" }}
	var escalated, wrong []string
	var total Picodollars
	for _, c := range golden {
		answer, by, spent, _ := Cascade(c.Ticket, []Tier{cheap, big})
		if by == "big" {
			escalated = append(escalated, c.ID)
		}
		if answer != c.Label {
			wrong = append(wrong, c.ID)
		}
		total += spent
	}
	if !slices.Equal(escalated, []string{"t04", "t10", "t12", "t14", "t17", "t19"}) || !slices.Equal(wrong, []string{"t15", "t20"}) || total.String() != "0.012" {
		t.Error(escalated, wrong, total)
	}
}

func TestP95ShowsTheSlowCallTheMedianHides(t *testing.T) {
	var ms []time.Duration
	for _, v := range []int{1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000} {
		ms = append(ms, time.Duration(v)*time.Millisecond)
	}
	if Percentile(ms, 50) != time.Second || Percentile(ms, 95) != 9*time.Second {
		t.Error(Percentile(ms, 50), Percentile(ms, 95))
	}
}

func TestTimeToFirstTokenIsMeasuredApart(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		chunks := make(chan string)
		go func() {
			defer close(chunks)
			time.Sleep(800 * time.Millisecond) // the model reads the prompt first
			chunks <- "Your"
			for _, w := range []string{" refund", " is", " on", " its", " way."} {
				time.Sleep(100 * time.Millisecond)
				chunks <- w
			}
		}()
		text, ttft, total := TimeStream(chunks)
		if text != "Your refund is on its way." || ttft != 800*time.Millisecond || total != 1300*time.Millisecond {
			t.Error(text, ttft, total)
		}
	})
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/14-cost-caching-and-latency/labs/go). `python3 labs/run.py cost-caching-and-latency/go`.

## 6. Java

Java uses `BigDecimal`, with `movePointLeft(6)` for "per million", which shifts the decimal point exactly instead of dividing. The check shows why money is compared with `compareTo`: the summed total and `new BigDecimal("2.5138")` have the same value and different scales, so `equals` says they differ. Jackson writes a `HashMap` in its own internal order and a `LinkedHashMap` in insertion order; two settings on the mapper sort both. The stream is a plain `Iterator`, the shape `HttpClient`'s `BodyHandlers.ofLines()` gives you.

```java
package cost;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.MapperFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.json.JsonMapper;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.function.LongSupplier;
import java.util.function.Predicate;
import java.util.function.UnaryOperator;

/** Pricing with exact BigDecimal money, prefix diagnosis, canonical JSON, a cascade and latency percentiles. */
public final class Cost {
    private Cost() {}

    /** US dollars per million tokens. */
    public record Price(BigDecimal input, BigDecimal output, BigDecimal cacheWrite, BigDecimal cacheRead) {
        static Price of(String input, String output, String cacheWrite, String cacheRead) {
            return new Price(new BigDecimal(input), new BigDecimal(output), new BigDecimal(cacheWrite), new BigDecimal(cacheRead));
        }

        public Price withCacheWrite(String value) { return new Price(input, output, new BigDecimal(value), cacheRead); }
    }

    /** Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them. */
    public static final Map<String, Price> PRICES = Map.of(
            "claude-haiku-4-5", Price.of("1", "5", "1.25", "0.1"),
            "claude-sonnet-5-5", Price.of("2", "10", "2.5", "0.2"),
            "claude-opus-5-5", Price.of("4", "20", "5", "0.2"),
            "local", Price.of("0", "0", "0", "0"));

    /** {@code input} counts only input that was neither written to nor read from the cache. */
    public record Usage(long input, long output, long cacheWrite, long cacheRead) {}

    public static BigDecimal cost(Usage u, Price p) {
        return p.input().multiply(BigDecimal.valueOf(u.input()))
                .add(p.output().multiply(BigDecimal.valueOf(u.output())))
                .add(p.cacheWrite().multiply(BigDecimal.valueOf(u.cacheWrite())))
                .add(p.cacheRead().multiply(BigDecimal.valueOf(u.cacheRead())))
                .movePointLeft(6); // per million tokens; exact, unlike dividing a double
    }

    /** Caching n calls costs write + (n − 1) × read; not caching costs n × input. */
    public static int breakEvenCalls(Price p) {
        return p.cacheWrite().subtract(p.cacheRead()).divide(p.input().subtract(p.cacheRead()), 0, RoundingMode.FLOOR).intValueExact() + 1;
    }

    public static int sharedPrefix(String a, String b) {
        int i = 0;
        while (i < a.length() && i < b.length() && a.charAt(i) == b.charAt(i)) i++;
        return i;
    }

    /** Jackson writes map entries in the map's own order (a HashMap's is arbitrary) and record or class
     *  properties in declaration order. These two settings sort both. */
    private static final ObjectMapper STABLE = JsonMapper.builder()
            .enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS)
            .enable(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY)
            .build();

    public static String stableJson(Object value) throws JsonProcessingException {
        return STABLE.writeValueAsString(value);
    }

    public record Tier(String name, BigDecimal cost, UnaryOperator<String> answer, Predicate<String> accept) {}

    public record Answer(String answer, String by, BigDecimal spent) {}

    public static Answer cascade(String input, List<Tier> tiers) {
        BigDecimal spent = BigDecimal.ZERO;
        for (int i = 0; i < tiers.size(); i++) {
            Tier tier = tiers.get(i);
            String answer = tier.answer().apply(input);
            spent = spent.add(tier.cost()); // a rejected answer was still paid for
            if (i == tiers.size() - 1 || tier.accept().test(answer)) return new Answer(answer, tier.name(), spent);
        }
        throw new IllegalArgumentException("a cascade needs at least one tier");
    }

    /** Nearest rank: the smallest value that at least p% of the values are less than or equal to. */
    public static long percentile(List<Long> values, double p) {
        List<Long> sorted = values.stream().sorted().toList();
        return sorted.get(Math.max(0, (int) Math.ceil(p / 100 * sorted.size()) - 1));
    }

    public record Timed(String text, long ttftMs, long totalMs) {}

    /** Reads a blocking stream of chunks (HttpClient's BodyHandlers.ofLines gives one), timing the first. */
    public static Timed timeStream(Iterator<String> chunks, LongSupplier nowMs) {
        long started = nowMs.getAsLong(), ttft = -1;
        var text = new StringBuilder();
        while (chunks.hasNext()) {
            String chunk = chunks.next();
            if (ttft < 0) ttft = nowMs.getAsLong() - started;
            text.append(chunk);
        }
        long total = nowMs.getAsLong() - started;
        return new Timed(text.toString(), ttft < 0 ? total : ttft, total);
    }
}
```

```java
package cost;

import com.fasterxml.jackson.databind.ObjectMapper;
import cost.Cost.*;
import evals.Evals;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/** Checks, run with `java -ea`. The same numbers as every other language. */
public final class CostCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    /** BigDecimal.equals also compares scale: 2.5138 and 2.51380 are "not equal". compareTo compares value. */
    static boolean same(BigDecimal a, String b) {
        return a.compareTo(new BigDecimal(b)) == 0;
    }

    public static void main(String[] args) throws Exception {
        Price sonnet = Cost.PRICES.get("claude-sonnet-5-5");
        check(same(Cost.cost(new Usage(2000, 500, 0, 0), sonnet), "0.009"), "output costs five times input");

        BigDecimal uncached = Cost.cost(new Usage(6150, 100, 0, 0), sonnet).multiply(BigDecimal.valueOf(1000));
        BigDecimal cached = Cost.cost(new Usage(150, 100, 6000, 0), sonnet);
        for (int i = 0; i < 999; i++) cached = cached.add(Cost.cost(new Usage(150, 100, 0, 6000), sonnet));
        check(same(uncached, "13.30") && same(cached, "2.5138"), uncached + " " + cached);
        check(!cached.equals(new BigDecimal("2.5138")), "equals compares scale too: " + cached); // 2.51380000...
        check(Cost.breakEvenCalls(sonnet) == 2 && Cost.breakEvenCalls(sonnet.withCacheWrite("4")) == 3, "break-even");

        String system = "You classify support tickets. Label by what the team has to do next. ".repeat(20);
        String a = "2026-10-02T09:00:00Z", b = "2026-10-02T09:00:07Z";
        check(Cost.sharedPrefix("Today is " + a + ".\n" + system, "Today is " + b + ".\n" + system) == 27, "front");
        check(Cost.sharedPrefix(system + "\nToday is " + a, system + "\nToday is " + b) == system.length() + 28, "end");

        var user = new LinkedHashMap<String, Object>();
        user.put("tier", "pro");
        user.put("id", 7);
        var inserted = new LinkedHashMap<String, Object>();
        inserted.put("user", user);
        inserted.put("tools", List.of("search"));
        String plain = new ObjectMapper().writeValueAsString(inserted);
        check(plain.equals("{\"user\":{\"tier\":\"pro\",\"id\":7},\"tools\":[\"search\"]}"), plain); // insertion order
        check(Cost.stableJson(inserted).equals("{\"tools\":[\"search\"],\"user\":{\"id\":7,\"tier\":\"pro\"}}"), Cost.stableJson(inserted));

        var golden = Evals.loadGolden(Path.of("..", "..", "..", "12-evals", "labs", "shared", "golden.jsonl"));
        Map<String, String> label = golden.stream().collect(Collectors.toMap(Evals.Case::ticket, Evals.Case::label));
        var big = new Tier("big", new BigDecimal("0.002"), label::get, x -> true); // a stand-in that is always right
        var cheap = new Tier("keywords", BigDecimal.ZERO, Evals::keywords, x -> !x.equals("other"));
        var escalated = new ArrayList<String>();
        var wrong = new ArrayList<String>();
        BigDecimal total = BigDecimal.ZERO;
        for (var c : golden) {
            Answer r = Cost.cascade(c.ticket(), List.of(cheap, big));
            if (r.by().equals("big")) escalated.add(c.id());
            if (!r.answer().equals(c.label())) wrong.add(c.id());
            total = total.add(r.spent());
        }
        check(escalated.equals(List.of("t04", "t10", "t12", "t14", "t17", "t19")) && wrong.equals(List.of("t15", "t20")) && same(total, "0.012"),
                escalated + " " + wrong + " " + total);

        List<Long> ms = List.of(1200L, 900L, 1100L, 1000L, 950L, 1050L, 980L, 1020L, 990L, 9000L);
        check(Cost.percentile(ms, 50) == 1000 && Cost.percentile(ms, 95) == 9000, "percentiles");

        long[] t = {0};
        Iterator<String> stream = new Iterator<>() {
            final List<String> words = List.of("Your", " refund", " is", " on", " its", " way.");
            int i;

            public boolean hasNext() { return i < words.size(); }

            public String next() {
                t[0] += i == 0 ? 800 : 100; // the model reads the prompt before the first token
                return words.get(i++);
            }
        };
        check(Cost.timeStream(stream, () -> t[0]).equals(new Timed("Your refund is on its way.", 800, 1300)), "time to first token");

        System.out.println("all cost checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/14-cost-caching-and-latency/labs/java). `check.sh` compiles the evals lab's `Evals.java` alongside it for the golden set and keyword rules, and fetches the Jackson jars on the first run. `python3 labs/run.py cost-caching-and-latency/java`.

## 7. Rust

Rust counts money in a `Picodollars` newtype that implements `Add`, `Mul<u64>`, `Sum` and `Display`, so costs add up with `+` and `.sum()` and can't be confused with token counts. `serde_json::Value` stores objects in a sorted map unless the crate's `preserve_order` feature is turned on, so `to_string` is already canonical. A standard `HashMap` is the danger: its iteration order is randomised for each map, to resist hash-flooding attacks, so serialising one directly into a prompt gives different bytes on every run. The test converts through `Value` to show the safe route. The stream is a tokio channel, timed on tokio's paused clock.

```rust
//! Pricing in exact integer money, prefix diagnosis, canonical JSON, a cascade and latency
//! percentiles. The same numbers as the TypeScript lab.
use std::fmt;
use std::iter::Sum;
use std::ops::{Add, Mul};
use std::time::Duration;
use tokio::sync::mpsc;
use tokio::time::Instant;

/// Millionths of a millionth of a dollar. A token count times a price in micro-dollars per million
/// tokens is a whole number of them, so sums are exact. A newtype keeps money from mixing with counts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Default)]
pub struct Picodollars(pub u64);

impl Add for Picodollars {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        Picodollars(self.0 + other.0)
    }
}

impl Mul<u64> for Picodollars {
    type Output = Self;
    fn mul(self, n: u64) -> Self {
        Picodollars(self.0 * n)
    }
}

impl Sum for Picodollars {
    fn sum<I: Iterator<Item = Self>>(iter: I) -> Self {
        iter.fold(Picodollars(0), Add::add)
    }
}

impl fmt::Display for Picodollars {
    /// Dollars, without trailing zeros: 2.5138.
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let text = format!(
            "{}.{:012}",
            self.0 / 1_000_000_000_000,
            self.0 % 1_000_000_000_000
        );
        f.write_str(text.trim_end_matches('0').trim_end_matches('.'))
    }
}

/// Micro-dollars per million tokens: $2.50 is 2_500_000.
#[derive(Debug, Clone, Copy)]
pub struct Price {
    pub input: u64,
    pub output: u64,
    pub cache_write: u64,
    pub cache_read: u64,
}

/// Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them.
pub const SONNET_5_5: Price = Price {
    input: 2_000_000,
    output: 10_000_000,
    cache_write: 2_500_000,
    cache_read: 200_000,
};
pub const HAIKU_4_5: Price = Price {
    input: 1_000_000,
    output: 5_000_000,
    cache_write: 1_250_000,
    cache_read: 100_000,
};
pub const OPUS_5_5: Price = Price {
    input: 4_000_000,
    output: 20_000_000,
    cache_write: 5_000_000,
    cache_read: 200_000,
};

/// `input` counts only input that was neither written to nor read from the cache.
#[derive(Debug, Clone, Copy, Default)]
pub struct Usage {
    pub input: u64,
    pub output: u64,
    pub cache_write: u64,
    pub cache_read: u64,
}

pub fn cost(u: Usage, p: Price) -> Picodollars {
    Picodollars(
        u.input * p.input
            + u.output * p.output
            + u.cache_write * p.cache_write
            + u.cache_read * p.cache_read,
    )
}

/// Caching n calls costs write + (n − 1) × read; not caching costs n × input.
pub fn break_even_calls(p: Price) -> u64 {
    (p.cache_write - p.cache_read) / (p.input - p.cache_read) + 1 // integer division is the floor here
}

/// Counted in bytes, which equals characters for ASCII text like this lesson's prompts.
pub fn shared_prefix(a: &str, b: &str) -> usize {
    a.bytes().zip(b.bytes()).take_while(|(x, y)| x == y).count()
}

/// serde_json's `Value` keeps object keys in a sorted map, so `to_string` is already canonical.
/// (Unless the `preserve_order` feature is on.) A std `HashMap` is different: its order changes
/// from one run of the program to the next, so never serialise one into a prompt.
pub fn stable_json(value: &serde_json::Value) -> String {
    value.to_string()
}

pub struct Tier<'a> {
    pub name: &'a str,
    pub cost: Picodollars, // per call
    pub answer: &'a dyn Fn(&str) -> String,
    pub accept: fn(&str) -> bool, // the last tier's answer is used whatever this says
}

pub fn cascade<'a>(input: &str, tiers: &[Tier<'a>]) -> (String, &'a str, Picodollars) {
    let mut spent = Picodollars(0);
    for (i, tier) in tiers.iter().enumerate() {
        let answer = (tier.answer)(input);
        spent = spent + tier.cost; // a rejected answer was still paid for
        if i == tiers.len() - 1 || (tier.accept)(&answer) {
            return (answer, tier.name, spent);
        }
    }
    panic!("a cascade needs at least one tier")
}

/// Nearest rank: the smallest value that at least p% of the values are less than or equal to.
pub fn percentile(values: &[Duration], p: f64) -> Duration {
    let mut sorted = values.to_vec();
    sorted.sort();
    sorted[((p / 100.0 * sorted.len() as f64).ceil() as usize).max(1) - 1]
}

/// Reads chunks until the sender is dropped, timing the first one separately.
pub async fn time_stream(mut chunks: mpsc::Receiver<String>) -> (String, Duration, Duration) {
    let started = Instant::now();
    let (mut text, mut ttft) = (String::new(), None);
    while let Some(chunk) = chunks.recv().await {
        ttft.get_or_insert_with(|| started.elapsed());
        text.push_str(&chunk);
    }
    let total = started.elapsed();
    (text, ttft.unwrap_or(total), total)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::collections::HashMap;

    #[test]
    fn output_costs_five_times_input() {
        assert_eq!(
            cost(
                Usage {
                    input: 2000,
                    output: 500,
                    ..Default::default()
                },
                SONNET_5_5
            )
            .to_string(),
            "0.009"
        );
        assert!(HAIKU_4_5.input < SONNET_5_5.input && SONNET_5_5.input < OPUS_5_5.input);
    }

    #[test]
    fn caching_a_6000_token_prefix_across_1000_calls() {
        let uncached = cost(
            Usage {
                input: 6150,
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        ) * 1000;
        let first = cost(
            Usage {
                cache_write: 6000,
                input: 150,
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        );
        let each = cost(
            Usage {
                cache_read: 6000,
                input: 150,
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        );
        let cached: Picodollars = std::iter::once(first)
            .chain(std::iter::repeat_n(each, 999))
            .sum();
        assert_eq!(
            (uncached.to_string(), cached.to_string()),
            ("13.3".into(), "2.5138".into())
        ); // exact
        let output = cost(
            Usage {
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        ) * 1000;
        assert_eq!((output.0 as f64 / cached.0 as f64 * 100.0).round(), 40.0);
    }

    #[test]
    fn a_cache_write_pays_for_itself_on_the_second_call() {
        let one_hour = Price {
            cache_write: 4_000_000,
            ..SONNET_5_5
        }; // 1-hour entries cost 2× to write
        assert_eq!(
            (break_even_calls(SONNET_5_5), break_even_calls(one_hour)),
            (2, 3)
        );
    }

    #[test]
    fn a_timestamp_at_the_front_leaves_nothing_to_cache() {
        let system =
            "You classify support tickets. Label by what the team has to do next. ".repeat(20);
        let front = |date: &str| format!("Today is {date}.\n{system}\nhelp");
        let end = |date: &str| format!("{system}\nToday is {date}.\nhelp");
        let (a, b) = ("2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z");
        assert_eq!(shared_prefix(&front(a), &front(b)), 27);
        assert_eq!(shared_prefix(&end(a), &end(b)), system.len() + 28);
    }

    #[test]
    fn json_objects_come_out_sorted() {
        let b = json!({"user": {"tier": "pro", "id": 7}, "tools": ["search"]});
        assert_eq!(
            stable_json(&b),
            r#"{"tools":["search"],"user":{"id":7,"tier":"pro"}}"#
        );
        // A HashMap's order isn't even stable between two maps holding the same keys, so only the
        // sorted Value is safe to put in a prompt.
        let map: HashMap<&str, i32> = [("b", 1), ("a", 2)].into();
        assert_eq!(
            stable_json(&serde_json::to_value(&map).unwrap()),
            r#"{"a":2,"b":1}"#
        );
    }

    #[test]
    fn a_cascade_from_keywords_to_a_big_model() {
        let golden = evals::load_golden("../../../12-evals/labs/shared/golden.jsonl");
        let label: HashMap<&str, &str> = golden
            .iter()
            .map(|c| (c.ticket.as_str(), c.label.as_str()))
            .collect();
        let lookup = |t: &str| label[t].to_string(); // a stand-in for a big model that is always right
        let tiers = [
            Tier {
                name: "keywords",
                cost: Picodollars(0),
                answer: &evals::keywords,
                accept: |a| a != "other",
            },
            Tier {
                name: "big",
                cost: Picodollars(2_000_000_000),
                answer: &lookup,
                accept: |_| true,
            },
        ];
        let results: Vec<_> = golden
            .iter()
            .map(|c| (c, cascade(&c.ticket, &tiers)))
            .collect();
        let escalated: Vec<_> = results
            .iter()
            .filter(|(_, (_, by, _))| *by == "big")
            .map(|(c, _)| c.id.as_str())
            .collect();
        let wrong: Vec<_> = results
            .iter()
            .filter(|(c, (a, _, _))| *a != c.label)
            .map(|(c, _)| c.id.as_str())
            .collect();
        let total: Picodollars = results.iter().map(|(_, (_, _, spent))| *spent).sum();
        assert_eq!(escalated, ["t04", "t10", "t12", "t14", "t17", "t19"]);
        assert_eq!(wrong, ["t15", "t20"]);
        assert_eq!(total.to_string(), "0.012");
    }

    #[test]
    fn p95_shows_the_slow_call_the_median_hides() {
        let ms: Vec<Duration> = [1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000]
            .map(Duration::from_millis)
            .to_vec();
        assert_eq!(
            (percentile(&ms, 50.0), percentile(&ms, 95.0)),
            (Duration::from_secs(1), Duration::from_secs(9))
        );
    }

    #[tokio::test(start_paused = true)]
    async fn time_to_first_token_is_measured_apart() {
        let (send, receive) = mpsc::channel(8);
        tokio::spawn(async move {
            tokio::time::sleep(Duration::from_millis(800)).await; // the model reads the prompt first
            for word in ["Your", " refund", " is", " on", " its", " way."] {
                if word != "Your" {
                    tokio::time::sleep(Duration::from_millis(100)).await;
                }
                send.send(word.to_string()).await.unwrap();
            }
        });
        let (text, ttft, total) = time_stream(receive).await;
        assert_eq!(
            (text.as_str(), ttft, total),
            (
                "Your refund is on its way.",
                Duration::from_millis(800),
                Duration::from_millis(1300)
            )
        );
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/14-cost-caching-and-latency/labs/rust). `python3 labs/run.py cost-caching-and-latency/rust`.

## 8. C#

C#'s `decimal` is part of the language, so money is exact with ordinary operators and literals such as `0.2m`, and `==` compares the value, unlike Java's `equals`. The check sums the same costs as `double` to show the drift. `System.Text.Json` has no option to sort keys, so `StableJson` serialises to a `JsonNode` tree and rebuilds every object with its properties sorted. It also escapes `<` as `\u003C` by default, with an upper-case hex digit unlike Go's; the relaxed encoder writes it as it is. The stream is an `IAsyncEnumerable<string>`, read with `await foreach`.

```csharp
// Pricing with exact decimal money, prefix diagnosis, canonical JSON, a cascade and latency percentiles.
// The same numbers as the TypeScript lab.
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Nodes;

/// <summary>US dollars per million tokens. decimal is base-10 and exact for prices like 0.2.</summary>
public sealed record Price(decimal Input, decimal Output, decimal CacheWrite, decimal CacheRead);

/// <summary>Input counts only input that was neither written to nor read from the cache.</summary>
public sealed record Usage(long Input = 0, long Output = 0, long CacheWrite = 0, long CacheRead = 0);

public sealed record Tier(string Name, decimal Cost, Func<string, string> Answer, Func<string, bool> Accept);

public static class Costs
{
    /// <summary>Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them.</summary>
    public static readonly Dictionary<string, Price> Prices = new()
    {
        ["claude-haiku-4-5"] = new(1m, 5m, 1.25m, 0.1m),
        ["claude-sonnet-5-5"] = new(2m, 10m, 2.5m, 0.2m),
        ["claude-opus-5-5"] = new(4m, 20m, 5m, 0.2m),
        ["local"] = new(0m, 0m, 0m, 0m),
    };

    public static decimal Cost(Usage u, Price p) =>
        (u.Input * p.Input + u.Output * p.Output + u.CacheWrite * p.CacheWrite + u.CacheRead * p.CacheRead) / 1_000_000m;

    /// <summary>Caching n calls costs write + (n − 1) × read; not caching costs n × input.</summary>
    public static int BreakEvenCalls(Price p) => (int)Math.Floor((p.CacheWrite - p.CacheRead) / (p.Input - p.CacheRead)) + 1;

    public static int SharedPrefix(string a, string b)
    {
        var i = 0;
        while (i < a.Length && i < b.Length && a[i] == b[i]) i++;
        return i;
    }

    static readonly JsonSerializerOptions Relaxed = new() { Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping };

    /// <summary>System.Text.Json writes properties in declaration order and dictionary entries in the
    /// dictionary's order, and has no option to sort them, so sort the tree. It also escapes &lt; and &gt;
    /// by default; the relaxed encoder writes them as they are, as Python and JavaScript do.</summary>
    public static string StableJson<T>(T value) => Sorted(JsonSerializer.SerializeToNode(value))!.ToJsonString(Relaxed);

    static JsonNode? Sorted(JsonNode? node) => node switch
    {
        JsonObject o => new JsonObject(o.OrderBy(p => p.Key, StringComparer.Ordinal)
            .Select(p => KeyValuePair.Create(p.Key, Sorted(p.Value)))),
        JsonArray a => new JsonArray(a.Select(Sorted).ToArray()),
        _ => node?.DeepClone(),
    };

    public static (string Answer, string By, decimal Spent) Cascade(string input, IReadOnlyList<Tier> tiers)
    {
        var spent = 0m;
        for (var i = 0; i < tiers.Count; i++)
        {
            var answer = tiers[i].Answer(input);
            spent += tiers[i].Cost; // a rejected answer was still paid for
            if (i == tiers.Count - 1 || tiers[i].Accept(answer)) return (answer, tiers[i].Name, spent);
        }
        throw new ArgumentException("a cascade needs at least one tier");
    }

    /// <summary>Nearest rank: the smallest value that at least p% of the values are less than or equal to.</summary>
    public static double Percentile(IEnumerable<double> values, double p)
    {
        var sorted = values.Order().ToList();
        return sorted[Math.Max(0, (int)Math.Ceiling(p / 100 * sorted.Count) - 1)];
    }

    /// <summary>Reads an async stream to the end, timing the first chunk separately.</summary>
    public static async Task<(string Text, double TtftMs, double TotalMs)> TimeStream(IAsyncEnumerable<string> chunks, Func<double> nowMs)
    {
        var started = nowMs();
        double? ttft = null;
        var text = new System.Text.StringBuilder();
        await foreach (var chunk in chunks)
        {
            ttft ??= nowMs() - started;
            text.Append(chunk);
        }
        var total = nowMs() - started;
        return (text.ToString(), ttft ?? total, total);
    }
}
```

```csharp
// Checks: the same numbers as every other language.
using System.Text.Json;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var sonnet = Costs.Prices["claude-sonnet-5-5"];
Check(Costs.Cost(new(Input: 2000, Output: 500), sonnet) == 0.009m, "output costs five times input");

var uncached = 1000 * Costs.Cost(new(Input: 6150, Output: 100), sonnet);
var cached = Costs.Cost(new(CacheWrite: 6000, Input: 150, Output: 100), sonnet);
for (var i = 0; i < 999; i++) cached += Costs.Cost(new(CacheRead: 6000, Input: 150, Output: 100), sonnet);
Check(uncached == 13.30m && cached == 2.5138m, (uncached, cached)); // exact; decimal == compares value, not scale
var asDouble = (double)Costs.Cost(new(CacheWrite: 6000, Input: 150, Output: 100), sonnet);
for (var i = 0; i < 999; i++) asDouble += (double)Costs.Cost(new(CacheRead: 6000, Input: 150, Output: 100), sonnet);
Check(asDouble != 2.5138 && Math.Abs(asDouble - 2.5138) < 1e-9, asDouble); // the same sum in double drifts
Check(Costs.BreakEvenCalls(sonnet) == 2 && Costs.BreakEvenCalls(sonnet with { CacheWrite = 4m }) == 3, "break-even");

var system = string.Concat(Enumerable.Repeat("You classify support tickets. Label by what the team has to do next. ", 20));
string Front(string date) => $"Today is {date}.\n{system}\nhelp";
string End(string date) => $"{system}\nToday is {date}.\nhelp";
var (a, b) = ("2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z");
Check(Costs.SharedPrefix(Front(a), Front(b)) == 27 && Costs.SharedPrefix(End(a), End(b)) == system.Length + 28, "prefix");

var inserted = new Dictionary<string, object> { ["user"] = new Dictionary<string, object> { ["tier"] = "pro", ["id"] = 7 }, ["tools"] = new[] { "search" } };
Check(JsonSerializer.Serialize(inserted) == """{"user":{"tier":"pro","id":7},"tools":["search"]}""", JsonSerializer.Serialize(inserted)); // insertion order
Check(Costs.StableJson(inserted) == """{"tools":["search"],"user":{"id":7,"tier":"pro"}}""", Costs.StableJson(inserted));
Check(JsonSerializer.Serialize("<ticket>") == "\"\\u003Cticket\\u003E\"" && Costs.StableJson("<ticket>") == "\"<ticket>\"", JsonSerializer.Serialize("<ticket>"));

var golden = Evals.LoadGolden(Path.Combine(args.Length > 0 ? args[0] : "../../../12-evals/labs/shared", "golden.jsonl"));
var label = golden.ToDictionary(c => c.Ticket, c => c.Label);
Tier[] tiers = [new("keywords", 0m, Evals.Keywords, x => x != "other"), new("big", 0.002m, t => label[t], _ => true)]; // big: a stand-in that is always right
var results = golden.Select(c => (Case: c, Result: Costs.Cascade(c.Ticket, tiers))).ToList();
Check(results.Where(r => r.Result.By == "big").Select(r => r.Case.Id).SequenceEqual(["t04", "t10", "t12", "t14", "t17", "t19"]), "escalated");
Check(results.Where(r => r.Result.Answer != r.Case.Label).Select(r => r.Case.Id).SequenceEqual(["t15", "t20"]), "wrong");
Check(results.Sum(r => r.Result.Spent) == 0.012m, results.Sum(r => r.Result.Spent));

double[] ms = [1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000];
Check(Costs.Percentile(ms, 50) == 1000 && Costs.Percentile(ms, 95) == 9000 && ms.Average() == 1819, "percentiles");

var t = 0.0;
async IAsyncEnumerable<string> Stream()
{
    t += 800; // the model reads the prompt before the first token
    yield return "Your";
    foreach (var word in new[] { " refund", " is", " on", " its", " way." })
    {
        t += 100;
        yield return word;
    }
    await Task.CompletedTask;
}
Check(await Costs.TimeStream(Stream(), () => t) == ("Your refund is on its way.", 800, 1300), "time to first token");

Console.WriteLine("all cost checks passed");
```

The project links the evals lab's `Evals.cs`, and `container.sh` runs it in the .NET SDK container with a copy of both labs and the golden set.

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/14-cost-caching-and-latency/labs/csharp). `python3 labs/run.py cost-caching-and-latency/csharp` (needs Podman).

## Common pitfalls

1. **Summing costs in floating point.** The total drifts from the exact value, and stops matching the invoice. Use a decimal type or integer minor units.
2. **Building a decimal from a float.** `Decimal(0.2)` in Python and `new BigDecimal(0.2)` in Java copy the float's error exactly. Build them from strings.
3. **Comparing `BigDecimal`s with `equals`.** It compares scale too. Use `compareTo`.
4. **Serialising a hash map into a prompt.** Its order is arbitrary in Java and random per run in Rust, and the cache never hits. Sort the keys.
5. **Assuming JSON is JSON.** Spaces in Python, HTML escaping in Go and C#: two services that "send the same prompt" may send different bytes. Compare the bytes.
6. **Comparing p95s from different tools.** With small samples, nearest-rank and interpolated percentiles differ by thousands of milliseconds. Check the definition before comparing.

## Check your understanding

1. Why does summing 1,000 per-call costs as floats give $2.513799999999958 instead of $2.5138?
2. Why can Go and Rust count money in integers here without losing anything?
3. A Python service and a Go service send a prompt containing the same JSON settings object. Name two reasons their prompts might not share a cache entry.
4. A Rust service puts a `HashMap` of feature flags into its system prompt. What happens to its cache hit rate after each restart, and why?
5. Your logs say p95 is 9 s; a monitoring tool says 5.5 s, for the same ten requests. Is one of them wrong?
6. Why does C#'s `cached == 2.5138m` pass when Java's `cached.equals(new BigDecimal("2.5138"))` fails?

<details>
<summary>Answers — after your attempt</summary>

1. Each per-call cost such as 0.00245 is stored as the nearest binary fraction, which is very slightly off, and every addition rounds again. Over a thousand additions the tiny errors accumulate into a visible difference in the twelfth decimal place.
2. Token counts are whole numbers and prices are whole numbers of micro-dollars per million tokens, so their product is a whole number of picodollars. Integers add up exactly.
3. Python's `json.dumps` puts spaces after commas and colons by default, and keeps insertion order where Go sorts map keys. Go also escapes `<` and `>` if the settings contain them.
4. It drops to zero for that prefix and stays there: a Rust `HashMap` iterates in a different random order in each process, so the JSON differs after every restart, and the cache matches bytes. Every replica of the service differs from the others, too.
5. Probably neither. Nearest rank gives 9000 ms, an actual measurement; an interpolating method gives about 5490 ms, between the two slowest calls. Find out which definition the tool uses, and compare like with like.
6. C#'s `decimal` equality compares values, so 2.51380… and 2.5138 are equal. Java's `BigDecimal.equals` compares the value and the scale (the number of decimal places), so it says they differ. `compareTo` compares the value.

</details>

## Practice — independent task

**Make your flagship's cost log exact and its prompt bytes stable.**

1. In your flagship's language, change the cost calculation in your log line (from the main lesson's Build) to an exact type or integer minor units, and check that a day's total equals the sum of the per-call costs exactly.
2. Find every place your prompt includes serialised data. Run it twice with the same data built in different orders, and compare the bytes with the lab's `shared_prefix` or `divergence`.
3. Find out which percentile definition your logging or monitoring tool uses, and write it next to the p95 on your dashboard.

**Done when:** the day's total matches to the last digit, two prompts built from the same data in different orders are byte-for-byte identical, and your dashboard says which p95 it shows.

## Before moving on

You can keep money exact in your language, produce canonical JSON so prompts cache, and say which percentile definition your tools use.

**Recap.** Pricing code is the same in every language; three details are not. Floats drift when summed, so use a decimal type (Python `Decimal`, Java `BigDecimal`, C# `decimal`) or integer minor units (Go, Rust). JSON differs in key order, spaces and HTML escaping between languages, and a hash map can change order between runs, so sort and compact your JSON before it goes into a prompt. "p95" has several definitions that differ widely on small samples, so know which one each tool uses.

## Related
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|Cost, caching and latency]] — the main lesson
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/in-other-languages|Reliability and plumbing in other languages]] — the same week, and the same fake clocks
- [[ai-ml/03-ai-engineer/12-evals/in-other-languages|Evals in other languages]] — the golden set and keyword rules the cascades reuse
- [[ai-ml/03-ai-engineer/04-calling-models/in-other-languages|Calling models in other languages]] — each language's HTTP client, streaming and usage fields
