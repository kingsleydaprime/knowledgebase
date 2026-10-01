package rates

import (
	"slices"
	"testing"
)

func TestStack(t *testing.T) {
	api := &FlakyAPI{Failures: 2}
	var log []string
	rates := Chain(api, Logging(&log), Caching(), Retrying(3))

	for range 2 {
		if v, err := rates.Rate("GBP", "NGN"); err != nil || v != 2000 {
			t.Fatalf("v=%d err=%v", v, err)
		}
	}
	if api.Calls != 3 || !slices.Equal(log, []string{"GBP->NGN = 2000", "GBP->NGN = 2000"}) {
		t.Fatalf("calls=%d log=%v", api.Calls, log)
	}
}

func TestTooManyFailures(t *testing.T) {
	if _, err := Chain(&FlakyAPI{Failures: 5}, Retrying(3)).Rate("GBP", "NGN"); err == nil {
		t.Fatal("expected an error")
	}
}
