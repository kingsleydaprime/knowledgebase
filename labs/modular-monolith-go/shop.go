// Package shop: modules exchange events over a bus. Orders never imports payments.
package shop

import "fmt"

type PaymentSucceeded struct {
	EventID    string
	OrderID    string
	AmountKobo int64
}

type Bus interface {
	Publish(PaymentSucceeded)
	Subscribe(func(PaymentSucceeded))
}

type InProcessBus struct{ handlers []func(PaymentSucceeded) }

func (b *InProcessBus) Subscribe(h func(PaymentSucceeded)) { b.handlers = append(b.handlers, h) }
func (b *InProcessBus) Publish(e PaymentSucceeded) {
	for _, h := range b.handlers {
		h(e)
	}
}

// AtLeastOnceBus delivers every event twice — what a broker is allowed to do.
type AtLeastOnceBus struct{ InProcessBus }

func (b *AtLeastOnceBus) Publish(e PaymentSucceeded) {
	b.InProcessBus.Publish(e)
	b.InProcessBus.Publish(e)
}

type Payments struct {
	Bus Bus
	n   int
}

func (p *Payments) RecordSuccess(orderID string, kobo int64) {
	p.n++
	p.Bus.Publish(PaymentSucceeded{EventID: fmt.Sprintf("evt_%d", p.n), OrderID: orderID, AmountKobo: kobo})
}

type Orders struct {
	Paid map[string]int64
	seen map[string]bool
}

func NewOrders(bus Bus, idempotent bool) *Orders {
	o := &Orders{Paid: map[string]int64{}, seen: map[string]bool{}}
	bus.Subscribe(func(e PaymentSucceeded) {
		if idempotent {
			if o.seen[e.EventID] {
				return
			}
			o.seen[e.EventID] = true
		}
		o.Paid[e.OrderID] += e.AmountKobo
	})
	return o
}
