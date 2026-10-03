package communication

import (
	"encoding/json"
	"fmt"
	"os"
	"reflect"
	"testing"
)

var screenQuery = Selection{"id": nil, "totalPence": nil, "customer": {"name": nil}, "items": {"quantity": nil, "product": {"name": nil}}}

func shop(t *testing.T) *Db {
	data, err := os.ReadFile("../shared/shop.json")
	if err != nil {
		t.Fatal(err)
	}
	db, err := NewDb(data)
	if err != nil {
		t.Fatal(err)
	}
	return db
}

func size(t *testing.T, v any) int {
	b, err := json.Marshal(v)
	if err != nil {
		t.Fatal(err)
	}
	return len(b)
}

func TestRESTFiveRequestsTwoRoundTrips(t *testing.T) {
	api := NewRestAPI(shop(t))
	screen, roundTrips, err := OrderScreenREST(api, "o1")
	if err != nil {
		t.Fatal(err)
	}
	if screen["customer"].(Object)["name"] != "Gbenga Ali" || api.Requests != 5 || roundTrips != 2 || api.Bytes != 912 || size(t, screen) != 203 {
		t.Fatal(api.Requests, roundTrips, api.Bytes, size(t, screen))
	}
	if _, err := api.Get("/refunds/r1"); err == nil {
		t.Fatal("expected a 404")
	}
}

func TestAGraphQLStyleQueryOneRequestOnlyTheFieldsAskedFor(t *testing.T) {
	for _, batched := range []bool{false, true} {
		db := shop(t)
		order := db.Find("orders", "o1")[0]
		screen := Execute([]Object{order}, screenQuery, NewResolvers(db, batched), "Order")[0]
		want, _, _ := OrderScreenREST(NewRestAPI(shop(t)), "o1")
		if !reflect.DeepEqual(screen, want) || size(t, screen) != 203 {
			t.Fatal(screen)
		}
		if wantQueries := map[bool]int{false: 5, true: 3}[batched]; db.Queries != wantQueries {
			t.Fatalf("batched=%v: %d queries", batched, db.Queries)
		}
	}
}

func TestNPlusOne41QueriesOr3(t *testing.T) {
	for _, batched := range []bool{false, true} {
		db := shop(t)
		var ids []string
		for i := 1; i <= 10; i++ {
			ids = append(ids, fmt.Sprintf("o%d", i))
		}
		page := Execute(db.Find("orders", ids...), Selection{"id": nil, "customer": {"name": nil}, "items": {"product": {"name": nil}}}, NewResolvers(db, batched), "Order")
		if len(page) != 10 || page[0]["customer"].(Object)["name"] != "Gbenga Ali" {
			t.Fatal(page[0])
		}
		if want := map[bool]int{false: 41, true: 3}[batched]; db.Queries != want {
			t.Fatalf("batched=%v: %d queries", batched, db.Queries)
		}
	}
}

func TestVarintsAndTagsAsInTheProtobufDocumentation(t *testing.T) {
	for n, want := range map[uint64]string{1: "01", 150: "96 01", 300: "ac 02", 1 << 35: "80 80 80 80 80 01"} {
		if got := fmt.Sprintf("% x", Varint(n)); got != want {
			t.Errorf("%d: got %s, want %s", n, got, want)
		}
	}
	if got := fmt.Sprintf("% x", EncodeOrderSummary(150, "testing", 1)); got != "08 96 01 12 07 74 65 73 74 69 6e 67 18 01" {
		t.Fatal(got)
	}
}

func TestTheSameSummary17BytesAsProtobuf50AsJSON(t *testing.T) {
	summary := struct {
		ID         int    `json:"id"`
		Customer   string `json:"customer"`
		TotalPence int    `json:"totalPence"`
	}{1, "Gbenga Ali", 8996}
	if got := len(EncodeOrderSummary(1, "Gbenga Ali", 8996)); got != 17 || size(t, summary) != 50 {
		t.Fatal(got, size(t, summary))
	}
}

func TestASynchronousChain(t *testing.T) {
	c, _ := ChainOf([]Call{{0.999, 20}, {0.999, 20}, {0.999, 20}, {0.999, 20}, {0.999, 20}})
	p, _ := ChainOf([]Call{{1, 30}, {1, 50}, {1, 20}})
	if fmt.Sprintf("%.2f", c.Availability*100) != "99.50" || c.SequentialMs != 100 || p.ParallelMs != 50 {
		t.Fatal(c, p)
	}
	if _, err := ChainOf(nil); err == nil {
		t.Fatal("expected an error for no calls")
	}
}
