package headers

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func get(origin string) *httptest.ResponseRecorder {
	req := httptest.NewRequest(http.MethodGet, "/me", nil)
	if origin != "" {
		req.Header.Set("Origin", origin)
	}
	rec := httptest.NewRecorder()
	Secure(http.HandlerFunc(Me)).ServeHTTP(rec, req)
	return rec
}

func TestSecurityHeaders(t *testing.T) {
	h := get("").Header()
	if h.Get("X-Content-Type-Options") != "nosniff" || !strings.Contains(h.Get("Content-Security-Policy"), "frame-ancestors 'none'") {
		t.Fatalf("headers = %v", h)
	}
}

func TestCORSAllowlist(t *testing.T) {
	if got := get("https://app.example.com").Header().Get("Access-Control-Allow-Origin"); got != "https://app.example.com" {
		t.Fatalf("allowed origin got %q", got)
	}
	evil := get("https://evil.example")
	if evil.Header().Get("Access-Control-Allow-Origin") != "" {
		t.Fatal("evil origin was allowed")
	}
	if !strings.Contains(evil.Body.String(), "ada@x.com") {
		t.Fatal("expected the body anyway: CORS is not access control")
	}
}
