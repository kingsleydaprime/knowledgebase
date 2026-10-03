package approach

import (
	"fmt"
	"math"
	"slices"
	"testing"
)

var game = Compute(Assumptions{
	DailyActiveUsers: 10_000_000, WritesPerUserPerDay: 5, ReadsPerUserPerDay: 10, PeakToAverage: 3,
	BytesPerWrite: 50, KeptForDays: 365, BytesPerRead: 2_000,
})

func TestEstimate(t *testing.T) {
	got := []float64{math.Round(game.WritesPerSecond.Average), math.Round(game.WritesPerSecond.Peak), math.Round(game.ReadsPerSecond.Peak), game.ReadsPerWrite}
	if !slices.Equal(got, []float64{579, 1736, 3472, 2}) {
		t.Fatal(got)
	}
	if s, e := HumanBytes(game.StorageBytes), HumanBytes(game.PeakEgressBytesPerSecond); s != "910 GB" || e != "6.9 MB" {
		t.Fatal(s, e)
	}
}

func TestWhyTheScanCannotWork(t *testing.T) {
	var players int64 = 50_000_000 // int64, not int: int is only 32 bits on 32-bit platforms
	if got := int64(math.Round(game.ReadsPerSecond.Peak)) * players; got != 173_600_000_000 {
		t.Fatal(got)
	}
	if got := HumanBytes(float64(players * 100)); got != "5 GB" {
		t.Fatal(got)
	}
}

func TestRanksTiesAndBestScores(t *testing.T) {
	b := NewLeaderboard(1_000)
	for _, p := range []struct {
		name  string
		score int
	}{{"ada", 100}, {"bo", 250}, {"cy", 250}, {"di", 90}} {
		b.Submit(p.name, p.score)
	}
	ranks := func(names ...string) []int {
		var out []int
		for _, n := range names {
			r, _ := b.Rank(n)
			out = append(out, r)
		}
		return out
	}
	if got := ranks("bo", "cy", "ada", "di"); !slices.Equal(got, []int{1, 1, 3, 4}) {
		t.Fatal(got)
	}
	if changed, _ := b.Submit("ada", 80); changed {
		t.Fatal("a lower score changed ada's best")
	}
	if changed, _ := b.Submit("ada", 300); !changed {
		t.Fatal("a higher score was ignored")
	}
	if got := ranks("ada", "bo", "cy", "di"); !slices.Equal(got, []int{1, 2, 2, 4}) {
		t.Fatal(got)
	}
	if _, ok := b.Rank("nobody"); ok {
		t.Fatal("an unknown player has a rank")
	}
	if _, err := b.Submit("ed", 1_001); err == nil {
		t.Fatal("a score above the maximum was accepted")
	}
}

func TestAbout20StepsInsteadOfOnePerPlayer(t *testing.T) {
	const maxScore = 1_000_000
	b := NewLeaderboard(maxScore)
	scores := make([]int, 200_000)
	for i := range scores {
		scores[i] = (i * 7_919) % (maxScore + 1)
		b.Submit(fmt.Sprintf("p%d", i), scores[i])
	}
	for _, i := range []int{0, 1, 12_345, 199_999} {
		want, steps := RankByScan(scores, scores[i])
		if got, _ := b.Rank(fmt.Sprintf("p%d", i)); got != want || b.Steps > 20 || steps != 200_000 {
			t.Fatal(i, got, want, b.Steps, steps)
		}
	}
}
