// Package approach: back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about
// 20 steps. The same numbers as the TypeScript lab.
package approach

import (
	"fmt"
	"strconv"
)

const SecondsPerDay = 86_400

// Assumptions are float64 so the arithmetic matches JavaScript's numbers; an estimate is never exact anyway.
type Assumptions struct {
	DailyActiveUsers, WritesPerUserPerDay, ReadsPerUserPerDay, PeakToAverage float64
	BytesPerWrite, KeptForDays, BytesPerRead                                 float64
}

type Rate struct{ Average, Peak float64 }

type Estimate struct {
	WritesPerSecond, ReadsPerSecond                       Rate
	ReadsPerWrite, StorageBytes, PeakEgressBytesPerSecond float64
}

func Compute(a Assumptions) Estimate {
	writes := a.DailyActiveUsers * a.WritesPerUserPerDay / SecondsPerDay
	reads := a.DailyActiveUsers * a.ReadsPerUserPerDay / SecondsPerDay
	return Estimate{
		WritesPerSecond:          Rate{writes, writes * a.PeakToAverage},
		ReadsPerSecond:           Rate{reads, reads * a.PeakToAverage},
		ReadsPerWrite:            a.ReadsPerUserPerDay / a.WritesPerUserPerDay,
		StorageBytes:             a.DailyActiveUsers * a.WritesPerUserPerDay * a.BytesPerWrite * a.KeptForDays,
		PeakEgressBytesPerSecond: reads * a.PeakToAverage * a.BytesPerRead,
	}
}

// HumanBytes gives two significant figures in powers of 1,000: 912,500,000,000 → "910 GB".
func HumanBytes(n float64) string {
	units := []string{"B", "KB", "MB", "GB", "TB", "PB"}
	i := 0
	for n >= 1000 && i < len(units)-1 {
		n /= 1000
		i++
	}
	// 'g' with 2 figures gives "9.1e+02" for 910; parse it back and print the shortest plain form.
	rounded, _ := strconv.ParseFloat(strconv.FormatFloat(n, 'g', 2, 64), 64)
	return fmt.Sprintf("%s %s", strconv.FormatFloat(rounded, 'f', -1, 64), units[i])
}

// Leaderboard keeps each player's best score, and a Fenwick tree of how many players have each score.
type Leaderboard struct {
	maxScore int
	best     map[string]int
	tree     []int
	Steps    int // the work the last Rank did
}

func NewLeaderboard(maxScore int) *Leaderboard {
	return &Leaderboard{maxScore: maxScore, best: map[string]int{}, tree: make([]int, maxScore+2)}
}

func (b *Leaderboard) Players() int { return len(b.best) }

// Submit records a score; only a player's best counts. A score can't be 2.5: the int type rules it out.
func (b *Leaderboard) Submit(player string, score int) (bool, error) {
	if score < 0 || score > b.maxScore {
		return false, fmt.Errorf("score must be from 0 to %d, got %d", b.maxScore, score)
	}
	old, seen := b.best[player]
	if seen && score <= old {
		return false, nil
	}
	if seen {
		b.add(old, -1)
	}
	b.add(score, +1)
	b.best[player] = score
	return true, nil
}

// Rank is 1 + the number of players with a strictly higher best; ok is false for an unknown player.
func (b *Leaderboard) Rank(player string) (rank int, ok bool) {
	score, ok := b.best[player]
	if !ok {
		return 0, false
	}
	b.Steps = 0
	return 1 + b.Players() - b.countAtMost(score), true
}

func (b *Leaderboard) add(score, delta int) {
	for i := score + 1; i < len(b.tree); i += i & -i {
		b.tree[i] += delta
	}
}

func (b *Leaderboard) countAtMost(score int) int {
	count := 0
	for i := score + 1; i > 0; i -= i & -i {
		count += b.tree[i]
		b.Steps++
	}
	return count
}

// RankByScan is the obvious way: look at every player.
func RankByScan(scores []int, mine int) (rank, steps int) {
	higher := 0
	for _, s := range scores {
		steps++
		if s > mine {
			higher++
		}
	}
	return 1 + higher, steps
}
