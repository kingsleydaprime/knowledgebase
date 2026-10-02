// Package decoding: from a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab.
package decoding

import (
	"cmp"
	"math"
	"slices"
)

// Entry is one token and its score or probability. Slices keep a fixed order, so sampling is reproducible.
type Entry struct {
	Token string
	P     float64
}

// SeededRandom is mulberry32. math/rand/v2 has seeded generators too; this one gives the same
// numbers in every language in this companion.
func SeededRandom(seed uint32) func() float64 {
	a := seed
	return func() float64 {
		a += 0x6d2b79f5 // uint32 arithmetic wraps, exactly like JavaScript's >>> 0
		t := a
		t = (t ^ (t >> 15)) * (t | 1)
		t ^= t + (t^(t>>7))*(t|61)
		return float64(t^(t>>14)) / 4294967296
	}
}

// Softmax divides by the temperature, then exponentiates and normalises.
func Softmax(scores []Entry, temperature float64) []Entry {
	top := math.Inf(-1)
	for _, e := range scores {
		top = max(top, e.P/temperature) // subtract the max so Exp can't overflow
	}
	out := make([]Entry, len(scores))
	total := 0.0
	for i, e := range scores {
		out[i] = Entry{e.Token, math.Exp(e.P/temperature - top)}
		total += out[i].P
	}
	for i := range out {
		out[i].P /= total
	}
	return out
}

func byProbability(dist []Entry) []Entry {
	sorted := slices.Clone(dist)
	slices.SortStableFunc(sorted, func(x, y Entry) int { return cmp.Compare(y.P, x.P) }) // descending
	return sorted
}

// TopK keeps the k most likely tokens.
func TopK(dist []Entry, k int) []Entry {
	return renormalise(byProbability(dist)[:min(k, len(dist))])
}

// TopP keeps the smallest set of most likely tokens whose probabilities reach p.
func TopP(dist []Entry, p float64) []Entry {
	sorted := byProbability(dist)
	cumulative := 0.0
	for i, e := range sorted {
		cumulative += e.P
		if cumulative >= p {
			return renormalise(sorted[:i+1])
		}
	}
	return renormalise(sorted)
}

func renormalise(entries []Entry) []Entry {
	total := 0.0
	for _, e := range entries {
		total += e.P
	}
	out := make([]Entry, len(entries))
	for i, e := range entries {
		out[i] = Entry{e.Token, e.P / total}
	}
	return out
}

// Sample walks the cumulative probabilities until passing a random number in [0, 1).
func Sample(dist []Entry, random func() float64) string {
	r := random()
	for _, e := range dist {
		if r -= e.P; r < 0 {
			return e.Token
		}
	}
	return dist[len(dist)-1].Token
}

// Greedy always picks the most likely token: temperature 0.
func Greedy(dist []Entry) string {
	return byProbability(dist)[0].Token
}
