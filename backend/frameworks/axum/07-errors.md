---
id: 6aa271be-5a4a-46f1-958e-a94b2ca0023d
---

# Errors and Structured Responses

**A structured response means every answer your API gives has the same, predictable shape: successes look one way, errors look another, and every error says what went wrong in words a program can check and a person can read.** In Rust, errors are ordinary values that functions return, and Axum lets any value become a response. So the design is: every handler and extractor returns one error type, and a single piece of code decides how every error looks on the wire.

## Before you start
<!-- bite: 494a1e51-cb3f-4ee1-87d5-c6f4c1114755 -->

You should have:

1. Finished [[backend/frameworks/axum/06-validation|lesson 6]], so every body goes through `ValidatedJson` and `cargo test` passes.
2. Read [[backend/06-cross-cutting/03-error-handling|Error Handling]] if you want the idea first. It's not required.

After this lesson you will be able to:

1. Give the app one error type, `ApiError`, and turn each feature's errors into it with `From`, so `?` does the converting.
2. Make every extractor refuse with that same type.
3. Write every error in one place, as RFC 9457 problem details, and keep internal causes out of the response.
4. Give every request an ID that's in the response, the error body and every log line.
5. Answer unknown routes, wrong methods, panics and timeouts in the same shape.
6. Wrap every success in `{"data": ...}`.
7. Read a stack of layers written with `ServiceBuilder`.

## What to install
<!-- bite: dcd82048-b4d5-461b-8f95-c273f352e77c -->

```bash
cargo add tower
cargo add tower-http --features timeout,catch-panic,trace,request-id
```

1. **`tower`** gives us `ServiceBuilder`, a neater way to list many layers (step 8). Axum already uses it underneath; now we use it directly.
2. **`trace`** adds tower-http's `TraceLayer`, which logs every request and opens a `tracing` *span* for it. Lesson 3 promised we'd switch to it once there were request IDs.
3. **`request-id`** adds the layers that give each request an ID and copy it into the response.

## Where we stopped
<!-- bite: e203d0fa-1725-4a00-a3bd-2f7d4a8e8230 -->

Mama Put answers in five different shapes:

| What happened | What the client gets today |
|---|---|
| Success | bare JSON: `{"id":2,"name":"Beans and plantain",...}` |
| Bad body | `{"error": "...", "fields": [...]}` from `BadInput` |
| Dish not found | plain text: `there's no dish 99` |
| Bad path or query | Axum's plain text: ``Invalid URL: Cannot parse `abc` to a `u64` `` |
| Unknown route | `404` with an empty body |
| Panic | plain text: `Service panicked` |

A client developer has to handle every one. And when a customer says "the app showed an error at 12:40", there's nothing tying what they saw to a line in our logs.

## The kid version
<!-- bite: 550eb44d-383d-4f0d-9287-2d6d566f6f55 -->

Mama used to answer complaints however she felt: a shout, a shrug, a note on the back of a receipt. Now every complaint, about anything, gets the same small printed form: what kind of problem (a short word you can tick), a sentence saying what went wrong, and a number. She keeps a copy of every form, filed by number.

When a customer comes back angry, she asks for the number, finds her copy, and knows exactly what happened.

The form is the problem-details response. The short word is the `code`. The number is the request ID, and her copies are the logs.

**Where the picture stops working.** Mama's copy and the customer's copy say the same thing. Ours don't, on purpose: when the problem is ours (the database fell over), the customer's copy only says "something went wrong, quote this number", and the details stay on Mama's copy. A database error can contain table names and customer data, and it must never leave the server.

## Terms used in this lesson
<!-- bite: e2c4d8ea-0a84-4152-b7a9-6ec0b6a86590 -->

1. **Problem details**: This is a standard shape for HTTP error bodies, from RFC 9457: `type`, `title`, `status` and `detail`, sent as `application/problem+json`. Clients and tools may already know how to read it.
2. **Error code**: This is a short, fixed word for a kind of error, like `dish-not-found`, for programs to check. Messages can change; codes don't.
3. **Request ID**: This is a unique label given to each request when it arrives, sent back in the `X-Request-Id` header and written on every log line about it.
4. **Span**: This is `tracing`'s name for a piece of work with a start and an end, like one request. Fields on a span (the request ID) appear on every log line recorded inside it.
5. **Envelope**: This is a fixed wrapper around every success, here `{"data": ...}`, so successes and errors are told apart by shape, and there's room to add things later (paging links, lesson 9).
6. **Response extensions**: This is a place on a response to keep any typed value, for code further out to find. The client never sees it.
7. **Fallback**: This is the handler a router calls when no route matches.

## Step 1: one error type for the app
<!-- bite: d625cdd9-aea5-4e81-91fc-19c32e78885f -->

Each feature has its own error enum, and they should stay as they are: `MenuError` and `OrderError` know Mama's rules and nothing about HTTP. What's missing is one type on the **HTTP side** that every refusal turns into. Make `src/http/error.rs`, and `mod error;` in `src/http/mod.rs`:

```rust
//! One error type for every HTTP answer that isn't a success, and the one place it's written out.

use axum::{
    Json,
    extract::Request,
    http::{StatusCode, header},
    middleware::Next,
    response::{IntoResponse, Response},
};
use serde::Serialize;

/// Something went wrong, said in words a client can act on.
/// Handlers return it; `write_problems` turns it into the response body.
#[derive(Clone, Debug, PartialEq)]
pub struct ApiError {
    pub status: StatusCode,
    /// Short and stable, for programs: `dish-not-found`.
    pub code: &'static str,
    /// The same every time for this code: "Dish not found".
    pub title: &'static str,
    /// This case, for people: "there's no dish 99".
    pub detail: String,
    /// For bad input: which fields, and what's wrong with each.
    pub fields: Vec<FieldError>,
}

#[derive(Clone, Debug, PartialEq, Serialize)]
pub struct FieldError {
    pub field: String,
    pub message: String,
}

impl ApiError {
    pub fn new(status: StatusCode, code: &'static str, title: &'static str, detail: impl Into<String>) -> Self {
        ApiError { status, code, title, detail: detail.into(), fields: Vec::new() }
    }

    /// For anything nobody planned for. The cause goes to the log, never to the client.
    pub fn internal(cause: impl std::fmt::Display) -> Self {
        tracing::error!(%cause, "unexpected error");
        ApiError::new(
            StatusCode::INTERNAL_SERVER_ERROR,
            "internal",
            "Something went wrong",
            "Something went wrong on our side. Quote the request ID if you contact us.",
        )
    }
}
```

1. **It holds a `StatusCode` directly.** In the Go version of this lesson, the app-wide error has a "kind" that isn't HTTP, because Go services return it. Ours don't: the services return `MenuError` and `OrderError`, which are already free of HTTP. `ApiError` lives in the `http` module and is only ever made by HTTP code, so a status code is exactly what it should hold.
2. **`code` and `title` are `&'static str`**: fixed text written into the program. A code is never made up at run time; it's one of a list you could print.
3. **`detail: impl Into<String>`** in `new` lets callers pass a `&str` or a `String`. `.into()` turns either into a `String`.
4. **`ApiError::internal(cause)` is the most important function here.** It takes the real cause, logs it at `error` level, and throws it away. What the client gets is a fixed sentence. Use it for every failure nobody planned for: a database down, a file missing. In lesson 8, every sqlx error goes through it.
5. **`FieldError` moved here** from `validation.rs`, because `ApiError` needs it. Lesson 6's `BadInput` is gone; `ApiError` with `fields` does its job.

## Step 2: feature errors become `ApiError`, with `From`
<!-- bite: 65bdb409-ae09-48b9-87b0-fa71184cc726 -->

In lesson 4, each feature had `impl IntoResponse for MenuError`. Replace that with **`From`**. In `src/menu/handlers.rs`:

```rust
impl From<MenuError> for ApiError {
    fn from(err: MenuError) -> Self {
        let (status, code, title) = match err {
            MenuError::NotFound(_) => (StatusCode::NOT_FOUND, "dish-not-found", "Dish not found"),
            MenuError::NoName => (StatusCode::UNPROCESSABLE_ENTITY, "dish-needs-name", "A dish needs a name"),
            MenuError::BadPrice => (StatusCode::UNPROCESSABLE_ENTITY, "bad-price", "Price not allowed"),
        };
        ApiError::new(status, code, title, err.to_string())
    }
}
```

and the handlers return `Result<_, ApiError>`:

```rust
async fn get_one(State(menu): State<MenuService>, Path(id): Path<u64>) -> Result<Data<Dish>, ApiError> {
    Ok(Data(menu.get(id)?))
}
```

Here's the trick. `menu.get(id)` returns `Result<Dish, MenuError>`, but the handler returns `Result<_, ApiError>`. **`?` converts the error with `From` on the way out.** If the types don't match, `?` looks for `impl From<MenuError> for ApiError`, finds it, and calls it. Nothing at the call site says so, and nothing needs to.

Still one `match`, still in `handlers.rs`, still the only place a menu error meets a status code. And because it's a `match` on an enum, adding a variant to `MenuError` is a compile error here until you decide its code and status.

`src/orders/handlers.rs` gets the same:

```rust
impl From<OrderError> for ApiError {
    fn from(err: OrderError) -> Self {
        let (status, code, title) = match err {
            OrderError::ShopClosed => (StatusCode::CONFLICT, "shop-closed", "The shop is closed"),
            OrderError::BadQuantity => (StatusCode::UNPROCESSABLE_ENTITY, "bad-quantity", "Quantity not allowed"),
            OrderError::NoSuchDish(_) => (StatusCode::UNPROCESSABLE_ENTITY, "no-such-dish", "No such dish"),
            OrderError::DishUnavailable => (StatusCode::CONFLICT, "dish-unavailable", "Dish not available"),
            OrderError::NotFound(_) => (StatusCode::NOT_FOUND, "order-not-found", "Order not found"),
            OrderError::BadStatusChange { .. } => {
                (StatusCode::CONFLICT, "bad-status-change", "Status can't go back")
            }
        };
        ApiError::new(status, code, title, err.to_string())
    }
}
```

And the kitchen's guard in `src/http/mod.rs` answers with one too:

```rust
        ApiError::new(StatusCode::UNAUTHORIZED, "staff-only", "Kitchen staff only", "Send the staff key in X-Staff-Key.")
            .into_response()
```

## Step 3: extractors refuse with `ApiError` too
<!-- bite: 022889b1-2b8e-4277-a116-659e6eb0b4c2 -->

Lesson 6's `ValidatedJson` refused with `BadInput`. Rename `src/http/validation.rs` to `src/http/extract.rs` (and `mod validation;` to `mod extract;`), and make it refuse with `ApiError`:

```rust
impl<S, T> FromRequest<S> for ValidatedJson<T>
where
    S: Send + Sync,
    T: DeserializeOwned + Validate,
{
    type Rejection = ApiError;

    async fn from_request(req: Request, state: &S) -> Result<Self, Self::Rejection> {
        let Json(value) = Json::<T>::from_request(req, state).await?;
        value.validate()?;
        Ok(ValidatedJson(value))
    }
}
```

The `.map_err(...)` calls are gone. `?` does the converting, because the same file now says how each kind of refusal becomes an `ApiError`:

```rust
impl From<JsonRejection> for ApiError {
    fn from(rejection: JsonRejection) -> Self {
        let (status, code, title) = match rejection {
            JsonRejection::MissingJsonContentType(_) => {
                (StatusCode::UNSUPPORTED_MEDIA_TYPE, "not-json", "Body must be JSON")
            }
            JsonRejection::BytesRejection(_) => (StatusCode::PAYLOAD_TOO_LARGE, "body-too-large", "Body too large"),
            _ => (StatusCode::BAD_REQUEST, "bad-json", "Body can't be read"),
        };
        ApiError::new(status, code, title, rejection.body_text())
    }
}

impl From<ValidationErrors> for ApiError {
    fn from(errors: ValidationErrors) -> Self {
        let mut fields: Vec<FieldError> = errors
            .field_errors()
            .into_iter()
            .flat_map(|(field, errors)| {
                errors.iter().map(move |e| FieldError {
                    field: camel_case(&field),
                    message: e.message.as_deref().unwrap_or(&e.code).to_string(),
                })
            })
            .collect();
        fields.sort_by(|a, b| a.field.cmp(&b.field));
        ApiError {
            fields,
            ..ApiError::new(StatusCode::BAD_REQUEST, "invalid-fields", "Some fields aren't right", "See `errors` for each field.")
        }
    }
}
```

`JsonRejection::BytesRejection` is what reading the body fails with when it's over the limit from lesson 6, so it gets 413. Everything else wrong with the body is a 400, as lesson 6 decided. (`camel_case` and its test stay as they were.)

### `Path` and `Query`, with our refusal

Axum's own `Path` and `Query` refuse in plain text. We can't change that, but we can wrap them, and Axum's `macros` feature writes the wrapper for us. In the same file:

```rust
/// Axum's `Path`, refusing with an `ApiError`.
#[derive(FromRequestParts)]
#[from_request(via(axum::extract::Path), rejection(ApiError))]
pub struct Path<T>(pub T);

/// Axum's `Query`, refusing with an `ApiError`.
#[derive(FromRequestParts)]
#[from_request(via(axum::extract::Query), rejection(ApiError))]
pub struct Query<T>(pub T);

impl From<PathRejection> for ApiError {
    fn from(rejection: PathRejection) -> Self {
        ApiError::new(StatusCode::BAD_REQUEST, "bad-path", "Address can't be read", rejection.body_text())
    }
}

impl From<QueryRejection> for ApiError {
    fn from(rejection: QueryRejection) -> Self {
        ApiError::new(StatusCode::BAD_REQUEST, "bad-query", "Query can't be read", rejection.body_text())
    }
}
```

1. **`#[derive(FromRequestParts)]`** writes the extractor: "build this the way `axum::extract::Path` builds itself (`via`), and if it refuses, turn the refusal into an `ApiError` (`rejection`)", using the `From` below it.
2. **The same names as Axum's.** Our `Path` and `Query` are `crate::http::Path` and `crate::http::Query`. In each `handlers.rs`, take `Path` and `Query` out of the `axum::extract::{...}` import and add them to `use crate::http::{...}`. The handlers don't change by a character, because they're used the same way: `Path(id): Path<u64>`.

That's the rule this lesson follows everywhere: **a handler only ever meets one error type.** Whether the body was broken, the path wasn't a number, the dish didn't exist or the shop was closed, it's an `ApiError`.

The new `src/http/mod.rs` puts the module's front counter together:

```rust
//! What every feature's HTTP code shares: errors, extractors, the staff key. Knows nothing about dishes or orders.

mod error;
mod extract;

use std::sync::Arc;

use axum::{
    extract::{Request, State},
    http::StatusCode,
    middleware::Next,
    response::{IntoResponse, Response},
};
use subtle::ConstantTimeEq;

pub use error::{ApiError, Data, FieldError, method_not_allowed, panic_response, route_not_found, write_problems};
pub use extract::{Path, Query, ValidatedJson};
```

with `StaffKey` and `kitchen_only` below, as before. `log_requests` is gone: `TraceLayer` replaces it in step 5.

## Step 4: the problem response, written in one place
<!-- bite: 8b9b1179-1898-4cc2-80ea-b4c3ecec25ea -->

Here's the shape every error will have. A missing dish:

```http
HTTP/1.1 404 Not Found
content-type: application/problem+json
x-request-id: 1f6c2b0e-5a7d-4c7e-9f0a-3b8e2d4c6a11

{
  "type": "https://mamaput.example/problems/dish-not-found",
  "title": "Dish not found",
  "status": 404,
  "detail": "there's no dish 99",
  "code": "dish-not-found",
  "requestId": "1f6c2b0e-5a7d-4c7e-9f0a-3b8e2d4c6a11"
}
```

The same shape, field for field, as the [[backend/frameworks/net-http/07-errors|net/http]] and Express versions of Mama Put. The first four fields are the standard's. `type` is a URL naming this kind of problem, `title` is a short summary that's the same every time, `status` repeats the HTTP status, and `detail` explains this case. We add `code` for programs, `requestId`, and `errors` for bad fields.

Now, where to write it. The obvious place is `impl IntoResponse for ApiError`. But `into_response` gets only the error, not the request, so it can't know the **request ID**. So we split the job in two.

**First, `into_response` writes nothing.** It makes a response with the right status, and tucks the error inside it, in the response's **extensions**:

```rust
impl IntoResponse for ApiError {
    /// Just the status, with the error tucked inside. `write_problems` writes the body.
    fn into_response(self) -> Response {
        let mut response = self.status.into_response();
        response.extensions_mut().insert(self);
        response
    }
}
```

Extensions are a typed box on every request and response: put in any value, and code further out can ask "is there an `ApiError` in here?". The client never sees them. (That's why `ApiError` derives `Clone`: extensions need it.)

**Second, one middleware, outside everything that can fail, writes the body:**

```rust
const PROBLEMS: &str = "https://mamaput.example/problems/";

/// RFC 9457 problem details, plus our `code`, `requestId` and `errors`.
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Problem<'a> {
    r#type: String,
    title: &'a str,
    status: u16,
    detail: &'a str,
    code: &'a str,
    request_id: &'a str,
    #[serde(skip_serializing_if = "<[_]>::is_empty")]
    errors: &'a [FieldError],
}

/// The one place an error becomes a response body. Sits outside everything that can fail.
pub async fn write_problems(req: Request, next: Next) -> Response {
    let request_id = req.headers().get("x-request-id").cloned();
    let response = next.run(req).await;

    let error = match response.extensions().get::<ApiError>() {
        Some(error) => error.clone(),
        // The timeout layer answers with a bare 408. Give it the same shape as everything else.
        None if response.status() == StatusCode::REQUEST_TIMEOUT => ApiError::new(
            StatusCode::REQUEST_TIMEOUT,
            "timeout",
            "Request took too long",
            "We gave up waiting. Try again.",
        ),
        None => return response,
    };

    let request_id = request_id.as_ref().and_then(|v| v.to_str().ok()).unwrap_or("");
    let problem = Problem {
        r#type: format!("{PROBLEMS}{}", error.code),
        title: error.title,
        status: error.status.as_u16(),
        detail: &error.detail,
        code: error.code,
        request_id,
        errors: &error.fields,
    };

    let mut body = (error.status, [(header::CONTENT_TYPE, "application/problem+json")], Json(problem)).into_response();
    // Keep any other headers set further in, like `Allow` on a 405.
    for (name, value) in response.headers() {
        if name != header::CONTENT_TYPE && name != header::CONTENT_LENGTH {
            body.headers_mut().entry(name).or_insert_with(|| value.clone());
        }
    }
    body
}
```

1. **The request ID is copied before `next.run(req)`**, because `req` is moved inside and gone afterwards (lesson 3). It's the ID the layer in step 5 put on the request.
2. **`response.extensions().get::<ApiError>()`**: "is there an `ApiError` in this response?". If not, and it isn't a timeout, it's a success or something we don't touch, and it goes out unchanged.
3. **`None if ... =>`**: a match guard (lesson 5). The timeout layer is tower-http's and doesn't know `ApiError`; it answers with a bare 408. This arm gives it the same shape as everything else.
4. **`struct Problem<'a>` borrows**: `&'a str` fields point into the `ApiError` instead of copying its text. `'a` is a **lifetime**: "these borrowed fields live no longer than the error they point into". The struct only exists for the length of this function, so that's easy for the compiler to check.
5. **`r#type`**: `type` is a Rust keyword. `r#` makes it a plain name, and serde writes it as `"type"`.
6. **`"<[_]>::is_empty"`**: `errors` is a borrowed slice, `&[FieldError]`, and that's how you name a slice's `is_empty` in an attribute.
7. **The tuple `(status, [(header, value)], Json(...))`** builds the response; the header in the tuple replaces the `application/json` that `Json` set.
8. **The loop keeps headers set further in**, except the two that described the old body. Axum's router adds an `Allow` header to a 405, listing methods that do work on that path, and the client should still get it.

Why is this the right shape? **Every error in the app becomes a body in exactly one function.** A handler's `ApiError`, an extractor's refusal, the kitchen guard, the fallbacks and the panic catcher (step 6) all produce an `ApiError` in a response, and they all pass through `write_problems` on the way out. Change the shape here, and every error changes.

## Step 5: request IDs, and `TraceLayer`
<!-- bite: ff361184-53ca-4f11-8394-68c8fd00488b -->

Two layers from tower-http handle the ID:

1. **`SetRequestIdLayer::x_request_id(MakeRequestUuid)`**, outermost: if the request has no `X-Request-Id` header, it makes one, a random **UUID**, a 128-bit number written as 36 characters that's unique for all practical purposes, and puts it on the request. If the request already has one (a phone app that makes its own, or another of our services in lesson 33), it keeps it, so one ID can follow a request across systems.
2. **`PropagateRequestIdLayer::x_request_id()`**: copies the ID onto the response's headers, so the client can see it.

And the logger. Lesson 3 wrote `log_requests` by hand; now **`TraceLayer`** takes over. Delete `log_requests` from `src/http/mod.rs`. In `src/lib.rs`:

```rust
        .layer(
            TraceLayer::new_for_http()
                .make_span_with(request_span)
                .on_response(DefaultOnResponse::new().level(Level::INFO)),
        )
```

with a small function at the bottom of `lib.rs`:

```rust
/// One span per request, so every log line inside it carries the request ID.
fn request_span<B>(req: &Request<B>) -> tracing::Span {
    let request_id = req.headers().get("x-request-id").and_then(|v| v.to_str().ok()).unwrap_or("");
    info_span!("request", method = %req.method(), path = req.uri().path(), request_id)
}
```

1. **`TraceLayer` opens a span for each request**, made by `request_span`, and closes it when the response is sent. The span has the method, path and request ID as fields.
2. **Every log line recorded inside the span carries those fields**, without anyone passing the ID around. `ApiError::internal`'s `tracing::error!` runs inside a handler, inside the span, so its line has the request ID on it. That's the whole point: the customer quotes the ID from the error, you search the log for it, and you have every line about that request.
3. **`on_response(...level(Level::INFO))`** logs one line when each response goes out, with its status and how long it took, the same job `log_requests` did. (tower-http's default level is `DEBUG`, which our filter, `mama_put=info,tower_http=info`, would hide.)
4. **`fn request_span<B>`** is generic over the body type, because `TraceLayer` calls it with whatever body the request has. We only read the head.

## Step 6: unknown routes, wrong methods, panics and timeouts
<!-- bite: 384e51c5-4799-4d56-8bcd-5681841cfe7a -->

Four answers that our handlers never wrote. Each one becomes an `ApiError`, so `write_problems` gives it the same shape.

**Unknown routes and wrong methods**, in `src/http/error.rs`:

```rust
/// For routes that don't exist.
pub async fn route_not_found() -> ApiError {
    ApiError::new(StatusCode::NOT_FOUND, "route-not-found", "Route not found", "There's nothing at this address.")
}

/// For routes that exist, called with a method they don't answer.
pub async fn method_not_allowed() -> ApiError {
    ApiError::new(
        StatusCode::METHOD_NOT_ALLOWED,
        "method-not-allowed",
        "Method not allowed",
        "This address doesn't answer that method.",
    )
}
```

They're handlers like any other: async functions that return something that can be a response. In `app`, after the merges:

```rust
        .fallback(http::route_not_found)
        .method_not_allowed_fallback(http::method_not_allowed)
```

`method_not_allowed_fallback` applies to every route registered *before* it, so it goes after the `merge` calls.

**Panics.** Lesson 3's `CatchPanicLayer::new()` answers "Service panicked" in plain text. `CatchPanicLayer::custom(...)` takes a function that makes the response instead:

```rust
/// For `CatchPanicLayer`: a panic is a bug, so it's an internal error, and its message is logged.
pub fn panic_response(panic: Box<dyn std::any::Any + Send>) -> Response {
    let message = panic
        .downcast_ref::<&str>()
        .map(|s| s.to_string())
        .or_else(|| panic.downcast_ref::<String>().cloned())
        .unwrap_or_else(|| "a panic with no message".to_string());
    ApiError::internal(format!("handler panicked: {message}")).into_response()
}
```

1. **`Box<dyn std::any::Any + Send>`**: a panic can carry any value at all, so Rust hands it over as "something; find out what". **`Any`** is the trait for "a value whose type you can ask about at run time".
2. **`downcast_ref::<&str>()`** asks "is it a `&str`?" and gives `Some(&the_str)` if so. `panic!("literal")` carries a `&str`; `panic!("{x}")` and an index out of bounds carry a `String`. So we try one, `or_else` the other, and give up politely.
3. **`ApiError::internal(...)`** logs the message and gives the client the fixed sentence. A panic is a bug, and a bug's details are ours.

**Timeouts** you've seen: `write_problems` turns the bare 408 into a problem.

## Step 7: every success in an envelope
<!-- bite: 8ec615d4-f0b8-4f93-ac4c-0bcbc1cf18f2 -->

Errors have one shape; successes should too. In `src/http/error.rs` (it's the "what a response looks like" module now):

```rust
/// Every success has the same shape: `{"data": ...}`.
pub struct Data<T>(pub T);

#[derive(Serialize)]
struct Envelope<T> {
    data: T,
}

impl<T: Serialize> IntoResponse for Data<T> {
    fn into_response(self) -> Response {
        Json(Envelope { data: self.0 }).into_response()
    }
}
```

Handlers return `Data(...)` where they returned `Json(...)`:

```rust
async fn list(State(menu): State<MenuService>, Query(params): Query<ListParams>) -> Data<Vec<Dish>> {
    Data(menu.list(params.available))
}
```

and `(StatusCode::CREATED, location, Data(dish))` for the two that create something. `remove` still returns a bare `204 No Content`: no body, so no envelope.

Why bother? Three reasons. A client can tell success from failure by shape, not just status. There's room beside `data` for things that aren't the data: lesson 9 adds paging links there. And it's the same on every route, so a client's code to unwrap it is written once.

## Step 8: the whole stack, with `ServiceBuilder`
<!-- bite: 8e8995ed-304f-4c62-97d6-712fccc79a3e -->

Here's all of `src/lib.rs`:

```rust
//! Mama Put API: the menu and orders for a roadside food seller.

pub mod clock;
pub mod http;
pub mod menu;
pub mod orders;

use std::time::Duration;

use axum::{
    Router,
    extract::{DefaultBodyLimit, FromRef},
    http::{Request, StatusCode},
    middleware,
    routing::get,
};
use tower::ServiceBuilder;
use tower_http::{
    catch_panic::CatchPanicLayer,
    request_id::{MakeRequestUuid, PropagateRequestIdLayer, SetRequestIdLayer},
    timeout::TimeoutLayer,
    trace::{DefaultOnResponse, TraceLayer},
};
use tracing::{Level, info_span};

/// Everything the handlers need, built once in `main` (or in a test).
#[derive(Clone, FromRef)]
pub struct AppState {
    pub menu: menu::MenuService,
    pub orders: orders::OrderService,
    pub staff_key: http::StaffKey,
}

/// Builds the whole app from what it's given. Builds nothing real itself.
pub fn app(state: AppState) -> Router {
    let layers = ServiceBuilder::new()
        // Outermost first: each line wraps everything below it.
        .layer(SetRequestIdLayer::x_request_id(MakeRequestUuid))
        .layer(
            TraceLayer::new_for_http()
                .make_span_with(request_span)
                .on_response(DefaultOnResponse::new().level(Level::INFO)),
        )
        .layer(PropagateRequestIdLayer::x_request_id())
        .layer(middleware::from_fn(http::write_problems))
        .layer(CatchPanicLayer::custom(http::panic_response))
        .layer(TimeoutLayer::with_status_code(StatusCode::REQUEST_TIMEOUT, Duration::from_secs(10)))
        .layer(DefaultBodyLimit::max(16 * 1024));

    Router::new()
        .route("/", get(|| async { "Mama Put is open!" }))
        .merge(menu::router(state.staff_key.clone()))
        .merge(orders::router(state.staff_key.clone()))
        .fallback(http::route_not_found)
        .method_not_allowed_fallback(http::method_not_allowed)
        .with_state(state)
        .layer(layers)
}
```

(with `request_span` from step 5 at the bottom).

Lesson 3 warned that a chain of `router.layer(...)` calls reads **bottom up**: the last one added is the outermost. **`ServiceBuilder` reads top down**: the first `.layer` is the outermost, and each line wraps everything below it. With seven layers, top down is much easier to check. Then `.layer(layers)` puts the whole stack on the router at once.

Read it as a request travelling in:

1. **Set the request ID** first, so everything after can see it.
2. **`TraceLayer`** opens the span, with the ID in it. Everything inside is logged under that ID, and it logs every response, whatever made it.
3. **Propagate the ID** onto the response on the way out.
4. **`write_problems`** turns any `ApiError` from inside into a body. It's outside the panic catcher and the timeout, so their answers get the shape too.
5. **Catch panics**, turning them into `ApiError::internal`.
6. **Time out** after ten seconds.
7. **Limit bodies** to 16 KB.

Then the router, then (for writes) `kitchen_only`, then the handler.

Every position has a reason. Move `write_problems` inside `CatchPanicLayer`, and panics come out as an empty 500, because the panic flies straight out through `write_problems` (its "after" code never runs, lesson 3). Move `TraceLayer` above `SetRequestIdLayer`, and the span is made before there's an ID to put in it.

## Trying it
<!-- bite: 30f757e5-21a1-49d6-b440-21ef4b26a7d5 -->

```bash
STAFF_KEY=sekret cargo run
```

```bash
curl -s localhost:8080/menu/2
# {"data":{"id":2,"name":"Beans and plantain","priceNaira":1200,"available":true,"special":false}}

curl -si localhost:8080/menu/99
# HTTP/1.1 404 Not Found
# content-type: application/problem+json
# x-request-id: 1f6c2b0e-...
# {"type":"https://mamaput.example/problems/dish-not-found","title":"Dish not found","status":404,
#  "detail":"there's no dish 99","code":"dish-not-found","requestId":"1f6c2b0e-..."}

curl -s localhost:8080/menu/abc
# {"type":".../problems/bad-path","title":"Address can't be read","status":400,"detail":"Invalid URL: Cannot parse `abc` to a `u64`",...}

curl -s localhost:8080/suya
# {"type":".../problems/route-not-found","title":"Route not found","status":404,...}

curl -si -X PUT localhost:8080/menu
# HTTP/1.1 405 Method Not Allowed
# content-type: application/problem+json
# allow: GET,HEAD,POST
# {"type":".../problems/method-not-allowed",...}

curl -s -X POST localhost:8080/menu -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"name":"","priceNaira":0}'
# {"type":".../problems/invalid-fields","title":"Some fields aren't right","status":400,
#  "detail":"See `errors` for each field.","code":"invalid-fields","requestId":"...",
#  "errors":[{"field":"name","message":"must be 1 to 80 characters"},
#            {"field":"priceNaira","message":"must be from ₦1 to ₦1,000,000"}]}

curl -s -H 'x-request-id: from-the-app-123' localhost:8080/orders/7
# {..."code":"order-not-found","requestId":"from-the-app-123"}
```

And in the server's log, each line about a request is inside its span:

```text
INFO request{method=GET path="/menu/99" request_id="1f6c2b0e-..."}: tower_http::trace::on_response: finished processing request latency=0 ms status=404
```

Ask the customer for the request ID on their error, search the log for it, and you have the whole story. (All of the above is from a run of this lesson's code.)

One answer changed from lesson 3. `PUT /menu/1` with no staff key used to be a 401, because the kitchen guard ran first. Now it's a **405**, with `allow: GET,HEAD,PATCH,DELETE`: `method_not_allowed_fallback` answers before any route's layers run. That tells a stranger which methods exist on the path, and that's fine. The API docs in lesson 11 publish exactly that to everyone. What matters is that `PATCH` and `DELETE` still need the key.

## The Rust in this lesson
<!-- bite: c5200e92-b28c-4809-9bc3-93429f8b56a3 -->

1. **`impl From<MenuError> for ApiError`**, and **`?` converting with `From`**: when the error types differ, `?` calls `From::from` on the way out.
2. **`impl Into<String>` as a parameter**, and `.into()`: accept anything that can become a `String`.
3. **`&'static str` fields**: text fixed in the program, for codes and titles that are never made at run time.
4. **Response extensions**, `extensions_mut().insert(x)` and `extensions().get::<T>()`: a typed box on a response, keyed by type.
5. **A struct that borrows, `struct Problem<'a>`**: fields of type `&'a str` point into another value; the lifetime `'a` says they can't outlive it.
6. **Raw identifiers, `r#type`**: use a keyword as a name.
7. **`#[derive(FromRequestParts)]` with `#[from_request(via(...), rejection(...))]`**: Axum's derive for wrapping an existing extractor with your own rejection.
8. **Types with the same name as another crate's**: `crate::http::Path` beside `axum::extract::Path`; what you `use` decides which you mean.
9. **`Box<dyn Any + Send>` and `downcast_ref::<T>()`**: a value of unknown type, and asking at run time whether it's a `T`.
10. **`Option::or_else` and `unwrap_or_else`**: try another way only if the first gave nothing; build a default only if needed.
11. **Generic functions, `fn request_span<B>(req: &Request<B>)`**: work for any body type.
12. **`tracing::info_span!` with fields**, and spans: every event inside a span carries its fields.
13. **`tower::ServiceBuilder`**: layers listed outermost first.
14. **`HeaderMap::entry(...).or_insert_with(...)`**: add a header only if it isn't there already.

## Your project so far
<!-- bite: 05e2e826-5eee-4011-8c4f-7eb32ec7d7b1 -->

```text
mama-put/
├── Cargo.toml             ← + tower; tower-http + trace, request-id
└── src/
    ├── main.rs
    ├── lib.rs             ← ServiceBuilder stack: request ID, TraceLayer, write_problems, panics, timeout, body limit;
    │                         fallback and method_not_allowed_fallback; request_span
    ├── clock.rs
    ├── http/
    │   ├── mod.rs         ← mod error, extract; StaffKey; kitchen_only answers with ApiError; log_requests gone
    │   ├── error.rs       ← ApiError, FieldError, write_problems, Problem, Data, the fallbacks, panic_response
    │   └── extract.rs     ← was validation.rs: ValidatedJson, Path, Query, From<…Rejection> for ApiError
    ├── menu/
    │   ├── handlers.rs    ← From<MenuError> for ApiError; handlers return Data and Result<_, ApiError>
    │   └── ...
    └── orders/
        ├── handlers.rs    ← From<OrderError> for ApiError; the same
        └── ...
```

## Common mistakes
<!-- bite: 789eb5a8-4d23-4a5f-a8ab-1073b86688e7 -->

1. **Sending an internal error's message to the client.** Database errors hold table names and customer data. `ApiError::internal`: log it, hide it.
2. **Writing error bodies in more than one place.** Then the shapes drift. One `write_problems`, outside everything that can fail.
3. **`write_problems` inside the panic catcher.** Panics fly out through it and come back as empty 500s.
4. **Codes made from messages.** Messages get reworded; clients break. Codes are fixed words, chosen once.
5. **Mixing Axum's `Path` with ours.** One `use` of `axum::extract::Path` in a handler file, and that handler refuses in plain text again. Import `Path` and `Query` from `crate::http` only.
6. **A request ID only in the response.** It has to be on the log lines too, or it can't be looked up. A span does that.
7. **`map_err` everywhere.** Write the `From` once; `?` uses it.
8. **Reading a `ServiceBuilder` bottom up.** It's the other way round from `.layer` chains: first is outermost.

## Check your understanding
<!-- bite: 0202212d-cfea-4f81-97b3-2c8d4a14614d -->

1. `menu.get(id)?` is inside a handler that returns `Result<_, ApiError>`, and `get` returns `Result<_, MenuError>`. What makes that compile?
2. Why does `ApiError` hold a `StatusCode`, when the Go version's app-wide error deliberately doesn't know HTTP?
3. Why doesn't `impl IntoResponse for ApiError` write the JSON body itself?
4. What does the client see when a database error goes through `ApiError::internal`, and where do the details go?
5. How does the request ID get onto a log line written deep inside a handler, when nobody passes it there?
6. What would change if `write_problems` sat inside `CatchPanicLayer`?
7. Why do our `Path` and `Query` exist, and what happens if a handler imports Axum's instead?
8. Give two reasons for wrapping successes in `{"data": ...}`.

<details>
<summary>Answers, after your attempt</summary>

1. `impl From<MenuError> for ApiError`. When `?` returns an error whose type differs from the function's, it calls `From::from` to convert it.
2. Because our services already return their own HTTP-free enums (`MenuError`, `OrderError`). `ApiError` is only made by HTTP code (handlers, extractors, middleware), so a status code is exactly what it should hold.
3. Because `into_response` gets only the error, not the request, so it can't know the request ID. It puts the error in the response's extensions, and `write_problems`, which has the request, writes the body.
4. A 500 with the code `internal` and a fixed sentence asking them to quote the request ID. The real cause is logged at `error` level, inside the request's span, so it's under the same ID.
5. `TraceLayer` opens a span for each request with the ID as a field, and every log event recorded while that request's code runs is inside the span, so it carries the field.
6. A panic would fly out through `write_problems` before being caught, so its "after" code wouldn't run, and the client would get the 500 with an empty body instead of a problem.
7. So that a bad path or query is refused with an `ApiError`, the same shape as every other error. A handler that imports Axum's `Path` gets Axum's plain-text refusal back.
8. A client can tell success from failure by shape; there's room beside `data` for things like paging links; and the shape is the same on every route, so unwrapping it is written once.

</details>

## Practice
<!-- bite: c2c70be7-bf88-4084-bbb8-10b1444697bf -->

1. Make the `type` URLs lead somewhere: add `GET /problems/{code}`, returning a short plain-text explanation of each code.
2. Check that `DELETE /menu/99` says *which* dish was missing, in `detail`. Then make `OrderError::BadStatusChange`'s detail use lower case (`ready`, not `Ready`), the way the JSON spells statuses.
3. Write a unit test for `From<OrderError> for ApiError` that checks every variant gets a code that's lower case with dashes, and no two variants share a code.
4. Put `/boom` back from lesson 3, request it, and find its log line by the request ID in the response.
5. Make the timeout five seconds, add a route that sleeps for six (`tokio::time::sleep`), and check its 408 comes back as a problem.

**Done when** every error, from every handler, extractor, guard, fallback, panic and timeout, is `application/problem+json` with a code and the request ID; internal causes appear only in the log; every response has `X-Request-Id`; every log line about a request carries its ID; every success is `{"data": ...}`; and `cargo test` passes.

## Before moving on
<!-- bite: a7e2563f-4cd7-44c7-92e0-35af22632326 -->

Mama Put now speaks with one voice. One error type, converted into from every feature with `From` and `?`. One function that writes every error body. One envelope for every success. And a request ID that ties what the customer saw to every log line about it.

Everything is still in memory, though, and gone when the server stops. Next lesson: data, with PostgreSQL and sqlx, SQL the compiler checks against a real schema, migrations, and transactions that roll back on their own when something fails.

## Related
<!-- bite: 86b668bf-b5f9-4e58-9cca-82b9b086a47c -->

- [[backend/frameworks/axum/08-data-with-postgres|Next: Data with PostgreSQL]]
- [[backend/frameworks/net-http/07-errors|The same lesson in net/http]] — wrapped errors, `errors.As`, and handlers that return errors
- [[backend/06-cross-cutting/03-error-handling|Error Handling]] — the idea, across languages
- [[backend/frameworks/axum/03-middleware|Middleware]] — why the order of layers decides what each sees

## About this lesson
<!-- bite: cef8f345-9563-431a-9811-b9c321eb2078 -->

**Level:** Intermediate → Advanced. Lesson 7 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, tower 0.5 and tower-http 0.7. Covers one `ApiError` on the HTTP side while services keep their own enums, `From` impls so `?` converts feature errors, extractors refusing with `ApiError` including `#[derive(FromRequestParts)]` wrappers for `Path` and `Query`, RFC 9457 problem details written in one middleware from response extensions, hiding internal causes with `ApiError::internal`, request IDs with `SetRequestIdLayer` and `PropagateRequestIdLayer`, `TraceLayer` with a span per request so every log line carries the ID, JSON answers for unknown routes, wrong methods, panics (`CatchPanicLayer::custom`, `Any` and `downcast_ref`) and timeouts, a `{"data": ...}` envelope with `Data<T>`, and a seven-layer stack read top down with `ServiceBuilder`.
