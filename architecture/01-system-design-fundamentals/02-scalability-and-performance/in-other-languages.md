# Scalability & Performance in Other Languages

> **[Intermediate]** · A companion to [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|scalability and performance]], which works out percentiles, predicts how waiting grows as a server fills up, checks the prediction with a seeded simulation, and finds where adding machines stops helping. This page does the same in Python, Go, Java, Rust and C#, with the same numbers in every language. Three things change between languages: how they compute a percentile by default, the random numbers they give for a seed, and how one process uses more than one core, which decides how far each can scale up before it has to scale out.

## Before you start

You can already:

- Read p50, p95 and p99, and predict response time from utilisation with $T = S/(1 - \rho)$ → [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|the main lesson]].
- Run tests in at least one of the languages here.

After this lesson you will be able to:

1. Name the percentile method your language's library uses by default, and get nearest rank when you need it.
2. Make a simulation give the same numbers in two languages, and say why each language's own random generator can't.
3. Say how a single process in your language uses several cores, and what that means for scaling up.

## The kid version

Five children each measure how long the school queue takes, every lunchtime for a month, and work out "the slowest one in a hundred". They get slightly different answers from the same times, because each was taught a different rule for picking that one: take the 99th-from-the-bottom time, or take a point between two times. And when they each pretend-roll a die to make up queues, they get different rolls, so they can't check each other's sums until they all agree to use the same die.

**Where the analogy stops working.** Children's dice really are random. A computer's "random" numbers come from a formula, so if everyone uses the same formula and the same starting number, they get identical rolls. That's what the labs do.

## 1. The tools, by ecosystem

| Language | Percentile, by default | Seeded random numbers | Using many cores in one process | Benchmarking |
|---|---|---|---|---|
| TypeScript | none built in | none built in | one thread per process, so run several (cluster, containers) | `node --cpu-prof`, `autocannon` for load |
| Python | `numpy.percentile` interpolates; `statistics.quantiles` too | `random.Random(seed)` (Mersenne Twister) | processes; threads are limited by the GIL unless you use the free-threaded build | `timeit`, `pytest-benchmark` |
| Go | none in the standard library | `math/rand/v2` (PCG, ChaCha8) | goroutines across all cores | `testing.B`, `pprof` |
| Java | none built in | `new Random(seed)`, `RandomGenerator.of(...)` | threads; virtual threads for many waiting tasks | JMH |
| Rust | none in std | the `rand` crate | threads, or async on the tokio runtime | `criterion` |
| C# | none built in | `new Random(seed)` | the thread pool, `async`/`await` | BenchmarkDotNet |

For production latency, every language has a port of **HdrHistogram**, which records millions of measurements in fixed memory and answers any percentile. Metrics libraries such as Prometheus clients use histograms with fixed buckets, so their percentiles are estimates within a bucket. C and C++ have the same tools (`rand_r`, `<random>`, threads) but aren't usually where a service's latency is measured, so they have no lab here.

## 2. What changes between languages

### The percentile you get by default

The main lesson uses **nearest rank**: sort, then take the value at position ⌈p/100 × n⌉, so every percentile is a real measurement. NumPy's `percentile` defaults to **linear interpolation**: it takes a point between the two nearest measurements, so its p99 can be a value nobody measured. Python's `statistics.quantiles` uses yet another method by default. With thousands of samples the methods nearly agree. With 20 samples they can differ a lot, and dashboards built on different libraries won't match. The labs write nearest rank out by hand, which takes three lines in each language.

### The same "random" numbers everywhere

Every language has a seeded generator, but each uses a different formula: Python's is the Mersenne Twister, Go's `math/rand/v2` offers PCG and ChaCha8, Java's `Random` is a 48-bit linear congruential generator. The same seed gives different numbers in each, so a simulation can't be compared across languages. The labs port the main lesson's mulberry32 instead, a 32-bit generator that fits in six lines. It must wrap round at 32 bits exactly as JavaScript does:

- Go, Java and C# use 32-bit integer types, which wrap on their own. Java has no unsigned type, so it uses `>>>`, the shift that ignores the sign, and `Integer.toUnsignedLong` at the end.
- Rust's `u32` panics on overflow in debug builds, so it spells out `wrapping_add` and `wrapping_mul`.
- Python's ints never wrap, so it masks every step with `& 0xFFFFFFFF`.

With that done, all six languages produce the same 1,000 latencies, bit for bit: average 93 ms, p50 50, p95 59, p99 2,208.

### Adding up floating-point numbers

The mean is a sum divided by a count, and floating-point addition rounds at every step, so the order and method of adding change the last bits. Since Python 3.12, `sum()` uses compensated summation, which is more accurate than adding in a loop, and so slightly different from JavaScript's `reduce`. The Python lab adds in a plain loop to match; for real work, prefer `sum()` or `math.fsum`. Rust's `iter().sum()` and the other languages' loops add in order, like JavaScript.

### Sorting floating-point numbers

Rust's `f64` doesn't implement `Ord`, because `NaN` isn't less than, equal to or greater than anything. Sorting needs `sort_by(f64::total_cmp)`, which picks an order for `NaN`. Go's `slices.Sort`, Java's `Arrays.sort` and C#'s `Order()` sort floats without asking. All of them sort in place except LINQ, so the labs copy first: a percentile function shouldn't reorder its caller's data.

### Scaling up inside one process

The main lesson says to start vertical: a bigger machine. A bigger machine mostly means more cores, and languages differ in how one process uses them:

- **Node** runs your JavaScript on one thread. A 32-core machine needs 32 processes (the `cluster` module, or containers) behind a load balancer: scaling out, even on one box.
- **Python** threads share one interpreter lock (the GIL), so only one runs Python code at a time. CPU-heavy work needs processes. The free-threaded build, officially supported since Python 3.14 but not the default, removes the lock.
- **Go** spreads goroutines over every core automatically.
- **Java** and **C#** run threads on every core. Java's virtual threads and C#'s `async`/`await` let one process hold thousands of waiting requests cheaply.
- **Rust** has threads on every core, and the tokio runtime for async work.

This changes where the bottleneck first appears. A Node or Python service often hits one core at 100% while the machine is mostly idle, which is a single stage at full utilisation, exactly the main lesson's queueing curve.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| nearest-rank p50, p90, p99, p100 of 1–10 | 5, 9, 10, 10 |
| 1,000 seeded latencies (2% slow) | average 93, p50 50, p95 59, p99 2,208 ms |
| 10 ms of work at 50, 80, 90, 95, 99% busy | 20, 50, 100, 200, 1,000 ms |
| simulation at 50, 80 and 90% busy | within 10% of the formula; p99 ≈ 4.6 × mean |
| slow code vs busy server, then a second server | 333 and 200 ms, then 316 and 19 ms |
| slowest stage, before and after more app servers | database writes, 2,000 a second, both times |
| Amdahl with 5% serial, 8 machines; USL peak | 5.93; about 31 machines (5.7, 9.0, 8.0, 6.3) |

## Terms used in this lesson

1. **Nearest rank**: This is a percentile method that sorts the measurements and returns the one at position ⌈p/100 × n⌉, so the answer is always a real measurement.
2. **Linear interpolation**: In percentiles, this is a method that returns a point between the two measurements nearest the exact position, weighted by how close each is. It's NumPy's default.
3. **Pseudo-random number generator**: This is a formula that produces a sequence of numbers that look random. Started from the same **seed**, it produces the same sequence every time.
4. **Compensated summation**: This is a way of adding many floating-point numbers that keeps track of the rounding error at each step and adds it back, so the total is more accurate.
5. **GIL (global interpreter lock)**: The letters stand for those words. It's a lock in the standard Python interpreter that lets only one thread run Python code at a time.
6. **HdrHistogram**: This is a data structure for recording latencies that keeps fixed memory however many measurements arrive, and answers any percentile to a chosen precision.

## 4. Python

The generator masks every step with `MASK`, because Python's ints never wrap on their own. `mean` adds in a loop rather than with `sum()`, to match JavaScript's rounding. `percentile` raises `ValueError` on no samples. The tests round with `math.floor(x + 0.5)`, because `round()` rounds halves to even.

```python
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
```

```python
import math
import unittest

from scaling import amdahl, mean, percentile, response_time, seeded, simulate_server, throughput, usl, usl_peak


def round_half_up(x: float) -> int:
    return math.floor(x + 0.5)  # Python's round() sends halves to the even number; JavaScript's goes up


class Scaling(unittest.TestCase):
    def test_percentiles_by_nearest_rank(self):
        tens = [10, 1, 9, 2, 8, 3, 7, 4, 6, 5]
        self.assertEqual([percentile(tens, p) for p in [50, 90, 99, 100]], [5, 9, 10, 10])
        with self.assertRaises(ValueError):
            percentile([], 50)

    def test_the_average_hides_the_tail(self):
        random = seeded(42)
        latencies = []
        for _ in range(1_000):
            slow = random() < 0.02
            latencies.append(1_500 + 1_000 * random() if slow else 40 + 20 * random())
        got = [round_half_up(x) for x in [mean(latencies), *(percentile(latencies, p) for p in [50, 95, 99])]]
        self.assertEqual(got, [93, 50, 59, 2_208])

    def test_waiting_grows_slowly_then_all_at_once(self):
        self.assertEqual([round_half_up(response_time(10, b)) for b in [0.5, 0.8, 0.9, 0.95, 0.99]], [20, 50, 100, 200, 1_000])
        self.assertEqual(response_time(10, 1), math.inf)

    def test_the_simulation_agrees_with_the_formula(self):
        for busy in [0.5, 0.8, 0.9]:
            sim, model = simulate_server(10, busy, 200_000, 7), response_time(10, busy)
            self.assertLess(abs(sim["mean"] - model) / model, 0.1)
            self.assertLess(abs(sim["p99"] / sim["mean"] - math.log(100)), 0.5)

    def test_performance_or_scalability(self):
        got = [response_time(300, 0.1), response_time(10, 0.95), response_time(10, 0.95 / 2), response_time(300, 0.05)]
        self.assertEqual([round_half_up(x) for x in got], [333, 200, 19, 316])

    def test_the_slowest_stage(self):
        stages = [("load balancer", 50_000), ("app servers", 4 * 800), ("database writes", 2_000)]
        self.assertEqual(throughput(stages), (2_000, "database writes"))
        stages[1] = ("app servers", 8 * 800)
        self.assertEqual(throughput(stages), (2_000, "database writes"))

    def test_why_adding_machines_stops_helping(self):
        self.assertEqual(f"{amdahl(8, 0.05):.2f}", "5.93")
        self.assertLess(amdahl(1_000_000, 0.05), 20)
        self.assertEqual(round_half_up(usl_peak(0.05, 0.001)), 31)
        self.assertEqual([f"{usl(n, 0.05, 0.001):.1f}" for n in [8, 31, 60, 100]], ["5.7", "9.0", "8.0", "6.3"])


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/02-scalability-and-performance/labs/python). `python3 labs/run.py scalability-and-performance/python`.

## 5. Go

`uint32` arithmetic wraps by itself, so mulberry32 is the shortest here. `Percentile` returns an error for no samples, and clones before `slices.Sort`, which sorts in place. `Throughput` uses `slices.MinFunc` with `cmp.Compare`. Subtracting and converting to `int` would treat 2,000.4 and 2,000.0 as equal.

```go
// Package scaling: the arithmetic behind performance and scalability. The same numbers as the TypeScript lab,
// because the random number generator is the same one, bit for bit.
package scaling

import (
	"cmp"
	"errors"
	"math"
	"slices"
)

// Percentile by nearest rank: p99 of 1,000 samples is the 990th smallest. Go's standard library has none.
func Percentile(samples []float64, p float64) (float64, error) {
	if len(samples) == 0 {
		return 0, errors.New("no samples")
	}
	sorted := slices.Clone(samples) // slices.Sort sorts in place; don't reorder the caller's data
	slices.Sort(sorted)
	rank := max(1, int(math.Ceil(p/100*float64(len(sorted)))))
	return sorted[rank-1], nil
}

func Mean(samples []float64) float64 {
	total := 0.0
	for _, x := range samples {
		total += x
	}
	return total / float64(len(samples))
}

// Seeded is mulberry32. uint32 arithmetic wraps on its own, which is exactly what the generator needs.
func Seeded(seed uint32) func() float64 {
	a := seed
	return func() float64 {
		a += 0x6d2b79f5
		t := (a ^ a>>15) * (a | 1)
		t ^= t + (t^t>>7)*(t|61)
		return float64(t^t>>14) / 4294967296
	}
}

func exponential(random func() float64, mean float64) float64 {
	return -mean * math.Log(1-random())
}

// ResponseTime is the M/M/1 model: service time ÷ (1 − utilisation).
func ResponseTime(serviceMs, utilisation float64) float64 {
	if utilisation >= 1 {
		return math.Inf(1)
	}
	return serviceMs / (1 - utilisation)
}

type Summary struct{ Mean, P50, P99 float64 }

func SimulateServer(serviceMs, utilisation float64, requests int, seed uint32) Summary {
	random := Seeded(seed)
	gapMs := serviceMs / utilisation
	var arrives, free float64
	times := make([]float64, 0, requests)
	for range requests {
		arrives += exponential(random, gapMs)
		starts := max(arrives, free)
		free = starts + exponential(random, serviceMs)
		times = append(times, free-arrives)
	}
	p50, _ := Percentile(times, 50)
	p99, _ := Percentile(times, 99)
	return Summary{Mean(times), p50, p99}
}

type Stage struct {
	Name      string
	PerSecond float64
}

// Throughput is the slowest stage's, because every request passes through every stage.
func Throughput(stages []Stage) Stage {
	return slices.MinFunc(stages, func(a, b Stage) int { return cmp.Compare(a.PerSecond, b.PerSecond) })
}

func Amdahl(n, serial float64) float64 { return 1 / (serial + (1-serial)/n) }

func USL(n, alpha, beta float64) float64 { return n / (1 + alpha*(n-1) + beta*n*(n-1)) }

func USLPeak(alpha, beta float64) float64 { return math.Sqrt((1 - alpha) / beta) }
```

```go
package scaling

import (
	"fmt"
	"math"
	"slices"
	"testing"
)

func TestPercentilesByNearestRank(t *testing.T) {
	tens := []float64{10, 1, 9, 2, 8, 3, 7, 4, 6, 5}
	var got []float64
	for _, p := range []float64{50, 90, 99, 100} {
		v, _ := Percentile(tens, p)
		got = append(got, v)
	}
	if !slices.Equal(got, []float64{5, 9, 10, 10}) || tens[0] != 10 {
		t.Fatal(got, tens)
	}
	if _, err := Percentile(nil, 50); err == nil {
		t.Fatal("no error for no samples")
	}
}

func TestTheAverageHidesTheTail(t *testing.T) {
	random := Seeded(42)
	latencies := make([]float64, 0, 1_000)
	for range 1_000 {
		if random() < 0.02 {
			latencies = append(latencies, 1_500+1_000*random())
		} else {
			latencies = append(latencies, 40+20*random())
		}
	}
	got := []float64{math.Round(Mean(latencies))}
	for _, p := range []float64{50, 95, 99} {
		v, _ := Percentile(latencies, p)
		got = append(got, math.Round(v))
	}
	if !slices.Equal(got, []float64{93, 50, 59, 2_208}) {
		t.Fatal(got)
	}
}

func TestWaitingGrowsSlowlyThenAllAtOnce(t *testing.T) {
	var got []float64
	for _, busy := range []float64{0.5, 0.8, 0.9, 0.95, 0.99} {
		got = append(got, math.Round(ResponseTime(10, busy)))
	}
	if !slices.Equal(got, []float64{20, 50, 100, 200, 1_000}) || !math.IsInf(ResponseTime(10, 1), 1) {
		t.Fatal(got)
	}
}

func TestTheSimulationAgreesWithTheFormula(t *testing.T) {
	for _, busy := range []float64{0.5, 0.8, 0.9} {
		sim, model := SimulateServer(10, busy, 200_000, 7), ResponseTime(10, busy)
		if math.Abs(sim.Mean-model)/model >= 0.1 || math.Abs(sim.P99/sim.Mean-math.Log(100)) >= 0.5 {
			t.Fatal(busy, sim, model)
		}
	}
}

func TestPerformanceOrScalability(t *testing.T) {
	got := []float64{ResponseTime(300, 0.1), ResponseTime(10, 0.95), ResponseTime(10, 0.95/2), ResponseTime(300, 0.05)}
	for i := range got {
		got[i] = math.Round(got[i])
	}
	if !slices.Equal(got, []float64{333, 200, 19, 316}) {
		t.Fatal(got)
	}
}

func TestTheSlowestStage(t *testing.T) {
	stages := []Stage{{"load balancer", 50_000}, {"app servers", 4 * 800}, {"database writes", 2_000}}
	want := Stage{"database writes", 2_000}
	if got := Throughput(stages); got != want {
		t.Fatal(got)
	}
	stages[1].PerSecond = 8 * 800
	if got := Throughput(stages); got != want {
		t.Fatal(got)
	}
}

func TestWhyAddingMachinesStopsHelping(t *testing.T) {
	if got := fmt.Sprintf("%.2f", Amdahl(8, 0.05)); got != "5.93" || Amdahl(1_000_000, 0.05) >= 20 {
		t.Fatal(got)
	}
	if got := math.Round(USLPeak(0.05, 0.001)); got != 31 {
		t.Fatal(got)
	}
	var got []string
	for _, n := range []float64{8, 31, 60, 100} {
		got = append(got, fmt.Sprintf("%.1f", USL(n, 0.05, 0.001)))
	}
	if !slices.Equal(got, []string{"5.7", "9.0", "8.0", "6.3"}) {
		t.Fatal(got)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/02-scalability-and-performance/labs/go). `python3 labs/run.py scalability-and-performance/go`.

## 6. Java

`int` wraps like the generator needs, `>>>` shifts without the sign, and `Integer.toUnsignedLong` reads the final bits as unsigned. The generator keeps its state in a one-element array, because a lambda can only capture variables that never change. `String.format` gets `Locale.ROOT`; without it, a machine set to French prints "5,93".

```java
package scaling;

import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.function.DoubleSupplier;

/** The arithmetic behind performance and scalability. The same numbers as the TypeScript lab. */
public final class Scaling {
    private Scaling() {}

    /** Nearest rank: p99 of 1,000 samples is the 990th smallest. */
    public static double percentile(double[] samples, double p) {
        if (samples.length == 0) throw new IllegalArgumentException("no samples");
        double[] sorted = samples.clone(); // Arrays.sort sorts in place
        Arrays.sort(sorted);
        int rank = Math.max(1, (int) Math.ceil(p / 100 * sorted.length));
        return sorted[rank - 1];
    }

    public static double mean(double[] samples) {
        double total = 0;
        for (double x : samples) total += x;
        return total / samples.length;
    }

    /** mulberry32. Java's int wraps on overflow and >>> shifts without the sign, which is what it needs. */
    public static DoubleSupplier seeded(int seed) {
        int[] a = {seed};
        return () -> {
            a[0] += 0x6d2b79f5;
            int t = a[0];
            t = (t ^ (t >>> 15)) * (t | 1);
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            return Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
        };
    }

    static double exponential(DoubleSupplier random, double mean) {
        return -mean * Math.log(1 - random.getAsDouble());
    }

    /** M/M/1: service time ÷ (1 − utilisation). */
    public static double responseTime(double serviceMs, double utilisation) {
        return utilisation >= 1 ? Double.POSITIVE_INFINITY : serviceMs / (1 - utilisation);
    }

    public record Summary(double mean, double p50, double p99) {}

    public static Summary simulateServer(double serviceMs, double utilisation, int requests, int seed) {
        DoubleSupplier random = seeded(seed);
        double gapMs = serviceMs / utilisation;
        double arrives = 0;
        double free = 0;
        double[] times = new double[requests];
        for (int i = 0; i < requests; i++) {
            arrives += exponential(random, gapMs);
            double starts = Math.max(arrives, free);
            free = starts + exponential(random, serviceMs);
            times[i] = free - arrives;
        }
        return new Summary(mean(times), percentile(times, 50), percentile(times, 99));
    }

    public record Stage(String name, double perSecond) {}

    /** Every request passes every stage, so the system handles only as many as its slowest. */
    public static Stage throughput(List<Stage> stages) {
        return stages.stream().min(Comparator.comparingDouble(Stage::perSecond)).orElseThrow();
    }

    public static double amdahl(double n, double serial) {
        return 1 / (serial + (1 - serial) / n);
    }

    public static double usl(double n, double alpha, double beta) {
        return n / (1 + alpha * (n - 1) + beta * n * (n - 1));
    }

    public static double uslPeak(double alpha, double beta) {
        return Math.sqrt((1 - alpha) / beta);
    }
}
```

```java
package scaling;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.function.DoubleSupplier;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class ScalingCheck {
    private ScalingCheck() {}

    private static String fixed(double x, int places) {
        return String.format(Locale.ROOT, "%." + places + "f", x); // without Locale.ROOT, a French machine prints "5,93"
    }

    public static void main(String[] args) {
        double[] tens = {10, 1, 9, 2, 8, 3, 7, 4, 6, 5};
        assert Scaling.percentile(tens, 50) == 5 && Scaling.percentile(tens, 90) == 9;
        assert Scaling.percentile(tens, 99) == 10 && Scaling.percentile(tens, 100) == 10 && tens[0] == 10;
        try {
            Scaling.percentile(new double[0], 50);
            throw new AssertionError("expected an error for no samples");
        } catch (IllegalArgumentException expected) {
            // no samples
        }

        DoubleSupplier random = Scaling.seeded(42);
        double[] latencies = new double[1_000];
        for (int i = 0; i < latencies.length; i++) {
            boolean slow = random.getAsDouble() < 0.02;
            latencies[i] = slow ? 1_500 + 1_000 * random.getAsDouble() : 40 + 20 * random.getAsDouble();
        }
        List<Long> tail = List.of(Math.round(Scaling.mean(latencies)), Math.round(Scaling.percentile(latencies, 50)),
                Math.round(Scaling.percentile(latencies, 95)), Math.round(Scaling.percentile(latencies, 99)));
        assert tail.equals(List.of(93L, 50L, 59L, 2_208L)) : tail;

        List<Long> waits = new ArrayList<>();
        for (double busy : new double[] {0.5, 0.8, 0.9, 0.95, 0.99}) waits.add(Math.round(Scaling.responseTime(10, busy)));
        assert waits.equals(List.of(20L, 50L, 100L, 200L, 1_000L)) : waits;
        assert Scaling.responseTime(10, 1) == Double.POSITIVE_INFINITY;

        for (double busy : new double[] {0.5, 0.8, 0.9}) {
            var sim = Scaling.simulateServer(10, busy, 200_000, 7);
            double model = Scaling.responseTime(10, busy);
            assert Math.abs(sim.mean() - model) / model < 0.1 : sim;
            assert Math.abs(sim.p99() / sim.mean() - Math.log(100)) < 0.5 : sim;
        }

        assert Math.round(Scaling.responseTime(300, 0.1)) == 333 && Math.round(Scaling.responseTime(10, 0.95)) == 200;
        assert Math.round(Scaling.responseTime(10, 0.95 / 2)) == 19 && Math.round(Scaling.responseTime(300, 0.05)) == 316;

        var stages = new ArrayList<>(List.of(new Scaling.Stage("load balancer", 50_000),
                new Scaling.Stage("app servers", 4 * 800), new Scaling.Stage("database writes", 2_000)));
        var want = new Scaling.Stage("database writes", 2_000);
        assert Scaling.throughput(stages).equals(want);
        stages.set(1, new Scaling.Stage("app servers", 8 * 800));
        assert Scaling.throughput(stages).equals(want);

        assert fixed(Scaling.amdahl(8, 0.05), 2).equals("5.93") && Scaling.amdahl(1_000_000, 0.05) < 20;
        assert Math.round(Scaling.uslPeak(0.05, 0.001)) == 31;
        List<String> usl = new ArrayList<>();
        for (double n : new double[] {8, 31, 60, 100}) usl.add(fixed(Scaling.usl(n, 0.05, 0.001), 1));
        assert usl.equals(List.of("5.7", "9.0", "8.0", "6.3")) : usl;
        System.out.println("all scaling checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/02-scalability-and-performance/labs/java). `python3 labs/run.py scalability-and-performance/java`.

## 7. Rust

`seeded` returns `impl FnMut() -> f64`: a closure that changes its own state each call, which Rust marks with `FnMut`. The generator uses `wrapping_add` and `wrapping_mul`. `percentile` returns `Option`, and sorts with `f64::total_cmp`. `throughput` borrows the stage names, so the returned name is tied to the input's lifetime.

```rust
//! The arithmetic behind performance and scalability. The same numbers as the TypeScript lab, because the
//! random number generator is the same one, bit for bit.

/// Nearest rank: p99 of 1,000 samples is the 990th smallest. None for no samples.
pub fn percentile(samples: &[f64], p: f64) -> Option<f64> {
    if samples.is_empty() {
        return None;
    }
    let mut sorted = samples.to_vec();
    sorted.sort_by(f64::total_cmp); // f64 isn't Ord (NaN has no place), so say how to order it
    let rank = ((p / 100.0 * sorted.len() as f64).ceil() as usize).max(1);
    Some(sorted[rank - 1])
}

pub fn mean(samples: &[f64]) -> f64 {
    samples.iter().sum::<f64>() / samples.len() as f64
}

/// mulberry32. Plain + and * on u32 panic on overflow in a debug build, so the wrap-around is written out.
pub fn seeded(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = (a ^ (a >> 15)).wrapping_mul(a | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4_294_967_296.0
    }
}

fn exponential(random: &mut impl FnMut() -> f64, mean: f64) -> f64 {
    -mean * (1.0 - random()).ln()
}

/// M/M/1: service time ÷ (1 − utilisation).
pub fn response_time(service_ms: f64, utilisation: f64) -> f64 {
    if utilisation >= 1.0 {
        f64::INFINITY
    } else {
        service_ms / (1.0 - utilisation)
    }
}

#[derive(Debug)]
pub struct Summary {
    pub mean: f64,
    pub p50: f64,
    pub p99: f64,
}

pub fn simulate_server(service_ms: f64, utilisation: f64, requests: usize, seed: u32) -> Summary {
    let mut random = seeded(seed);
    let gap_ms = service_ms / utilisation;
    let (mut arrives, mut free) = (0.0_f64, 0.0_f64);
    let mut times = Vec::with_capacity(requests);
    for _ in 0..requests {
        arrives += exponential(&mut random, gap_ms);
        let starts = arrives.max(free);
        free = starts + exponential(&mut random, service_ms);
        times.push(free - arrives);
    }
    let p = |q| percentile(&times, q).expect("at least one request");
    Summary {
        mean: mean(&times),
        p50: p(50.0),
        p99: p(99.0),
    }
}

/// Every request passes every stage, so the system handles only as many as its slowest.
pub fn throughput<'a>(stages: &[(&'a str, f64)]) -> (&'a str, f64) {
    *stages
        .iter()
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .expect("at least one stage")
}

pub fn amdahl(n: f64, serial: f64) -> f64 {
    1.0 / (serial + (1.0 - serial) / n)
}

pub fn usl(n: f64, alpha: f64, beta: f64) -> f64 {
    n / (1.0 + alpha * (n - 1.0) + beta * n * (n - 1.0))
}

pub fn usl_peak(alpha: f64, beta: f64) -> f64 {
    ((1.0 - alpha) / beta).sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn percentiles_by_nearest_rank() {
        let tens = [10.0, 1.0, 9.0, 2.0, 8.0, 3.0, 7.0, 4.0, 6.0, 5.0];
        let got = [50.0, 90.0, 99.0, 100.0].map(|p| percentile(&tens, p).unwrap());
        assert_eq!(got, [5.0, 9.0, 10.0, 10.0]);
        assert_eq!(percentile(&[], 50.0), None);
    }

    #[test]
    fn the_average_hides_the_tail() {
        let mut random = seeded(42);
        let latencies: Vec<f64> = (0..1_000)
            .map(|_| {
                if random() < 0.02 {
                    1_500.0 + 1_000.0 * random()
                } else {
                    40.0 + 20.0 * random()
                }
            })
            .collect();
        let got = [
            mean(&latencies),
            percentile(&latencies, 50.0).unwrap(),
            percentile(&latencies, 95.0).unwrap(),
            percentile(&latencies, 99.0).unwrap(),
        ];
        assert_eq!(got.map(f64::round), [93.0, 50.0, 59.0, 2_208.0]);
    }

    #[test]
    fn waiting_grows_slowly_then_all_at_once() {
        let got = [0.5, 0.8, 0.9, 0.95, 0.99].map(|busy| response_time(10.0, busy).round());
        assert_eq!(got, [20.0, 50.0, 100.0, 200.0, 1_000.0]);
        assert_eq!(response_time(10.0, 1.0), f64::INFINITY);
    }

    #[test]
    fn the_simulation_agrees_with_the_formula() {
        for busy in [0.5, 0.8, 0.9] {
            let (sim, model) = (
                simulate_server(10.0, busy, 200_000, 7),
                response_time(10.0, busy),
            );
            assert!((sim.mean - model).abs() / model < 0.1, "{busy}: {sim:?}");
            assert!(
                (sim.p99 / sim.mean - 100f64.ln()).abs() < 0.5,
                "{busy}: {sim:?}"
            );
        }
    }

    #[test]
    fn performance_or_scalability() {
        let got = [
            response_time(300.0, 0.1),
            response_time(10.0, 0.95),
            response_time(10.0, 0.95 / 2.0),
            response_time(300.0, 0.05),
        ];
        assert_eq!(got.map(f64::round), [333.0, 200.0, 19.0, 316.0]);
    }

    #[test]
    fn the_slowest_stage() {
        let mut stages = [
            ("load balancer", 50_000.0),
            ("app servers", 4.0 * 800.0),
            ("database writes", 2_000.0),
        ];
        assert_eq!(throughput(&stages), ("database writes", 2_000.0));
        stages[1].1 = 8.0 * 800.0;
        assert_eq!(throughput(&stages), ("database writes", 2_000.0));
    }

    #[test]
    fn why_adding_machines_stops_helping() {
        assert_eq!(format!("{:.2}", amdahl(8.0, 0.05)), "5.93");
        assert!(amdahl(1_000_000.0, 0.05) < 20.0);
        assert_eq!(usl_peak(0.05, 0.001).round(), 31.0);
        assert_eq!(
            [8.0, 31.0, 60.0, 100.0].map(|n| format!("{:.1}", usl(n, 0.05, 0.001))),
            ["5.7", "9.0", "8.0", "6.3"]
        );
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/02-scalability-and-performance/labs/rust). `python3 labs/run.py scalability-and-performance/rust`.

## 8. C#

`uint` arithmetic is unchecked by default, so the generator reads like Go's. `Percentile` sorts a copy with LINQ's `Order()`, and `Throughput` uses `MinBy`. The checks round with `MidpointRounding.AwayFromZero` and format with `InvariantCulture`. It runs in the .NET SDK container.

```csharp
// The arithmetic behind performance and scalability. The same numbers as the TypeScript lab, because the
// random number generator is the same one, bit for bit.
public static class Scaling
{
    /// <summary>Nearest rank: p99 of 1,000 samples is the 990th smallest.</summary>
    public static double Percentile(IReadOnlyCollection<double> samples, double p)
    {
        if (samples.Count == 0) throw new ArgumentException("no samples", nameof(samples));
        var sorted = samples.Order().ToArray(); // a sorted copy; the caller's data keeps its order
        var rank = Math.Max(1, (int)Math.Ceiling(p / 100 * sorted.Length));
        return sorted[rank - 1];
    }

    public static double Mean(IReadOnlyCollection<double> samples)
    {
        var total = 0.0;
        foreach (var x in samples) total += x;
        return total / samples.Count;
    }

    /// <summary>mulberry32. C# arithmetic is unchecked unless you ask, so uint wraps as the generator needs.</summary>
    public static Func<double> Seeded(uint seed)
    {
        var a = seed;
        return () =>
        {
            a += 0x6d2b79f5;
            var t = (a ^ (a >> 15)) * (a | 1);
            t ^= t + (t ^ (t >> 7)) * (t | 61);
            return (t ^ (t >> 14)) / 4294967296.0;
        };
    }

    static double Exponential(Func<double> random, double mean) => -mean * Math.Log(1 - random());

    /// <summary>M/M/1: service time ÷ (1 − utilisation).</summary>
    public static double ResponseTime(double serviceMs, double utilisation) =>
        utilisation >= 1 ? double.PositiveInfinity : serviceMs / (1 - utilisation);

    public record Summary(double Mean, double P50, double P99);

    public static Summary SimulateServer(double serviceMs, double utilisation, int requests, uint seed)
    {
        var random = Seeded(seed);
        var gapMs = serviceMs / utilisation;
        double arrives = 0, free = 0;
        var times = new List<double>(requests);
        for (var i = 0; i < requests; i++)
        {
            arrives += Exponential(random, gapMs);
            var starts = Math.Max(arrives, free);
            free = starts + Exponential(random, serviceMs);
            times.Add(free - arrives);
        }
        return new(Mean(times), Percentile(times, 50), Percentile(times, 99));
    }

    public record Stage(string Name, double PerSecond);

    /// <summary>Every request passes every stage, so the system handles only as many as its slowest.</summary>
    public static Stage Throughput(IEnumerable<Stage> stages) => stages.MinBy(s => s.PerSecond)!;

    public static double Amdahl(double n, double serial) => 1 / (serial + (1 - serial) / n);

    public static double Usl(double n, double alpha, double beta) => n / (1 + alpha * (n - 1) + beta * n * (n - 1));

    public static double UslPeak(double alpha, double beta) => Math.Sqrt((1 - alpha) / beta);
}
```

```csharp
// Checks: the same numbers as every other language.
using System.Globalization;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Math.Round sends halves to the even number by default; JavaScript's Math.round goes up. Say which you mean.
static double Round(double x) => Math.Round(x, MidpointRounding.AwayFromZero);
static string Fixed(double x, int places) => x.ToString("F" + places, CultureInfo.InvariantCulture);

double[] tens = [10, 1, 9, 2, 8, 3, 7, 4, 6, 5];
Check(new[] { 50.0, 90, 99, 100 }.Select(p => Scaling.Percentile(tens, p)).SequenceEqual([5.0, 9, 10, 10]) && tens[0] == 10, "percentiles");
try
{
    Scaling.Percentile([], 50);
    Check(false, "expected an error for no samples");
}
catch (ArgumentException)
{
    // no samples
}

var random = Scaling.Seeded(42);
var latencies = new List<double>();
for (var i = 0; i < 1_000; i++) latencies.Add(random() < 0.02 ? 1_500 + 1_000 * random() : 40 + 20 * random());
double[] tail = [Scaling.Mean(latencies), .. new[] { 50.0, 95, 99 }.Select(p => Scaling.Percentile(latencies, p))];
Check(tail.Select(Round).SequenceEqual([93.0, 50, 59, 2_208]), string.Join(", ", tail));

Check(new[] { 0.5, 0.8, 0.9, 0.95, 0.99 }.Select(b => Round(Scaling.ResponseTime(10, b))).SequenceEqual([20.0, 50, 100, 200, 1_000]), "waits");
Check(double.IsPositiveInfinity(Scaling.ResponseTime(10, 1)), "full");

foreach (var busy in new[] { 0.5, 0.8, 0.9 })
{
    var sim = Scaling.SimulateServer(10, busy, 200_000, 7);
    var model = Scaling.ResponseTime(10, busy);
    Check(Math.Abs(sim.Mean - model) / model < 0.1 && Math.Abs(sim.P99 / sim.Mean - Math.Log(100)) < 0.5, sim);
}

double[] diagnosis = [Scaling.ResponseTime(300, 0.1), Scaling.ResponseTime(10, 0.95), Scaling.ResponseTime(10, 0.95 / 2), Scaling.ResponseTime(300, 0.05)];
Check(diagnosis.Select(Round).SequenceEqual([333.0, 200, 19, 316]), string.Join(", ", diagnosis));

var stages = new List<Scaling.Stage> { new("load balancer", 50_000), new("app servers", 4 * 800), new("database writes", 2_000) };
var want = new Scaling.Stage("database writes", 2_000);
Check(Scaling.Throughput(stages) == want, Scaling.Throughput(stages));
stages[1] = new("app servers", 8 * 800);
Check(Scaling.Throughput(stages) == want, "more app servers change nothing");

Check(Fixed(Scaling.Amdahl(8, 0.05), 2) == "5.93" && Scaling.Amdahl(1_000_000, 0.05) < 20, "amdahl");
Check(Round(Scaling.UslPeak(0.05, 0.001)) == 31, "peak");
Check(new[] { 8.0, 31, 60, 100 }.Select(n => Fixed(Scaling.Usl(n, 0.05, 0.001), 1)).SequenceEqual(["5.7", "9.0", "8.0", "6.3"]), "usl");
Console.WriteLine("all scaling checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/02-scalability-and-performance/labs/csharp). `python3 labs/run.py scalability-and-performance/csharp`.

## Common pitfalls

1. **Comparing percentiles from different libraries.** NumPy, `statistics`, Prometheus histograms and nearest rank each give a slightly different p99 for the same data. Use one method, and say which.
2. **Expecting the same seed to mean the same numbers across languages.** Each language's generator is a different formula. Port one generator if you need to compare.
3. **Averaging percentiles.** True in every language: the p99 of two servers isn't the mean of their p99s. Merge the raw data or the histograms.
4. **Sorting the caller's samples.** `slices.Sort`, `Arrays.sort` and `list.sort()` sort in place. Copy first in a function that only reads.
5. **One busy core on an idle machine.** Node, and Python with the GIL, use one core per process for your code. Watch per-core utilisation, not just the machine's average.

## Check your understanding

1. Why can't the Python lab use `random.Random(42)` and still match the TypeScript numbers?
2. Why does the Python generator need `& 0xFFFFFFFF` when the Go one doesn't?
3. On the first 20 of the lab's latencies, `numpy.percentile` gives p95 = 153 ms and p99 = 1,607 ms; nearest rank gives 58 ms and 1,971 ms. On all 1,000 they agree. Which is wrong, and why do they agree on 1,000?
4. Why does Rust refuse `samples.sort()` on a `Vec<f64>`?
5. A Python service on a 16-core machine is slow at 60% total CPU. Name a likely cause and a fix.

<details>
<summary>Answers — after your attempt</summary>

1. `random.Random` is the Mersenne Twister, a different formula from mulberry32, so seed 42 produces a different sequence, and every number built on it differs.
2. Python's integers grow without limit, so additions and multiplications never wrap. mulberry32 relies on 32-bit wrap-around, so the Python version keeps only the low 32 bits after each step. Go's `uint32` does that by itself.
3. Neither: they use different methods. With 20 samples, the 95% and 99% points fall between a fast request and the one slow one, and NumPy's interpolation lands somewhere in that gap: 153 ms is a latency no request had. Nearest rank returns a real measurement. With 1,000 samples, the neighbours around each point are close together, so interpolating between them barely moves the answer. Pick one method, use it everywhere, and distrust tail percentiles from small samples.
4. `sort()` needs `Ord`, a total order. `f64` has `NaN`, which isn't ordered against anything, so `f64` only implements `PartialOrd`. `sort_by(f64::total_cmp)` supplies an order that places `NaN` too.
5. Probably one process running CPU-heavy Python on one core at 100%, while the GIL keeps its other threads from helping. Run several worker processes (for example `gunicorn --workers`), move the hot path to code that releases the GIL, or try the free-threaded build.

</details>

## Practice — independent task

**Measure the interpolation gap.**

1. In Python, generate the main lesson's 1,000 latencies with the lab's `seeded(42)`.
2. Compute p50, p95, p99 and p99.9 by nearest rank and with `numpy.percentile` (`uv run --with numpy`), and with `statistics.quantiles(n=1000)`.
3. Repeat with only the first 20 latencies.

**Done when:** you have a table of the three methods at both sample sizes, and two sentences on when the methods' differences matter and which one you'd put on a dashboard.

## Before moving on

You can get a nearest-rank percentile in your language, reproduce a seeded simulation across languages, and say how your language uses several cores in one process.

**Recap.** The ideas don't change between languages; the defaults do. NumPy and `statistics` interpolate percentiles, and most standard libraries have none, so write nearest rank yourself or use HdrHistogram. Each language's generator is a different formula, so the labs port mulberry32 and handle 32-bit wrap-around in each language's way. Python's `sum()` compensates for rounding, and Rust's floats need `total_cmp` to sort. Node and GIL-bound Python use one core per process for your code, so they reach the queueing curve on a single core, while Go, Java, Rust and C# spread over all of them.

## Related

- [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|Scalability and performance]]: the main lesson
- [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/in-other-languages|How to approach system design in other languages]]: overflow and rounding in the same languages
- [[architecture/03-architectural-patterns/02-resilience-patterns/in-other-languages|Resilience patterns in other languages]]: limiting concurrent work in each language
