---
id: ad8352f8-41e8-4c57-ba33-72df1d4d30fc
---

# What net/http Is, and Your First Server

**`net/http` is the package that comes with Go for answering web requests: you say "when someone asks for this address, run this function", and Go does the rest.** You don't install anything. It is already there when you install Go, and it is good enough that many companies run it in production with no framework on top.

## Before you start
<!-- bite: 90940845-c033-474c-9e6b-7d07fe13df8b -->

You should be able to:

1. Install Go and run a small program with `go run main.go`. If you can't yet, do [[languages/02-go/01-why-go-and-the-toolchain|Why Go, and the Toolchain]] first.
2. Explain what a request and a response are, in a sentence. If you can't yet, read [[backend/01-foundations/01-what-a-backend-is|What a Backend Is]] first.

After this lesson you will be able to:

1. Create a Go project from an empty folder and start a server.
2. Say what happens, step by step, when a request reaches your server.
3. Send back text, JSON and a status code, in the right order.
4. Explain why `http.ListenAndServe` must never go to production as it is.

## The app we will build in this subject
<!-- bite: 9a14d770-5bf9-4522-9671-3c6d1784c400 -->

Every lesson in this subject adds to one app, so you never start from zero again.

Imagine a **Mama Put**: the woman by the roadside with the big pots, selling jollof, beans, plantain and stew. Her customers are now ordering on their phones, so she needs a backend. That backend is what we will build, and we will call it **Mama Put API**.

By the last lesson it will:

1. Show the menu, and let the kitchen add, change and remove dishes.
2. Let customers sign up, log in, place orders and pay for them with Paystack.
3. Let only kitchen staff mark an order as "ready", and show new orders live on a kitchen screen.
4. Store everything in PostgreSQL, and keep the busy parts fast with Redis.
5. Offer the same data over GraphQL, and as an MCP server so AI assistants can order for a customer.
6. Send receipts and "your food is ready" messages from a **second, separate service**, so you learn how microservices talk to each other.
7. Check every request, handle every error, have tests, logs and metrics, and run on a real server, deployed automatically when you push.

That's a real production backend, the kind a small company would actually run. We get there one lesson at a time, using as little outside code as Go allows.

Today we just get the pot on the fire: a server that starts and answers its first request.

## The kid version
<!-- bite: 72630901-8b6f-4691-bdee-6063d0c15be4 -->

Think of Mama Put's stand. A customer walks up and says "one plate of jollof". Mama listens, picks the right pot, dishes the food and hands it over.

A Go server is Mama for the internet. A request comes in ("give me the menu"). `net/http` looks at what was asked for, picks the function you wrote for that request, and that function hands back a response (the menu).

**Where the picture stops working.** Mama serves one customer at a time with her own hands. Go gives every request its own **goroutine**, a very cheap worker, so a thousand customers can be served at once. That is a gift, and it is also the first thing that can bite you, because a thousand workers can reach for the same pot at the same time. We meet that in the next lesson.

## Why Go needs no framework to start
<!-- bite: e71268cc-9454-4c0d-98ff-015c310e18ca -->

In most languages the built-in web server is a toy, and everyone reaches for a framework on day one. Go is different. It was made at Google for writing network servers, and its standard library (the packages that come with the language) has a production-grade HTTP server in it.

Since Go 1.22, the built-in router also understands methods and IDs in the path (`GET /menu/{id}`). That was the last big reason people took a framework. So in this subject we build the whole production system on `net/http` itself, and only take small, focused packages where the standard library really has nothing (a Postgres driver, a JWT library, Redis).

The [[backend/frameworks/chi/index|Chi]] and [[backend/frameworks/gin/index|Gin]] subjects build the same app with a framework on top. Because Chi uses the exact types you learn here, everything in this subject carries over to it.

## Terms used in this lesson
<!-- bite: 000b33ef-de42-4697-b30c-b8e9b3ff2fc7 -->

1. **Request**: This is the message a client (a phone app, a browser, another server) sends to your backend. It says what it wants (the **method**, like GET or POST), where (the **path**, like `/menu`), and sometimes carries extra data (the **body**).
2. **Response**: This is the message your backend sends back. It has a **status code** (a number saying how it went, like 200 for "fine" or 404 for "not found"), some **headers** (labels about the response, like "this is JSON"), and usually a body.
3. **Handler**: This is anything that can answer a request. In Go it is a very small idea: any value with a method `ServeHTTP(w, r)`. A plain function with the right shape can be one too.
4. **Mux**: This is short for **multiplexer**, Go's name for a router. It holds a list of patterns like `GET /menu`, and for each request it picks the handler whose pattern matches.
5. **Port**: This is a number that tells the computer which program a network message is for. Your server "listens" on a port, like 8080, so messages sent to that port reach it.
6. **Goroutine**: This is a function running on its own, alongside others, managed by Go. Starting one costs a few kilobytes, so Go happily starts one per request.

## Setting up the project
<!-- bite: fc71b654-a096-49a7-b357-542f1ba16579 -->

Check that Go is installed, and its version:

```bash
go version   # needs go1.24 or later
```

Now make the project:

```bash
mkdir mama-put
cd mama-put
go mod init mamaput
```

`go mod init` creates `go.mod`, the file that says "this folder is a Go **module** called `mamaput`". A module is Go's word for a project: one folder of code that is built and versioned together. Everything we write will live inside this one module, even the second service later on.

Open `go.mod` and you'll see two lines, something like:

```text
module mamaput

go 1.24.0
```

The second line is the oldest Go version the project needs. Yours may show a newer number; that's fine.

That's all the setup. No package manager to install, no config file for the compiler. `net/http` comes with Go, so there's nothing to download yet.

## Your first server
<!-- bite: de381796-7b7e-4812-a7c0-d8d66f4de3a4 -->

Create `main.go`:

```go
package main

import (
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Mama Put is open!\n"))
	})

	log.Println("Mama Put API listening on http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", mux))
}
```

Run it:

```bash
go run .
```

You should see `Mama Put API listening on http://localhost:8080`. Now, in a second terminal:

```bash
curl http://localhost:8080/
# Mama Put is open!

curl -i http://localhost:8080/suya
# HTTP/1.1 404 Not Found
# ...
# 404 page not found
```

Before you run that last one, predict: what will Go send back for a path you never wrote? Then run it. The `-i` flag shows the status line and headers too.

Okay!!!!! The pot is on the fire.

Two things in that pattern need a word now. `GET` means this handler only answers GET requests. `/{$}` means "exactly `/` and nothing after it". Without the `{$}`, a pattern ending in `/` matches **everything below it**, so `GET /` would answer `/suya` too, with "Mama Put is open!". That surprises everyone once. Lesson 2 covers patterns properly.

## The whole of net/http is one small interface
<!-- bite: a1528d68-b231-42a8-9615-3180b2de3069 -->

Here is the idea that makes Go's web world different from every other language's. A handler is defined like this, in the standard library:

```go
type Handler interface {
	ServeHTTP(w http.ResponseWriter, r *http.Request)
}
```

Anything with a `ServeHTTP` method of that shape is a handler. That's all. The mux is a handler too: it has a `ServeHTTP` that looks at the path and calls the right handler inside it. That's why you could pass `mux` to `ListenAndServe`, which asks for a `Handler`.

Writing a whole type just to have one method is tiresome, so Go also gives you `http.HandlerFunc`:

```go
type HandlerFunc func(w http.ResponseWriter, r *http.Request)

func (f HandlerFunc) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	f(w, r)
}
```

It turns a plain function into a `Handler`: its `ServeHTTP` just calls the function. `mux.HandleFunc` uses it for you.

Why does this matter so much? Because every router, every framework and every piece of middleware in Go speaks this one interface. A Chi router is a `Handler`. Your own function is a `Handler`. A package someone wrote ten years ago for logging is a function that takes a `Handler` and returns a `Handler`. They all fit together with no glue. In Express or Spring, a piece of middleware usually works only in that framework. In Go, it works everywhere.

## What just happened, step by step
<!-- bite: 92f1f3db-ecd7-4299-ba25-b5e231f7aff9 -->

Let's follow one request, `GET /`, from your terminal to the answer. This picture is the one to keep in your head for the whole subject.

1. **`curl` opens a connection** to port 8080 and sends: method GET, path `/`.
2. **The server accepts the connection** and starts a goroutine for it. From now on, this request has its own worker.
3. **The server reads the request** and builds two things: `r`, a `*http.Request` describing it, and `w`, an `http.ResponseWriter` you use to answer.
4. **It calls `mux.ServeHTTP(w, r)`.** The mux looks at the method and the path, and finds the pattern `GET /{$}`.
5. **The mux calls your function** with the same `w` and `r`.
6. **Your function writes to `w`.** The first write sends the status line (200, since you didn't choose one), the headers, then your text.
7. **Your function returns, and the request is finished.** The connection stays open for the next request from the same client, which is called **keep-alive**.

If no pattern matches, the mux has its own answer: 404 "page not found". If the path matches but the method doesn't, it answers **405 Method Not Allowed** and an `Allow` header listing the methods that would work. Try `curl -i -X POST http://localhost:8080/`.

## Sending things back
<!-- bite: 3633b5f8-54ad-4210-a7ae-2b17d33960d8 -->

`w` is not a response object you fill in and hand back. It is a pipe straight to the client, and things go down it in a fixed order: **status line, then headers, then body**. Once something has gone down the pipe, it can't be taken back.

So in Go you always do three steps, in this order:

```go
w.Header().Set("Content-Type", "application/json") // 1. headers
w.WriteHeader(http.StatusCreated)                  // 2. status (201)
w.Write([]byte(`{"id":"3"}`))                      // 3. body
```

Get the order wrong and Go won't stop you. It just quietly does something else:

1. **Writing the body first** sends a 200 status straight away. A `WriteHeader(404)` after that is ignored, and Go prints `http: superfluous response.WriteHeader call` in your log.
2. **Setting a header after the first write** does nothing. The headers have already gone.
3. **Not writing anything at all** sends an empty 200. Go never leaves a client hanging when your function returns, but an empty 200 is still wrong if something failed.

For JSON, the `encoding/json` package can write straight into `w`. Let's give Mama a menu. Add this to `main.go`:

```go
type Dish struct {
	ID         string `json:"id"`
	Name       string `json:"name"`
	PriceNaira int    `json:"priceNaira"`
}

var dishes = []Dish{
	{ID: "1", Name: "Jollof rice", PriceNaira: 1500},
	{ID: "2", Name: "Beans and plantain", PriceNaira: 1200},
}
```

And this route, inside `main`, under the first one:

```go
mux.HandleFunc("GET /menu", func(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(dishes)
})
```

Add `"encoding/json"` to the imports at the top. Stop the server with Ctrl+C, run `go run .` again, then:

```bash
curl http://localhost:8080/menu
# [{"id":"1","name":"Jollof rice","priceNaira":1500},{"id":"2","name":"Beans and plantain","priceNaira":1200}]
```

The `json:"priceNaira"` part after each field is a **struct tag**. It tells `encoding/json` what to call the field in JSON. Without it, the JSON would say `"PriceNaira"`, with a capital P, which is not what JavaScript clients expect.

Go doesn't restart by itself when you save. Stop and run again after each change. If that gets tiring, the tool `air` watches your files and restarts for you, but you don't need it.

## The line you must never ship
<!-- bite: 930c0235-3b3a-4cf8-9c92-926bba389f61 -->

Look at this line again:

```go
log.Fatal(http.ListenAndServe(":8080", mux))
```

It works, and every tutorial uses it. But that server has **no timeouts at all**. A client can open a connection and send one byte a minute, forever, and your server will patiently wait, holding a goroutine and an open connection the whole time. Open ten thousand of those and the server runs out of connections and stops serving real customers. That attack is called **slowloris**, and it needs no skill at all.

The fix is to build the server yourself, with limits. Replace the last two lines of `main` with:

```go
srv := &http.Server{
	Addr:              ":8080",
	Handler:           mux,
	ReadHeaderTimeout: 5 * time.Second,
	ReadTimeout:       10 * time.Second,
	WriteTimeout:      30 * time.Second,
	IdleTimeout:       120 * time.Second,
}

log.Println("Mama Put API listening on http://localhost:8080")
log.Fatal(srv.ListenAndServe())
```

And add `"time"` to the imports. Here is what each limit means, in the order they happen to a request:

1. **`ReadHeaderTimeout`**: how long a client has, after connecting, to finish sending its headers. This one alone stops slowloris.
2. **`ReadTimeout`**: how long it has to send the whole request, body included.
3. **`WriteTimeout`**: how long your handler and the response together may take. It must be longer than your slowest honest handler, or slow requests get cut off halfway.
4. **`IdleTimeout`**: how long a keep-alive connection may sit doing nothing before the server closes it.

`http.ListenAndServe(":8080", mux)` is a shortcut that builds an `http.Server` with all of these set to zero, which means "no limit". So from today, Mama Put API never uses the shortcut. Lesson 14 tightens these further, and lesson 28 adds a clean shutdown.

## The Go in this lesson
<!-- bite: c320cd39-b873-4218-b182-a3ebe617bd9e -->

If you haven't written much Go, here is everything this lesson used, in the order it appeared.

1. **`package main`**: Every Go file starts by saying which **package** it belongs to. A package is a folder of code that's compiled together. `main` is special: it means "this builds into a program you can run", and Go starts it from the function called `main`.
2. **`import ( "log" "net/http" )`**: This brings in other packages. `net/http` is a path; you then use its last part, `http`, as the name (`http.NewServeMux`). Go refuses to compile if you import something you don't use, which keeps files tidy.
3. **`func main() { ... }`**: This declares a function. `main` takes nothing and returns nothing.
4. **`mux := http.NewServeMux()`**: `:=` declares a new variable and gives it a value in one go. Go works out the type from the value, here a `*http.ServeMux`. You can only use `:=` inside functions.
5. **`func(w http.ResponseWriter, r *http.Request) { ... }`**: This is a function with no name, written right where it's used. Each parameter has its name first and its type second, which is backwards from most languages.
6. **`*http.Request`**: The `*` means **pointer**: `r` doesn't hold the request itself, it holds the address of it. The server builds one request and hands your function its address, so nothing gets copied. You use a pointer exactly like the value (`r.Method`), Go follows the address for you.
7. **`[]byte("Mama Put is open!\n")`**: `[]byte` is a **slice** (a list) of bytes. `w.Write` takes raw bytes, not text, so we convert the string. `` `{"id":"3"}` `` with backticks is a **raw string**: no escaping needed inside, which is handy for JSON.
8. **`type Handler interface { ServeHTTP(...) }`**: An **interface** is a list of methods. Any type that has those methods satisfies it automatically. You never write "implements Handler"; having the method is enough.
9. **`type HandlerFunc func(...)` and `func (f HandlerFunc) ServeHTTP(...)`**: The first line makes a new type that *is* a function type. The second gives that type a **method**. The `(f HandlerFunc)` before the name is the **receiver**: the value the method is called on, like `this` in other languages, but named and explicit.
10. **`type Dish struct { ... }`**: A **struct** is a group of named fields. A field whose name starts with a **capital letter** is **exported**, meaning other packages (like `encoding/json`) can see it. A lower-case field is invisible to them, so `encoding/json` would silently leave it out. This is the most common first Go mistake with JSON.
11. **`` `json:"priceNaira"` ``**: A **struct tag**, a little label packages can read. `encoding/json` reads the `json` one to choose the JSON name.
12. **`var dishes = []Dish{ {...}, {...} }`**: `var` declares a variable; outside functions you must use `var`, not `:=`. `[]Dish{...}` is a slice of dishes written out in place.
13. **`json.NewEncoder(w).Encode(dishes)`**: This makes a JSON encoder that writes into `w`, and encodes the slice straight down the pipe. It works because `w` has a `Write` method, and the encoder only needs something it can write to.
14. **`&http.Server{ Addr: ":8080", ... }`**: This builds a struct with named fields. Fields you don't name get their **zero value**: 0 for numbers, `""` for strings, `nil` for pointers. That's exactly why the shortcut has no timeouts: zero means none. The `&` gives you a pointer to the new struct.
15. **`5 * time.Second`**: `time.Second` is a `time.Duration`, a number of nanoseconds with its own type. Multiplying gives five seconds. The type stops you passing a plain `5` and getting five nanoseconds by accident.
16. **`log.Fatal(srv.ListenAndServe())`**: `ListenAndServe` only returns if it fails (port in use, for example), and it returns an **error**. `log.Fatal` prints it and stops the program. Go has no exceptions: functions that can fail return an error value, and you deal with it. Lesson 7 is all about this.

## Your project so far
<!-- bite: 5c3b6dd7-c696-4fc3-8b43-5f42a19b03d7 -->

```text
mama-put/
├── go.mod      ← the module name (mamaput) and the Go version
└── main.go     ← the Dish type, the dishes slice, two routes, and a server with timeouts
```

1. **`go.mod`**: says this folder is the Go module `mamaput`, and which Go version it needs. Later it will also list the outside packages we use.
2. **`main.go`**: in package `main`. Defines `Dish` and the in-memory `dishes`, registers `GET /{$}` and `GET /menu` on a mux, and starts an `http.Server` with all four timeouts on port 8080.

Also run `git init` and add a `.gitignore` with one line, `/mama-put`, the program file `go build` makes, so it never goes into git.

## Common mistakes
<!-- bite: 1df3aa2d-a981-4b9b-95a3-5e9e93256e64 -->

1. **Using `http.ListenAndServe` in production.** No timeouts. Always build an `http.Server`.
2. **Lower-case struct fields.** `name string` is invisible to `encoding/json`, so the field is silently missing from the JSON. Capitalise it and add a tag.
3. **Writing before setting headers or status.** The first `Write` sends a 200 and the headers. Anything set after that is ignored.
4. **`GET /` when you meant only the home page.** A pattern ending in `/` matches everything under it. Use `GET /{$}`.
5. **Forgetting to restart.** `go run` builds once. After a change, stop it and run it again.
6. **Port already in use.** `bind: address already in use` means another program (often your server from an earlier run) is on 8080. Stop it, or use another port.

## Check your understanding
<!-- bite: c6473811-5781-4c08-9224-2acf940a9c7b -->

1. In your own words, what is a handler in Go, and why can a mux be passed where a handler is expected?
2. What does this handler send, and what does the log say?

   ```go
   mux.HandleFunc("GET /menu", func(w http.ResponseWriter, r *http.Request) {
   	json.NewEncoder(w).Encode(dishes)
   	w.WriteHeader(http.StatusCreated)
   })
   ```

3. A request for `POST /menu` arrives, and you only wrote `GET /menu`. What does the client get back?
4. Why is `http.ListenAndServe(":8080", mux)` dangerous, when it works perfectly on your laptop?

<details>
<summary>Answers, after your attempt</summary>

1. A handler is any value with the method `ServeHTTP(w http.ResponseWriter, r *http.Request)`. The mux has that method too: it picks the matching handler and calls it. So it satisfies the `Handler` interface, and anything that wants a handler accepts it.
2. It sends status 200 with the menu as JSON. The `Encode` call wrote the body first, which sent a 200 automatically. The later `WriteHeader(201)` is ignored, and the log shows `http: superfluous response.WriteHeader call`. (It also has no `Content-Type: application/json` header, so some clients won't treat it as JSON.)
3. A 405 Method Not Allowed, with the header `Allow: GET, HEAD`. The path matched, the method didn't, and since Go 1.22 the mux says so instead of pretending the page doesn't exist.
4. It has no timeouts. On your laptop every client is polite. On the internet, someone will open thousands of connections and send them slowly, and your server will wait on every one of them until it can't accept real customers.

</details>

## Practice
<!-- bite: a62aa2e3-832b-4305-bbae-142110abff7c -->

Add two routes to Mama Put API:

1. `GET /hours` returns the JSON `{ "opens": "07:00", "closes": "21:00" }`, with the right `Content-Type`. Use a struct with tags, not a hand-written string.
2. `GET /health` returns status 200 with the text `ok`. Real servers have a route like this so other programs can check the app is alive. We'll make it proper in the production lesson.

**Done when** `curl -i` against both shows status 200 with the right body and headers, `curl -i http://localhost:8080/hourz` still shows a 404, and `curl -i -X DELETE http://localhost:8080/hours` shows a 405.

## Before moving on
<!-- bite: 34b96c0e-3e19-4ce8-8d66-fff952623198 -->

You can start a Go server with proper timeouts, and you know the path a request takes: a goroutine of its own, a mux that matches the method and path, a handler that writes the status, then the headers, then the body.

Right now our menu is written straight into the code, and there's only one way to ask for it. A real menu needs to fetch one dish by its ID, add new dishes and remove old ones. That means different methods, IDs inside the path, reading JSON from the body, and, because every request has its own goroutine, keeping two customers from changing the menu at the same moment. That's the next lesson.

## Related
<!-- bite: 66793129-4407-4b0e-89cc-272bb14e41be -->

- [[backend/frameworks/net-http/02-routing|Next: Routing]]
- [[backend/01-foundations/02-http-servers|HTTP Servers]] — what's underneath every framework
- [[languages/02-go/06-goroutines-and-channels|Goroutines and Channels]] — the workers that serve each request
- [[backend/frameworks/express/01-what-express-is-and-a-first-app|The same lesson in Express]] — compare how much Go gives you built in

## About this lesson
<!-- bite: e1990d5f-9e7d-474e-9618-f47f5261eb04 -->

**Level:** Beginner. Lesson 1 of the [[backend/frameworks/net-http/index|net/http]] subject, which teaches the whole backend course by building one app, Mama Put API, in Go. Written for Go 1.24 or later. Rewritten in November 2026 from an older reference note, "`net/http` in Depth".
