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
