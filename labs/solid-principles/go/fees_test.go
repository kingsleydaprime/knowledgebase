package fees

import "testing"

func TestBothDesignsAgree(t *testing.T) {
	if OpenRules["card"](10_000) != 290 {
		t.Fatal("open card fee")
	}
	if fee, ok := Fee(Card, 10_000); !ok || fee != 290 {
		t.Fatal("closed card fee")
	}
}

// A new constant compiles without touching Fee — it falls into default.
func TestForgottenCaseIsOnlyCaughtAtRuntime(t *testing.T) {
	const Ussd Method = Transfer + 1
	if _, ok := Fee(Ussd, 10_000); ok {
		t.Fatal("expected the unknown method to be rejected at runtime")
	}
}
