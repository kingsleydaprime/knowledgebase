// Package balancing: how a load balancer picks a server, health checks that take a failing server out and put it
// back, and consistent hashing. The same numbers as the TypeScript lab.
package balancing

import (
	"cmp"
	"errors"
	"fmt"
	"math"
	"slices"
)

// Pick chooses a server from how many requests each is still working on.
type Pick func(outstanding []int, random func() float64) int

func RoundRobin() Pick {
	next := 0
	return func(outstanding []int, _ func() float64) int {
		chosen := next % len(outstanding)
		next++
		return chosen
	}
}

// LeastOutstanding picks the server with the fewest requests in progress; ties go to the lowest number.
func LeastOutstanding(outstanding []int, _ func() float64) int {
	return slices.Index(outstanding, slices.Min(outstanding))
}

func Random(outstanding []int, random func() float64) int {
	return int(random() * float64(len(outstanding)))
}

// TwoChoices picks two servers at random and takes the less busy one.
func TwoChoices(outstanding []int, random func() float64) int {
	a := int(random() * float64(len(outstanding)))
	b := int(random() * float64(len(outstanding)))
	if outstanding[b] < outstanding[a] {
		return b
	}
	return a
}

// Seeded is mulberry32, the same generator as week 1's lab.
func Seeded(seed uint32) func() float64 {
	a := seed
	return func() float64 {
		a += 0x6d2b79f5
		t := (a ^ a>>15) * (a | 1)
		t ^= t + (t^t>>7)*(t|61)
		return float64(t^t>>14) / 4294967296
	}
}

func percentile(sorted []float64, p float64) float64 {
	return sorted[max(1, int(math.Ceil(p/100*float64(len(sorted)))))-1]
}

type Latency struct{ Mean, P50, P99 float64 }

// Simulate sends random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms.
func Simulate(pick Pick, servers int, busy float64, requests int, seed uint32) Latency {
	random := Seeded(seed)
	meanWorkMs := 0.95*10 + 0.05*200
	gapMs := meanWorkMs / (busy * float64(servers))
	finishes := make([][]float64, servers) // per server: when each queued request ends
	outstanding := make([]int, servers)
	now, total := 0.0, 0.0
	times := make([]float64, 0, requests)
	for range requests {
		now += -gapMs * math.Log(1-random())
		for s, queue := range finishes {
			for len(queue) > 0 && queue[0] <= now {
				queue = queue[1:]
			}
			finishes[s], outstanding[s] = queue, len(queue)
		}
		s := pick(outstanding, random)
		workMs := 10.0
		if random() < 0.05 {
			workMs = 200
		}
		start := now
		if n := len(finishes[s]); n > 0 {
			start = max(now, finishes[s][n-1])
		}
		ends := start + workMs
		finishes[s] = append(finishes[s], ends)
		times = append(times, ends-now)
		total += ends - now
	}
	slices.Sort(times)
	return Latency{math.Round(total / float64(len(times))), math.Round(percentile(times, 50)), math.Round(percentile(times, 99))}
}

type Weighted struct {
	Name   string
	Weight int
}

// SmoothWeighted is nginx's method: each server gains its weight; the highest is chosen and pays the total.
// It takes a slice, not a map: Go maps have no order, and the order breaks ties.
func SmoothWeighted(servers []Weighted) func() string {
	total := 0
	for _, s := range servers {
		total += s.Weight
	}
	current := make([]int, len(servers))
	return func() string {
		best := 0
		for i, s := range servers {
			current[i] += s.Weight
			if current[i] > current[best] {
				best = i
			}
		}
		current[best] -= total
		return servers[best].Name
	}
}

// Health takes Fall failures in a row to mark a server down, and Rise successes in a row to bring it back.
type Health struct {
	Up         bool
	fall, rise int
	streak     int
}

func NewHealth(fall, rise int) *Health { return &Health{Up: true, fall: fall, rise: rise} }

func (h *Health) Record(ok bool) {
	if ok == h.Up {
		h.streak = 0
		return
	}
	h.streak++
	limit := h.rise
	if h.Up {
		limit = h.fall
	}
	if h.streak >= limit {
		h.Up, h.streak = !h.Up, 0
	}
}

type Server struct {
	Name   string
	Health *Health
}

var ErrNoHealthyServers = errors.New("no healthy servers: answer 503")

func PickHealthy(servers []Server, turn int) (string, error) {
	var up []string
	for _, s := range servers {
		if s.Health.Up {
			up = append(up, s.Name)
		}
	}
	if len(up) == 0 {
		return "", ErrNoHealthyServers
	}
	return up[turn%len(up)], nil
}

// Hash is FNV-1a then a mixing step. hash/fnv has FNV-1a too, but over bytes; this matches the other labs exactly.
func Hash(text string) uint32 {
	h := uint32(0x811c9dc5)
	for i := 0; i < len(text); i++ { // bytes, which for these ASCII keys are JavaScript's UTF-16 code units
		h = (h ^ uint32(text[i])) * 0x01000193
	}
	h = (h ^ h>>16) * 0x85ebca6b
	h = (h ^ h>>13) * 0xc2b2ae35
	return h ^ h>>16
}

func Modulo(key string, servers []string) string {
	return servers[Hash(key)%uint32(len(servers))]
}

type point struct {
	at     uint32
	server string
}

// HashRing places servers and keys on one circle of hash values; a key belongs to the first server clockwise.
type HashRing struct {
	points   []point
	replicas int
}

func NewHashRing(servers []string, replicas int) *HashRing {
	r := &HashRing{replicas: replicas}
	for _, s := range servers {
		r.Add(s)
	}
	return r
}

func (r *HashRing) Add(server string) {
	for i := range r.replicas {
		r.points = append(r.points, point{Hash(fmt.Sprintf("%s#%d", server, i)), server})
	}
	slices.SortStableFunc(r.points, func(a, b point) int { return cmp.Compare(a.at, b.at) })
}

func (r *HashRing) Remove(server string) {
	r.points = slices.DeleteFunc(r.points, func(p point) bool { return p.server == server })
}

func (r *HashRing) ServerFor(key string) string {
	h := Hash(key)
	i, _ := slices.BinarySearchFunc(r.points, h, func(p point, h uint32) int { return cmp.Compare(p.at, h) })
	return r.points[i%len(r.points)].server // past the last point, wrap round to the first
}
