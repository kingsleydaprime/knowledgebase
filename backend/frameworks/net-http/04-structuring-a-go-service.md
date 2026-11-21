---
id: 71ec1ca8-f44a-4ca6-84e1-3ce49c4e192c
---

# Structuring a Go Service

**Structuring a service means deciding which code lives in which package, so each part has one job and you can find, change and test it without touching the rest.** In Go, the package is the unit of everything: of naming, of what's visible, and of what may depend on what. Get the packages right and the rest of the app has somewhere obvious to go.

## Before you start
<!-- bite: d3e1b144-ebf7-4958-ba1e-2e76f887eb82 -->

You should have:

1. Finished [[backend/frameworks/net-http/03-middleware|lesson 3]], so Mama Put API has the menu routes, order routes and three middleware, all in package `main`.
2. Read, or at least skimmed, [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers: Controllers, Services and Repositories]]. This lesson puts that idea into Go.

After this lesson you will be able to:

1. Lay out a Go service with `cmd/` and `internal/`, and say why each exists.
2. Split a feature into handlers, a service and a store, each with one job.
3. Write handlers as methods on a struct that holds what they need.
4. Return errors from a service and turn them into status codes in the handler.
5. Explain why Go refuses import cycles, and how that pushes you to a clean design.

## Where we stopped
<!-- bite: d46f07c4-b859-4d3a-a3df-c1365eef2658 -->

Everything is in package `main`, in two files. `main.go` holds types, the store, the routes, the rules (like "a dish must be available to order") and the start-up code. It works. But try to answer "where is the rule about order quantities?" and you're scrolling. And there's no line between HTTP code and Mama's rules: the check that a dish is available sits inside a handler, so the background jobs in lesson 18, which have no HTTP request, can't use it.

## The kid version
<!-- bite: 0954199d-396c-42b5-951e-dd98100c0efa -->

When Mama started, she did everything at one table: took the money, cooked, served, washed plates. When the queue grew, she gave each job its own place. The money box by the front. The pots at the back. The plates in a basin to the side.

Nothing about the food changed. But now when the money box is wrong, she knows where to look, and she can hire someone for the plates without teaching them to cook.

**Where the picture stops working.** In a kitchen, anyone can walk to any station. In Go, packages can only use each other in one direction. If the money box uses the pots, the pots may never use the money box. That rule feels strict at first, and it's the thing that keeps a Go app from turning into spaghetti.

## Terms used in this lesson
<!-- bite: b0b82e93-0778-47ed-b3fd-10e90fde13d9 -->

1. **Package**: This is a folder of `.go` files that are compiled together and share one name. Code in one package uses another by importing its path, and can only see the other's **exported** names, the ones starting with a capital letter.
2. **Import path**: This is how you name a package to import it: the module name followed by the folder, like `mamaput/internal/menu`.
3. **Handler layer**: This is the code that speaks HTTP. It reads the request, calls the service, and turns the result into a response. It knows about status codes and JSON; it doesn't know Mama's rules.
4. **Service**: This is the code that holds the business rules: "you can't order a finished dish", "at most 20 plates per order". It knows nothing about HTTP.
5. **Store**: This is the code that keeps and finds data, also called a **repository**. Today it's in memory; in lesson 8 it's PostgreSQL. Nothing above it should care which.
6. **Sentinel error**: This is an error value made once and shared, like `ErrDishNotFound`, so other code can check "was it *this* error?" with `errors.Is`.
7. **Import cycle**: This is when package A imports B and B imports A, directly or through others. Go refuses to compile it.

## The layout
<!-- bite: a951aae3-00c3-4803-89a1-5f91a9662da9 -->

Here's where we're going. Don't make the files yet; read the shape first.

```text
mama-put/
├── go.mod
├── cmd/
│   └── api/
│       └── main.go          ← starts the API: builds everything and listens
└── internal/
    ├── menu/
    │   ├── menu.go          ← the types: Dish, NewDish, DishChanges, errors
    │   ├── store.go         ← MemoryStore: keeps the dishes
    │   ├── service.go       ← Service: the menu rules
    │   └── handlers.go      ← Handler: HTTP in and out, and its routes
    ├── orders/
    │   ├── orders.go
    │   ├── store.go
    │   ├── service.go
    │   └── handlers.go
    └── httpx/
        ├── json.go          ← WriteJSON, ReadJSON
        └── middleware.go    ← the three middleware, statusRecorder, Chain
```

Each folder in it is there for a reason.

**`cmd/api/`** holds the program. In Go, every folder with `package main` builds into its own program, and by habit those folders sit under `cmd/`. Right now there's one, the API. Lesson 8 adds `cmd/migrate`, and lesson 25 adds `cmd/notifications`, the second service. They'll all live in this one module and share the code in `internal/`.

**`internal/`** is special to the Go compiler. A package inside a folder called `internal` can only be imported by code in the folder that contains `internal`, here the whole `mama-put` module. Someone else's project can't import `mamaput/internal/menu`, even if they wanted to. That means you can change anything in there without breaking anyone outside. Almost all of an app's code belongs in `internal/`.

**`internal/menu/` and `internal/orders/`** are the features. Everything about the menu lives together: its types, its store, its rules and its routes. This is **organising by feature**, and it's the Go habit. The opposite, folders called `handlers/`, `services/` and `models/` each holding a bit of every feature, means one change to the menu touches four folders. [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|Organising by Layer vs by Feature]] compares the two.

**`internal/httpx/`** holds the HTTP helpers every feature uses. It's called `httpx` and not `http` so it doesn't clash with `net/http` when both are imported.

Notice what's **not** there: no `utils/`, `common/` or `helpers/` package. A package's name should say what it gives you. "Utils" says nothing, so everything ends up in it. And no `models/` package with every type in the app: in Go, a type lives in the package that owns it, so a dish is `menu.Dish`.

## Names in Go read with their package
<!-- bite: 46e43a62-f0e1-40e3-8e51-a941db55fbb7 -->

You always use an imported name with its package in front: `menu.Dish`, `orders.Service`. So the package name is part of every name, and Go style says don't repeat it. Call it `menu.Service`, not `menu.MenuService`, and `menu.NewService`, not `menu.NewMenuService`. It reads like plain English from the outside: "a menu service", "a new menu service".

That's why every feature package can have a `Service`, a `Handler` and a `MemoryStore`, with the same names, and never get them confused.

## The menu package, from the bottom up
<!-- bite: 67db9d25-8e7a-4ea1-becb-92e0fa3090e5 -->

Start at the bottom, the part that depends on nothing. Make the folders:

```bash
mkdir -p cmd/api internal/menu internal/orders internal/httpx
```

`internal/menu/menu.go` holds the types and errors the whole feature shares:

```go
package menu

import "errors"

type Dish struct {
	ID         string `json:"id"`
	Name       string `json:"name"`
	PriceNaira int    `json:"priceNaira"`
	Available  bool   `json:"available"`
	Special    bool   `json:"special"`
}

type NewDish struct {
	Name       string `json:"name"`
	PriceNaira int    `json:"priceNaira"`
	Special    bool   `json:"special"`
}

type DishChanges struct {
	Name       *string `json:"name"`
	PriceNaira *int    `json:"priceNaira"`
	Available  *bool   `json:"available"`
	Special    *bool   `json:"special"`
}

var (
	ErrDishNotFound = errors.New("dish not found")
	ErrBadDish      = errors.New("a dish needs a name and a positive price")
)
```

The types are now exported (`NewDish`, not `newDish`), because the handlers and other packages need them.

The two `Err...` values are **sentinel errors**. Each is made once, with `errors.New`. Code anywhere can return `menu.ErrDishNotFound`, and code anywhere can check for it with `errors.Is(err, menu.ErrDishNotFound)`. That's how the service tells the handler what went wrong without knowing anything about HTTP.

`internal/menu/store.go` is the `menuStore` from lesson 2, moved and renamed to `MemoryStore`, with exported methods:

```go
package menu

import (
	"slices"
	"strconv"
	"sync"
)

type MemoryStore struct {
	mu     sync.Mutex
	dishes []Dish
	nextID int
}

func NewMemoryStore(seed []Dish) *MemoryStore {
	return &MemoryStore{dishes: slices.Clone(seed), nextID: len(seed) + 1}
}

func (s *MemoryStore) List() []Dish {
	s.mu.Lock()
	defer s.mu.Unlock()
	return slices.Clone(s.dishes)
}

func (s *MemoryStore) Find(id string) (Dish, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	for _, d := range s.dishes {
		if d.ID == id {
			return d, true
		}
	}
	return Dish{}, false
}

func (s *MemoryStore) Add(d Dish) Dish {
	s.mu.Lock()
	defer s.mu.Unlock()
	d.ID = strconv.Itoa(s.nextID)
	s.nextID++
	s.dishes = append(s.dishes, d)
	return d
}

func (s *MemoryStore) Update(id string, change func(*Dish)) (Dish, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	for i := range s.dishes {
		if s.dishes[i].ID == id {
			change(&s.dishes[i])
			return s.dishes[i], true
		}
	}
	return Dish{}, false
}

func (s *MemoryStore) Remove(id string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	for i, d := range s.dishes {
		if d.ID == id {
			s.dishes = slices.Delete(s.dishes, i, i+1)
			return true
		}
	}
	return false
}
```

The starting menu is now passed in as `seed`, so the store doesn't decide what Mama sells. `main` does.

The store does one job: keep dishes and find them. It has no rules. It would happily store a dish with a price of -500. Rules are the next layer's job.

## The service: Mama's rules, and no HTTP
<!-- bite: c30955c3-227c-4db4-bdbf-91bb8fce1424 -->

`internal/menu/service.go`:

```go
package menu

type Service struct {
	store *MemoryStore
}

func NewService(store *MemoryStore) *Service {
	return &Service{store: store}
}

func (s *Service) List(onlyAvailable bool) []Dish {
	dishes := s.store.List()
	if onlyAvailable {
		dishes = slices.DeleteFunc(dishes, func(d Dish) bool { return !d.Available })
	}
	return dishes
}

func (s *Service) Specials() []Dish {
	return slices.DeleteFunc(s.store.List(), func(d Dish) bool { return !d.Special || !d.Available })
}

func (s *Service) Get(id string) (Dish, error) {
	dish, ok := s.store.Find(id)
	if !ok {
		return Dish{}, ErrDishNotFound
	}
	return dish, nil
}

func (s *Service) Add(in NewDish) (Dish, error) {
	if in.Name == "" || in.PriceNaira <= 0 {
		return Dish{}, ErrBadDish
	}
	return s.store.Add(Dish{Name: in.Name, PriceNaira: in.PriceNaira, Special: in.Special, Available: true}), nil
}

func (s *Service) Change(id string, ch DishChanges) (Dish, error) {
	if ch.PriceNaira != nil && *ch.PriceNaira <= 0 {
		return Dish{}, ErrBadDish
	}
	if ch.Name != nil && *ch.Name == "" {
		return Dish{}, ErrBadDish
	}
	dish, ok := s.store.Update(id, func(d *Dish) {
		if ch.Name != nil {
			d.Name = *ch.Name
		}
		if ch.PriceNaira != nil {
			d.PriceNaira = *ch.PriceNaira
		}
		if ch.Available != nil {
			d.Available = *ch.Available
		}
		if ch.Special != nil {
			d.Special = *ch.Special
		}
	})
	if !ok {
		return Dish{}, ErrDishNotFound
	}
	return dish, nil
}

func (s *Service) Remove(id string) error {
	if !s.store.Remove(id) {
		return ErrDishNotFound
	}
	return nil
}
```

Add `import "slices"` at the top.

Read through it and look for anything about HTTP. There's none: no `http.ResponseWriter`, no status codes, no JSON. The service takes plain Go values and returns plain Go values and errors. That's the point. A background job, a test, a command-line tool or the GraphQL API in lesson 21 can all call `Service.Add`, and the rule "a dish needs a positive price" holds for all of them.

The functions follow the Go pattern for anything that can fail: return the result **and** an `error`. When it worked, the error is `nil`. When it didn't, the result is an empty value you mustn't use, and the error says why.

We also caught a rule that was missing before: a special that's sold out isn't much of a special. `Specials` now leaves it out. That's the kind of rule that belongs in the service, and it was easy to see once rules had their own home.

## The handlers: HTTP in, HTTP out
<!-- bite: 0320cf18-06a6-4b03-b72a-27e344de5406 -->

First, the JSON helpers every feature will use. `internal/httpx/json.go`:

```go
package httpx

import (
	"encoding/json"
	"net/http"
)

func WriteJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func ReadJSON(r *http.Request, v any) error {
	return json.NewDecoder(r.Body).Decode(v)
}
```

Move `middleware.go` into `internal/httpx/` too, change its first line to `package httpx`, and capitalise the names other packages need: `LogRequests`, `RecoverPanic`, `KitchenOnly` and `Chain`. `statusRecorder` stays lower-case. Nothing outside `httpx` needs it, so nothing outside can see it.

Now `internal/menu/handlers.go`. In lesson 2 every handler was a function written inside `registerMenuRoutes`, and they reached the store because a closure remembers what's around it. That doesn't scale. In Go, the usual shape is a **struct that holds what the handlers need, with each handler as a method on it**:

```go
package menu

import (
	"errors"
	"net/http"

	"mamaput/internal/httpx"
)

type Handler struct {
	svc *Service
}

func NewHandler(svc *Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(mux *http.ServeMux, staff func(http.Handler) http.Handler) {
	mux.HandleFunc("GET /menu", h.list)
	mux.HandleFunc("GET /menu/specials", h.specials)
	mux.HandleFunc("GET /menu/{id}", h.get)
	mux.Handle("POST /menu", staff(http.HandlerFunc(h.add)))
	mux.Handle("PATCH /menu/{id}", staff(http.HandlerFunc(h.change)))
	mux.Handle("DELETE /menu/{id}", staff(http.HandlerFunc(h.remove)))
}

func (h *Handler) list(w http.ResponseWriter, r *http.Request) {
	onlyAvailable := r.URL.Query().Get("available") == "true"
	httpx.WriteJSON(w, http.StatusOK, h.svc.List(onlyAvailable))
}

func (h *Handler) specials(w http.ResponseWriter, r *http.Request) {
	httpx.WriteJSON(w, http.StatusOK, h.svc.Specials())
}

func (h *Handler) get(w http.ResponseWriter, r *http.Request) {
	dish, err := h.svc.Get(r.PathValue("id"))
	if err != nil {
		writeError(w, err)
		return
	}
	httpx.WriteJSON(w, http.StatusOK, dish)
}

func (h *Handler) add(w http.ResponseWriter, r *http.Request) {
	var in NewDish
	if err := httpx.ReadJSON(r, &in); err != nil {
		http.Error(w, "body must be JSON describing a dish", http.StatusBadRequest)
		return
	}
	dish, err := h.svc.Add(in)
	if err != nil {
		writeError(w, err)
		return
	}
	w.Header().Set("Location", "/menu/"+dish.ID)
	httpx.WriteJSON(w, http.StatusCreated, dish)
}

func (h *Handler) change(w http.ResponseWriter, r *http.Request) {
	var in DishChanges
	if err := httpx.ReadJSON(r, &in); err != nil {
		http.Error(w, "body must be JSON", http.StatusBadRequest)
		return
	}
	dish, err := h.svc.Change(r.PathValue("id"), in)
	if err != nil {
		writeError(w, err)
		return
	}
	httpx.WriteJSON(w, http.StatusOK, dish)
}

func (h *Handler) remove(w http.ResponseWriter, r *http.Request) {
	if err := h.svc.Remove(r.PathValue("id")); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func writeError(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, ErrDishNotFound):
		http.Error(w, err.Error(), http.StatusNotFound)
	case errors.Is(err, ErrBadDish):
		http.Error(w, err.Error(), http.StatusBadRequest)
	default:
		http.Error(w, "something went wrong on our side", http.StatusInternalServerError)
	}
}
```

A few things to see here.

**`h.list` is a method value.** `mux.HandleFunc("GET /menu", h.list)` passes the method `list` already tied to `h`. When a request comes, Go calls it with `h` as the receiver, so the handler can reach `h.svc`. Every handler gets the service the same way, with no global variables.

**Handlers are lower-case.** Nothing outside the package calls `h.list` directly. The only exported doorway is `Register`, which puts them on a mux. That keeps the package's surface small: from the outside, the menu package is "a handler you can register", and that's all.

**The handler reads, calls, writes.** Each one does three things and nothing else: read what it needs from the request, call one service method, turn the result into a response. No rules.

**`writeError` is the one place errors become status codes.** The service returns `ErrDishNotFound`; only `writeError` knows that means 404. An error it doesn't recognise means something went wrong that nobody planned for, and that's a 500 with a vague message. Lesson 7 grows this into one error handler for the whole app.

**`staff` is passed in.** The menu package doesn't build its own `KitchenOnly`; it doesn't know the staff key. `main` gives it the middleware to use. A package should receive what it needs, not reach out and grab it. That's the whole of the next lesson.

## The orders package
<!-- bite: b62e182a-ec88-42db-b471-c347ddc25a51 -->

The orders package has the same four files and the same shape. Its service is where the interesting rules live, so here it is in full. `internal/orders/orders.go`:

```go
package orders

import "errors"

type Status string

const (
	StatusPending   Status = "pending"
	StatusReady     Status = "ready"
	StatusCollected Status = "collected"
)

type Order struct {
	ID         string `json:"id"`
	DishID     string `json:"dishId"`
	Quantity   int    `json:"quantity"`
	TotalNaira int    `json:"totalNaira"`
	Status     Status `json:"status"`
}

type NewOrder struct {
	DishID   string `json:"dishId"`
	Quantity int    `json:"quantity"`
}

var (
	ErrOrderNotFound    = errors.New("order not found")
	ErrBadQuantity      = errors.New("you can order between 1 and 20 plates")
	ErrDishUnavailable  = errors.New("that dish isn't available right now")
	ErrBadStatusChange  = errors.New("an order can't go back to an earlier status")
)
```

`Status` is its own type, with three named values. A function that takes a `Status` won't accept a random string by accident, and the names say what the values mean.

`internal/orders/service.go`:

```go
package orders

import "mamaput/internal/menu"

type Service struct {
	store  *MemoryStore
	dishes *menu.Service
}

func NewService(store *MemoryStore, dishes *menu.Service) *Service {
	return &Service{store: store, dishes: dishes}
}

func (s *Service) Place(in NewOrder) (Order, error) {
	if in.Quantity < 1 || in.Quantity > 20 {
		return Order{}, ErrBadQuantity
	}
	dish, err := s.dishes.Get(in.DishID)
	if err != nil {
		return Order{}, err
	}
	if !dish.Available {
		return Order{}, ErrDishUnavailable
	}
	return s.store.Add(Order{
		DishID:     dish.ID,
		Quantity:   in.Quantity,
		TotalNaira: dish.PriceNaira * in.Quantity,
		Status:     StatusPending,
	}), nil
}

func (s *Service) Get(id string) (Order, error) {
	order, ok := s.store.Find(id)
	if !ok {
		return Order{}, ErrOrderNotFound
	}
	return order, nil
}

var statusOrder = map[Status]int{StatusPending: 0, StatusReady: 1, StatusCollected: 2}

func (s *Service) SetStatus(id string, to Status) (Order, error) {
	if _, known := statusOrder[to]; !known {
		return Order{}, ErrBadStatusChange
	}
	var err error
	order, ok := s.store.Update(id, func(o *Order) {
		if statusOrder[to] <= statusOrder[o.Status] {
			err = ErrBadStatusChange
			return
		}
		o.Status = to
	})
	if !ok {
		return Order{}, ErrOrderNotFound
	}
	if err != nil {
		return Order{}, err
	}
	return order, nil
}
```

`Place` holds three rules: the quantity limit, that the dish exists, and that it's available. If `s.dishes.Get` fails, `Place` just returns that error as it is, so the handler sees `menu.ErrDishNotFound` and can answer 404. The total is worked out here, from the price on the menu, never from anything the customer sends. A customer who sends `"totalNaira": 1` doesn't get a cheap lunch.

`SetStatus` checks the order moves forward (pending, then ready, then collected), inside the store's lock, so two kitchen staff tapping "ready" and "collected" at once can't tangle it.

The store, `internal/orders/store.go`, is `MemoryStore` again, holding orders, with `Add`, `Find` and `Update`. Write it yourself from the menu one; it's good practice and it's the same shape. The handlers, `internal/orders/handlers.go`, are `Register`, `place`, `get` and `setStatus`, with a `writeError` that knows `ErrOrderNotFound` and `menu.ErrDishNotFound` are 404, `ErrBadQuantity` and `ErrDishUnavailable` are 400, and `ErrBadStatusChange` is 409 Conflict.

## The one-way rule
<!-- bite: 0b04e59c-2967-4182-b7d1-6c2afe4b5d9f -->

`orders` imports `menu`, because placing an order needs the menu. So `menu` may **never** import `orders`. If it did, Go would refuse to build, with `import cycle not allowed`.

Many languages let two modules import each other, and over time everything ends up tangled with everything. Go makes that impossible. You're forced to decide which way each dependency points, and the answer shapes the design:

1. **`cmd/api` imports everything.** It's the top. Nothing imports it.
2. **Feature packages import `httpx`** for helpers, and other features they truly need (`orders` → `menu`).
3. **`httpx` imports nothing of ours.** It's at the bottom, used by all.
4. **Inside a feature, handlers use the service, and the service uses the store.** Never the other way.

When you hit an import cycle (and you will), it's a design question, not a compiler annoyance. Usually one of three things is true: a type is in the wrong package, two packages are really one, or the lower package needs an **interface** instead of the other package's concrete type. That last one is the next lesson.

## The new main
<!-- bite: 0271dd69-f447-45fa-a0a6-61985af8f4dc -->

`cmd/api/main.go` is now short. It builds things and connects them:

```go
package main

import (
	"log/slog"
	"net/http"
	"os"
	"time"

	"mamaput/internal/httpx"
	"mamaput/internal/menu"
	"mamaput/internal/orders"
)

func main() {
	logger := slog.New(slog.NewTextHandler(os.Stdout, nil))

	staffKey := os.Getenv("STAFF_KEY")
	if staffKey == "" {
		logger.Error("STAFF_KEY is not set")
		os.Exit(1)
	}
	staff := httpx.KitchenOnly(staffKey)

	menuStore := menu.NewMemoryStore([]menu.Dish{
		{ID: "1", Name: "Jollof rice", PriceNaira: 1500, Available: true, Special: true},
		{ID: "2", Name: "Beans and plantain", PriceNaira: 1200, Available: true},
		{ID: "3", Name: "Egusi and pounded yam", PriceNaira: 2500},
	})
	menuService := menu.NewService(menuStore)
	orderService := orders.NewService(orders.NewMemoryStore(), menuService)

	mux := http.NewServeMux()
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Mama Put is open!\n"))
	})
	menu.NewHandler(menuService).Register(mux, staff)
	orders.NewHandler(orderService).Register(mux, staff)

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           httpx.Chain(mux, httpx.LogRequests(logger), httpx.RecoverPanic(logger)),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       120 * time.Second,
	}

	logger.Info("Mama Put API listening", "addr", "http://localhost:8080")
	if err := srv.ListenAndServe(); err != nil {
		logger.Error("server stopped", "error", err)
		os.Exit(1)
	}
}
```

Delete the old `main.go` and `middleware.go` at the root. Then run the program from its new folder:

```bash
STAFF_KEY=mama-secret go run -race ./cmd/api
```

`./cmd/api` is the folder holding the `main` package. Go builds it and everything it imports.

Two more commands become useful now that there are several packages:

```bash
go build ./...   # compile every package, to check everything builds
go vet ./...     # look for likely bugs, like a copied mutex
```

`./...` means "this folder and every folder under it".

Try the routes from lessons 2 and 3 again. Everything works exactly as before, which is how it should be: **restructuring changes where code lives, not what it does.**

## The Go in this lesson
<!-- bite: 162bca98-66f5-4dda-bc73-0200dad5eaa7 -->

1. **`import "mamaput/internal/menu"`**: You import your own packages by the module name from `go.mod` plus the folder path. Imports from the standard library and from your module are usually written in two groups, with a blank line between.
2. **Exported and unexported names**: A capital first letter (`Service`, `List`, `ErrDishNotFound`) means other packages can use it. A lower-case one (`list`, `statusRecorder`, `store`) means only this package can. That's Go's whole idea of public and private.
3. **`var ( ... )`**: A block that declares several variables at once. Same for `const ( ... )` and `import ( ... )`.
4. **`errors.New("dish not found")`**: Makes a new error value with that message. Made once, at the top level, it becomes a sentinel others can compare against.
5. **`errors.Is(err, ErrDishNotFound)`**: Asks "is this error, or anything it wraps, that sentinel?". Lesson 7 shows why "anything it wraps" matters; for now, think of it as a careful `==`.
6. **`err.Error()`**: Every error has an `Error()` method that returns its message as a string. That's the entire `error` interface: one method.
7. **`return Dish{}, ErrDishNotFound`**: Returning the zero value with an error is the Go habit. The caller must check the error before using the other value.
8. **`switch { case ...: }`**: A `switch` with nothing after the word works like a chain of `if`/`else if`. The first `case` that's true runs. Go's `switch` doesn't "fall through" to the next case, so there's no `break` to forget.
9. **`mux.HandleFunc("GET /menu", h.list)`**: A **method value**: `h.list` without brackets is the method, bound to `h`, ready to be called later.
10. **`type Status string`** and **`const StatusPending Status = "pending"`**: A new type built on `string`, and constants of that type. `const` values are fixed when the program is compiled.
11. **`map[Status]int{StatusPending: 0, ...}`**: A **map**, from keys to values, written out in place. `statusOrder[to]` looks a key up; a missing key gives the zero value, 0.
12. **`if _, known := statusOrder[to]; !known`**: Looking a key up with two variables gives the value and whether the key was there. We throw the value away with `_` and keep only `known`.
13. **`var err error` set inside a closure**: The function passed to `Update` changes `err`, a variable outside it. A closure can change the variables it captured, not just read them.
14. **`./cmd/api` and `./...`**: Not Go code, but how the `go` command names packages: a folder path, or `...` for "everything below".

## Your project so far
<!-- bite: 866bf48a-5bb6-4ee4-871e-69b8bf4b57dc -->

```text
mama-put/
├── .gitignore
├── go.mod
├── cmd/
│   └── api/
│       └── main.go          ← builds stores, services, handlers; mux, chain, server
└── internal/
    ├── httpx/
    │   ├── json.go          ← WriteJSON, ReadJSON
    │   └── middleware.go    ← LogRequests, RecoverPanic, KitchenOnly, Chain, statusRecorder
    ├── menu/
    │   ├── menu.go          ← Dish, NewDish, DishChanges, ErrDishNotFound, ErrBadDish
    │   ├── store.go         ← MemoryStore: List, Find, Add, Update, Remove
    │   ├── service.go       ← Service: List, Specials, Get, Add, Change, Remove
    │   └── handlers.go      ← Handler, Register (writes behind staff), writeError
    └── orders/
        ├── orders.go        ← Order, Status, NewOrder, the four errors
        ├── store.go         ← MemoryStore: Add, Find, Update
        ├── service.go       ← Service: Place, Get, SetStatus (uses menu.Service)
        └── handlers.go      ← Handler, Register, writeError
```

Each file has one job. Only `handlers.go` files, `httpx` and `main.go` import `net/http`. Services and stores don't know HTTP exists. Add `/api` to `.gitignore` (the program `go build ./cmd/api` makes).

## Common mistakes
<!-- bite: 04d0c13a-5861-4f28-a103-084b24ba8a97 -->

1. **Rules in handlers.** If a handler has an `if` about dishes or orders, it's a rule, and it belongs in the service.
2. **Status codes in services.** A service returns `ErrDishNotFound`; it never decides on 404. Then the same service works for jobs and tests.
3. **A `models/` or `utils/` package.** Types live with the feature that owns them. Helpers live in a package named for what they do.
4. **Stuttering names.** `menu.MenuService` reads "menu menu service". Use `menu.Service`.
5. **Exporting everything.** Start lower-case. Export only what another package really calls.
6. **Code outside `internal/` for no reason.** If nothing outside your module should import it, it goes in `internal/`.
7. **Fixing an import cycle by merging everything into one package.** Ask which way the dependency should point, and whether an interface would break the cycle.

## Check your understanding
<!-- bite: 55a3f920-15cf-48d8-80f3-66d8dacd161a -->

1. What does putting a package under `internal/` stop, and why is that useful?
2. `orders.Service.Place` calls `s.dishes.Get(...)` and gets `menu.ErrDishNotFound`. What does `Place` do with it, and what status does the customer finally get?
3. Why are `h.list`, `h.add` and the others lower-case, while `Register` is exported?
4. A teammate wants the menu package to show, for each dish, how many orders it has today. They add `import "mamaput/internal/orders"` to `menu/service.go`. What happens, and what would you suggest?

<details>
<summary>Answers, after your attempt</summary>

1. It stops code outside your module from importing the package. So you can change it freely without breaking anyone else's code; only your own module can depend on it.
2. It returns it as it is. The orders handler's `writeError` checks `errors.Is(err, menu.ErrDishNotFound)` and answers 404.
3. Nothing outside the `menu` package needs to call one handler directly; they only need to put all of them on a mux. Keeping them unexported makes `Register` the package's one doorway, so the package can change its handlers without anyone else noticing.
4. It won't compile: `orders` already imports `menu`, so this makes an import cycle. Better options: count orders in the orders package and show it there (`GET /orders/stats`), or let the menu package declare a small interface ("something that can count orders for a dish") that `main` fills with the orders service. That second idea is the next lesson.

</details>

## Practice
<!-- bite: df911baf-d6da-4a81-8551-b22f6082f181 -->

1. Write `internal/orders/store.go` and `internal/orders/handlers.go` from the descriptions above. Use the menu ones as your model.
2. Add the rule "Mama only takes orders between 07:00 and 21:00" to `orders.Service.Place`, with a new sentinel `ErrShopClosed` that the handler turns into a 422 Unprocessable Content. Use `time.Now().Hour()`.
3. Run `go vet ./...` and fix anything it reports.

**Done when** `go build ./...` and `go vet ./...` print nothing, every route from lessons 2 and 3 still works the same, and an order placed outside opening hours gets a 422. (To test that without waiting for night, temporarily change the hours.)

## Before moving on
<!-- bite: 8c2ae831-3fb3-4eb7-b592-49f507f1da9a -->

Mama Put API now has a shape: features in their own packages, handlers that only speak HTTP, services that only know rules, stores that only keep data, and a `main` that connects them. Each dependency points one way.

But try writing a test for the shop-hours rule from the practice. You can't, not easily: `Place` calls `time.Now()` itself, so the test passes or fails depending on the time of day. And to test `Place` at all, you must build a real `menu.Service` with a real store. The orders service reaches for its dependencies instead of being given them. In the next lesson, every part receives what it needs, through small interfaces it declares itself, so a test can hand it a fake menu and a fake clock.

## Related
<!-- bite: 026ee3f0-933e-4994-9112-2e1df66e331a -->

- [[backend/frameworks/net-http/05-wiring-dependencies|Next: Wiring Dependencies]]
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers: Controllers, Services and Repositories]] — the idea this lesson builds
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|Organising by Layer vs by Feature]] — why the folders are features
- [[languages/02-go/12-modules-and-project-layout|Modules and Project Layout]] — modules, `internal/` and `cmd/` in the Go course
- [[backend/frameworks/express/04-structuring-an-express-app|The same lesson in Express]]

## About this lesson
<!-- bite: 24563108-f087-4024-9415-ee7afa1d18f6 -->

**Level:** Intermediate. Lesson 4 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later. Rewritten in November 2026 from an older reference note, "Structuring a Go Service".
