---
id: 268fba07-dc55-4870-b304-f08b71bb6f29
---

# Routing

**Routing is choosing which function answers a request, using its method and its path.** `GET /menu` goes to the function that lists the menu, `DELETE /menu/7` goes to the one that removes dish 7. In Go, the built-in `http.ServeMux` does this, and since Go 1.22 it understands methods and IDs in the path by itself.

## Before you start
<!-- bite: eb864305-7961-4424-a43f-3d8536556f7d -->

You should have:

1. Finished [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|lesson 1]], so Mama Put API starts and answers `GET /menu`.
2. A rough idea of what REST means. [[backend/02-api-design/01-apis-and-rest|APIs and REST]] explains it from the start.

After this lesson you will be able to:

1. Design the routes for a resource: list, get one, add, change, remove.
2. Read path values, query parameters and a JSON body.
3. Pick the right status code for each answer.
4. Explain how the mux chooses between two patterns that both match.
5. Protect shared data from two requests changing it at once, and prove it with the race detector.

## Where we stopped
<!-- bite: 283b207d-9a6d-4d92-8245-d28a6d4fd18d -->

Mama Put API has two routes. `GET /menu` sends a slice of dishes written straight into the code. Nobody can add a dish, change a price or ask for one dish. Today the menu becomes a proper **resource** that the kitchen can manage.

## The kid version
<!-- bite: e2d3fc44-f1d6-4cde-bdf5-64c16c02d0c4 -->

Mama's stand has different windows. At one window you look at the menu. At another, you hand over an order. Behind the counter, only Mama changes what's in the pots.

Routing is the signboard over each window. "Want to see the menu? This window. Want dish number 7? That window, and say the number." Every request walks to exactly one window.

**Where the picture stops working.** A real stand has a handful of windows. An API can have hundreds of routes, and two signboards can both seem to fit the same request. The mux needs a rule for choosing, and Go's rule is different from Express's. We'll see it below.

## Terms used in this lesson
<!-- bite: da330ead-babe-4ac6-9125-11a2a480a276 -->

1. **Resource**: This is a thing your API lets clients work with, like the menu or an order. In REST, each resource has an address (a path), and the method says what you want to do to it.
2. **Pattern**: This is the text you give the mux, like `GET /menu/{id}`. It has an optional method, then a path that can contain wildcards.
3. **Wildcard**: This is a part of a pattern in curly braces, like `{id}`. It matches any one segment of the path, and you read what it matched with `r.PathValue("id")`.
4. **Path segment**: This is one piece of a path between slashes. `/menu/7` has two segments, `menu` and `7`.
5. **Query parameter**: This is a named value after the `?` in an address, like `?available=true`. It's for options, such as filtering, not for saying which thing you want.
6. **Body**: This is the data sent with a request, after the headers. For a POST or PATCH, it's usually JSON describing the new thing or the change.
7. **Data race**: This happens when two goroutines touch the same data at the same time and at least one of them is changing it. The result is unpredictable, and it can corrupt your data without any error.
8. **Mutex**: This is short for **mutual exclusion**. It's a lock: a goroutine takes it before touching shared data and gives it back after, so only one goroutine is inside at a time.

## The routes for the menu
<!-- bite: 5fe74cf2-322d-428b-930e-1e166979ee18 -->

Here is the menu as a REST resource. The path names **what**, the method says **what to do**.

| Method and path | What it does | Success status |
|---|---|---|
| `GET /menu` | list the dishes | 200 |
| `GET /menu/specials` | list today's specials | 200 |
| `GET /menu/{id}` | get one dish | 200 |
| `POST /menu` | add a dish | 201, and a `Location` header |
| `PATCH /menu/{id}` | change some fields of a dish | 200 |
| `DELETE /menu/{id}` | remove a dish | 204, no body |

Notice there's no `/getDish` or `/deleteDish`. The verb is already in the method. And `{id}` is in the path, not the query, because it says **which** dish, not how to show it.

## A store that's safe with many goroutines
<!-- bite: 8be01b93-5391-47c8-9423-d0dd57c0ae1b -->

Before the routes, the menu needs somewhere to live that can change. We'll keep it in memory for now (lesson 8 moves it into PostgreSQL), but there's a catch that Express never had.

Node runs your JavaScript on one thread, so two requests never touch the `dishes` array at exactly the same moment. Go starts a goroutine per request, and goroutines really do run at the same time, on different CPU cores. Two `POST /menu` requests arriving together would both read `nextID`, both get 3, and both write dish 3. Worse, Go's slices and maps aren't safe to change from two goroutines at once: a map changed by two goroutines can crash the whole program with `fatal error: concurrent map writes`.

So the store gets a mutex. Replace the `Dish` type and the `dishes` slice in `main.go` with:

```go
type Dish struct {
	ID         string `json:"id"`
	Name       string `json:"name"`
	PriceNaira int    `json:"priceNaira"`
	Available  bool   `json:"available"`
	Special    bool   `json:"special"`
}

type menuStore struct {
	mu     sync.Mutex
	dishes []Dish
	nextID int
}

func newMenuStore() *menuStore {
	return &menuStore{
		dishes: []Dish{
			{ID: "1", Name: "Jollof rice", PriceNaira: 1500, Available: true, Special: true},
			{ID: "2", Name: "Beans and plantain", PriceNaira: 1200, Available: true},
			{ID: "3", Name: "Egusi and pounded yam", PriceNaira: 2500, Available: false},
		},
		nextID: 4,
	}
}

func (s *menuStore) list() []Dish {
	s.mu.Lock()
	defer s.mu.Unlock()
	return slices.Clone(s.dishes)
}

func (s *menuStore) find(id string) (Dish, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	for _, d := range s.dishes {
		if d.ID == id {
			return d, true
		}
	}
	return Dish{}, false
}

func (s *menuStore) add(d Dish) Dish {
	s.mu.Lock()
	defer s.mu.Unlock()
	d.ID = strconv.Itoa(s.nextID)
	s.nextID++
	s.dishes = append(s.dishes, d)
	return d
}

func (s *menuStore) update(id string, change func(*Dish)) (Dish, bool) {
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

func (s *menuStore) remove(id string) bool {
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

Every method starts with `s.mu.Lock()` and `defer s.mu.Unlock()`. That pair means "wait until no one else is inside, come in, and leave when this function returns, whatever happens". Only one goroutine can be inside any of these methods at a time, so `nextID` can't be read twice.

Two details matter:

1. **`list` returns a copy** (`slices.Clone`). If it returned `s.dishes` itself, the handler would be reading the slice after the lock was released, while another goroutine might be changing it. The lock only protects what happens inside it.
2. **`update` takes a function** that changes the dish while the lock is held. That way, "find the dish and change it" happens as one step, and no one can delete the dish halfway through.

## Reading the path: one dish
<!-- bite: 576d5f0d-c6c3-438c-bb20-1ec617e63415 -->

Now a small helper, so every handler doesn't repeat three lines to send JSON. Put it at the bottom of `main.go`:

```go
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}
```

It does the three steps from lesson 1 in the right order: header, status, body. Every route uses it from now on.

The routes go in their own function, so `main` stays short. Add this:

```go
func registerMenuRoutes(mux *http.ServeMux, store *menuStore) {
	mux.HandleFunc("GET /menu", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, store.list())
	})

	mux.HandleFunc("GET /menu/{id}", func(w http.ResponseWriter, r *http.Request) {
		dish, ok := store.find(r.PathValue("id"))
		if !ok {
			http.Error(w, "dish not found", http.StatusNotFound)
			return
		}
		writeJSON(w, http.StatusOK, dish)
	})
}
```

`{id}` in the pattern matches one path segment, and `r.PathValue("id")` gives you what it matched, always as a string. `GET /menu/7` gives `"7"`, and `GET /menu/jollof` gives `"jollof"`; it's your job to decide whether that's a valid ID. (Lesson 6 does that properly.)

`http.Error` sends a plain-text error with the status you give it. And see the `return` after it. Go doesn't stop your function when you send a response. Without that `return`, it would carry on and also call `writeJSON`, sending a second, broken response.

In `main`, replace the old menu route with:

```go
store := newMenuStore()
registerMenuRoutes(mux, store)
```

Add `"slices"`, `"strconv"` and `"sync"` to the imports, and run it:

```bash
curl http://localhost:8080/menu/2
# {"id":"2","name":"Beans and plantain","priceNaira":1200,"available":true,"special":false}

curl -i http://localhost:8080/menu/99
# HTTP/1.1 404 Not Found
# ...
# dish not found
```

## Reading the query: filtering the list
<!-- bite: 8e4a5164-d3f3-42c4-9c5f-6b444ebfdf4e -->

The phone app wants to show only dishes still available. That's an option on the same list, so it's a query parameter: `GET /menu?available=true`.

Change the `GET /menu` handler:

```go
mux.HandleFunc("GET /menu", func(w http.ResponseWriter, r *http.Request) {
	dishes := store.list()
	if r.URL.Query().Get("available") == "true" {
		dishes = slices.DeleteFunc(dishes, func(d Dish) bool { return !d.Available })
	}
	writeJSON(w, http.StatusOK, dishes)
})
```

`r.URL.Query()` reads everything after the `?` into a map of names to values, and `.Get` gives you the first value for a name, or `""` if it isn't there. Like path values, query values are always strings. `?available=yes` is simply not `"true"`, so the filter is off. Lesson 6 makes bad values a 400 instead of quietly ignoring them, and lesson 9 builds full filtering, sorting and pages.

We could filter like this because `list` returned a copy. `slices.DeleteFunc` changes the slice it's given, and changing the store's own slice would have deleted dishes from the menu for everyone.

## Which pattern wins
<!-- bite: eaaa584d-c5f4-4ea5-90ae-703fc4ee6abe -->

Now the specials. Add, inside `registerMenuRoutes`:

```go
mux.HandleFunc("GET /menu/specials", func(w http.ResponseWriter, r *http.Request) {
	dishes := slices.DeleteFunc(store.list(), func(d Dish) bool { return !d.Special })
	writeJSON(w, http.StatusOK, dishes)
})
```

Here's the puzzle. `GET /menu/specials` matches the pattern `GET /menu/specials`, but it also matches `GET /menu/{id}`, with `id` = `"specials"`. Which one runs?

In Express, the answer is "whichever you wrote first", and writing them in the wrong order is a famous bug. Go's answer is different: **the most specific pattern wins, whatever order you registered them in.** `/menu/specials` only matches one path; `/menu/{id}` matches many. So `/menu/specials` is more specific, and it wins.

The rule, in plain words: if every request one pattern matches is also matched by the other, but not the other way round, the narrower one wins. A method counts too: `GET /menu` beats a pattern with no method, `/menu`.

And if two patterns overlap and **neither** is narrower, like `GET /menu/{id}/photo` and `GET /menu/specials/{size}` (which both match `/menu/specials/photo`), Go refuses to start: registering the second one **panics** with a message naming both patterns. That's a gift. The conflict shows up the moment you run the server, not months later as a strange bug.

Two more pattern tools you'll want:

1. **`{$}` at the end** matches only that exact path, with nothing after it. You used it in lesson 1 for `GET /{$}`.
2. **`{name...}` at the end** matches the rest of the path, slashes and all. `GET /files/{path...}` matches `/files/photos/jollof.jpg` with `path` = `"photos/jollof.jpg"`.

## Reading the body: adding a dish
<!-- bite: cf14dd6d-9ede-4ccf-b2de-0bdf29160091 -->

To add a dish, the kitchen sends its details as JSON in the body. We need a struct for what they send. It's not a `Dish`, because the client mustn't choose the ID:

```go
type newDish struct {
	Name       string `json:"name"`
	PriceNaira int    `json:"priceNaira"`
	Special    bool   `json:"special"`
}
```

And the route:

```go
mux.HandleFunc("POST /menu", func(w http.ResponseWriter, r *http.Request) {
	var in newDish
	if err := json.NewDecoder(r.Body).Decode(&in); err != nil {
		http.Error(w, "body must be JSON describing a dish", http.StatusBadRequest)
		return
	}
	if in.Name == "" || in.PriceNaira <= 0 {
		http.Error(w, "name and a positive priceNaira are required", http.StatusBadRequest)
		return
	}

	dish := store.add(Dish{Name: in.Name, PriceNaira: in.PriceNaira, Special: in.Special, Available: true})

	w.Header().Set("Location", "/menu/"+dish.ID)
	writeJSON(w, http.StatusCreated, dish)
})
```

`json.NewDecoder(r.Body).Decode(&in)` reads the body and fills `in`. We pass `&in`, the address of `in`, because `Decode` has to change our variable, and in Go a function can only change something you give it the address of.

The answer is **201 Created**, not 200, and the `Location` header says where the new dish lives. A good client can follow it without guessing.

Try it:

```bash
curl -i -X POST http://localhost:8080/menu \
  -H "Content-Type: application/json" \
  -d '{"name":"Moi moi","priceNaira":800}'
# HTTP/1.1 201 Created
# Location: /menu/4
# ...
# {"id":"4","name":"Moi moi","priceNaira":800,"available":true,"special":false}
```

Those two `if` checks are the bare minimum. A body like `{"name":"Moi moi","priceNaira":800,"pricenaira":-5}` or a 2 GB body would still get through. Lesson 6 closes those holes.

## Changing part of a dish
<!-- bite: cfc03e4e-12c0-42d8-acd2-0565d0c6ce2d -->

`PATCH` means "change only the fields I sent". If the kitchen sends `{"available": false}`, the price and name must stay as they are.

That raises a very Go problem. If the struct has `Available bool`, and the client didn't send `available`, the field is `false` anyway, its zero value. You can't tell "they sent false" from "they didn't send it". The fix is a **pointer** field: a pointer is `nil` when nothing was sent, and points at a value when something was.

```go
type dishChanges struct {
	Name       *string `json:"name"`
	PriceNaira *int    `json:"priceNaira"`
	Available  *bool   `json:"available"`
	Special    *bool   `json:"special"`
}
```

And the route:

```go
mux.HandleFunc("PATCH /menu/{id}", func(w http.ResponseWriter, r *http.Request) {
	var in dishChanges
	if err := json.NewDecoder(r.Body).Decode(&in); err != nil {
		http.Error(w, "body must be JSON", http.StatusBadRequest)
		return
	}

	dish, ok := store.update(r.PathValue("id"), func(d *Dish) {
		if in.Name != nil {
			d.Name = *in.Name
		}
		if in.PriceNaira != nil {
			d.PriceNaira = *in.PriceNaira
		}
		if in.Available != nil {
			d.Available = *in.Available
		}
		if in.Special != nil {
			d.Special = *in.Special
		}
	})
	if !ok {
		http.Error(w, "dish not found", http.StatusNotFound)
		return
	}
	writeJSON(w, http.StatusOK, dish)
})
```

`*in.Name` means "the value the pointer points at". Only the fields that were sent are copied, while the store's lock is held.

## Removing a dish
<!-- bite: 0db2a980-31c3-4d22-8cf6-55541601fcd8 -->

```go
mux.HandleFunc("DELETE /menu/{id}", func(w http.ResponseWriter, r *http.Request) {
	if !store.remove(r.PathValue("id")) {
		http.Error(w, "dish not found", http.StatusNotFound)
		return
	}
	w.WriteHeader(http.StatusNoContent)
})
```

**204 No Content** means "done, and there's nothing to send back". You call `WriteHeader` and write no body.

## Status codes, all in one place
<!-- bite: 81c46819-7a53-453e-b3e9-ddb7ca6a9d66 -->

These are the ones Mama Put API uses so far:

1. **200 OK**: it worked, and here's the answer.
2. **201 Created**: a new thing was made. Send a `Location` header too.
3. **204 No Content**: it worked, and there's nothing to send.
4. **400 Bad Request**: the client sent something we can't use (broken JSON, a missing name).
5. **404 Not Found**: there's no such thing at that address.
6. **405 Method Not Allowed**: the path exists but not with that method. The mux sends this for you.

There are many more, and lesson 7 adds 401, 403, 409 and 422 when we design the error responses. The rule behind all of them: the status is for programs. A phone app, a proxy or a monitoring tool reads the number, not your message.

## Proving the lock works
<!-- bite: abce9797-bbc5-4a6c-b39c-2e68b064d1b3 -->

You wrote a mutex because I told you to. Let's prove it matters. Go has a built-in **race detector** that watches memory while your program runs and reports any data race it sees.

First, break the store on purpose. Comment out the two lock lines in `add`:

```go
func (s *menuStore) add(d Dish) Dish {
	// s.mu.Lock()
	// defer s.mu.Unlock()
	...
```

Run the server with the race detector on:

```bash
go run -race .
```

In another terminal, send twenty POSTs at the same time. The `&` at the end of each line starts it in the background, so they all go out together:

```bash
for i in $(seq 1 20); do
  curl -s -o /dev/null -X POST http://localhost:8080/menu \
    -d '{"name":"Akara","priceNaira":300}' &
done; wait
```

Look at the server's terminal. You'll see `WARNING: DATA RACE`, the two goroutines involved, and the exact lines in `add` where they collided. Now `curl http://localhost:8080/menu` and look at the IDs: you may see the same ID twice.

Put the two lines back, run it again with `-race`, and send the twenty POSTs again. Silence, and twenty different IDs.

Make `go run -race .` a habit while developing. The race detector only reports races that actually happen while it watches, so it's not proof there are none, but it catches most of them the first time two requests overlap.

## The Go in this lesson
<!-- bite: aa233629-8f61-4bea-9cb5-43c281b9c4db -->

1. **`type menuStore struct { mu sync.Mutex; ... }`**: A struct can hold a mutex as a field. Its zero value is an unlocked mutex, ready to use, so `newMenuStore` doesn't set it.
2. **`func newMenuStore() *menuStore`**: Go has no constructors. By habit, a function called `newX` builds an `X` and returns it, here as a pointer.
3. **`func (s *menuStore) list() []Dish`**: A method with a **pointer receiver**. `s` points at the real store, so methods change the real thing, and the mutex inside isn't copied. A mutex must never be copied; a pointer receiver is how you avoid it.
4. **`defer s.mu.Unlock()`**: `defer` runs a call when the surrounding function returns, however it returns. Lock, then defer the unlock on the next line, and you can't forget it on some early `return`.
5. **`(Dish, bool)`**: A function can return several values. `find` returns the dish and `true`, or an empty `Dish{}` and `false`. The caller writes `dish, ok := store.find(id)`. This "comma ok" style is how Go says "maybe nothing was there".
6. **`for _, d := range s.dishes`**: `range` walks a slice, giving the index and a **copy** of each element. `_` throws away a value you don't need. In `update` we loop with `for i := range` and use `s.dishes[i]`, because changing `d` would only change the copy.
7. **`strconv.Itoa(s.nextID)`** and **`s.nextID++`**: `strconv` converts between strings and numbers (`Itoa` is "integer to ASCII"). `++` adds one; in Go it's a statement on its own, never part of an expression.
8. **`append(s.dishes, d)`**: adds to the end of a slice and returns the new slice. You must store the result, because `append` may have moved the slice to a bigger space.
9. **`slices.Clone`, `slices.Delete`, `slices.DeleteFunc`**: helpers from the standard `slices` package. `Clone` copies, `Delete` removes the elements from index `i` up to (not including) `i+1`, and `DeleteFunc` removes every element the function says yes to.
10. **`func(d Dish) bool { return !d.Available }`**: a function passed as a value. `!` means "not".
11. **`change func(*Dish)`**: a parameter whose type is a function that takes a pointer to a `Dish`. Functions are ordinary values in Go.
12. **`v any`**: `any` means "a value of any type". `writeJSON` can send dishes, slices or anything else, because `Encode` also accepts `any`.
13. **`var in newDish`**: declares a variable with its zero value: empty name, 0 price, `false`. `Decode` then fills in what the JSON contained.
14. **`if err := ...; err != nil { ... }`**: an `if` with a short statement before the condition. `err` exists only inside this `if`. `nil` means "no error". This is the Go pattern you will type more than any other.
15. **`&in`** and **`*in.Name`**: `&` takes the address of a variable, making a pointer. `*` in front of a pointer gives the value it points at. In a type, `*string` means "a pointer to a string".
16. **`"/menu/" + dish.ID`**: `+` joins strings.

## Your project so far
<!-- bite: 6ebe1140-db09-4714-a358-0df5d597d25c -->

```text
mama-put/
├── .gitignore
├── go.mod
└── main.go     ← Dish, menuStore (with a mutex), newDish, dishChanges,
                   registerMenuRoutes, writeJSON, and main
```

1. **`main.go`**: still the only file, on purpose. It now holds the `Dish` type, the `menuStore` with its lock and five methods, the two input types `newDish` and `dishChanges`, `registerMenuRoutes` with all six menu routes, the `writeJSON` helper, and `main`, which builds the store, registers the routes and starts the server with its timeouts. In lesson 4 it gets split into packages.

## Common mistakes
<!-- bite: aa06e0e6-63c0-47f6-87cf-04ba054e87fb -->

1. **No `return` after `http.Error`.** The function carries on and sends a second response. Every error branch ends with `return`.
2. **Sharing data between requests without a lock.** Maps and slices aren't safe for goroutines changing them at once. Lock, or keep the data somewhere that handles it (a database).
3. **Returning the store's own slice.** The lock is released, and the caller reads while others write. Return a copy.
4. **Copying a mutex.** A value receiver (`func (s menuStore)`) copies the struct and its mutex, and the lock stops working. Use a pointer receiver. `go vet` warns about this.
5. **Plain `bool` and `int` fields for PATCH.** You can't tell "not sent" from "zero". Use pointers.
6. **Verbs in paths.** `/deleteDish/7` instead of `DELETE /menu/7`. The method is the verb.
7. **200 for everything.** A new dish is 201 with a `Location`; a removal with nothing to say is 204.

## Check your understanding
<!-- bite: 0824c442-0480-41e9-9567-d649eab9fd73 -->

1. You register `GET /menu/{id}` first and `GET /menu/specials` second. A request comes for `GET /menu/specials`. Which handler runs, and why?
2. Why does `PATCH` decode into `dishChanges` with pointer fields, and not into `Dish`?
3. Without the mutex, two `POST /menu` requests arrive at the same moment. Describe one thing that could go wrong.
4. What's wrong with this?

   ```go
   func (s menuStore) add(d Dish) Dish {
   	s.mu.Lock()
   	defer s.mu.Unlock()
   	...
   }
   ```

<details>
<summary>Answers, after your attempt</summary>

1. The specials handler. Go picks the most specific pattern, not the first registered. `/menu/specials` matches exactly one path, which `/menu/{id}` also matches, so it's narrower and wins.
2. Because with plain fields you can't tell a field the client left out from one they set to its zero value. `{"name":"Fried rice"}` would decode `Available` as `false` and take the dish off the menu. A pointer field is `nil` when the field wasn't sent.
3. Both read `nextID` before either adds one, so both dishes get the same ID. Or both `append` at once and one dish is lost. The race detector reports it as a data race.
4. The receiver is a value, so `s` is a **copy** of the store, including a copy of the mutex. Each call locks its own copy, which protects nothing, and the dish is appended to the copy's slice, so it's lost when the method returns. It should be `func (s *menuStore)`.

</details>

## Practice
<!-- bite: 1c9c7462-feb0-4217-9eb5-36ada6606036 -->

Give Mama Put API its first orders:

1. An `Order` has `ID`, `DishID`, `Quantity`, `TotalNaira` and `Status` (start it at `"pending"`). Make an `orderStore` with a mutex, like `menuStore`.
2. `POST /orders` takes `{ "dishId": "2", "quantity": 3 }`. If the dish doesn't exist or isn't available, answer 400. Otherwise work out the total from the dish's price, save the order, and answer 201 with a `Location`.
3. `GET /orders/{id}` returns one order, or 404.
4. `PATCH /orders/{id}/status` takes `{ "status": "ready" }`.

**Done when** you can place an order for dish 2 and see the right total, an order for dish 3 (not available) gets a 400, and twenty orders sent at once with `go run -race .` running give twenty different IDs and no race warning.

## Before moving on
<!-- bite: 590124a1-e8c5-412d-8229-ee62b24bc6a1 -->

Mama Put API now has a full menu resource: six routes, three ways of reading input (path, query, body), honest status codes, and a store two goroutines can't corrupt.

But look at what's missing. Anyone can `DELETE /menu/1`, not just the kitchen. Nothing is logged, so when something goes wrong you won't know which request did it. And if a handler panics, you'd like one place to catch it. Each of those is something every request should go through, before or after its handler. In Go that's a function that wraps a handler, called **middleware**, and it's the next lesson.

## Related
<!-- bite: 7a46c9f0-97e5-4c2a-9a2e-e7520a672e7e -->

- [[backend/frameworks/net-http/03-middleware|Next: Middleware]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — the design behind these routes
- [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]] — mutexes, and when a channel fits better
- [[backend/frameworks/express/02-routing|The same lesson in Express]] — where route order decides instead

## About this lesson
<!-- bite: c93567ed-858f-4390-97c5-b368fafa41a4 -->

**Level:** Beginner. Lesson 2 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later; method and wildcard patterns need Go 1.22.
