---
id: 6c180128-3120-41ce-bb43-f64b9319b63b
---

# Middleware

**Middleware is code that runs around your handlers: it sees each request before the handler does, can stop it or pass it on, and sees the response on the way back out.** In Axum, middleware are **layers**, from the Tower crate. Each layer wraps everything inside it, like the skins of an onion, and the same layers work for HTTP servers, HTTP clients and gRPC alike.

## Before you start
<!-- bite: 4f02d12e-d5cc-4b8a-a6f9-91f4cd8b25d4 -->

You should have:

1. Finished [[backend/frameworks/axum/02-routing-and-extractors|lesson 2]], with the six menu routes working.
2. Met traits and generics in Rust. If not, skim [[languages/03-rust/09-traits|Traits]]; this lesson uses them more than it explains them.

After this lesson you will be able to:

1. Write middleware as a plain async function with `middleware::from_fn`.
2. Log every request with `tracing`: method, path, status and how long it took.
3. Turn a panic in a handler into a 500 with `CatchPanicLayer`, instead of a dropped connection.
4. Guard some routes but not others with `route_layer`, and pass settings to middleware with `from_fn_with_state`.
5. Get the order of layers right, and say why order is behaviour.

## What to install
<!-- bite: 8ea684ac-1830-4f98-ac3d-af0381c94c25 -->

```bash
cargo add tracing
cargo add tracing-subscriber --features env-filter
cargo add tower-http --features timeout,catch-panic
cargo add subtle
```

1. **`tracing`** is how Rust programs record what they're doing: log lines with named fields (`status = 200`), and later (lesson 35) spans that time pieces of work. Almost every async crate uses it, including Axum and Tower.
2. **`tracing-subscriber`** decides what happens to those records: print them, filter them, format them as JSON. `env-filter` lets you choose how much to see with a setting like `mama_put=info`.
3. **`catch-panic`** adds tower-http's panic catcher to the `timeout` you already have.
4. **`subtle`** compares secrets safely (step 4).

## Where we stopped
<!-- bite: bad62347-213e-4340-bfa2-6ba9563a26e7 -->

The menu works, but nothing is recorded. When a customer says "the app showed an error at 12:40", there's no way to see what came in or what went out. If a handler panics, the customer's connection is just cut. And anyone at all can add, change or delete dishes.

## The kid version
<!-- bite: 975619bf-fb8e-4423-990a-bdbbeb5063bf -->

Mama's stall has a gate with a helper standing at it. Every customer passes the helper on the way in and on the way out. On the way in, the helper writes their name in a notebook; on the way out, what they bought and how long it took.

There's a second helper, further in, in front of the kitchen door only. That one asks for the staff password, and turns away anyone without it, before they reach the pots.

Each helper is a middleware. The notebook is the log. The kitchen-door helper is the staff check. And the order they stand in matters: if the kitchen-door helper stood outside the notebook-keeper, the people turned away would never be written down.

**Where the picture stops working.** At the stall, a helper can't stop a pot from boiling over. Our panic catcher can: when a handler crashes, it catches the crash and answers "sorry, something went wrong", and the server carries on.

## Terms used in this lesson
<!-- bite: 2ec80b93-1502-400a-8fc6-348822d501a8 -->

1. **Middleware**: This is code that wraps request handling, before and after.
2. **Layer**: This is Tower's name for a middleware: something that takes a service and returns a new service wrapped around it. `.layer(...)` adds one to a router.
3. **Service**: This is Tower's idea of "something that answers requests". Your router is one; so is every layer wrapped around it.
4. **`Next`**: This is what a `from_fn` middleware calls to pass the request on to whatever is inside it.
5. **`tracing`**: This is Rust's library for recording events with named fields, and the **subscriber** is what prints or sends them.
6. **Panic**: This is Rust stopping the current piece of work because something happened that the code said can't happen (an index past the end, an `unwrap` on `None`).
7. **Constant-time comparison**: This is comparing two secrets in a way that takes the same time whether they differ at the first character or the last.

## Step 1: the shape of every middleware
<!-- bite: 508bcc65-dde0-403a-8973-1a762ea8dc7d -->

Tower defines middleware with two traits, `Service` and `Layer`, and writing them by hand means a struct, two trait implementations and a boxed future: about forty lines of very careful code. Axum gives a much easier way, for the middleware you write yourself: **a plain async function**.

```rust
use axum::{extract::Request, middleware::Next, response::Response};

async fn my_middleware(req: Request, next: Next) -> Response {
    // before: look at the request, maybe change it, maybe answer it yourself
    let response = next.run(req).await;
    // after: look at the response, maybe change it
    response
}
```

1. **`req: Request`** is the whole request.
2. **`next: Next`** is "everything inside this middleware": other middleware, the router, the handler. **`next.run(req).await`** passes the request in and waits for the response to come back out.
3. **Returning without calling `next`** stops the request: the inside never runs. That's how a guard works.

Add it with `middleware::from_fn`:

```rust
let app = Router::new()
    // ... routes ...
    .layer(middleware::from_fn(my_middleware));
```

`from_fn` turns the function into a Tower layer. You'll write all of Mama Put's own middleware this way. Ready-made middleware from `tower-http` (timeouts, panics, CORS, compression) are real Tower layers, and you add them with the same `.layer(...)`.

## Step 2: logging every request
<!-- bite: 2d955467-9f82-4213-8f49-9052c35ae903 -->

First, switch on `tracing`'s output, at the top of `main`:

```rust
tracing_subscriber::fmt().with_env_filter("mama_put=info,tower_http=info").init();
```

That prints every event from our crate (`mama_put`) and from tower-http at `info` level or above, to the terminal, with the time. Lesson 35 switches it to JSON and reads the filter from an environment variable, `RUST_LOG`.

Now the logger:

```rust
use tracing::info;

async fn log_requests(req: Request, next: Next) -> Response {
    let method = req.method().clone();
    let path = req.uri().path().to_owned();
    let start = std::time::Instant::now();

    let response = next.run(req).await;

    info!(%method, path, status = response.status().as_u16(), took_ms = start.elapsed().as_millis() as u64, "request");
    response
}
```

1. **Copy what we need from the request *before* `next.run(req)`.** `next.run` takes the request by value: it's moved inside, and we can't look at it again afterwards. So the method and path are copied first (`.clone()`, `.to_owned()`). This is Rust's ownership rule at work: once you've given something away, it's not yours.
2. **`Instant::now()` and `start.elapsed()`** measure how long the inside took.
3. **The response is a value we get back**, so its status is right there: `response.status()`. In Go, a logger can't see the status without wrapping the writer in a "status recorder" ([[backend/frameworks/net-http/03-middleware|lesson 3 of net/http]] builds one). In Axum, the handler *returns* the response, so the middleware simply has it.
4. **`info!(...)`** records an event with named fields. `%method` means "record it using its `Display` text" (`GET`); `path` on its own means "a field called `path` with this variable's value"; `status = ...` names a field explicitly. The last argument is the message.

From a run of this lesson's code (colours removed):

```text
INFO mama_put: Mama Put API listening addr=127.0.0.1:8080
INFO mama_put: request method=GET path="/menu/2" status=200 took_ms=0
INFO mama_put: request method=POST path="/menu" status=401 took_ms=0
INFO mama_put: request method=POST path="/menu" status=201 took_ms=0
INFO mama_put: request method=GET path="/nope" status=404 took_ms=0
```

Every request, including the 401s and the router's own 404s, because the logger wraps everything (step 5).

(tower-http has a ready-made logging layer, `TraceLayer`, which also opens a `tracing` *span* per request. We'll switch to it in lesson 7, when we add request IDs; writing one by hand first shows there's no magic in it.)

## Step 3: catching panics
<!-- bite: 98dfbf7a-463d-46dc-83b7-3c686d3cd931 -->

Add a route that panics on purpose:

```rust
async fn boom() -> &'static str {
    let dishes: Vec<&str> = Vec::new();
    dishes[5] // the vector is empty, so this panics
}
```

with `.route("/boom", get(boom))`, and request it **without** any panic catcher:

```bash
curl -i localhost:8080/boom
```

```text
curl: (52) Empty reply from server
```

Tokio catches the panic in that request's task, so the **server keeps running** (the next request to `/` still works). But this request's connection is simply dropped, with no response at all. The customer's phone shows a network error, not a server error, which is confusing. And our logger never logs it: the panic flew straight out through it.

Now add tower-http's panic catcher:

```rust
use tower_http::catch_panic::CatchPanicLayer;

// ...
    .layer(CatchPanicLayer::new())
```

```text
HTTP/1.1 500 Internal Server Error
content-type: text/plain; charset=utf-8

Service panicked
```

and the log shows the panic, then the request:

```text
ERROR tower_http::catch_panic: Service panicked: index out of bounds: the len is 0 but the index is 5
INFO mama_put: request method=GET path="/boom" status=500 took_ms=0
```

A proper 500, logged with its cause. (Lesson 7 makes this 500 the same JSON problem response as every other error, and hides "Service panicked" from the client.)

Panics should be rare in Rust code, because Rust's errors are values (`Result`) that you handle, not exceptions that fly. A panic means a bug: an `unwrap()` on something that wasn't there, an index past the end. That's exactly why the catcher matters: bugs happen in production, and one bug in one route must not cut customers off without a word.

Delete `/boom` when you've tried it.

## Step 4: kitchen staff only
<!-- bite: fb242637-52c4-40ff-959d-997861c9ca87 -->

Only the kitchen may change the menu. Proper logins come in lesson 12. For now, the kitchen has a secret **staff key**, and every request that changes the menu must send it in a header, `X-Staff-Key`.

The key must not be written in the code, where anyone who sees the code sees the key. It comes from an **environment variable**, read once in `main`:

```rust
let staff_key = std::env::var("STAFF_KEY").expect("set STAFF_KEY to the kitchen's secret key");
```

If `STAFF_KEY` isn't set, the program stops at start-up with that message. Better than starting with no key and letting everyone in.

The middleware needs the key, so it's a `from_fn_with_state` middleware, which gets state like a handler does:

```rust
use subtle::ConstantTimeEq;

async fn kitchen_only(State(staff_key): State<String>, req: Request, next: Next) -> Response {
    let given = req.headers().get("x-staff-key").map(|v| v.as_bytes()).unwrap_or_default();
    if given.ct_eq(staff_key.as_bytes()).into() {
        next.run(req).await
    } else {
        (StatusCode::UNAUTHORIZED, "kitchen staff only").into_response()
    }
}
```

1. **`State(staff_key): State<String>`** first, like a handler's extractors, then `req` and `next` last.
2. **`req.headers().get("x-staff-key")`** gives an `Option<&HeaderValue>`; `.map(|v| v.as_bytes())` turns it into the header's bytes, and `.unwrap_or_default()` gives an empty slice if the header is missing. (Header names are case-insensitive, and stored in lower case.)
3. **`given.ct_eq(staff_key.as_bytes())`** compares in constant time. Why not `==`? Because `==` on bytes stops at the first difference. A wrong guess that starts with the right letter takes a tiny bit longer to fail than one that doesn't. Over thousands of tries, an attacker can measure that and find the key one character at a time. `ct_eq` always looks at every byte. Use it whenever you compare secrets. (It returns a `subtle::Choice`, not a `bool`, on purpose: `.into()` turns it into one at the last moment.)
4. **The wrong key stops the request**: we answer 401 and don't call `next`. The handler never runs.
5. **`.into_response()`** turns the tuple into a `Response`, because this function must return the same type on both branches.

### On some routes, not all

The logger is for every request. The staff key is only for the three routes that change the menu. Axum's answer is to put those routes in a router of their own, and give that router the guard:

```rust
let public = Router::new()
    .route("/", get(open))
    .route("/menu", get(list_dishes))
    .route("/menu/specials", get(specials))
    .route("/menu/{id}", get(get_dish));

let kitchen = Router::new()
    .route("/menu", post(add_dish))
    .route("/menu/{id}", patch(change_dish).delete(remove_dish))
    .route_layer(middleware::from_fn_with_state(staff_key, kitchen_only));

let app = public
    .merge(kitchen)
    .with_state(menu)
    // ... the layers for everything, in step 5
```

1. **Two routers, merged.** `merge` puts both sets of routes into one router, at the same level. `GET /menu` comes from `public`, `POST /menu` from `kitchen`, and Axum joins the two into one route with two methods.
2. **`route_layer`**, not `layer`. The difference is real: `layer` wraps the router's *fallback* too (the thing that answers 404 for unknown paths), so a `layer`-added guard would also run for requests to paths that don't exist. `route_layer` wraps only the routes that matched. For a guard, that's what you want.
3. **A route group** is just a router. Go's standard library has no route groups, which is the main thing Chi adds to it. In Axum, grouping is how routers are built.

Try it:

```bash
STAFF_KEY=sekret cargo run
```

```bash
curl -i -X POST localhost:8080/menu -H 'content-type: application/json' -d '{"name":"Moi moi","priceNaira":700}'
# 401 kitchen staff only
curl -i -X POST localhost:8080/menu -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"name":"Moi moi","priceNaira":700}'
# 201 Created
curl -i localhost:8080/menu/2
# 200, no key needed
```

One detail you might spot: `PUT /menu/1` (a method nobody handles) now answers **401**, not 405, when there's no key, because the kitchen's guard sits on that path and runs first. That's fine: it tells a stranger nothing about which methods exist. With the key, it's 405 as before.

## Step 5: order is behaviour
<!-- bite: b4c1b5f4-f3d1-4c50-92a4-9b000547bf02 -->

The layers for everything go on the merged router:

```rust
let app = public
    .merge(kitchen)
    .with_state(menu)
    .layer(CatchPanicLayer::new())
    .layer(TimeoutLayer::with_status_code(StatusCode::REQUEST_TIMEOUT, Duration::from_secs(10)))
    .layer(middleware::from_fn(log_requests));
```

**Each `.layer` wraps everything above it.** So the **last** one added is the **outermost**. A request travels in from the bottom of this list to the top, and the response travels back out from the top to the bottom:

```text
request → log_requests → timeout → catch panics → router → kitchen_only (some routes) → handler
response ← log_requests ← timeout ← catch panics ← router ← ...
```

That reversal ("the last line runs first") catches everyone at least once. Read a chain of `.layer` calls from the bottom up.

The order isn't style. Each layer only sees what happens **inside** it. Swap the panic catcher and the logger, so the catcher is outermost:

```rust
    .layer(TimeoutLayer::with_status_code(StatusCode::REQUEST_TIMEOUT, Duration::from_secs(10)))
    .layer(middleware::from_fn(log_requests))
    .layer(CatchPanicLayer::new());
```

I tried it with `/boom`: the client still gets its 500, but the log has the panic and **no `request` line**. The panic flew straight out through the logger (its "after" code never ran) and was caught outside it. The one request you most needed to see isn't logged.

The rules that hold in almost every app:

1. **The logger goes outermost**, so it sees everything, including the 401s, the 404s, the timeouts and the 500s from other layers.
2. **The panic catcher goes just inside it**, so it protects everything else, and its 500 is logged.
3. **Checks that can stop a request (the staff key, later the login) go close to the handlers they guard**, with `route_layer`, so they don't block routes that don't need them.

(There's also `tower::ServiceBuilder`, which lists layers in the other order, outermost first, top to bottom, and reads more naturally. Lesson 7 uses it once the list gets long. Either way, the rule is the same: know which one is outside.)

## The Rust in this lesson
<!-- bite: 32c9799c-e207-4bd2-936d-54ab039a858a -->

1. **`middleware::from_fn(f)` and `from_fn_with_state(state, f)`**: turn an `async fn(Request, Next) -> Response` (with extractors in front, for the second) into a Tower layer.
2. **Moving a value, `next.run(req)`**: `req` is given away; it can't be used after. Copy what you need first.
3. **`.clone()` and `.to_owned()`**: make an owned copy, here of the method and of the path text.
4. **`std::time::Instant`**: a moment in time for measuring how long something took, with `.elapsed()`.
5. **`tracing::info!` with fields**: `%x` records `x`'s `Display` text, `?x` its `Debug` text, `name = value` names a field.
6. **`std::env::var("NAME")`**: reads an environment variable, as a `Result` (it might not be set, or not be text).
7. **`Option::map` and `unwrap_or_default()`**: change what's inside an `Option`, then take it or the type's default (an empty slice).
8. **Traits from other crates, `use subtle::ConstantTimeEq;`**: bringing the trait into scope is what makes its method, `ct_eq`, available on byte slices.
9. **`.into()`**: convert to whatever type the context needs, here `Choice` into `bool`.
10. **`.into_response()`**: turn anything with `IntoResponse` into a `Response`, so both branches of an `if` have the same type.
11. **`Router::merge` and `route_layer`**: combine routers at one level; wrap only matched routes with a layer.
12. **Panics, and `CatchPanicLayer`**: a panic stops one request's task; the layer turns it into a 500.

## Your project so far
<!-- bite: ef121f41-cacc-497a-a88b-6f5c0ad037a6 -->

```text
mama-put/
├── Cargo.toml      ← + tracing, tracing-subscriber (env-filter), subtle; tower-http catch-panic
├── Cargo.lock
└── src/
    └── main.rs     ← STAFF_KEY from the environment; public and kitchen routers, merged;
                       log_requests (outermost), CatchPanicLayer, timeout; kitchen_only on writes only
```

## Common mistakes
<!-- bite: 421106db-319a-4ddd-a64a-eb8f17b5db42 -->

1. **Reading the request after `next.run(req)`.** It's been moved. Copy the method and path first.
2. **Reading `.layer` calls top to bottom.** The last one added is the outermost.
3. **The panic catcher outside the logger.** Panicking requests are answered but never logged.
4. **No panic catcher.** A bug in one route cuts customers off with an empty reply.
5. **A guard added with `layer` instead of `route_layer`.** It also runs for paths that don't exist.
6. **Comparing secrets with `==`.** It leaks timing. `ct_eq`.
7. **A secret written in the code, or a default key when the variable is missing.** Read it from the environment, and refuse to start without it.
8. **Writing a full Tower `Service` for every middleware.** `from_fn` covers almost everything; write a real `Layer` only when you need what it alone can do (lesson 33 meets one).

## Check your understanding
<!-- bite: 0fc795d4-4a89-439b-a4b4-22bbd4326661 -->

1. Why does `log_requests` copy the method and path before calling `next.run(req)`?
2. How does a Go logging middleware find out the response's status, and why doesn't an Axum one need to?
3. What does a client see when a handler panics with no `CatchPanicLayer`, and with one?
4. Why is the staff check added with `route_layer` on its own router, and not with `layer` on the whole app?
5. In `.layer(A).layer(B).layer(C)`, which one does a request reach first?
6. The panic catcher is moved outside the logger. What changes for the client, and what changes in the logs?

<details>
<summary>Answers, after your attempt</summary>

1. Because `next.run(req)` takes ownership of the request: it's moved inside, and the middleware can't use it afterwards. Anything it wants to log must be copied out first.
2. In Go, the handler writes the status into a `ResponseWriter`, so a logger must wrap the writer to see it. In Axum, the handler returns the response as a value, so `next.run(req).await` hands it straight back to the middleware, status and all.
3. With none: the connection is dropped, and curl reports an empty reply, while the server keeps running. With one: a proper `500 Internal Server Error`, and the panic's message in the log.
4. So the guard only runs for the routes that change the menu, and only for routes that matched. Reads stay open, and with `layer` the check would also run on the fallback for paths that don't exist.
5. `C`. Each `.layer` wraps everything before it, so the last one added is the outermost and sees the request first.
6. The client still gets a 500. But the panic now flies out through the logger before it's caught, so the logger's "after" code never runs and that request has no log line.

</details>

## Practice
<!-- bite: 482370fe-c4e3-4e84-ae7b-1efb2c3ca0e1 -->

1. Add the `X-Response-Time` header to every response, from a `from_fn` middleware: `response.headers_mut().insert("x-response-time", ...)`.
2. Log the request's `user-agent` header too, and decide what to log when it's missing.
3. Make `kitchen_only` refuse to start if `STAFF_KEY` is shorter than 16 characters.
4. Add `/boom` back, try both orders of the logger and the panic catcher, and compare the logs yourself.
5. Rewrite the three `.layer` calls with `tower::ServiceBuilder::new().layer(...).layer(...).layer(...)` (`cargo add tower`), in the order that gives the same behaviour, and check with `/boom` that it does.

**Done when** every request is logged with its method, path, status and time, a panicking route answers 500 and is logged, writes without the right `X-Staff-Key` get 401 while reads need no key, the server won't start without `STAFF_KEY`, and you can say for any pair of layers which one is outside.

## Before moving on
<!-- bite: 3f0c7ce2-6865-4fb0-b293-b7f2353fe4c7 -->

Every request is now logged, a panic is a 500 instead of a dropped connection, and the kitchen's routes are guarded. You've written middleware as plain async functions, grouped routes by putting them in their own router, and seen that the order of layers decides what each one can see.

`main.rs` is now well over two hundred lines: dishes, the store, six handlers, three middleware and `main`, all in one file. Orders are coming next, and they'd double it. Next lesson: structuring a Rust service, with a module per feature, a library crate beside the binary, and Rust's privacy rules doing the work.

## Related
<!-- bite: bc0d955c-7b6c-495b-ad69-5b9a80bf6bc0 -->

- [[backend/frameworks/axum/04-structuring-an-axum-service|Next: Structuring an Axum Service]]
- [[backend/frameworks/net-http/03-middleware|The same lesson in net/http]] — `func(Handler) Handler`, and a status recorder to see the status
- [[backend/03-structuring-a-backend/index|Structuring a Backend]] — where middleware fits in a backend's layers
- [[languages/03-rust/09-traits|Traits]] — what `Service`, `Layer` and `IntoResponse` are

## About this lesson
<!-- bite: 64ac3ae7-8fe6-4c93-9606-d274393a6b3a -->

**Level:** Intermediate. Lesson 3 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later, Axum 0.8, tower-http 0.7, tracing and subtle. Covers Tower layers and services, middleware as async functions with `from_fn` and `from_fn_with_state`, ownership of the request across `next.run`, logging with `tracing` and why the status is simply in the returned response, what a panic does with and without `CatchPanicLayer`, a staff key from the environment compared in constant time, route groups as separate routers joined with `merge`, `route_layer` versus `layer`, and why the last layer added is the outermost and why order is behaviour.
