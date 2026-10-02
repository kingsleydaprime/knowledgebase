package shop

import "testing"

func TestNaiveConsumerDoubleCounts(t *testing.T) {
	bus := &AtLeastOnceBus{}
	orders := NewOrders(bus, false)
	(&Payments{Bus: bus}).RecordSuccess("o1", 500_000)
	if orders.Paid["o1"] != 1_000_000 {
		t.Fatalf("paid = %d", orders.Paid["o1"])
	}
}

func TestIdempotentConsumer(t *testing.T) {
	bus := &AtLeastOnceBus{}
	orders := NewOrders(bus, true)
	payments := &Payments{Bus: bus}
	payments.RecordSuccess("o1", 500_000)
	payments.RecordSuccess("o1", 250_000)
	if orders.Paid["o1"] != 750_000 {
		t.Fatalf("paid = %d", orders.Paid["o1"])
	}
}
