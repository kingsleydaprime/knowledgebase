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
