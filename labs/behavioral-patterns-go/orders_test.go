package orders

import (
	"slices"
	"testing"
)

func TestObserversAndHistory(t *testing.T) {
	var audit []string
	o := New("o1")
	o.OnChange(func(_ string, from, to Status) { audit = append(audit, string(from)+"->"+string(to)) })
	for _, a := range []string{"pay", "ship", "deliver"} {
		if err := o.Apply(a); err != nil {
			t.Fatal(err)
		}
	}
	if !slices.Equal(audit, []string{"pending->paid", "paid->shipped", "shipped->delivered"}) {
		t.Fatalf("audit = %v", audit)
	}
	if got := slices.Collect(o.History()); !slices.Equal(got, []Status{Pending, Paid, Shipped, Delivered}) {
		t.Fatalf("history = %v", got)
	}
}

func TestIllegalTransition(t *testing.T) {
	calls := 0
	o := New("o2")
	o.OnChange(func(string, Status, Status) { calls++ })
	_ = o.Apply("pay")
	_ = o.Apply("ship")
	if err := o.Apply("cancel"); err == nil || o.Status != Shipped || calls != 2 {
		t.Fatalf("err=%v status=%s calls=%d", err, o.Status, calls)
	}
}
