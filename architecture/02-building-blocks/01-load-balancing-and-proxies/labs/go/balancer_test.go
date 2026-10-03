package balancing

import (
	"errors"
	"fmt"
	"slices"
	"testing"
)

var four = []string{"cache-a", "cache-b", "cache-c", "cache-d"}

func keys() []string {
	ks := make([]string, 10_000)
	for i := range ks {
		ks[i] = fmt.Sprintf("user:%d", i)
	}
	return ks
}

func TestRoundRobinTakesTurnsLeastOutstandingLooks(t *testing.T) {
	pick, queues := RoundRobin(), []int{5, 0, 0}
	var got []int
	for range 6 {
		got = append(got, pick(queues, nil))
	}
	if !slices.Equal(got, []int{0, 1, 2, 0, 1, 2}) || LeastOutstanding(queues, nil) != 1 {
		t.Fatal(got)
	}
}

func TestSmoothWeightedRoundRobin(t *testing.T) {
	pick := SmoothWeighted([]Weighted{{"a", 5}, {"b", 1}, {"c", 1}})
	got := ""
	for range 7 {
		got += pick()
	}
	if got != "aabacaa" {
		t.Fatal(got)
	}
}

func TestAlgorithmsThatLookAtQueuesWinInTheTail(t *testing.T) {
	for _, c := range []struct {
		pick Pick
		want Latency
	}{
		{RoundRobin(), Latency{214, 138, 1_158}},
		{Random, Latency{255, 159, 1_588}},
		{LeastOutstanding, Latency{68, 17, 466}},
		{TwoChoices, Latency{96, 25, 495}},
	} {
		if got := Simulate(c.pick, 4, 0.8, 100_000, 7); got != c.want {
			t.Errorf("got %v, want %v", got, c.want)
		}
	}
}

func TestThreeFailuresToGoDownTwoSuccessesToComeBack(t *testing.T) {
	h := NewHealth(3, 2)
	var states []bool
	for _, ok := range []bool{false, false, true, false, false, false, true, true} {
		h.Record(ok)
		states = append(states, h.Up)
	}
	if !slices.Equal(states, []bool{true, true, true, true, true, false, false, true}) {
		t.Fatal(states)
	}
}

func TestSkipsDownServersAndFailsWhenAllAreDown(t *testing.T) {
	servers := []Server{{"app-1", NewHealth(3, 2)}, {"app-2", NewHealth(3, 2)}, {"app-3", NewHealth(3, 2)}}
	for range 3 {
		servers[1].Health.Record(false)
	}
	var got []string
	for turn := range 4 {
		name, _ := PickHealthy(servers, turn)
		got = append(got, name)
	}
	if !slices.Equal(got, []string{"app-1", "app-3", "app-1", "app-3"}) {
		t.Fatal(got)
	}
	for _, s := range servers {
		for range 3 {
			s.Health.Record(false)
		}
	}
	if _, err := PickHealthy(servers, 0); !errors.Is(err, ErrNoHealthyServers) {
		t.Fatal(err)
	}
}

func TestModuloMovesFourInFiveARingAboutOneInFive(t *testing.T) {
	ks, five := keys(), append(slices.Clone(four), "cache-e")
	movedByModulo := 0
	for _, k := range ks {
		if Modulo(k, four) != Modulo(k, five) {
			movedByModulo++
		}
	}
	ring := NewHashRing(four, 100)
	before := make([]string, len(ks))
	for i, k := range ks {
		before[i] = ring.ServerFor(k)
	}
	ring.Add("cache-e")
	moved := 0
	for i, k := range ks {
		if now := ring.ServerFor(k); now != before[i] {
			moved++
			if now != "cache-e" {
				t.Fatal(k, "moved to", now)
			}
		}
	}
	if abs(movedByModulo-8_000) >= 200 || abs(moved-2_000) >= 300 {
		t.Fatal(movedByModulo, moved)
	}
	ring.Remove("cache-e")
	for i, k := range ks {
		if ring.ServerFor(k) != before[i] {
			t.Fatal(k, "didn't go back")
		}
	}
}

func TestVirtualNodesEvenOutTheKeys(t *testing.T) {
	busiest := func(replicas int) float64 {
		ring, counts := NewHashRing(four, replicas), map[string]int{}
		for _, k := range keys() {
			counts[ring.ServerFor(k)]++
		}
		most := 0
		for _, n := range counts {
			most = max(most, n)
		}
		return float64(most) / (10_000 / 4)
	}
	if one, hundred := busiest(1), busiest(100); one <= 1.4 || hundred >= 1.2 {
		t.Fatal(one, hundred)
	}
}

func abs(n int) int { return max(n, -n) }
