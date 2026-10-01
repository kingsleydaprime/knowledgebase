// Package orders: State as a transition table, Observer as a slice of funcs,
// Iterator as a range-over-func sequence (Go 1.23+).
package orders

import (
	"fmt"
	"iter"
)

type Status string

const (
	Pending   Status = "pending"
	Paid      Status = "paid"
	Shipped   Status = "shipped"
	Delivered Status = "delivered"
	Cancelled Status = "cancelled"
)

var transitions = map[Status]map[string]Status{
	Pending: {"pay": Paid, "cancel": Cancelled},
	Paid:    {"ship": Shipped, "cancel": Cancelled},
	Shipped: {"deliver": Delivered},
}

type Listener func(orderID string, from, to Status)

type Order struct {
	ID        string
	Status    Status
	listeners []Listener
	history   []Status
}

func New(id string) *Order { return &Order{ID: id, Status: Pending, history: []Status{Pending}} }

func (o *Order) OnChange(l Listener) { o.listeners = append(o.listeners, l) }

func (o *Order) Apply(action string) error {
	next, ok := transitions[o.Status][action]
	if !ok {
		return fmt.Errorf("cannot %s an order that is %s", action, o.Status)
	}
	from := o.Status
	o.Status = next
	o.history = append(o.history, next)
	for _, l := range o.listeners {
		l(o.ID, from, next)
	}
	return nil
}

// History is an iterator: callers write `for s := range order.History()`.
func (o *Order) History() iter.Seq[Status] {
	return func(yield func(Status) bool) {
		for _, s := range o.history {
			if !yield(s) {
				return
			}
		}
	}
}
