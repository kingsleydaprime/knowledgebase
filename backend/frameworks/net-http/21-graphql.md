---
id: 586d91d6-0076-4bff-b8a9-4b32a26e3855
---

# GraphQL

**GraphQL is a way of building an API where the server publishes one typed description of all its data, and each client sends a query saying exactly which pieces it wants, in the shape it wants them. One request, one endpoint, and the answer has exactly the fields asked for, no more and no fewer.** REST says "here are the resources, take what each URL gives you". GraphQL says "here's everything I have; ask for what you need".

## Before you start
<!-- bite: a3aa71ae-d55e-4a61-aae6-416a5a1dce95 -->

You should have the whole of Parts 1 to 4, up to [[backend/frameworks/net-http/20-real-time|lesson 20]]. GraphQL here sits *beside* REST, on top of the same services, so everything you built is reused. It helps to remember lesson 11, where oapi-codegen wrote Go types for us from a spec: gqlgen does the same job for GraphQL.

After this lesson you will be able to:

1. Read and write a GraphQL schema: types, queries, mutations, inputs, enums, nullability.
2. Generate a type-safe GraphQL server with gqlgen, bound to the domain types you already have.
3. Write resolvers that call the same services, so the rules and permissions can't drift from REST.
4. Fix the N+1 problem with a per-request dataloader.
5. Turn `apperr` errors into GraphQL errors, hide everything else, and refuse queries that ask for too much.
6. Say when GraphQL beats REST, and when it doesn't.

## What to install
<!-- bite: 685c3536-72dd-40d2-bedb-1311a7560887 -->

Nothing outside Go. GraphQL is a language and some libraries; there's no separate server program to run. In the `mama-put` folder:

```bash
go get -tool github.com/99designs/gqlgen@latest
go get github.com/vikstrous/dataloadgen@latest
```

1. **gqlgen** is the most used GraphQL server for Go. It's a **code generator**: you write the schema, it writes the Go that reads queries, checks them and calls your functions. `go get -tool` records it in `go.mod` at an exact version, the same way lesson 11 added oapi-codegen, so everyone runs `go tool gqlgen` and gets the same generated code.
2. **dataloadgen** batches database lookups (step 5). It's the dataloader gqlgen's own documentation recommends.

For syntax colours in your editor, install a GraphQL extension (VS Code has an official one, "GraphQL: Language Feature Support").

## Where we stopped
<!-- bite: 7e9085bc-1eab-4b4b-ad9a-6538846cd05e -->

The new phone app's order screen shows the order, its dish (name, photo, price), and the customer's last three orders underneath. With REST, that's:

1. `GET /v2/orders/42`
2. `GET /v2/menu/1` for the dish
3. `GET /v2/me`
4. `GET /v2/orders?limit=3`, then a `GET /v2/menu/{id}` for each of those dishes.

Six or seven round trips on a 3G connection in a market, each one waiting for the last. And each response carries fields the screen doesn't show. Lesson 9's `fields=` helps with the extra fields; it can't help with the round trips.

The phone team asks: can we ask for all of it, in one go?

## The kid version
<!-- bite: 0b4b7a98-caa4-4f41-9a3d-2fd795418dcc -->

At a REST restaurant, the menu has set plates. Plate 1: rice, stew, chicken. Plate 2: beans, plantain. If you want rice *and* plantain, you order two plates and leave half of each.

At a GraphQL restaurant, you write your own order on a slip: "rice, plantain, one piece of chicken, and the drinks list". The kitchen knows everything it can make, and sends exactly that, on one tray.

**Where the picture stops working.** A greedy customer could write "every dish, and for each dish, every customer who ordered it, and for each customer, every dish *they* ordered..." on one slip. A real kitchen would laugh. Our server has to be taught to refuse slips like that.

## Terms used in this lesson
<!-- bite: 1aacdd20-2567-400b-b538-7e92c65f70bb -->

1. **Schema**: This is the typed description of everything the API offers, written in GraphQL's own language, SDL (the schema definition language).
2. **Type**: This is a shape, like `Dish` with fields `id`, `name` and `price`.
3. **Query**: This is a read. The client sends a query document listing the fields it wants.
4. **Mutation**: This is a write, like `placeOrder`.
5. **Resolver**: This is the function that works out the value of one field. The server calls resolvers to build the answer.
6. **Binding**: This is gqlgen's word for "this GraphQL type is this Go type". A bound field with the same name as a struct field is read straight from the struct, with no resolver.
7. **N+1 problem**: This is when fetching a list of N things runs 1 query for the list and then N more queries, one per item, for something each item needs.
8. **Dataloader**: This is a small helper that collects all the "load dish 1", "load dish 4", "load dish 1" calls made in the same moment and turns them into one batched query.
9. **Connection**: This is GraphQL's usual shape for a paginated list: `edges`, each with a `node` and a `cursor`, plus `pageInfo`.
10. **Complexity**: This is a number gqlgen works out for each query before running it, roughly "how much work could this be?". Queries over a limit are refused.

## Step 1: the schema
<!-- bite: 48f93c4c-8b89-4e69-b84a-65c2773d16c1 -->

`internal/graph/schema.graphqls` (gqlgen's convention is the `.graphqls` ending, with an `s` for schema):

```graphql
scalar Time

type Query {
  menu(first: Int! = 20, after: String, search: String): DishConnection!
  dish(id: ID!): Dish
  me: User
  order(id: ID!): Order
}

type Mutation {
  placeOrder(input: PlaceOrderInput!): PlaceOrderPayload!
}

type Money {
  amount: Int! # in kobo
  currency: String!
}

type Dish {
  id: ID!
  name: String!
  price: Money!
  available: Boolean!
  special: Boolean!
  description: String!
  thumbnailUrl: String
  portionsLeft: Int # staff only; null for everyone else
}

enum OrderStatus {
  PENDING
  READY
  COLLECTED
}

type Order {
  id: ID!
  dish: Dish!
  quantity: Int!
  total: Money!
  status: OrderStatus!
  paidAt: Time
  createdAt: Time!
}

type User {
  id: ID!
  name: String!
  orders(first: Int! = 10, after: String): OrderConnection!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}

type DishConnection {
  edges: [DishEdge!]!
  pageInfo: PageInfo!
}

type DishEdge {
  cursor: String!
  node: Dish!
}

type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
}

type OrderEdge {
  cursor: String!
  node: Order!
}

input PlaceOrderInput {
  dishId: ID!
  quantity: Int!
  idempotencyKey: String!
}

type PlaceOrderPayload {
  order: Order!
}
```

How to read it:

1. **`!` means "never null".** `name: String!` always has a value. `thumbnailUrl: String` may be `null`. Be careful with `!`: if a resolver fails for a non-null field, GraphQL can't put `null` there, so it nulls the *parent* object instead, and that can blank out a large part of the answer. Mark fields `!` only when they truly can't be missing.
2. **Arguments can have defaults**: `first: Int! = 20`. Because of the default, a client can leave `first` out, but the resolver always gets a number.
3. **`input` types** are for arguments. A mutation takes one `input` object, so it can gain fields later without breaking anyone.
4. **Mutations return a payload type**, not the order directly, for the same reason: next year `PlaceOrderPayload` can gain a `checkoutUrl` without changing anything existing.
5. **`enum`** is a fixed set of words. GraphQL enums are written in capitals by convention, so `PENDING` here is our `"pending"`.
6. **`scalar Time`** declares a type GraphQL doesn't have built in. gqlgen knows this one, and maps it to Go's `time.Time`, sent as RFC 3339 text.
7. **`ID`** is GraphQL's type for identifiers. On the wire it's always a string (`"42"`), even when it's a number underneath, so clients never do maths on it.

Now the phone team's screen is **one** request:

```graphql
query OrderScreen($id: ID!) {
  order(id: $id) {
    id
    status
    total { amount currency }
    dish { name thumbnailUrl }
  }
  me {
    name
    orders(first: 3) {
      edges { node { id status dish { name } } }
    }
  }
}
```

And the answer has exactly that shape. Nothing more.

## Step 2: telling gqlgen about our types
<!-- bite: 51f2bdb2-f8f9-46a0-a332-830a1f52452b -->

gqlgen reads the schema and writes Go. Left alone, it would invent a new Go struct for every GraphQL type: a `model.Dish` next to our `menu.Dish`, and we'd copy between them all day. Instead we **bind** the GraphQL types to the domain types we already have. `gqlgen.yml`, at the root of the module:

```yaml
schema:
  - internal/graph/schema.graphqls

exec:
  filename: internal/graph/generated.go
  package: graph

model:
  filename: internal/graph/model/models_gen.go
  package: model

resolver:
  layout: follow-schema
  dir: internal/graph
  package: graph
  filename_template: "{name}.resolvers.go"

models:
  ID:
    model: mamaput/internal/graph/scalar.ID # our int64 IDs, written as strings
  Dish:
    model: mamaput/internal/menu.Dish
    fields:
      portionsLeft:
        resolver: true # staff only: never read straight off the struct
  Order:
    model: mamaput/internal/orders.Order
  User:
    model: mamaput/internal/auth.User
  OrderStatus:
    model: mamaput/internal/orders.Status
    enum_values:
      PENDING:
        value: mamaput/internal/orders.StatusPending
      READY:
        value: mamaput/internal/orders.StatusReady
      COLLECTED:
        value: mamaput/internal/orders.StatusCollected
```

Then generate:

```bash
go tool gqlgen generate
```

and it writes three things:

1. **`internal/graph/generated.go`**: about 4,500 lines that parse queries, check them against the schema, and call resolvers. Never edit it; it's rewritten every time.
2. **`internal/graph/model/models_gen.go`**: Go structs for the GraphQL types we *didn't* bind: `Money`, `PageInfo`, the connections and edges, `PlaceOrderInput`, `PlaceOrderPayload`.
3. **`internal/graph/schema.resolvers.go`**: one empty function for every field that needs code, each with a `panic("not implemented")` inside. This one is yours. When you change the schema and generate again, gqlgen **keeps your function bodies** and adds stubs for the new fields.

Put `//go:generate go tool gqlgen generate` at the top of `internal/graph/resolver.go`, so `go generate ./...` regenerates GraphQL and lesson 11's OpenAPI types together.

### What binding does, field by field

For each field of a bound type, gqlgen looks for a struct field or method with the same name (ignoring case). Look at `Dish`:

1. `name`, `available`, `special`, `description`: found on `menu.Dish`, same names, same types. **Read straight from the struct; no code to write.**
2. `price`: `menu.Dish` has `Price money.Kobo`, but the schema says `Money` (an object with `amount` and `currency`). The types don't match, so gqlgen asks for a **resolver**: `Price(ctx, obj *menu.Dish) (*model.Money, error)`.
3. `thumbnailUrl`: no such field (ours is `PhotoThumb`), so a resolver.
4. `id`: `ID int64`, through our own `ID` scalar (below).

The same goes for `Order`: `quantity`, `status`, `paidAt` and `createdAt` bind straight on; `dish` and `total` need resolvers. And the `enum_values` lines bind `OrderStatus` to our own `orders.Status` constants, so `PENDING` arrives in Go as `orders.StatusPending`, with no `strings.ToUpper` anywhere.

### The binding trap: `portionsLeft`

Now the line with the comment. The first time I generated this schema without it, gqlgen found `PortionsLeft int` on `menu.Dish`, saw the types matched, and bound it **straight to the struct**. No resolver. Every customer could read how many plates were left of everything, which lesson 13 hid from them on purpose.

That's the trap of automatic binding: **gqlgen binds by name, not by permission.** `resolver: true` forces a resolver for that one field, so the permission check has somewhere to live. Any field whose answer depends on who's asking needs it.

The flip side is reassuring. `auth.User` has `Email` and `PasswordHash` on it. Neither is in the schema, so neither can ever be sent: **the schema is the allow-list.** A field that isn't written in the schema doesn't exist as far as any client can tell, whatever the Go struct holds. (Compare REST in Go, where a struct with the wrong `json` tags sends everything. That's why lesson 10 made separate wire types.)

### An `ID` that's an `int64` inside and a string outside

Our IDs are `int64`. GraphQL's `ID` is a string on the wire. gqlgen's own `graphql.Int64` would bind them, but it writes them as JSON *numbers* (`"id": 1`), which breaks the `ID` promise. So we write our own scalar. `internal/graph/scalar/id.go`:

```go
// Package scalar maps GraphQL's ID to our int64 IDs.
package scalar

import (
	"encoding/json"
	"io"
	"strconv"

	"github.com/99designs/gqlgen/graphql"

	"mamaput/internal/apperr"
)

var ErrBadID = apperr.New(apperr.Invalid, "bad-id", "IDs are whole numbers, like \"42\".")

// MarshalID writes an ID the way GraphQL expects: as a string.
func MarshalID(id int64) graphql.Marshaler {
	return graphql.WriterFunc(func(w io.Writer) {
		io.WriteString(w, strconv.Quote(strconv.FormatInt(id, 10)))
	})
}

// UnmarshalID accepts "42" or 42, and refuses anything else.
func UnmarshalID(v any) (int64, error) {
	var s string
	switch v := v.(type) {
	case string:
		s = v
	case json.Number:
		s = v.String()
	case int64:
		s = strconv.FormatInt(v, 10)
	case int:
		s = strconv.Itoa(v)
	default:
		return 0, ErrBadID
	}
	id, err := strconv.ParseInt(s, 10, 64)
	if err != nil || id < 1 {
		return 0, ErrBadID
	}
	return id, nil
}
```

`model: mamaput/internal/graph/scalar.ID` in the config means "a package with functions called `MarshalID` and `UnmarshalID`". gqlgen finds them by name and uses them for every `ID` in the schema. Now `dish(id: ID!)` arrives in our resolver as an `int64`, already checked, and `dish(id: "abc")` is answered with `bad-id` before any resolver runs. It's lesson 2's `PathID`, for GraphQL.

## Step 3: resolvers call the same services
<!-- bite: 8f66afba-cdee-414d-9920-ab1f56ce154b -->

First, the struct every resolver hangs off. `internal/graph/resolver.go`:

```go
// Package graph serves the GraphQL API. Resolvers are thin: every rule lives in the services.
package graph

//go:generate go tool gqlgen generate

import (
	"context"

	"mamaput/internal/auth"
	"mamaput/internal/menu"
	"mamaput/internal/orders"
)

// The services GraphQL needs, declared here by their user (lesson 5).
type Menu interface {
	List(ctx context.Context, q menu.ListQuery) (menu.Page, error)
	Many(ctx context.Context, ids []int64) ([]menu.Dish, error)
}

type Orders interface {
	Get(ctx context.Context, actor auth.Identity, id int64) (orders.Order, error)
	List(ctx context.Context, actor auth.Identity, q orders.ListQuery) ([]orders.Order, error)
	Place(ctx context.Context, customerID *int64, in orders.NewOrder) (orders.Order, error)
}

type Users interface {
	Me(ctx context.Context, id auth.Identity) (auth.User, error)
}

// Resolver holds what every resolver needs. The fields can't be called Menu or
// Orders: gqlgen's resolvers have methods with those names, which would hide them.
type Resolver struct {
	MenuService  Menu
	OrderService Orders
	UserService  Users
}
```

The same pattern as lesson 5: the `graph` package says what it needs, as interfaces, and `run` hands it the real services. The comment on the field names is from experience: gqlgen makes a `queryResolver` type that embeds `*Resolver` and has a method called `Menu` (for the `menu` query). If the struct also had a field called `Menu`, the method would hide it, and `r.Menu.List` would fail to compile with a confusing message.

`Many` is new: the menu service passes it straight to a new store method, one query for many dishes:

```go
func (s *PostgresStore) FindMany(ctx context.Context, ids []int64) ([]Dish, error) {
	rows, err := s.pool.Query(ctx, "SELECT "+dishColumns+" FROM dishes WHERE id = ANY($1)", ids)
	if err != nil {
		return nil, err
	}
	return pgx.CollectRows(rows, scanDishRow)
}
```

pgx sends a Go `[]int64` as a Postgres `bigint[]`, and `= ANY($1)` means "id is any of these". One placeholder, however many IDs, so it's still safe from SQL injection (lesson 8).

Now the resolvers. `internal/graph/schema.resolvers.go` (the parts we write; gqlgen wrote the function headers):

```go
func (r *queryResolver) Menu(ctx context.Context, first int, after *string, search *string) (*model.DishConnection, error) {
	offset, err := offsetFrom(after)
	if err != nil {
		return nil, err
	}
	q := menu.ListQuery{OnlyAvailable: true, Limit: clamp(first, 1, 50), Offset: offset}
	if search != nil {
		q.Search = *search
	}
	page, err := r.MenuService.List(ctx, q)
	if err != nil {
		return nil, err
	}
	conn := &model.DishConnection{PageInfo: &model.PageInfo{}}
	for i := range page.Dishes {
		conn.Edges = append(conn.Edges, &model.DishEdge{
			Cursor: offsetCursor(offset + i + 1),
			Node:   &page.Dishes[i],
		})
	}
	if n := len(conn.Edges); n > 0 {
		conn.PageInfo.EndCursor = &conn.Edges[n-1].Cursor
		conn.PageInfo.HasNextPage = offset+n < page.Total
	}
	return conn, nil
}

func (r *queryResolver) Dish(ctx context.Context, id int64) (*menu.Dish, error) {
	return loadDish(ctx, id)
}

func (r *queryResolver) Me(ctx context.Context) (*auth.User, error) {
	who, ok := auth.IdentityFrom(ctx)
	if !ok {
		return nil, nil // nobody logged in: me is null
	}
	u, err := r.UserService.Me(ctx, who)
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func (r *queryResolver) Order(ctx context.Context, id int64) (*orders.Order, error) {
	who, err := auth.Current(ctx)
	if err != nil {
		return nil, err
	}
	o, err := r.OrderService.Get(ctx, who, id)
	if err != nil {
		return nil, err
	}
	return &o, nil
}

func (r *mutationResolver) PlaceOrder(ctx context.Context, input model.PlaceOrderInput) (*model.PlaceOrderPayload, error) {
	who, err := auth.Current(ctx)
	if err != nil {
		return nil, err
	}
	key := strings.TrimSpace(input.IdempotencyKey)
	if len(key) < 8 || len(key) > 100 {
		return nil, errBadKey
	}
	o, err := r.OrderService.Place(ctx, &who.UserID, orders.NewOrder{
		DishID:         input.DishID,
		Quantity:       input.Quantity,
		IdempotencyKey: key,
	})
	if err != nil {
		return nil, err
	}
	return &model.PlaceOrderPayload{Order: &o}, nil
}

func (r *dishResolver) Price(ctx context.Context, obj *menu.Dish) (*model.Money, error) {
	return naira(obj.Price), nil
}

func (r *dishResolver) ThumbnailURL(ctx context.Context, obj *menu.Dish) (*string, error) {
	if obj.PhotoThumb == "" {
		return nil, nil
	}
	url := "/photos/" + obj.PhotoThumb
	return &url, nil
}

func (r *dishResolver) PortionsLeft(ctx context.Context, obj *menu.Dish) (*int, error) {
	who, ok := auth.IdentityFrom(ctx)
	if !ok || !auth.Can(who, auth.MenuWrite, auth.Resource{}) {
		return nil, nil // not staff: the field is null, not an error
	}
	return &obj.PortionsLeft, nil
}

func (r *orderResolver) Dish(ctx context.Context, obj *orders.Order) (*menu.Dish, error) {
	return loadDish(ctx, obj.DishID)
}

func (r *orderResolver) Total(ctx context.Context, obj *orders.Order) (*model.Money, error) {
	return naira(obj.Total), nil
}

func (r *userResolver) Orders(ctx context.Context, obj *auth.User, first int, after *string) (*model.OrderConnection, error) {
	who, err := auth.Current(ctx)
	if err != nil {
		return nil, err
	}
	q := orders.ListQuery{Limit: clamp(first, 1, 50)}
	if after != nil {
		c, err := decodeOrderCursor(*after)
		if err != nil {
			return nil, err
		}
		q.After = &c
	}
	list, err := r.OrderService.List(ctx, who, q) // the service scopes a customer to their own orders
	if err != nil {
		return nil, err
	}
	return orderConnection(list, q.Limit), nil
}
```

Every resolver gets a `context.Context` first. That's the **same request context** that came through our middleware, so `auth.IdentityFrom(ctx)` finds what lesson 12's `Authenticate` put there, `httpx.LoggerFrom(ctx)` finds the request's logger, and a client hanging up cancels the database queries underneath. Nothing new to learn; it's the context we've been passing since lesson 8.

The thing to notice is what *isn't* here. No SQL. No permission rules. No "20 plates maximum". `PlaceOrder` calls `r.OrderService.Place`, the same function the REST handler calls, so it gets the same shop hours and quantity rules (lessons 6 and 8), the same last-plate transaction (lesson 8), and the same idempotency constraint in the database (lesson 15). `Order` calls `Get(ctx, who, id)`, so Ada asking for Bayo's order gets `order-not-found`, exactly as in REST (lesson 13). That's why lesson 6 put rules in the service, and why lesson 13 made services take the actor. **A second API on top of the same services is a few hundred lines. A second API with its own copy of the rules is a second set of bugs.**

GraphQL-shaped decisions:

1. **Optional login.** `me` returns `null` when nobody's logged in, but `order` needs a login (`auth.Current` gives `login-required`). One request can mix public fields (`menu`) and private ones (`me`), so each resolver decides, not a middleware in front of the whole endpoint. Lesson 12's `Authenticate` already reads a token *if there is one*, so that's all we need in front.
2. **Field-level permissions.** `portionsLeft` returns `nil` unless the caller is staff. In REST, lesson 13 did this in the presenter; here the field's resolver *is* the presenter. That's why the field is `Int`, not `Int!`: `null` has to be a legal answer.
3. **Limits on lists.** `clamp(first, 1, 50)`. A client asking for `menu(first: 1000000)` gets 50. Every list argument in a GraphQL API needs a cap.
4. **Idempotency arrives as a field of the input**, not a header. GraphQL clients usually can't set a header per mutation easily, and it puts the key in the schema where everyone can see it's required. Lesson 15's unique `(customer_id, idempotency_key)` constraint does the work: a retry with the same key gets the original order back. (Lesson 15's middleware isn't in front of `/graphql`, so its "same key, different body" check doesn't run here. The store still promises one order per key, and that's the promise that matters for money.)
5. **Pointers mean "maybe absent".** `after *string` is `nil` when the client didn't send it, and a resolver returns `*menu.Dish` so `nil` can mean `null`.

The small helpers (`naira`, `clamp`, the cursors, and `orderConnection`, which uses lesson 9's "fetch one more than the page" trick to set `hasNextPage`) live in `internal/graph/helpers.go`. The menu's cursor is honest about what it is: lesson 9 pages the menu by offset, so the cursor is an offset, base64-encoded so clients treat it as an opaque string and we can change it later.

## Step 4: serving it
<!-- bite: d35ce641-f170-4c61-96a4-aa8cd0bf0060 -->

`internal/graph/server.go`:

```go
package graph

import (
	"log/slog"
	"net/http"

	"github.com/99designs/gqlgen/graphql/handler"
	"github.com/99designs/gqlgen/graphql/handler/extension"
	"github.com/99designs/gqlgen/graphql/handler/transport"
	"github.com/99designs/gqlgen/graphql/playground"
)

type Options struct {
	Production bool
	MaxCost    int // the most work one query may ask for
}

// Register adds POST /graphql (and, outside production, a playground at GET /graphql).
func Register(mux *http.ServeMux, r *Resolver, log *slog.Logger, opt Options) {
	srv := handler.New(NewExecutableSchema(Config{Resolvers: r, Complexity: costs()}))
	srv.AddTransport(transport.POST{})
	srv.SetErrorPresenter(presentError(log))
	srv.SetRecoverFunc(recoverPanic(log))
	srv.Use(extension.FixedComplexityLimit(opt.MaxCost))
	if !opt.Production {
		srv.Use(extension.Introspection{})
		mux.Handle("GET /graphql", playground.Handler("Mama Put", "/graphql"))
	}

	mux.Handle("POST /graphql", http.MaxBytesHandler(WithLoaders(r.MenuService, srv), 64<<10))
}
```

Line by line:

1. **`handler.New(...)`** makes the gqlgen server, which is an ordinary `http.Handler`. `NewExecutableSchema` and `Config` were generated in step 2. (You'll see `handler.NewDefaultServer` in older tutorials. It's deprecated, because it switches on every transport and extension whether you want them or not. `New` starts with nothing, and we add what we choose.)
2. **`transport.POST{}`**: accept queries as a JSON body on POST. That's all the phone app needs. No GET queries, no WebSockets, no file uploads: every transport you don't add is one less thing to secure.
3. **The error presenter and recover function** are step 6.
4. **`FixedComplexityLimit`** is step 7.
5. **`extension.Introspection{}`**: introspection lets a client download the whole schema, which is how the playground and editor tools know what fields exist. With `handler.New` it's **off** unless added, so we add it only outside production. The playground at `GET /graphql` is a web page where you can type queries and see the schema; also not in production.
6. **`http.MaxBytesHandler(..., 64<<10)`**: the standard library's way to cap a body's size, the same idea as lesson 6's `MaxBytesReader`. No phone screen's query is anywhere near 64 KB.
7. **`WithLoaders`** gives every request its own dataloaders: step 5.

In `app.New`, on the `api` mux, next to REST:

```go
graph.Register(api, &graph.Resolver{
	MenuService:  d.Menu,
	OrderService: d.Orders,
	UserService:  d.Users,
}, d.Logger, graph.Options{Production: d.Production, MaxCost: 300})
```

Because it's on `api`, `/graphql` gets lesson 17's whole chain: request IDs, logging, panic recovery, security headers, CORS, the rate limit and `Authenticate`. Not under `/v1` or `/v2`: step 8 explains why GraphQL doesn't version that way.

Try it. Start the API, open `http://localhost:8080/graphql` in a browser, and type the `OrderScreen` query from step 1 into the playground (put a token in its headers panel as `{"Authorization": "Bearer ..."}`). Or from the terminal:

```bash
curl -s localhost:8080/graphql -H 'Content-Type: application/json' \
  -d '{"query":"{ menu(first: 2) { edges { node { id name price { amount } } } } }"}'
```

```json
{"data":{"menu":{"edges":[{"node":{"id":"1","name":"Jollof rice","price":{"amount":150000}}},{"node":{"id":"2","name":"Ofada stew","price":{"amount":200000}}}]}}}
```

Okay!!!!! One request, exactly the fields asked for, and `"id":"1"` is a string, as `ID` promises.

## Step 5: the N+1 problem, and a dataloader
<!-- bite: bc8cacb9-2630-4263-84f2-b49f41471449 -->

Look at this harmless-looking query:

```graphql
{ me { orders(first: 20) { edges { node { id dish { name } } } } } }
```

Without care: 1 query for the 20 orders, then `Order.dish` runs 20 times, and that's 20 queries for dishes, many of them the same dish (half of Mama's orders are jollof). 21 queries for one small screen. With 50 orders, 51. That's the **N+1 problem**, and every GraphQL API meets it on its first day.

A dataloader fixes it. Each `Load(ctx, id)` call doesn't query at once: it waits a moment to see what else is asked for, then calls *your* fetch function **once** with every ID collected.

"Waits a moment" is where Go differs from JavaScript. Node's DataLoader waits for the end of the current event-loop tick. Go has no event loop: gqlgen runs the resolvers for a list's items **in parallel goroutines**, so 20 `Order.dish` resolvers all call `Load` at nearly the same instant. dataloadgen waits a short, fixed time (we choose 2 milliseconds) for the calls to gather, then runs one fetch with all the IDs. Every goroutine waiting on `Load` gets its own dish back.

`internal/graph/loaders.go`:

```go
package graph

import (
	"context"
	"errors"
	"net/http"
	"time"

	"github.com/vikstrous/dataloadgen"

	"mamaput/internal/menu"
)

// Loaders batch lookups made while one request is being answered.
type Loaders struct {
	Dish *dataloadgen.Loader[int64, menu.Dish]
}

func newLoaders(m Menu) *Loaders {
	return &Loaders{
		Dish: dataloadgen.NewMappedLoader(func(ctx context.Context, ids []int64) (map[int64]menu.Dish, error) {
			dishes, err := m.Many(ctx, ids)
			if err != nil {
				return nil, err
			}
			byID := make(map[int64]menu.Dish, len(dishes))
			for _, d := range dishes {
				byID[d.ID] = d
			}
			return byID, nil
		}, dataloadgen.WithWait(2*time.Millisecond)),
	}
}

type loadersKey struct{}

// WithLoaders gives every request its own, fresh set of loaders.
func WithLoaders(m Menu, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ctx := context.WithValue(r.Context(), loadersKey{}, newLoaders(m))
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func loadersFrom(ctx context.Context) *Loaders {
	return ctx.Value(loadersKey{}).(*Loaders)
}

func loadDish(ctx context.Context, id int64) (*menu.Dish, error) {
	d, err := loadersFrom(ctx).Dish.Load(ctx, id)
	if errors.Is(err, dataloadgen.ErrNotFound) {
		return nil, menu.ErrDishNotFound
	}
	if err != nil {
		return nil, err
	}
	return &d, nil
}
```

Now those 20 orders cost **two** queries: one for the orders, one `= ANY($1)` for all their dishes. Duplicate IDs are fetched once, because the loader also remembers what it already loaded *in this request*. Our test (step 9) counts the calls: 20 orders, alternating two dishes, one call to `Many`.

Three rules the loader is strict about:

1. **Results must match keys.** A plain batch function must return its results in the same order as the IDs, one for one. Postgres returns rows in any order, so that's an easy bug: Ada's order shows Bayo's dish. `NewMappedLoader` removes the bug: we return a **map** from ID to dish, and dataloadgen matches each caller to its own key. An ID missing from the map becomes `dataloadgen.ErrNotFound`, which `loadDish` turns into our `dish-not-found`.
2. **One set of loaders per request.** That memory of "already loaded" is a cache. Share loaders across requests and you'd serve stale dishes forever, and for anything personal, one customer's data to another. `WithLoaders` wraps the gqlgen handler and makes fresh ones in each request's context; they die when the request ends. It's lesson 7's request ID trick: a private key type (`loadersKey struct{}`), so no other package can collide with it.
3. **The fetch gets the context of the first caller in the batch.** Since every caller is part of the same request, that's fine here: it's the same request context either way.

Where does the menu cache from lesson 19 fit? `Many` could check Redis for each ID first. For a menu of thirty dishes that's not worth it yet; one indexed query for a few IDs takes about a millisecond. Measure first (lesson 27), then decide.

## Step 6: errors
<!-- bite: 037d4be1-9856-4b4d-b1b5-dccf0d4fdf95 -->

GraphQL reports errors differently from REST. The HTTP status is usually **200**, and the body has `data` (what worked) and `errors` (what didn't), side by side:

```json
{
  "errors": [
    {
      "message": "There's no such order.",
      "path": ["order"],
      "extensions": { "code": "order-not-found", "kind": "not_found" }
    }
  ],
  "data": { "order": null, "me": { "name": "Ada" } }
}
```

That's real output from our test: `order` failed, `me` still worked, and the screen gets both. This is a feature. But it means clients must look at `errors`, not just the status.

Our services return `*apperr.Error`s. Some errors are safe to show (a business rule, a bad cursor) and some aren't (a database that's down, whose message might include an internal address). gqlgen's **error presenter** decides, for every error a resolver returns. `internal/graph/errors.go`:

```go
package graph

import (
	"context"
	"errors"
	"log/slog"

	"github.com/99designs/gqlgen/graphql"
	"github.com/vektah/gqlparser/v2/gqlerror"

	"mamaput/internal/apperr"
)

// presentError decides what the client may see of an error.
func presentError(log *slog.Logger) graphql.ErrorPresenterFunc {
	return func(ctx context.Context, err error) *gqlerror.Error {
		var appErr *apperr.Error
		if errors.As(err, &appErr) && appErr.Kind != apperr.Internal {
			gqlErr := gqlerror.WrapPath(graphql.GetPath(ctx), err)
			gqlErr.Message = appErr.Message
			gqlErr.Extensions = map[string]any{"code": appErr.Code, "kind": appErr.Kind.String()}
			if len(appErr.Fields) > 0 {
				gqlErr.Extensions["fields"] = appErr.Fields
			}
			return gqlErr
		}

		var gqlErr *gqlerror.Error
		if errors.As(err, &gqlErr) && gqlErr.Unwrap() == nil {
			return gqlErr // GraphQL's own: a bad query, a wrong argument type
		}

		// Anything else is a bug or an outage: log all of it, show none of it.
		log.ErrorContext(ctx, "graphql resolver failed", "path", graphql.GetPath(ctx).String(), "error", err)
		return &gqlerror.Error{
			Message:    "Something went wrong on our side.",
			Path:       graphql.GetPath(ctx),
			Extensions: map[string]any{"code": "internal"},
		}
	}
}

func recoverPanic(log *slog.Logger) graphql.RecoverFunc {
	return func(ctx context.Context, p any) error {
		log.ErrorContext(ctx, "graphql resolver panicked", "panic", p)
		return errors.New("panic in resolver") // goes through presentError, so it's hidden
	}
}
```

Three cases, in order:

1. **One of ours**, an `*apperr.Error` that isn't `Internal`: show its message, with the same `code` and `kind` REST uses. The phone team handles `not-enough-portions` the same way in both APIs. `errors.As` finds it even when it's been wrapped with `%w` on the way up (lesson 7). `WrapPath` keeps `path`, so the client knows *which* field failed.
2. **GraphQL's own**: a query that asks for a field that doesn't exist, or the wrong type of argument. These come from gqlgen itself, wrap nothing, and are safe and useful to show.
3. **Anything else**, hidden. In the test, a fake store fails with `pq: connection refused at 10.0.0.3`. The client sees "Something went wrong on our side." with `code: internal`; the log gets the whole thing, with the request ID from lesson 7, since `ErrorContext` is given the request's context.

Lesson 3's `RecoverPanic` middleware won't catch a resolver panic: gqlgen runs resolvers in goroutines of its own, and a panic can only be recovered in the goroutine where it happened. gqlgen catches them there and calls our **recover function**, which logs and returns an ordinary error, which the presenter then hides. Without `SetRecoverFunc`, gqlgen's default would print the panic to standard error, outside our structured logs.

A query gqlgen can't even read (a field that doesn't exist) is answered with HTTP **422** and `GRAPHQL_VALIDATION_FAILED`, before any resolver runs. Everything after that point is 200.

## Step 7: refusing expensive queries
<!-- bite: 8550be96-8506-4963-9500-fb470998b6f3 -->

In REST, each URL does a known amount of work. In GraphQL, the *client* writes the query, so the client chooses the work. A friendly client asks for one screen. A hostile one asks for the same list 500 times under different names (that's an **alias**: `a: menu(...) b: menu(...)`), or nests lists inside lists. Each is one small HTTP request, and each can make the server do enormous work.

gqlgen's answer is **complexity**. Before running a query, it adds up a cost for every field. By default each field costs 1, plus whatever's inside it. That's too kind to lists: `menu(first: 50) { ... }` can return 50 dishes, so it should cost 50 times what's inside. We tell it so, with functions it generated for us:

```go
// costs makes lists cost what they could return, not 1.
func costs() ComplexityRoot {
	var c ComplexityRoot
	c.Query.Menu = func(child int, first int, _ *string, _ *string) int {
		return 1 + clamp(first, 1, 50)*child
	}
	c.User.Orders = func(child int, first int, _ *string) int {
		return 1 + clamp(first, 1, 50)*child
	}
	return c
}
```

`child` is the cost of what's inside one item; gqlgen works it out and passes it in, along with the field's arguments. Then `FixedComplexityLimit(300)` refuses anything over 300 **before any resolver runs**. From the test:

```text
{ a: menu(first: 50) { edges { node { name price { amount } } } }
  b: menu(first: 50) { edges { node { name } } } }
```

```json
{"errors":[{"message":"operation has complexity 402, which exceeds the limit of 300","extensions":{"code":"COMPLEXITY_LIMIT_EXCEEDED"}}],"data":null}
```

Aliases don't help an attacker: every alias is counted. The phone app's real screens cost 20 to 80. Set the limit comfortably above your biggest real query, and log the cost of each operation (lesson 27) so you know when a new screen gets close.

The full set of defences, from simplest:

1. **Caps on every list** (`clamp` in step 3), so nothing returns a million items.
2. **A complexity limit** that counts lists properly, as above. It also limits depth in practice: nesting multiplies cost.
3. **A body size limit** (`MaxBytesHandler`), so nobody sends a 10 MB query.
4. **The rate limit** from lesson 14, which already runs in front of `/graphql`.
5. **Trusted documents**: the phone app's queries are registered when the app is built, each under a hash, and the production server *only* runs registered ones. Nobody can send a new query at all. It's the strongest protection, for an API used only by your own apps. (gqlgen's `extension.AutomaticPersistedQuery` is a different thing, despite the similar name: it lets a client send a hash instead of a long query to save bandwidth, but it'll still accept any new query. It saves bytes, it doesn't protect you.)

And CSRF: since we use Bearer tokens, not cookies, a malicious website can't make Ada's browser send a logged-in GraphQL request, because the token isn't attached automatically. Accepting only `application/json` POSTs (all `transport.POST` does) blocks the simple-form trick too.

## Step 8: GraphQL and the rest of the API
<!-- bite: 808d482f-16ac-462b-bbfb-abc10b476353 -->

**Versioning.** GraphQL APIs usually don't have v1 and v2. Because clients name every field they use, you can **add** freely (old clients don't ask for new fields), and for changes you mark the old field deprecated:

```graphql
type Dish {
  priceNaira: Int @deprecated(reason: "Use price, which is in kobo.")
  price: Money!
}
```

The playground and editor tools show the warning. Then you measure which clients still ask for `priceNaira` (lesson 27 can log the fields each operation uses), and remove it when nobody does. It's lesson 10's "add, don't change", built into the language.

**Docs.** The schema *is* the documentation. Clients with introspection can download it; in production, where introspection is off, give the phone team the `.graphqls` file itself, from the repository. Turning introspection off is a speed bump for strangers mapping your API, not real security: the rules are enforced in the services anyway.

**Caching.** REST GETs cache well with HTTP (lesson 19's `ETag` and `Cache-Control`), because each URL is one resource. GraphQL queries are POSTs to one URL, so HTTP caching mostly doesn't apply. The Redis cache in the menu service still works for both, because it sits *below* the API layer. Another win for putting it there.

**Files, webhooks, streams.** Photo uploads, Paystack's webhooks and the kitchen's SSE stay REST. GraphQL is good at one thing: letting clients read and write a graph of data flexibly.

## Step 9: testing
<!-- bite: 8bdba269-13bf-43f4-b9e4-d619a49189f0 -->

GraphQL is just HTTP, so lesson 16's `apptest` works unchanged: `POST /graphql` with a JSON body, through the whole app. For the `graph` package on its own, build the handler with fake services and send queries to it with `httptest`:

```go
func gql(t *testing.T, h http.Handler, token, query string) map[string]any {
	t.Helper()
	body, _ := json.Marshal(map[string]any{"query": query})
	req := httptest.NewRequest("POST", "/graphql", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	if token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, req)
	var out map[string]any
	if err := json.Unmarshal(rec.Body.Bytes(), &out); err != nil {
		t.Fatalf("not JSON: %s", rec.Body)
	}
	return out
}

func TestOrdersLoadTheirDishesInOneBatch(t *testing.T) {
	x := apptest.New(t)
	ada := x.Login(t, "ada@example.com")
	x.PlaceOrders(t, ada, 20) // alternating jollof and ofada

	out := gql(t, x.Handler, ada, `{ me { orders(first: 20) { edges { node { dish { name } } } } } }`)

	if out["errors"] != nil {
		t.Fatalf("errors: %v", out["errors"])
	}
	if got := x.Menu.ManyCalls(); got != 1 {
		t.Errorf("Many was called %d times, want 1", got)
	}
}
```

(`PlaceOrders` and a counting `ManyCalls` on the in-memory menu store are small additions to lesson 16's `apptest`.)

What to test, each as its own test:

1. **The same rules as REST**: `placeOrder` with 21 plates gets `extensions.code == "too-many-plates"`, the same code as REST, with no GraphQL code mentioning 20.
2. **Ownership**: Ada asking for Bayo's order gets `order-not-found`, and `data.order` is `null`.
3. **Field permissions**: `portionsLeft` is `null` for a customer and a number for staff. This is the test that catches the binding trap from step 2.
4. **Hidden errors**: a fake store that fails with a message containing an address; the client sees `code: internal` and not the address.
5. **Bad input**: `dish(id: "abc")` gets `bad-id`.
6. **Cost**: the two-alias query from step 7 is refused with `COMPLEXITY_LIMIT_EXCEEDED`, and a real screen's query isn't.
7. **The batch**: the test above.

Run them with `-race`: gqlgen's parallel resolvers and the loader's shared batch are exactly where a data race would hide, and the race detector finds it.

One more check belongs in CI (lesson 29): run `go generate ./...` and then `git diff --exit-code`. If someone changed the schema and forgot to regenerate, the diff isn't empty and the build fails.

## The Go in this lesson
<!-- bite: 3a2ade78-06dd-4728-a509-44240d595f99 -->

1. **`go get -tool`** and **`go tool gqlgen generate`**: The generator is recorded in `go.mod` at an exact version and run through `go tool`, as in lesson 11.
2. **Code generation with your code kept**: gqlgen rewrites `generated.go` and `models_gen.go` every time, but keeps the function bodies in `schema.resolvers.go`. Edit only the files it says are yours.
3. **Binding a GraphQL type to a Go struct**: Fields with matching names and types are read straight from the struct; the rest get a resolver. `resolver: true` forces one.
4. **A custom scalar as two functions**: `MarshalID(int64) graphql.Marshaler` and `UnmarshalID(any) (int64, error)`, found by name. `graphql.WriterFunc` turns a function that writes to an `io.Writer` into a `Marshaler`.
5. **A type switch, `switch v := v.(type)`**: Each `case` gets `v` as that type. Input can arrive as a `string` or a `json.Number`, so we handle both.
6. **An embedded pointer, `type queryResolver struct{ *Resolver }`**: `queryResolver` gets all of `Resolver`'s fields and methods as its own. A method with the same name as a promoted field hides it, which is why our fields are called `MenuService`, not `Menu`.
7. **Pointer results as `null`**: A resolver returning `(*menu.Dish)(nil), nil` sends `null` with no error. `return nil, nil` is how `me` says "nobody's logged in".
8. **`&page.Dishes[i]`**: The address of an item in the slice itself. Writing `for _, d := range page.Dishes { ... &d }` would also work since Go 1.22 (each loop gives `d` a fresh variable), but indexing makes it plain that the edge points into the page.
9. **`dataloadgen.Loader[int64, menu.Dish]`**: A generic type with two type parameters, the key and the value. `NewMappedLoader` infers them from the fetch function you pass.
10. **`context.WithValue` with a private key type**: Gives each request its own loaders, where no other package can reach or replace them.
11. **`= ANY($1)` with a `[]int64`**: pgx turns a Go slice into a Postgres array, so one placeholder carries any number of IDs.
12. **`http.MaxBytesHandler(h, n)`**: Wraps a handler so the request body can't be longer than `n` bytes.
13. **`max(lo, min(n, hi))`**: The built-in `min` and `max` (Go 1.21) make a one-line clamp.
14. **`errors.As(err, &appErr)`**: Finds an `*apperr.Error` anywhere in a chain of wrapped errors, as in lesson 7.

## Your project so far
<!-- bite: 216e3f9a-7391-42c6-a4e2-b669d55e2024 -->

```text
mama-put/
├── go.mod                         ← tool github.com/99designs/gqlgen; dataloadgen
├── gqlgen.yml                     ← NEW: bindings to menu.Dish, orders.Order, auth.User, orders.Status; ID scalar
└── internal/
    ├── app/
    │   └── app.go                 ← graph.Register on the api mux (full middleware chain)
    ├── graph/                     ← NEW package
    │   ├── schema.graphqls        ← the schema: Query, Mutation, Dish, Order, User, connections, inputs
    │   ├── resolver.go            ← Resolver with the services it needs, as interfaces; //go:generate
    │   ├── schema.resolvers.go    ← thin resolvers into the same services; portionsLeft for staff only
    │   ├── helpers.go             ← naira, clamp, cursors, orderConnection
    │   ├── loaders.go             ← per-request dish loader (mapped, 2 ms wait), WithLoaders
    │   ├── errors.go              ← presentError (apperr shown, GraphQL's own shown, the rest hidden), recoverPanic
    │   ├── server.go              ← Register: POST only, complexity costs and limit, introspection and playground outside production
    │   ├── graph_test.go          ← rules, ownership, field permissions, hidden errors, bad IDs, cost, one batch
    │   ├── generated.go           ← GENERATED: never edit
    │   ├── model/models_gen.go    ← GENERATED: Money, PageInfo, connections, input and payload
    │   └── scalar/id.go           ← NEW: MarshalID, UnmarshalID
    └── menu/
        ├── service.go             ← Many
        └── postgres.go            ← FindMany with = ANY($1)
```

## Common mistakes
<!-- bite: 1a97f8b0-5623-420d-b3b1-1e26db6ce505 -->

1. **Business rules in resolvers.** Then REST and GraphQL disagree. Resolvers call services; services hold the rules.
2. **Trusting automatic binding with private fields.** gqlgen binds by name. A field only some people may see needs `resolver: true`, and a test.
3. **No dataloader.** Every list of N items costs N+1 queries.
4. **Loaders shared between requests.** Stale data forever, or one person's data served to another. Make them per request, in the context.
5. **A batch function that returns results in the wrong order.** Use a mapped loader, or map back over the keys.
6. **Default complexity for lists.** A list that costs 1 lets one query fetch thousands of rows. Make lists cost what they could return.
7. **No cap on `first`.** `menu(first: 1000000)` must get 50.
8. **Showing raw errors.** A database message reaching the phone. Present your own `apperr`s; hide the rest.
9. **No recover function.** Resolver panics happen in gqlgen's goroutines, out of reach of your panic middleware.
10. **`!` everywhere.** One failing non-null field nulls its parent, and a whole screen goes blank.
11. **`handler.NewDefaultServer` in production.** It switches on transports and introspection you didn't choose.
12. **Editing `generated.go`.** The next `go generate` throws your change away.
13. **Checking only the HTTP status on the client.** GraphQL errors usually come with 200.

## Check your understanding
<!-- bite: 5fc5c053-99df-4efa-b295-e3617a88a454 -->

1. Why does `placeOrder` refuse 21 plates, when no code in the `graph` package mentions 20?
2. What would have happened if we had left `resolver: true` off `portionsLeft`, and why can't the same mistake leak a customer's password hash?
3. A query asks for 30 orders and each order's dish. How many SQL queries run with and without the dataloader, and how does Go's loader know when to stop waiting for more IDs?
4. Why are the loaders made in `WithLoaders`, per request, and not once in `run`?
5. A resolver's database call fails with a message that includes the database's address. What does the client see, and what does the log get?
6. Why doesn't lesson 3's `RecoverPanic` catch a panic inside a resolver?
7. Give one reason Mama Put keeps REST as its main public API.

<details>
<summary>Answers, after your attempt</summary>

1. The resolver calls `OrderService.Place`, the same function as REST, and the quantity rule lives there (lessons 6 and 8). Any API built on the service gets every rule for free.
2. gqlgen would have bound it straight to `menu.Dish.PortionsLeft`, with no resolver, so every customer would have seen it. `PasswordHash` can't leak the same way because it isn't in the schema at all, and gqlgen only ever sends fields the schema declares.
3. Without: 1 for the orders plus 30 for the dishes, 31 in all. With: 2, one for the orders and one `= ANY($1)` for all their dishes, with duplicates fetched once. gqlgen runs the 30 `Order.dish` resolvers in parallel goroutines; the loader waits a fixed 2 milliseconds after the first `Load`, gathering every ID asked for in that window, then fetches them together.
4. Each loader remembers what it loaded. Made once and shared, it would keep stale dishes forever and could hand one user's data to another. Made per request, its memory lasts exactly one request.
5. "Something went wrong on our side." with `code: internal`, at the right `path`. The log gets the full error with the request ID, through `log.ErrorContext(ctx, ...)`.
6. gqlgen runs resolvers in goroutines of its own, and `recover` only works in the goroutine that panicked. That's why `SetRecoverFunc` exists.
7. Any of: HTTP caching and CDNs work naturally with REST GETs; it's simpler for outside developers; each URL has a known cost, which is easier to rate-limit and secure; webhooks, uploads and streams are plain HTTP anyway.

</details>

## Practice
<!-- bite: ede40324-8d8c-4fcb-91f3-517871a57f3b -->

1. Write the tests from step 9 in `internal/graph/graph_test.go`, with fake services, and run them with `-race`.
2. Add a `startPayment(orderId: ID!): Checkout!` mutation (with `reference` and `checkoutUrl`) that calls lesson 17's `payments.Service.StartCheckout`. Regenerate, and watch gqlgen add the stub while keeping your other resolvers.
3. Add an `operation` log line: a gqlgen `extension` (or an `AroundOperations` function) that logs each operation's name (`OrderScreen`), its complexity and how long it took. Lesson 27 will turn it into a metric.
4. Add `specials: [Dish!]!` to `Query`, from the menu service's `Specials`, and give it a complexity of `10 * child`.
5. Add the CI check: `go generate ./... && git diff --exit-code`.

**Done when** the phone team's `OrderScreen` query returns everything in one request; a 20-order query runs exactly two SQL queries; `portionsLeft` is `null` for customers; every error `code` matches its REST twin; the two-alias query is refused before any resolver runs; and `make test` passes with `-race`.

## Before moving on
<!-- bite: 26aa5cda-3c6d-44ee-bbff-a7f5c76014db -->

Mama Put API now speaks two languages to the outside world: REST for everyone, GraphQL for the phone app, both on the same services, so the rules can't drift apart. gqlgen wrote the boring part, and binding to our own types means there's no second set of structs to keep in step.

Both APIs are made for clients far away: phones, browsers, partners. But soon a different kind of client arrives: **our own services**. In Part 6 we split out a notifications service, and it will need to ask the main API things like "what's dish 1 called?" thousands of times a day. For that, JSON over HTTP is slow and loose. Services talking to services want a strict contract, small binary messages and built-in deadlines. That's gRPC, and Go is its home ground. Next lesson.

## Related
<!-- bite: 7967255b-441a-4af6-980e-7a7eb01f25bb -->

- [[backend/frameworks/net-http/22-grpc|Next: gRPC]]
- [[backend/frameworks/express/21-graphql|The same lesson in Express]] — GraphQL Yoga and DataLoader, schema first without code generation
- [[backend/frameworks/net-http/11-api-docs|API Docs with OpenAPI]] — the other code generator, run the same way
- [[backend/frameworks/net-http/09-listing|Pagination, Filtering, Searching, Sorting and Field Selection]] — the REST answer to "only the fields I need"
- [[backend/02-api-design/index|API Design]] — REST, GraphQL and gRPC side by side

## About this lesson
<!-- bite: 7ff94a4e-2ac0-4a5a-8ed5-fd1e9d609aff -->

**Level:** Intermediate → Advanced. Lesson 21 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, gqlgen v0.17 and dataloadgen. Covers the GraphQL schema language (types, nullability, enums, inputs, payload types, connections, custom scalars), schema-first code generation with gqlgen as a Go tool, binding GraphQL types to existing domain types and the trap of automatic binding for private fields, a custom `ID` scalar over `int64`, resolvers as thin calls into the same services with the actor from the request context, optional login and field-level permissions, caps on list sizes, idempotency keys as input fields, the N+1 problem and per-request mapped dataloaders that batch across goroutines, partial results and an error presenter with stable codes, recovering resolver panics, complexity limits that count lists, trusted documents versus automatic persisted queries, deprecation instead of versions, introspection, and testing GraphQL with `httptest` and the race detector.
