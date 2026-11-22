---
id: 825eb9f3-831c-41ed-9e7b-7931204c4aab
---

# Versioning

**Versioning an API means you can change its shape for new clients without breaking the old clients that still depend on the old shape: both versions run side by side, each client says which one it speaks, and the old one is retired on a date everyone was told about.** In Go, the clean way is to keep **one** set of rules and data, and give each version its own small layer at the door: its own request and response structs, and its own routes.

## Before you start
<!-- bite: daa85d9d-6617-48a1-9e28-5b9400cdddff -->

You should have:

1. Finished [[backend/frameworks/net-http/09-listing|lesson 9]], so `GET /menu` filters, sorts, pages and selects fields.
2. Read [[backend/02-api-design/01-apis-and-rest|APIs and REST]] if "breaking change" is a new phrase.

After this lesson you will be able to:

1. Tell a breaking change from a safe one, and avoid needing a version when you can.
2. Compare the four ways a client can ask for a version, and choose one.
3. Separate the app's own types from the shapes it sends, so each version is a translator at the door.
4. Run v1 and v2 side by side from one service and one database.
5. Change how data is stored (naira to kobo) without the API noticing.
6. Deprecate a version with standard headers, measure who still uses it, and switch it off kindly.

## Where we stopped
<!-- bite: 82fa58d0-48a5-490f-a4fc-5148c4c7a2de -->

Paystack works in **kobo**, and the new phone app wants prices as `{ "amount": 150000, "currency": "NGN" }`. But last month's app, on thousands of phones, reads `priceNaira`. Rename the field and every old app shows an empty price, or crashes. Don't, and the new app can't move forward.

There's a second, hidden problem. The database stores whole naira. Paystack will tell us about payments in kobo, and one day Mama will sell a ₦750.50 snack. Prices should be stored in kobo too. That's a storage change, and it should be invisible to every client.

## The kid version
<!-- bite: e3a37daa-f960-4f63-af6d-db277db1a4d4 -->

Mama prints a new menu board with prices in a new style. But her regular customers have the old paper menu folded in their pockets, and they order from it by number. If the numbers on the new board are different, they'll order the wrong food.

So she keeps both. The old board stays by the gate, with a note: "this board goes away on 1 June, please use the new one". The new board hangs by the pots. Both are read out from the same pots, the same food, the same kitchen. Only the board is different.

**Where the picture stops working.** Mama can see who's still reading the old board. Your API can too, but only if you log it, and the "customers" are programs that won't read a note. You have to tell them in ways a program understands: headers, and finally a clear "this board is gone" answer.

## Terms used in this lesson
<!-- bite: c75d72f9-85a4-42ee-a024-c5ffa719ba70 -->

1. **Breaking change**: This is a change that makes a correctly written old client stop working: removing or renaming a field, changing its type or meaning, or making something optional required.
2. **Version**: This is a named, fixed shape of the API that clients can rely on, like `v1`. Everything inside one version only ever changes in safe ways.
3. **Domain type**: This is the app's own idea of a thing, like `menu.Dish`, used by the service and the store. It's shaped for the code, not for any client.
4. **Wire type**: This is also called a **DTO**, a data transfer object. It's a struct shaped exactly like what's sent or received in one version, like `dishV1`. It exists only to be turned into JSON, or read from it.
5. **Presenter**: This is a function that turns a domain type into a wire type for one version.
6. **Deprecation**: This means announcing that a version will be removed, while it still works.
7. **Sunset**: This is the date a deprecated version stops working.
8. **Tolerant reader**: This is a client that ignores fields it doesn't know. Adding a field is only safe because good clients are tolerant readers.

## Step 1: what counts as breaking
<!-- bite: 54ffcaae-7d1a-45ef-9b13-52976a311584 -->

Before choosing **how** to version, know **when** you need to. Most changes don't need a new version at all.

**Safe, in the same version:**

1. Adding a new route.
2. Adding a new **optional** field to a response, like `description`. Tolerant readers ignore it.
3. Adding a new **optional** query parameter or body field.
4. Making a validation rule looser, like allowing names up to 120 characters instead of 80.

**Breaking, needs a new version:**

1. Removing or renaming a field (`priceNaira` → `price`).
2. Changing a field's type or meaning. `price` in naira becoming `price` in kobo, with the same name, is the most dangerous of all, because nothing **looks** broken: the old app just shows ₦150,000 jollof.
3. Making an optional input field required.
4. Making validation stricter, like names now at most 40 characters.
5. Changing status codes, error codes, or the response envelope.
6. Changing what a filter or a sort means.

A good habit: **add, don't change.** If you can give clients the new thing next to the old thing, you don't need a new version. We could add `price` alongside `priceNaira` in v1, and often that's the right call. We'll build a real v2 anyway, because one day you'll need it, and because v2 also lets new clients **send** prices in kobo.

## Step 2: the four ways to say which version
<!-- bite: 924ae6dc-055a-4292-bd7c-a1fe028a3dff -->

| Way | Looks like | Good | Costs |
|---|---|---|---|
| **In the path** | `GET /v2/menu` | obvious in every log line, browser and `curl`; easy to route and cache | the URL changes; some say a version isn't part of a resource's name |
| **In a header** | `Api-Version: 2` | URLs stay clean | invisible in a browser, easy to forget; caches must be told it matters (`Vary`) |
| **By media type** | `Accept: application/vnd.mamaput.v2+json` | the most correct by HTTP's rules: same resource, different form | awkward to type and test; few people know it |
| **By query parameter** | `GET /menu?api-version=2` | easy to add to any URL | mixes versions with filters; easy to drop by accident |

There's a fifth style worth knowing: **dated versions**, like Stripe's `Stripe-Version: 2026-11-01`. Every breaking change gets a date, and each client is pinned to the date it signed up. It's powerful and a lot of work, best for big public APIs.

For Mama Put we choose **the path**. It's what most public APIs do, and anyone can see the version in a log line. All four ride on the same idea underneath, though, and step 7 shows the header way is a small difference.

## Step 3: separate what the app knows from what it sends
<!-- bite: e23da634-992c-4db1-a625-a968d388838a -->

Up to now, `menu.Dish` has done two jobs. It's what the store returns and the service works with, **and**, through its `json` tags, it's exactly what clients receive. That was fine while there was one shape. With two versions, one struct can't be both `priceNaira` and `price`.

So the jobs split:

1. **`menu.Dish` is the domain type.** It's shaped for the code: it holds the price in kobo, as a number type of its own. It has **no** `json` tags, because it's never sent as it is.
2. **Each version has its own wire types**, with `json` tags, shaped for clients: `dishV1`, `dishV2`.
3. **A presenter per version** copies one into the other.

That might feel like extra typing, and it is. It's also what stops a renamed field in your Go code from silently renaming a field in your public API. Once the shapes are separate, the API only changes when you change the wire types, on purpose.

First, a small type for money, so nobody mixes up naira and kobo again. `internal/money/money.go`:

```go
// Package money keeps amounts in kobo, so they're always whole numbers.
package money

// Kobo is an amount of money in kobo. ₦1 is 100 kobo.
type Kobo int64

func FromNaira(naira int64) Kobo { return Kobo(naira * 100) }

// Naira gives the amount in whole naira, rounding down.
func (k Kobo) Naira() int64 { return int64(k) / 100 }

// Amount is how v2 sends money: an amount in kobo and a currency.
type Amount struct {
	Amount   int64  `json:"amount"   validate:"required,gt=0,lte=100000000"`
	Currency string `json:"currency" validate:"required,eq=NGN"`
}

func NGN(k Kobo) Amount { return Amount{Amount: int64(k), Currency: "NGN"} }
```

Why a type of its own instead of a plain `int64`? Because then Go **won't let you mix them up**. A function that takes `money.Kobo` refuses a plain naira number unless you convert it on purpose. The bug "we charged 1,500 kobo (₦15) instead of ₦1,500" can't happen by accident.

And why kobo, never naira with a decimal point? Because computers store decimals like 0.1 inexactly, and money must add up to the kobo. Whole kobo in an integer is exact. Every payment system works this way.

The domain types in `internal/menu/menu.go` lose their tags and gain kobo:

```go
type Dish struct {
	ID           int64
	Name         string
	Price        money.Kobo
	Available    bool
	Special      bool
	PortionsLeft int
	Description  string
	CreatedAt    time.Time
}

type NewDish struct {
	Name         string
	Price        money.Kobo
	Special      bool
	PortionsLeft int
	Description  string
}

type DishChanges struct {
	Name         *string
	Price        *money.Kobo
	Available    *bool
	Special      *bool
	PortionsLeft *int
	Description  *string
}
```

The `validate` tags move off these too, onto the wire types, because what's valid to **send** depends on the version.

## Step 4: store kobo, without the API noticing
<!-- bite: ba2feabb-8b38-48d6-b41f-b585460f1c87 -->

Now the storage change. `migrations/005_prices_in_kobo.sql`:

```sql
ALTER TABLE dishes RENAME COLUMN price_naira TO price_kobo;
ALTER TABLE dishes ALTER COLUMN price_kobo TYPE bigint;
UPDATE dishes SET price_kobo = price_kobo * 100;

ALTER TABLE orders RENAME COLUMN total_naira TO total_kobo;
ALTER TABLE orders ALTER COLUMN total_kobo TYPE bigint;
UPDATE orders SET total_kobo = total_kobo * 100;
```

It runs in one transaction (our migration runner from lesson 8 does that), so it's either fully done or not at all. Run `make migrate`. Then in the stores, every `price_naira` becomes `price_kobo`, and every `total_naira` becomes `total_kobo`, and `scanDish` scans into `&d.Price`. pgx scans a `bigint` into a `money.Kobo` because `Kobo` is built on `int64`.

One honest warning. This migration is safe here because Mama Put API isn't live yet: we stop the app, migrate, start the new code. On a live system with several copies running, the old code would still be reading `price_naira` for a few seconds after the rename, and fail. Live systems change columns in steps ("add the new column, write both, switch reads, drop the old"), which lesson 29 shows when it deploys a migration with no downtime.

Since this changes the meaning of what's stored, the `CHECK` from lesson 8 still says `> 0`, which is still right. And the sort allow-list now maps to `price_kobo`.

## Step 5: one service, two translators at the door
<!-- bite: 50c2d996-1ace-4033-bee2-346383524f3b -->

Here's the key idea: **versions differ at the edge, not inside.** v1 and v2 share the same `menu.Service`, the same rules, the same store and the same database. Only the shapes at the door change.

`internal/menu/versions.go`:

```go
package menu

import (
	"net/http"

	"mamaput/internal/httpx"
	"mamaput/internal/money"
)

// Version is everything that differs between API versions of the menu.
type Version struct {
	Present       func(Dish) any
	ReadNew       func(w http.ResponseWriter, r *http.Request) (NewDish, error)
	ReadChanges   func(w http.ResponseWriter, r *http.Request) (DishChanges, error)
	Fields        []string          // what ?fields= may name
	Sortable      map[string]string // what ?sort= may name
	PriceInFilter money.Kobo        // what 1 means in ?minPrice=1 (₦1 in v1, 1 kobo in v2)
}
```

A `Version` is a bundle of functions and settings: how to show a dish, how to read a new one, how to read changes, and which field names this version's clients use. The handlers will take one, and never ask which version it is.

**v1** keeps exactly the shape it always had:

```go
type dishV1 struct {
	ID           int64     `json:"id,string"`
	Name         string    `json:"name"`
	PriceNaira   int64     `json:"priceNaira"`
	Available    bool      `json:"available"`
	Special      bool      `json:"special"`
	PortionsLeft int       `json:"portionsLeft"`
	CreatedAt    time.Time `json:"createdAt"`
}

type newDishV1 struct {
	Name         string `json:"name"         validate:"required,max=80"`
	PriceNaira   int64  `json:"priceNaira"   validate:"required,gt=0,lte=1000000"`
	Special      bool   `json:"special"`
	PortionsLeft int    `json:"portionsLeft" validate:"gte=0,lte=1000"`
}

var V1 = Version{
	Present: func(d Dish) any {
		return dishV1{ID: d.ID, Name: d.Name, PriceNaira: d.Price.Naira(), Available: d.Available,
			Special: d.Special, PortionsLeft: d.PortionsLeft, CreatedAt: d.CreatedAt}
	},
	ReadNew: func(w http.ResponseWriter, r *http.Request) (NewDish, error) {
		in, err := httpx.Decode[newDishV1](w, r)
		return NewDish{Name: in.Name, Price: money.FromNaira(in.PriceNaira),
			Special: in.Special, PortionsLeft: in.PortionsLeft}, err
	},
	ReadChanges:   readChangesV1,
	Fields:        []string{"id", "name", "priceNaira", "available", "special", "portionsLeft", "createdAt"},
	Sortable:      map[string]string{"id": "id", "name": "name", "priceNaira": "price_kobo", "createdAt": "created_at"},
	PriceInFilter: 100,
}
```

**v2** has the new shape, and a description (lesson 8's practice added the column; v1 never had it, and v1 doesn't change):

```go
type dishV2 struct {
	ID           int64        `json:"id,string"`
	Name         string       `json:"name"`
	Price        money.Amount `json:"price"`
	Available    bool         `json:"available"`
	Special      bool         `json:"special"`
	PortionsLeft int          `json:"portionsLeft"`
	Description  string       `json:"description,omitempty"`
	CreatedAt    time.Time    `json:"createdAt"`
}

type newDishV2 struct {
	Name         string       `json:"name"         validate:"required,max=80"`
	Price        money.Amount `json:"price"        validate:"required"`
	Special      bool         `json:"special"`
	PortionsLeft int          `json:"portionsLeft" validate:"gte=0,lte=1000"`
	Description  string       `json:"description"  validate:"max=300"`
}

var V2 = Version{
	Present: func(d Dish) any {
		return dishV2{ID: d.ID, Name: d.Name, Price: money.NGN(d.Price), Available: d.Available,
			Special: d.Special, PortionsLeft: d.PortionsLeft, Description: d.Description, CreatedAt: d.CreatedAt}
	},
	ReadNew: func(w http.ResponseWriter, r *http.Request) (NewDish, error) {
		in, err := httpx.Decode[newDishV2](w, r)
		return NewDish{Name: in.Name, Price: money.Kobo(in.Price.Amount), Special: in.Special,
			PortionsLeft: in.PortionsLeft, Description: in.Description}, err
	},
	ReadChanges:   readChangesV2,
	Fields:        []string{"id", "name", "price", "available", "special", "portionsLeft", "description", "createdAt"},
	Sortable:      map[string]string{"id": "id", "name": "name", "price": "price_kobo", "createdAt": "created_at"},
	PriceInFilter: 1,
}
```

Add `"time"` to the imports. Look at the two `ReadNew` functions. Each reads **its own** shape from the client, checks it with its own tags, then **translates** it into the same `NewDish` the service has always taken. The service never learns v2 exists. v1 clients still send naira, and it's stored as kobo. v2 clients send kobo, and it's stored as kobo.

Notice `validate:"required"` on `Price` in `newDishV2`. The validator checks the fields inside `money.Amount` too, using **its** tags: the currency must be `NGN`, and the amount must be positive. One rule, written once, for every place v2 accepts money.

The two `readChanges` functions do the same for PATCH. Here's v2's; v1's is the same shape with `PriceNaira *int64` converted with `money.FromNaira`:

```go
type dishChangesV2 struct {
	Name         *string       `json:"name"         validate:"omitempty,min=1,max=80"`
	Price        *money.Amount `json:"price"        validate:"omitempty"`
	Available    *bool         `json:"available"`
	Special      *bool         `json:"special"`
	PortionsLeft *int          `json:"portionsLeft" validate:"omitempty,gte=0,lte=1000"`
	Description  *string       `json:"description"  validate:"omitempty,max=300"`
}

func readChangesV2(w http.ResponseWriter, r *http.Request) (DishChanges, error) {
	in, err := httpx.Decode[dishChangesV2](w, r)
	ch := DishChanges{Name: in.Name, Available: in.Available, Special: in.Special,
		PortionsLeft: in.PortionsLeft, Description: in.Description}
	if in.Price != nil {
		k := money.Kobo(in.Price.Amount)
		ch.Price = &k
	}
	return ch, err
}
```

`validate:"omitempty"` on a pointer to a struct means "if it was sent, check the struct inside". A v2 PATCH with `{"price":{"amount":0,"currency":"USD"}}` gets two field errors back, one for each.

## Step 6: handlers that take a version
<!-- bite: 48d59465-1109-4791-9e80-0800f2b61abc -->

The menu handler holds its version like any other dependency:

```go
type Handler struct {
	svc     *Service
	version Version
	prefix  string // "/v1" or "/v2"
}

func NewHandler(svc *Service, version Version, prefix string) *Handler {
	return &Handler{svc: svc, version: version, prefix: prefix}
}

func (h *Handler) Register(mux *http.ServeMux, staff func(http.Handler) http.Handler) {
	p := h.prefix
	mux.Handle("GET "+p+"/menu", httpx.HandlerFunc(h.list))
	mux.Handle("GET "+p+"/menu/{id}", httpx.HandlerFunc(h.get))
	mux.Handle("POST "+p+"/menu", staff(httpx.HandlerFunc(h.add)))
	mux.Handle("PATCH "+p+"/menu/{id}", staff(httpx.HandlerFunc(h.change)))
	mux.Handle("DELETE "+p+"/menu/{id}", staff(httpx.HandlerFunc(h.remove)))
}
```

The patterns are built from the prefix: `"GET " + "/v2" + "/menu"` is `GET /v2/menu`. Each version's handler registers its own copy of every route, on the same mux.

The handlers ask the version for anything version-shaped:

```go
func (h *Handler) get(w http.ResponseWriter, r *http.Request) error {
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	dish, err := h.svc.Get(r.Context(), id)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, h.version.Present(dish))
}

func (h *Handler) add(w http.ResponseWriter, r *http.Request) error {
	in, err := h.version.ReadNew(w, r)
	if err != nil {
		return err
	}
	dish, err := h.svc.Add(r.Context(), in)
	if err != nil {
		return err
	}
	w.Header().Set("Location", h.prefix+"/menu/"+strconv.FormatInt(dish.ID, 10))
	return httpx.WriteData(w, http.StatusCreated, h.version.Present(dish))
}
```

The `Location` header uses the prefix, so it always points into the version the client used. A v1 client is never sent to a v2 address.

And `list` uses the version's fields, sort names and price unit:

```go
	lq := ListQuery{
		// ...
		Sort:     q.Sort("sort", h.version.Sortable),
		MinPrice: priceFilter(q.OptionalInt("minPrice", 1, 100_000_000), h.version.PriceInFilter),
		MaxPrice: priceFilter(q.OptionalInt("maxPrice", 1, 100_000_000), h.version.PriceInFilter),
	}
	fields := q.Fields("fields", h.version.Fields)
	// ... after the service call:
	presented := make([]any, len(dishes))
	for i, d := range dishes {
		presented[i] = h.version.Present(d)
	}
	return httpx.WriteList(w, httpx.Pick(presented, fields), pageMeta{...})
```

`ListQuery.MinPrice` and `MaxPrice` become `*money.Kobo`, and `priceFilter` multiplies by the unit (nil stays nil). `?maxPrice=2000` means ₦2,000 to a v1 client and 2,000 kobo (₦20) to a v2 client, just as each version's prices are written. Field selection runs **after** presenting, so `fields=priceNaira` works in v1 and `fields=price` in v2, each checked against its own list.

The orders package gets the same treatment, smaller: `orderV1` has `totalNaira`, `orderV2` has `total` as a `money.Amount`, and `orders.NewHandler` takes a `Version` with just a `Present` function. Write it from the menu one; the practice checks it.

## Step 7: both versions in one app
<!-- bite: f6a63b38-5037-4bd7-a63a-33573a9045c4 -->

`internal/app/app.go` registers each version:

```go
func New(d Deps) http.Handler {
	staff := httpx.KitchenOnly(d.StaffKey)
	mux := http.NewServeMux()
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Mama Put is open!\n"))
	})

	v1 := http.NewServeMux()
	menu.NewHandler(d.Menu, menu.V1, "/v1").Register(v1, staff)
	orders.NewHandler(d.Orders, orders.V1, "/v1").Register(v1, staff)
	mux.Handle("/v1/", httpx.Deprecated(d.V1Policy)(httpx.MuxProblems(v1)))

	menu.NewHandler(d.Menu, menu.V2, "/v2").Register(mux, staff)
	orders.NewHandler(d.Orders, orders.V2, "/v2").Register(mux, staff)

	return httpx.Chain(httpx.MuxProblems(mux), httpx.RequestID, httpx.LogRequests(d.Logger), httpx.RecoverPanic)
}
```

v1's routes go on a **mux of their own**, and that whole mux is registered under `/v1/`, wrapped in a `Deprecated` middleware (step 9). A pattern ending in `/` matches everything below it, the lesson 1 rule, so every `/v1/...` request goes through `Deprecated` and then into the v1 mux, which picks the route. It's the standard library's way of giving a group of routes shared middleware: a mux inside a mux. The v1 mux gets its own `MuxProblems` wrap. The outer one only checks the outer mux, where `/v1/` always matches, so without it a wrong v1 address would get the inner mux's plain-text 404.

What about the old paths with no version, `/menu` and `/orders`? Clients from before this lesson use them. Since they **are** v1, register them as v1 too, with an empty prefix, on the same deprecated v1 mux, plus `mux.Handle("/menu", ...)`-style entries pointing at it. The practice does it. A route clients use is a promise; you don't break it just because you've started numbering versions.

```bash
curl -s localhost:8080/v1/menu/1
# {"data":{"id":"1","name":"Jollof rice","priceNaira":1500,...}}

curl -s localhost:8080/v2/menu/1
# {"data":{"id":"1","name":"Jollof rice","price":{"amount":150000,"currency":"NGN"},...}}

curl -s -X POST localhost:8080/v2/menu -H "X-Staff-Key: mama-secret" -H "Content-Type: application/json" \
  -d '{"name":"Puff puff","price":{"amount":20050,"currency":"NGN"},"portionsLeft":60}'
# a ₦200.50 dish, which v1 shows as "priceNaira": 200
```

That last line is worth noticing. v1 can only show whole naira, so ₦200.50 shows as 200. That's v1's honest limit, and a good reason for its clients to move.

## Step 8: the header way
<!-- bite: 9598b212-12ea-4b0d-bc06-ee40ae9f3940 -->

If you'd rather keep URLs clean, here's the same app choosing the version from a header instead. A small middleware decides, and remembers its choice in the context:

```go
var versionPattern = regexp.MustCompile(`application/vnd\.mamaput\.v(\d+)\+json`)

func ChooseVersion(supported []string, fallback string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			asked := r.Header.Get("Api-Version")
			if asked == "" {
				if m := versionPattern.FindStringSubmatch(r.Header.Get("Accept")); m != nil {
					asked = m[1]
				}
			}
			if asked == "" {
				asked = fallback
			}
			if !slices.Contains(supported, asked) {
				WriteError(w, r, apperr.New(apperr.Invalid, "unsupported-version",
					"API version "+asked+" is not supported. Use one of: "+strings.Join(supported, ", ")+"."))
				return
			}
			w.Header().Add("Vary", "Api-Version, Accept")
			next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), versionKey, asked)))
		})
	}
}
```

It reads the `Api-Version` header, then the media type in `Accept`, and falls back to a default. A handler then picks its `Version` from the context instead of being given one.

`Vary` matters more than it looks. It tells any cache in between (a CDN, a proxy, the phone's own cache) "the answer depends on these request headers". Without it, a cache could store the v2 answer and hand it to a v1 client. With path versioning you don't need `Vary`, because the URLs differ. That's one of the quiet reasons path versioning is popular.

The default when a client sends no version should be **the oldest supported one**, so clients that never heard of versioning keep getting what they always got. Defaulting to "latest" means every new version breaks them.

## Step 9: deprecating v1
<!-- bite: b759275c-8a0d-4891-b574-0efdc5d0ec03 -->

A version you never retire is a version you maintain forever. Retiring one well is four things.

**1. Tell clients, in every response.** Two standard headers do it. `Deprecation` (RFC 9745) says when the version was deprecated, as `@` and a Unix time. `Sunset` (RFC 8594) says when it stops working, as an HTTP date. A `Link` points to the migration guide.

Add `Gone` to the kinds in `apperr` (and `apperr.Gone: http.StatusGone` to `statusFor`). Then `internal/httpx/deprecated.go`:

```go
package httpx

import (
	"net/http"
	"strconv"
	"time"

	"mamaput/internal/apperr"
)

type DeprecationPolicy struct {
	Version      string
	DeprecatedAt time.Time
	SunsetAt     time.Time
	Guide        string
	Now          func() time.Time
}

func Deprecated(p DeprecationPolicy) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if !p.Now().Before(p.SunsetAt) {
				WriteError(w, r, apperr.New(apperr.Gone, "version-retired",
					"API "+p.Version+" stopped working on "+p.SunsetAt.Format("2 January 2006")+". See "+p.Guide))
				return
			}
			w.Header().Set("Deprecation", "@"+strconv.FormatInt(p.DeprecatedAt.Unix(), 10))
			w.Header().Set("Sunset", p.SunsetAt.UTC().Format(http.TimeFormat))
			w.Header().Set("Link", "<"+p.Guide+`>; rel="deprecation"`)
			LoggerFrom(r.Context()).Info("deprecated version used",
				"version", p.Version, "path", r.URL.Path, "client", r.UserAgent())
			next.ServeHTTP(w, r)
		})
	}
}
```

It takes `Now`, a clock, for the same reason the orders service does: so a test can check "after the sunset date, it answers 410" without waiting until June. The policy is built in `run` and passed through `app.Deps`:

```go
V1Policy: httpx.DeprecationPolicy{
	Version:      "v1",
	DeprecatedAt: time.Date(2026, 12, 1, 0, 0, 0, 0, time.UTC),
	SunsetAt:     time.Date(2027, 6, 1, 0, 0, 0, 0, time.UTC),
	Guide:        "https://mamaput.example/docs/moving-to-v2",
	Now:          time.Now,
},
```

```bash
curl -si localhost:8080/v1/menu/1 | grep -E "^(Deprecation|Link|Sunset)"
# Deprecation: @1796083200
# Link: <https://mamaput.example/docs/moving-to-v2>; rel="deprecation"
# Sunset: Tue, 01 Jun 2027 00:00:00 GMT
```

**2. Measure who's still on it.** That log line fires for every v1 request, with the client's user agent. In lesson 27 it becomes a proper metric, "v1 requests per day". You switch v1 off when that number is near zero, not just because the calendar says so.

**3. Tell people directly.** Headers are for programs. Humans need an email, a changelog entry, a note in the docs. If the phone app is yours, ship an update that moves to v2 **before** the sunset.

**4. Switch it off kindly.** After the sunset, the middleware answers **410 Gone** with a problem saying what happened and where to go. A clear 410 is far better than a confusing 404 or, worse, quietly sending v2 data to a v1 client.

## The same idea everywhere
<!-- bite: 3e17d217-71a4-4ca0-9248-f702e2749f9e -->

Versioning isn't only for REST routes. Anything other programs depend on has a shape, and shapes need versions:

1. **Webhooks you send** (lesson 17): partners' code reads your payloads, so they carry a version.
2. **Events between services** (lesson 25): the notifications service reads `order.placed`. Change its shape and you break it, so events carry a version number.
3. **gRPC** (lesson 22): Protocol Buffers have their own rules for safe changes, and you'll find they're the same rules as step 1.

## The Go in this lesson
<!-- bite: b56586a0-ca48-4d68-ba3f-a169440201f1 -->

1. **`type Kobo int64`** and **`Kobo(naira * 100)`**: A named type built on `int64`. Go treats it as a different type, so mixing it with plain numbers needs a conversion, written out on purpose.
2. **`func (k Kobo) Naira() int64`**: A method on a number type. Any type you declare can have methods, not just structs.
3. **Structs without `json` tags**: `menu.Dish` is never encoded directly any more, so it doesn't need them. Keeping domain and wire types separate is how Go code stops internal renames leaking into the API.
4. **`validate:"required"` on a struct field**: The validator goes inside nested structs and checks their own tags.
5. **`type Version struct { Present func(Dish) any; ... }`**: A struct of functions. It's a lightweight alternative to an interface when you have a few fixed variants; `V1` and `V2` are just two values of it.
6. **`var V1 = Version{ Present: func(d Dish) any { ... }, ... }`**: Functions written in place as field values. Each closes over nothing; they only use their arguments.
7. **`in, err := httpx.Decode[newDishV1](w, r)` then using `in` even if `err` is set**: When `err` isn't nil, `in` is the zero value, and the caller checks `err` first, so the half-filled `NewDish` is never used. It keeps the function short.
8. **`strconv.FormatInt(dish.ID, 10)`**: An `int64` to text, in base 10. `strconv.Itoa` only takes an `int`.
9. **`mux.Handle("/v1/", httpx.Deprecated(policy)(v1))`**: A mux is a handler, so it can be registered on another mux, wrapped in middleware like any handler.
10. **`versionPattern.FindStringSubmatch(...)`**: Returns the whole match and each bracketed group, or nil. `m[1]` is the first group, the version number.
11. **`w.Header().Add("Vary", ...)`**: `Add` appends a header value; `Set` replaces every existing value. `Vary` might already have values from other code, so add to it.
12. **`!p.Now().Before(p.SunsetAt)`**: "Now is not before the sunset", meaning now is at or after it. `time.Time` values are compared with methods (`Before`, `After`, `Equal`), never with `<`.
13. **`p.SunsetAt.UTC().Format(http.TimeFormat)`**: `http.TimeFormat` is the date layout HTTP headers use. Go formats dates by example: the layout is a picture of one fixed moment, `Mon, 02 Jan 2006 15:04:05 GMT`.
14. **`time.Date(2027, 6, 1, 0, 0, 0, 0, time.UTC)`**: Builds an exact moment: year, month, day, hour, minute, second, nanosecond, time zone.

## Your project so far
<!-- bite: 80c7dd33-ac64-49f9-a9f6-98e61a8d97d5 -->

```text
mama-put/
├── Makefile
├── go.mod
├── migrations/
│   ├── ...
│   └── 005_prices_in_kobo.sql         ← NEW: price_kobo and total_kobo, values times 100
├── cmd/
│   ├── api/
│   │   └── main.go                    ← builds the v1 deprecation policy
│   └── migrate/
│       └── main.go
└── internal/
    ├── apperr/
    │   └── apperr.go                  ← Gone kind
    ├── app/
    │   └── app.go                     ← v1 on its own mux under /v1/, behind Deprecated; v2 on the main mux
    ├── db/
    ├── httpx/
    │   ├── deprecated.go              ← NEW: DeprecationPolicy, Deprecated (headers, log, 410)
    │   ├── version.go                 ← NEW: ChooseVersion, the header way (not used by the app)
    │   ├── errors.go                  ← statusFor has Gone → 410
    │   └── ...
    ├── listing/
    ├── money/
    │   └── money.go                   ← NEW: Kobo, FromNaira, Naira, Amount, NGN
    ├── menu/
    │   ├── menu.go                    ← Dish, NewDish, DishChanges in kobo, no json tags
    │   ├── versions.go                ← NEW: Version; V1 and V2 with their wire types and readers
    │   ├── postgres.go                ← price_kobo
    │   ├── handlers.go                ← Handler holds a Version and a prefix
    │   └── ...
    └── orders/
        ├── orders.go                  ← Order.Total is money.Kobo
        ├── versions.go                ← NEW: V1 (totalNaira) and V2 (total)
        ├── postgres.go                ← total_kobo
        ├── handlers.go                ← takes a Version and a prefix
        └── ...
```

## Common mistakes
<!-- bite: c1610d1c-cf46-40c0-95e8-9fb0907b543b -->

1. **Changing a field's meaning without changing its name.** `price` from naira to kobo breaks every client silently. New meaning, new field or new version.
2. **Encoding domain types directly.** Then renaming a Go field renames an API field. Present through wire types.
3. **Versioning inside the service.** `if version == 2` in a rule means v1 and v2 can drift apart in behaviour. Versions translate at the door; rules stay one.
4. **Defaulting to the latest version.** Every new version then breaks clients that never asked for one.
5. **Header versioning without `Vary`.** A cache serves one version's answer to another version's client.
6. **Money as a float.** `0.1 + 0.2` isn't `0.3` in a computer. Keep whole kobo in an integer type.
7. **Retiring a version by date alone.** Measure who still uses it first.
8. **A 404 after the sunset.** Answer 410 with a problem that says where to go.

## Check your understanding
<!-- bite: b2b98f7d-3735-4f4a-9dce-a6a759e395e6 -->

1. A teammate wants to add `"spicy": true` to every dish in v1. Does that need v2?
2. Why does `newDishV1` translate `priceNaira` into a `NewDish` with kobo, instead of the service taking naira from v1 and kobo from v2?
3. A v1 client sends `GET /v1/menu?maxPrice=2000`, a v2 client `GET /v2/menu?maxPrice=2000`. Do they get the same dishes?
4. With header versioning, a CDN caches `GET /menu` for 60 seconds. What goes wrong if the response has no `Vary` header?
5. Why does `Deprecated` take a clock?

<details>
<summary>Answers, after your attempt</summary>

1. No. Adding an optional field is safe; tolerant clients ignore fields they don't know. (If any v1 client is known to break on unknown fields, that client has a bug, but it's worth knowing before you ship.)
2. So the service has one meaning of a price, and every rule (positive, at most a million naira, how totals are worked out) is written once. Each version's job is only to translate its own shape into that one meaning.
3. No. In v1, `maxPrice` is in naira, so it's ₦2,000. In v2, it's in kobo, like every v2 price, so it's ₦20, and probably nothing matches. Each version's filters use the same unit as its own prices.
4. The CDN stores whichever version's answer it saw first, and gives it to everyone for 60 seconds, whatever version they asked for. `Vary: Api-Version, Accept` tells it to keep a separate copy per value.
5. So a test can check what happens after the sunset date by passing a clock set in June 2027, instead of waiting for it. The same reason the orders service takes one.

</details>

## Practice
<!-- bite: e15d7a14-0afa-4501-94e3-02c04f215bb7 -->

1. Write `internal/orders/versions.go`: `orderV1` with `totalNaira`, `orderV2` with `total` as a `money.Amount`, and `V1`, `V2` with a `Present` function each. Make `GET /v1/orders/{id}` and `GET /v2/orders/{id}` both work.
2. Keep the old unversioned routes working: register v1's handlers a second time with prefix `""` on the deprecated v1 mux, and register that mux on the main mux for `/menu`, `/menu/`, `/orders` and `/orders/`. Check `curl -si localhost:8080/menu` shows v1's shape and a `Sunset` header.
3. Write `internal/httpx/deprecated_test.go` with a fake clock: before the sunset you get the next handler's answer and the three headers; at and after it, a 410 problem with `code: "version-retired"`.
4. Make `GET /menu/specials` from lesson 2 a v1-only route, and leave it out of v2, since `?special=true` does the same job. Is removing it from v2 a breaking change? (Think about who uses v2 so far.)

**Done when** `make test` passes, v1 and v2 show the same dish in their own shapes, a ₦200.50 dish added through v2 shows as `"priceNaira": 200` in v1, and every v1 response carries `Deprecation`, `Sunset` and `Link`.

## Before moving on
<!-- bite: e790c79a-6d8a-4039-9137-a25c0ea57de3 -->

Mama Put API now speaks two versions from one service and one database. Prices are stored in kobo, each version translates its own shapes at the door, and v1 tells every client, in headers they can read, when it goes away.

But how does the phone team **know** what v2 looks like? Right now they'd read our Go structs, or guess from `curl`. They want a document: every route, every field, every error, for each version, that their tools can read to generate a client. And it must never drift from what the code really does. That's OpenAPI, and it's the next lesson.

## Related
<!-- bite: abd88bf3-b42a-462a-847c-efa3c5df5c28 -->

- [[backend/frameworks/net-http/11-api-docs|Next: API Docs with OpenAPI]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — resources and their shapes
- [[backend/frameworks/express/10-versioning|The same lesson in Express]] — presenters as objects of functions

## About this lesson
<!-- bite: 3010e411-36d4-441d-a119-e15a826729c5 -->

**Level:** Intermediate. Lesson 10 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later.
