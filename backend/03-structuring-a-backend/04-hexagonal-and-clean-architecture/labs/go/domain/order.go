// Package domain holds the rules and the ports. It imports nothing from this module.
package domain

import "errors"

var ErrInvalidTotal = errors.New("total must be positive")
var ErrDeclined = errors.New("payment declined")

type Order struct {
	ID        string
	TotalKobo int64
	Paid      bool
}

// Ports: what the domain needs, declared here, where it's used.
type OrderRepository interface{ Save(Order) error }
type PaymentGateway interface {
	Charge(customerID string, kobo int64) (ok bool, err error)
}

// PlaceOrder is the use case. It depends only on the ports.
func PlaceOrder(orders OrderRepository, payments PaymentGateway, id, customerID string, kobo int64) (Order, error) {
	if kobo <= 0 {
		return Order{}, ErrInvalidTotal
	}
	ok, err := payments.Charge(customerID, kobo)
	if err != nil {
		return Order{}, err
	}
	if !ok {
		return Order{}, ErrDeclined
	}
	order := Order{ID: id, TotalKobo: kobo, Paid: true}
	return order, orders.Save(order)
}
