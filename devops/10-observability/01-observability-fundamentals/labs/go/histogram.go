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
