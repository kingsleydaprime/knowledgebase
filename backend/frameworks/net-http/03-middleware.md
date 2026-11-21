---
id: e5808543-ba85-4c12-a67a-ee1255553d33
---

# Middleware

**Middleware is code that runs around your handlers, for every request or for a group of them: logging, checking who's calling, catching crashes.** In Go it has one shape, a function that takes a handler and returns a new handler that does something extra before or after calling the first one. That's the whole idea, and it's built only from what you learned in lesson 1.

## Before you start
<!-- bite: 2f7d00d2-75bf-43ab-bfd4-eb5786e2a0f2 -->

You should have:

1. Finished [[backend/frameworks/net-http/02-routing|lesson 2]], so Mama Put API has its six menu routes and a locked store.
2. Done the lesson 2 practice, so there are order routes too. If you skipped it, the lesson still works; just leave the order lines out.

After this lesson you will be able to:

1. Write middleware as `func(http.Handler) http.Handler`.
2. Log every request with its status and how long it took.
3. Catch a panicking handler and answer 500 instead of dropping the connection.
4. Protect only some routes with a staff-key check.
5. Explain why the order you wrap middleware in changes how the app behaves.

## Where we stopped
<!-- bite: f462c547-50a2-4f8d-9d5d-6e7a67b4a8a0 -->

The menu works, but anyone can delete a dish, nothing is logged, and a bug that panics in one handler just cuts the customer off. Each of these needs code that runs on many routes. Writing it inside every handler would mean copying it twenty times and forgetting it once.

## The kid version
<!-- bite: 9388f459-6bd0-4853-8779-51de3efe7ec2 -->

Before a customer reaches Mama's pots, they pass her son at the gate. He writes down who came and when. If the customer is heading behind the counter, he checks they're family. And if something spills and someone shouts, he's the one who calms everyone down and says "sorry, come back".

Middleware is the son at the gate. Mama (your handler) just cooks. The son does the same few jobs for everybody, before and after.

**Where the picture stops working.** There's one son. In Go you can have as many gates as you like, one inside the other, and each can see the customer on the way in and on the way out. The order of the gates matters, and that's where the bugs live.

## Terms used in this lesson
<!-- bite: a639729f-6f41-4437-9c79-a125692a3dec -->

1. **Middleware**: This is a function that wraps a handler. It gets the next handler, and returns a new handler that does its own work and then (usually) calls the next one.
2. **Wrapping**: This is putting one handler inside another, so the outer one runs first and decides whether and when to call the inner one.
3. **Chain**: This is several middleware wrapped one inside the other, with your mux at the centre.
4. **Panic**: This is Go's word for a crash in the middle of a function: a nil pointer, an index past the end of a slice, or a call to `panic(...)`. It unwinds the goroutine until something **recovers** it, or the program dies.
5. **Recover**: This is the built-in Go function that stops a panic, if it's called from a deferred function while the panic is happening.
6. **Structured log**: This is a log line made of named fields (`method=GET path=/menu status=200`) instead of a free sentence, so programs can search and count them.
7. **Constant-time comparison**: This is comparing two secrets in a way that always takes the same time, so an attacker can't learn the secret by timing how fast wrong guesses fail.

## The shape of every middleware
<!-- bite: b6c3a262-f9da-43f4-b8e2-9a9538e3ed29 -->

Here is a middleware that does nothing at all, so you can see the bones:

```go
func doNothing(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// before: runs on the way in
		next.ServeHTTP(w, r)
		// after: runs on the way out
	})
}
```

Read it slowly:

1. It takes `next`, the handler it's wrapping.
2. It returns a new handler, made from a function with `http.HandlerFunc`, from lesson 1.
3. When a request comes, the new handler can do something, then call `next.ServeHTTP(w, r)` to pass the request on, then do something else after.
4. If it decides the request shouldn't go on (wrong staff key), it writes a response itself and **doesn't** call `next`. The inner handler never runs.

Because what comes out is a plain `http.Handler`, you can wrap it again, and again. That's all a chain is: `logRequests(recoverPanic(mux))` is a handler, inside a handler, inside a handler.

There's no special middleware type, no registration, no `next()` function to remember to call with the right arguments. A middleware written this way works with any Go router and any Go framework that uses `net/http`. You'll see that pay off in the [[backend/frameworks/chi/index|Chi]] subject, where these exact functions plug straight in.

## Middleware 1: logging every request
<!-- bite: 27e353a9-7c64-444a-99fb-f1b89701bbe1 -->

We want one line per request: the method, the path, the status, and how long it took. The first three are easy. The status is the problem, because `http.ResponseWriter` has no way to ask "what status did you send?". It's a pipe, and things go down it, not back up.

So the logger gives the handler a different `ResponseWriter`: one that passes everything through, but writes down the status on the way. Make a new file next to `main.go`, called `middleware.go`:

```go
package main

import (
	"log/slog"
	"net/http"
	"time"
)

type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (rec *statusRecorder) WriteHeader(code int) {
	rec.status = code
	rec.ResponseWriter.WriteHeader(code)
}

func (rec *statusRecorder) Unwrap() http.ResponseWriter {
	return rec.ResponseWriter
}

func logRequests(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			rec := &statusRecorder{ResponseWriter: w, status: http.StatusOK}

			next.ServeHTTP(rec, r)

			logger.Info("request",
				"method", r.Method,
				"path", r.URL.Path,
				"status", rec.status,
				"duration", time.Since(start),
			)
		})
	}
}
```

Three things are happening.

**The recorder.** `statusRecorder` has the real `ResponseWriter` inside it as an **embedded field** (a field with a type but no name). Embedding means all of the real writer's methods (`Header`, `Write`) become the recorder's methods too, for free. We only replace `WriteHeader`, to note the code before passing it on. We start `status` at 200, because a handler that calls `Write` without `WriteHeader` sends a 200.

**`Unwrap`.** This one line saves you a real headache later. Some handlers need things the plain `ResponseWriter` interface doesn't list, like **flushing** (pushing data to the client right now, which the live kitchen screen in lesson 20 needs). Our recorder hides those. Go's `http.ResponseController` looks for an `Unwrap` method to find the real writer underneath, so with it, flushing still works through the recorder. Every `ResponseWriter` wrapper you write should have it.

**The logger.** `log/slog` is Go's built-in structured logger. `logger.Info("request", "method", r.Method, ...)` takes a message and then pairs of name and value. Notice `logRequests` doesn't take `next` directly: it takes the logger and **returns** a middleware. That's the usual way to give a middleware settings it needs.

## Middleware 2: catching panics
<!-- bite: fe2b17c1-0027-4fe4-b9a2-b8965ddd8f1c -->

Add this to `middleware.go`:

```go
func recoverPanic(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				err := recover()
				if err == nil {
					return
				}
				if err == http.ErrAbortHandler {
					panic(err)
				}
				logger.Error("panic", "error", err, "path", r.URL.Path, "stack", string(debug.Stack()))
				w.Header().Set("Connection", "close")
				http.Error(w, "something went wrong on our side", http.StatusInternalServerError)
			}()

			next.ServeHTTP(w, r)
		})
	}
}
```

And add `"runtime/debug"` to the imports in `middleware.go`.

A deferred function runs when the surrounding function returns, **including when it's being unwound by a panic**. Inside it, `recover()` stops the panic and gives you what was panicked with. If there was no panic, it returns `nil` and we do nothing.

When there was one, we log it with the **stack trace** (the list of function calls that led to it, so you can find the bug) and answer 500. The message to the customer is deliberately vague. They don't need to know what a nil pointer is, and the details could help an attacker. They go to the log.

Two details:

1. **`http.ErrAbortHandler`** is a special panic value the standard library uses to say "stop this response on purpose". We let it carry on.
2. **`Connection: close`** tells the client not to reuse this connection. After a panic, we can't be sure the response was left in a clean state.

You might hear that `net/http` already recovers panics. It does, sort of: the server catches a panic in a handler, logs it, and **closes the connection**. The customer gets no response at all, just a dropped connection, and the log line isn't in your format. Our middleware turns that into a proper 500 they can see and you can search for.

But it only works if it's outside the panicking handler and the response hasn't started. If a handler already wrote half its body, then panicked, the 200 has gone. Nothing can turn it into a 500. That's one more reason handlers should decide their status before writing anything.

## Middleware 3: kitchen staff only
<!-- bite: 5b23328a-7d6c-4d4b-9f54-3cf10105f4d8 -->

Only the kitchen may change the menu. Proper logins come in lesson 12. For now, the kitchen has a secret **staff key**, and every request that changes the menu must send it in a header, `X-Staff-Key`.

The key must not be written in the code, where anyone who sees the code sees the key. It comes from an **environment variable**, a named setting the operating system gives your program when it starts. Add to `middleware.go`:

```go
func kitchenOnly(staffKey string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			given := r.Header.Get("X-Staff-Key")
			if subtle.ConstantTimeCompare([]byte(given), []byte(staffKey)) != 1 {
				http.Error(w, "kitchen staff only", http.StatusUnauthorized)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}
```

Add `"crypto/subtle"` to the imports.

Why not just `given == staffKey`? Because `==` on strings stops at the first wrong character. A wrong guess starting with the right letter takes a tiny bit longer to fail than one starting with the wrong letter. Over thousands of tries, an attacker can measure that and find the key one character at a time. `subtle.ConstantTimeCompare` always looks at every byte, so every wrong guess takes the same time. Use it whenever you compare secrets.

This middleware stops the request when the key is wrong: it answers 401 and returns **without calling `next`**. The handler never runs. That's what it means for middleware to guard a route.

## Using middleware on some routes
<!-- bite: 7558ec01-c46a-4784-b9be-305e571d28aa -->

The logger and the panic catcher are for every request. The staff key is only for the routes that change the menu. In `registerMenuRoutes`, give it the key, and wrap just those three handlers. Change the start of the function and the three write routes:

```go
func registerMenuRoutes(mux *http.ServeMux, store *menuStore, staffKey string) {
	staff := kitchenOnly(staffKey)

	// ... the three GET routes stay exactly as they were ...

	mux.Handle("POST /menu", staff(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// ... the same body as before ...
	})))

	mux.Handle("PATCH /menu/{id}", staff(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// ... the same body as before ...
	})))

	mux.Handle("DELETE /menu/{id}", staff(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// ... the same body as before ...
	})))
}
```

Notice it's now `mux.Handle`, not `mux.HandleFunc`. `HandleFunc` takes a plain function. `Handle` takes an `http.Handler`, and `staff(...)` returns one. To give `staff` a handler, we turn our function into one with `http.HandlerFunc(...)`.

That's a lot of brackets, and with twenty protected routes it gets old fast. The standard mux has no **route groups** ("these ten routes share this middleware"). It's the main thing [[backend/frameworks/chi/index|Chi]] adds. With the standard library, wrapping each route like this is the honest answer, and lesson 4 makes it tidier by giving each handler a name.

## Using middleware on every route
<!-- bite: 4c1dcfa6-f464-4186-beed-3b6ab3b4781a -->

Now wrap the whole mux in `main`. Change `main` to:

```go
func main() {
	logger := slog.New(slog.NewTextHandler(os.Stdout, nil))

	staffKey := os.Getenv("STAFF_KEY")
	if staffKey == "" {
		logger.Error("STAFF_KEY is not set")
		os.Exit(1)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Mama Put is open!\n"))
	})

	store := newMenuStore()
	registerMenuRoutes(mux, store, staffKey)

	handler := chain(mux, logRequests(logger), recoverPanic(logger))

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           handler,
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

Add `"log/slog"` and `"os"` to `main.go`'s imports, and remove `"log"`, which isn't used any more (Go will refuse to compile until you do).

The app refuses to start without a staff key. That's on purpose. An app that starts with an empty key would let anyone in who sends an empty header. Failing loudly at start-up is much better than running quietly broken.

`chain` is a small helper that saves writing `logRequests(logger)(recoverPanic(logger)(mux))`, which is hard to read. Add it to `middleware.go`:

```go
func chain(h http.Handler, middleware ...func(http.Handler) http.Handler) http.Handler {
	for i := len(middleware) - 1; i >= 0; i-- {
		h = middleware[i](h)
	}
	return h
}
```

It wraps from the **last** one in the list to the first, so the first one in the list ends up outermost, and runs first. `chain(mux, logRequests, recoverPanic)` reads in the order a request meets them.

Run it, giving it a key:

```bash
STAFF_KEY=mama-secret go run -race .
```

In another terminal:

```bash
curl http://localhost:8080/menu
curl -i -X DELETE http://localhost:8080/menu/2
# HTTP/1.1 401 Unauthorized
curl -i -X DELETE http://localhost:8080/menu/2 -H "X-Staff-Key: mama-secret"
# HTTP/1.1 204 No Content
```

And look at the server's terminal:

```text
time=... level=INFO msg=request method=GET path=/menu status=200 duration=94.3µs
time=... level=INFO msg=request method=DELETE path=/menu/2 status=401 duration=21.5µs
time=... level=INFO msg=request method=DELETE path=/menu/2 status=204 duration=30.1µs
```

Every request, with its real status, including the 401 that the handler never even saw.

## Order is behaviour
<!-- bite: 4c4f4ed5-d9d8-4293-a4d6-80b760b317ad -->

The order in `chain` isn't a style choice. Each middleware only sees what happens **inside** it.

With `chain(mux, logRequests(logger), recoverPanic(logger))`, a request goes: logger in, panic catcher in, mux, handler, then back out through the panic catcher and the logger. If the handler panics, the panic catcher writes a 500 through the recorder, and the logger logs `status=500`. 

Swap them, `chain(mux, recoverPanic(logger), logRequests(logger))`, and a panic now flies straight out through the logger before anything catches it. The logger's "after" code never runs, so **the one request you most needed to see isn't logged**.

Try it. Add a route that panics on purpose:

```go
mux.HandleFunc("GET /boom", func(w http.ResponseWriter, r *http.Request) {
	var dishes []Dish
	writeJSON(w, http.StatusOK, dishes[5]) // the slice is empty, so this panics
})
```

Request `/boom` with the right order, then with them swapped, and compare the logs. Then delete the route.

A few rules that hold in almost every app:

1. **The logger goes outermost**, so it sees everything, including the 401s, the 404s and the 500s from other middleware.
2. **The panic catcher goes just inside it**, so it protects all the rest.
3. **Checks that can stop a request (staff key, later the login) go close to the handlers they guard**, so they don't block routes that don't need them.

## The Go in this lesson
<!-- bite: e0cd273a-9f6e-4cba-9cad-9c3a53df6760 -->

1. **Two files, one package.** `middleware.go` also starts with `package main`. All files in a folder with the same package share everything: `main.go` calls `chain` without importing anything. Each file still lists its own imports.
2. **`func logRequests(logger *slog.Logger) func(http.Handler) http.Handler`**: A function that returns a function. Read the return type from the left: "a func that takes a Handler and returns a Handler". The inner functions can use `logger`, because a function remembers the variables around it where it was made. That's called a **closure**.
3. **`type statusRecorder struct { http.ResponseWriter; status int }`**: The first field has a type and no name, so it's **embedded**. Its methods are **promoted**: `rec.Header()` works and calls the real writer's `Header`. That means `statusRecorder` satisfies `http.ResponseWriter` without writing those methods.
4. **`rec.ResponseWriter.WriteHeader(code)`**: An embedded field is still reachable by its type name. Here we call the real one after noting the code. This is how you **override** one method and keep the rest.
5. **`&statusRecorder{ResponseWriter: w, status: http.StatusOK}`**: Builds the struct with named fields and takes its address. We pass `rec` (a pointer) down the chain, because its methods have pointer receivers.
6. **`time.Now()` and `time.Since(start)`**: The current time, and how long since then, as a `time.Duration`, which prints nicely, like `94.3µs`.
7. **`defer func() { ... }()`**: Defers a call to a function written in place. The `()` at the end matters: you're deferring a *call*, so the function must be called.
8. **`recover()`**: Returns what `panic` was called with, or `nil` if there's no panic. It only works directly inside a deferred function.
9. **`string(debug.Stack())`**: `debug.Stack()` returns the stack trace as bytes; `string(...)` converts them to text.
10. **`subtle.ConstantTimeCompare(a, b) != 1`**: It returns 1 when the two byte slices are equal, 0 when they're not. It's in `crypto/subtle`, Go's home for these careful helpers.
11. **`os.Getenv("STAFF_KEY")`**: Reads an environment variable, or `""` if it's not set. **`os.Exit(1)`** stops the program at once with exit code 1, which means "failed". Deferred functions don't run when you `os.Exit`.
12. **`middleware ...func(http.Handler) http.Handler`**: The `...` makes a **variadic** parameter: the caller can pass any number of these, and inside the function they arrive as a slice.
13. **`for i := len(middleware) - 1; i >= 0; i-- { ... }`**: Go's classic three-part `for` loop, here counting down. `len` gives the length of a slice.
14. **`STAFF_KEY=mama-secret go run .`**: Not Go, but the shell. Writing `NAME=value` before a command sets that environment variable for that one command.

## Your project so far
<!-- bite: b4c5ebfd-ef13-4470-bc77-a820a2b10180 -->

```text
mama-put/
├── .gitignore
├── go.mod
├── main.go         ← main: logger, STAFF_KEY, mux, chain, server; menu types, menuStore,
│                      registerMenuRoutes (writes wrapped in kitchenOnly), writeJSON
└── middleware.go   ← NEW: statusRecorder, logRequests, recoverPanic, kitchenOnly, chain
```

1. **`main.go`**: `main` now builds a `slog` logger, refuses to start without `STAFF_KEY`, registers the routes and wraps the mux in `chain(mux, logRequests(logger), recoverPanic(logger))`. The three menu routes that change things are wrapped in `kitchenOnly`.
2. **`middleware.go`**: everything that runs around handlers. `statusRecorder` (with `Unwrap`), the three middleware, and `chain`.

## Common mistakes
<!-- bite: a576b5a8-c020-4a6d-9083-493d822c30cb -->

1. **Forgetting to call `next.ServeHTTP`.** The request stops in the middleware and the client gets an empty 200. Every path through a middleware either calls `next` or writes a response.
2. **Calling `next` after writing an error.** The `return` after `http.Error` is what stops the request. Without it, the handler runs anyway, and the guard guards nothing.
3. **A wrapper without `Unwrap`.** Flushing and other extras silently stop working behind it. Every `ResponseWriter` wrapper gets an `Unwrap` method.
4. **The logger inside the panic catcher.** Panicking requests vanish from the logs. Logger outermost.
5. **Comparing secrets with `==`.** Use `subtle.ConstantTimeCompare`.
6. **A default secret in the code.** `if staffKey == "" { staffKey = "changeme" }` ships to production one day. Refuse to start instead.
7. **Sending the panic message to the client.** Details go to the log; the client gets a plain 500.

## Check your understanding
<!-- bite: 64344510-c7e9-4d3a-8828-2d803a33f31e -->

1. In your own words, what does a middleware get, and what does it give back?
2. Why can't the logger just ask `w` what status was sent? How does it find out instead?
3. A request comes for `DELETE /menu/1` with the wrong key. List, in order, what runs and what doesn't: the logger, the panic catcher, `kitchenOnly`, the delete handler.
4. What does `chain(mux, a, b, c)` build, written out by hand?

<details>
<summary>Answers, after your attempt</summary>

1. It gets the next handler, and gives back a new handler that does something extra before and/or after calling that next handler, or answers by itself without calling it.
2. Because `http.ResponseWriter` has no method for reading the status back; it only sends. The logger passes the handler a `statusRecorder` that wraps the real writer and remembers the code whenever `WriteHeader` is called.
3. The logger starts (notes the time, wraps `w`), the panic catcher sets up its deferred function, the mux finds `DELETE /menu/{id}`, which is `kitchenOnly` wrapping the handler. `kitchenOnly` sees the wrong key, answers 401 and returns. The delete handler never runs. Then the panic catcher's deferred function runs and finds no panic, and the logger logs `status=401`.
4. `a(b(c(mux)))`. `a` is outermost, so it runs first on the way in and last on the way out.

</details>

## Practice
<!-- bite: bf60d647-296e-4580-9376-f81afe9068d4 -->

1. Write a middleware `onlyJSON` that answers **415 Unsupported Media Type** if a `POST` or `PATCH` request doesn't have the header `Content-Type: application/json`, and otherwise passes the request on. Add it to the chain for every route.
2. Protect `PATCH /orders/{id}/status` with `kitchenOnly`, so only the kitchen can mark an order ready. Customers can still place orders without a key.
3. Make `logRequests` also log the client's address (`r.RemoteAddr`) and the size of the response in bytes. Hint: the recorder needs a `Write` method too, which adds `len(b)` to a counter before passing `b` on.

**Done when** a `POST /menu` with the right key but no content type gets a 415, a customer can place an order but not mark it ready, and every log line shows the address and the byte count.

## Before moving on
<!-- bite: 69e24587-efa2-4db7-bdde-8a098bdbbfc8 -->

You can write middleware, use it on every route or just some, and you know why the order matters: each one only sees what happens inside it.

Now look at `main.go`. It's getting long: types, a store, routes, helpers and `main`, all in one file. Adding orders made it worse, and lesson 8 will add a database. Before it becomes a mess, we need to give each part of the app its own place: packages for the menu and orders, and a clear line between the code that speaks HTTP and the code that knows Mama's rules. That's the next lesson.

## Related
<!-- bite: ed6b0ef3-8c29-459b-886f-0ae39129877d -->

- [[backend/frameworks/net-http/04-structuring-a-go-service|Next: Structuring a Go Service]]
- [[backend/01-foundations/03-the-request-lifecycle/index|The Request Lifecycle]] — where middleware sits in the journey of a request
- [[concepts/02-design-patterns/02-structural-patterns/index|Structural Patterns]] — middleware is the decorator pattern
- [[backend/frameworks/express/03-middleware|The same lesson in Express]] — `(req, res, next)` instead of wrapping

## About this lesson
<!-- bite: d7ab3c85-ce04-400c-801d-420bb5fb1771 -->

**Level:** Beginner to Intermediate. Lesson 3 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later. Rewritten in November 2026 from an older reference note, "Middleware as Composition".
