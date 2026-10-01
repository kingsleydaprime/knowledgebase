package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func post(t *testing.T, body string) *httptest.ResponseRecorder {
	t.Helper()
	rec := httptest.NewRecorder()
	newMux().ServeHTTP(rec, httptest.NewRequest(http.MethodPost, "/orders", strings.NewReader(body)))
	return rec
}

func TestPlaceOrderThroughTheCompositionRoot(t *testing.T) {
	rec := post(t, `{"userId":"u1","totalKobo":500000}`)
	if rec.Code != http.StatusCreated {
		t.Fatalf("status = %d, body = %s", rec.Code, rec.Body)
	}
	if got := strings.TrimSpace(rec.Body.String()); got != `{"id":1,"userId":"u1","totalKobo":500000}` {
		t.Fatalf("body = %s", got)
	}
}

func TestUnknownUserIsRejected(t *testing.T) {
	if rec := post(t, `{"userId":"nobody","totalKobo":1}`); rec.Code != http.StatusUnprocessableEntity {
		t.Fatalf("status = %d", rec.Code)
	}
}
