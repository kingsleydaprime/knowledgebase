# How LLMs Work in Other Languages

> **[Beginner]** · A companion to [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]], which builds softmax, temperature, top-k, top-p and seeded sampling in TypeScript. This page builds the same decoder in Python, Go, Java, Rust, C, C++ and C#, and every version produces **the same numbers and the same sampled tokens from the same seed**. It also names each ecosystem's tokenizer and local-inference tools.

## Before you start

You can already:

- Explain softmax, temperature, top-k, top-p and sampling → [[ai-ml/03-ai-engineer/02-how-llms-work/index|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Name your language's tokenizer library and its way of running a model locally.
2. Write the decoding step in your language, and make it reproducible with a seed.
3. Explain why the same seed gives the same tokens in every language, and what each language has to do about 32-bit overflow to get there.

## The kid version

Imagine seven friends in seven countries, each with the same rule book for a dice game and the same list of dice rolls written down in advance. They speak different languages, but if they all follow the rules exactly, they all end up with the same result. That's this page: one recipe for picking the next word, written in seven programming languages, and given the same "dice rolls" (the seed). Every one picks Paris, Paris, a, Paris…

**Where the analogy stops working.** Real dice don't care what language you speak. A computer's numbers do. Each language stores whole numbers a bit differently, and when they get too big some languages wrap around while others don't. To get identical rolls, each version has to say exactly how big its numbers are and what happens when they overflow.

## 1. The tools, by ecosystem

| Language | Tokenizer | Run a model locally | Talk to Ollama |
|---|---|---|---|
| TypeScript | `js-tiktoken`, `@huggingface/transformers` | `node-llama-cpp` | `ollama` (npm), or plain `fetch` |
| Python | **`tiktoken`** (OpenAI), **`tokenizers`** (Hugging Face) | `llama-cpp-python`, `transformers` | `ollama` (pip) |
| Go | `tiktoken-go` | Ollama itself is written in Go | **`github.com/ollama/ollama/api`** — Ollama's own client |
| Java | `jtokkit` | `jlama`, `java-llama.cpp` | LangChain4j, Spring AI |
| Rust | `tiktoken-rs`, `tokenizers` (the Hugging Face library is Rust underneath) | `candle`, `mistral.rs` | `ollama-rs` |
| C, C++ | built into llama.cpp | **llama.cpp** — the engine Ollama runs on | llama.cpp's own server |
| C# | `Microsoft.ML.Tokenizers` | LLamaSharp | `OllamaSharp`, `Microsoft.Extensions.AI` |

The sampling settings have the same names nearly everywhere — `temperature`, `top_p`, `top_k`, `seed`, `max_tokens` — because almost every client follows the OpenAI request format. The one you just ran through Ollama was sampled by C++ code in llama.cpp doing what this page's labs do.

## 2. What's the same, and what isn't

The algorithm doesn't change between languages: divide the scores by the temperature, subtract the maximum, take `exp`, normalise, then walk the cumulative probabilities until passing a random number. All seven languages use the same IEEE 754 doubles and correctly rounded `exp`, so `0.802`, `0.108`, `0.066` and `0.024` come out identically.

What differs is the **random number generator**. Each language's built-in seeded generator (`random.Random`, `math/rand/v2`, `java.util.Random`, `std::mt19937`, `System.Random`) produces a *different* sequence from the same seed, so the same seed gives different tokens in different languages. To show "same seed, same tokens", every lab here implements the same tiny generator, **mulberry32**, and asserts the same first three numbers: `0.6011037519201636`, `0.44829055899754167`, `0.8524657934904099`.

Mulberry32 relies on 32-bit unsigned arithmetic that **wraps around** on overflow. That's where the languages genuinely differ:

| Language | How 32-bit wrapping is written |
|---|---|
| TypeScript | numbers are doubles; `Math.imul` and `>>> 0` force 32-bit behaviour |
| Python | integers never overflow, so mask with `& 0xFFFFFFFF` after every step |
| Go | `uint32` wraps by definition |
| Java | `int` wraps by definition; it has no unsigned type, so use `>>>` for unsigned shifts and `Integer.toUnsignedLong` at the end |
| Rust | overflow panics in debug builds, so say `wrapping_add` and `wrapping_mul` |
| C, C++ | **unsigned** overflow wraps by definition; **signed overflow is undefined behaviour**, so `uint32_t` is required |
| C# | `uint` wraps, inside an `unchecked` block |

## Terms used in this lesson

1. **Seed**: This is the starting number for a random number generator. The same seed always produces the same sequence from the same generator.
2. **PRNG (pseudo-random number generator)**: The letters stand for those words. It is an algorithm that produces numbers that look random but are completely determined by the seed.
3. **Mulberry32**: This is a very small PRNG with 32 bits of state. It's used here because it's easy to write identically in every language.
4. **Wrapping overflow**: This is when a number that gets too big for its type starts again from zero, like a car's odometer rolling over.
5. **Undefined behaviour**: In C and C++, this is a program state the language rules don't define, such as signed integer overflow. The compiler is allowed to assume it never happens, so the result can be anything.
6. **IEEE 754**: IEEE stands for the Institute of Electrical and Electronics Engineers. IEEE 754 is its standard for floating-point numbers that all seven languages use for `double`. It's why the probabilities match to the last digit.
7. **Tokenizer**: This is the code that splits text into a model's tokens and back. Each model family has its own vocabulary, so the tokenizer must match the model.

## 3. Python

Python's integers never overflow, so the generator masks every result back to 32 bits. Everything else reads almost like the TypeScript.

```python
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
```

```python
import unittest

from decoding import greedy, sample, seeded_random, softmax, top_k, top_p

SCORES = [("Paris", 4.0), ("a", 2.0), ("the", 1.5), ("Lyon", 0.5)]


def rounded(dist):
    return {tok: round(p, 3) for tok, p in dist}


class DecodingTests(unittest.TestCase):
    def test_temperature_reshapes_the_same_scores(self):
        self.assertEqual(rounded(softmax(SCORES, 1)), {"Paris": 0.802, "a": 0.108, "the": 0.066, "Lyon": 0.024})
        self.assertEqual(rounded(softmax(SCORES, 0.5)), {"Paris": 0.975, "a": 0.018, "the": 0.007, "Lyon": 0.001})
        self.assertEqual(rounded(softmax(SCORES, 2)), {"Paris": 0.547, "a": 0.201, "the": 0.157, "Lyon": 0.095})

    def test_top_k_and_top_p(self):
        dist = softmax(SCORES, 1)
        self.assertEqual([t for t, _ in top_k(dist, 2)], ["Paris", "a"])
        self.assertEqual([t for t, _ in top_p(dist, 0.9)], ["Paris", "a"])
        self.assertEqual([t for t, _ in top_p(dist, 0.97)], ["Paris", "a", "the"])

    def test_same_seed_same_numbers_as_every_other_language(self):
        r = seeded_random(42)
        self.assertEqual([r(), r(), r()], [0.6011037519201636, 0.44829055899754167, 0.8524657934904099])

    def test_same_seed_same_tokens(self):
        dist, r = softmax(SCORES, 1), seeded_random(42)
        self.assertEqual(" ".join(sample(dist, r) for _ in range(10)), "Paris Paris a Paris Paris Paris Paris Paris a Paris")
        r = seeded_random(42)
        self.assertEqual(sum(sample(dist, r) == "Paris" for _ in range(1000)), 796)  # about 80.2%, as expected

    def test_greedy(self):
        self.assertEqual(greedy(softmax(SCORES, 2)), "Paris")


if __name__ == "__main__":
    unittest.main()
```

## 4. Go

Go's `uint32` wraps on its own, so the generator is the most direct translation. `cmp.Compare` with the arguments swapped gives a descending sort, and `slices.SortStableFunc` keeps equal probabilities in their original order.

```go
// Package decoding: from a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab.
package decoding

import (
	"cmp"
	"math"
	"slices"
)

// Entry is one token and its score or probability. Slices keep a fixed order, so sampling is reproducible.
type Entry struct {
	Token string
	P     float64
}

// SeededRandom is mulberry32. math/rand/v2 has seeded generators too; this one gives the same
// numbers in every language in this companion.
func SeededRandom(seed uint32) func() float64 {
	a := seed
	return func() float64 {
		a += 0x6d2b79f5 // uint32 arithmetic wraps, exactly like JavaScript's >>> 0
		t := a
		t = (t ^ (t >> 15)) * (t | 1)
		t ^= t + (t^(t>>7))*(t|61)
		return float64(t^(t>>14)) / 4294967296
	}
}

// Softmax divides by the temperature, then exponentiates and normalises.
func Softmax(scores []Entry, temperature float64) []Entry {
	top := math.Inf(-1)
	for _, e := range scores {
		top = max(top, e.P/temperature) // subtract the max so Exp can't overflow
	}
	out := make([]Entry, len(scores))
	total := 0.0
	for i, e := range scores {
		out[i] = Entry{e.Token, math.Exp(e.P/temperature - top)}
		total += out[i].P
	}
	for i := range out {
		out[i].P /= total
	}
	return out
}

func byProbability(dist []Entry) []Entry {
	sorted := slices.Clone(dist)
	slices.SortStableFunc(sorted, func(x, y Entry) int { return cmp.Compare(y.P, x.P) }) // descending
	return sorted
}

// TopK keeps the k most likely tokens.
func TopK(dist []Entry, k int) []Entry {
	return renormalise(byProbability(dist)[:min(k, len(dist))])
}

// TopP keeps the smallest set of most likely tokens whose probabilities reach p.
func TopP(dist []Entry, p float64) []Entry {
	sorted := byProbability(dist)
	cumulative := 0.0
	for i, e := range sorted {
		cumulative += e.P
		if cumulative >= p {
			return renormalise(sorted[:i+1])
		}
	}
	return renormalise(sorted)
}

func renormalise(entries []Entry) []Entry {
	total := 0.0
	for _, e := range entries {
		total += e.P
	}
	out := make([]Entry, len(entries))
	for i, e := range entries {
		out[i] = Entry{e.Token, e.P / total}
	}
	return out
}

// Sample walks the cumulative probabilities until passing a random number in [0, 1).
func Sample(dist []Entry, random func() float64) string {
	r := random()
	for _, e := range dist {
		if r -= e.P; r < 0 {
			return e.Token
		}
	}
	return dist[len(dist)-1].Token
}

// Greedy always picks the most likely token: temperature 0.
func Greedy(dist []Entry) string {
	return byProbability(dist)[0].Token
}
```

```go
package decoding

import (
	"math"
	"slices"
	"strings"
	"testing"
)

var scores = []Entry{{"Paris", 4.0}, {"a", 2.0}, {"the", 1.5}, {"Lyon", 0.5}}

func rounded(dist []Entry) []float64 {
	out := []float64{}
	for _, e := range dist {
		out = append(out, math.Round(e.P*1000)/1000)
	}
	return out
}

func tokens(dist []Entry) []string {
	out := []string{}
	for _, e := range dist {
		out = append(out, e.Token)
	}
	return out
}

func TestTemperatureReshapesTheSameScores(t *testing.T) {
	for _, c := range []struct {
		temperature float64
		want        []float64
	}{
		{1, []float64{0.802, 0.108, 0.066, 0.024}},
		{0.5, []float64{0.975, 0.018, 0.007, 0.001}},
		{2, []float64{0.547, 0.201, 0.157, 0.095}},
	} {
		if got := rounded(Softmax(scores, c.temperature)); !slices.Equal(got, c.want) {
			t.Errorf("T=%v: got %v, want %v", c.temperature, got, c.want)
		}
	}
}

func TestTopKAndTopP(t *testing.T) {
	dist := Softmax(scores, 1)
	for _, c := range []struct {
		got, want []string
	}{
		{tokens(TopK(dist, 2)), []string{"Paris", "a"}},
		{tokens(TopP(dist, 0.9)), []string{"Paris", "a"}},
		{tokens(TopP(dist, 0.97)), []string{"Paris", "a", "the"}},
	} {
		if !slices.Equal(c.got, c.want) {
			t.Errorf("got %v, want %v", c.got, c.want)
		}
	}
}

func TestSameSeedSameNumbersAsEveryOtherLanguage(t *testing.T) {
	r := SeededRandom(42)
	got := []float64{r(), r(), r()}
	if want := []float64{0.6011037519201636, 0.44829055899754167, 0.8524657934904099}; !slices.Equal(got, want) {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestSameSeedSameTokens(t *testing.T) {
	dist, r := Softmax(scores, 1), SeededRandom(42)
	picks := []string{}
	for range 10 {
		picks = append(picks, Sample(dist, r))
	}
	if got, want := strings.Join(picks, " "), "Paris Paris a Paris Paris Paris Paris Paris a Paris"; got != want {
		t.Errorf("got %q, want %q", got, want)
	}
	r, paris := SeededRandom(42), 0
	for range 1000 {
		if Sample(dist, r) == "Paris" {
			paris++
		}
	}
	if paris != 796 { // about 80.2%, as expected
		t.Errorf("Paris picked %d times, want 796", paris)
	}
}

func TestGreedy(t *testing.T) {
	if got := Greedy(Softmax(scores, 2)); got != "Paris" {
		t.Errorf("got %s", got)
	}
}
```

## 5. Java

Java has no unsigned integers. `int` still wraps, and `>>>` shifts without copying the sign bit, so the bits come out the same. `Integer.toUnsignedLong` reads the final value as unsigned before dividing. The lambda keeps its state in a one-element array because Java lambdas can't reassign captured local variables.

```java
package decoding;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.function.DoubleSupplier;

/** From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab. */
public final class Decoding {
    private Decoding() {}

    /** One token and its score or probability. Lists keep a fixed order, so sampling is reproducible. */
    public record Entry(String token, double p) {}

    /** mulberry32. java.util.Random(seed) also repeats; this one matches every language in this companion. */
    public static DoubleSupplier seededRandom(int seed) {
        int[] a = {seed};
        return () -> {
            a[0] += 0x6d2b79f5;                       // int arithmetic wraps at 32 bits
            int t = a[0];
            t = (t ^ (t >>> 15)) * (t | 1);           // >>> is the unsigned shift, as in JavaScript
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            return Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
        };
    }

    public static List<Entry> softmax(List<Entry> scores, double temperature) {
        double top = scores.stream().mapToDouble(e -> e.p() / temperature).max().orElseThrow();
        List<Entry> exps = scores.stream().map(e -> new Entry(e.token(), Math.exp(e.p() / temperature - top))).toList();
        return renormalise(exps);
    }

    private static List<Entry> byProbability(List<Entry> dist) {
        return dist.stream().sorted(Comparator.comparingDouble(Entry::p).reversed()).toList();
    }

    public static List<Entry> topK(List<Entry> dist, int k) {
        return renormalise(byProbability(dist).stream().limit(k).toList());
    }

    public static List<Entry> topP(List<Entry> dist, double p) {
        List<Entry> kept = new ArrayList<>();
        double cumulative = 0;
        for (Entry e : byProbability(dist)) {
            kept.add(e);
            cumulative += e.p();
            if (cumulative >= p) break;
        }
        return renormalise(kept);
    }

    private static List<Entry> renormalise(List<Entry> entries) {
        double total = entries.stream().mapToDouble(Entry::p).sum();
        return entries.stream().map(e -> new Entry(e.token(), e.p() / total)).toList();
    }

    public static String sample(List<Entry> dist, DoubleSupplier random) {
        double r = random.getAsDouble();
        for (Entry e : dist) {
            r -= e.p();
            if (r < 0) return e.token();
        }
        return dist.getLast().token();
    }

    public static String greedy(List<Entry> dist) {
        return byProbability(dist).getFirst().token();
    }

    // --- checks, run with `java -ea` ---

    static final List<Entry> SCORES = List.of(new Entry("Paris", 4.0), new Entry("a", 2.0), new Entry("the", 1.5), new Entry("Lyon", 0.5));

    static List<Double> rounded(List<Entry> dist) {
        return dist.stream().map(e -> Math.round(e.p() * 1000) / 1000.0).toList();
    }

    static List<String> tokens(List<Entry> dist) {
        return dist.stream().map(Entry::token).toList();
    }

    static void check(Object got, Object want) {
        if (!got.equals(want)) throw new AssertionError("got " + got + ", want " + want);
    }

    public static void main(String[] args) {
        check(rounded(softmax(SCORES, 1)), List.of(0.802, 0.108, 0.066, 0.024));
        check(rounded(softmax(SCORES, 0.5)), List.of(0.975, 0.018, 0.007, 0.001));
        check(rounded(softmax(SCORES, 2)), List.of(0.547, 0.201, 0.157, 0.095));

        List<Entry> dist = softmax(SCORES, 1);
        check(tokens(topK(dist, 2)), List.of("Paris", "a"));
        check(tokens(topP(dist, 0.9)), List.of("Paris", "a"));
        check(tokens(topP(dist, 0.97)), List.of("Paris", "a", "the"));

        DoubleSupplier r = seededRandom(42);
        check(List.of(r.getAsDouble(), r.getAsDouble(), r.getAsDouble()), List.of(0.6011037519201636, 0.44829055899754167, 0.8524657934904099));

        DoubleSupplier r2 = seededRandom(42);
        List<String> picks = new ArrayList<>();
        for (int i = 0; i < 10; i++) picks.add(sample(dist, r2));
        check(String.join(" ", picks), "Paris Paris a Paris Paris Paris Paris Paris a Paris");
        DoubleSupplier r3 = seededRandom(42);
        int paris = 0;
        for (int i = 0; i < 1000; i++) if (sample(dist, r3).equals("Paris")) paris++;
        check(paris, 796); // about 80.2%, as expected

        check(greedy(softmax(SCORES, 2)), "Paris");
        System.out.println("ok: decoding matches the TypeScript lab");
    }
}
```

## 6. Rust

Rust treats integer overflow as a bug: it panics in debug builds. Mulberry32 *wants* overflow, so it says so with `wrapping_add` and `wrapping_mul`. `f64::total_cmp` gives floats a total order so `sort_by` can use them.

```rust
//! From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab.

/// One token and its score or probability. A Vec keeps a fixed order, so sampling is reproducible.
pub type Dist = Vec<(&'static str, f64)>;

/// mulberry32. Rust's standard library has no seeded generator (the `rand` crate does);
/// this one gives the same numbers in every language in this companion.
pub fn seeded_random(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5); // wrapping_ makes the 32-bit overflow explicit
        let mut t = a;
        t = (t ^ (t >> 15)).wrapping_mul(t | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4294967296.0
    }
}

pub fn softmax(scores: &Dist, temperature: f64) -> Dist {
    let top = scores
        .iter()
        .map(|&(_, s)| s / temperature)
        .fold(f64::NEG_INFINITY, f64::max);
    let exps = scores
        .iter()
        .map(|&(tok, s)| (tok, (s / temperature - top).exp()))
        .collect();
    renormalise(exps)
}

fn by_probability(dist: &Dist) -> Dist {
    let mut sorted = dist.clone();
    sorted.sort_by(|x, y| y.1.total_cmp(&x.1)); // stable, descending
    sorted
}

pub fn top_k(dist: &Dist, k: usize) -> Dist {
    renormalise(by_probability(dist).into_iter().take(k).collect())
}

pub fn top_p(dist: &Dist, p: f64) -> Dist {
    let mut kept = Vec::new();
    let mut cumulative = 0.0;
    for entry in by_probability(dist) {
        kept.push(entry);
        cumulative += entry.1;
        if cumulative >= p {
            break;
        }
    }
    renormalise(kept)
}

fn renormalise(entries: Dist) -> Dist {
    let total: f64 = entries.iter().map(|&(_, p)| p).sum();
    entries
        .into_iter()
        .map(|(tok, p)| (tok, p / total))
        .collect()
}

pub fn sample(dist: &Dist, random: &mut impl FnMut() -> f64) -> &'static str {
    let mut r = random();
    for &(tok, p) in dist {
        r -= p;
        if r < 0.0 {
            return tok;
        }
    }
    dist.last()
        .expect("an empty distribution has nothing to sample")
        .0
}

pub fn greedy(dist: &Dist) -> &'static str {
    by_probability(dist)[0].0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scores() -> Dist {
        vec![("Paris", 4.0), ("a", 2.0), ("the", 1.5), ("Lyon", 0.5)]
    }

    fn rounded(dist: &Dist) -> Vec<f64> {
        dist.iter()
            .map(|&(_, p)| (p * 1000.0).round() / 1000.0)
            .collect()
    }

    fn tokens(dist: &Dist) -> Vec<&str> {
        dist.iter().map(|&(tok, _)| tok).collect()
    }

    #[test]
    fn temperature_reshapes_the_same_scores() {
        assert_eq!(
            rounded(&softmax(&scores(), 1.0)),
            [0.802, 0.108, 0.066, 0.024]
        );
        assert_eq!(
            rounded(&softmax(&scores(), 0.5)),
            [0.975, 0.018, 0.007, 0.001]
        );
        assert_eq!(
            rounded(&softmax(&scores(), 2.0)),
            [0.547, 0.201, 0.157, 0.095]
        );
    }

    #[test]
    fn top_k_and_top_p() {
        let dist = softmax(&scores(), 1.0);
        assert_eq!(tokens(&top_k(&dist, 2)), ["Paris", "a"]);
        assert_eq!(tokens(&top_p(&dist, 0.9)), ["Paris", "a"]);
        assert_eq!(tokens(&top_p(&dist, 0.97)), ["Paris", "a", "the"]);
    }

    #[test]
    fn same_seed_same_numbers_as_every_other_language() {
        let mut r = seeded_random(42);
        assert_eq!(
            [r(), r(), r()],
            [0.6011037519201636, 0.44829055899754167, 0.8524657934904099]
        );
    }

    #[test]
    fn same_seed_same_tokens() {
        let dist = softmax(&scores(), 1.0);
        let mut r = seeded_random(42);
        let picks: Vec<_> = (0..10).map(|_| sample(&dist, &mut r)).collect();
        assert_eq!(
            picks.join(" "),
            "Paris Paris a Paris Paris Paris Paris Paris a Paris"
        );
        let mut r = seeded_random(42);
        let paris = (0..1000)
            .filter(|_| sample(&dist, &mut r) == "Paris")
            .count();
        assert_eq!(paris, 796); // about 80.2%, as expected
    }

    #[test]
    fn greedy_picks_the_top_token() {
        assert_eq!(greedy(&softmax(&scores(), 2.0)), "Paris");
    }
}
```

## 7. C and C++

This is where real local inference happens: llama.cpp's sampler, which picked "Paris" in the main lesson, does this same job in C++. The C version sorts in place with `qsort`. Note `uint32_t`: with a signed `int`, the overflow mulberry32 depends on would be undefined behaviour.

```c
/* From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab. */
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char *token;
    double p; /* a score before softmax, a probability after */
} Entry;

/* mulberry32. uint32_t arithmetic wraps, exactly like JavaScript's >>> 0. */
typedef struct { uint32_t a; } Rng;

static double next_random(Rng *rng) {
    rng->a += 0x6d2b79f5u;
    uint32_t t = rng->a;
    t = (t ^ (t >> 15)) * (t | 1u);
    t ^= t + (t ^ (t >> 7)) * (t | 61u);
    return (double)(t ^ (t >> 14)) / 4294967296.0;
}

/* Softmax in place: n entries, scores in, probabilities out. */
static void softmax(Entry *e, size_t n, double temperature) {
    double top = -INFINITY, total = 0;
    for (size_t i = 0; i < n; i++) top = fmax(top, e[i].p / temperature);
    for (size_t i = 0; i < n; i++) total += e[i].p = exp(e[i].p / temperature - top);
    for (size_t i = 0; i < n; i++) e[i].p /= total;
}

static int by_probability_desc(const void *x, const void *y) {
    double px = ((const Entry *)x)->p, py = ((const Entry *)y)->p;
    return (px < py) - (px > py);
}

/* Top-p in place: sorts, keeps the smallest prefix reaching p, renormalises. Returns the new length.
   (qsort isn't stable; ties don't occur in this example.) */
static size_t top_p(Entry *e, size_t n, double p) {
    qsort(e, n, sizeof *e, by_probability_desc);
    size_t kept = 0;
    double cumulative = 0;
    while (kept < n && cumulative < p) cumulative += e[kept++].p;
    for (size_t i = 0; i < kept; i++) e[i].p /= cumulative;
    return kept;
}

static const char *sample(const Entry *e, size_t n, Rng *rng) {
    double r = next_random(rng);
    for (size_t i = 0; i < n; i++)
        if ((r -= e[i].p) < 0) return e[i].token;
    return e[n - 1].token;
}

/* --- checks --- */

static Entry scores[] = {{"Paris", 4.0}, {"a", 2.0}, {"the", 1.5}, {"Lyon", 0.5}};
#define N (sizeof scores / sizeof scores[0])

static void expect_rounded(double temperature, const double want[N]) {
    Entry e[N];
    memcpy(e, scores, sizeof scores);
    softmax(e, N, temperature);
    for (size_t i = 0; i < N; i++) assert(round(e[i].p * 1000) / 1000 == want[i]);
}

int main(void) {
    expect_rounded(1, (double[]){0.802, 0.108, 0.066, 0.024});
    expect_rounded(0.5, (double[]){0.975, 0.018, 0.007, 0.001});
    expect_rounded(2, (double[]){0.547, 0.201, 0.157, 0.095});

    Entry dist[N];
    memcpy(dist, scores, sizeof scores);
    softmax(dist, N, 1);

    Entry nucleus[N];
    memcpy(nucleus, dist, sizeof dist);
    size_t kept = top_p(nucleus, N, 0.9);
    assert(kept == 2 && strcmp(nucleus[0].token, "Paris") == 0 && strcmp(nucleus[1].token, "a") == 0);

    Rng rng = {42};
    assert(next_random(&rng) == 0.6011037519201636);
    assert(next_random(&rng) == 0.44829055899754167);
    assert(next_random(&rng) == 0.8524657934904099);

    char picks[128] = "";
    rng = (Rng){42};
    for (int i = 0; i < 10; i++) {
        if (i) strcat(picks, " ");
        strcat(picks, sample(dist, N, &rng));
    }
    assert(strcmp(picks, "Paris Paris a Paris Paris Paris Paris Paris a Paris") == 0);

    rng = (Rng){42};
    int paris = 0;
    for (int i = 0; i < 1000; i++) paris += strcmp(sample(dist, N, &rng), "Paris") == 0;
    assert(paris == 796); /* about 80.2%, as expected */

    puts("ok: decoding matches the TypeScript lab");
    return 0;
}
```

The C++ version uses `std::ranges` for the sort and the maximum, and then shows the standard library's own tools: a seeded `std::mt19937` engine and `std::discrete_distribution`. Those give a different sequence from the same seed, but the same share of Paris. It printed 805 out of 1000, against mulberry32's 796; both are close to the expected 802.

```cpp
// From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab,
// plus the standard library's own way to sample: <random>'s discrete_distribution.
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <ranges>
#include <string>
#include <vector>

struct Entry {
    std::string token;
    double p;  // a score before softmax, a probability after
};
using Dist = std::vector<Entry>;

// mulberry32, as a callable object. std::uint32_t arithmetic wraps like JavaScript's >>> 0.
class Mulberry32 {
public:
    explicit Mulberry32(std::uint32_t seed) : a_(seed) {}
    double operator()() {
        a_ += 0x6d2b79f5u;
        std::uint32_t t = a_;
        t = (t ^ (t >> 15)) * (t | 1u);
        t ^= t + (t ^ (t >> 7)) * (t | 61u);
        return static_cast<double>(t ^ (t >> 14)) / 4294967296.0;
    }

private:
    std::uint32_t a_;
};

Dist renormalise(Dist entries) {
    double total = 0;
    for (const auto& e : entries) total += e.p;
    for (auto& e : entries) e.p /= total;
    return entries;
}

Dist softmax(Dist scores, double temperature) {
    double top = std::ranges::max(scores | std::views::transform([&](const Entry& e) { return e.p / temperature; }));
    for (auto& e : scores) e.p = std::exp(e.p / temperature - top);
    return renormalise(std::move(scores));
}

Dist by_probability(Dist dist) {
    std::ranges::stable_sort(dist, std::greater{}, &Entry::p);
    return dist;
}

Dist top_k(const Dist& dist, std::size_t k) {
    Dist sorted = by_probability(dist);
    sorted.resize(std::min(k, sorted.size()));
    return renormalise(std::move(sorted));
}

Dist top_p(const Dist& dist, double p) {
    Dist kept;
    double cumulative = 0;
    for (const auto& e : by_probability(dist)) {
        kept.push_back(e);
        if ((cumulative += e.p) >= p) break;
    }
    return renormalise(std::move(kept));
}

template <typename Random>
std::string sample(const Dist& dist, Random& random) {
    double r = random();
    for (const auto& e : dist)
        if ((r -= e.p) < 0) return e.token;
    return dist.back().token;
}

std::vector<std::string> tokens(const Dist& dist) {
    std::vector<std::string> out;
    for (const auto& e : dist) out.push_back(e.token);
    return out;
}

int main() {
    const Dist scores{{"Paris", 4.0}, {"a", 2.0}, {"the", 1.5}, {"Lyon", 0.5}};
    auto rounded = [](const Dist& d) {
        std::vector<double> out;
        for (const auto& e : d) out.push_back(std::round(e.p * 1000) / 1000);
        return out;
    };
    assert((rounded(softmax(scores, 1)) == std::vector{0.802, 0.108, 0.066, 0.024}));
    assert((rounded(softmax(scores, 0.5)) == std::vector{0.975, 0.018, 0.007, 0.001}));
    assert((rounded(softmax(scores, 2)) == std::vector{0.547, 0.201, 0.157, 0.095}));

    const Dist dist = softmax(scores, 1);
    assert((tokens(top_k(dist, 2)) == std::vector<std::string>{"Paris", "a"}));
    assert((tokens(top_p(dist, 0.9)) == std::vector<std::string>{"Paris", "a"}));
    assert((tokens(top_p(dist, 0.97)) == std::vector<std::string>{"Paris", "a", "the"}));

    Mulberry32 r(42);
    assert(r() == 0.6011037519201636 && r() == 0.44829055899754167 && r() == 0.8524657934904099);

    Mulberry32 r2(42);
    std::string picks;
    for (int i = 0; i < 10; i++) picks += (i ? " " : "") + sample(dist, r2);
    assert(picks == "Paris Paris a Paris Paris Paris Paris Paris a Paris");
    Mulberry32 r3(42);
    int paris = 0;
    for (int i = 0; i < 1000; i++) paris += sample(dist, r3) == "Paris";
    assert(paris == 796);  // about 80.2%, as expected

    // The standard library's version: a seeded engine and a distribution over indices.
    // Same idea, different generator, so different picks, but the same share.
    std::mt19937 engine(42);
    std::discrete_distribution<std::size_t> pick({dist[0].p, dist[1].p, dist[2].p, dist[3].p});
    int std_paris = 0;
    for (int i = 0; i < 1000; i++) std_paris += pick(engine) == 0;
    assert(std_paris > 760 && std_paris < 845);

    std::cout << "ok: decoding matches the TypeScript lab; std::discrete_distribution picked Paris " << std_paris
              << " times in 1000\n";
}
```

## 8. C#

`uint` arithmetic inside `unchecked` wraps. `OrderByDescending` is a stable sort, and records with `with` make the renormalising steps read as copies rather than mutations.

```csharp
// From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab.

var scores = new List<Entry> { new("Paris", 4.0), new("a", 2.0), new("the", 1.5), new("Lyon", 0.5) };
static List<double> Rounded(List<Entry> d) => d.Select(e => Math.Round(e.P, 3, MidpointRounding.AwayFromZero)).ToList();
static List<string> Tokens(List<Entry> d) => d.Select(e => e.Token).ToList();

Check(Rounded(Decoder.Softmax(scores, 1)), [0.802, 0.108, 0.066, 0.024]);
Check(Rounded(Decoder.Softmax(scores, 0.5)), [0.975, 0.018, 0.007, 0.001]);
Check(Rounded(Decoder.Softmax(scores, 2)), [0.547, 0.201, 0.157, 0.095]);

var dist = Decoder.Softmax(scores, 1);
Check(Tokens(Decoder.TopK(dist, 2)), ["Paris", "a"]);
Check(Tokens(Decoder.TopP(dist, 0.9)), ["Paris", "a"]);
Check(Tokens(Decoder.TopP(dist, 0.97)), ["Paris", "a", "the"]);

var r = Decoder.SeededRandom(42);
Check([r(), r(), r()], [0.6011037519201636, 0.44829055899754167, 0.8524657934904099]);

var r2 = Decoder.SeededRandom(42);
var picks = string.Join(" ", Enumerable.Range(0, 10).Select(_ => Decoder.Sample(dist, r2)));
Check([picks], ["Paris Paris a Paris Paris Paris Paris Paris a Paris"]);
var r3 = Decoder.SeededRandom(42);
Check([Enumerable.Range(0, 1000).Count(_ => Decoder.Sample(dist, r3) == "Paris")], [796]); // about 80.2%

Check([Decoder.Greedy(Decoder.Softmax(scores, 2))], ["Paris"]);
Console.WriteLine("ok: decoding matches the TypeScript lab");

static void Check<T>(List<T> got, List<T> want)
{
    if (!got.SequenceEqual(want))
        throw new Exception($"got [{string.Join(", ", got)}], want [{string.Join(", ", want)}]");
}

/// <summary>One token and its score or probability. Lists keep a fixed order, so sampling is reproducible.</summary>
record Entry(string Token, double P);

static class Decoder
{
    /// <summary>mulberry32. new Random(seed) also repeats; this one matches every language in this companion.</summary>
    public static Func<double> SeededRandom(uint seed)
    {
        var a = seed;
        return () =>
        {
            unchecked // uint arithmetic wraps at 32 bits, like JavaScript's >>> 0
            {
                a += 0x6d2b79f5;
                var t = a;
                t = (t ^ (t >> 15)) * (t | 1);
                t ^= t + (t ^ (t >> 7)) * (t | 61);
                return (t ^ (t >> 14)) / 4294967296.0;
            }
        };
    }

    public static List<Entry> Softmax(List<Entry> scores, double temperature)
    {
        var top = scores.Max(e => e.P / temperature); // subtract the max so Math.Exp can't overflow
        return Renormalise(scores.Select(e => e with { P = Math.Exp(e.P / temperature - top) }));
    }

    static IEnumerable<Entry> ByProbability(List<Entry> dist) => dist.OrderByDescending(e => e.P); // stable

    public static List<Entry> TopK(List<Entry> dist, int k) => Renormalise(ByProbability(dist).Take(k));

    public static List<Entry> TopP(List<Entry> dist, double p)
    {
        var kept = new List<Entry>();
        var cumulative = 0.0;
        foreach (var e in ByProbability(dist))
        {
            kept.Add(e);
            if ((cumulative += e.P) >= p) break;
        }
        return Renormalise(kept);
    }

    static List<Entry> Renormalise(IEnumerable<Entry> entries)
    {
        var list = entries.ToList();
        var total = list.Sum(e => e.P);
        return list.Select(e => e with { P = e.P / total }).ToList();
    }

    public static string Sample(List<Entry> dist, Func<double> random)
    {
        var r = random();
        foreach (var e in dist)
            if ((r -= e.P) < 0) return e.Token;
        return dist[^1].Token;
    }

    public static string Greedy(List<Entry> dist) => ByProbability(dist).First().Token;
}
```

**Labs:** every version is in [`ai-ml/03-ai-engineer/02-how-llms-work/labs/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/02-how-llms-work/labs), one folder per language. From the vault root, `python3 labs/run.py how-llms-work` runs all eight and checks this page still shows the same code. The C# lab runs in the .NET SDK container, through podman.

## Common pitfalls

1. **Expecting the same seed to give the same text across languages or libraries.** Each generator has its own sequence. Only the same generator, given the same seed, repeats.
2. **Signed overflow in C or C++.** `int` overflow is undefined behaviour, and an optimising compiler can produce something unexpected. Use `uint32_t`.
3. **Forgetting Python never overflows.** Without masking, the numbers just grow, and the sequence is wrong from the second step.
4. **Sampling from an unordered map.** Go's maps and Python's sets don't promise an order, so the same random number would pick a different token from run to run. Keep the distribution in a list.
5. **Tokenizer mismatch.** Counting tokens for a Llama model with OpenAI's `tiktoken` gives the wrong number. Use the tokenizer that matches the model.

## Check your understanding

1. Why do the probabilities match exactly in all seven languages?
2. `random.Random(42)` in Python and `new Random(42)` in C# both start from 42. Will they sample the same tokens? Why or why not?
3. Why does the Python generator need `& 0xFFFFFFFF`, while the Go one doesn't?
4. What would go wrong if the C version used `int` instead of `uint32_t`?
5. Ollama is written in Go. Why does the main lesson's sampling actually happen in C++?

<details>
<summary>Answers — after your attempt</summary>

1. All seven use IEEE 754 doubles, and the same operations in the same order, with correctly rounded results for `exp` and division.
2. No. They're different generator algorithms, so the same seed produces different sequences, and so different picks.
3. Python integers grow without limit, so the program has to cut them back to 32 bits itself. Go's `uint32` wraps automatically.
4. The multiplications overflow, and signed overflow is undefined behaviour in C. The compiler may assume it never happens and optimise accordingly, so the results could be wrong and could change with the optimisation level.
5. Ollama manages models and serves the API in Go, but runs the model itself through llama.cpp, which is C and C++. Scoring and sampling happen there.

</details>

## Practice — independent task

**Add top-k and a temperature-0 path to the language you'll use most.** Several versions above implement top-p but leave out pieces (C has no top-k; none of them has `generate`).

1. Add `top_k` in that language, and a `generate` loop with a toy bigram model, like the main lesson's TypeScript.
2. Assert that temperature 0 gives `the cat sat on the cat sat` from the main lesson's corpus.
3. Then use that language's Ollama client from §1 to ask for `logprobs` on one prompt, and print the top five tokens as percentages.

**Done when:** your tests pass, your bigram output matches the TypeScript output word for word, and your live script prints probabilities from the real model.

## Before moving on

You can name your language's tokenizer and local-inference tools, write the decoding step in it, and explain why identical seeds only give identical tokens with the identical generator.

**Recap.** The decoding maths is identical in every language, and so are its results, because they all use IEEE 754 doubles. Random generators differ between languages, so cross-language reproducibility needs one shared generator. Its 32-bit wrapping is written differently in each: masks in Python, unsigned types in Go, C, C++ and C#, `>>>` in Java, `wrapping_*` in Rust.

## Related
- [[ai-ml/03-ai-engineer/02-how-llms-work/index|How LLMs work]] — the main lesson
- [[ai-ml/03-ai-engineer/04-calling-models/in-other-languages|Calling models in other languages]] — each language's model clients
- [[ai-ml/03-ai-engineer/16-local-and-open-models/index|Local and open models]] — running llama.cpp through Ollama on a laptop
