package architecture

import (
	"fmt"
	"math"
	"slices"
	"testing"
)

var price = Pricing{PerMillionRequests: 0.2, PerGBSecond: 0.0000166667}

func TestCoordinationGrowsWithTheSquare(t *testing.T) {
	if got := []int{CoordinationLinks(4), CoordinationLinks(8), CoordinationLinks(50)}; !slices.Equal(got, []int{6, 28, 1_225}) {
		t.Fatal(got)
	}
}

func TestASharedReleaseBreaksMoreOften(t *testing.T) {
	if a, b := fmt.Sprintf("%.1f", ReleaseBreaks(40, 0.01)*100), fmt.Sprintf("%.1f", ReleaseBreaks(5, 0.01)*100); a != "33.1" || b != "4.9" {
		t.Fatal(a, b)
	}
}

func TestChattyVersusCoarse(t *testing.T) {
	ms, availability := Extract(40, 1, 0.9999)
	coarseMs, coarse := Extract(1, 1, 0.9999)
	if ms != 40 || fmt.Sprintf("%.2f", availability*100) != "99.60" || coarseMs != 1 || fmt.Sprintf("%.2f", coarse*100) != "99.99" {
		t.Fatal(ms, availability, coarseMs, coarse)
	}
}

func TestServerlessUntilTrafficIsSteady(t *testing.T) {
	one, fifty := ServerlessMonthly(1_000_000, 200, 0.5, price), ServerlessMonthly(50_000_000, 200, 0.5, price)
	breakEven := math.Round(BreakEvenRequests(30, 200, 0.5, price)/1e5) / 10
	if fmt.Sprintf("%.2f %.2f", one, fifty) != "1.87 93.33" || breakEven != 16.1 {
		t.Fatal(one, fifty, breakEven)
	}
}

func TestColdStartsHitQuietFunctions(t *testing.T) {
	var got []string
	for _, rate := range []float64{10, 1, 0.1} {
		got = append(got, fmt.Sprintf("%.2f", ColdShare(rate, 5)*100))
	}
	if !slices.Equal(got, []string{"0.00", "0.67", "60.65"}) {
		t.Fatal(got)
	}
	for _, rate := range []float64{1, 0.1} {
		if sim := SimulateColdShare(rate, 5, 100_000, 7); math.Abs(sim-ColdShare(rate, 5)) >= 0.005 {
			t.Fatal(rate, sim)
		}
	}
}

func TestBoundariesAndCycles(t *testing.T) {
	shop := []Module{
		{"orders", []string{"billing", "catalog/internal/prices"}},
		{"billing", []string{"customers"}},
		{"catalog", []string{"catalog/internal/prices"}},
		{"customers", nil},
	}
	if got := BoundaryViolations(shop); !slices.Equal(got, []string{"orders → catalog/internal/prices"}) || FindCycle(shop) != nil {
		t.Fatal(got, FindCycle(shop))
	}
	shop[3].Imports = append(shop[3].Imports, "orders")
	if got := FindCycle(shop); !slices.Equal(got, []string{"orders", "billing", "customers", "orders"}) {
		t.Fatal(got)
	}
}
