---
id: 89abf20e-3168-41ca-8163-a34f7b00c5c8
---

# Routing and Extractors

**Routing is deciding which function answers which request, by its method and path. Extractors are how that function gets what it needs from the request: you write the parameter's type (`Path<u64>`, `Json<NewDish>`), and Axum fills it in, or answers the request with an error before your function ever runs.** In Axum, the list of a handler's arguments *is* the list of what it reads from the request, checked by the compiler.

## Before you start
<!-- bite: 8eb1f4dc-771e-402d-97a7-e6dfd273788c -->

You should have:

1. Finished [[backend/frameworks/axum/01-what-axum-is-and-a-first-server|lesson 1]], with the server running.
2. Met structs, enums, `Option` and `Result` in Rust. If not, read [[languages/03-rust/06-structs-enums-and-pattern-matching|Structs, Enums and Pattern Matching]] and [[languages/03-rust/07-option-and-result|Option and Result]].
3. Heard of `Arc` and `Mutex`. If not, skim [[languages/03-rust/13-concurrency|Concurrency]]; this lesson explains what we need.

After this lesson you will be able to:

1. Design the menu's routes as a REST resource, and register them in a `Router`.
2. Read the path, the query and the JSON body with the `Path`, `Query` and `Json` extractors, and turn Rust structs into JSON and back with serde.
3. Share the menu between requests with `State`, `Arc` and `Mutex`, and say why the compiler insists.
4. Return the right status codes, with `Result` and tuples.
5. Read the two compiler errors every Axum beginner meets, and make them readable with `#[axum::debug_handler]`.

## What to install
<!-- bite: 875cea66-a9d7-419f-a566-b7eb8d2fd334 -->

One crate, for turning Rust values into JSON and back:

```bash
cargo add serde --features derive
```

**serde** (SERialize, DEserialize) is how almost every Rust program reads and writes JSON, TOML, YAML and more. The `derive` feature lets you write `#[derive(Serialize, Deserialize)]` on a struct instead of writing the conversion by hand. Axum's `Json` extractor uses it, and Axum depends on `serde_json` already.

And switch on Axum's `macros` feature, for `#[axum::debug_handler]` in step 7:

```bash
cargo add axum --features macros
```

## Where we stopped
<!-- bite: 4449b9b8-8a04-451b-bd5e-6bc287a47427 -->

Lesson 1's `/menu` returns a string we typed by hand. A real menu changes: the kitchen adds a dish, changes a price, marks egusi as finished. And customers want to see one dish, or only the dishes still available.

## The kid version
<!-- bite: 912148d2-3fd4-45d5-b2a3-6382da585e7b -->

Mama Put's stall has a board on the wall: "Menu — ask here. Specials — ask here. One dish by its number — ask here." That board is the router.

When you ask for "dish number 2", the helper at the counter checks it really is a number before bothering Mama. If you say "dish number banana", the helper says "that's not a dish number" and Mama never hears about it. That helper is an extractor.

**Where the picture stops working.** At the stall, several helpers might reach into the same pot at once and spill it. Our server has many requests running at once, on different threads. Rust won't let you write a program where two of them can change the menu at the same instant: it simply won't compile. The helpers have to take turns, and the compiler checks that they do.

## Terms used in this lesson
<!-- bite: 17b79a8b-71d2-493f-acaa-fc684a1a62f9 -->

1. **Resource**: This is a thing the API lets you work with, like the menu or one dish, named by a path like `/menu/2`.
2. **Path parameter**: This is the part of the path that changes, like the `2` in `/menu/2`. In Axum's route pattern it's written `{id}`.
3. **Query string**: This is the part after `?` in a URL, like `?available=true`. It says how to show something, not which thing.
4. **Body**: This is data sent with a request, usually JSON for `POST` and `PATCH`.
5. **serde**: This is Rust's library for turning values into formats like JSON (**serializing**) and back (**deserializing**).
6. **State**: This is data every handler can reach, like the menu, given to the router once with `.with_state(...)`.
7. **`Arc`**: This means "atomically reference counted": a pointer that lets many owners share one value, safely across threads. The value is freed when the last owner is gone.
8. **`Mutex`**: This is a lock: only one thread at a time can be inside it. `lock()` waits your turn and gives you a **guard**; the lock is released when the guard goes away.
9. **Rejection**: This is the error response an extractor sends when it can't make sense of the request.

## Step 1: the routes for the menu
<!-- bite: 98dad607-55a0-42ba-8adc-a59a1b5f763c -->

Here is the menu as a REST resource. The path names **what**, the method says **what to do**.

| Method and path | What it does | Success status |
|---|---|---|
| `GET /menu` | list the dishes (`?available=true` to filter) | 200 |
| `GET /menu/specials` | list today's specials | 200 |
| `GET /menu/{id}` | get one dish | 200 |
| `POST /menu` | add a dish | 201, and a `Location` header |
| `PATCH /menu/{id}` | change some fields of a dish | 200 |
| `DELETE /menu/{id}` | remove a dish | 204, no body |

Notice there's no `/getDish` or `/deleteDish`. The verb is already in the method. And `{id}` is in the path, not the query, because it says **which** dish, not how to show it.

In Axum, the whole table is five lines:

```rust
let app = Router::new()
    .route("/", get(open))
    .route("/menu", get(list_dishes).post(add_dish))
    .route("/menu/specials", get(specials))
    .route("/menu/{id}", get(get_dish).patch(change_dish).delete(remove_dish))
    .with_state(menu)
    .layer(TimeoutLayer::with_status_code(StatusCode::REQUEST_TIMEOUT, Duration::from_secs(10)));
```

1. **One `.route` per path**, and the methods for that path chained on it: `get(list_dishes).post(add_dish)`. Each method only goes to its own handler; any other method on that path gets lesson 1's 405, with an `allow` header listing the real ones.
2. **`{id}`** captures one path segment. In lesson 1's common mistakes: the old `:id` form from Axum 0.7 now stops the program at start-up. I tried it:

   ```text
   thread 'main' panicked at src/main.rs:90:10:
   Path segments must not start with `:`. For capture groups, use `{capture}`.
   ```

   A panic at start-up is the good kind: you find out the moment you run it, not when a customer does.
3. **`/menu/specials` and `/menu/{id}` don't fight.** Axum's router always prefers the exact path to the one with a capture, whatever order you write them in. `GET /menu/specials` reaches `specials`, and `GET /menu/2` reaches `get_dish`. You can also add the same path in two `.route` calls with different methods, and Axum joins them; but the same *method* on the same path twice is another start-up panic ("Overlapping method route"), not a silent "the first one wins".
4. **`.with_state(menu)`** gives every handler access to the menu (step 3).

## Step 2: dishes as Rust structs, and JSON with serde
<!-- bite: a11bda01-2f12-4c2f-8691-e7eda991476f -->

```rust
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct Dish {
    id: u64,
    name: String,
    price_naira: i64,
    available: bool,
    special: bool,
}
```

1. **`#[derive(Serialize)]`** writes the code that turns a `Dish` into JSON, at compile time, from the field names and types. No reflection at run time, and no chance of a typo in a field name: the code is generated from the struct itself.
2. **`#[serde(rename_all = "camelCase")]`**: Rust names fields in `snake_case` (`price_naira`); JSON APIs usually use `camelCase` (`priceNaira`). This line converts every field's name. The API's clients never see Rust's naming style.
3. **`#[derive(Clone)]`** lets us copy a dish with `.clone()`, which we'll need to hand a copy out while the original stays in the menu.
4. **`i64` for the price.** Whole naira, as a signed 64-bit number. (Lesson 10 moves prices to kobo, as the Go and Express subjects do. Money is never a floating-point number.)

What clients send to add a dish is a **different type** from a dish:

```rust
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct NewDish {
    name: String,
    price_naira: i64,
    #[serde(default = "yes")]
    available: bool,
    #[serde(default)]
    special: bool,
}

fn yes() -> bool {
    true
}
```

1. **No `id`.** The server chooses IDs. If `NewDish` had an `id` field, a client could send one; because it doesn't, there's nowhere to put it.
2. **`#[derive(Deserialize)]`** writes the code that reads JSON into a `NewDish`. A missing `name` or `price_naira` is an error, because those fields aren't `Option`s.
3. **`#[serde(default)]`** says "if it's missing, use the type's default", which is `false` for `bool`. **`default = "yes"`** names a function to call instead, so a new dish is available unless the kitchen says otherwise.

And for changing part of a dish, every field is optional:

```rust
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct DishChanges {
    name: Option<String>,
    price_naira: Option<i64>,
    available: Option<bool>,
    special: Option<bool>,
}
```

`Option<T>` is either `Some(value)` or `None`. serde reads a missing field as `None`, so `{"available": true}` gives `DishChanges { available: Some(true), name: None, ... }`, and we change only what was sent. That's exactly what `PATCH` means.

Three types for one dish (what's stored, what's sent to add, what's sent to change) feels like a lot at first. It's what keeps each request honest: the type says exactly what a client may send, and the compiler won't let you mix them up.

## Step 3: a menu many requests can share
<!-- bite: b9570ddc-3d0c-4540-9de5-42fc5acb5293 -->

The menu needs to live somewhere every handler can reach, and change. Here's where Rust differs from every other language in these subjects.

Tokio runs requests on several threads at once, one per CPU core. Two `POST /menu` requests can really run at the same moment. In Go, two goroutines can change the same slice at once, and the program compiles; you find the bug with the race detector, if you think to run it ([[backend/frameworks/net-http/02-routing|lesson 2 of net/http]] does exactly that). In Rust, **a program where two threads can change the same value without a lock doesn't compile.** So we must say how the menu is shared, in its type:

```rust
use std::sync::{Arc, Mutex};

struct Menu {
    dishes: Vec<Dish>,
    next_id: u64,
}

type SharedMenu = Arc<Mutex<Menu>>;
```

Read `Arc<Mutex<Menu>>` from the inside out:

1. **`Menu`** is the data: the dishes, and the next ID to hand out.
2. **`Mutex<Menu>`**: the menu, behind a lock. The only way to reach the `Menu` inside is to call `.lock()`, which waits until no one else holds it. The type system makes it impossible to touch the dishes without the lock.
3. **`Arc<...>`**: a shared pointer, so every request can hold the same mutex. Cloning an `Arc` doesn't copy the menu; it adds one more owner of the same one.

In `main`:

```rust
let menu: SharedMenu = Arc::new(Mutex::new(Menu::new()));
```

and `Menu::new()` starts with three dishes:

```rust
impl Menu {
    fn new() -> Self {
        let dish = |id, name: &str, price_naira, available, special| Dish {
            id,
            name: name.to_string(),
            price_naira,
            available,
            special,
        };
        Menu {
            dishes: vec![
                dish(1, "Jollof rice", 1500, true, true),
                dish(2, "Beans and plantain", 1200, true, false),
                dish(3, "Egusi and pounded yam", 2500, false, false),
            ],
            next_id: 4,
        }
    }
}
```

(`dish` is a **closure**, a small function written inline, to save typing `name: ..., price_naira: ...` three times.)

`.with_state(menu)` hands it to the router, and any handler that wants it asks for it with the `State` extractor:

```rust
async fn specials(State(menu): State<SharedMenu>) -> Json<Vec<Dish>> {
    let menu = menu.lock().unwrap();
    Json(menu.dishes.iter().filter(|d| d.special).cloned().collect())
}
```

1. **`State(menu): State<SharedMenu>`** is a **pattern** in the argument list: the argument is a `State<SharedMenu>`, and `State(menu)` takes it apart, so `menu` is the `Arc<Mutex<Menu>>` inside. Every extractor is used this way.
2. **`menu.lock()`** waits for the lock and returns a **guard**. `.unwrap()` is because `lock` returns a `Result`: it fails only if another thread *panicked* while holding the lock, which would mean a bug elsewhere, so stopping is the right response.
3. **The guard unlocks when it goes away**, at the end of the function. There's no `unlock()` to forget, and no `defer` to write: when the guard's variable goes out of scope, Rust runs its clean-up (`Drop`) and the lock is released. This is called **RAII**, and you'll meet it again for database transactions in lesson 8.
4. **`.iter().filter(...).cloned().collect()`**: go through the dishes, keep the specials, copy each one, and gather them into a new `Vec<Dish>`. The copies leave the function; the originals stay in the menu.
5. **`Json(...)`** wraps the `Vec<Dish>`, and Axum turns it into a JSON response with `content-type: application/json`. Lesson 1's hand-written JSON is gone.

The state is given to the router *as a type*, so it's checked too: if a handler asks for `State<SomethingElse>`, the program doesn't compile. Nothing is looked up by name at run time.

### `std::sync::Mutex`, not Tokio's

Tokio has its own `tokio::sync::Mutex`, whose `lock()` is async. You might think an async program needs the async one. Usually it doesn't. **Use `std::sync::Mutex` when you only hold the lock for a moment and never `.await` while holding it**, which is the case for every handler here: lock, read or change the vector, done. It's faster and simpler. Tokio's mutex is for the rare case where you really must hold a lock across an `.await`. Step 7 shows what the compiler does if you hold `std`'s across an `.await` by mistake.

## Step 4: reading the path
<!-- bite: f7d7a645-869b-48f3-bee1-d382123dd575 -->

```rust
async fn get_dish(State(menu): State<SharedMenu>, Path(id): Path<u64>) -> Result<Json<Dish>, StatusCode> {
    let menu = menu.lock().unwrap();
    match menu.dishes.iter().find(|d| d.id == id) {
        Some(dish) => Ok(Json(dish.clone())),
        None => Err(StatusCode::NOT_FOUND),
    }
}
```

1. **`Path(id): Path<u64>`**: take the `{id}` from the path, and turn it into a `u64`. If it isn't one, the handler never runs:

   ```bash
   curl -i localhost:8080/menu/abc
   ```

   ```text
   HTTP/1.1 400 Bad Request
   content-type: text/plain; charset=utf-8

   Invalid URL: Cannot parse `abc` to a `u64`
   ```

   That's a **rejection**: the extractor's own error response. In the handler, `id` is *always* a valid `u64`. There's no "parse it and check the error" code, because there's no way to get past the extractor with a bad one. (Lesson 7 changes these plain-text rejections into the same JSON error shape as everything else.)
2. **The return type is `Result<Json<Dish>, StatusCode>`.** `Ok(Json(dish))` sends the dish with 200; `Err(StatusCode::NOT_FOUND)` sends 404. Axum implements `IntoResponse` for `Result` when both sides implement it, so a handler can return "this, or that error".
3. **`.find(|d| d.id == id)`** gives an `Option<&Dish>`: `Some` with a reference to the dish, or `None`. `match` handles both, and the compiler checks we didn't forget one. There's no way to use a dish we didn't find.

## Step 5: reading the query
<!-- bite: 8a303f24-7af6-4315-86ee-21d54afe6e36 -->

```rust
#[derive(Deserialize)]
struct ListParams {
    available: Option<bool>,
}

async fn list_dishes(State(menu): State<SharedMenu>, Query(params): Query<ListParams>) -> Json<Vec<Dish>> {
    let menu = menu.lock().unwrap();
    let dishes = menu
        .dishes
        .iter()
        .filter(|d| params.available.is_none_or(|want| d.available == want))
        .cloned()
        .collect();
    Json(dishes)
}
```

**`Query<ListParams>`** reads the query string into a struct with serde, the same way `Json` reads a body. `available` is an `Option<bool>`, so `/menu` gives `None` (show everything), `/menu?available=true` gives `Some(true)`, and `/menu?available=maybe` is rejected:

```text
HTTP/1.1 400 Bad Request

Failed to deserialize query string: available: provided string was not `true` or `false`
```

`is_none_or(|want| d.available == want)` reads as it sounds: "true if there's no filter, or if the dish matches it". (`Option::is_none_or` is in Rust 1.82 and later.)

## Step 6: reading the body, and the status codes
<!-- bite: 291afd08-5b97-4dc3-8d24-e5edfa7d1928 -->

**Adding a dish:**

```rust
async fn add_dish(State(menu): State<SharedMenu>, Json(new): Json<NewDish>) -> impl IntoResponse {
    let mut menu = menu.lock().unwrap();
    let dish = Dish {
        id: menu.next_id,
        name: new.name,
        price_naira: new.price_naira,
        available: new.available,
        special: new.special,
    };
    menu.next_id += 1;
    menu.dishes.push(dish.clone());

    let mut headers = HeaderMap::new();
    headers.insert(header::LOCATION, format!("/menu/{}", dish.id).parse().unwrap());
    (StatusCode::CREATED, headers, Json(dish))
}
```

1. **`Json(new): Json<NewDish>`** reads the body as JSON into a `NewDish`. It's the last argument, and that matters (step 7).
2. **`let mut menu`**: to change the menu, the guard must be `mut`. Rust makes you say when something will change.
3. **Taking the ID and adding one happen under the same lock**, so two requests at once can't both get ID 4. That isn't something you have to remember: there's no way to reach `next_id` without holding the lock.
4. **`-> impl IntoResponse`**: "some type that can be a response; you work out which". Handy when the real type is a long tuple.
5. **`(StatusCode::CREATED, headers, Json(dish))`**: 201, a `Location` header saying where the new dish lives, and the dish itself. `.parse()` turns the text into a `HeaderValue`, which can fail for text that isn't allowed in a header; ours is digits and slashes, so `unwrap` is safe.

What the `Json` extractor refuses, each with its own status, before `add_dish` runs:

| Request | Status | Why |
|---|---|---|
| No `content-type: application/json` | **415** Unsupported Media Type | "Expected request with `Content-Type: application/json`" |
| Body isn't JSON (`{"name":`) | **400** Bad Request | "Failed to parse the request body as JSON: ... EOF while parsing" |
| JSON, but the wrong shape (no `priceNaira`) | **422** Unprocessable Entity | "missing field `priceNaira`" |

Every one of those came from `curl` against this code. None needed a line of ours.

**Changing a dish:**

```rust
async fn change_dish(
    State(menu): State<SharedMenu>,
    Path(id): Path<u64>,
    Json(changes): Json<DishChanges>,
) -> Result<Json<Dish>, StatusCode> {
    let mut menu = menu.lock().unwrap();
    let dish = menu.dishes.iter_mut().find(|d| d.id == id).ok_or(StatusCode::NOT_FOUND)?;
    if let Some(name) = changes.name {
        dish.name = name;
    }
    if let Some(price) = changes.price_naira {
        dish.price_naira = price;
    }
    if let Some(available) = changes.available {
        dish.available = available;
    }
    if let Some(special) = changes.special {
        dish.special = special;
    }
    Ok(Json(dish.clone()))
}
```

1. **`iter_mut()`** goes through the dishes so they can be changed; `find` gives an `Option<&mut Dish>`.
2. **`.ok_or(StatusCode::NOT_FOUND)?`** turns `None` into `Err(NOT_FOUND)`, and `?` returns it straight away. The same `?` as lesson 1, for our own errors now.
3. **`if let Some(name) = changes.name`** runs only if the field was sent. Finding the dish and changing it happen under one lock, so nobody can remove it half-way.

**Removing a dish:**

```rust
async fn remove_dish(State(menu): State<SharedMenu>, Path(id): Path<u64>) -> StatusCode {
    let mut menu = menu.lock().unwrap();
    let before = menu.dishes.len();
    menu.dishes.retain(|d| d.id != id);
    if menu.dishes.len() < before { StatusCode::NO_CONTENT } else { StatusCode::NOT_FOUND }
}
```

`retain` keeps only the dishes that match, so a removed dish is simply not kept. A bare `StatusCode` is a response too: 204 with no body, or 404.

The status codes, all in one place:

| Status | When | Where it comes from |
|---|---|---|
| 200 OK | read or changed | `Json(...)` |
| 201 Created | dish added | `(StatusCode::CREATED, ...)` |
| 204 No Content | dish removed | `StatusCode::NO_CONTENT` |
| 400 Bad Request | path, query or body can't be read | the extractors |
| 404 Not Found | no such dish, or no such route | our handlers, and the router |
| 405 Method Not Allowed | wrong method for the path | the router |
| 415, 422 | wrong content type, wrong JSON shape | the `Json` extractor |

Try them all:

```bash
curl -s localhost:8080/menu
curl -s "localhost:8080/menu?available=false"
curl -s localhost:8080/menu/specials
curl -i -X POST localhost:8080/menu -H 'content-type: application/json' -d '{"name":"Moi moi","priceNaira":700}'
curl -i -X PATCH localhost:8080/menu/3 -H 'content-type: application/json' -d '{"available":true}'
curl -i -X DELETE localhost:8080/menu/4
```

The `POST` answers `201 Created` with `location: /menu/4`. Okay!!!!! A real, changing menu.

## Step 7: when the compiler says no
<!-- bite: 684d6e10-9095-479f-8c87-aac65c22387a -->

Two mistakes everyone makes in their first week with Axum. Make each on purpose, so you recognise them.

### Holding a lock across `.await`

Put an `.await` in `specials`, between taking the lock and finishing with it:

```rust
async fn specials(State(menu): State<SharedMenu>) -> Json<Vec<Dish>> {
    let menu = menu.lock().unwrap();
    tokio::time::sleep(Duration::from_millis(1)).await; // pretend this is a database call
    Json(menu.dishes.iter().filter(|d| d.special).cloned().collect())
}
```

The compiler refuses, with one of Rust's least helpful messages:

```text
error[E0277]: the trait bound `fn(State<Arc<Mutex<Menu>>>) -> ... {specials}: Handler<_, _>` is not satisfied
  = help: the trait `Handler<_, _>` is not implemented for fn item ...
note: required by a bound in `axum::routing::get`
```

"Your function isn't a handler." It doesn't say why. Now put **`#[axum::debug_handler]`** on the line above `async fn specials`, and build again:

```text
error: future cannot be sent between threads safely
note: future is not `Send` as this value is used across an await
    |         ---- has type `std::sync::MutexGuard<'_, Menu>` which is not `Send`
    |                                                  ^^^^^ await occurs here, with `menu` maybe used later
```

That's the real problem, in plain words. Here's what it means. At an `.await`, Tokio may pause this request and later carry on with it **on a different thread**. A `std::sync::MutexGuard` must be unlocked by the same thread that locked it, so it isn't allowed to move between threads (it isn't **`Send`**). Holding it across the `.await` would make the whole request un-movable, and Tokio requires every request to be movable. The compiler found it.

And it found something worse than a rule broken: if this *had* compiled, the lock would stay held for as long as the "database call" took. Every other request wanting the menu would queue behind it. The compiler stopped a slowdown you'd otherwise have found in production, at lunchtime.

The fix is to let go of the lock before the `.await`: do the work under the lock in a small block, and `.await` outside it. (Or, rarely, use `tokio::sync::Mutex`, whose guard *can* cross an `.await`.)

**Rule for the rest of the subject: the moment a handler won't compile, put `#[axum::debug_handler]` on it.** It changes nothing about how the code runs; it only makes the error readable. Take it off again when it's fixed, or leave it: it costs nothing in release builds.

### The body extractor must come last

Swap `change_dish`'s arguments so `Json` comes first, and add `#[axum::debug_handler]`:

```text
error: `Json<_>` consumes the request body and thus must be the last argument to the handler function
```

The body can only be read once (it arrives as a stream of bytes, and reading it uses them up). So Axum lets exactly one extractor read the body, and makes it go last. Extractors that only look at the path, the query, headers or state can go in any order before it.

## The Rust in this lesson
<!-- bite: 9b4ab1c7-5e0a-430c-bebe-30ac0095558d -->

1. **`#[derive(Serialize, Deserialize, Clone)]`**: derive macros that write code for a struct at compile time: conversions to and from JSON, and copying.
2. **`#[serde(rename_all = "camelCase")]`, `#[serde(default)]`, `#[serde(default = "yes")]`**: serde attributes that change field names and give missing fields a value.
3. **`Option<T>`**: `Some(value)` or `None`. serde reads a missing field as `None`.
4. **`Arc<Mutex<T>>`**: a value shared by many owners (`Arc`) behind a lock (`Mutex`), safe across threads.
5. **Guards and `Drop`**: `lock()` returns a guard; when it goes out of scope, the lock is released automatically.
6. **`type SharedMenu = Arc<Mutex<Menu>>;`**: a type alias, a short name for a long type.
7. **Patterns in arguments, `State(menu): State<SharedMenu>`**: take a wrapper apart right in the parameter list.
8. **Closures, `|d| d.special`**: small inline functions, used with iterator methods.
9. **Iterators: `.iter()`, `.iter_mut()`, `.filter()`, `.find()`, `.cloned()`, `.collect()`, `.retain()`**: go through a collection, choose, copy and gather, without writing loops.
10. **`match` and `if let`**: handle each case of an `Option` or `Result`; the compiler checks none is missed.
11. **`Result<T, E>` as a return type**, and **`.ok_or(...)?`**: turn a missing value into an error and return it early.
12. **`impl IntoResponse`**: "a type that implements this trait", without naming it.
13. **`let mut`**: a variable that will change. Without `mut`, it can't.
14. **`Send`**: a marker trait meaning "can be moved to another thread". Tokio needs every request's future to be `Send`, which is why a lock guard can't be held across `.await`.
15. **`#[axum::debug_handler]`**: an attribute that turns Axum's "not a handler" error into the real reason.

## Your project so far
<!-- bite: a74ee31a-8ee2-4530-a1ee-93177fcaf8ff -->

```text
mama-put/
├── Cargo.toml      ← axum (with macros), tokio, tower-http, serde
├── Cargo.lock
└── src/
    └── main.rs     ← Dish, NewDish, DishChanges, ListParams; Menu behind Arc<Mutex<>>;
                       six routes with Path, Query, Json and State; 200, 201, 204, 404
```

## Common mistakes
<!-- bite: 4637da7f-b920-486d-a0a6-b143d3cd3c15 -->

1. **One type for everything.** A `Dish` with an `id` used for input lets clients choose IDs. Separate types for what's stored, added and changed.
2. **`:id` instead of `{id}`.** A start-up panic in Axum 0.8, with a message that says so.
3. **The body extractor not last.** Only one extractor may read the body, and it must be the last argument.
4. **A `std::sync::Mutex` guard held across `.await`.** It doesn't compile, and if it did, every request would queue behind the slow one. Lock, do the work, unlock, then await.
5. **Reaching for `tokio::sync::Mutex` by default.** It's slower; use it only when a lock really must be held across an `.await`.
6. **Reading "Handler is not implemented" and guessing.** Put `#[axum::debug_handler]` on the handler and read the real error.
7. **Returning the menu's own dishes instead of copies.** You can't anyway: the compiler won't let a reference outlive the lock. That's why we `clone`.
8. **Floating-point prices.** Money is a whole number of the smallest unit.

## Check your understanding
<!-- bite: a176d7dc-ccac-46f1-8d09-3c9a6f352c64 -->

1. Why does `GET /menu/specials` reach `specials` and not `get_dish`, even though `{id}` could match `specials`?
2. A client calls `GET /menu/abc`. What runs, what's sent back, and why does `get_dish` never need to check that `id` is a number?
3. Read `Arc<Mutex<Menu>>` from the inside out, and say what each layer is for.
4. Why does `NewDish` have no `id` field?
5. What does the compiler say when a `MutexGuard` is held across an `.await`, in plain words, and what would have happened at lunchtime if it had compiled?
6. Why must `Json<DishChanges>` be the last argument of `change_dish`?

<details>
<summary>Answers, after your attempt</summary>

1. Axum's router always prefers a path written out exactly to one with a capture, whatever order the routes were added in. `/menu/specials` matches exactly, so it wins.
2. The `Path<u64>` extractor tries to turn `abc` into a `u64`, fails, and sends a 400 with "Cannot parse `abc` to a `u64`". `get_dish` is never called. Inside it, `id` can only ever be a valid `u64`, because there's no way past the extractor with anything else.
3. `Menu` is the data. `Mutex<Menu>` puts it behind a lock, so the only way to reach the dishes is to hold the lock, one request at a time. `Arc<...>` lets every request share the same mutex: cloning it adds an owner, not a copy of the menu.
4. Because the server chooses IDs. With no `id` field in the input type, a client has nowhere to send one, so they can't pick an ID or overwrite another dish.
5. That the request's future can't be sent between threads, because a `std::sync::MutexGuard`, which isn't `Send`, is still held when the `.await` happens. If it had compiled, the lock would stay held for the whole slow call, and every other request needing the menu would wait behind it.
6. Because the body can only be read once, so only one extractor may consume it, and Axum makes that one go last. The others (state, path) only look at parts of the request that can be read any number of times.

</details>

## Practice
<!-- bite: fb54399d-58e8-4986-8236-fefd84f69aaa -->

1. Add `GET /menu/{id}/price` that returns just `{"priceNaira": 1500}`, using a small struct with `#[derive(Serialize)]`.
2. Add `?special=true` to `GET /menu` alongside `available`, and make both filters work together.
3. Refuse a `POST /menu` with an empty name or a price of 0 or less, with 422 and no body (`StatusCode::UNPROCESSABLE_ENTITY`). Lesson 6 does this properly; do it by hand once.
4. Make `remove_dish` return the removed dish with 200 instead of 204, and decide which you prefer for an API, and why.
5. Hold the lock across an `.await` on purpose, read both versions of the error, then fix it with a block: `let specials = { let menu = menu.lock().unwrap(); ... };` then the `.await`.

**Done when** all six routes work with `curl`, a bad ID gets 400, a missing dish gets 404, a POST without `content-type` gets 415 and one without a price gets 422, a POST answers 201 with a `Location` header, and you've seen and fixed both compiler errors from step 7.

## Before moving on
<!-- bite: baf6c374-abba-4458-a10d-6a428dfc7ff5 -->

The menu is a real REST resource now: six routes, each handler reading exactly what its arguments say, every bad request rejected before it reaches your code, and a menu shared between requests in a way the compiler has checked. You've also met Rust's most famous habit: refusing to compile something that would have been a bug.

Every request is handled, but none is *recorded*: nothing says what came in, how long it took, or what went wrong. And anyone can change the menu. Next lesson: middleware, the layers that wrap every request, for logging, catching panics and keeping the kitchen's routes for the kitchen.

## Related
<!-- bite: 44154353-df8f-4523-930c-5889f0b53cc5 -->

- [[backend/frameworks/axum/03-middleware|Next: Middleware]]
- [[backend/frameworks/net-http/02-routing|The same lesson in net/http]] — a mutex you must remember, and the race detector to prove it
- [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers and Interior Mutability]] — `Arc`, `Mutex` and why they fit together
- [[backend/02-api-design/index|API Design]] — resources, methods and status codes

## About this lesson
<!-- bite: bcd44c5c-1571-4e95-9974-f707a0fe1250 -->

**Level:** Beginner → Intermediate. Lesson 2 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later, Axum 0.8 with its `macros` feature, and serde 1. Covers REST routes in a `Router` with method chaining, `{id}` captures and their start-up checks, exact paths beating captures, serde derives with renaming and defaults, separate types for stored, new and changed data, the `Path`, `Query`, `Json` and `State` extractors and their rejections (400, 415, 422), shared state with `Arc<Mutex<>>` and guards released by `Drop`, `std::sync::Mutex` versus Tokio's, `Result` and tuples as responses with 201 and `Location`, 204 and 404, and the two classic compile errors (a guard held across `.await`, and a body extractor that isn't last) made readable with `#[axum::debug_handler]`.
