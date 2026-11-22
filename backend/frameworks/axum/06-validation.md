---
id: ac1c7535-3e50-4ca4-9562-fd1cba10fbf9
---

# Input Validation

**Input validation means checking everything a request brings in (the body, the path, the query) at the door, before any of it reaches your rules or your data, and refusing it with a clear message if it's the wrong shape.** Axum's extractors already check that the JSON has the right fields with the right types. This lesson makes them strict about fields nobody asked for, adds one crate, `validator`, to check the values, and puts both checks in one extractor of our own, so a handler can't be reached with a bad body.

## Before you start
<!-- bite: ebd7e660-d1e2-4b54-85a6-ebc921316d57 -->

You should have:

1. Finished [[backend/frameworks/axum/05-state-and-dependency-injection|lesson 5]], so Mama Put has stores behind traits, one `AppState`, and `cargo test` passes.
2. Read [[backend/06-cross-cutting/01-validation-and-dtos|Validation and DTOs]] if you want the idea before the Rust version. It's not required.

After this lesson you will be able to:

1. Refuse JSON with fields the API doesn't know, with `deny_unknown_fields`.
2. Write value rules on a struct with `#[derive(Validate)]`, and report every bad field at once.
3. Write your own extractor, `ValidatedJson`, by implementing `FromRequest`.
4. Cap the size of a request body.
5. Say which checks belong at the door and which belong in the service.

## What to install
<!-- bite: 298d01fb-824e-48cc-b107-e09b7ac0afdb -->

```bash
cargo add validator --features derive
```

**`validator`** checks the values inside a struct: lengths, ranges, emails, URLs, patterns. You write the rules as attributes on each field, and its `derive` feature writes the checking code for you, the way serde's derive writes the JSON code.

## Where we stopped
<!-- bite: c643bab0-e573-49f1-9265-842c9fa7a60d -->

Here's what gets through today, all with `201 Created`:

```bash
# A field nobody asked for. serde ignores it without a word.
curl -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":1,"quantity":2,"totalNaira":1}'

# A typo. "prise" is ignored, so this PATCH changes nothing, and says 200 OK.
curl -X PATCH localhost:8080/menu/1 -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"prise":1800}'

# A 4,000-character name, and a price of ₦15,000,000.
```

And the refusals are uneven. The `Json` extractor answers a wrong shape with 422, the service answers a bad price with 422 too, and both send plain text. A body with three mistakes gets told about the first one only. And Axum will read a body of up to 2 MB, for an API whose biggest request is a few hundred bytes.

## The kid version
<!-- bite: 1dcbf430-2333-4100-a0f0-1aa35f2965d7 -->

Before an order reaches Mama, her nephew at the gate reads the slip. Is it really an order slip? Is the plate count a number between 1 and 20? Is the dish written in letters, not scribbled? Anything wrong, he hands it back at once, with every problem circled, not just the first.

Mama still checks the things only she can know: is there jollof left? Is it past 9pm? The nephew can't know that from the slip. That's the line in this lesson: the gate checks the slip, Mama checks the world.

**Where the picture stops working.** The nephew can be tired and let a bad slip through. In Axum, once `ValidatedJson` is the only way a handler gets its body, the compiler makes sure no handler is ever reached with a slip that skipped the gate.

## Terms used in this lesson
<!-- bite: 697b0143-8f9b-427c-93b5-0c1b8f29fcf6 -->

1. **Validation**: This is checking that input has the right shape and sensible values, using only the input itself.
2. **Business rule**: This is a check that needs to know how things are right now, like "is this dish available?". It belongs in the service, not at the door.
3. **`deny_unknown_fields`**: This is a serde setting that makes reading JSON fail if it has a field the struct doesn't.
4. **Extractor**: This is a type that can build itself from a request, like `Json`, `Path` and `State`. A handler's arguments are all extractors.
5. **`FromRequest`**: This is the trait an extractor implements when it needs the request's body. One that only needs the headers, path or query implements `FromRequestParts` instead.
6. **Rejection**: This is what an extractor answers with when it can't build itself. It must be something Axum can turn into a response.
7. **Body limit**: This is the most bytes the server will read from a request body before it gives up with `413 Payload Too Large`.

## Step 1: no fields nobody asked for
<!-- bite: 2f60d5fd-f7fe-43d1-ba2d-ad533472e9aa -->

Add one word to the `#[serde(...)]` line of every type a client sends. In `src/menu/model.rs`:

```rust
#[derive(Debug, Deserialize, Validate)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct NewDish {
```

and the same on `DishChanges`, and on `NewOrder` and `StatusChange` in `src/orders/model.rs`.

**`deny_unknown_fields`** turns "ignore anything extra" into "refuse anything extra". `{"prise":1800}` is now an error that names the field, instead of a `200 OK` that did nothing. That's the important case: a client developer's typo is caught the first time they try, not weeks later when someone asks why prices never change.

It also closes a door. `NewOrder` has no `totalNaira` field, so a client could never *set* the total, but they might believe they had. Now they're told.

There's one more struct the client fills in: the query string for `GET /menu`. In `src/menu/handlers.rs`:

```rust
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ListParams {
    available: Option<bool>,
}
```

so `/menu?availble=true` (a typo) is refused instead of quietly showing every dish.

## Step 2: checking values with `validator`
<!-- bite: 5b859b5f-e139-438b-bd81-790783233b00 -->

serde guarantees the JSON has the right fields with the right types. It doesn't check the values: an empty name, a price of -500 and a name of 4,000 characters all read fine.

That's what `validator` is for. Here's all of `src/menu/model.rs`:

```rust
use serde::{Deserialize, Serialize};
use validator::Validate;

#[derive(Clone, Debug, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Dish {
    pub id: u64,
    pub name: String,
    pub price_naira: i64,
    pub available: bool,
    pub special: bool,
}

#[derive(Debug, Deserialize, Validate)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct NewDish {
    #[validate(length(min = 1, max = 80, message = "must be 1 to 80 characters"))]
    pub name: String,
    #[validate(range(min = 1, max = 1_000_000, message = "must be from ₦1 to ₦1,000,000"))]
    pub price_naira: i64,
    #[serde(default = "yes")]
    pub available: bool,
    #[serde(default)]
    pub special: bool,
}

fn yes() -> bool {
    true
}

#[derive(Debug, Default, Deserialize, Validate)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct DishChanges {
    #[validate(length(min = 1, max = 80, message = "must be 1 to 80 characters"))]
    pub name: Option<String>,
    #[validate(range(min = 1, max = 1_000_000, message = "must be from ₦1 to ₦1,000,000"))]
    pub price_naira: Option<i64>,
    pub available: Option<bool>,
    pub special: Option<bool>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_new_dish_breaking_two_rules_reports_both() {
        let dish = NewDish { name: String::new(), price_naira: 0, available: true, special: false };
        let errors = dish.validate().unwrap_err();
        let fields = errors.field_errors();
        assert!(fields.contains_key("name"));
        assert!(fields.contains_key("price_naira"));
    }

    #[test]
    fn changes_only_check_what_was_sent() {
        let changes = DishChanges { available: Some(false), ..Default::default() };
        assert!(changes.validate().is_ok());
    }
}
```

Read the attributes like a sentence. A new dish's **name** has a **length** of at least 1 and at most 80 characters. Its **price** is in the **range** ₦1 to ₦1,000,000 (a typo guard: nobody's jollof costs ₦15,000,000). `message` is what the client will be told.

1. **`#[derive(Validate)]`** writes a method, `validate()`, that checks every rule and returns `Result<(), ValidationErrors>`.
2. **It checks every field, not just the first that fails.** The test shows it: a dish with no name *and* no price reports both. A client developer fixes everything in one go.
3. **On an `Option` field, the rule applies only when the field was sent.** `DishChanges { name: None, .. }` passes; `name: Some("")` fails. That's exactly what `PATCH` needs.
4. **`length` counts characters, not bytes.** `ọ` is one character but three bytes, so a limit in bytes would cut Yoruba dish names short.
5. **`1_000_000`**: Rust lets you put `_` in numbers, anywhere, to make them easier to read. The compiler ignores it.
6. **`..Default::default()`** in the test: "every other field from `DishChanges::default()`", all `None`. It's why `DishChanges` derives `Default`.

And in `src/orders/model.rs`:

```rust
#[derive(Debug, Deserialize, Validate)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct NewOrder {
    pub dish_id: u64,
    #[validate(range(min = 1, max = 20, message = "you can order 1 to 20 plates"))]
    pub quantity: u32,
}

#[derive(Debug, Deserialize, Validate)]
#[serde(deny_unknown_fields)]
pub struct StatusChange {
    pub status: Status,
}
```

with `use validator::Validate;` at the top. `StatusChange` has no rules (serde already refuses a status that isn't one of the three), but it derives `Validate` anyway, so it can go through the same extractor as everything else.

## Step 3: an extractor of our own
<!-- bite: 4554bf7b-f843-414c-b485-e9fe2bd64e12 -->

Now there are two checks: serde reading the body, then `validate()`. Every handler could call `validate()` itself. But then one day someone forgets, and a handler runs with a bad body. Better to make a type that *can't exist* unless both checks passed, and make handlers ask for it.

`src/http.rs` is getting full, so make it a folder: move it to `src/http/mod.rs` (same contents; Rust finds `http/mod.rs` the same way it found `http.rs`), and add at the top:

```rust
mod validation;

pub use validation::{BadInput, FieldError, ValidatedJson};
```

Then the new file, `src/http/validation.rs`:

```rust
//! Reading a JSON body strictly, and checking its values, before a handler sees it.

use axum::{
    Json,
    extract::{FromRequest, Request, rejection::JsonRejection},
    http::StatusCode,
    response::{IntoResponse, Response},
};
use serde::{Serialize, de::DeserializeOwned};
use validator::{Validate, ValidationErrors};

/// Like `Json<T>`, but the value has also passed `T`'s validation rules.
/// A handler that takes `ValidatedJson<NewDish>` can't be reached with a bad dish.
pub struct ValidatedJson<T>(pub T);

impl<S, T> FromRequest<S> for ValidatedJson<T>
where
    S: Send + Sync,
    T: DeserializeOwned + Validate,
{
    type Rejection = BadInput;

    async fn from_request(req: Request, state: &S) -> Result<Self, Self::Rejection> {
        let Json(value) = Json::<T>::from_request(req, state).await.map_err(BadInput::from_json)?;
        value.validate().map_err(BadInput::from_validation)?;
        Ok(ValidatedJson(value))
    }
}
```

Read it slowly; it's the first trait in this subject you've implemented for Axum itself.

1. **`pub struct ValidatedJson<T>(pub T);`**: a wrapper, like `Json<T>`. The field is `pub` so handlers can take it apart: `ValidatedJson(new): ValidatedJson<NewDish>`.
2. **`impl<S, T> FromRequest<S> for ValidatedJson<T>`**: "a `ValidatedJson<T>` can be built from a request, in an app whose state is `S`". We don't use the state, so any `S` will do.
3. **`T: DeserializeOwned + Validate`**: it works for any `T` that serde can read from JSON and that has rules. **`DeserializeOwned`** means the value owns its data and doesn't borrow from the body, which is gone by the time the handler runs.
4. **`type Rejection = BadInput;`**: when it can't build itself, it answers with a `BadInput`, our own type (below).
5. **`Json::<T>::from_request(req, state).await`**: we don't read JSON ourselves. We ask Axum's `Json` extractor to do it, then add our check on top. `::<T>` tells Rust which `Json` we mean.
6. **`.map_err(BadInput::from_json)?`**: if `Json` refused, turn its refusal into ours, and return it.
7. **`value.validate().map_err(BadInput::from_validation)?`**: if a rule failed, the same.
8. **`async fn` in a trait.** `from_request` is async because reading a body means waiting for the bytes to arrive.

The refusal, in the same file:

```rust
/// What a client gets back when its input is refused at the door.
#[derive(Debug, Serialize)]
pub struct BadInput {
    #[serde(skip)]
    status: StatusCode,
    error: String,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    fields: Vec<FieldError>,
}

#[derive(Debug, Serialize, PartialEq)]
pub struct FieldError {
    pub field: String,
    pub message: String,
}

impl BadInput {
    fn from_json(rejection: JsonRejection) -> Self {
        let status = match rejection {
            // Axum says 422 for JSON of the wrong shape. To us, that's bad input like any other: 400.
            JsonRejection::JsonDataError(_) => StatusCode::BAD_REQUEST,
            _ => rejection.status(),
        };
        BadInput { status, error: rejection.body_text(), fields: Vec::new() }
    }

    fn from_validation(errors: ValidationErrors) -> Self {
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
        BadInput { status: StatusCode::BAD_REQUEST, error: "some fields aren't right".to_string(), fields }
    }
}

impl IntoResponse for BadInput {
    fn into_response(self) -> Response {
        (self.status, Json(self)).into_response()
    }
}
```

1. **`#[serde(skip)]`** leaves the status out of the JSON; it goes in the response's status line instead.
2. **`skip_serializing_if = "Vec::is_empty"`** leaves `fields` out when there are none, so a broken-JSON answer is just `{"error": "..."}`.
3. **`from_json` keeps Axum's status, except one.** A missing `content-type` stays 415, a body too big stays 413, broken JSON stays 400. But JSON of the wrong shape (a string where a number goes, an unknown field) is 422 in Axum, and 400 to us. Why: 422 is what our *service* says when a rule is broken ("I understood you, and the answer is no"). Keeping 400 for everything wrong at the door means a client can tell "fix your request" from "Mama said no" by the status alone.
4. **`rejection.body_text()`** is Axum's message, like "Failed to deserialize the JSON body into the target type: unknown field `prise`...". Good enough for a developer to act on. (Lesson 7 gives every refusal a short code, too.)
5. **`from_validation`** turns validator's errors into a list. `field_errors()` gives a map from each field's name to its errors; `flat_map` flattens "fields, each with errors" into one list of `FieldError`s; `move |e|` lets the inner closure keep `field`. `e.message.as_deref().unwrap_or(&e.code)` uses our `message` if we wrote one, else validator's code (`"length"`).
6. **`sort_by`**: the map has no order, so without sorting, the same bad request could list its fields in a different order each time. Tests and client developers both like stable answers.

### Field names the client recognises

validator reports fields by their **Rust** names: `price_naira`. The client sent `priceNaira`. A message about a field they never sent is confusing, so one small function at the bottom of the file converts:

```rust
/// `price_naira` → `priceNaira`, so field names match the JSON the client sent.
fn camel_case(snake: &str) -> String {
    let mut out = String::new();
    let mut upper = false;
    for c in snake.chars() {
        if c == '_' {
            upper = true;
        } else if upper {
            out.extend(c.to_uppercase());
            upper = false;
        } else {
            out.push(c);
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn camel_case_matches_serde() {
        assert_eq!(camel_case("price_naira"), "priceNaira");
        assert_eq!(camel_case("name"), "name");
        assert_eq!(camel_case("dish_id"), "dishId");
    }
}
```

`c.to_uppercase()` gives an iterator, not a `char`, because some letters become two when made upper case (the German `ß` becomes `SS`). `out.extend(...)` adds all of them.

## Step 4: handlers that use it
<!-- bite: 58fc3e2d-4179-403c-9b08-bf9e3a5a7342 -->

In both `handlers.rs` files, add `ValidatedJson` to the `use crate::http::{...}` line, and change every `Json(...)` argument:

```rust
async fn add(State(menu): State<MenuService>, ValidatedJson(new): ValidatedJson<NewDish>) -> Result<impl IntoResponse, MenuError> {
```

Do the same for `change` (`ValidatedJson<DishChanges>`), `place` (`ValidatedJson<NewOrder>`) and `set_status` (`ValidatedJson<StatusChange>`). The handlers' bodies don't change at all.

That's the payoff of an extractor. The check isn't a line inside the handler that someone could delete; it's the *type* of the argument. If `ValidatedJson<NewDish>` exists, the dish passed every rule. And a new handler that takes `ValidatedJson<Something>` won't compile until `Something` derives `Validate`.

Keep `Json(...)` for what handlers *send back*. `ValidatedJson` is only for what comes in.

## Step 5: a cap on the body
<!-- bite: 6a4f784b-b91d-4128-a337-49cfb3a64e29 -->

Axum's `Json` extractor already refuses bodies over **2 MB**. That's a sensible default for a framework that doesn't know your API, and far too much for ours: the biggest thing a client sends Mama Put is a dish, a few hundred bytes. Every request that's allowed 2 MB is a request that can make the server hold 2 MB in memory. A few thousand at once is a lot of memory for nothing.

In `src/lib.rs`, add `DefaultBodyLimit` to the `extract::{...}` import and one layer:

```rust
        .with_state(state)
        .layer(DefaultBodyLimit::max(16 * 1024))
```

16 KB: dozens of times our biggest real body, and tiny for the server. A bigger body gets **413 Payload Too Large**, from the `Json` extractor, before any of it is parsed. (Lesson 14 adds the other kinds of limit: on uploads, and on how many requests one client can send.)

## Step 6: the path and the query are input too
<!-- bite: 6d845e17-ca3e-46fc-86f3-47eea4a21691 -->

They're already typed. `Path<u64>` refuses `/menu/abc` with a 400 before the handler runs, and `Query<ListParams>` refuses `?available=maybe`. With `deny_unknown_fields` on `ListParams`, a misspelt filter is refused too.

What isn't right yet is how they refuse: in plain text, in Axum's words, a different shape from `BadInput`. Lesson 7 gives every refusal, from every extractor, one shape.

## The line between validation and rules
<!-- bite: e72155a8-2a58-4c68-8119-2af20c889474 -->

Now there are two layers of checks, and it matters which goes where.

**At the door (`ValidatedJson`, `Path`, `Query`):** anything you can check by looking at the request alone. Is it JSON? Are the fields known? Is the name present and short enough? Is the quantity between 1 and 20? Is the ID a number? These give **400 Bad Request**.

**In the service:** anything that needs to know the state of the world. Does dish 7 exist? Is it available? Is the shop open? Is this status change going forwards? These give 404, 409, or **422 Unprocessable Content**.

Should the service *still* check that a price is positive, now the door does? **Yes.** The service will be called from places that don't go through `ValidatedJson`: a background job, the GraphQL API in lesson 21, the MCP server in lesson 23, a test. "A dish's price is more than ₦0" is Mama's rule, and the service must hold it whoever calls. The door check is there to give HTTP clients a clear, early, field-by-field answer. It's a kindness and a first defence, not the only one.

And some checks only the service can do even for a request that passed the door. `"   "` (three spaces) has a length of 3, so it passes `length(min = 1)`. The service trims it first and refuses it with `NoName`, a 422. Both checks, each in its place.

## Trying it
<!-- bite: 002f4e21-a96a-4019-8399-7f08c8ea9547 -->

```bash
STAFF_KEY=sekret cargo run
```

```bash
curl -s -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":1,"quantity":2,"totalNaira":1}'
# 400 {"error":"Failed to deserialize the JSON body into the target type: unknown field `totalNaira`, expected `dishId` or `quantity` ..."}

curl -s -X POST localhost:8080/menu -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"name":"","priceNaira":0}'
# 400 {"error":"some fields aren't right","fields":[
#   {"field":"name","message":"must be 1 to 80 characters"},
#   {"field":"priceNaira","message":"must be from ₦1 to ₦1,000,000"}]}

curl -s -X POST localhost:8080/menu -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"name":"   ","priceNaira":700}'
# 422 a dish needs a name          ← passed the door, refused by the service

curl -s -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":1,"quantity":21}'
# 400 {"error":"some fields aren't right","fields":[{"field":"quantity","message":"you can order 1 to 20 plates"}]}

curl -s 'localhost:8080/menu?availble=true'
# 400 Failed to deserialize query string: unknown field `availble` ...

head -c 20000 /dev/zero | tr '\0' 'a' | curl -s -X POST localhost:8080/menu -H 'x-staff-key: sekret' -H 'content-type: application/json' --data-binary @-
# 413 {"error":"Failed to buffer the request body: length limit exceeded"}
```

The last one sends 20,000 bytes of the letter `a`. It's refused before a single byte of it is parsed.

## The Rust in this lesson
<!-- bite: 48f1c771-a92c-48b4-818b-3e3ea160f427 -->

1. **`#[serde(deny_unknown_fields)]`**: reading fails on a field the struct doesn't have.
2. **`#[derive(Validate)]` and `#[validate(length(...))]`, `#[validate(range(...))]`**: rules on fields, checked by a generated `validate()` method.
3. **`1_000_000`**: underscores in number literals, for reading.
4. **`..Default::default()`**: struct update syntax; every field not written comes from another value.
5. **`src/http/mod.rs`**: a module that's a file can become a folder without anything outside it changing.
6. **Implementing an Axum trait, `impl<S, T> FromRequest<S> for ValidatedJson<T>`**: generic over two types, with bounds in a `where`.
7. **`type Rejection = BadInput;`**: an **associated type**, a type each implementation of a trait chooses for itself.
8. **`DeserializeOwned`**: serde's bound for "can be read, and owns its data".
9. **`Json::<T>::from_request(...)`**: the **turbofish**, `::<T>`, naming a generic type where Rust can't work it out.
10. **`async fn` in a trait implementation**.
11. **`#[serde(skip)]` and `skip_serializing_if`**: leave a field out of the JSON, always or sometimes.
12. **`flat_map`, and `move` closures inside closures**: flatten a list of lists; let the inner closure keep a value from the outer one.
13. **`sort_by(|a, b| a.field.cmp(&b.field))`**: sort with your own comparison.
14. **`char::to_uppercase()` and `String::extend`**: case changes can give more than one character.

## Your project so far
<!-- bite: 9be88ffb-ab6c-4134-972b-2e35d3bb7adb -->

```text
mama-put/
├── Cargo.toml             ← + validator (derive)
└── src/
    ├── main.rs
    ├── lib.rs             ← + DefaultBodyLimit::max(16 KB)
    ├── clock.rs
    ├── http/
    │   ├── mod.rs         ← was http.rs; + mod validation, pub use ValidatedJson, BadInput, FieldError
    │   └── validation.rs  ← ValidatedJson (FromRequest), BadInput, camel_case, 1 test
    ├── menu/
    │   ├── model.rs       ← NewDish and DishChanges: deny_unknown_fields, Validate rules; 2 tests
    │   ├── handlers.rs    ← ValidatedJson in add and change; ListParams denies unknown fields
    │   └── ...
    └── orders/
        ├── model.rs       ← NewOrder (quantity 1 to 20) and StatusChange: deny_unknown_fields, Validate
        ├── handlers.rs    ← ValidatedJson in place and set_status
        └── ...
```

## Common mistakes
<!-- bite: a0561fd7-95be-4b46-8594-30bd94dc7a4a -->

1. **Calling `validate()` inside handlers.** One day a handler forgets. Put it in the extractor, and make the type the proof.
2. **Leaving out `deny_unknown_fields`.** A typo in a field name turns into a request that silently does nothing.
3. **Only checking at the door.** Jobs, GraphQL and tests skip the door. Mama's rules live in the service.
4. **Business rules at the door.** "Is the dish available?" needs the store; it's the service's question.
5. **Reporting only the first bad field.** `validate()` collects them all; send them all.
6. **Field names in Rust's spelling.** The client sent `priceNaira`; tell them about `priceNaira`.
7. **Limits in bytes for text people type.** `length` counts characters, which is what a person means by "80 characters".
8. **The framework's body limit.** 2 MB is a default for everyone; set yours for your API.

## Check your understanding
<!-- bite: dafe697b-e5ee-459a-af7e-5a954b7fa367 -->

1. What does `deny_unknown_fields` change for `{"prise":1800}` sent to `PATCH /menu/1`, and why is the old behaviour worse than an error?
2. A new dish arrives with an empty name and a price of 0. How many problems does the client hear about, and why?
3. Why is `ValidatedJson` an extractor instead of a `validate()` call at the top of each handler?
4. In `impl<S, T> FromRequest<S> for ValidatedJson<T>`, what do `S` and `T` stand for, and what must `T` be able to do?
5. Axum answers JSON of the wrong shape with 422. Why does `BadInput` change it to 400?
6. The door already refuses a price of 0. Why does `MenuService::add` still check it?
7. `{"name":"   ","priceNaira":700}` passes the door. What refuses it, and with which status?
8. Why cap the body at 16 KB when Axum already caps it at 2 MB?

<details>
<summary>Answers, after your attempt</summary>

1. Before, serde ignored the unknown field `prise`, the `PATCH` changed nothing, and the answer was 200 with the dish unchanged. Now it's a 400 naming the unknown field. The old way hides a client's bug until someone notices prices never change.
2. Both. `validate()` checks every rule on every field and collects all the failures, and `BadInput` lists them all, so the client can fix everything at once.
3. So it can't be forgotten. A handler that takes `ValidatedJson<NewDish>` can't run unless both serde and the rules passed; the check is the argument's type, not a line someone might delete.
4. `S` is the app's state type (any, since the extractor doesn't use it) and `T` is the type being read. `T` must be readable from JSON into owned data (`DeserializeOwned`) and have validation rules (`Validate`).
5. So the status says who said no. 400 always means "your request is wrong, fix it", from the door. 422 means the request was fine but a rule in the service refused it.
6. Because the service is called from places that don't go through `ValidatedJson`: background jobs, GraphQL, the MCP server, tests. The rule must hold for all of them.
7. The service. It trims the name to `""` and returns `MenuError::NoName`, which is a 422.
8. Because every allowed byte is memory the server may have to hold, for every request at once. Our biggest real body is a few hundred bytes, so 16 KB is plenty and 2 MB is an invitation.

</details>

## Practice
<!-- bite: febbabf7-ad7e-46b5-aa8d-53a57953e50d -->

1. Add a rule that a dish name can't start or end with a space, using validator's `regex` rule or a `custom` function. Decide whether it belongs at the door or in the service, and say why.
2. Write a test for `BadInput::from_validation` (it's private, but the test module can see it) that checks the fields come out sorted and in camel case.
3. Make the `fields` messages for `NewOrder` mention the value sent: "you sent 21; you can order 1 to 20 plates". (validator puts the value in `e.params`.)
4. Lower the body limit to 100 bytes, and find out which of the curl requests above stops working. Then put it back.
5. Add `#[validate(length(max = 200))]` to a new optional field on `NewOrder`, `note: Option<String>` ("no pepper, please"), and check that orders without a note still work.

**Done when** every body is read through `ValidatedJson`, unknown fields in bodies and in the menu's query are refused with 400, bad values come back as a sorted list of camel-case fields, bodies over 16 KB get 413, the services still hold their own rules, and `cargo test` passes.

## Before moving on
<!-- bite: eb543af8-1b8e-4dd3-a2cb-8c232b8b9bb2 -->

Nothing reaches a handler now without passing the door: the shape is checked by serde, strictly, the values by validator, all at once, and the size by a limit sized for this API. And you've written your first extractor, which made "this body was checked" something the type system knows.

But look at the refusals. A bad field is `{"error", "fields"}`; a missing dish is plain text; a bad path is Axum's plain text; an unknown route is an empty 404; a panic is "Service panicked". Five shapes. Next lesson: errors and structured responses, with one `ApiError` for the whole app, the standard problem-details shape, request IDs in every answer and every log line, and `{"data": ...}` around every success.

## Related
<!-- bite: c2517400-3f42-4184-a83a-d780d0fdda7a -->

- [[backend/frameworks/axum/07-errors|Next: Errors and Structured Responses]]
- [[backend/frameworks/net-http/06-validation|The same lesson in net/http]] — a strict decoder by hand, and validator's struct tags
- [[backend/06-cross-cutting/01-validation-and-dtos|Validation and DTOs]] — the idea, and where each check belongs
- [[backend/frameworks/axum/02-routing-and-extractors|Routing and Extractors]] — the extractors this lesson builds on

## About this lesson
<!-- bite: c236c366-3e1c-4c91-8dc5-69b7d3353426 -->

**Level:** Intermediate. Lesson 6 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, serde and validator 0.21. Covers `deny_unknown_fields` on bodies and queries, value rules with `#[derive(Validate)]` including `length` counting characters and rules on `Option` fields, a `ValidatedJson<T>` extractor implementing `FromRequest` with its own `Rejection`, keeping 400 for the door and 422 for the service, every bad field reported at once in camel case and in a stable order, `DefaultBodyLimit` and why the 2 MB default is too generous, typed path and query values, and the line between validation at the door and business rules in the service.
