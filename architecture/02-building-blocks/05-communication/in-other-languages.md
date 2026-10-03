# Communication in Other Languages

> **[Intermediate]** · A companion to [[architecture/02-building-blocks/05-communication/index|communication]], which counts what one screen costs over REST and over a GraphQL-style query, shows the N+1 problem and batching, encodes Protocol Buffers' varints by hand, and works out synchronous chains. This page does the same in Python, Go, Java, Rust and C#, with the same numbers in every language, reading the same shop data. Two things change more than you'd expect. First, *when* a batching loader fires depends on how the language runs concurrent work. Second, "how many bytes is this JSON?" depends on the language's serialiser defaults: the same screen is 203 bytes in five languages and 225 in Python's default.

## Before you start

You can already:

- Count a screen's requests, round trips and bytes, explain the N+1 problem and DataLoader, and encode a varint → [[architecture/02-building-blocks/05-communication/index|the main lesson]].
- Read and write JSON in at least one of the languages here.

After this lesson you will be able to:

1. Say when your language's DataLoader sends its batch, and why it can't simply copy JavaScript's approach.
2. Name the defaults in your language's JSON serialiser that change what's sent: spaces, key order, escaping.
3. Encode a protobuf string field correctly, using UTF-8 bytes rather than the language's string length.

## The kid version

A class is collecting lunch orders to phone through to the kitchen in one call. In one class, the teacher waits until everyone at the current table has spoken, then phones. In another, the teacher phones after a set ten seconds, whoever has spoken by then. In a third, the teacher phones once the whole row has answered. All three save the kitchen from forty separate calls; they just decide differently when "everyone" has finished.

**Where the analogy stops working.** A teacher can look around the room. A program has to decide "everyone has asked" from how its code runs: the event loop going quiet, a timer, or the query being worked through one level at a time. Choosing wrong means either a batch sent too early, so more queries, or one held too long, so slower answers.

## 1. The tools, by ecosystem

| Language | JSON | GraphQL server and batching | gRPC and protobuf |
|---|---|---|---|
| TypeScript | `JSON` built in | graphql-js, Apollo Server; `dataloader` | `@grpc/grpc-js`, protobuf-es |
| Python | `json` built in | Strawberry, Graphene; DataLoader on asyncio | `grpcio`, `protobuf` |
| Go | `encoding/json` built in | gqlgen; dataloader packages that wait a few milliseconds | grpc-go, `google.golang.org/protobuf` |
| Java | **none built in**: Jackson | graphql-java, Spring for GraphQL; java-dataloader, dispatched per level | grpc-java, protobuf-java |
| Rust | the `serde_json` crate | async-graphql (DataLoader built in), Juniper | tonic, prost |
| C# | `System.Text.Json` built in | Hot Chocolate (DataLoader built in) | Grpc.AspNetCore, Google.Protobuf |

For REST, every language has a mature server framework, and none of the costs in the main lesson depend on which you use. C and C++ have gRPC and protobuf (protobuf is written in C++), but no lab here: the costs being counted are the same.

## 2. What changes between languages

### When does a batching loader send its batch?

A DataLoader collects keys and sends them as one query, so it has to decide when everyone who will ask has asked.

- **JavaScript** waits for the event loop: every resolver that's ready runs until it hits an `await`, and only then does the queued `setImmediate` fire with all their keys. Python's asyncio libraries do the same with the event loop.
- **Threads** have no moment when "everything ready has run", because other threads may be about to ask. Go dataloader packages instead wait a few milliseconds and send whatever has arrived, trading a little latency for the batch.
- **graphql-java** knows the query's shape, so it sends the loaders' batches when it has finished resolving one level of the query.

The labs here all use that last approach, **batching by level**: `execute` passes a resolver every object at one depth at once, such as all ten orders or all thirty items, so the resolver can make one query. It needs no timers and no event loop, so it works the same in every language, and gives the main lesson's counts: 5 and 3 for one order, 41 and 3 for ten.

### What the JSON bytes are depends on the serialiser

The main lesson counts 912 bytes for the REST screen and 203 for the GraphQL one, measured with `JSON.stringify`. Each language's serialiser has its own defaults:

- **Python's** `json.dumps` puts a space after every `,` and `:`, so the same screen is **225 bytes** (the lab checks it). Pass `separators=(",", ":")` for compact output.
- **Go's** `json.Marshal` is compact, but writes map keys in sorted order and escapes `<`, `>` and `&` as `<` and so on, so HTML-sensitive text grows.
- **C#'s** `System.Text.Json` is compact, but by default escapes every non-ASCII character: `é` becomes six characters, `é`.
- **Java** has no JSON in its standard library; Jackson is compact by default and keeps fields in order.
- **Rust's** `serde_json` is compact; with the `preserve_order` feature, fields keep their order.

The shop data is all ASCII, so the labs agree. With customer names like `Adaeze Ọkọnkwọ`, the byte counts would differ between languages, and none of them would be "the JSON size". Before comparing payload sizes across services, compare their serialiser settings.

### Untyped JSON in typed languages

A GraphQL query can ask for any field, so the labs keep the shop data as untyped JSON trees: Go's `map[string]any` with type assertions, Jackson's `JsonNode`, `serde_json::Value`, C#'s `JsonNode`. Real servers don't: gqlgen, async-graphql and Hot Chocolate generate or check typed classes from the schema. One C# surprise: a `JsonNode` can belong to only one parent, so copying a value from the order into the screen needs `DeepClone()`.

### A protobuf string's length is its UTF-8 bytes

A string field is written as its length, then its bytes, and the length must be in **UTF-8 bytes**. Each language's "length of a string" means something different:

- **Go's** `len(s)` and **Rust's** `s.len()` count UTF-8 bytes, which is right.
- **Python's** `len(s)` counts code points, and **Java's** `length()` and **C#'s** `Length` count UTF-16 units. For `café` they say 4, but it's 5 bytes.

The labs encode to UTF-8 first (`encode("utf-8")`, `getBytes(UTF_8)`, `Encoding.UTF8.GetBytes`) and take that length.

### Varints and the sign bit

A varint shifts right by 7 until nothing is left. On a signed 64-bit number, Java's `>>` copies the sign bit in, so a negative number would never reach zero; the lab uses `>>>`, which shifts in zeros, and rejects negatives. Go, Rust and C# use unsigned types (`uint64`, `u64`, `ulong`), so there's no sign to worry about. Python's ints have no fixed size, so the lab rejects negatives explicitly. In real protobuf, a negative `int32` is sent as a 10-byte varint, which is why schemas use `sint32` for values that are often negative: it maps them to small positive numbers first.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| the REST order screen | 5 requests, 2 round trips, 912 bytes sent, 203 used |
| the same screen as a GraphQL-style query | identical to REST's, 203 bytes; 5 queries, or 3 batched |
| ten orders with customers and products | 41 queries, or 3 batched |
| varints of 1, 150, 300, 2³⁵ | `01`, `96 01`, `ac 02`, `80 80 80 80 80 01` |
| id = 150, customer = "testing", total = 1 | `08 96 01 12 07 74 65 73 74 69 6e 67 18 01` |
| the order summary | 17 bytes as protobuf, 50 as compact JSON |
| five 99.9% services, 20 ms each | 99.50%, 100 ms in a row; max(30, 50, 20) = 50 ms in parallel |

## Terms used in this lesson

1. **Batching by level**: This is resolving one depth of a query for all its objects at once, so each resolver can fetch everything that level needs in one query.
2. **Serialiser**: This is the code that turns an object into text or bytes to send, such as a JSON library.
3. **Code point**: This is one Unicode character's number. `é` is one code point, but two UTF-8 bytes.
4. **Untyped JSON tree**: This is JSON held as nested generic maps and lists, rather than decoded into classes, so any field can be read by name.
5. **ZigZag encoding**: This is protobuf's way of turning signed numbers into unsigned ones (0, −1, 1, −2 … become 0, 1, 2, 3 …) so that small negative numbers get short varints. `sint32` and `sint64` use it.

## 4. Python

The shop is plain dicts. `compact` gives `json.dumps` the separators that match `JSON.stringify`, and the test shows the default's 225 bytes too. `execute` batches by level, and `resolvers` builds either a one-row-per-parent resolver or an all-at-once one, using `dict.fromkeys` to keep each ID once, in order. `varint` uses `bytearray`, and the test compares against `bytes.hex(" ")`.

```python
"""What an API style costs, counted: REST requests and bytes, a GraphQL-style query with the N+1 problem and
batching, Protocol Buffers' varints, and synchronous chains. The same numbers as the TypeScript lab."""
import json
import math
from typing import Callable

Selection = dict  # field → True, or a nested selection
FIELD_TYPES = {"Order.customer": "Customer", "Order.items": "Item", "Item.product": "Product"}


def compact(value) -> str:
    """JSON as JavaScript's JSON.stringify writes it. json.dumps puts a space after every ',' and ':' by default."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


class Db:
    """A tiny shop database that counts its queries."""

    def __init__(self, shop: dict):
        self.queries = 0
        self.customers = {c["id"]: c for c in shop["customers"]}
        self.products = {p["id"]: p for p in shop["products"]}
        self.orders = {o["id"]: o for o in shop["orders"]}

    def find(self, table: str, ids: list[str]) -> list[dict]:
        """One query for any number of rows: SELECT … WHERE id IN (…)."""
        self.queries += 1
        rows = getattr(self, table)
        return [rows[i] for i in ids]


class RestApi:
    """One resource per URL, always returned whole. Counts requests and bytes sent."""

    def __init__(self, db: Db):
        self.db, self.requests, self.bytes = db, 0, 0

    def get(self, path: str) -> dict:
        _, kind, id_ = path.split("/")
        if kind not in ("orders", "customers", "products"):
            raise LookupError(f"404 {path}")
        body = self.db.find(kind, [id_])[0]
        self.requests += 1
        self.bytes += len(compact(body))
        return body


def order_screen_rest(api: RestApi, order_id: str) -> tuple[dict, int]:
    """The order first (round trip 1), then its customer and products together (round trip 2)."""
    order = api.get(f"/orders/{order_id}")
    customer = api.get(f"/customers/{order['customerId']}")
    products = [api.get(f"/products/{i['productId']}") for i in order["items"]]
    screen = {
        "id": order["id"],
        "totalPence": order["totalPence"],
        "customer": {"name": customer["name"]},
        "items": [{"quantity": i["quantity"], "product": {"name": p["name"]}} for i, p in zip(order["items"], products)],
    }
    return screen, 2


Resolvers = dict[str, Callable[[list[dict]], list]]


def execute(values: list[dict], selection: Selection, resolvers: Resolvers, type_: str) -> list[dict]:
    """Runs a selection over every object at one level of the query at once, so a resolver sees them all."""
    outs: list[dict] = [{} for _ in values]
    for field, sub in selection.items():
        resolver = resolvers.get(f"{type_}.{field}")
        children = resolver(values) if resolver else [v[field] for v in values]
        if sub is True:
            for out, child in zip(outs, children):
                out[field] = child
        elif children and isinstance(children[0], list):  # a list field: all its elements form the next level
            flat = [c for cs in children for c in cs]
            done = iter(execute(flat, sub, resolvers, FIELD_TYPES[f"{type_}.{field}"]))
            for out, cs in zip(outs, children):
                out[field] = [next(done) for _ in cs]
        else:
            for out, result in zip(outs, execute(children, sub, resolvers, FIELD_TYPES[f"{type_}.{field}"])):
                out[field] = result
    return outs


def resolvers(db: Db, batched: bool) -> Resolvers:
    """One query per parent (the N+1 problem), or one query for the whole level."""
    def one_each(table: str, key: str):
        return lambda parents: [db.find(table, [p[key]])[0] for p in parents]

    def all_at_once(table: str, key: str):
        def resolve(parents):
            ids = list(dict.fromkeys(p[key] for p in parents))  # each ID once, in first-seen order
            rows = dict(zip(ids, db.find(table, ids)))
            return [rows[p[key]] for p in parents]
        return resolve

    make = all_at_once if batched else one_each
    return {"Order.customer": make("customers", "customerId"), "Item.product": make("products", "productId")}


def varint(n: int) -> bytes:
    """Base-128: 7 bits a byte, low bits first, top bit set if more follow. Python ints never overflow."""
    if n < 0:
        raise ValueError("varint takes a whole number from 0")
    out = bytearray()
    while True:
        byte, n = n & 0x7F, n >> 7
        out.append(byte | 0x80 if n else byte)
        if not n:
            return bytes(out)


def encode_order_summary(id_: int, customer: str, total_pence: int) -> bytes:
    text = customer.encode("utf-8")
    return (varint(1 << 3 | 0) + varint(id_)
            + varint(2 << 3 | 2) + varint(len(text)) + text
            + varint(3 << 3 | 0) + varint(total_pence))


def chain(services: list[tuple[float, float]]) -> dict:
    """(availability, ms) for each call in a row."""
    return {"availability": math.prod(a for a, _ in services),
            "sequential_ms": sum(ms for _, ms in services),
            "parallel_ms": max(ms for _, ms in services)}
```

```python
import json
import pathlib
import unittest

from communication import Db, RestApi, chain, compact, encode_order_summary, execute, order_screen_rest, resolvers, varint

SHOP = json.loads((pathlib.Path(__file__).parent.parent / "shared" / "shop.json").read_text())
ORDER_SCREEN = {"id": True, "totalPence": True, "customer": {"name": True}, "items": {"quantity": True, "product": {"name": True}}}


class Communication(unittest.TestCase):
    def test_rest_five_requests_two_round_trips(self):
        api = RestApi(Db(SHOP))
        screen, round_trips = order_screen_rest(api, "o1")
        self.assertEqual(screen["customer"]["name"], "Gbenga Ali")
        self.assertEqual([f"{i['quantity']} × {i['product']['name']}" for i in screen["items"]], ["1 × Kettle", "1 × Toaster", "2 × Mug set"])
        self.assertEqual((api.requests, round_trips, api.bytes), (5, 2, 912))
        self.assertEqual(len(compact(screen)), 203)
        self.assertEqual(len(json.dumps(screen)), 225)  # the default separators add 22 spaces

    def test_a_graphql_style_query_one_request_only_the_fields_asked_for(self):
        for batched in [False, True]:
            db = Db(SHOP)
            order = db.find("orders", ["o1"])[0]
            [screen] = execute([order], ORDER_SCREEN, resolvers(db, batched), "Order")
            self.assertEqual(screen, order_screen_rest(RestApi(Db(SHOP)), "o1")[0])
            self.assertEqual(len(compact(screen)), 203)
            self.assertEqual(db.queries, 3 if batched else 5)

    def test_n_plus_one_41_queries_or_3(self):
        for batched in [False, True]:
            db = Db(SHOP)
            orders = db.find("orders", [o["id"] for o in SHOP["orders"]])
            page = execute(orders, {"id": True, "customer": {"name": True}, "items": {"product": {"name": True}}}, resolvers(db, batched), "Order")
            self.assertEqual((len(page), page[0]["customer"]["name"]), (10, "Gbenga Ali"))
            self.assertEqual(db.queries, 3 if batched else 41)

    def test_varints_and_tags_as_in_the_protobuf_documentation(self):
        self.assertEqual(varint(1), b"\x01")
        self.assertEqual(varint(150), b"\x96\x01")
        self.assertEqual(varint(300), b"\xac\x02")
        self.assertEqual(varint(2**35), b"\x80\x80\x80\x80\x80\x01")
        with self.assertRaises(ValueError):
            varint(-1)
        self.assertEqual(encode_order_summary(150, "testing", 1).hex(" "), "08 96 01 12 07 74 65 73 74 69 6e 67 18 01")

    def test_the_same_summary_17_bytes_as_protobuf_50_as_json(self):
        self.assertEqual(len(encode_order_summary(1, "Gbenga Ali", 8996)), 17)
        self.assertEqual(len(compact({"id": 1, "customer": "Gbenga Ali", "totalPence": 8996})), 50)

    def test_a_synchronous_chain(self):
        c = chain([(0.999, 20)] * 5)
        self.assertEqual(f"{c['availability'] * 100:.2f}", "99.50")
        self.assertEqual(c["sequential_ms"], 100)
        self.assertEqual(chain([(1, 30), (1, 50), (1, 20)])["parallel_ms"], 50)


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/05-communication/labs/python). `python3 labs/run.py communication/python`.

## 5. Go

The shop decodes into `map[string]any`, so reading a field takes a type assertion such as `order["customerId"].(string)`. `Selection` is a map whose `nil` value means a plain field. `Varint` works on `uint64`, and `len(customer)` is already the UTF-8 byte count. The test prints bytes with `fmt.Sprintf("% x")`.

```go
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
```

```go
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
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/05-communication/labs/go). `python3 labs/run.py communication/go`.

## 6. Java

Jackson 3 reads the shop into `JsonNode`s; `check.sh` downloads it once from Maven Central, as the other Java labs with libraries do. `Selection.of` builds an ordered selection, with `Selection.FIELD` for a plain field. `varint` uses `>>>` on a `long`. `encodeOrderSummary` takes the UTF-8 bytes of the name. `HexFormat` prints the bytes.

```java
package communication;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ArrayNode;
import tools.jackson.databind.node.ObjectNode;

/** What an API style costs, counted. The same numbers as the TypeScript lab. Java has no JSON built in: this uses Jackson. */
public final class Communication {
    private Communication() {}

    static final JsonMapper JSON = JsonMapper.shared();

    /** JSON as JSON.stringify writes it: Jackson is compact by default and keeps the fields in order. */
    public static int size(JsonNode node) {
        return JSON.writeValueAsString(node).length();
    }

    /** A tiny shop database that counts its queries. */
    public static final class Db {
        public int queries;
        private final Map<String, Map<String, JsonNode>> tables = new HashMap<>();

        public Db(JsonNode shop) {
            for (String table : List.of("customers", "products", "orders")) {
                Map<String, JsonNode> rows = new HashMap<>();
                for (JsonNode row : shop.get(table)) rows.put(row.get("id").asString(), row);
                tables.put(table, rows);
            }
        }

        /** One query for any number of rows: SELECT … WHERE id IN (…). */
        public List<JsonNode> find(String table, List<String> ids) {
            queries++;
            return ids.stream().map(tables.get(table)::get).toList();
        }
    }

    /** One whole resource per URL. Counts requests and bytes sent. */
    public static final class RestApi {
        private final Db db;
        public int requests;
        public int bytes;

        public RestApi(Db db) {
            this.db = db;
        }

        public JsonNode get(String path) {
            String[] parts = path.split("/"); // "/orders/o1" → "", "orders", "o1"
            if (parts.length != 3 || !List.of("orders", "customers", "products").contains(parts[1])) {
                throw new IllegalArgumentException("404 " + path);
            }
            JsonNode body = db.find(parts[1], List.of(parts[2])).getFirst();
            requests++;
            bytes += size(body);
            return body;
        }
    }

    public record Fetched(ObjectNode screen, int roundTrips) {}

    /** The order (round trip 1), then its customer and products together (round trip 2). */
    public static Fetched orderScreenRest(RestApi api, String orderId) {
        JsonNode order = api.get("/orders/" + orderId);
        JsonNode customer = api.get("/customers/" + order.get("customerId").asString());
        ObjectNode screen = JSON.createObjectNode();
        screen.set("id", order.get("id"));
        screen.set("totalPence", order.get("totalPence"));
        screen.putObject("customer").set("name", customer.get("name"));
        ArrayNode items = screen.putArray("items");
        for (JsonNode item : order.get("items")) {
            JsonNode product = api.get("/products/" + item.get("productId").asString());
            ObjectNode line = items.addObject();
            line.set("quantity", item.get("quantity"));
            line.putObject("product").set("name", product.get("name"));
        }
        return new Fetched(screen, 2);
    }

    /** Fields wanted, in order. An empty selection is a plain field; a non-empty one selects inside it. */
    public record Selection(Map<String, Selection> fields) {
        public static final Selection FIELD = new Selection(Map.of());

        public static Selection of(Object... nameThenSelection) {
            var fields = new LinkedHashMap<String, Selection>();
            for (int i = 0; i < nameThenSelection.length; i += 2) {
                fields.put((String) nameThenSelection[i], (Selection) nameThenSelection[i + 1]);
            }
            return new Selection(fields);
        }
    }

    /** A resolver fetches one field for every parent at one level of the query at once. */
    public interface Resolver extends Function<List<JsonNode>, List<JsonNode>> {}

    private static final Map<String, String> FIELD_TYPES = Map.of("Order.customer", "Customer", "Order.items", "Item", "Item.product", "Product");

    /** Runs a selection over every object at one level together, so each resolver sees the whole level. */
    public static List<ObjectNode> execute(List<JsonNode> values, Selection selection, Map<String, Resolver> resolvers, String type) {
        List<ObjectNode> outs = values.stream().map(v -> JSON.createObjectNode()).toList();
        selection.fields().forEach((field, sub) -> {
            Resolver resolver = resolvers.get(type + "." + field);
            List<JsonNode> children = resolver != null ? resolver.apply(values) : values.stream().map(v -> v.get(field)).toList();
            String childType = FIELD_TYPES.get(type + "." + field);
            if (sub.fields().isEmpty()) {
                for (int i = 0; i < outs.size(); i++) outs.get(i).set(field, children.get(i));
            } else if (!children.isEmpty() && children.getFirst().isArray()) { // a list: its elements form the next level
                List<JsonNode> flat = new ArrayList<>();
                children.forEach(c -> c.forEach(flat::add));
                var done = execute(flat, sub, resolvers, childType).iterator();
                for (int i = 0; i < outs.size(); i++) {
                    ArrayNode list = outs.get(i).putArray(field);
                    for (int n = 0; n < children.get(i).size(); n++) list.add(done.next());
                }
            } else {
                var done = execute(children, sub, resolvers, childType);
                for (int i = 0; i < outs.size(); i++) outs.get(i).set(field, done.get(i));
            }
        });
        return outs;
    }

    /** One query per parent (the N+1 problem), or one query for the whole level. */
    public static Map<String, Resolver> resolvers(Db db, boolean batched) {
        Function<String[], Resolver> make = tableAndKey -> parents -> {
            String table = tableAndKey[0];
            String key = tableAndKey[1];
            if (!batched) return parents.stream().map(p -> db.find(table, List.of(p.get(key).asString())).getFirst()).toList();
            var ids = new ArrayList<>(new LinkedHashSet<>(parents.stream().map(p -> p.get(key).asString()).toList())); // each once
            var rows = new HashMap<String, JsonNode>();
            var found = db.find(table, ids);
            for (int i = 0; i < ids.size(); i++) rows.put(ids.get(i), found.get(i));
            return parents.stream().map(p -> rows.get(p.get(key).asString())).toList();
        };
        return Map.of("Order.customer", make.apply(new String[] {"customers", "customerId"}),
                "Item.product", make.apply(new String[] {"products", "productId"}));
    }

    /** Base-128, low bits first, top bit set if more follow. >>> so the shift ignores the sign of a long. */
    public static byte[] varint(long n) {
        if (n < 0) throw new IllegalArgumentException("varint takes a whole number from 0");
        var out = new java.io.ByteArrayOutputStream();
        while ((n & ~0x7FL) != 0) {
            out.write((int) (n & 0x7F) | 0x80);
            n >>>= 7;
        }
        out.write((int) n);
        return out.toByteArray();
    }

    public static byte[] encodeOrderSummary(long id, String customer, long totalPence) {
        byte[] text = customer.getBytes(StandardCharsets.UTF_8); // bytes, not chars: protobuf strings are UTF-8
        var out = new java.io.ByteArrayOutputStream();
        out.writeBytes(varint(1 << 3));
        out.writeBytes(varint(id));
        out.writeBytes(varint(2 << 3 | 2));
        out.writeBytes(varint(text.length));
        out.writeBytes(text);
        out.writeBytes(varint(3 << 3));
        out.writeBytes(varint(totalPence));
        return out.toByteArray();
    }

    public record Call(double availability, double ms) {}

    public record Chain(double availability, double sequentialMs, double parallelMs) {}

    public static Chain chain(List<Call> calls) {
        double availability = 1;
        double sequential = 0;
        double parallel = 0;
        for (Call c : calls) {
            availability *= c.availability();
            sequential += c.ms();
            parallel = Math.max(parallel, c.ms());
        }
        return new Chain(availability, sequential, parallel);
    }
}
```

```java
package communication;

import static communication.Communication.Selection.FIELD;

import communication.Communication.Selection;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.stream.IntStream;
import tools.jackson.databind.JsonNode;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class CommunicationCheck {
    private CommunicationCheck() {}

    public static void main(String[] args) throws Exception {
        JsonNode shop = Communication.JSON.readTree(Files.readString(Path.of("../shared/shop.json")));
        var screenQuery = Selection.of("id", FIELD, "totalPence", FIELD, "customer", Selection.of("name", FIELD),
                "items", Selection.of("quantity", FIELD, "product", Selection.of("name", FIELD)));

        var api = new Communication.RestApi(new Communication.Db(shop));
        var rest = Communication.orderScreenRest(api, "o1");
        assert rest.screen().get("customer").get("name").asString().equals("Gbenga Ali");
        assert api.requests == 5 && rest.roundTrips() == 2 && api.bytes == 912 : api.bytes;
        assert Communication.size(rest.screen()) == 203 : Communication.size(rest.screen());

        for (boolean batched : new boolean[] {false, true}) {
            var db = new Communication.Db(shop);
            var order = db.find("orders", List.of("o1"));
            var screen = Communication.execute(order, screenQuery, Communication.resolvers(db, batched), "Order").getFirst();
            assert screen.equals(rest.screen()) && Communication.size(screen) == 203 : screen;
            assert db.queries == (batched ? 3 : 5) : db.queries;
        }

        for (boolean batched : new boolean[] {false, true}) {
            var db = new Communication.Db(shop);
            var orders = db.find("orders", IntStream.rangeClosed(1, 10).mapToObj(i -> "o" + i).toList());
            var listQuery = Selection.of("id", FIELD, "customer", Selection.of("name", FIELD), "items", Selection.of("product", Selection.of("name", FIELD)));
            var page = Communication.execute(orders, listQuery, Communication.resolvers(db, batched), "Order");
            assert page.size() == 10 && page.getFirst().get("customer").get("name").asString().equals("Gbenga Ali");
            assert db.queries == (batched ? 3 : 41) : db.queries;
        }

        var hex = HexFormat.ofDelimiter(" ");
        assert hex.formatHex(Communication.varint(1)).equals("01");
        assert hex.formatHex(Communication.varint(150)).equals("96 01");
        assert hex.formatHex(Communication.varint(300)).equals("ac 02");
        assert hex.formatHex(Communication.varint(1L << 35)).equals("80 80 80 80 80 01");
        try {
            Communication.varint(-1);
            throw new AssertionError("expected a refusal");
        } catch (IllegalArgumentException expected) {
            // negative
        }
        assert hex.formatHex(Communication.encodeOrderSummary(150, "testing", 1)).equals("08 96 01 12 07 74 65 73 74 69 6e 67 18 01");

        assert Communication.encodeOrderSummary(1, "Gbenga Ali", 8996).length == 17;
        var summary = Communication.JSON.createObjectNode().put("id", 1).put("customer", "Gbenga Ali").put("totalPence", 8996);
        assert Communication.size(summary) == 50;

        var c = Communication.chain(java.util.Collections.nCopies(5, new Communication.Call(0.999, 20)));
        assert String.format(Locale.ROOT, "%.2f", c.availability() * 100).equals("99.50") && c.sequentialMs() == 100;
        assert Communication.chain(List.of(new Communication.Call(1, 30), new Communication.Call(1, 50), new Communication.Call(1, 20))).parallelMs() == 50;
        System.out.println("all communication checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/05-communication/labs/java). `python3 labs/run.py communication/java`.

## 7. Rust

`serde_json::Value` with `preserve_order` holds the shop, and `json!` builds the screen. `Db` counts queries in a `Cell`, so the resolvers can share `&Db` without `&mut`. Each resolver is a boxed closure that borrows the database. `RestApi::get` matches the path with a slice pattern. `varint` works on `u64`.

```rust
//! What an API style costs, counted: REST requests and bytes, a GraphQL-style query with the N+1 problem and
//! batching, Protocol Buffers' varints, and synchronous chains. The same numbers as the TypeScript lab.
use serde_json::{Map, Value, json};
use std::cell::Cell;
use std::collections::HashMap;

/// Compact JSON, as JSON.stringify writes it. `preserve_order` keeps fields in the order they were read.
pub fn size(v: &Value) -> usize {
    v.to_string().len()
}

/// A tiny shop database that counts its queries. The count is a Cell, so finding rows needs only `&self`.
pub struct Db {
    pub queries: Cell<u32>,
    tables: HashMap<String, HashMap<String, Value>>,
}

impl Db {
    pub fn new(shop: &Value) -> Self {
        let mut tables = HashMap::new();
        for table in ["customers", "products", "orders"] {
            let rows = shop[table]
                .as_array()
                .into_iter()
                .flatten()
                .map(|r| (r["id"].as_str().unwrap_or_default().to_string(), r.clone()));
            tables.insert(table.to_string(), rows.collect());
        }
        Db {
            queries: Cell::new(0),
            tables,
        }
    }

    /// One query for any number of rows: SELECT … WHERE id IN (…).
    pub fn find(&self, table: &str, ids: &[&str]) -> Vec<Value> {
        self.queries.set(self.queries.get() + 1);
        ids.iter()
            .map(|id| self.tables[table].get(*id).cloned().unwrap_or(Value::Null))
            .collect()
    }
}

/// One whole resource per URL. Counts requests and bytes sent.
pub struct RestApi<'a> {
    db: &'a Db,
    pub requests: u32,
    pub bytes: usize,
}

impl<'a> RestApi<'a> {
    pub fn new(db: &'a Db) -> Self {
        RestApi {
            db,
            requests: 0,
            bytes: 0,
        }
    }

    pub fn get(&mut self, path: &str) -> Result<Value, String> {
        let parts: Vec<&str> = path.split('/').collect(); // "/orders/o1" → "", "orders", "o1"
        let [_, kind @ ("orders" | "customers" | "products"), id] = parts[..] else {
            return Err(format!("404 {path}"));
        };
        let body = self.db.find(kind, &[id]).remove(0);
        if body.is_null() {
            return Err(format!("404 {path}"));
        }
        self.requests += 1;
        self.bytes += size(&body);
        Ok(body)
    }
}

fn text(v: &Value) -> &str {
    v.as_str().unwrap_or_default()
}

/// The order (round trip 1), then its customer and products together (round trip 2).
pub fn order_screen_rest(api: &mut RestApi, order_id: &str) -> Result<(Value, u32), String> {
    let order = api.get(&format!("/orders/{order_id}"))?;
    let customer = api.get(&format!("/customers/{}", text(&order["customerId"])))?;
    let mut items = Vec::new();
    for item in order["items"].as_array().into_iter().flatten() {
        let product = api.get(&format!("/products/{}", text(&item["productId"])))?;
        items.push(json!({ "quantity": item["quantity"], "product": { "name": product["name"] } }));
    }
    let screen = json!({ "id": order["id"], "totalPence": order["totalPence"], "customer": { "name": customer["name"] }, "items": items });
    Ok((screen, 2))
}

/// Fields wanted, in order: `None` for a plain field, `Some` to select inside an object or list.
pub struct Selection(pub Vec<(&'static str, Option<Selection>)>);

/// Fetches one field for every parent at one level of the query at once.
pub type Resolver<'a> = Box<dyn Fn(&[Value]) -> Vec<Value> + 'a>;

fn field_type(typ: &str, field: &str) -> &'static str {
    match (typ, field) {
        ("Order", "customer") => "Customer",
        ("Order", "items") => "Item",
        ("Item", "product") => "Product",
        _ => "",
    }
}

/// Runs a selection over every object at one level together, so each resolver sees the whole level.
pub fn execute(
    values: &[Value],
    selection: &Selection,
    resolvers: &HashMap<&str, Resolver>,
    typ: &str,
) -> Vec<Value> {
    let mut outs: Vec<Map<String, Value>> = values.iter().map(|_| Map::new()).collect();
    for (field, sub) in &selection.0 {
        let children = match resolvers.get(format!("{typ}.{field}").as_str()) {
            Some(resolve) => resolve(values),
            None => values.iter().map(|v| v[*field].clone()).collect(),
        };
        let child_type = field_type(typ, field);
        match sub {
            None => {
                for (out, child) in outs.iter_mut().zip(children) {
                    out.insert(field.to_string(), child);
                }
            }
            Some(sub) if children.first().is_some_and(Value::is_array) => {
                // a list field: all its elements form the next level
                let flat: Vec<Value> = children
                    .iter()
                    .flat_map(|c| c.as_array().cloned().unwrap_or_default())
                    .collect();
                let mut done = execute(&flat, sub, resolvers, child_type).into_iter();
                for (out, c) in outs.iter_mut().zip(&children) {
                    let n = c.as_array().map_or(0, Vec::len);
                    out.insert(
                        field.to_string(),
                        Value::Array(done.by_ref().take(n).collect()),
                    );
                }
            }
            Some(sub) => {
                for (out, r) in outs
                    .iter_mut()
                    .zip(execute(&children, sub, resolvers, child_type))
                {
                    out.insert(field.to_string(), r);
                }
            }
        }
    }
    outs.into_iter().map(Value::Object).collect()
}

/// One query per parent (the N+1 problem), or one query for the whole level.
pub fn resolvers(db: &Db, batched: bool) -> HashMap<&'static str, Resolver<'_>> {
    let make = move |table: &'static str, key: &'static str| -> Resolver<'_> {
        Box::new(move |parents: &[Value]| {
            if !batched {
                return parents
                    .iter()
                    .map(|p| db.find(table, &[text(&p[key])]).remove(0))
                    .collect();
            }
            let mut ids: Vec<&str> = Vec::new();
            for p in parents {
                if !ids.contains(&text(&p[key])) {
                    ids.push(text(&p[key])); // each ID once
                }
            }
            let rows: HashMap<&str, Value> =
                ids.iter().copied().zip(db.find(table, &ids)).collect();
            parents
                .iter()
                .map(|p| rows[text(&p[key])].clone())
                .collect()
        })
    };
    HashMap::from([
        ("Order.customer", make("customers", "customerId")),
        ("Item.product", make("products", "productId")),
    ])
}

/// Base-128, low bits first, top bit set if more follow.
pub fn varint(mut n: u64) -> Vec<u8> {
    let mut out = Vec::new();
    while n >= 0x80 {
        out.push((n as u8 & 0x7f) | 0x80);
        n >>= 7;
    }
    out.push(n as u8);
    out
}

pub fn encode_order_summary(id: u64, customer: &str, total_pence: u64) -> Vec<u8> {
    let mut out = varint(1 << 3);
    out.extend(varint(id));
    out.extend(varint(2 << 3 | 2));
    out.extend(varint(customer.len() as u64)); // len() is bytes, which is what protobuf wants
    out.extend(customer.as_bytes());
    out.extend(varint(3 << 3));
    out.extend(varint(total_pence));
    out
}

#[derive(Debug)]
pub struct Chain {
    pub availability: f64,
    pub sequential_ms: f64,
    pub parallel_ms: f64,
}

/// (availability, ms) for each call in a row.
pub fn chain(calls: &[(f64, f64)]) -> Chain {
    Chain {
        availability: calls.iter().map(|c| c.0).product(),
        sequential_ms: calls.iter().map(|c| c.1).sum(),
        parallel_ms: calls.iter().map(|c| c.1).fold(0.0, f64::max),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn shop() -> Value {
        serde_json::from_str(
            &std::fs::read_to_string("../shared/shop.json").expect("the shared shop"),
        )
        .expect("valid JSON")
    }

    fn screen_query() -> Selection {
        Selection(vec![
            ("id", None),
            ("totalPence", None),
            ("customer", Some(Selection(vec![("name", None)]))),
            (
                "items",
                Some(Selection(vec![
                    ("quantity", None),
                    ("product", Some(Selection(vec![("name", None)]))),
                ])),
            ),
        ])
    }

    #[test]
    fn rest_five_requests_two_round_trips() {
        let db = Db::new(&shop());
        let mut api = RestApi::new(&db);
        let (screen, round_trips) = order_screen_rest(&mut api, "o1").unwrap();
        assert_eq!(screen["customer"]["name"], "Gbenga Ali");
        assert_eq!(
            (api.requests, round_trips, api.bytes, size(&screen)),
            (5, 2, 912, 203)
        );
        assert!(api.get("/refunds/r1").is_err());
    }

    #[test]
    fn a_graphql_style_query_one_request_only_the_fields_asked_for() {
        let shop = shop();
        let rest_db = Db::new(&shop);
        let (want, _) = order_screen_rest(&mut RestApi::new(&rest_db), "o1").unwrap();
        for batched in [false, true] {
            let db = Db::new(&shop);
            let order = db.find("orders", &["o1"]);
            let screen =
                execute(&order, &screen_query(), &resolvers(&db, batched), "Order").remove(0);
            assert_eq!((&screen, size(&screen)), (&want, 203));
            assert_eq!(db.queries.get(), if batched { 3 } else { 5 });
        }
    }

    #[test]
    fn n_plus_one_41_queries_or_3() {
        let shop = shop();
        for batched in [false, true] {
            let db = Db::new(&shop);
            let ids: Vec<String> = (1..=10).map(|i| format!("o{i}")).collect();
            let orders = db.find(
                "orders",
                &ids.iter().map(String::as_str).collect::<Vec<_>>(),
            );
            let query = Selection(vec![
                ("id", None),
                ("customer", Some(Selection(vec![("name", None)]))),
                (
                    "items",
                    Some(Selection(vec![(
                        "product",
                        Some(Selection(vec![("name", None)])),
                    )])),
                ),
            ]);
            let page = execute(&orders, &query, &resolvers(&db, batched), "Order");
            assert_eq!(
                (page.len(), &page[0]["customer"]["name"]),
                (10, &json!("Gbenga Ali"))
            );
            assert_eq!(db.queries.get(), if batched { 3 } else { 41 });
        }
    }

    fn hex(bytes: &[u8]) -> String {
        bytes
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<Vec<_>>()
            .join(" ")
    }

    #[test]
    fn varints_and_tags_as_in_the_protobuf_documentation() {
        assert_eq!(hex(&varint(1)), "01");
        assert_eq!(hex(&varint(150)), "96 01");
        assert_eq!(hex(&varint(300)), "ac 02");
        assert_eq!(hex(&varint(1 << 35)), "80 80 80 80 80 01");
        assert_eq!(
            hex(&encode_order_summary(150, "testing", 1)),
            "08 96 01 12 07 74 65 73 74 69 6e 67 18 01"
        );
    }

    #[test]
    fn the_same_summary_17_bytes_as_protobuf_50_as_json() {
        assert_eq!(encode_order_summary(1, "Gbenga Ali", 8996).len(), 17);
        assert_eq!(
            size(&json!({ "id": 1, "customer": "Gbenga Ali", "totalPence": 8996 })),
            50
        );
    }

    #[test]
    fn a_synchronous_chain() {
        let c = chain(&[(0.999, 20.0); 5]);
        assert_eq!(format!("{:.2}", c.availability * 100.0), "99.50");
        assert_eq!(c.sequential_ms, 100.0);
        assert_eq!(
            chain(&[(1.0, 30.0), (1.0, 50.0), (1.0, 20.0)]).parallel_ms,
            50.0
        );
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/05-communication/labs/rust). `python3 labs/run.py communication/rust`.

## 8. C#

`System.Text.Json.Nodes` holds the shop, `JsonNode.DeepEquals` compares screens, and every value copied into a new object is `DeepClone`d, because a node can have only one parent. `Selection` is a record of `(field, sub)` tuples. `EncodeOrderSummary` builds its bytes with collection expressions. Its `container.sh` copies `../shared` into the container beside the lab. It runs in the .NET SDK container.

```csharp
// What an API style costs, counted: REST requests and bytes, a GraphQL-style query with the N+1 problem and
// batching, Protocol Buffers' varints, and synchronous chains. The same numbers as the TypeScript lab.
using System.Text;
using System.Text.Json.Nodes;

/// <summary>A tiny shop database that counts its queries.</summary>
public sealed class Db
{
    private readonly Dictionary<string, Dictionary<string, JsonNode>> _tables = [];
    public int Queries { get; private set; }

    public Db(JsonNode shop)
    {
        foreach (var table in new[] { "customers", "products", "orders" })
            _tables[table] = shop[table]!.AsArray().ToDictionary(r => (string)r!["id"]!, r => r!);
    }

    /// <summary>One query for any number of rows: SELECT … WHERE id IN (…).</summary>
    public List<JsonNode> Find(string table, params IEnumerable<string> ids)
    {
        Queries++;
        return ids.Select(id => _tables[table][id]).ToList();
    }
}

/// <summary>One whole resource per URL. Counts requests and bytes sent.</summary>
public sealed class RestApi(Db db)
{
    public int Requests { get; private set; }
    public int Bytes { get; private set; }

    public JsonNode Get(string path)
    {
        var parts = path.Split('/'); // "/orders/o1" → "", "orders", "o1"
        if (parts.Length != 3 || parts[1] is not ("orders" or "customers" or "products")) throw new KeyNotFoundException($"404 {path}");
        var body = db.Find(parts[1], parts[2])[0];
        Requests++;
        Bytes += Api.Size(body);
        return body;
    }
}

/// <summary>Fields wanted, in order: null for a plain field, a nested selection to look inside.</summary>
public sealed record Selection(params (string Field, Selection? Sub)[] Fields);

public static class Api
{
    /// <summary>Compact JSON, like JSON.stringify. The default encoder also escapes non-ASCII, which these strings don't have.</summary>
    public static int Size(JsonNode node) => node.ToJsonString().Length;

    /// <summary>The order (round trip 1), then its customer and products together (round trip 2).</summary>
    public static (JsonObject Screen, int RoundTrips) OrderScreenRest(RestApi api, string orderId)
    {
        var order = api.Get($"/orders/{orderId}");
        var customer = api.Get($"/customers/{order["customerId"]}");
        var items = new JsonArray();
        foreach (var item in order["items"]!.AsArray())
        {
            var product = api.Get($"/products/{item!["productId"]}");
            // A node can belong to only one parent, so values copied into the screen are cloned.
            items.Add(new JsonObject { ["quantity"] = item["quantity"]!.DeepClone(), ["product"] = new JsonObject { ["name"] = product["name"]!.DeepClone() } });
        }
        var screen = new JsonObject
        {
            ["id"] = order["id"]!.DeepClone(),
            ["totalPence"] = order["totalPence"]!.DeepClone(),
            ["customer"] = new JsonObject { ["name"] = customer["name"]!.DeepClone() },
            ["items"] = items,
        };
        return (screen, 2);
    }

    private static readonly Dictionary<string, string> FieldTypes = new() { ["Order.customer"] = "Customer", ["Order.items"] = "Item", ["Item.product"] = "Product" };

    /// <summary>Runs a selection over every object at one level together, so each resolver sees the whole level.</summary>
    public static List<JsonObject> Execute(IReadOnlyList<JsonNode> values, Selection selection,
        IReadOnlyDictionary<string, Func<IReadOnlyList<JsonNode>, List<JsonNode>>> resolvers, string type)
    {
        var outs = values.Select(_ => new JsonObject()).ToList();
        foreach (var (field, sub) in selection.Fields)
        {
            var children = resolvers.TryGetValue($"{type}.{field}", out var resolve) ? resolve(values) : values.Select(v => v[field]!).ToList();
            var childType = FieldTypes.GetValueOrDefault($"{type}.{field}", "");
            if (sub is null)
            {
                for (var i = 0; i < outs.Count; i++) outs[i][field] = children[i].DeepClone();
            }
            else if (children.Count > 0 && children[0] is JsonArray) // a list field: all its elements form the next level
            {
                var flat = children.SelectMany(c => c.AsArray()).Select(e => e!).ToList();
                var done = Execute(flat, sub, resolvers, childType).GetEnumerator();
                for (var i = 0; i < outs.Count; i++)
                {
                    var list = new JsonArray();
                    for (var n = 0; n < children[i].AsArray().Count && done.MoveNext(); n++) list.Add(done.Current);
                    outs[i][field] = list;
                }
            }
            else
            {
                var done = Execute(children, sub, resolvers, childType);
                for (var i = 0; i < outs.Count; i++) outs[i][field] = done[i];
            }
        }
        return outs;
    }

    /// <summary>One query per parent (the N+1 problem), or one query for the whole level.</summary>
    public static Dictionary<string, Func<IReadOnlyList<JsonNode>, List<JsonNode>>> Resolvers(Db db, bool batched)
    {
        Func<IReadOnlyList<JsonNode>, List<JsonNode>> Make(string table, string key) => parents =>
        {
            if (!batched) return parents.Select(p => db.Find(table, (string)p[key]!)[0]).ToList();
            var ids = parents.Select(p => (string)p[key]!).Distinct().ToList(); // each ID once, in first-seen order
            var rows = ids.Zip(db.Find(table, ids)).ToDictionary(r => r.First, r => r.Second);
            return parents.Select(p => rows[(string)p[key]!]).ToList();
        };
        return new() { ["Order.customer"] = Make("customers", "customerId"), ["Item.product"] = Make("products", "productId") };
    }

    /// <summary>Base-128, low bits first, top bit set if more follow.</summary>
    public static byte[] Varint(ulong n)
    {
        var bytes = new List<byte>();
        for (; n >= 0x80; n >>= 7) bytes.Add((byte)(n & 0x7f | 0x80));
        bytes.Add((byte)n);
        return [.. bytes];
    }

    public static byte[] EncodeOrderSummary(ulong id, string customer, ulong totalPence)
    {
        var text = Encoding.UTF8.GetBytes(customer); // bytes, not chars: protobuf strings are UTF-8
        return [.. Varint(1 << 3), .. Varint(id), .. Varint(2 << 3 | 2), .. Varint((ulong)text.Length), .. text, .. Varint(3 << 3), .. Varint(totalPence)];
    }

    public static (double Availability, double SequentialMs, double ParallelMs) Chain(IEnumerable<(double Availability, double Ms)> calls) =>
        calls.Aggregate((1.0, 0.0, 0.0), (c, call) => (c.Item1 * call.Availability, c.Item2 + call.Ms, Math.Max(c.Item3, call.Ms)));
}
```

```csharp
// Checks: the same numbers as every other language.
using System.Globalization;
using System.Text.Json.Nodes;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var shop = JsonNode.Parse(File.ReadAllText("../shared/shop.json"))!;
var screenQuery = new Selection(("id", null), ("totalPence", null), ("customer", new(("name", null))),
    ("items", new(("quantity", null), ("product", new(("name", null))))));

var api = new RestApi(new Db(shop));
var (screen, roundTrips) = Api.OrderScreenRest(api, "o1");
Check((string?)screen["customer"]!["name"] == "Gbenga Ali", screen);
Check(api.Requests == 5 && roundTrips == 2 && api.Bytes == 912 && Api.Size(screen) == 203, (api.Requests, api.Bytes, Api.Size(screen)));
try
{
    api.Get("/refunds/r1");
    Check(false, "expected a 404");
}
catch (KeyNotFoundException)
{
    // not a resource
}

foreach (var batched in new[] { false, true })
{
    var db = new Db(shop);
    var result = Api.Execute(db.Find("orders", "o1"), screenQuery, Api.Resolvers(db, batched), "Order")[0];
    Check(JsonNode.DeepEquals(result, screen) && Api.Size(result) == 203, result);
    Check(db.Queries == (batched ? 3 : 5), (batched, db.Queries));
}

foreach (var batched in new[] { false, true })
{
    var db = new Db(shop);
    var orders = db.Find("orders", Enumerable.Range(1, 10).Select(i => $"o{i}"));
    var page = Api.Execute(orders, new Selection(("id", null), ("customer", new(("name", null))), ("items", new(("product", new(("name", null)))))),
        Api.Resolvers(db, batched), "Order");
    Check(page.Count == 10 && (string?)page[0]["customer"]!["name"] == "Gbenga Ali", page[0]);
    Check(db.Queries == (batched ? 3 : 41), (batched, db.Queries));
}

static string Hex(byte[] bytes) => Convert.ToHexString(bytes).ToLowerInvariant().Chunk(2).Select(c => new string(c)).Aggregate((a, b) => $"{a} {b}");
Check(Hex(Api.Varint(1)) == "01" && Hex(Api.Varint(150)) == "96 01" && Hex(Api.Varint(300)) == "ac 02", "varints");
Check(Hex(Api.Varint(1UL << 35)) == "80 80 80 80 80 01", "past 32 bits");
Check(Hex(Api.EncodeOrderSummary(150, "testing", 1)) == "08 96 01 12 07 74 65 73 74 69 6e 67 18 01", Hex(Api.EncodeOrderSummary(150, "testing", 1)));

Check(Api.EncodeOrderSummary(1, "Gbenga Ali", 8996).Length == 17, "protobuf");
Check(Api.Size(new JsonObject { ["id"] = 1, ["customer"] = "Gbenga Ali", ["totalPence"] = 8996 }) == 50, "json");

var c = Api.Chain(Enumerable.Repeat((0.999, 20.0), 5));
Check((c.Availability * 100).ToString("F2", CultureInfo.InvariantCulture) == "99.50" && c.SequentialMs == 100, c);
Check(Api.Chain([(1, 30), (1, 50), (1, 20)]).ParallelMs == 50, "parallel");
Console.WriteLine("all communication checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/05-communication/labs/csharp). `python3 labs/run.py communication/csharp`.

## Common pitfalls

1. **Comparing JSON sizes across languages without matching serialiser settings.** Spaces, escaping and key order all change the count.
2. **A string's length as protobuf's length.** Python, Java and C# count characters or UTF-16 units, not UTF-8 bytes. Encode first.
3. **Copying JavaScript's DataLoader timing into a threaded server.** There's no "event loop went quiet" moment. Use your framework's loader, which batches by level or by a short wait.
4. **`>>` instead of `>>>` in a Java varint.** A negative number never reaches zero, and the loop never ends.
5. **Reusing a `JsonNode` in two places in C#.** It throws "the node already has a parent". Clone it.

## Check your understanding

1. Why can't a Java GraphQL server batch by waiting for "the event loop to go quiet", the way JavaScript does?
2. The same screen is 203 bytes from `JSON.stringify` and 225 from Python's `json.dumps`. Where do the 22 bytes come from?
3. How many bytes does the name `José` take in a protobuf string field, and what would Java's `"José".length()` say?
4. Why does the Java varint use `>>>`?
5. Go's `json.Marshal` writes the REST resources' keys in a different order from JavaScript. Why doesn't that change the 912?

<details>
<summary>Answers — after your attempt</summary>

1. A Java server runs resolvers on several threads, so there's no single loop whose quiet moment means "everyone has asked": another thread could be about to ask. It needs another signal, such as finishing one level of the query, or a short timer.
2. The default separators are `", "` and `": "`, with a space after each comma and colon. The screen has 22 of them; compact output drops them.
3. Five bytes: J, o, s are one byte each and é is two, plus one length byte (and the tag) in front. `length()` says 4, because é is one UTF-16 unit. Writing 4 as the length would cut the last byte off.
4. Java's `long` is signed, and `>>` copies the sign bit in from the left, so a negative number stays negative and never becomes 0. `>>>` shifts in zeros, so the value always reaches 0. The lab also rejects negatives, as protobuf's `uint` types would.
5. Reordering keys moves characters around without adding or removing any: the same names, values, quotes, colons and commas, so the same length. Escaping and spacing change the length; ordering doesn't.

</details>

## Practice — independent task

**Batch on the event loop in Python, the JavaScript way.**

1. Make an async version of the Python lab's executor, `execute_async`, that resolves fields concurrently with `asyncio.gather`, like the TypeScript one.
2. Write a `DataLoader` whose `load(key)` returns a future, and which sends its batch from `loop.call_soon` once the current work has run.
3. Run the order screen and the ten-order page through it, and check the query counts: 5 and 3, and 41 and 3.

**Done when:** the counts match, and you can explain whether your loader would batch correctly if the query were nested one level deeper, and how you checked.

<details>
<summary>Hints — after your attempt</summary>

- Schedule the dispatch only when the first key of a new batch arrives, as the TypeScript `load` does with `setImmediate`.
- If deeper levels give more queries than expected, `call_soon` may be firing before the next level's resolvers have asked. Schedule the dispatch one step later, or wait until the loop has no other ready callbacks.

</details>

## Before moving on

You can say when your language's batching loader sends its batch, name the serialiser defaults that change JSON's size, and encode a protobuf string with the right byte length.

**Recap.** The costs in the main lesson don't depend on the language; how you measure them does. JavaScript and Python batch on the event loop; threaded servers batch by level (graphql-java) or by a short wait (Go's loaders); the labs batch by level everywhere and get 5/3 and 41/3. JSON's size depends on the serialiser: Python adds spaces, Go sorts keys and escapes HTML characters, C# escapes non-ASCII. Protobuf string lengths are UTF-8 bytes, which only Go and Rust give directly; Java's varint needs `>>>`. And in C#, a JSON node has one parent.

## Related

- [[architecture/02-building-blocks/05-communication/index|Communication]]: the main lesson
- [[architecture/02-building-blocks/04-messaging-and-async/in-other-languages|Messaging and async in other languages]]: the asynchronous side, in the same languages
- [[architecture/02-building-blocks/01-load-balancing-and-proxies/in-other-languages|Load balancing in other languages]]: UTF-16 against UTF-8 again, for hashing
