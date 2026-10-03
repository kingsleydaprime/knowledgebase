// Package communication: what an API style costs, counted. REST requests and bytes, a GraphQL-style query with the
// N+1 problem and batching, Protocol Buffers' varints, and synchronous chains. The same numbers as the TypeScript lab.
package communication

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"
)

// Object is one decoded JSON object. The shop data is read without structs, so the query can pick any field.
type Object = map[string]any

// Db is a tiny shop database that counts its queries.
type Db struct {
	Queries int
	tables  map[string]map[string]Object
}

func NewDb(shopJSON []byte) (*Db, error) {
	var shop map[string][]Object
	if err := json.Unmarshal(shopJSON, &shop); err != nil {
		return nil, err
	}
	db := &Db{tables: map[string]map[string]Object{}}
	for table, rows := range shop {
		db.tables[table] = map[string]Object{}
		for _, row := range rows {
			db.tables[table][row["id"].(string)] = row
		}
	}
	return db, nil
}

// Find is one query for any number of rows: SELECT … WHERE id IN (…).
func (d *Db) Find(table string, ids ...string) []Object {
	d.Queries++
	rows := make([]Object, len(ids))
	for i, id := range ids {
		rows[i] = d.tables[table][id]
	}
	return rows
}

// RestAPI returns one whole resource per URL, and counts requests and bytes sent.
type RestAPI struct {
	db              *Db
	Requests, Bytes int
}

func NewRestAPI(db *Db) *RestAPI { return &RestAPI{db: db} }

func (a *RestAPI) Get(path string) (Object, error) {
	parts := strings.Split(path, "/") // "/orders/o1" → "", "orders", "o1"
	if len(parts) != 3 || (parts[1] != "orders" && parts[1] != "customers" && parts[1] != "products") {
		return nil, fmt.Errorf("404 %s", path)
	}
	body := a.db.Find(parts[1], parts[2])[0]
	if body == nil {
		return nil, fmt.Errorf("404 %s", path)
	}
	encoded, err := json.Marshal(body) // compact, like JSON.stringify; keys come out sorted, which doesn't change the length
	if err != nil {
		return nil, err
	}
	a.Requests++
	a.Bytes += len(encoded)
	return body, nil
}

// OrderScreenREST fetches the order (round trip 1), then its customer and products together (round trip 2).
func OrderScreenREST(api *RestAPI, orderID string) (screen Object, roundTrips int, err error) {
	order, err := api.Get("/orders/" + orderID)
	if err != nil {
		return nil, 0, err
	}
	customer, err := api.Get("/customers/" + order["customerId"].(string))
	if err != nil {
		return nil, 0, err
	}
	var items []any
	for _, raw := range order["items"].([]any) {
		item := raw.(Object)
		product, err := api.Get("/products/" + item["productId"].(string))
		if err != nil {
			return nil, 0, err
		}
		items = append(items, Object{"quantity": item["quantity"], "product": Object{"name": product["name"]}})
	}
	screen = Object{"id": order["id"], "totalPence": order["totalPence"], "customer": Object{"name": customer["name"]}, "items": items}
	return screen, 2, nil
}

// Selection names the fields wanted. A nil value is a plain field; a non-nil one selects inside an object or list.
type Selection map[string]Selection

// Resolvers fetch a field for every parent at one level of the query at once.
type Resolvers map[string]func(parents []Object) []any

var fieldTypes = map[string]string{"Order.customer": "Customer", "Order.items": "Item", "Item.product": "Product"}

// Execute runs a selection over every object at one level together, so each resolver sees the whole level.
func Execute(values []Object, sel Selection, resolvers Resolvers, typ string) []Object {
	outs := make([]Object, len(values))
	for i := range outs {
		outs[i] = Object{}
	}
	for field, sub := range sel {
		var children []any
		if resolve, ok := resolvers[typ+"."+field]; ok {
			children = resolve(values)
		} else {
			for _, v := range values {
				children = append(children, v[field])
			}
		}
		switch {
		case sub == nil:
			for i, child := range children {
				outs[i][field] = child
			}
		case len(children) > 0 && isList(children[0]): // a list field: all its elements form the next level
			var flat []Object
			for _, c := range children {
				for _, e := range c.([]any) {
					flat = append(flat, e.(Object))
				}
			}
			done := Execute(flat, sub, resolvers, fieldTypes[typ+"."+field])
			for i, c := range children {
				n := len(c.([]any))
				outs[i][field] = toAny(done[:n])
				done = done[n:]
			}
		default:
			objects := make([]Object, len(children))
			for i, c := range children {
				objects[i] = c.(Object)
			}
			for i, r := range Execute(objects, sub, resolvers, fieldTypes[typ+"."+field]) {
				outs[i][field] = r
			}
		}
	}
	return outs
}

func isList(v any) bool { _, ok := v.([]any); return ok }

func toAny(objects []Object) []any {
	out := make([]any, len(objects))
	for i, o := range objects {
		out[i] = o
	}
	return out
}

// NewResolvers makes one query per parent (the N+1 problem), or one query for the whole level.
func NewResolvers(db *Db, batched bool) Resolvers {
	field := func(table, key string) func([]Object) []any {
		return func(parents []Object) []any {
			out := make([]any, len(parents))
			if !batched {
				for i, p := range parents {
					out[i] = db.Find(table, p[key].(string))[0]
				}
				return out
			}
			var ids []string
			seen := map[string]bool{}
			for _, p := range parents {
				if id := p[key].(string); !seen[id] {
					seen[id] = true
					ids = append(ids, id)
				}
			}
			rows := map[string]Object{}
			for i, row := range db.Find(table, ids...) {
				rows[ids[i]] = row
			}
			for i, p := range parents {
				out[i] = rows[p[key].(string)]
			}
			return out
		}
	}
	return Resolvers{"Order.customer": field("customers", "customerId"), "Item.product": field("products", "productId")}
}

// Varint writes n base-128: 7 bits a byte, low bits first, top bit set if more follow.
func Varint(n uint64) []byte {
	var out []byte
	for n >= 0x80 {
		out = append(out, byte(n)|0x80)
		n >>= 7
	}
	return append(out, byte(n))
}

// EncodeOrderSummary encodes message OrderSummary { uint32 id = 1; string customer = 2; uint32 total_pence = 3; }.
func EncodeOrderSummary(id uint64, customer string, totalPence uint64) []byte {
	out := append(Varint(1<<3|0), Varint(id)...)
	out = append(out, Varint(2<<3|2)...)
	out = append(out, Varint(uint64(len(customer)))...) // len counts bytes, which is what protobuf wants
	out = append(out, customer...)
	out = append(out, Varint(3<<3|0)...)
	return append(out, Varint(totalPence)...)
}

type Call struct{ Availability, Ms float64 }

type Chain struct{ Availability, SequentialMs, ParallelMs float64 }

func ChainOf(calls []Call) (Chain, error) {
	if len(calls) == 0 {
		return Chain{}, errors.New("no calls")
	}
	c := Chain{Availability: 1}
	for _, call := range calls {
		c.Availability *= call.Availability
		c.SequentialMs += call.Ms
		c.ParallelMs = max(c.ParallelMs, call.Ms)
	}
	return c, nil
}
