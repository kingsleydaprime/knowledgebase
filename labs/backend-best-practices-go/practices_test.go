package practices

import (
	"bytes"
	"strings"
	"testing"
	"time"
)

func TestTokenBucket(t *testing.T) {
	l := NewLimiter()
	start := time.Date(2026, 10, 5, 9, 0, 0, 0, time.UTC)
	var got []bool
	for range 4 {
		ok, _ := Allow(l, start)
		got = append(got, ok)
	}
	if got[0] != true || got[1] != true || got[2] != true || got[3] != false {
		t.Fatalf("burst = %v, want three allowed then refused", got)
	}
	if _, wait := Allow(l, start); wait != 2*time.Second {
		t.Fatalf("retry after %v, want 2s", wait)
	}
	if ok, _ := Allow(l, start.Add(2*time.Second)); !ok {
		t.Fatal("refilled after 2s")
	}
}

func TestLogsAreJSONAndRedacted(t *testing.T) {
	var buf bytes.Buffer
	NewLogger(&buf).Info("payment.charged", "requestId", "req_1", "cardToken", "tok_visa_4242", "amountKobo", 500000)
	line := strings.TrimSpace(buf.String())
	want := `{"level":"INFO","msg":"payment.charged","requestId":"req_1","cardToken":"[redacted]","amountKobo":500000}`
	if line != want {
		t.Fatalf("\n got %s\nwant %s", line, want)
	}
}
