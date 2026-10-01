# Observability in Other Languages

> **[Intermediate]** · A companion to [[devops/10-observability/01-observability-fundamentals|observability fundamentals]], which computes exact percentiles by sorting every request time. Real metrics systems don't keep every value: they count requests into **histogram buckets** and *estimate* percentiles from the counts. This companion shows that estimate in seven languages — using Prometheus's own client libraries and .NET's built-in metrics API where they exist.

## Before you start

You can already:

- Explain the three pillars, the golden signals, percentiles versus the average, SLOs and burn rate → [[devops/10-observability/01-observability-fundamentals|the main lesson]].
- Read code in at least one language below. Read §1–2 and your languages.

After this lesson you will be able to:

1. Explain how a histogram stores latency in constant memory, and how a percentile is estimated from it.
2. Choose bucket boundaries so the estimate is accurate where it matters — around your SLO.
3. Name your ecosystem's metrics library and its OpenTelemetry SDK.

## The kid version

Instead of writing down every runner's exact finishing time, a race marshal just counts how many finished in under 10 minutes, under 20, under 30. Later, asked "how fast was the middle runner?", the marshal can say "somewhere between 10 and 20 minutes — probably about 14". That's a **histogram**: counts per band, and a sensible guess inside the band.

**Where the analogy stops working.** A marshal can choose bands after the race. A histogram's buckets are fixed before any data arrives — choose them badly and every answer is a wide guess. §2 shows how wide.

## 1. The tools, by ecosystem

| Language | Metrics API | Prometheus client | Tracing |
|---|---|---|---|
| TypeScript | OpenTelemetry API | `prom-client` | OpenTelemetry JS |
| Python | OpenTelemetry API | **`prometheus_client`** | OpenTelemetry Python |
| Go | OpenTelemetry API | **`client_golang`** | OpenTelemetry Go |
| Java | **Micrometer** (Spring Boot's default) | Micrometer's Prometheus registry | OpenTelemetry Java agent |
| Rust | `metrics` crate | `metrics-exporter-prometheus`, `prometheus` | `tracing` + `tracing-opentelemetry` |
| C# | **`System.Diagnostics.Metrics`** — built in | OpenTelemetry's Prometheus exporter | **`System.Diagnostics.Activity`** — built in |
| C, C++ | — | `prometheus-cpp` | OpenTelemetry C++ |

**OpenTelemetry** is the common thread: one vendor-neutral standard for metrics, traces and logs, with an SDK per language, so instrumenting once lets you send data to any backend. .NET goes furthest — its built-in `Meter` and `Activity` types *are* the OpenTelemetry API.

## 2. How a histogram estimates a percentile

A histogram has fixed **upper bounds** — here 25, 50, 100, 250, 500, 1000, 2500 and 5000 ms, plus an overflow bucket — and one counter per bucket. Recording a request is one increment, whatever the traffic, so memory never grows.

To estimate a percentile, Prometheus's `histogram_quantile()`:

1. Computes the **rank**: q × total. For p99 of 100 requests, rank 99.
2. Finds the first bucket whose **cumulative** count reaches the rank.
3. Assumes requests are spread evenly inside that bucket and **interpolates** between its lower and upper bound.

For the main lesson's 100 requests:

| Bucket (`le`, ms) | Cumulative count |
|---|---|
| ≤ 25 | 60 |
| ≤ 50 | 97 |
| ≤ 100 … ≤ 1000 | 97 |
| ≤ 2500 | 99 |
| ≤ 5000 | 100 |

- **p50:** rank 50 lies in the first bucket (0–25 ms, 60 requests): 0 + 25 × 50 ⁄ 60 ≈ **20.8 ms**. Exact: 24 ms.
- **p99:** rank 99 lies in the 1000–2500 bucket (requests 98 and 99): 1000 + 1500 × (99 − 97) ⁄ (99 − 97) = **2500 ms**. Exact: 2100 ms.

The p99 is off by 400 ms because the bucket is 1500 ms wide. **The estimate can only be as precise as the bucket containing it.** So put bounds close together where you make decisions: if the SLO is "under 500 ms", have bounds at 400, 500 and 600, so "how many requests beat 500 ms?" is exact and nearby percentiles are tight.

Note **`le` means *less than or equal***: a 25 ms request counts in the ≤ 25 bucket. (Writing this lesson, the first hand count used "less than" and got 50 instead of 60; the real library's output corrected it.)

## Terms used in this lesson

1. **Histogram (metric)**: This is a metric that counts observations into fixed buckets by value, plus a total count and sum.
2. **Bucket bound (`le`)**: This is a bucket's upper limit, inclusive: "less than or equal".
3. **Cumulative count**: This is the number of observations in a bucket *and all smaller ones* — how Prometheus stores histograms.
4. **OpenTelemetry**: This is also known as **OTel**. It is a vendor-neutral standard and set of SDKs for producing metrics, traces and logs.
5. **Exposition format**: This is the plain-text format a service serves at `/metrics` for Prometheus to scrape.

## 3. Python

`prometheus_client` records the histogram; `generate_latest` renders the text Prometheus scrapes, where the cumulative buckets are visible line by line.

```python
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
```

**Lab:** `labs/observability-python/` — checked with Python 3.14; `uv` fetches `prometheus_client`. The test checks the scrape text contains `request_duration_ms_bucket{le="25.0"} 60.0`.

## 4. Go

`client_golang` is Prometheus's own Go client — Prometheus itself is written in Go. `Write` exposes the histogram's cumulative buckets directly.

```go
// Package signals: a real Prometheus histogram (client_golang), and the bucket-based
// percentile estimate Prometheus's histogram_quantile() performs.
package signals

import (
	"math"

	"github.com/prometheus/client_golang/prometheus"
	dto "github.com/prometheus/client_model/go"
)

var BucketsMs = []float64{25, 50, 100, 250, 500, 1000, 2500, 5000}

type Bucket struct{ UpperBound, CumulativeCount float64 }

// Record observes every latency and returns the cumulative buckets, as Prometheus stores them.
func Record(latenciesMs []float64) ([]Bucket, error) {
	h := prometheus.NewHistogram(prometheus.HistogramOpts{
		Name: "request_duration_ms", Help: "Request latency", Buckets: BucketsMs,
	})
	for _, ms := range latenciesMs {
		h.Observe(ms)
	}
	var m dto.Metric
	if err := h.Write(&m); err != nil {
		return nil, err
	}
	var out []Bucket
	for _, b := range m.GetHistogram().GetBucket() {
		out = append(out, Bucket{b.GetUpperBound(), float64(b.GetCumulativeCount())})
	}
	return append(out, Bucket{UpperBound: math.Inf(1), CumulativeCount: float64(m.GetHistogram().GetSampleCount())}), nil
}

// EstimateQuantile finds the bucket holding rank q×total and interpolates linearly inside it.
func EstimateQuantile(q float64, buckets []Bucket) float64 {
	rank := q * buckets[len(buckets)-1].CumulativeCount
	lower, lowerCount := 0.0, 0.0
	for _, b := range buckets {
		if b.CumulativeCount >= rank {
			if math.IsInf(b.UpperBound, 1) {
				return lower
			}
			return lower + (b.UpperBound-lower)*(rank-lowerCount)/(b.CumulativeCount-lowerCount)
		}
		lower, lowerCount = b.UpperBound, b.CumulativeCount
	}
	return lower
}
```

**Lab:** `labs/observability-go/` — checked with Go 1.26; `go test` downloads the client on the first run.

## 5. Java

In Spring Boot, **Micrometer** records metrics and Actuator serves them; a `Timer` with `publishPercentileHistogram()` exports exactly these buckets. The lab builds the histogram by hand to show the mechanics:

```java
package signals;

import java.util.Arrays;

// A Prometheus-style histogram: fixed upper bounds, a count per bucket. In Spring Boot,
// Micrometer's Timer with publishPercentileHistogram() exports exactly this to Prometheus.
public final class Histogram {
    private final double[] bounds;       // upper bounds, ascending; the last bucket is +Inf
    private final long[] counts;         // per bucket, not cumulative

    public Histogram(double... bounds) {
        this.bounds = bounds.clone();
        this.counts = new long[bounds.length + 1];
    }

    public void observe(double value) {
        int i = 0;
        while (i < bounds.length && value > bounds[i]) i++;   // "le": less than or equal
        counts[i]++;
    }

    // Prometheus's histogram_quantile: find the bucket holding rank q×total, interpolate inside it.
    public double estimateQuantile(double q) {
        double total = Arrays.stream(counts).sum();
        double rank = q * total, lower = 0, cumulative = 0;
        for (int i = 0; i < counts.length; i++) {
            double before = cumulative;
            cumulative += counts[i];
            if (cumulative >= rank) {
                if (i == bounds.length) return lower;                 // the +Inf bucket
                return lower + (bounds[i] - lower) * (rank - before) / (cumulative - before);
            }
            if (i < bounds.length) lower = bounds[i];
        }
        return lower;
    }

    public static void main(String[] args) {
        var h = new Histogram(25, 50, 100, 250, 500, 1000, 2500, 5000);
        for (int i = 0; i < 97; i++) h.observe(20 + i % 10);
        for (double ms : new double[] {1800, 2100, 3000}) h.observe(ms);
        assert Math.abs(h.estimateQuantile(0.50) - 20.83) < 0.01 : h.estimateQuantile(0.50);   // exact: 24
        assert h.estimateQuantile(0.99) == 2500 : h.estimateQuantile(0.99);                    // exact: 2100
        System.out.println("ok: p50 ~ 20.83, p99 ~ 2500 from buckets");
    }
}
```

**Lab:** `labs/observability-java/` — checked with Java 21.

## 6. Rust

The `metrics` crate is the facade, like `log` for logging, with a Prometheus exporter behind it; `tracing` with `tracing-opentelemetry` covers traces. The histogram itself:

```rust
//! A Prometheus-style histogram. In services, the `metrics` crate with a Prometheus exporter
//! (or the `prometheus` crate) records these; the estimate below is what Prometheus computes.
pub struct Histogram {
    bounds: Vec<f64>, // ascending upper bounds; one extra bucket for +Inf
    counts: Vec<u64>,
}

impl Histogram {
    pub fn new(bounds: &[f64]) -> Self {
        Histogram {
            bounds: bounds.to_vec(),
            counts: vec![0; bounds.len() + 1],
        }
    }

    pub fn observe(&mut self, value: f64) {
        // "le": the first bucket whose bound is >= the value
        let i = self
            .bounds
            .iter()
            .position(|&b| value <= b)
            .unwrap_or(self.bounds.len());
        self.counts[i] += 1;
    }

    pub fn estimate_quantile(&self, q: f64) -> f64 {
        let total: u64 = self.counts.iter().sum();
        let rank = q * total as f64;
        let (mut lower, mut cumulative) = (0.0, 0.0);
        for (i, &count) in self.counts.iter().enumerate() {
            let before = cumulative;
            cumulative += count as f64;
            if cumulative >= rank {
                return match self.bounds.get(i) {
                    Some(&upper) => {
                        lower + (upper - lower) * (rank - before) / (cumulative - before)
                    }
                    None => lower, // the +Inf bucket
                };
            }
            if let Some(&upper) = self.bounds.get(i) {
                lower = upper;
            }
        }
        lower
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bucket_estimates_versus_exact() {
        let mut h = Histogram::new(&[25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0]);
        (0..97).for_each(|i| h.observe(20.0 + (i % 10) as f64));
        [1800.0, 2100.0, 3000.0]
            .into_iter()
            .for_each(|ms| h.observe(ms));
        assert!((h.estimate_quantile(0.50) - 20.83).abs() < 0.01); // exact: 24
        assert_eq!(h.estimate_quantile(0.99), 2500.0); // exact: 2100
    }
}
```

**Lab:** `labs/observability-rust/` — checked with Rust 1.96.

## 7. C and C++

A fixed array of counters — the reason histograms are cheap enough for hot paths. C++ sizes it at compile time with `std::array` and finds the bucket with `std::lower_bound`, which is exactly the "first bound ≥ value" rule.

```c
/* histogram.c — a fixed-bucket latency histogram: constant memory, one increment per
 * observation. This is how metrics libraries record latency cheaply in hot paths. */
#include <assert.h>
#include <math.h>
#include <stdio.h>

#define NBOUNDS 8
static const double bounds[NBOUNDS] = {25, 50, 100, 250, 500, 1000, 2500, 5000};

typedef struct { long counts[NBOUNDS + 1]; } histogram;   /* the last slot is +Inf */

static void observe(histogram *h, double value) {
    int i = 0;
    while (i < NBOUNDS && value > bounds[i]) i++;          /* "le": less than or equal */
    h->counts[i]++;
}

static double estimate_quantile(const histogram *h, double q) {
    long total = 0;
    for (int i = 0; i <= NBOUNDS; i++) total += h->counts[i];
    double rank = q * (double)total, lower = 0, cumulative = 0;
    for (int i = 0; i <= NBOUNDS; i++) {
        double before = cumulative;
        cumulative += (double)h->counts[i];
        if (cumulative >= rank) {
            if (i == NBOUNDS) return lower;                 /* the +Inf bucket */
            return lower + (bounds[i] - lower) * (rank - before) / (cumulative - before);
        }
        if (i < NBOUNDS) lower = bounds[i];
    }
    return lower;
}

int main(void) {
    histogram h = {0};
    for (int i = 0; i < 97; i++) observe(&h, 20 + i % 10);
    observe(&h, 1800); observe(&h, 2100); observe(&h, 3000);
    assert(fabs(estimate_quantile(&h, 0.50) - 20.83) < 0.01);   /* exact: 24 */
    assert(estimate_quantile(&h, 0.99) == 2500);                /* exact: 2100 */
    puts("ok: p50 ~ 20.83, p99 ~ 2500 from buckets");
    return 0;
}
```

```cpp
// histogram.cpp — a fixed-bucket histogram with std::array, sized at compile time.
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>

template <std::size_t N>
class Histogram {
public:
    explicit constexpr Histogram(std::array<double, N> bounds) : bounds_(bounds) {}

    void observe(double value) {
        // "le": the first bound >= value; past the end means the +Inf bucket
        auto it = std::lower_bound(bounds_.begin(), bounds_.end(), value);
        ++counts_[static_cast<std::size_t>(it - bounds_.begin())];
    }

    double estimate_quantile(double q) const {
        const double total = static_cast<double>(std::accumulate(counts_.begin(), counts_.end(), 0L));
        const double rank = q * total;
        double lower = 0, cumulative = 0;
        for (std::size_t i = 0; i < counts_.size(); ++i) {
            const double before = cumulative;
            cumulative += static_cast<double>(counts_[i]);
            if (cumulative >= rank) {
                if (i == N) return lower;
                return lower + (bounds_[i] - lower) * (rank - before) / (cumulative - before);
            }
            if (i < N) lower = bounds_[i];
        }
        return lower;
    }

private:
    std::array<double, N> bounds_;
    std::array<long, N + 1> counts_{};
};

int main() {
    Histogram<8> h({25, 50, 100, 250, 500, 1000, 2500, 5000});
    for (int i = 0; i < 97; ++i) h.observe(20 + i % 10);
    for (double ms : {1800.0, 2100.0, 3000.0}) h.observe(ms);
    assert(std::abs(h.estimate_quantile(0.50) - 20.83) < 0.01);   // exact: 24
    assert(h.estimate_quantile(0.99) == 2500);                    // exact: 2100
    std::cout << "ok: p50 ~ 20.83, p99 ~ 2500 from buckets\n";
}
```

**Labs:** `labs/observability-c/` and `labs/observability-cpp/` — checked with GCC 16.

## 8. C#

`System.Diagnostics.Metrics` is part of .NET: code records to a `Histogram<T>` from a `Meter`, and exporters subscribe through a `MeterListener`. In an app, `AddOpenTelemetry().WithMetrics(...)` with a Prometheus exporter does the listening; here the listener does the bucketing itself.

```csharp
using System.Diagnostics.Metrics;

// System.Diagnostics.Metrics is built into .NET: code records to a Histogram<T> on a Meter;
// an exporter (OpenTelemetry, Prometheus) listens and does the bucketing. Here a MeterListener
// plays the exporter, bucketing exactly as Prometheus would.
double[] bounds = [25, 50, 100, 250, 500, 1000, 2500, 5000];
var counts = new long[bounds.Length + 1];

using var meter = new Meter("Shop.Api");
var duration = meter.CreateHistogram<double>("request.duration", unit: "ms");

using var listener = new MeterListener();
listener.InstrumentPublished = (instrument, l) => { if (instrument.Meter == meter) l.EnableMeasurementEvents(instrument); };
listener.SetMeasurementEventCallback<double>((_, value, _, _) =>
{
    var i = Array.FindIndex(bounds, b => value <= b);   // "le": less than or equal
    counts[i < 0 ? bounds.Length : i]++;
});
listener.Start();

for (var i = 0; i < 97; i++) duration.Record(20 + i % 10);
foreach (var ms in new double[] { 1800, 2100, 3000 }) duration.Record(ms);

Check(Math.Abs(EstimateQuantile(0.50) - 20.83) < 0.01, "p50 from buckets");   // exact: 24
Check(EstimateQuantile(0.99) == 2500, "p99 from buckets");                     // exact: 2100
Console.WriteLine("ok: p50 ~ 20.83, p99 ~ 2500 from buckets");

double EstimateQuantile(double q)
{
    double rank = q * counts.Sum(), lower = 0, cumulative = 0;
    for (var i = 0; i < counts.Length; i++)
    {
        var before = cumulative;
        cumulative += counts[i];
        if (cumulative >= rank)
            return i == bounds.Length ? lower : lower + (bounds[i] - lower) * (rank - before) / (cumulative - before);
        if (i < bounds.Length) lower = bounds[i];
    }
    return lower;
}

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }
```

**Lab:** `labs/observability-csharp/` — runs in the .NET 10 SDK container.

## Check your understanding

1. Why does a histogram use constant memory, and what does it give up in exchange?
2. Estimate p90 from the table in §2.
3. Your SLO is "99% of requests under 300 ms" and your buckets are 100, 250, 500, 1000. What's wrong, and how do you fix it?
4. What does `le` mean, and which bucket holds a request of exactly 50 ms?
5. Which ecosystem's built-in types *are* the OpenTelemetry API?

<details>
<summary>Answers — after your attempt</summary>

1. It keeps one counter per bucket, not one value per request. It gives up exactness: percentiles are estimated inside a bucket.
2. Rank 90 lies in the 25–50 ms bucket (cumulative 60 → 97): 25 + 25 × (90 − 60) ⁄ (97 − 60) ≈ 45.3 ms.
3. There's no bound at 300, so "fraction under 300 ms" can only be interpolated inside 250–500. Add bounds around 300 — say 250, 300, 350 — so the SLO is measured exactly.
4. Less than or equal. A 50 ms request is in the ≤ 50 bucket.
5. .NET's — `System.Diagnostics.Metrics` (`Meter`) and `System.Diagnostics.Activity` are the OpenTelemetry metrics and tracing APIs.

</details>

## Practice — independent task

**In your second language, or on the flagship:** instrument one route with a histogram from the language's metrics library, with bucket bounds chosen around your SLO threshold. Load-test it, then compare the bucket-estimated p99 with the exact p99 from the request logs (the main lesson's `red()` function).

**Done when:** the two are within the width of the bucket that holds the estimate, and you can say why they differ.

## Before moving on

You can explain how histograms estimate percentiles, choose buckets around an SLO, and name your ecosystem's metrics and tracing libraries.

**Recap.** Histograms count requests into fixed, inclusive buckets — constant memory, estimated percentiles. The estimate is only as precise as the bucket holding it, so put bounds around your SLO. OpenTelemetry is the cross-language standard; Prometheus has official clients for Go, Python and Java — Spring apps usually reach it through Micrometer instead; .NET builds metrics and tracing in.

**Next.** Back to the course: [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation and output encoding]] (week 7).

## Related
- [[devops/10-observability/01-observability-fundamentals|Observability fundamentals]] — the main lesson
- [[devops/10-observability/02-the-observability-stack|The observability stack]] — Prometheus, Grafana, Loki, Tempo
- [[languages/01-java/03-tooling/05-logging-and-observability|Logging and observability in Java]]
