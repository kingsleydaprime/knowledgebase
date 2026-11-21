---
id: bbfa9adf-1c18-4ec6-83c0-43062aa4c2c6
---

# Wiring Dependencies

**Wiring dependencies means every part of the app is handed the things it needs, instead of building or finding them itself, and one place at the top builds them all and connects them.** In Go you do it with plain code: constructors that take their dependencies as arguments, small interfaces declared by the code that uses them, and a `main` that wires everything up. No container, no annotations, no magic.

## Before you start
<!-- bite: e1360711-d6c9-4b8a-a93e-6890b2a5e07c -->

You should have:

1. Finished [[backend/frameworks/net-http/04-structuring-a-go-service|lesson 4]], so Mama Put API is split into `cmd/api` and `internal/` packages, including the shop-hours rule from its practice.
2. Read [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]] in the Go course, or be ready to come back to it. This lesson leans on interfaces.

After this lesson you will be able to:

1. Explain what a dependency is, and why a part should receive its dependencies rather than reach for them.
2. Declare a small interface in the package that **uses** it, and say why Go puts it there.
3. Build the whole app in one place, a `run` function, and keep `main` to three lines.
4. Write your first Go tests, using a fake menu and a fake clock.

## Where we stopped
<!-- bite: 0a683b11-2e4c-4032-bfbb-aa9369a573c3 -->

`orders.Service` needs a `*menu.Service` and a `*MemoryStore`, and it calls `time.Now()` itself to check the shop is open. That works when the app runs. But to test the shop-hours rule you'd have to run the test at 22:00. To test "a finished dish can't be ordered" you need a real menu service with a real store holding a finished dish. And when lesson 8 swaps the memory store for PostgreSQL, the orders service would have to change too, even though its rules didn't.

## The kid version
<!-- bite: f97c3790-ad0d-4d71-a89e-d6500cefcb85 -->

Mama doesn't grow her own rice. She doesn't care which farm it's from, either. She needs "a bag of rice, good quality", and whoever brings that is fine. If the usual supplier is out, her son buys from the next market and she cooks exactly the same way.

That's wiring. Mama (the service) says what she needs ("rice"), not where it comes from. Someone else (`main`) goes and gets it, and hands it over. When Mama is learning a new recipe, her son can hand her a cheap practice bag (a fake) and nothing about the cooking changes.

**Where the picture stops working.** In real life, Mama checks the bag. In Go, the compiler checks it for you: if what you hand over doesn't have the methods Mama asked for, the program won't even build.

## Terms used in this lesson
<!-- bite: 45b028a7-aca5-4f65-a982-a8b4b0e4b663 -->

1. **Dependency**: This is something a piece of code needs to do its job. `orders.Service` depends on a store, on a way to look up dishes, and on a clock.
2. **Dependency injection**: This means handing a piece of code its dependencies from outside, usually as arguments to its constructor, instead of letting it make them. The name is grander than the idea.
3. **Composition root**: This is the one place in the program where all the real dependencies are built and connected. In Mama Put API, it's `run` in `cmd/api/main.go`.
4. **Interface**: This is a list of methods. Any type with those methods satisfies it, automatically.
5. **Fake**: This is a small, simple stand-in for a real dependency, written for tests. A fake menu that always says dish 9 is sold out is easier to set up than a real one.
6. **Test**: In Go, this is a function whose name starts with `Test`, in a file ending in `_test.go`, that `go test` runs and that reports failures through `t`.
7. **Table-driven test**: This is a test that lists many cases (inputs and expected results) in a slice, and runs the same checks on each.

## Small interfaces, declared where they're used
<!-- bite: da6e6da0-6816-45c3-b893-17ab8e4f7ab4 -->

Here's the Go idea that makes all of this easy, and it's the opposite of what Java or C# teach.

In those languages, the menu package would declare `interface MenuService { ... }` with every method, and the class would say `implements MenuService`. In Go, the **user** declares the interface, and lists only the methods **it** calls. Look at what `orders.Service` actually uses from the menu: one method, `Get`. So that's all its interface asks for.

At the top of `internal/orders/service.go`, add:

```go
// Menu is what placing an order needs from the menu.
type Menu interface {
	Get(id string) (menu.Dish, error)
}

// Store keeps orders.
type Store interface {
	Add(o Order) Order
	Find(id string) (Order, bool)
	Update(id string, change func(*Order)) (Order, bool)
}
```

And change the service to depend on these, plus a clock:

```go
type Service struct {
	store  Store
	dishes Menu
	now    func() time.Time
	lagos  *time.Location
}

func NewService(store Store, dishes Menu, now func() time.Time) (*Service, error) {
	lagos, err := time.LoadLocation("Africa/Lagos")
	if err != nil {
		return nil, fmt.Errorf("load Lagos time zone: %w", err)
	}
	return &Service{store: store, dishes: dishes, now: now, lagos: lagos}, nil
}
```

`menu.Service` never mentions `orders.Menu`. It doesn't need to. It has a method `Get(id string) (menu.Dish, error)`, so it **already satisfies** `orders.Menu`. Go checks that when you pass a `*menu.Service` to `NewService`, and if the method were missing or had a different shape, the program wouldn't compile.

Why put the interface in `orders` and not `menu`? Three reasons, and they're the heart of Go design:

1. **Each user asks only for what it needs.** Orders needs `Get`. Something else might need `List`. Small interfaces are easy to fake, and they say exactly what a part depends on. The Go proverb is: "the bigger the interface, the weaker the abstraction".
2. **The provider stays free.** The menu package can add, rename or remove other methods without breaking orders, as long as `Get` stays.
3. **It breaks import cycles.** Remember the teammate from lesson 4 who wanted the menu to count orders? With an interface declared in `menu` ("something that can count orders for a dish"), the menu package doesn't import `orders` at all. `main`, which imports both, hands one to the other.

A saying you'll hear: **accept interfaces, return structs.** `NewService` accepts the interfaces `Store` and `Menu`, and returns a concrete `*Service`. The caller gets the real thing with all its methods; the service only demands the little it uses.

## The clock is a dependency too
<!-- bite: d2231bb9-3a3a-4f6e-a451-e015b1dded42 -->

`now func() time.Time` is a dependency that's easy to miss. Any code that calls `time.Now()` directly is code whose result depends on when you run it. So we ask for a function that gives the time, and `main` hands over the real `time.Now`. A test hands over a function that always says 10:00, or 22:00.

It doesn't need an interface. A dependency with one job can just be a function. Go is happy either way.

Now the shop-hours rule, using the clock, in Lagos time:

```go
var ErrShopClosed = errors.New("the shop is closed; Mama Put opens at 7am")

func (s *Service) Place(in NewOrder) (Order, error) {
	hour := s.now().In(s.lagos).Hour()
	if hour < 7 || hour >= 21 {
		return Order{}, ErrShopClosed
	}
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
```

Put `ErrShopClosed` with the other errors in `orders.go`, and add `"errors"`, `"fmt"` and `"time"` to the imports where they're used.

Why `.In(s.lagos)`? Because the server might not be in Lagos. Most cloud servers run on **UTC**, an hour behind Lagos. Without it, Mama's shop would open at 8am Lagos time and close at 10pm. Time zones are a dependency of your rules too.

`time.LoadLocation` reads the time zone rules from the operating system. Tiny Docker images (lesson 28) don't have them, so it would fail there. Adding one import anywhere in the program puts a copy of the rules inside your program instead:

```go
import _ "time/tzdata"
```

Add it to `cmd/api/main.go`. The `_` means "import this for its side effect only; I won't call anything from it".

## The menu service gets an interface too
<!-- bite: 4992b468-3f1c-446d-9ea0-620ecfecc1d6 -->

Do the same to `menu.Service`. It uses five methods of its store, so in `internal/menu/service.go`:

```go
type Store interface {
	List() []Dish
	Find(id string) (Dish, bool)
	Add(d Dish) Dish
	Update(id string, change func(*Dish)) (Dish, bool)
	Remove(id string) bool
}

type Service struct {
	store Store
}

func NewService(store Store) *Service {
	return &Service{store: store}
}
```

Nothing else in the service changes. `*MemoryStore` already has those five methods, so it satisfies `Store`. In lesson 8, a `PostgresStore` with the same five methods will slot straight in, and `menu.Service` won't change by one line.

## One place builds the whole app
<!-- bite: 1910e6ea-6d65-4d01-b2de-cc8d237dc2aa -->

Now the composition root. Two steps.

**First, the app itself becomes a function.** Tests in lesson 16 will want to build the whole HTTP app, with fakes, without starting a real server. So the mux and middleware move into `internal/app/app.go`:

```go
package app

import (
	"log/slog"
	"net/http"

	"mamaput/internal/httpx"
	"mamaput/internal/menu"
	"mamaput/internal/orders"
)

type Deps struct {
	Logger   *slog.Logger
	StaffKey string
	Menu     *menu.Service
	Orders   *orders.Service
}

func New(d Deps) http.Handler {
	staff := httpx.KitchenOnly(d.StaffKey)

	mux := http.NewServeMux()
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Mama Put is open!\n"))
	})
	menu.NewHandler(d.Menu).Register(mux, staff)
	orders.NewHandler(d.Orders).Register(mux, staff)

	return httpx.Chain(mux, httpx.LogRequests(d.Logger), httpx.RecoverPanic(d.Logger))
}
```

`app.New` takes everything the HTTP app needs in one struct, `Deps`, and returns an `http.Handler`. It builds nothing real: no stores, no reading environment variables. It only connects what it's given.

**Second, `main` gets a `run` function.** Replace `cmd/api/main.go` with:

```go
package main

import (
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
	"time"
	_ "time/tzdata"

	"mamaput/internal/app"
	"mamaput/internal/menu"
	"mamaput/internal/orders"
)

func main() {
	if err := run(os.Getenv, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, "mama-put:", err)
		os.Exit(1)
	}
}

func run(getenv func(string) string, stdout io.Writer) error {
	logger := slog.New(slog.NewTextHandler(stdout, nil))

	staffKey := getenv("STAFF_KEY")
	if staffKey == "" {
		return errors.New("STAFF_KEY is not set")
	}

	menuService := menu.NewService(menu.NewMemoryStore(startingMenu))
	orderService, err := orders.NewService(orders.NewMemoryStore(), menuService, time.Now)
	if err != nil {
		return err
	}

	srv := &http.Server{
		Addr: ":8080",
		Handler: app.New(app.Deps{
			Logger:   logger,
			StaffKey: staffKey,
			Menu:     menuService,
			Orders:   orderService,
		}),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       120 * time.Second,
	}

	logger.Info("Mama Put API listening", "addr", "http://localhost:8080")
	return srv.ListenAndServe()
}

var startingMenu = []menu.Dish{
	{ID: "1", Name: "Jollof rice", PriceNaira: 1500, Available: true, Special: true},
	{ID: "2", Name: "Beans and plantain", PriceNaira: 1200, Available: true},
	{ID: "3", Name: "Egusi and pounded yam", PriceNaira: 2500},
}
```

Look at the shape. `main` does only three things: call `run`, print the error if there is one, and exit with 1. Everything else is in `run`, which **returns an error instead of exiting**. That gives you two things:

1. **One way out.** Every failure, from a missing staff key to a port already in use, is a returned error, printed once, the same way.
2. **`run` can be tested.** It takes `getenv` and `stdout` as arguments, instead of reading `os.Getenv` and writing to `os.Stdout` directly. A test can pass in its own settings and capture the logs. Even the program's environment is a dependency.

And read `run` from top to bottom: it is now the **one place** that knows which store is real, which clock is real, and how the parts connect. Want PostgreSQL? Change two lines here. Want a fake clock in a demo? Change one. Nothing else in the app knows or cares.

## Why there's no DI container
<!-- bite: f673a1e3-be4b-4919-9a4a-93ae2aa6c324 -->

In Spring, NestJS or ASP.NET Core, a **container** builds your objects: you mark a class, and it works out what to pass to its constructor. Go programmers mostly don't use one, and Mama Put API won't.

The reason is what you just wrote. `run` is maybe forty lines, and it says exactly what's built and in what order. When something's wrong, you read it. With a container, the wiring is in annotations and rules spread across files, and a mistake shows up when the app starts, or worse, when a request first needs the thing.

Go's compiler already checks the wiring: pass the wrong thing to `NewService` and it won't build. That's most of what a container gives you, for free.

If `run` ever grows to hundreds of lines, Google's **Wire** tool can generate it for you, as plain Go code you can read. Most apps never need it.

## Your first tests
<!-- bite: 66f5a290-43a0-4bae-93b0-702c877450b1 -->

Now the payoff. The orders service can be tested without a real menu, a real store or a real clock.

Create `internal/orders/service_test.go`:

```go
package orders

import (
	"errors"
	"testing"
	"time"

	"mamaput/internal/menu"
)

type fakeMenu map[string]menu.Dish

func (f fakeMenu) Get(id string) (menu.Dish, error) {
	dish, ok := f[id]
	if !ok {
		return menu.Dish{}, menu.ErrDishNotFound
	}
	return dish, nil
}

func clockAt(hour int) func() time.Time {
	lagos, _ := time.LoadLocation("Africa/Lagos")
	return func() time.Time {
		return time.Date(2026, 11, 21, hour, 30, 0, 0, lagos)
	}
}

var testMenu = fakeMenu{
	"2": {ID: "2", Name: "Beans and plantain", PriceNaira: 1200, Available: true},
	"9": {ID: "9", Name: "Ofada stew", PriceNaira: 3000, Available: false},
}

func TestPlaceWorksOutTheTotal(t *testing.T) {
	svc, err := NewService(NewMemoryStore(), testMenu, clockAt(12))
	if err != nil {
		t.Fatal(err)
	}

	order, err := svc.Place(NewOrder{DishID: "2", Quantity: 3})
	if err != nil {
		t.Fatalf("Place returned an error: %v", err)
	}
	if order.TotalNaira != 3600 {
		t.Errorf("total = %d, want 3600", order.TotalNaira)
	}
	if order.Status != StatusPending {
		t.Errorf("status = %q, want %q", order.Status, StatusPending)
	}
}

func TestPlaceRefuses(t *testing.T) {
	tests := []struct {
		name string
		hour int
		in   NewOrder
		want error
	}{
		{"before opening", 6, NewOrder{DishID: "2", Quantity: 1}, ErrShopClosed},
		{"after closing", 21, NewOrder{DishID: "2", Quantity: 1}, ErrShopClosed},
		{"no plates", 12, NewOrder{DishID: "2", Quantity: 0}, ErrBadQuantity},
		{"too many plates", 12, NewOrder{DishID: "2", Quantity: 21}, ErrBadQuantity},
		{"no such dish", 12, NewOrder{DishID: "404", Quantity: 1}, menu.ErrDishNotFound},
		{"finished dish", 12, NewOrder{DishID: "9", Quantity: 1}, ErrDishUnavailable},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			svc, err := NewService(NewMemoryStore(), testMenu, clockAt(tt.hour))
			if err != nil {
				t.Fatal(err)
			}

			_, err = svc.Place(tt.in)
			if !errors.Is(err, tt.want) {
				t.Errorf("got error %v, want %v", err, tt.want)
			}
		})
	}
}
```

Run every test in the module:

```bash
go test ./...
```

```text
?       mamaput/cmd/api         [no test files]
?       mamaput/internal/app    [no test files]
ok      mamaput/internal/orders 0.004s
```

And to see each case by name:

```bash
go test -v ./internal/orders
```

Look at what made this easy:

1. **`fakeMenu` is a map with one method.** Because `orders.Menu` asks for just `Get`, the fake is six lines. If the interface had twenty methods, so would the fake.
2. **`clockAt(6)` is a clock stuck at 06:30.** The "before opening" test passes at any time of day, on any computer, in any time zone.
3. **The table.** Six cases, one loop. Adding a seventh is one line. `t.Run` gives each case its own name, so a failure says exactly which one: `--- FAIL: TestPlaceRefuses/finished_dish`.

Go testing needs no framework. `testing` is in the standard library, `go test` is built into the `go` command, and there's no assertion library: you write an `if`, and call `t.Errorf` when it's wrong. It feels bare at first. It also means every Go test you ever read looks like this one. Lesson 16 is the whole testing story.

## Making the compiler check a promise
<!-- bite: 4714c6ef-0550-431f-bf5e-0803e4961934 -->

One more trick. `menu.Service` satisfies `orders.Menu` today, and you'd find out it stopped when `main` failed to compile. Some people like to state the promise right next to the type, so it's checked even if no code passes one yet. In `cmd/api/main.go`, or in a test:

```go
var _ orders.Menu = (*menu.Service)(nil)
```

It reads: "declare a throwaway variable of type `orders.Menu`, and put a nil `*menu.Service` in it". If `*menu.Service` doesn't satisfy `orders.Menu`, that line won't compile. It costs nothing when the program runs.

## The Go in this lesson
<!-- bite: b70c9a98-bded-4267-b137-688095e26498 -->

1. **`type Menu interface { Get(id string) (menu.Dish, error) }`**: An interface with one method. Any type with exactly that method satisfies it, with no `implements` anywhere.
2. **`now func() time.Time`**: A struct field whose type is a function that takes nothing and returns a time. `time.Now` itself (no brackets) is such a function, so `main` passes `time.Now`.
3. **`(*Service, error)`** from a constructor: `NewService` can fail now (the time zone might not load), so it returns an error too, and `nil` for the service when it fails.
4. **`fmt.Errorf("load Lagos time zone: %w", err)`**: Makes a new error with a message that adds context, and **wraps** the original with `%w`. `errors.Is` can still find the original inside. Lesson 7 is about this.
5. **`s.now().In(s.lagos).Hour()`**: Call the clock, convert the time to Lagos, take the hour (0 to 23). Each method returns a value the next one is called on.
6. **`import _ "time/tzdata"`**: A **blank import**: the package's start-up code runs (here, it embeds the time zone database), but you use nothing from it by name.
7. **`func run(getenv func(string) string, stdout io.Writer) error`**: `io.Writer` is the standard library's interface for "something you can write bytes to", with one method, `Write`. `os.Stdout`, a file, a buffer in a test and an `http.ResponseWriter` all satisfy it.
8. **`fmt.Fprintln(os.Stderr, "mama-put:", err)`**: Prints its arguments, separated by spaces, to standard error, the stream for error messages.
9. **`app.Deps{ Logger: logger, ... }`**: A struct used to pass many dependencies at once, by name. Easier to read than a function with seven arguments, and the order doesn't matter.
10. **`package orders` in `service_test.go`**: A test file in the same package can see unexported names, like the `statusOrder` map. Test files only build during `go test`.
11. **`type fakeMenu map[string]menu.Dish`** with a method: You can give methods to any type you declare, even a map. That's why the fake is so short.
12. **`func TestPlaceRefuses(t *testing.T)`**: The signature every test has. `t.Errorf` reports a failure and carries on; `t.Fatalf` and `t.Fatal` report it and stop this test at once.
13. **`[]struct{ name string; ... }{ {...}, {...} }`**: A slice of an **anonymous struct**, a struct type with no name, declared right where it's used. Perfect for test tables.
14. **`t.Run(tt.name, func(t *testing.T) { ... })`**: Runs a **subtest** with its own name and its own `t`.
15. **`%v`, `%d`, `%q`**: Format verbs, used by `Errorf` and the `fmt` functions. `%v` prints any value in its default form, `%d` a whole number, `%q` a string with quotes around it.
16. **`var _ orders.Menu = (*menu.Service)(nil)`**: `(*menu.Service)(nil)` converts `nil` to the pointer type, giving a typed nil. Assigning it to the interface makes the compiler check the methods.

## Your project so far
<!-- bite: 5fee472d-c252-4c2f-aac5-4dd81c2625b0 -->

```text
mama-put/
├── .gitignore
├── go.mod
├── cmd/
│   └── api/
│       └── main.go              ← main → run(getenv, stdout): the composition root
└── internal/
    ├── app/
    │   └── app.go               ← NEW: Deps, New(deps) http.Handler: mux, routes, middleware
    ├── httpx/
    │   ├── json.go
    │   └── middleware.go
    ├── menu/
    │   ├── menu.go
    │   ├── store.go             ← MemoryStore satisfies menu.Store
    │   ├── service.go           ← Store interface; Service depends on it
    │   └── handlers.go
    └── orders/
        ├── orders.go            ← ErrShopClosed added
        ├── store.go
        ├── service.go           ← Menu and Store interfaces, a clock, Lagos time
        ├── service_test.go      ← NEW: fakeMenu, clockAt, the first table-driven tests
        └── handlers.go          ← ErrShopClosed → 422
```

What changed since lesson 4: services depend on interfaces they declare themselves, the clock is passed in, `internal/app` builds the HTTP app from what it's given, and `run` in `cmd/api` is the only code that builds the real things.

## Common mistakes
<!-- bite: 3a71f6f8-7fb4-4ff7-809d-f0e7836d30a8 -->

1. **Declaring the interface next to the type that satisfies it.** In Go, the user declares it, with only the methods it calls.
2. **Huge interfaces.** A `Menu` interface with every menu method makes every fake huge. Ask for what you use.
3. **Returning an interface from a constructor.** `func NewService(...) Menu` hides the real type's other methods from everyone. Return the struct.
4. **Calling `time.Now()` inside rules.** Pass a clock. Same for random numbers and anything else that changes between runs.
5. **Forgetting the time zone.** Servers usually run on UTC. Convert to Lagos before checking opening hours, and import `time/tzdata` so it works in a container.
6. **`os.Exit` deep inside the app.** It skips deferred clean-up and can't be tested. Return errors up to `main`.
7. **Global variables for dependencies.** `var db *Store` at the top of a package means every test shares it, and you can't tell who uses it. Pass it in.

## Check your understanding
<!-- bite: bdc720bd-b16a-4cd9-ab86-d9bf3bc69a07 -->

1. `orders.Menu` has one method. `menu.Service` has six. Does `*menu.Service` satisfy `orders.Menu`? What would stop it?
2. Why does the "before opening" test pass even when you run it at noon?
3. `run` returns an error instead of calling `os.Exit(1)` itself. Give two reasons that's better.
4. In lesson 8 we'll write `menu.PostgresStore`. Which files have to change to start using it?

<details>
<summary>Answers, after your attempt</summary>

1. Yes. A type satisfies an interface when it has all the interface's methods; extra methods don't matter. It would stop satisfying it if `Get` were renamed, removed, or changed shape (for example, returning `(Dish, bool)` instead of `(Dish, error)`).
2. The service doesn't ask the computer for the time. It calls the clock it was given, and the test gave it `clockAt(6)`, which always says 06:30 in Lagos.
3. Any two of: every failure leaves through one place and is printed the same way; deferred clean-up inside `run` still happens; `run` can be called from a test, which can check the error; `main` stays tiny and has nothing in it to go wrong.
4. Only `cmd/api/main.go`, where `run` builds the store. `menu.Service` depends on the `menu.Store` interface, so it doesn't change. (Plus the new file that holds `PostgresStore`, of course.)

</details>

## Practice
<!-- bite: c9962aa0-4fd5-488f-9a1f-df631bbe1853 -->

1. Write `internal/menu/service_test.go`. Use the real `MemoryStore` (it's simple and fast, no fake needed) and test that `Specials` leaves out a special that isn't available, and that `Change` with a price of 0 returns `ErrBadDish`.
2. Add a test to `orders` for `SetStatus`: pending → ready works, ready → pending gives `ErrBadStatusChange`, and an unknown status like `"eaten"` gives `ErrBadStatusChange` too.
3. Make `KitchenOnly`'s staff key come through `app.Deps` (it already does) and check: is there anywhere else in `internal/` that reads an environment variable? There shouldn't be. Use `grep -rn "os.Getenv" internal/` to look.

**Done when** `go test ./...` passes, `go test -v ./internal/...` shows each case by name, and `grep -rn "os.Getenv\|time.Now()" internal/` finds nothing outside test files.

## Before moving on
<!-- bite: 84506da1-53d6-4b78-b01d-31b44558fa17 -->

Every part of Mama Put API now receives what it needs. Services depend on small interfaces they declare themselves, the clock is a dependency, `run` is the one place that builds the real things, and you have your first table-driven tests, using a fake menu and a fake clock.

Now look at what the handlers accept. `POST /menu` with `{"name": "Moi moi", "priceNaira": "800"}` (a string, not a number) gets a confusing error. `{"name":"Moi moi","priceNaira":800,"isFree":true}` gets accepted, and `isFree` is silently ignored. A body of 2 GB is read until the server runs out of memory. And `GET /menu/abc` is treated as a real ID. The service rules can't fix these, because they're about the **shape** of the input, not Mama's rules. Checking input at the door is the next lesson.

## Related
<!-- bite: 7be75a9a-a6de-4b9a-9971-6fa1d00ca96b -->

- [[backend/frameworks/net-http/06-validation|Next: Input Validation]]
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|Dependency Injection and Wiring]] — the idea, across languages
- [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]] — interfaces in the Go course
- [[languages/02-go/11-testing-and-benchmarking|Testing and Benchmarking]] — `go test` in depth
- [[backend/frameworks/express/05-wiring-dependencies|The same lesson in Express]]

## About this lesson
<!-- bite: 354c063d-270c-4339-95b7-2aafff6abac0 -->

**Level:** Intermediate. Lesson 5 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later.
