// Package cost: pricing in exact integer money, prefix diagnosis, canonical JSON, a cascade and
// latency percentiles. The same numbers as the TypeScript lab.
package cost

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math"
	"slices"
	"strings"
	"time"
)

// Picodollars are millionths of a millionth of a dollar. A token count times a price in
// micro-dollars per million tokens is a whole number of them, so sums are exact.
type Picodollars int64

func (p Picodollars) String() string { // dollars, without trailing zeros
	whole, frac := p/1e12, p%1e12
	return strings.TrimRight(strings.TrimRight(fmt.Sprintf("%d.%012d", whole, frac), "0"), ".")
}

// Price is in micro-dollars per million tokens: $2.50 is 2_500_000.
type Price struct{ Input, Output, CacheWrite, CacheRead int64 }

// Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them.
var Prices = map[string]Price{
	"claude-haiku-4-5":  {1_000_000, 5_000_000, 1_250_000, 100_000},
	"claude-sonnet-5-5": {2_000_000, 10_000_000, 2_500_000, 200_000},
	"claude-opus-5-5":   {4_000_000, 20_000_000, 5_000_000, 200_000},
	"local":             {},
}

// Usage: Input counts only input that was neither written to nor read from the cache.
type Usage struct{ Input, Output, CacheWrite, CacheRead int64 }

func Cost(u Usage, p Price) Picodollars {
	return Picodollars(u.Input*p.Input + u.Output*p.Output + u.CacheWrite*p.CacheWrite + u.CacheRead*p.CacheRead)
}

// BreakEvenCalls: caching n calls costs write + (n − 1) × read; not caching costs n × input.
func BreakEvenCalls(p Price) int64 {
	return (p.CacheWrite-p.CacheRead)/(p.Input-p.CacheRead) + 1 // integer division is the floor here
}

func SharedPrefix(a, b string) int {
	i := 0
	for i < len(a) && i < len(b) && a[i] == b[i] {
		i++
	}
	return i
}

// StableJSON: encoding/json already sorts map keys (struct fields keep their declared order).
// What it adds is HTML escaping: by default "<ticket>" becomes "\u003cticket\u003e", which Python and
// JavaScript don't do. Turn that off, and drop the newline Encode adds.
func StableJSON(value any) (string, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(value); err != nil {
		return "", err
	}
	return strings.TrimSuffix(buf.String(), "\n"), nil
}

type Tier struct {
	Name   string
	Cost   Picodollars // per call
	Answer func(input string) (string, error)
	Accept func(answer string) bool // the last tier's answer is used whatever this says
}

func Cascade(input string, tiers []Tier) (answer, by string, spent Picodollars, err error) {
	for i, t := range tiers {
		if answer, err = t.Answer(input); err != nil {
			return "", t.Name, spent, err
		}
		spent += t.Cost // a rejected answer was still paid for
		if i == len(tiers)-1 || t.Accept(answer) {
			return answer, t.Name, spent, nil
		}
	}
	return "", "", 0, fmt.Errorf("a cascade needs at least one tier")
}

// Percentile by nearest rank: the smallest value that at least p% of the values are less than or equal to.
func Percentile(values []time.Duration, p float64) time.Duration {
	sorted := slices.Sorted(slices.Values(values))
	return sorted[max(0, int(math.Ceil(p/100*float64(len(sorted))))-1)]
}

// TimeStream reads chunks until the channel closes, timing the first one separately.
func TimeStream(chunks <-chan string) (text string, ttft, total time.Duration) {
	started := time.Now()
	var b strings.Builder
	for chunk := range chunks {
		if b.Len() == 0 {
			ttft = time.Since(started)
		}
		b.WriteString(chunk)
	}
	return b.String(), ttft, time.Since(started)
}
