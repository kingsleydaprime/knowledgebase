package signals

import (
	"math"
	"testing"
)

func TestBucketEstimates(t *testing.T) {
	var latencies []float64
	for i := range 97 {
		latencies = append(latencies, float64(20+i%10))
	}
	latencies = append(latencies, 1800, 2100, 3000)

	buckets, err := Record(latencies)
	if err != nil {
		t.Fatal(err)
	}
	if p50 := EstimateQuantile(0.50, buckets); math.Abs(p50-20.83) > 0.01 { // exact: 24
		t.Fatalf("p50 = %v", p50)
	}
	if p99 := EstimateQuantile(0.99, buckets); p99 != 2500 { // exact: 2100
		t.Fatalf("p99 = %v", p99)
	}
}
