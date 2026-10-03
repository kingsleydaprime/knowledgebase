// Package resilience: a tick-by-tick simulation of a cascade, Little's law, and a bulkhead.
// The same numbers as the TypeScript lab. One tick is 100 ms.
package resilience

import (
	"context"
	"errors"
	"math"
	"slices"
	"sync/atomic"
)

type Counts struct{ OK, Failed, TimedOut, Rejected, Unfinished int }

type Config struct {
	Pools                  map[string]string // endpoint → pool; the same pool name means a shared pool
	Order                  []string          // pool names in order: Go maps have none, and the order decides who starts first
	Sizes                  map[string]int
	QueueLimit             int // waiting requests per pool before new ones are turned away
	DependencyTimeoutTicks int
}

type Load struct {
	Ticks, ClientTimeoutTicks int
	ArrivalsPerTick           map[string]int
	ServiceTicks              map[string]int
}

type request struct {
	kind            string
	arrived, endsAt int
	failed          bool
}

var kinds = []string{"search", "profile"}

func Simulate(c Config, l Load) map[string]*Counts {
	counts := map[string]*Counts{"search": {}, "profile": {}}
	queues, running := map[string][]request{}, map[string][]request{}
	for t := range l.Ticks {
		for _, pool := range c.Order { // 1. finished work frees its worker
			running[pool] = slices.DeleteFunc(running[pool], func(r request) bool {
				if r.endsAt > t {
					return false
				}
				if r.failed {
					counts[r.kind].Failed++
				} else {
					counts[r.kind].OK++
				}
				return true
			})
		}
		for _, pool := range c.Order { // 2. callers who waited too long give up
			queues[pool] = slices.DeleteFunc(queues[pool], func(r request) bool {
				gaveUp := t-r.arrived >= l.ClientTimeoutTicks
				if gaveUp {
					counts[r.kind].TimedOut++
				}
				return gaveUp
			})
		}
		for _, kind := range kinds { // 3. new requests arrive, or are turned away
			pool := c.Pools[kind]
			for range l.ArrivalsPerTick[kind] {
				if len(queues[pool]) >= c.QueueLimit {
					counts[kind].Rejected++ // load shedding
				} else {
					queues[pool] = append(queues[pool], request{kind: kind, arrived: t})
				}
			}
		}
		for _, pool := range c.Order { // 4. free workers take requests, oldest first
			for len(running[pool]) < c.Sizes[pool] && len(queues[pool]) > 0 {
				r := queues[pool][0]
				queues[pool] = queues[pool][1:]
				needs, limit := l.ServiceTicks[r.kind], math.MaxInt
				if r.kind == "search" {
					limit = c.DependencyTimeoutTicks
				}
				r.endsAt, r.failed = t+min(needs, limit), needs > limit
				running[pool] = append(running[pool], r)
			}
		}
	}
	for _, pool := range c.Order {
		for _, r := range append(queues[pool], running[pool]...) {
			counts[r.kind].Unfinished++
		}
	}
	return counts
}

// WorkersNeeded is Little's law: requests in the system = arrival rate × time each one stays.
func WorkersNeeded(perSecond, seconds float64) float64 { return perSecond * seconds }

var ErrBulkheadFull = errors.New("bulkhead full")

// Bulkhead is a buffered channel used as a semaphore: a send takes a place, a receive gives it back.
// When a place frees up and a goroutine is blocked sending, the runtime hands the place straight to
// it, so a latecomer can't slip in: the bug from the main lesson can't happen here.
type Bulkhead struct {
	places   chan struct{}
	waiting  atomic.Int64
	maxQueue int64
}

func NewBulkhead(maxConcurrent, maxQueue int) *Bulkhead {
	return &Bulkhead{places: make(chan struct{}, maxConcurrent), maxQueue: int64(maxQueue)}
}

func (b *Bulkhead) Run(ctx context.Context, fn func() error) error {
	select {
	case b.places <- struct{}{}: // a free place, at once
	default:
		if b.waiting.Add(1) > b.maxQueue {
			b.waiting.Add(-1)
			return ErrBulkheadFull // a fast "no" now beats a slow failure later
		}
		select {
		case b.places <- struct{}{}:
			b.waiting.Add(-1)
		case <-ctx.Done(): // a caller who stops waiting leaves the queue
			b.waiting.Add(-1)
			return ctx.Err()
		}
	}
	defer func() { <-b.places }()
	return fn()
}
