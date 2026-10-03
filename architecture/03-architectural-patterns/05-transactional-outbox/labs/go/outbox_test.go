package outbox

import (
	"errors"
	"slices"
	"strings"
	"testing"
)

func TestSaveThenPublishLosesTheEvent(t *testing.T) {
	db, err := OpenDB()
	if err != nil {
		t.Fatal(err)
	}
	b := &FakeBroker{}
	if err := PlaceOrderSaveThenPublish(db, b, "o1", 500_000, true); !errors.Is(err, ErrCrash) {
		t.Fatal(err)
	}
	if n, _ := CountOrders(db); n != 1 || len(b.Sent) != 0 {
		t.Fatal(n, b.Sent)
	}
}

func TestPublishThenSaveLeavesAPhantom(t *testing.T) {
	db, _ := OpenDB()
	b := &FakeBroker{}
	if err := PlaceOrderPublishThenSave(db, b, "o2", -1); err == nil || !strings.Contains(err.Error(), "CHECK constraint failed") {
		t.Fatal(err)
	}
	if n, _ := CountOrders(db); n != 0 || len(b.Sent) != 1 {
		t.Fatal(n, b.Sent)
	}
}

func TestOutboxACrashBeforeTheRelayLosesNothing(t *testing.T) {
	db, _ := OpenDB()
	b := &FakeBroker{}
	if err := PlaceOrderWithOutbox(db, "o3", 500_000); err != nil {
		t.Fatal(err)
	}
	first, _ := Relay(db, b, false)
	second, _ := Relay(db, b, false)
	if first != 1 || second != 0 || !slices.Equal(b.Sent, []Event{{"evt-o3", "OrderPlaced", "o3"}}) {
		t.Fatal(first, second, b.Sent)
	}
}

func TestOutboxAFailedOrderRollsBackItsEvent(t *testing.T) {
	db, _ := OpenDB()
	if err := PlaceOrderWithOutbox(db, "o4", -1); err == nil || !strings.Contains(err.Error(), "CHECK constraint failed") {
		t.Fatal(err)
	}
	n, _ := CountOrders(db)
	sent, _ := Relay(db, &FakeBroker{}, false)
	if n != 0 || sent != 0 {
		t.Fatal(n, sent)
	}
}

func TestRelayCrashSendsTwiceConsumerAppliesOnce(t *testing.T) {
	db, _ := OpenDB()
	b := &FakeBroker{}
	PlaceOrderWithOutbox(db, "o5", 500_000)
	if _, err := Relay(db, b, true); !errors.Is(err, ErrCrash) {
		t.Fatal(err)
	}
	Relay(db, b, false)
	var c IdempotentConsumer
	var results []string
	for _, e := range b.Sent {
		results = append(results, c.Handle(e))
	}
	if len(b.Sent) != 2 || !slices.Equal(results, []string{"applied", "duplicate"}) || !slices.Equal(c.Applied, []string{"o5"}) {
		t.Fatal(b.Sent, results, c.Applied)
	}
}
