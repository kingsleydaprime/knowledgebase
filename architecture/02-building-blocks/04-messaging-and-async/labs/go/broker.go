// Package messaging: a small in-memory message broker with queues, topics, redelivery, a dead-letter queue, a
// partitioned log and load levelling. The same numbers as the TypeScript lab. The bounded queue is a channel.
package messaging

import (
	"fmt"
	"slices"
)

type Delivery struct {
	ID, Body, Key string
	Attempt       int
}

type stored struct {
	id, body, key string
	attempts      int
	visibleAt     int64
}

// Broker: subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery.
type Broker struct {
	now          func() int64 // milliseconds
	visibilityMs int64
	maxAttempts  int
	subscribers  map[string][]string
	queues, dead map[string][]*stored
	nextID       int
}

func NewBroker(now func() int64, visibilityMs int64, maxAttempts int) *Broker {
	return &Broker{now: now, visibilityMs: visibilityMs, maxAttempts: maxAttempts,
		subscribers: map[string][]string{}, queues: map[string][]*stored{}, dead: map[string][]*stored{}, nextID: 1}
}

func (b *Broker) Subscribe(topic, subscription string) {
	b.subscribers[topic] = append(b.subscribers[topic], subscription)
	b.queues[subscription], b.dead[subscription] = nil, nil
}

// Publish copies the message into every subscription. With no subscribers, nobody keeps it.
func (b *Broker) Publish(topic, body, key string) string {
	id := fmt.Sprintf("m%d", b.nextID)
	b.nextID++
	for _, s := range b.subscribers[topic] {
		b.queues[s] = append(b.queues[s], &stored{id: id, body: body, key: key})
	}
	return id
}

// Receive returns the oldest message no consumer is working on, and hides it for the visibility timeout.
func (b *Broker) Receive(subscription string) (Delivery, bool) {
	queue := b.queues[subscription]
	for i := 0; i < len(queue); i++ {
		m := queue[i]
		if m.visibleAt > b.now() {
			continue // a consumer has it
		}
		if m.attempts >= b.maxAttempts {
			b.dead[subscription] = append(b.dead[subscription], m) // poison: stop retrying it
			queue = slices.Delete(queue, i, i+1)
			b.queues[subscription] = queue
			i--
			continue
		}
		m.attempts++
		m.visibleAt = b.now() + b.visibilityMs
		return Delivery{m.id, m.body, m.key, m.attempts}, true
	}
	return Delivery{}, false
}

func (b *Broker) Ack(subscription, id string) {
	b.queues[subscription] = slices.DeleteFunc(b.queues[subscription], func(m *stored) bool { return m.id == id })
}

func (b *Broker) Depth(subscription string) int { return len(b.queues[subscription]) }

func (b *Broker) DeadLetters(subscription string) []string {
	var bodies []string
	for _, m := range b.dead[subscription] {
		bodies = append(bodies, m.body)
	}
	return bodies
}

// Idempotent remembers which message IDs it has processed and skips them the second time.
func Idempotent(handle func(body string), seen map[string]bool) func(Delivery) string {
	return func(d Delivery) string {
		if seen[d.ID] {
			return "duplicate"
		}
		handle(d.Body)
		seen[d.ID] = true
		return "processed"
	}
}

// PartitionFor is the same stable hash as the TypeScript lab.
func PartitionFor(key string, partitions int) int {
	h := uint32(0x811c9dc5)
	for i := 0; i < len(key); i++ {
		h = (h ^ uint32(key[i])) * 0x01000193
	}
	h = (h ^ h>>16) * 0x85ebca6b
	h = (h ^ h>>13) * 0xc2b2ae35
	return int((h ^ h>>16) % uint32(partitions))
}

// PartitionedLog is Kafka-like: messages are kept; each consumer group has its own offset per partition.
type PartitionedLog struct {
	partitions [][]string
	offsets    map[string][]int
}

func NewPartitionedLog(partitions int) *PartitionedLog {
	return &PartitionedLog{partitions: make([][]string, partitions), offsets: map[string][]int{}}
}

func (l *PartitionedLog) Append(key, body string) int {
	p := PartitionFor(key, len(l.partitions))
	l.partitions[p] = append(l.partitions[p], body)
	return p
}

func (l *PartitionedLog) Poll(group string, partition int) (string, bool) {
	offset := l.offsetsFor(group)[partition]
	if offset >= len(l.partitions[partition]) {
		return "", false
	}
	return l.partitions[partition][offset], true
}

func (l *PartitionedLog) Commit(group string, partition int) { l.offsetsFor(group)[partition]++ }

func (l *PartitionedLog) offsetsFor(group string) []int {
	if _, ok := l.offsets[group]; !ok {
		l.offsets[group] = make([]int, len(l.partitions)) // a new group starts at the beginning
	}
	return l.offsets[group]
}

type Levelled struct{ Served, Rejected, PeakDepth, ClearedAfterSeconds, MaxWaitSeconds int }

// LevelLoad compares turning away what doesn't fit each second with queueing it and working through it in order.
func LevelLoad(arrivals []int, perSecond int) Levelled {
	var r Levelled
	for _, a := range arrivals {
		r.Served += min(a, perSecond)
		r.Rejected += max(0, a-perSecond)
	}
	type batch struct{ second, count int }
	var waiting []batch
	depth := 0
	for second := 0; second < len(arrivals) || depth > 0; second++ {
		a := 0
		if second < len(arrivals) {
			a = arrivals[second]
		}
		if a > 0 {
			waiting = append(waiting, batch{second, a})
		}
		depth += a
		for capacity := perSecond; capacity > 0 && len(waiting) > 0; {
			n := min(capacity, waiting[0].count)
			waiting[0].count -= n
			capacity -= n
			depth -= n
			r.MaxWaitSeconds = max(r.MaxWaitSeconds, second-waiting[0].second)
			if waiting[0].count == 0 {
				waiting = waiting[1:]
			}
		}
		r.PeakDepth = max(r.PeakDepth, depth)
		if depth > 0 {
			r.ClearedAfterSeconds = second + 2
		}
	}
	return r
}

// TryPut is a non-blocking send on a buffered channel: false if it's full.
func TryPut[T any](q chan<- T, item T) bool {
	select {
	case q <- item:
		return true
	default:
		return false
	}
}
