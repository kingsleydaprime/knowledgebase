---
id: 5fee3439-949c-430c-8a44-be844541105c
---

# Pagination, Filtering, Searching, Sorting and Field Selection

**These five are how a client asks for part of a long list, in the order it wants, without downloading everything: pagination gives one page at a time, filtering keeps only matching items, searching matches typed text, sorting chooses the order, and field selection sends only the fields asked for.** They're all query parameters on the same list routes, and in Go the work is turning those strings into checked values, then into SQL that's safe no matter what the client typed.

## Before you start
<!-- bite: d0e13c91-599e-4ba5-9710-21c6862615a4 -->

You should have:

1. Finished [[backend/frameworks/net-http/08-data-with-postgres|lesson 8]], so the menu and orders live in Postgres and every store method takes a context.
2. Read [[backend/02-api-design/01-apis-and-rest|APIs and REST]], if the idea of query parameters as "how you want it" is new.

After this lesson you will be able to:

1. Design the query parameters for a list, and check every one of them, including ones the client misspelled.
2. Build a `WHERE` clause from optional filters, with every value in a placeholder.
3. Let clients sort by a field without ever putting their text into SQL.
4. Page through a quiet list with offset pagination, and a busy one with cursor pagination.
5. Send only the fields a client asks for.
6. Add the indexes that keep all of this fast.

## Where we stopped
<!-- bite: 6d85b4eb-0d63-4a15-837d-56c132d65ba7 -->

Lesson 8 ended with a picture of Mama Put six months from now: thousands of orders, and the kitchen screen getting every one of them in a single response. Here's what different people actually want from those lists:

1. **The kitchen screen**: pending orders, oldest first, 20 at a time, and it must never skip or repeat an order while new ones keep arriving.
2. **A customer on the phone app**: dishes under ₦2,000, cheapest first.
3. **Someone searching**: "egusi".
4. **A slow phone on a bad network**: only each dish's name and price, nothing else.

Remember the rule from [[backend/frameworks/net-http/02-routing|lesson 2]]: the path says **which thing**, the query says **how you want it**. All four wishes are "how", so they're all query parameters, on two routes: `GET /menu` and a new kitchen route, `GET /orders`.

## The kid version
<!-- bite: 3b79abce-e747-4867-9833-f05725750d31 -->

Mama's order notebook has hundreds of pages. When the kitchen asks "what's still waiting?", she doesn't read out the whole book. She flips to the waiting ones (filtering), starts from the oldest (sorting), reads twenty (a page), and puts her finger on the last one she read, so next time she carries on from there (a cursor).

**Where the picture stops working.** Mama's finger stays put while she talks. On a server, between "page one" and "page two" new orders keep arriving, and if you count pages by number instead of keeping a finger on the last one you read, the pages slide under you. That's step 5.

## Terms used in this lesson
<!-- bite: f3236595-6c1a-4055-bbc1-469e5d56d324 -->

1. **Pagination**: This means sending a long list one page at a time.
2. **Offset pagination**: This means asking for a page by how many items to skip: `limit=20&offset=40` is "items 41 to 60".
3. **Cursor pagination**: This is also called **keyset pagination**. Each page comes with a **cursor**, a bookmark meaning "the last item you saw", and the next request asks for items after it.
4. **Filter**: This is a condition that keeps only some items, like `maxPrice=2000`.
5. **Search**: This is matching items by text the user typed, like `q=egusi`.
6. **Sort**: This is the order items come back in, like `sort=-priceNaira`, where a minus sign means highest first.
7. **Field selection**: This is also called **sparse fieldsets**. The client lists the fields it wants, like `fields=name,priceNaira`, and gets only those.
8. **Allow-list**: This is a fixed list of values you accept. Anything not on it is refused. It's how client text gets near SQL safely.
9. **Index**: This is a structure the database keeps beside a table, like the index at the back of a book, so it can find rows without reading every one.

## Step 1: decide the query parameters
<!-- bite: 710b0253-b51f-4c5e-a378-240764f55b57 -->

Before any code, the design. These are the parameters, and what each means:

| Parameter | Example | Means | On |
|---|---|---|---|
| `limit` | `limit=20` | at most this many items (1 to 100, default 20) | both |
| `offset` | `offset=40` | skip this many first | menu |
| `cursor` | `cursor=eyJ0Ij...` | after this bookmark | orders |
| `available` | `available=true` | only dishes still available | menu |
| `special` | `special=true` | only today's specials | menu |
| `minPrice`, `maxPrice` | `maxPrice=2000` | a price range, in naira | menu |
| `q` | `q=egusi` | dish names containing this, any case | menu |
| `sort` | `sort=priceNaira,-name` | comma-separated, `-` for descending | menu |
| `fields` | `fields=name,priceNaira` | only these fields | menu |
| `status` | `status=pending` | only orders in this status | orders |

A few decisions are hidden in that table:

1. **Names use the API's words**, the same `priceNaira` the JSON uses, never the database's `price_naira`. Clients shouldn't know or care what the columns are called.
2. **`limit` has a maximum.** Without one, `limit=1000000` is the "send everything" request we're trying to get rid of.
3. **Every parameter is checked**, and an unknown one is a 400. `?maxprice=2000` with a small p would otherwise be silently ignored, and the customer would see dishes they can't afford and think the filter is broken. It's lesson 6's `DisallowUnknownFields`, for the query.

And `GET /menu/specials` from lesson 2 is now just `GET /menu?special=true`. Keep the old route for now (old clients use it); lesson 10 is about retiring routes properly.

## Step 2: a query reader that collects every mistake
<!-- bite: 2b89ca0f-9799-4c67-86e2-4e304955cb88 -->

In lesson 6, `QueryBool` returned an error for one parameter. With ten parameters, ten `if err != nil` blocks would bury the handler, and the client would learn about one mistake per request.

Instead, a small reader that **remembers** its mistakes and reports them all at the end. It's a pattern you'll see in Go's own standard library (`bufio.Scanner` works this way), and a nice example of the Go saying "errors are values": an error is just data, so you can collect it, like any other data.

Make `internal/httpx/query.go`:

```go
package httpx

import (
	"net/http"
	"net/url"
	"slices"
	"strconv"
	"strings"

	"mamaput/internal/apperr"
)

// Query reads query parameters, collecting every problem instead of stopping at the first.
type Query struct {
	values url.Values
	used   map[string]bool
	errs   []apperr.FieldError
}

func NewQuery(r *http.Request) *Query {
	return &Query{values: r.URL.Query(), used: map[string]bool{}}
}

func (q *Query) get(name string) string {
	q.used[name] = true
	return q.values.Get(name)
}

func (q *Query) fail(name, message string) {
	q.errs = append(q.errs, apperr.FieldError{Field: name, Message: message})
}

func (q *Query) Int(name string, def, min, max int) int {
	raw := q.get(name)
	if raw == "" {
		return def
	}
	n, err := strconv.Atoi(raw)
	if err != nil || n < min || n > max {
		q.fail(name, "must be a whole number from "+strconv.Itoa(min)+" to "+strconv.Itoa(max))
		return def
	}
	return n
}

// OptionalInt is like Int, but nil means "not sent".
func (q *Query) OptionalInt(name string, min, max int) *int {
	if q.values.Get(name) == "" {
		q.used[name] = true
		return nil
	}
	n := q.Int(name, 0, min, max)
	return &n
}

func (q *Query) Bool(name string) bool {
	raw := q.get(name)
	if raw == "" {
		return false
	}
	b, err := strconv.ParseBool(raw)
	if err != nil {
		q.fail(name, "must be true or false")
	}
	return b
}

func (q *Query) String(name string, maxLen int) string {
	raw := strings.TrimSpace(q.get(name))
	if len(raw) > maxLen {
		q.fail(name, "must be at most "+strconv.Itoa(maxLen)+" characters")
		return ""
	}
	return raw
}

func (q *Query) OneOf(name string, allowed ...string) string {
	raw := q.get(name)
	if raw != "" && !slices.Contains(allowed, raw) {
		q.fail(name, "must be one of: "+strings.Join(allowed, ", "))
		return ""
	}
	return raw
}

// Err reports every problem, including parameters nobody read.
func (q *Query) Err() error {
	for name := range q.values {
		if !q.used[name] {
			q.fail(name, "is not a parameter this address accepts")
		}
	}
	if len(q.errs) == 0 {
		return nil
	}
	return apperr.InvalidFields(q.errs)
}
```

Each method reads one parameter, checks it, and on a problem **writes it down** (`q.fail`) and returns a safe default, so the handler carries on. `Err` at the end turns everything written down into one `Invalid` error with a list of fields, the same shape as a bad body from lesson 6.

The `used` map is how unknown parameters are caught: every method marks the name it read, and `Err` complains about anything in the URL that nothing read.

Two methods are still missing, `Sort` and `Fields`, because they're about safety more than parsing. They come in step 3 and step 4.

## Step 3: sorting, without putting client text into SQL
<!-- bite: f943154a-8cb4-44a6-a350-2e5d4a870a28 -->

Here is the most dangerous query parameter in the lesson. The client sends `sort=priceNaira`, and SQL needs `ORDER BY price_naira`. A **column name** can't go in a placeholder: `ORDER BY $1` sorts by a constant value, which means not at all. So the column name has to be part of the SQL text.

Lesson 8's rule was: the only things joined into SQL text are things **you** wrote. An **allow-list** keeps that rule. The client's text is never used as SQL; it's only used to **look up** text you wrote.

The result of reading a sort is a list of "which column, which way". The menu store will need that type, and so will `httpx`, which reads it. If it lived in `httpx`, the store deep down would import an HTTP helper package: it would compile, but the dependency would point the wrong way. So it gets a tiny package of its own, `internal/listing/listing.go`, which knows nothing about HTTP or about any feature:

```go
// Package listing holds the shared pieces of list queries.
package listing

// SortField is one part of a sort: which column, and which way.
type SortField struct {
	Column string // SQL text from an allow-list, never from the client
	Desc   bool
}
```

Small packages with one job are cheap in Go; use them. Now the reader, in `query.go` (add `"mamaput/internal/listing"` to its imports):

```go
// Sort reads "priceNaira,-name" using allowed, a map from API names to SQL columns.
func (q *Query) Sort(name string, allowed map[string]string) []listing.SortField {
	raw := q.get(name)
	if raw == "" {
		return nil
	}
	var out []listing.SortField
	for _, part := range strings.Split(raw, ",") {
		desc := strings.HasPrefix(part, "-")
		column, ok := allowed[strings.TrimPrefix(part, "-")]
		if !ok {
			q.fail(name, strings.TrimPrefix(part, "-")+" is not a field you can sort by")
			return nil
		}
		out = append(out, listing.SortField{Column: column, Desc: desc})
	}
	return out
}
```

`sort=price_naira`, `sort=password_hash` and `sort=1;DROP TABLE dishes` all fail the map lookup and become a 400. Nothing the client sends can reach the SQL, because the only strings that can come out of `Sort` are the map's values, which live in your code.

## Step 4: the menu's list, in SQL
<!-- bite: 7c84c97b-df57-4abc-a9bc-ca1018154e41 -->

Now the menu's own types. In `internal/menu/menu.go`, replace `ListFilter` with:

```go
type ListQuery struct {
	OnlyAvailable bool
	OnlySpecials  bool
	MinPrice      *int
	MaxPrice      *int
	Search        string
	Sort          []listing.SortField
	Limit, Offset int
}

// SortableFields maps the API's field names to columns.
var SortableFields = map[string]string{
	"id":         "id",
	"name":       "name",
	"priceNaira": "price_naira",
	"createdAt":  "created_at",
}
```

The store interface's `List` becomes `List(ctx context.Context, q ListQuery) ([]Dish, int, error)`: the page of dishes, the total that match, and an error. The Postgres version, in `internal/menu/postgres.go`:

```go
var likeEscaper = strings.NewReplacer(`\`, `\\`, `%`, `\%`, `_`, `\_`)

func (s *PostgresStore) List(ctx context.Context, q ListQuery) ([]Dish, int, error) {
	var where []string
	var args []any
	add := func(condition string, value any) {
		args = append(args, value)
		where = append(where, fmt.Sprintf(condition, len(args)))
	}

	if q.OnlyAvailable {
		where = append(where, "available")
	}
	if q.OnlySpecials {
		where = append(where, "special")
	}
	if q.MinPrice != nil {
		add("price_naira >= $%d", *q.MinPrice)
	}
	if q.MaxPrice != nil {
		add("price_naira <= $%d", *q.MaxPrice)
	}
	if q.Search != "" {
		add("name ILIKE '%%' || $%d || '%%'", likeEscaper.Replace(q.Search))
	}

	whereSQL := ""
	if len(where) > 0 {
		whereSQL = " WHERE " + strings.Join(where, " AND ")
	}

	var total int
	if err := s.pool.QueryRow(ctx, "SELECT count(*) FROM dishes"+whereSQL, args...).Scan(&total); err != nil {
		return nil, 0, fmt.Errorf("count dishes: %w", err)
	}

	order := make([]string, 0, len(q.Sort)+1)
	for _, f := range q.Sort {
		if f.Desc {
			order = append(order, f.Column+" DESC")
		} else {
			order = append(order, f.Column)
		}
	}
	order = append(order, "id") // always last, so the order is the same every time

	args = append(args, q.Limit, q.Offset)
	sql := "SELECT " + dishColumns + " FROM dishes" + whereSQL +
		" ORDER BY " + strings.Join(order, ", ") +
		fmt.Sprintf(" LIMIT $%d OFFSET $%d", len(args)-1, len(args))

	rows, err := s.pool.Query(ctx, sql, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("list dishes: %w", err)
	}
	defer rows.Close()

	dishes := []Dish{}
	for rows.Next() {
		d, err := scanDish(rows)
		if err != nil {
			return nil, 0, err
		}
		dishes = append(dishes, d)
	}
	return dishes, total, rows.Err()
}
```

The heart of it is the little `add` function. Each optional filter appends its **value** to `args`, and its **condition** to `where`, with the placeholder number filled in from how many values there are so far. So `maxPrice=2000&q=rice` builds:

```sql
SELECT ... FROM dishes WHERE price_naira <= $1 AND name ILIKE '%' || $2 || '%'
 ORDER BY id LIMIT $3 OFFSET $4
```

with `args` = `[2000, "rice", 20, 0]`. Every value is in a placeholder. The only text joined into the SQL is text in this file: conditions, column names from the allow-list, and numbers like `$3` that we counted ourselves. `fmt.Sprintf` here only ever formats **our own** numbers into **our own** strings. (The `%%` is how you write a literal `%` inside `Sprintf`.)

Three details worth stopping on:

1. **Search escaping.** In `ILIKE`, `%` means "anything" and `_` means "any one character". A customer searching for `100%` would match far more than they meant. `likeEscaper` puts a `\` before each of them (and before `\` itself), so the search text is matched literally. It's not a security hole (the value is still a placeholder), it's correctness.
2. **The count runs with the same `WHERE` and the same `args`**, before the limit and offset are added. So `total` is how many dishes match the filters, not how many exist.
3. **`id` is always the last sort.** Sorting by price alone, two dishes at ₦1,500 could come back in either order, and could swap between page 1 and page 2, so one appears twice and the other never. Ending every `ORDER BY` with a unique column makes the order the same every time.

## Step 5: the menu handler, and offset pagination
<!-- bite: 3d386dea-b7ea-4f98-bd28-06e9a256249a -->

The response needs somewhere to put the page details. That's what `meta` in the envelope from lesson 7 was for. Add to `internal/httpx/json.go`:

```go
func WriteList(w http.ResponseWriter, data, meta any) error {
	body, err := json.Marshal(envelope{Data: data, Meta: meta})
	if err != nil {
		return fmt.Errorf("encode response: %w", err)
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(body)
	return nil
}
```

The handler reads the query, calls the service, and sends the page:

```go
type pageMeta struct {
	Limit  int `json:"limit"`
	Offset int `json:"offset"`
	Total  int `json:"total"`
}

func (h *Handler) list(w http.ResponseWriter, r *http.Request) error {
	q := httpx.NewQuery(r)
	lq := ListQuery{
		OnlyAvailable: q.Bool("available"),
		OnlySpecials:  q.Bool("special"),
		MinPrice:      q.OptionalInt("minPrice", 1, 1_000_000),
		MaxPrice:      q.OptionalInt("maxPrice", 1, 1_000_000),
		Search:        q.String("q", 50),
		Sort:          q.Sort("sort", SortableFields),
		Limit:         q.Int("limit", 20, 1, 100),
		Offset:        q.Int("offset", 0, 0, 10_000),
	}
	fields := q.Fields("fields", dishFieldNames)
	if err := q.Err(); err != nil {
		return err
	}

	dishes, total, err := h.svc.List(r.Context(), lq)
	if err != nil {
		return err
	}
	return httpx.WriteList(w, httpx.Pick(dishes, fields), pageMeta{Limit: lq.Limit, Offset: lq.Offset, Total: total})
}
```

Read it as a form being filled in: one line per parameter, then **one** check. Every mistake in the request comes back together:

```bash
curl -s "localhost:8080/menu?limit=500&sort=password&maxprice=2000"
# {"type":".../problems/invalid-fields","status":400,...,"errors":[
#   {"field":"sort","message":"password is not a field you can sort by"},
#   {"field":"limit","message":"must be a whole number from 1 to 100"},
#   {"field":"maxprice","message":"is not a parameter this address accepts"}]}

curl -s "localhost:8080/menu?maxPrice=2000&sort=priceNaira&limit=2"
# {"data":[{"id":"2","name":"Beans and plantain","priceNaira":1200,...},
#          {"id":"1","name":"Jollof rice","priceNaira":1500,...}],
#  "meta":{"limit":2,"offset":0,"total":2}}

curl -s "localhost:8080/menu?q=EGUSI"
```

Did `Offset` get a maximum, 10,000? Yes, and here's why. To answer `OFFSET 10000`, Postgres has to find the first 10,000 rows and throw them away. That gets slower the deeper you go, and it's a cheap way for someone to make your database work hard. A menu never has 10,000 dishes, so for the menu that limit costs nothing.

`h.svc.List` is a one-line pass-through in `menu.Service` today. It's still worth having: it's where a rule like "customers never see hidden dishes" would go.

## Step 6: field selection
<!-- bite: 938bc2b7-38cd-411a-805e-5ba0cf61342c -->

`fields=name,priceNaira` should send `{"id":"1","name":"Jollof rice","priceNaira":1500}` for each dish. In JavaScript you'd just copy some keys. In Go, a `Dish` is a struct with all its fields, always. So for field selection we turn each dish into a **map**, keep the keys asked for, and send the maps.

First the reader, in `query.go`:

```go
// Fields reads "name,priceNaira", checking each against the allowed names.
func (q *Query) Fields(name string, allowed []string) []string {
	raw := q.get(name)
	if raw == "" {
		return nil // nil means "every field"
	}
	fields := strings.Split(raw, ",")
	for _, f := range fields {
		if !slices.Contains(allowed, f) {
			q.fail(name, f+" is not a field of this resource")
			return nil
		}
	}
	return fields
}
```

And the picker, in `json.go`:

```go
// Pick turns each item into a map holding only the given fields, plus "id".
// With no fields, it returns the items unchanged.
func Pick[T any](items []T, fields []string) any {
	if len(fields) == 0 {
		return items
	}
	keep := map[string]bool{"id": true}
	for _, f := range fields {
		keep[f] = true
	}
	out := make([]map[string]json.RawMessage, 0, len(items))
	for _, item := range items {
		b, err := json.Marshal(item)
		if err != nil {
			return items
		}
		var all map[string]json.RawMessage
		json.Unmarshal(b, &all)
		for key := range all {
			if !keep[key] {
				delete(all, key)
			}
		}
		out = append(out, all)
	}
	return out
}
```

It encodes each item to JSON, decodes that into a map, and deletes the keys not wanted. `json.RawMessage` means "keep this value as the exact JSON it was", so numbers, dates and the `"id":"1"` string come out precisely as they went in. It always keeps `id`, because a client can't do much with an item it can't point back to.

In `menu.go`, the allowed names:

```go
var dishFieldNames = []string{"id", "name", "priceNaira", "available", "special", "portionsLeft", "createdAt"}
```

Encoding twice costs a little time, and only when `fields` is used, on a page of at most 100 items. That's a good trade for code this simple. Notice also what field selection does **not** do: it doesn't change the SQL. The database still reads every column, which for a seven-column table is nothing. Field selection here saves **network**, which is what the slow phone needed.

## Step 7: where offset pagination breaks
<!-- bite: ab81f2d7-9e0c-43eb-9f50-1fc74e2e5569 -->

Offset pagination is fine for the menu, which changes a few times a day. For the kitchen's order list, it's broken, and it's worth seeing why.

The kitchen screen shows pending orders, oldest first, 20 per page. It loads page 1 (`offset=0`): orders 1 to 20. While the cook is reading, orders 3 and 7 are marked ready, so they're no longer pending. Now the cook taps "next" (`offset=20`). The list has shifted up by two, so items 21 and 22 slid into page 1's positions. Page 2 starts at what used to be item 23. **Orders 21 and 22 were never shown.** Two customers wait forever for food nobody started.

New orders arriving cause the opposite bug when sorting newest first: items slide down, and the cook sees some twice.

The cause is that "skip 20" is counted from the top of a list that keeps moving. The fix is to stop counting, and put a finger on the last order actually seen: "orders after **this one**". That's a cursor.

## Step 8: cursor pagination for orders
<!-- bite: c6118577-019d-43de-af36-e95c231ad5f5 -->

The kitchen's list is sorted by `created_at`, then `id` (two orders can share a time). So "after this one" means: after this `(created_at, id)` pair. Postgres can compare pairs directly:

```sql
WHERE (created_at, id) > ($1, $2)
ORDER BY created_at, id
```

That reads "rows whose time is later, or the same time with a bigger id". It's exact, it doesn't care what happened to the rows before the finger, and with the right index (step 9) it's fast at any depth: Postgres jumps straight to the bookmark instead of counting.

The client shouldn't need to know what's inside the bookmark, so we pack it into one piece of text. Make `internal/listing/cursor.go`:

```go
package listing

import (
	"encoding/base64"
	"encoding/json"
	"time"
)

type Cursor struct {
	Time time.Time `json:"t"`
	ID   int64     `json:"id"`
}

func (c Cursor) Encode() string {
	b, _ := json.Marshal(c)
	return base64.RawURLEncoding.EncodeToString(b)
}

func DecodeCursor(s string) (Cursor, bool) {
	b, err := base64.RawURLEncoding.DecodeString(s)
	if err != nil {
		return Cursor{}, false
	}
	var c Cursor
	if err := json.Unmarshal(b, &c); err != nil || c.ID < 1 || c.Time.IsZero() {
		return Cursor{}, false
	}
	return c, true
}
```

A cursor is the JSON `{"t":"2026-11-21T12:00:00.123456Z","id":482}` in **base64url**, a way of writing any data with only letters, digits, `-` and `_`, so it's safe in a URL. It isn't secret (anyone can decode it), but it's **opaque**: clients just pass it back. A cursor that's been tampered with fails to decode or fails the checks, and becomes a 400.

Look at the time in that cursor: six digits after the seconds. Postgres stores time to the **microsecond**, and a bookmark must be exact, or `(created_at, id) > (bookmark)` might be true for the very order the bookmark points at, and every page would start by repeating it. Go's `time.Time` holds nanoseconds, and `encoding/json` writes times in the **RFC 3339 with nanoseconds** format, so the full value survives the trip. Here's the trap: if you ever format a cursor time yourself with `time.RFC3339` instead of `time.RFC3339Nano`, the fraction of a second is **dropped**, and you get exactly that repeating bug. Let `encoding/json` do it, or use `RFC3339Nano`.

The orders store gets a list method, in `internal/orders/postgres.go`:

```go
type ListQuery struct {
	Status Status
	After  *listing.Cursor
	Limit  int
}

func (s *PostgresStore) List(ctx context.Context, q ListQuery) ([]Order, error) {
	var where []string
	var args []any
	add := func(condition string, value ...any) {
		args = append(args, value...)
		where = append(where, condition)
	}

	if q.Status != "" {
		add(fmt.Sprintf("status = $%d", len(args)+1), q.Status)
	}
	if q.After != nil {
		n := len(args)
		add(fmt.Sprintf("(created_at, id) > ($%d, $%d)", n+1, n+2), q.After.Time, q.After.ID)
	}

	sql := "SELECT " + orderColumns + " FROM orders"
	if len(where) > 0 {
		sql += " WHERE " + strings.Join(where, " AND ")
	}
	args = append(args, q.Limit+1)
	sql += fmt.Sprintf(" ORDER BY created_at, id LIMIT $%d", len(args))

	rows, err := s.pool.Query(ctx, sql, args...)
	if err != nil {
		return nil, fmt.Errorf("list orders: %w", err)
	}
	defer rows.Close()

	orders := []Order{}
	for rows.Next() {
		o, err := scanOrder(rows)
		if err != nil {
			return nil, err
		}
		orders = append(orders, o)
	}
	return orders, rows.Err()
}
```

Notice `LIMIT q.Limit+1`. We ask for **one more** than the page size. If it comes back, there's a next page, and we drop it before sending; if it doesn't, this is the last page. That's how we know whether to send a cursor, without a second query to count.

Add `List(ctx, ListQuery) ([]Order, error)` to the `orders.Store` interface, a pass-through `List` on the service, and the handler, in `internal/orders/handlers.go`:

```go
type cursorMeta struct {
	Limit      int    `json:"limit"`
	NextCursor string `json:"nextCursor,omitempty"`
}

func (h *Handler) list(w http.ResponseWriter, r *http.Request) error {
	q := httpx.NewQuery(r)
	lq := ListQuery{
		Status: Status(q.OneOf("status", "pending", "ready", "collected")),
		Limit:  q.Int("limit", 20, 1, 100),
	}
	if raw := q.String("cursor", 200); raw != "" {
		c, ok := listing.DecodeCursor(raw)
		if !ok {
			return apperr.New(apperr.Invalid, "bad-cursor", "The cursor is not valid. Start again from the first page.")
		}
		lq.After = &c
	}
	if err := q.Err(); err != nil {
		return err
	}

	orders, err := h.svc.List(r.Context(), lq)
	if err != nil {
		return err
	}

	meta := cursorMeta{Limit: lq.Limit}
	if len(orders) > lq.Limit {
		orders = orders[:lq.Limit]
		last := orders[len(orders)-1]
		meta.NextCursor = listing.Cursor{Time: last.CreatedAt, ID: last.ID}.Encode()
	}
	return httpx.WriteList(w, orders, meta)
}
```

And register it for the kitchen only: `mux.Handle("GET /orders", staff(httpx.HandlerFunc(h.list)))`.

```bash
curl -s -H "X-Staff-Key: mama-secret" "localhost:8080/orders?status=pending&limit=2"
# {"data":[{...},{...}],"meta":{"limit":2,"nextCursor":"eyJ0IjoiMjAyNi0xMS0yMVQ..."}}

curl -s -H "X-Staff-Key: mama-secret" "localhost:8080/orders?status=pending&limit=2&cursor=eyJ0IjoiMjAyNi0xMS0yMVQ..."
```

The client keeps the same filters, adds the cursor, and repeats until there's no `nextCursor`.

There's no `total` and no "jump to page 9". That's the trade: cursors give you correct, fast "next, next, next", which is exactly what a kitchen screen or an infinite-scroll feed needs. Offset gives you "page 9 of 12", which suits a menu that rarely changes. Use each where it fits.

## Step 9: indexes, so it stays fast
<!-- bite: 245242c8-2c3c-4e83-b324-af04819a74b1 -->

With 40 dishes, none of this needs an index. With 500,000 orders, `WHERE status = 'pending' ORDER BY created_at, id` makes Postgres read the whole table and sort it, for every refresh of every kitchen screen. Indexes fix that. `migrations/004_list_indexes.sql` (lesson 8's practice used `003`):

```sql
-- The kitchen's list: filter by status, then walk in (created_at, id) order.
CREATE INDEX orders_status_created_idx ON orders (status, created_at, id);

-- Any-case "contains" search on dish names.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX dishes_name_trgm_idx ON dishes USING gin (name gin_trgm_ops);
```

1. **The orders index** has the columns in the same order as the query uses them: first the `status` filter, then the sort. Postgres can jump to "pending", then read in order, starting right at the cursor, and stop after 21 rows. The cost of the query no longer depends on how many orders exist.
2. **The trigram index** helps `ILIKE '%egusi%'`. A normal index can only help searches that start at the beginning of the text; a **trigram** index breaks names into three-letter pieces, so "contains" searches can use it too. `pg_trgm` is an extension that comes with Postgres; `CREATE EXTENSION` switches it on.

Run `make migrate`. To see whether Postgres uses an index, put `EXPLAIN` before a query in `psql` (`docker exec -it mama-put-db psql -U postgres mama_put`) and look for `Index Scan` instead of `Seq Scan`. With a tiny table, Postgres may still choose to read it all, because that's faster for 40 rows; it switches as the table grows.

## The Go in this lesson
<!-- bite: afc6b020-4ebd-426b-b730-df273bf551d6 -->

1. **`url.Values`**: The type `r.URL.Query()` returns: a `map[string][]string`, since a name can appear more than once (`?a=1&a=2`). `.Get` gives the first value.
2. **A struct that collects errors** (`Query` with `errs` and `Err()`): Errors are ordinary values, so you can keep them in a slice and report them later. `bufio.Scanner` in the standard library does the same.
3. **`map[string]bool{}`** used as a **set**: The key is what matters; reading a missing key gives `false`, so `q.used[name]` is "has this been read?".
4. **`strconv.Atoi`**: Text to `int` ("ASCII to integer"), with an error if it isn't one.
5. **`*int` for "maybe a number"**: `OptionalInt` returns `nil` when the parameter wasn't sent, the same trick as PATCH's pointer fields.
6. **`allowed ...string`** and **`slices.Contains`**: A variadic parameter, then the standard check "is this value in the slice?".
7. **`for name := range q.values`**: `range` over a map gives each key (in a random order; never rely on it).
8. **`add := func(condition string, value any) { ... }`**: A function stored in a variable, inside another function. It's a closure, so it can append to `where` and `args`.
9. **`fmt.Sprintf("price_naira >= $%d", len(args))`** and **`%%`**: `%d` drops a number into the text; `%%` writes a single `%`.
10. **`args...`**: Passing a slice to a variadic parameter. `Query(ctx, sql, args...)` spreads the slice out as separate arguments.
11. **`strings.NewReplacer(old1, new1, old2, new2, ...)`**: Builds a replacer that swaps all those pairs in one pass. Safe to share between goroutines.
12. **`json.RawMessage`**: A `[]byte` holding JSON exactly as it was. Decoding into `map[string]json.RawMessage` splits an object into its keys without touching the values.
13. **`delete(all, key)`**: Removes a key from a map. Deleting while ranging over the same map is allowed in Go.
14. **`base64.RawURLEncoding`**: Base64 with the URL-safe alphabet (`-` and `_`) and no `=` padding at the end.
15. **`orders[:lq.Limit]`** and **`orders[len(orders)-1]`**: A slice of the first `Limit` items, and the last item. Slicing doesn't copy; it's a view of the same items.
16. **`Status(q.OneOf(...))`**: Converts a `string` to the `Status` type, which is allowed because `Status` is built on `string`.

## Your project so far
<!-- bite: 0d996b8e-4a8a-45a0-b48f-d6a6817a2c60 -->

```text
mama-put/
├── .env
├── .env.example
├── .gitignore
├── Makefile
├── go.mod
├── go.sum
├── migrations/
│   ├── migrations.go
│   ├── 001_create_dishes.sql
│   ├── 002_create_orders.sql
│   ├── 003_add_dish_description.sql   ← from lesson 8's practice
│   └── 004_list_indexes.sql           ← NEW: (status, created_at, id) and a trigram index
├── cmd/
│   ├── api/
│   │   └── main.go
│   └── migrate/
│       └── main.go
└── internal/
    ├── apperr/
    │   └── apperr.go
    ├── app/
    │   └── app.go
    ├── db/
    │   ├── db.go
    │   └── migrate.go
    ├── httpx/
    │   ├── errors.go
    │   ├── json.go                    ← WriteList (data + meta), Pick[T] for field selection
    │   ├── middleware.go
    │   ├── query.go                   ← NEW: Query: Int, OptionalInt, Bool, String, OneOf, Sort, Fields, Err
    │   └── requestid.go
    ├── listing/
    │   ├── listing.go                 ← NEW: SortField
    │   └── cursor.go                  ← NEW: Cursor, Encode, DecodeCursor
    ├── menu/
    │   ├── menu.go                    ← ListQuery, SortableFields, dishFieldNames
    │   ├── store.go
    │   ├── postgres.go                ← List builds WHERE, ORDER BY, LIMIT and OFFSET safely
    │   ├── service.go
    │   ├── service_test.go
    │   └── handlers.go                ← list reads ten parameters, answers with meta
    └── orders/
        ├── orders.go
        ├── postgres.go                ← ListQuery, List with a cursor and LIMIT n+1
        ├── service.go
        ├── service_test.go
        └── handlers.go                ← GET /orders for the kitchen, nextCursor in meta
```

## Common mistakes
<!-- bite: d698099c-62b9-4004-8493-bf7408a75142 -->

1. **Client text in SQL.** `"ORDER BY " + r.URL.Query().Get("sort")` is SQL injection. Look the text up in an allow-list, and use what the list gives back.
2. **No maximum `limit`.** `limit=1000000` is "send everything" again.
3. **Ignoring unknown parameters.** A misspelled filter that silently does nothing looks like a broken app. Answer 400.
4. **Sorting without a unique last column.** Ties come back in any order, and items repeat or vanish between pages. End with `id`.
5. **Offset pagination on a list that changes all the time.** Items get skipped or repeated. Use a cursor.
6. **A cursor less precise than the column.** `time.RFC3339` drops fractions of a second, and every page repeats its last item. Use `RFC3339Nano`, or let `encoding/json` format it.
7. **Counting with different filters than the page.** The count and the page must use the same `WHERE` and the same values.
8. **Forgetting `%` and `_` in search.** They're wildcards in `LIKE`. Escape them.
9. **An index in the wrong column order.** `(created_at, status)` can't help "pending, by time" nearly as well as `(status, created_at, id)`.

## Check your understanding
<!-- bite: 12f94314-6f6b-4e25-b038-2f20e6c86920 -->

1. A client sends `GET /menu?sort=-price_naira`. What happens, and why is that the right answer even though the column really is called `price_naira`?
2. Why does the orders query ask for `limit + 1` rows?
3. The kitchen loads page 1 of pending orders with a cursor, then three of those orders are marked ready, then it loads page 2 with the cursor. Is anything skipped? Why?
4. `q=50%`. What SQL value does Postgres receive, and what does it match?
5. Why does `Pick` always keep `id`?

<details>
<summary>Answers, after your attempt</summary>

1. A 400: `price_naira is not a field you can sort by`. The allow-list is keyed by the API's names (`priceNaira`). Clients should never need to know, or be able to use, the database's names, so we can rename a column without breaking anyone.
2. To find out whether there's a next page without a second query. If the extra row comes back, there's more, so we drop it and send a cursor pointing at the last row we kept. If not, this is the last page.
3. No. The cursor says "after this `(created_at, id)`", and it doesn't matter what happened to rows before it. Page 2 starts with the first pending order after the bookmark, whatever happened above it.
4. The value `50\%`, inside `'%' || $1 || '%'`, so the pattern is `%50\%%`. It matches names containing the literal text "50%", not "50 followed by anything".
5. Because a client needs it to do anything with an item: open it, change it, order it. A list of names with no IDs is a dead end.

</details>

## Practice
<!-- bite: 6d6f79da-7ca7-4476-9d7d-886b0db787fd -->

1. Change `GET /menu/specials` to call the same `list` code with `OnlySpecials: true`, so it gets paging and sorting too. Then check it still answers exactly as before when called with no parameters.
2. Add a `createdAfter` filter to `GET /orders`, an RFC 3339 time, so the kitchen can ask for "today's orders". Add a `Time` method to `httpx.Query` that uses `time.Parse(time.RFC3339Nano, ...)`.
3. Write `internal/httpx/query_test.go`: a table of URLs and the field errors you expect. Include an unknown parameter, `limit=0`, `limit=abc`, `sort=-name,password`, and a URL with no problems.
4. Write a test for `listing.Cursor`: encode a cursor with a time that has microseconds (`time.Date(2026, 11, 21, 12, 0, 0, 123456000, time.UTC)`), decode it, and check the time is **equal** (`Equal`, not `==`) to the original. Then try it with `time.RFC3339` formatting in place of `encoding/json`, and watch it fail.

**Done when** `make test` passes, `GET /menu?maxPrice=2000&sort=-priceNaira&fields=name,priceNaira&limit=2` gives two small objects with `meta.total`, and paging through 50 pending orders with `limit=7` shows each exactly once, even if you mark some ready halfway.

## Before moving on
<!-- bite: 20faa415-bf63-48a5-976f-5c1f16b7a8c1 -->

Mama Put API's lists now do what each client actually needs: filtered, searched, sorted, paged and trimmed, with every parameter checked and every value safely in a placeholder. The menu pages by offset, the busy kitchen list by cursor, and the indexes keep both fast at any size.

Now Mama has a new problem, and it's a happy one. Paystack works in **kobo**, not naira, and the phone app team wants prices as `{ "amount": 150000, "currency": "NGN" }` so they can show "₦1,500.00" properly. That changes the shape of every dish in every response. But last month's app, still on thousands of customers' phones, expects `priceNaira`. Change it, and their app breaks. Don't change it, and the new app can't move forward. That's what API versioning is for, and it's the next lesson.

## Related
<!-- bite: e5cc5585-3015-4e92-847d-ad53f052996a -->

- [[backend/frameworks/net-http/10-versioning|Next: Versioning]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — query parameters as "how you want it"
- [[databases/index|Databases]] — indexes and `EXPLAIN`, in depth
- [[backend/frameworks/express/09-listing|The same lesson in Express]] — the same design with zod

## About this lesson
<!-- bite: ec6c346c-4535-43b9-8e4b-d72745ed7f12 -->

**Level:** Intermediate. Lesson 9 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, pgx v5 and PostgreSQL 17.
