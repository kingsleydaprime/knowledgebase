---
id: 6b935046-9999-4feb-9aec-ebf806102c11
---

# What Axum Is, and Your First Server

**Axum is a library for building web servers in Rust: you say "when someone asks for this address, run this function", and Axum turns each request into a call to your function and its return value into a response.** It's small on purpose. It sits on top of three other Rust libraries that each do one job, and it adds the part that's missing: routing requests to your functions, in a way the compiler can check.

## Before you start
<!-- bite: 6984b729-8f7f-4a01-ba5d-7db50bb44b00 -->

You should be able to:

1. Install Rust and run a small program with `cargo run`. If you can't yet, do [[languages/03-rust/01-why-rust-and-the-toolchain|Why Rust, and the Toolchain]] first.
2. Read `async fn` and `.await`, and say what an async runtime is for. If you can't yet, read [[languages/03-rust/14-async-and-tokio|Async and Tokio]] first. You don't need all of it; the first half is enough for now.
3. Explain what a request and a response are, in a sentence. If you can't yet, read [[backend/01-foundations/01-what-a-backend-is|What a Backend Is]] first.

After this lesson you will be able to:

1. Create an Axum project from an empty folder and start a server.
2. Name the four layers under every Axum app (Tokio, hyper, Tower, Axum) and what each one does.
3. Send back text, JSON and a status code from a handler.
4. Stop the server cleanly, and explain why `axum::serve` must not face the internet on its own.

## What to install
<!-- bite: ab1008c9-8fd8-48bd-80dd-5b8ffc5005ef -->

1. **Rust**, with **rustup**, from [rustup.rs](https://rustup.rs). It installs `rustc` (the compiler), `cargo` (the build tool and package manager) and keeps them updated. Check with:

   ```bash
   cargo --version
   ```

   This subject is written for Rust 1.85 or later (the 2024 edition). If yours is older, `rustup update`.
2. **rust-analyzer** in your editor. In VS Code it's the "rust-analyzer" extension. It shows types as you type, which matters more in Rust than anywhere else: half of learning Axum is seeing what type something is.
3. **curl**, to send requests from the terminal. It comes with macOS, Linux and Windows 10 or later.

The libraries themselves come with `cargo add`, in step 1.

## The app we will build in this subject
<!-- bite: 52593fb7-e658-46fb-a013-c87ee16c9f37 -->

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

It's the same app the [[backend/frameworks/net-http/index|net/http]] and [[backend/frameworks/express/index|Express]] subjects build, so you can put any lesson next to its twin and see what Rust changes. Today we just get the pot on the fire: a server that starts and answers its first request.

## The kid version
<!-- bite: 69463f39-0ec5-4be2-b07b-375285d444b5 -->

Think of Mama Put's stand. A customer walks up and says "one plate of jollof". Mama listens, picks the right pot, dishes the food and hands it over.

An Axum server is Mama for the internet. A request comes in ("give me the menu"). Axum looks at what was asked for, picks the function you wrote for that request, and hands back whatever the function returns, as a response.

**Where the picture stops working.** Mama serves one customer at a time. Our server serves thousands at once, while each one is waiting for the database or the network. In most languages that's where the hardest bugs come from: two customers reaching for the same pot at the same moment. In Rust, the compiler refuses to build a program where that can happen. You'll see it refuse in lesson 2, and it will be annoying, and it will be right.

## Terms used in this lesson
<!-- bite: eebbd75c-e553-4c83-83fc-b38b1dc868f7 -->

1. **Crate**: This is Rust's word for a package: a library or a program. Axum is a crate; so is your app.
2. **Cargo**: This is Rust's build tool. It downloads crates, compiles, runs and tests. `Cargo.toml` is its settings file.
3. **Async runtime**: This is the part of a program that runs many async tasks on a few threads, switching to another task whenever one is waiting. Rust doesn't come with one; **Tokio** is the one almost everyone uses.
4. **Handler**: This is the async function that answers one kind of request, like `GET /menu`.
5. **Router**: This is the table from "method and path" to handler. In Axum it's the `Router` type.
6. **Extractor**: This is a handler argument that Axum fills in from the request, like the path's ID or the JSON body. Lesson 2 is about them.
7. **`IntoResponse`**: This is the trait for "anything that can become a response". A handler can return any type that has it.
8. **Graceful shutdown**: This means stopping the server without cutting off requests that are halfway through.

## Step 1: a new project
<!-- bite: e2fe0ace-0e91-4f82-b0d0-b3dce3b8bfa3 -->

```bash
cargo new mama-put
cd mama-put
cargo add axum
cargo add tokio --features full
cargo add tower-http --features timeout
```

1. **`cargo new mama-put`** makes a folder with `Cargo.toml` and `src/main.rs`, and starts a git repository in it.
2. **`cargo add axum`** adds Axum to `Cargo.toml`'s `[dependencies]`, at the newest version.
3. **`cargo add tokio --features full`** adds Tokio, with all of its parts switched on (networking, timers, signals, the multi-threaded scheduler). Crates in Rust have **features**: optional parts you switch on by name, so you only compile what you use. `full` is the simple choice while learning.
4. **`cargo add tower-http --features timeout`** adds a crate of ready-made middleware. We need just its timeout today.

`Cargo.toml` now has:

```toml
[package]
name = "mama-put"
version = "0.1.0"
edition = "2024"

[dependencies]
axum = "0.8.9"
tokio = { version = "1.54.1", features = ["full"] }
tower-http = { version = "0.7.1", features = ["timeout"] }
```

`edition = "2024"` is the version of the Rust *language rules* this crate uses; it's not the compiler version. `"0.8.9"` means "0.8.9 or any later 0.8.x", because Cargo treats each `0.x` as its own series. Axum 0.8 changed some things from 0.7 (path parameters are written `{id}` now, not `:id`), so if you find an older tutorial with colons, that's why.

Cargo also wrote `Cargo.lock`, with the exact version of every crate and every crate *they* use. Commit it: it's what makes your build the same on every machine.

## Step 2: four layers, one server
<!-- bite: afaadfed-198a-4cc1-999c-8c8f50f75674 -->

Before the code, the picture, because Axum is unusual: it isn't one big framework, it's the top of a stack of separate crates, each made by people who only care about that one job.

```text
your handlers          the menu, orders, payments...
    │
  AXUM                 routing, extractors, turning return values into responses
    │
  TOWER                the Service trait: "a function from request to response"; middleware
    │
  HYPER                the HTTP protocol itself: HTTP/1.1 and HTTP/2, bytes in and out
    │
  TOKIO                the async runtime: sockets, timers, running thousands of tasks on a few threads
```

1. **Tokio** runs the program. Every request is an async task, and while one is waiting for the database, Tokio runs others on the same thread. A few threads, one per CPU core, serve thousands of requests.
2. **hyper** speaks HTTP. It reads bytes off the network and turns them into requests, and turns responses back into bytes. It's also the HTTP library under most of Rust's HTTP clients.
3. **Tower** defines one idea: a **`Service`**, something that takes a request and, later, gives back a response. Middleware is a service that wraps another service (lesson 3). Tower isn't about HTTP at all: the same middleware works for gRPC (lesson 22) and for clients calling other services (lesson 26).
4. **Axum** adds routing and **extractors**, and makes your plain async functions into Tower services.

You'll mostly write code at the top, but you'll meet each layer by name. When something about timeouts or connections goes wrong, it's usually hyper's business; when something about middleware does, it's Tower's.

## Step 3: your first server
<!-- bite: a8492898-7c3f-407e-90b9-eccac21191a6 -->

Replace `src/main.rs` with:

```rust
use std::time::Duration;

use axum::{Router, http::StatusCode, routing::get};
use tokio::net::TcpListener;
use tower_http::timeout::TimeoutLayer;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let app = Router::new()
        .route("/", get(open))
        .layer(TimeoutLayer::with_status_code(
            StatusCode::REQUEST_TIMEOUT,
            Duration::from_secs(10),
        ));

    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    println!("Mama Put API listening on http://{}", listener.local_addr()?);

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
}

async fn open() -> &'static str {
    "Mama Put is open!"
}

async fn shutdown_signal() {
    tokio::signal::ctrl_c().await.expect("can't listen for Ctrl+C");
    println!("shutting down");
}
```

Run it:

```bash
cargo run
```

The first build takes a minute or two: Cargo compiles Axum, Tokio, hyper and everything they use, once. After that, only your code is rebuilt, in seconds. When it prints `Mama Put API listening on http://127.0.0.1:8080`, open another terminal:

```bash
curl -i localhost:8080/
```

```text
HTTP/1.1 200 OK
content-type: text/plain; charset=utf-8
content-length: 17
date: Sun, 22 Nov 2026 06:35:54 GMT

Mama Put is open!
```

Okay!!!!! The pot is on the fire.

## Step 4: what just happened, line by line
<!-- bite: 86bf3dcd-eb1c-4783-96f9-dd4665b7f66d -->

1. **`#[tokio::main]`** turns `async fn main` into an ordinary `main` that starts the Tokio runtime and runs your async code on it. Rust's `main` can't be async by itself, because Rust has no runtime built in. This one line is that runtime.
2. **`-> std::io::Result<()>`**: `main` can return a `Result`. If it returns an `Err`, the program prints it and exits with a failure code. That lets us use **`?`** below.
3. **`Router::new().route("/", get(open))`**: one route. `get(open)` means "for GET requests, call `open`". `open` is just a function, passed by name, with no attribute or macro on it. Axum checks *at compile time* that it can be a handler.
4. **`.layer(TimeoutLayer::...)`**: wraps every route in middleware that gives up after 10 seconds and answers `408 Request Timeout`. A handler stuck waiting on something can't hold a connection forever. Lesson 3 is all about layers.
5. **`TcpListener::bind("127.0.0.1:8080").await?`**: opens the port. `127.0.0.1` means only programs on this computer can connect, which is right on your laptop; inside Docker (lesson 28) it becomes `0.0.0.0`, "every network interface". **`?`** means "if this failed (the port is taken, say), return the error from `main` now". `.await` because opening a socket is async in Tokio.
6. **`axum::serve(listener, app)`** accepts connections, hands each to hyper, and hyper calls our router for each request. It runs until the shutdown signal.
7. **`.with_graceful_shutdown(shutdown_signal())`**: when `shutdown_signal()` finishes (when you press Ctrl+C), stop accepting new connections, let requests already running finish, and then return. Press Ctrl+C now: it prints `shutting down` and exits.

And the handler:

```rust
async fn open() -> &'static str {
    "Mama Put is open!"
}
```

It takes nothing and returns a `&'static str`: a piece of text that's built into the program and lives forever (`'static`). Axum knows how to turn a `&'static str` into a response: status 200, `content-type: text/plain; charset=utf-8`, and the text as the body. That's **`IntoResponse`**, and it's implemented for many types.

## Step 5: sending things back
<!-- bite: caafc65a-8ac8-4d9d-bdef-c39e8b7a3f29 -->

Handlers can return anything that implements `IntoResponse`. Add a second route:

```rust
let app = Router::new()
    .route("/", get(open))
    .route("/menu", get(menu))
    // ... the layer as before
```

```rust
async fn menu() -> (StatusCode, [(&'static str, &'static str); 1], String) {
    let body = r#"[{"name":"Jollof rice","priceNaira":1500}]"#.to_string();
    (StatusCode::OK, [("content-type", "application/json")], body)
}
```

A **tuple** of parts is also a response: Axum reads it left to right. The `StatusCode` first, then headers (here an array of one name-value pair), then the body. You can leave any of them out: `(StatusCode::CREATED, body)` works, and so does just `body`.

`r#"..."#` is a **raw string**: inside it, `"` doesn't need escaping, which is handy for JSON. We're writing the JSON by hand here only to see that it's just text. Lesson 2 uses `Json<T>`, which turns a Rust struct into JSON and sets the header for you, and that's how you'll always do it.

The order of the parts can't be wrong in a way that compiles and misbehaves. In some frameworks, writing the body before setting the status silently sends 200 anyway (lesson 1 of the [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|net/http]] subject is about exactly that). In Axum, the response is a value you *return*, built all at once, so there's no "too late to set the status".

Try what you didn't write:

```bash
curl -i -X POST localhost:8080/
```

```text
HTTP/1.1 405 Method Not Allowed
allow: GET,HEAD
```

```bash
curl -i localhost:8080/nope
```

```text
HTTP/1.1 404 Not Found
```

You get **405** with an `allow` header for a path that exists with the wrong method, and **404** for a path that doesn't exist. Both for free, both correct. (And `HEAD`, the "headers only" version of `GET`, works on every `GET` route by itself.)

## Step 6: what `axum::serve` doesn't do
<!-- bite: 7ef8878d-0e13-41f6-ae8a-fe70d40f54bb -->

`axum::serve` is made to be simple, and it says so in its documentation. One thing it leaves out matters on the internet: **it never times out a slow client.**

A client can open a connection, send half a request's headers, and then wait. And wait. hyper has a setting for this (a "header read timeout", 30 seconds by default), but it only takes effect if hyper is given a timer, and `axum::serve` doesn't give it one. I tested it: a connection that sent `GET / HTTP/1.1` and one header, then nothing, was **still open after 36 seconds**, and would have stayed open for ever.

One such connection is harmless. A few thousand, from one attacker's laptop, use up the server's connections and memory, and real customers can't get in. It's called a **slowloris** attack, after the very slow animal.

`TimeoutLayer` doesn't help here: it starts timing when the request has fully arrived and reached the router, and a slowloris request never fully arrives.

So, a rule for the rest of the subject: **`axum::serve` never faces the internet directly.** In production (lesson 28), a proxy, Caddy, sits in front: it reads each request completely, with its own timeouts, before passing it on, so slow clients only ever tie up Caddy, which is built for it. And lesson 28 also shows how to serve with hyper's own settings switched on, for when there's no proxy. On your laptop, `axum::serve` is perfect.

## The Rust in this lesson
<!-- bite: 9bfb2a96-b89a-4de2-9cfc-f9c4910e6b67 -->

1. **`cargo new`, `cargo add`, `cargo run`**: make a project, add a crate to `Cargo.toml`, build and run.
2. **Crate features, `--features full`**: optional parts of a crate, switched on by name.
3. **`use axum::{Router, http::StatusCode, routing::get};`**: brings several names from a crate into scope at once, including ones from inside its modules (`http::StatusCode`).
4. **`#[tokio::main]`**: an attribute macro that wraps `async fn main` in code that starts the Tokio runtime.
5. **`async fn` and `.await`**: an async function returns a *future*, work that hasn't happened yet; `.await` waits for it without blocking the thread.
6. **`std::io::Result<()>`**: a `Result` whose error is an I/O error and whose success value is `()`, "nothing".
7. **`?`**: if the `Result` is an `Err`, return it from this function now; otherwise unwrap the value.
8. **Method chaining, `Router::new().route(...).layer(...)`**: each method takes the router and returns a new one, so calls chain.
9. **Passing a function by name, `get(open)`**: functions are values in Rust; Axum checks at compile time that `open` can be a handler.
10. **`&'static str`**: borrowed text that lives as long as the program, like a string written in the code.
11. **Tuples, `(StatusCode::OK, headers, body)`**: a fixed group of values of different types; Axum turns this one into a response.
12. **Raw strings, `r#"..."#`**: text where `"` and `\` are taken literally.
13. **`.expect("...")`**: unwraps a `Result` or `Option`, or stops the program with that message if it's an error. Fine where failing really is fatal, like being unable to listen for Ctrl+C.

## Your project so far
<!-- bite: cc1ffd6e-3814-479e-a415-4c92b823d8cf -->

```text
mama-put/
├── Cargo.toml      ← the crate's name, edition 2024, and axum, tokio, tower-http
├── Cargo.lock      ← exact versions of every crate; commit it
└── src/
    └── main.rs     ← the router (/ and /menu), a 10-second timeout, serve with graceful shutdown
```

## Common mistakes
<!-- bite: 40c475e5-d997-43bc-9c55-c92d6aa90a4b -->

1. **Forgetting `#[tokio::main]`.** The compiler says `main` can't be `async`. Rust has no runtime of its own; the attribute adds Tokio's.
2. **Using `:id` from an old tutorial.** Axum 0.8 writes path parameters as `{id}`. The old form now panics when the router is built, with a message saying so.
3. **Forgetting the `full` feature, or a feature you need.** You get "could not find `signal` in `tokio`" or similar. Add the feature.
4. **Binding to `0.0.0.0` on your laptop.** Anyone on the same Wi-Fi can reach your server. `127.0.0.1` until Docker.
5. **Putting `axum::serve` straight on the internet.** It never times out slow clients. A proxy in front, or hyper's own timeouts (lesson 28).
6. **Not committing `Cargo.lock`.** The next machine builds with different versions of your dependencies.
7. **Reading a compiler error from the bottom.** Rust's errors are long; the first line and the first `-->` location usually say what's wrong.

## Check your understanding
<!-- bite: 1785431a-4cfa-4d0f-b843-b60b48edead2 -->

1. What does each of Tokio, hyper, Tower and Axum do for your server?
2. Why does `main` need `#[tokio::main]` to be `async`?
3. What does the `?` after `TcpListener::bind(...).await` do, and why can `main` use it?
4. A handler returns `(StatusCode::CREATED, "made it")`. What status and body does the client get, and why can't you "set the status too late" in Axum?
5. What happens to a request halfway through when you press Ctrl+C, and why?
6. Why mustn't `axum::serve` face the internet on its own, and why doesn't `TimeoutLayer` fix it?

<details>
<summary>Answers, after your attempt</summary>

1. Tokio runs the program: it runs thousands of async tasks on a few threads and handles sockets and timers. hyper speaks HTTP: it turns bytes into requests and responses into bytes. Tower defines a "service" (request in, response out, later) and middleware that wraps services. Axum adds routing and extractors, and turns your async functions into Tower services.
2. Rust has no async runtime built in, so an `async fn main` would have nothing to run it. `#[tokio::main]` wraps it in an ordinary `main` that starts Tokio's runtime and runs your code on it.
3. If opening the port fails, `?` returns that error from `main` straight away; otherwise it gives the listener. `main` can use it because it returns `std::io::Result<()>`, so it has somewhere to return the error to, and the program then exits with a failure.
4. Status 201 and the body `made it`, as plain text. The whole response is a value returned at the end of the handler, built all at once, so there's no moment where the body has been sent but the status hasn't.
5. It finishes. `with_graceful_shutdown` stops accepting new connections when the signal arrives, but lets requests already running complete before `serve` returns.
6. Because it never times out a client that sends its request very slowly, so an attacker can hold thousands of connections open (a slowloris attack). `TimeoutLayer` only starts timing once the whole request has arrived and reached the router, which a slowloris request never does. A proxy in front, or hyper's own header timeout, is the fix.

</details>

## Practice
<!-- bite: 99d23e61-2ac8-4fe2-a618-7353c87574d1 -->

1. Add `GET /health` that returns `204 No Content` with no body. (Return just `StatusCode::NO_CONTENT`.)
2. Make `/menu` return two dishes, and check the `content-type` header with `curl -i`.
3. Change the port with an environment variable: read `PORT` with `std::env::var("PORT")`, and fall back to 8080 if it isn't set. (`unwrap_or_else(|_| "8080".into())`.)
4. Add a route whose handler sleeps for 15 seconds (`tokio::time::sleep(Duration::from_secs(15)).await`) and check you get `408` after 10.
5. Make `shutdown_signal` also wait for `SIGTERM`, the signal Docker sends, with `tokio::signal::unix::signal(SignalKind::terminate())` and `tokio::select!`. (Lesson 28 needs it; try it now.)

**Done when** `cargo run` starts the server, `curl` gets "Mama Put is open!" from `/` and JSON from `/menu`, a POST to `/` gets 405 with an `allow` header, the slow route gets 408, and Ctrl+C stops it cleanly.

## Before moving on
<!-- bite: db62e630-4386-4e05-84a7-c1068a06c644 -->

You have a Rust web server: a router, two handlers that are plain async functions, a timeout, and a clean shutdown, on a stack of four crates that each do one job. You also know the one thing `axum::serve` leaves out, and that a proxy will cover it.

The menu is written by hand as a string, which isn't a menu at all. Next lesson: real routes for the menu (list, get one, add, change, remove), reading the path, the query and the JSON body with extractors, and keeping the dishes in memory where many requests can reach them at once. That's where the Rust compiler will start saying no, and you'll learn to be glad it does.

## Related
<!-- bite: 3a9d073d-5419-473c-a5dc-e2ba0add664c -->

- [[backend/frameworks/axum/02-routing-and-extractors|Next: Routing and Extractors]]
- [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|The same lesson in net/http]] — Go's built-in server, and its own "never ship this" line
- [[languages/03-rust/14-async-and-tokio|Async and Tokio]] — what `async`, `.await` and the runtime really are
- [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and Concurrency Models]] — how Tokio's model compares with goroutines and Node's event loop

## About this lesson
<!-- bite: f7caacef-d2e0-40a5-9c8b-bfc16417c2bb -->

**Level:** Beginner → Intermediate. Lesson 1 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (edition 2024), Axum 0.8, Tokio 1 and tower-http 0.7. Covers creating a crate with Cargo and features, the Tokio, hyper, Tower and Axum layers, `#[tokio::main]`, a `Router` with handlers as plain async functions, `IntoResponse` for text, tuples and status codes, automatic 404, 405 and `HEAD`, a request timeout layer, graceful shutdown, and why `axum::serve` has no timeout for slow clients and must sit behind a proxy.
