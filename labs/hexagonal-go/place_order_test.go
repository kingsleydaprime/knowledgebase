package shop_test

import (
	"errors"
	"testing"

	"shop/adapters/memory"
	"shop/domain"
)

func TestPlaceOrderWithInMemoryAdapters(t *testing.T) {
	orders := &memory.Orders{}
	order, err := domain.PlaceOrder(orders, memory.Payments{DeclineAbove: 1_000_000}, "o1", "c1", 250_000)
	if err != nil || !order.Paid || len(orders.Saved) != 1 {
		t.Fatalf("order=%+v err=%v saved=%d", order, err, len(orders.Saved))
	}
}

func TestDeclinedPaymentSavesNothing(t *testing.T) {
	orders := &memory.Orders{}
	_, err := domain.PlaceOrder(orders, memory.Payments{DeclineAbove: 100}, "o2", "c1", 250_000)
	if !errors.Is(err, domain.ErrDeclined) || len(orders.Saved) != 0 {
		t.Fatalf("err=%v saved=%d", err, len(orders.Saved))
	}
}
