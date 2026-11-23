---
id: 3a6f8bd4-1f7b-4813-89d1-97b6e6be1c2c
---

# Structuring an Axum Service

**Structuring a service means deciding which code lives in which file, so each part has one job and you can find it, change it and test it without touching the rest.** In Rust, the tool for this is the **module**: a named box of code with a wall around it. Inside the wall, everything can see everything. From outside, you only see what the module chooses to make `pub`.

## Before you start
<!-- bite: 09958f10-0d0e-4bc5-a0bb-886187ec480c -->

You should have:

1. Finished [[backend/frameworks/axum/03-middleware|lesson 3]], so Mama Put API has the six menu routes, a logger, a panic catcher and the staff key, all in `main.rs`.
2. Read, or at least skimmed, [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers: Controllers, Services and Repositories]]. This lesson puts that idea into Rust.

After this lesson you will be able to:

1. Split a crate into modules with `mod`, and say how Rust finds the file for each one.
2. Put the app in a **library crate** (`lib.rs`) and keep `main.rs` to a few lines, and say why.
3. Split a feature into a model, a store, a service and handlers, each with one job.
4. Give each feature its own error enum, and turn it into a status code in one place, with `IntoResponse`.
5. Decide what a module shows the outside with `pub` and `pub use`, and read the two privacy errors.
6. Explain why Rust, unlike Go, will happily let two modules use each other, and what you do about it.

## What to install
<!-- bite: aa9418ea-a420-40a9-a48f-ce246b928522 -->

```bash
cargo add thiserror
```

**`thiserror`** writes the boring part of an error type for you. You write an enum with a message on each variant; it writes the code that prints the message and makes the enum a proper Rust error. Almost every Rust library uses it.

## Where we stopped
<!-- bite: 81661ba0-eeb0-4875-9f5a-4f12d1a7f349 -->

Everything is in `main.rs`: the dish types, the menu behind `Arc<Mutex<>>`, six handlers, three middleware and `main`. That's well over two hundred lines. Orders come in this lesson too, and they would double it.

And there's no line between HTTP and Mama's rules. `add_dish` takes a dish with a price of ₦0 and stores it happily, because there's nowhere obvious for a rule to live. If there were, it would end up inside a handler, and the background jobs in lesson 18, which have no HTTP request, couldn't use it.

## The kid version
<!-- bite: b8a7ee75-3df1-4af6-bcb8-86f546152d22 -->

When Mama started, she did everything at one table: took the money, cooked, served, washed plates. When the queue grew, she gave each job its own place. The money box by the front. The pots at the back. The plates in a basin to the side.

Nothing about the food changed. But now when the money is short, she knows where to look, and she can hire someone for the plates without teaching them to cook.

Each place is a module. The front of each place, the part customers can see, is what the module makes `pub`. The back of it is private.

**Where the picture stops working.** In Mama's stall, the pots could walk over and use the money box, and the money box could use the pots, and nobody would stop them. Rust is the same, and that surprises people coming from Go: inside one crate, the compiler doesn't care which way modules use each other. Keeping the arrows pointing one way is your job (the section near the end).

## Terms used in this lesson
<!-- bite: 2e0970f8-d217-420e-99c7-2ed9e9fec43a -->

1. **Crate**: This is one thing the Rust compiler builds: a program (a **binary crate**) or a library other code uses (a **library crate**). One package, one `Cargo.toml`, can hold one library and any number of binaries.
2. **Module**: This is a named part of a crate, with its own names inside it, declared with `mod`. A module can live in its own file, and can hold other modules.
3. **Path**: This is how you name something in another module, with `::` between the parts, like `crate::menu::MenuService`.
4. **`pub`**: This is the word that makes a module, struct, field, function or method visible outside the module it's in. Without it, everything is private.
5. **Re-export**: This is `pub use`, which takes a name from deep inside a module and offers it one level up, so the outside sees `menu::MenuService` instead of `menu::service::MenuService`.
6. **Handler layer**: This is the code that speaks HTTP. It reads the request, calls the service, and turns the result into a response. It knows about status codes and JSON; it doesn't know Mama's rules.
7. **Service**: This is the code that holds the business rules: "a dish needs a price", "at most 20 plates per order". It knows nothing about HTTP.
8. **Store**: This is the code that keeps and finds data, also called a **repository**. Today it's in memory; in lesson 8 it's PostgreSQL. Nothing above it should care which.

## The layout
<!-- bite: 73e774b7-2d9a-419e-9e28-b0bf94f5c3a5 -->

Here's where we're going. Don't make the files yet; read the shape first.

```text
mama-put/
├── Cargo.toml
└── src/
    ├── main.rs            ← the program: reads STAFF_KEY, starts the server
    ├── lib.rs             ← the library: declares the modules, builds the app
    ├── http.rs            ← StaffKey and the middleware every feature uses
    ├── menu/
    │   ├── mod.rs         ← what the menu module shows the outside
    │   ├── model.rs       ← Dish, NewDish, DishChanges
    │   ├── store.rs       ← MenuStore: keeps the dishes
    │   ├── service.rs     ← MenuService and MenuError: the menu's rules
    │   └── handlers.rs    ← the menu's routes, and MenuError as a status code
    └── orders/
        ├── mod.rs
        ├── model.rs
        ├── store.rs
        ├── service.rs
        └── handlers.rs
```

Each part is there for a reason.

**`main.rs` and `lib.rs` side by side** make two crates in one package. `lib.rs` is the library: all of Mama Put lives in it. `main.rs` is the program: a few lines that read settings and start the library's app. Step 1 explains why that split is worth it.

**`menu/` and `orders/`** are the features. Everything about the menu lives together: its types, its store, its rules and its routes. This is **organising by feature**. The opposite, folders called `handlers/`, `services/` and `models/` each holding a bit of every feature, means one change to the menu touches four folders. [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|Organising by Layer vs by Feature]] compares the two.

**Inside each feature, four files, one job each.** The model is the data's shape. The store keeps it. The service holds the rules. The handlers speak HTTP.

**`http.rs`** holds what every feature's HTTP code needs: the staff key and the middleware. It knows nothing about dishes or orders.

Notice what's **not** there: no `utils.rs` or `common.rs`. A module's name should say what it gives you. "Utils" says nothing, so everything ends up in it. And no `models/` module with every type in the app: a type lives with the feature that owns it, so a dish is `menu::Dish`.

## Step 1: a library crate, and a short main
<!-- bite: 6639ca0b-8806-4e8c-9496-e47117db0d11 -->

Make the folders, and an empty `lib.rs`:

```bash
mkdir -p src/menu src/orders
touch src/lib.rs
```

That's all it takes. Cargo sees `src/lib.rs` and builds a library crate called `mama_put` (the package's name, with the `-` turned into `_`, because `-` isn't allowed in a Rust name). `src/main.rs` is still the program, and it can use the library like any other crate: `mama_put::app(...)`.

Why bother? Three reasons, and each comes up later:

1. **Tests.** The tests in lesson 16 live in their own crate, under `tests/`, and they need to build the whole app without starting a server. They can call `mama_put::app(...)` only if it's in a library. A binary crate can't be used by anything.
2. **More programs.** Lesson 8 adds a program that runs database migrations, and lesson 29 a second service. Each is a small file under `src/bin/`, using the same library.
3. **`main.rs` only sees `pub`.** The program is outside the library's wall, so it can only use what the library made public. That keeps you honest about what's really the library's front door.

## Step 2: modules, and how Rust finds them
<!-- bite: d7dc1ee5-ad62-4c07-9a18-5f3133193c22 -->

In Go, a folder *is* a package. In Rust, a file is nothing until a module declares it. At the top of `lib.rs`:

```rust
pub mod http;
pub mod menu;
pub mod orders;
```

**`mod menu;`** with a semicolon means "there's a module called `menu`; its code is in another file". Rust looks for it in one of two places:

1. **`src/menu.rs`**, or
2. **`src/menu/mod.rs`**.

We use `mod.rs`, so the whole feature sits in one folder. (Some people prefer `src/menu.rs` beside a `src/menu/` folder, which Rust also allows. Pick one and stick to it.)

**`pub mod`** means the module itself can be seen from outside the crate, by `main.rs`. Without `pub`, `main.rs` couldn't write `mama_put::http::StaffKey`.

Then `src/menu/mod.rs` declares the menu's own four modules:

```rust
//! The menu: dishes, and the rules for changing them.

mod handlers;
mod model;
mod service;
mod store;

pub use handlers::router;
pub use model::{Dish, DishChanges, NewDish};
pub use service::{MenuError, MenuService};
pub use store::MenuStore;
```

1. **`mod handlers;`** inside `menu/mod.rs` makes Rust look for `src/menu/handlers.rs`. Modules nest the way the folders do.
2. **The four modules are private** (no `pub`). Nobody outside the menu can write `menu::store::...`.
3. **`pub use`** re-exports the names the outside needs, one level up. Outside, it's `menu::MenuService`, as if the file split didn't exist. You can move code between `service.rs` and `store.rs` tomorrow, and nothing outside the menu changes.
4. **`//!`** is a doc comment for the module it's in. `///` documents the thing below it. `cargo doc --open` turns both into web pages.

So `mod.rs` is the menu's front counter. It's the one file you read to learn what the menu offers.

## Step 3: the model
<!-- bite: 62c1eda0-65f1-4aa7-974b-9e6965ed1912 -->

`src/menu/model.rs` is the three types from lesson 2, moved, with `pub` added:

```rust
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Dish {
    pub id: u64,
    pub name: String,
    pub price_naira: i64,
    pub available: bool,
    pub special: bool,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NewDish {
    pub name: String,
    pub price_naira: i64,
    #[serde(default = "yes")]
    pub available: bool,
    #[serde(default)]
    pub special: bool,
}

fn yes() -> bool {
    true
}

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DishChanges {
    pub name: Option<String>,
    pub price_naira: Option<i64>,
    pub available: Option<bool>,
    pub special: Option<bool>,
}
```

1. **`pub` on the struct, and `pub` on each field.** In Rust, a struct's fields are private even when the struct is public. `pub struct Dish` lets other modules *name* a `Dish`; `pub id` lets them read its `id`. These are plain data, read by the store, the service and the orders feature, so every field is `pub`.
2. **`yes` has no `pub`.** Only serde, inside this file, calls it.
3. **`Debug` and `PartialEq`** are new: `Debug` lets you print a value with `{:?}`, and `PartialEq` lets you compare two with `==`. The tests in lesson 16 need both.

## Step 4: the store
<!-- bite: 82edb638-402c-48f0-bced-4001c6664cd7 -->

`src/menu/store.rs` is the `Menu` from lesson 2, renamed `MenuStore`, with the lock moved *inside* it:

```rust
use std::sync::Mutex;

use super::model::{Dish, DishChanges, NewDish};

/// Dishes kept in memory, safe to use from many requests at once.
pub struct MenuStore {
    inner: Mutex<Inner>,
}

struct Inner {
    dishes: Vec<Dish>,
    next_id: u64,
}

impl MenuStore {
    pub fn new(dishes: Vec<Dish>) -> Self {
        let next_id = dishes.iter().map(|d| d.id).max().unwrap_or(0) + 1;
        MenuStore { inner: Mutex::new(Inner { dishes, next_id }) }
    }

    pub fn with_sample_dishes() -> Self {
        let dish = |id, name: &str, price_naira, available, special| Dish {
            id,
            name: name.to_string(),
            price_naira,
            available,
            special,
        };
        MenuStore::new(vec![
            dish(1, "Jollof rice", 1500, true, true),
            dish(2, "Beans and plantain", 1200, true, false),
            dish(3, "Egusi and pounded yam", 2500, false, false),
        ])
    }

    pub fn list(&self) -> Vec<Dish> {
        self.inner.lock().unwrap().dishes.clone()
    }

    pub fn find(&self, id: u64) -> Option<Dish> {
        self.inner.lock().unwrap().dishes.iter().find(|d| d.id == id).cloned()
    }

    pub fn add(&self, new: NewDish) -> Dish {
        let mut inner = self.inner.lock().unwrap();
        let dish = Dish {
            id: inner.next_id,
            name: new.name,
            price_naira: new.price_naira,
            available: new.available,
            special: new.special,
        };
        inner.next_id += 1;
        inner.dishes.push(dish.clone());
        dish
    }

    pub fn change(&self, id: u64, changes: DishChanges) -> Option<Dish> {
        let mut inner = self.inner.lock().unwrap();
        let dish = inner.dishes.iter_mut().find(|d| d.id == id)?;
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
        Some(dish.clone())
    }

    pub fn remove(&self, id: u64) -> bool {
        let mut inner = self.inner.lock().unwrap();
        let before = inner.dishes.len();
        inner.dishes.retain(|d| d.id != id);
        inner.dishes.len() < before
    }
}
```

1. **`use super::model::...`**: `super` means "the module above this one", here `menu`. So `super::model` is the menu's model module, the file beside this one.
2. **`Inner` is private**, and so is the `inner` field. Nobody outside this file knows there's a `Vec` and a `Mutex` in here. In lesson 8, `MenuStore` holds a database pool instead, and nothing outside this file will notice.
3. **Every method takes `&self`, even the ones that change things.** You'd expect `add` to need `&mut self`. It doesn't, because the `Mutex` hands out a changeable guard to whoever holds the lock. That's called **interior mutability**: the store looks unchangeable from outside, and is safe to share, because the lock guards every change inside.
4. **The lock is taken and let go inside each method.** No caller can hold it too long, or across an `.await`, because no caller ever sees it. The `Send` error from lesson 2 can't happen to code that never touches the guard.
5. **The `?` in `change`**: `find` gives an `Option`, and `?` on an `Option` returns `None` straight away if there's nothing there. The same `?` as for `Result`.
6. **`new` takes the dishes**, and `with_sample_dishes` gives Mama's three. The store doesn't decide what Mama sells; whoever builds it does.

The store does one job: keep dishes and find them. It has no rules. It would store a dish with a price of ₦0 without a word. Rules are the next layer's job.

## Step 5: the service, and an error enum
<!-- bite: ef25d17f-8640-4d96-b5e4-c3a1eb54e7bb -->

`src/menu/service.rs`:

```rust
use std::sync::Arc;

use super::{
    model::{Dish, DishChanges, NewDish},
    store::MenuStore,
};

/// Everything that can go wrong with the menu, as far as Mama's rules are concerned.
#[derive(Debug, thiserror::Error, PartialEq)]
pub enum MenuError {
    #[error("there's no dish {0}")]
    NotFound(u64),
    #[error("a dish needs a name")]
    NoName,
    #[error("a price must be more than ₦0")]
    BadPrice,
}

/// The menu's rules. Knows nothing about HTTP. Cheap to clone: every clone shares one store.
#[derive(Clone)]
pub struct MenuService {
    store: Arc<MenuStore>,
}

impl MenuService {
    pub fn new(store: MenuStore) -> Self {
        MenuService { store: Arc::new(store) }
    }

    pub fn list(&self, available: Option<bool>) -> Vec<Dish> {
        let mut dishes = self.store.list();
        dishes.retain(|d| available.is_none_or(|want| d.available == want));
        dishes
    }

    pub fn specials(&self) -> Vec<Dish> {
        let mut dishes = self.store.list();
        dishes.retain(|d| d.special && d.available);
        dishes
    }

    pub fn get(&self, id: u64) -> Result<Dish, MenuError> {
        self.store.find(id).ok_or(MenuError::NotFound(id))
    }

    pub fn add(&self, mut new: NewDish) -> Result<Dish, MenuError> {
        new.name = new.name.trim().to_string();
        if new.name.is_empty() {
            return Err(MenuError::NoName);
        }
        if new.price_naira <= 0 {
            return Err(MenuError::BadPrice);
        }
        Ok(self.store.add(new))
    }

    pub fn change(&self, id: u64, changes: DishChanges) -> Result<Dish, MenuError> {
        if changes.price_naira.is_some_and(|p| p <= 0) {
            return Err(MenuError::BadPrice);
        }
        if changes.name.as_deref().is_some_and(|n| n.trim().is_empty()) {
            return Err(MenuError::NoName);
        }
        self.store.change(id, changes).ok_or(MenuError::NotFound(id))
    }

    pub fn remove(&self, id: u64) -> Result<(), MenuError> {
        if self.store.remove(id) { Ok(()) } else { Err(MenuError::NotFound(id)) }
    }
}
```

Read through it and look for anything about HTTP. There's none: no `StatusCode`, no `Json`, no extractors. The service takes plain Rust values and returns plain Rust values and errors. A background job, a test, or the GraphQL API in lesson 21 can call `MenuService::add`, and "a dish needs a price" holds for all of them.

### The error enum

**`MenuError` lists every way the menu's rules can say no.** Each failure is a variant, and `NotFound` carries the id that wasn't found. Because it's an enum, code that handles a `MenuError` with `match` must handle every variant, or it doesn't compile. Add a fourth rule next month, and the compiler shows you every place that needs to decide what it means.

**`#[derive(thiserror::Error)]`** and the **`#[error("...")]`** lines write the rest: `MenuError::NotFound(4).to_string()` is `"there's no dish 4"` (`{0}` is the variant's first value). Without `thiserror`, that's an `impl Display` and an `impl Error` by hand, about fifteen lines.

**Every method that can fail returns `Result<_, MenuError>`.** `get` turns the store's `Option` into a `Result` with `ok_or`: `Some(dish)` becomes `Ok(dish)`, and `None` becomes `Err(MenuError::NotFound(id))`.

### Why `Arc<MenuStore>`, and `Clone`

Every handler gets its own copy of the service (that's how `State` works: it clones what you gave `with_state`). We want every copy to share **one** store, not each have a fresh one with Mama's three sample dishes. So the service holds an `Arc<MenuStore>`, and `#[derive(Clone)]` clones the `Arc`: one more owner of the same store, not a copy of it.

That's the `Arc<Mutex<Menu>>` from lesson 2, split in two. The `Mutex` is inside the store, because the store is what needs locking. The `Arc` is in the service, because the service is what gets shared.

### New rules, now they have a home

Three rules arrived with the service, and each was hard to place before:

1. **A dish needs a name.** `"   "` doesn't count, so the name is trimmed first.
2. **A price must be more than ₦0.**
3. **A sold-out special isn't a special.** `specials` leaves out dishes that aren't available.

`change` checks the same two rules on the fields that were sent. `is_some_and(|p| p <= 0)` reads as it sounds: "there is a price, and it's ₦0 or less". `as_deref()` turns an `Option<String>` into an `Option<&str>`, so we can look at the name without taking it out of `changes`.

## Step 6: the handlers, and errors as responses
<!-- bite: 2ea6de8e-f241-4067-b6a3-05a555f524b9 -->

`src/menu/handlers.rs`:

```rust
use axum::{
    Json, Router,
    extract::{Path, Query, State},
    http::{StatusCode, header},
    middleware,
    response::{IntoResponse, Response},
    routing::{get, patch, post},
};
use serde::Deserialize;

use super::{
    model::{Dish, DishChanges, NewDish},
    service::{MenuError, MenuService},
};
use crate::http::{StaffKey, kitchen_only};

/// The menu's routes: reads for everyone, writes for the kitchen.
pub fn router(menu: MenuService, staff_key: StaffKey) -> Router {
    let public = Router::new()
        .route("/menu", get(list))
        .route("/menu/specials", get(specials))
        .route("/menu/{id}", get(get_one));

    let kitchen = Router::new()
        .route("/menu", post(add))
        .route("/menu/{id}", patch(change).delete(remove))
        .route_layer(middleware::from_fn_with_state(staff_key, kitchen_only));

    public.merge(kitchen).with_state(menu)
}

impl IntoResponse for MenuError {
    fn into_response(self) -> Response {
        let status = match self {
            MenuError::NotFound(_) => StatusCode::NOT_FOUND,
            MenuError::NoName | MenuError::BadPrice => StatusCode::UNPROCESSABLE_ENTITY,
        };
        (status, self.to_string()).into_response()
    }
}

#[derive(Deserialize)]
struct ListParams {
    available: Option<bool>,
}

async fn list(State(menu): State<MenuService>, Query(params): Query<ListParams>) -> Json<Vec<Dish>> {
    Json(menu.list(params.available))
}

async fn specials(State(menu): State<MenuService>) -> Json<Vec<Dish>> {
    Json(menu.specials())
}

async fn get_one(State(menu): State<MenuService>, Path(id): Path<u64>) -> Result<Json<Dish>, MenuError> {
    Ok(Json(menu.get(id)?))
}

async fn add(State(menu): State<MenuService>, Json(new): Json<NewDish>) -> Result<impl IntoResponse, MenuError> {
    let dish = menu.add(new)?;
    let location = [(header::LOCATION, format!("/menu/{}", dish.id))];
    Ok((StatusCode::CREATED, location, Json(dish)))
}

async fn change(
    State(menu): State<MenuService>,
    Path(id): Path<u64>,
    Json(changes): Json<DishChanges>,
) -> Result<Json<Dish>, MenuError> {
    Ok(Json(menu.change(id, changes)?))
}

async fn remove(State(menu): State<MenuService>, Path(id): Path<u64>) -> Result<StatusCode, MenuError> {
    menu.remove(id)?;
    Ok(StatusCode::NO_CONTENT)
}
```

A few things to see here.

**`router` is the feature's one way in.** The handlers are private (`async fn list`, no `pub`). From outside, the menu's HTTP side is a single function: "give me a service and the staff key, and I'll give you a router with the menu's routes". The public and kitchen routers from lesson 3 now live here, with the routes they guard.

**`.with_state(menu)` is called inside the feature.** It returns a `Router` whose state is already filled in, so the app can merge it with routers that have different state (the orders router holds an `OrderService`). Each feature gets exactly what it needs and nothing else. Lesson 5 looks at the other way: one `AppState` for everything.

**`impl IntoResponse for MenuError` is the one place a menu error becomes a status code.** The service says `NotFound`; only this `match` knows that means 404. Then every handler can return `Result<_, MenuError>`, and Axum turns an `Err` into a response by calling `into_response`. No handler writes a status code for an error.

**422 for a broken rule.** That matches what the `Json` extractor already says for a body of the wrong shape (lesson 2): the request was read fine, but what it asks for isn't allowed.

**The `?` does the work.** In `get_one`, `menu.get(id)?` either gives the dish, or returns the `MenuError` from the handler right there. Each handler is one line of real work: read, call, answer.

**The impl lives in `handlers.rs`, beside the HTTP code.** Rust lets you write `impl SomeTrait for SomeType` in any module of the crate that owns either one, so we put it where HTTP lives, and `service.rs` never mentions `IntoResponse`. Look at the `use` lines at the top of each file: only `handlers.rs` imports from `axum`.

**`[(header::LOCATION, ...)]`**: an array of (name, value) pairs is a response part too, so this is a shorter way to set the `Location` header than lesson 2's `HeaderMap`.

## Step 7: the wall, and the two errors you'll meet
<!-- bite: 1b66327d-2cf2-4eab-b742-6ded42a92bd3 -->

Try reaching through the wall. In `specials`, use the store directly, skipping the service:

```rust
Json(menu.store.list())
```

```text
error[E0616]: field `store` of struct `MenuService` is private
  --> src/menu/handlers.rs:52:15
   |
52 |     Json(menu.store.list())
   |               ^^^^^ private field
```

`handlers.rs` and `service.rs` are both in the menu, but they're different modules, and the `store` field is private to `service`. A handler can't skip the rules, even by accident. Put it back.

Now, in `lib.rs`, try naming the store by its full path:

```rust
use menu::store::MenuStore;
```

```text
error[E0603]: module `store` is private
 --> src/lib.rs:6:11
  |
6 | use menu::store::MenuStore;
  |           ^^^^^ private module
  |
note: the module `store` is defined here
 --> src/menu/mod.rs:6:1
  |
6 | mod store;
  | ^^^^^^^^^^
```

The way in is the front counter: `menu::MenuStore`, which `mod.rs` re-exported.

The rule that explains both: **in Rust, everything is private to the module it's written in, until you write `pub`.** A child module can see its parent's private things (`handlers` can use whatever `menu/mod.rs` declares), but not the other way round, and not its siblings' private things. Start with nothing `pub`, and add it only when the compiler tells you someone needs it.

(Between private and `pub` there's **`pub(crate)`**: "visible anywhere in this crate, but not to `main.rs` or anyone using the library". Useful for helpers several features share that aren't part of the library's front door.)

## Step 8: the orders feature
<!-- bite: d091a4eb-aec0-4f3c-b521-b8c36f274be2 -->

Orders have the same four files and the same shape. `src/orders/model.rs`:

```rust
use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Status {
    Pending,
    Ready,
    Collected,
}

#[derive(Clone, Debug, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Order {
    pub id: u64,
    pub dish_id: u64,
    pub quantity: u32,
    pub total_naira: i64,
    pub status: Status,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NewOrder {
    pub dish_id: u64,
    pub quantity: u32,
}

#[derive(Debug, Deserialize)]
pub struct StatusChange {
    pub status: Status,
}
```

1. **`Status` is an enum**, so an order's status can only ever be one of the three. `{"status": "cooked"}` is rejected by the `Json` extractor with a 422, before any of our code runs.
2. **`#[serde(rename_all = "lowercase")]`** writes `Status::Ready` as `"ready"` in JSON.
3. **`PartialOrd, Ord`** make the variants comparable, **in the order they're written**: `Pending < Ready < Collected`. So "is this a step forward?" is just `to > current`. Reorder the variants and you change the rule, so leave a comment if you ever do.
4. **`Copy`**: a `Status` is tiny, so it's copied instead of moved, like a number.
5. **`NewOrder` has no `total_naira`.** The client says what dish and how many. The server works out the price. A customer who sends `"totalNaira": 1` doesn't get a cheap lunch: there's no field for serde to put it in.

`src/orders/service.rs`:

```rust
use std::sync::Arc;

use super::{
    model::{NewOrder, Order, Status},
    store::OrderStore,
};
use crate::menu::MenuService;

#[derive(Debug, thiserror::Error, PartialEq)]
pub enum OrderError {
    #[error("you can order between 1 and 20 plates")]
    BadQuantity,
    #[error("there's no dish {0}")]
    NoSuchDish(u64),
    #[error("that dish isn't available right now")]
    DishUnavailable,
    #[error("there's no order {0}")]
    NotFound(u64),
    #[error("an order can't go from {from:?} back to {to:?}")]
    BadStatusChange { from: Status, to: Status },
}

#[derive(Clone)]
pub struct OrderService {
    store: Arc<OrderStore>,
    menu: MenuService,
}

impl OrderService {
    pub fn new(store: OrderStore, menu: MenuService) -> Self {
        OrderService { store: Arc::new(store), menu }
    }

    pub fn place(&self, new: NewOrder) -> Result<Order, OrderError> {
        if !(1..=20).contains(&new.quantity) {
            return Err(OrderError::BadQuantity);
        }
        let dish = self.menu.get(new.dish_id).map_err(|_| OrderError::NoSuchDish(new.dish_id))?;
        if !dish.available {
            return Err(OrderError::DishUnavailable);
        }
        let total = dish.price_naira * i64::from(new.quantity);
        Ok(self.store.insert(dish.id, new.quantity, total))
    }

    pub fn get(&self, id: u64) -> Result<Order, OrderError> {
        self.store.find(id).ok_or(OrderError::NotFound(id))
    }

    /// Moves an order forward: pending → ready → collected. Never back.
    pub fn set_status(&self, id: u64, to: Status) -> Result<Order, OrderError> {
        match self.store.set_status(id, to, |current| to > current) {
            None => Err(OrderError::NotFound(id)),
            Some(Err(from)) => Err(OrderError::BadStatusChange { from, to }),
            Some(Ok(order)) => Ok(order),
        }
    }
}
```

1. **`use crate::menu::MenuService`**: `crate` means "the top of this crate", so this is the path from `lib.rs` down. The orders feature uses the menu through its front counter, like anyone else.
2. **`OrderService` holds a `MenuService`.** Placing an order needs the menu. It's a clone, so it shares the same store as the menu's routes: a dish the kitchen marks sold out is sold out for orders straight away.
3. **`(1..=20).contains(&new.quantity)`**: `1..=20` is the range from 1 to 20, including 20. The `!` in front means "not in it".
4. **`.map_err(|_| OrderError::NoSuchDish(...))?`** changes the menu's error into an order error, then `?` returns it. The orders feature doesn't pass `MenuError` up, because "no such dish" is something *placing an order* can go wrong with, in the order's own words. The handler only needs to know `OrderError`.
5. **`i64::from(new.quantity)`**: the quantity is a `u32` and the price an `i64`. Rust never mixes number types silently; `i64::from` converts, and it can't fail because every `u32` fits in an `i64`.
6. **`BadStatusChange { from, to }`** is a variant with named fields. `{from:?}` in its message prints them with `Debug`: "an order can't go from Ready back to Pending".

`set_status` gives the store a small function, `|current| to > current`, that decides whether the move is allowed. The store runs it **under the lock**, so checking and changing happen at once. Two kitchen staff tapping "ready" and "collected" at the same moment can't tangle an order.

`src/orders/store.rs`:

```rust
use std::sync::Mutex;

use super::model::{Order, Status};

pub struct OrderStore {
    inner: Mutex<Inner>,
}

struct Inner {
    orders: Vec<Order>,
    next_id: u64,
}

impl OrderStore {
    pub fn new() -> Self {
        OrderStore { inner: Mutex::new(Inner { orders: Vec::new(), next_id: 1 }) }
    }

    pub fn insert(&self, dish_id: u64, quantity: u32, total_naira: i64) -> Order {
        let mut inner = self.inner.lock().unwrap();
        let order = Order { id: inner.next_id, dish_id, quantity, total_naira, status: Status::Pending };
        inner.next_id += 1;
        inner.orders.push(order.clone());
        order
    }

    pub fn find(&self, id: u64) -> Option<Order> {
        self.inner.lock().unwrap().orders.iter().find(|o| o.id == id).cloned()
    }

    /// Changes the status if `allowed(current)` says so. Checking and changing happen under one lock.
    pub fn set_status(&self, id: u64, to: Status, allowed: impl Fn(Status) -> bool) -> Option<Result<Order, Status>> {
        let mut inner = self.inner.lock().unwrap();
        let order = inner.orders.iter_mut().find(|o| o.id == id)?;
        if !allowed(order.status) {
            return Some(Err(order.status));
        }
        order.status = to;
        Some(Ok(order.clone()))
    }
}

impl Default for OrderStore {
    fn default() -> Self {
        Self::new()
    }
}
```

1. **`allowed: impl Fn(Status) -> bool`**: "any function that takes a `Status` and returns a `bool`". The closure from the service fits.
2. **`Option<Result<Order, Status>>`** says three things in one type: `None` (no such order), `Some(Err(status))` (found, but not allowed; here's its status), `Some(Ok(order))` (changed). The service's `match` turns each into its own answer.
3. **`impl Default`**: when a type's `new()` takes nothing, Rust's linter, Clippy, asks for a `Default` too, so generic code can make one. It just calls `new()`.

`src/orders/handlers.rs`:

```rust
use axum::{
    Json, Router,
    extract::{Path, State},
    http::{StatusCode, header},
    middleware,
    response::{IntoResponse, Response},
    routing::{get, patch, post},
};

use super::{
    model::{NewOrder, Order, StatusChange},
    service::{OrderError, OrderService},
};
use crate::http::{StaffKey, kitchen_only};

pub fn router(orders: OrderService, staff_key: StaffKey) -> Router {
    let public = Router::new()
        .route("/orders", post(place))
        .route("/orders/{id}", get(get_one));

    let kitchen = Router::new()
        .route("/orders/{id}/status", patch(set_status))
        .route_layer(middleware::from_fn_with_state(staff_key, kitchen_only));

    public.merge(kitchen).with_state(orders)
}

impl IntoResponse for OrderError {
    fn into_response(self) -> Response {
        let status = match self {
            OrderError::NotFound(_) => StatusCode::NOT_FOUND,
            OrderError::BadQuantity | OrderError::NoSuchDish(_) => StatusCode::UNPROCESSABLE_ENTITY,
            OrderError::DishUnavailable | OrderError::BadStatusChange { .. } => StatusCode::CONFLICT,
        };
        (status, self.to_string()).into_response()
    }
}

async fn place(State(orders): State<OrderService>, Json(new): Json<NewOrder>) -> Result<impl IntoResponse, OrderError> {
    let order = orders.place(new)?;
    let location = [(header::LOCATION, format!("/orders/{}", order.id))];
    Ok((StatusCode::CREATED, location, Json(order)))
}

async fn get_one(State(orders): State<OrderService>, Path(id): Path<u64>) -> Result<Json<Order>, OrderError> {
    Ok(Json(orders.get(id)?))
}

async fn set_status(
    State(orders): State<OrderService>,
    Path(id): Path<u64>,
    Json(change): Json<StatusChange>,
) -> Result<Json<Order>, OrderError> {
    Ok(Json(orders.set_status(id, change.status)?))
}
```

Anyone may place an order and look one up. Only the kitchen moves an order to "ready" or "collected".

**409 Conflict** is for "your request is fine, but it clashes with how things are right now": the dish is sold out, or the order has already moved past that status. Try again later, or with something else, and it may work. A 422 means the request itself is wrong and will never work as sent.

(Anyone who guesses an order number can look it up. That's fine for now; lesson 13 makes orders belong to the customer who placed them.)

## Step 9: what every feature shares
<!-- bite: 14acb18d-3d22-40fd-8bc0-a7fc81a8e6f4 -->

`src/http.rs` takes the two middleware from lesson 3, made `pub`, and a new type for the staff key:

```rust
//! Middleware and helpers every feature can use. Knows nothing about dishes or orders.

use std::sync::Arc;

use axum::{
    extract::{Request, State},
    http::StatusCode,
    middleware::Next,
    response::{IntoResponse, Response},
};
use subtle::ConstantTimeEq;
use tracing::info;

/// The kitchen's shared secret. Cheap to clone; never printed.
#[derive(Clone)]
pub struct StaffKey(Arc<str>);

impl StaffKey {
    pub fn new(key: &str) -> Self {
        StaffKey(key.into())
    }

    /// Reads STAFF_KEY, and stops the program if it's missing.
    pub fn from_env() -> Self {
        let key = std::env::var("STAFF_KEY").expect("set STAFF_KEY to the kitchen's secret key");
        StaffKey::new(&key)
    }
}

pub async fn log_requests(req: Request, next: Next) -> Response {
    let method = req.method().clone();
    let path = req.uri().path().to_owned();
    let start = std::time::Instant::now();

    let response = next.run(req).await;

    info!(%method, path, status = response.status().as_u16(), took_ms = start.elapsed().as_millis() as u64, "request");
    response
}

pub async fn kitchen_only(State(key): State<StaffKey>, req: Request, next: Next) -> Response {
    let given = req.headers().get("x-staff-key").map(|v| v.as_bytes()).unwrap_or_default();
    if given.ct_eq(key.0.as_bytes()).into() {
        next.run(req).await
    } else {
        (StatusCode::UNAUTHORIZED, "kitchen staff only").into_response()
    }
}
```

**`StaffKey` is a newtype**: a struct with one field, `struct StaffKey(Arc<str>)`, that wraps another type to give it a name of its own. Lesson 3 used `State<String>`. That worked, but a `String` could be anything: a database address, a Paystack key. With `State<StaffKey>`, the type says what it is, and you can't hand the middleware the wrong string by mistake. The field is private, so only this module can read the secret.

**`Arc<str>`** instead of `String`: the key is cloned into each feature's router, and it never changes. Cloning an `Arc` just adds an owner; cloning a `String` copies the text.

**`StaffKey` has no `Debug`.** It's on purpose. Without it, `{:?}` won't compile on a key, so nobody can print the secret into the logs by accident.

**The name `http` is ours, and so is `axum::http`.** Inside this crate, `crate::http` is always this file. Axum's is always `axum::http`. Writing the full path, as `handlers.rs` does, means there's never a doubt which one you mean.

## Step 10: the new lib.rs and main.rs
<!-- bite: c42a3478-155b-4a2a-b215-eb5745397250 -->

`src/lib.rs` builds the whole app:

```rust
//! Mama Put API: the menu and orders for a roadside food seller.

pub mod http;
pub mod menu;
pub mod orders;

use std::time::Duration;

use axum::{Router, http::StatusCode, middleware, routing::get};
use tower_http::{catch_panic::CatchPanicLayer, timeout::TimeoutLayer};

/// Builds the whole app. `main` calls this; so will the tests.
pub fn app(staff_key: http::StaffKey) -> Router {
    let menu = menu::MenuService::new(menu::MenuStore::with_sample_dishes());
    let orders = orders::OrderService::new(orders::OrderStore::new(), menu.clone());

    Router::new()
        .route("/", get(|| async { "Mama Put is open!" }))
        .merge(menu::router(menu, staff_key.clone()))
        .merge(orders::router(orders, staff_key))
        .layer(CatchPanicLayer::new())
        .layer(TimeoutLayer::with_status_code(StatusCode::REQUEST_TIMEOUT, Duration::from_secs(10)))
        .layer(middleware::from_fn(http::log_requests))
}
```

`app` builds the stores and services, gives each feature its router, merges them, and wraps the lot in the layers from lesson 3, in the same order. Reading it top to bottom tells you everything the app has. It takes the staff key as an argument instead of reading the environment itself, so a test can pass in any key it likes.

`src/main.rs` is now just the program:

```rust
use mama_put::http::StaffKey;
use tokio::net::TcpListener;
use tracing::info;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    tracing_subscriber::fmt().with_env_filter("mama_put=info,tower_http=info").init();

    let staff_key = StaffKey::from_env();
    let app = mama_put::app(staff_key);

    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    info!(addr = %listener.local_addr()?, "Mama Put API listening");
    axum::serve(listener, app).with_graceful_shutdown(shutdown_signal()).await
}

async fn shutdown_signal() {
    tokio::signal::ctrl_c().await.expect("can't listen for Ctrl+C");
    info!("shutting down");
}
```

`main.rs` uses the library as `mama_put::...`, like any crate from crates.io. It sets up logging, reads the one setting, binds the port and serves. Nothing about dishes.

Build it, and run it:

```bash
cargo build
cargo clippy
STAFF_KEY=sekret cargo run
```

`cargo clippy` is Rust's linter: it reads your code and suggests better ways to write it (the `Default` for `OrderStore` came from it). Get used to running it after every change; it teaches Rust as you go.

The menu routes from lessons 2 and 3 work exactly as before, apart from the three new rules. **Restructuring changes where code lives, not what it does.** And now the orders:

```bash
curl -i -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":1,"quantity":2,"totalNaira":1}'
# 201, totalNaira 3000: the price comes from the menu, not from you
curl -i -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":3,"quantity":1}'
# 409 that dish isn't available right now
curl -i -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":1,"quantity":21}'
# 422 you can order between 1 and 20 plates
curl -i -X PATCH localhost:8080/orders/1/status -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"status":"ready"}'
# 200, status ready
curl -i -X PATCH localhost:8080/orders/1/status -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"status":"pending"}'
# 409 an order can't go from Ready back to Pending
curl -i -X POST localhost:8080/menu -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"name":"Moi moi","priceNaira":0}'
# 422 a price must be more than ₦0
```

## The one-way rule, which Rust won't enforce for you
<!-- bite: a16d9e66-dd79-4b01-9fb0-2e5fbd76a0a2 -->

`orders` uses `menu`, because placing an order needs the menu. So `menu` should **never** use `orders`. If the menu needed to know about orders (say, "don't delete a dish with pending orders"), and orders needed the menu, each would have to change whenever the other did. Over time, everything ends up tangled with everything.

In Go, that tangle doesn't compile: two packages importing each other is an `import cycle not allowed` error ([[backend/frameworks/net-http/04-structuring-a-go-service|lesson 4 of net/http]]). **Rust allows it.** I added `use crate::orders::OrderService;` to `menu/service.rs` and built: no error at all. Modules in one crate are compiled together, as one unit, so they can use each other in any direction.

So the arrows are yours to keep. Inside Mama Put:

1. **`main.rs` uses the library.** Nothing uses `main.rs`.
2. **`lib.rs` uses every feature**, to build the app.
3. **Features use `http`**, and other features they truly need (`orders` → `menu`). Never back.
4. **`http` uses nothing of ours.** It's at the bottom, used by all.
5. **Inside a feature, handlers use the service, and the service uses the store.** Never the other way. The `use` lines at the top of each file show it: only `handlers.rs` mentions `axum`.

When you feel the need to point an arrow backwards, it's a design question. Usually a type is in the wrong module, or two modules are really one, or the lower one should take a trait instead of the other's concrete type. That last idea is the next lesson.

**If you want the compiler to enforce it**, split the code into several crates in one **Cargo workspace**: say `mama-put-menu`, `mama-put-orders` and `mama-put-api`. Crates *can't* depend on each other in a circle; Cargo refuses. Big Rust projects do this, and it speeds up builds too, because Cargo only rebuilds the crates that changed. For one small service it's more setup than it's worth. Modules, and a habit of reading your `use` lines, are enough for now.

## Names: `MenuService`, not `Service`
<!-- bite: 87276349-8a11-4bda-b8c6-d546b5b616e2 -->

In Go, you always write the package in front of an imported name, so `menu.Service` reads well and `menu.MenuService` stutters. In Rust, you usually `use` a type once at the top and then write just its name: `MenuService`, `OrderService`. If both were called `Service`, every file that used both would need `menu::Service` and `orders::Service`, or renaming with `as`. So Rust code tends to give types their full name. Functions are different: `menu::router` and `orders::router` are called with the module in front, so the short name is right.

## The Rust in this lesson
<!-- bite: 6a37eba1-393c-48d7-8f2d-a1ca2e8ad6c5 -->

1. **`mod name;`**: declares a module whose code is in `name.rs` or `name/mod.rs`. A file that no `mod` declares isn't compiled at all.
2. **`src/lib.rs` beside `src/main.rs`**: two crates in one package, a library and a program. The program uses the library by the package's name, with `-` turned into `_`: `mama_put::app`.
3. **`pub`, private by default, and `pub(crate)`**: everything is private to its module until marked `pub`; `pub(crate)` is visible in the whole crate but not outside it.
4. **Struct fields are private separately.** `pub struct` lets others name the type; each field needs its own `pub` to be read.
5. **`pub use`**: re-export a name, so the outside reaches it through a shorter path, and the inside can be rearranged freely.
6. **`crate::`, `super::`**: paths from the top of the crate, and from the module above.
7. **`//!` and `///`**: doc comments, for the module you're in and for the item below.
8. **`#[derive(thiserror::Error)]` and `#[error("...")]`**: an error enum with a message per variant, `{0}` for a value, `{name:?}` for a named field printed with `Debug`.
9. **Enums with data**: `NotFound(u64)` carries a value; `BadStatusChange { from, to }` carries named fields; `BadStatusChange { .. }` in a pattern ignores them.
10. **`impl IntoResponse for MenuError`**: implementing a trait from another crate for your own type, so handlers can return `Result<_, MenuError>`.
11. **Interior mutability**: a `Mutex` inside a struct lets `&self` methods change data, safely.
12. **`Option` to `Result` and back**: `ok_or(err)`, and `?` on an `Option` inside a function that returns one.
13. **`map_err(|_| ...)`**: change the error inside a `Result`, here from the menu's words into the order's.
14. **`is_some_and`, `is_none_or`, `as_deref`**: ask about what's inside an `Option` without taking it out.
15. **`#[derive(PartialOrd, Ord)]` on an enum**: variants compare in the order they're written.
16. **`impl Fn(Status) -> bool`**: a parameter that takes any function, or closure, of that shape.
17. **Ranges, `1..=20`**: from 1 to 20 inclusive; `.contains(&x)` checks a number is in it.
18. **`i64::from(x)`**: convert between number types where it can't fail.
19. **A newtype, `struct StaffKey(Arc<str>)`**: a new name and type for an existing one, with its own rules, like no `Debug`.
20. **`impl Default`**: a standard way to make a type's "empty" value.
21. **`cargo clippy`**: the linter. Run it after `cargo build`.

## Your project so far
<!-- bite: 9044381f-b864-4709-bb95-f065ab453845 -->

```text
mama-put/
├── Cargo.toml             ← + thiserror
├── Cargo.lock
└── src/
    ├── main.rs            ← logging, StaffKey::from_env, bind, serve with graceful shutdown
    ├── lib.rs             ← pub mod http, menu, orders; app(): services, routers merged, layers
    ├── http.rs            ← StaffKey, log_requests, kitchen_only
    ├── menu/
    │   ├── mod.rs         ← private modules; pub use router, Dish, NewDish, DishChanges, MenuService, MenuError, MenuStore
    │   ├── model.rs       ← Dish, NewDish, DishChanges
    │   ├── store.rs       ← MenuStore (Mutex inside): list, find, add, change, remove
    │   ├── service.rs     ← MenuError; MenuService (Arc<MenuStore>): the name, price and specials rules
    │   └── handlers.rs    ← router (public + kitchen), IntoResponse for MenuError, six handlers
    └── orders/
        ├── mod.rs
        ├── model.rs       ← Status (pending < ready < collected), Order, NewOrder, StatusChange
        ├── store.rs       ← OrderStore: insert, find, set_status (checked under the lock)
        ├── service.rs     ← OrderError; OrderService (uses MenuService): place, get, set_status
        └── handlers.rs    ← router (POST /orders, GET /orders/{id}, kitchen PATCH /orders/{id}/status)
```

Only the `handlers.rs` files, `http.rs`, `lib.rs` and `main.rs` use Axum. Services and stores don't know HTTP exists.

## Common mistakes
<!-- bite: ab38b75e-ea52-4633-8cad-5caffb5279c5 -->

1. **Making a file and forgetting `mod`.** Rust doesn't compile files nobody declares, and the error is about a missing name somewhere else, not about the file.
2. **Rules in handlers.** If a handler has an `if` about dishes or orders, it's a rule, and it belongs in the service.
3. **Status codes in services.** A service returns `MenuError::NotFound`; it never decides on 404. Then the same service works for jobs and tests.
4. **Making everything `pub` to quiet the compiler.** Start private. When the compiler says something's private, ask whether the caller should really reach it, or should go through the front counter.
5. **A service without `Arc`.** If `MenuService` held a `MenuStore` directly and derived `Clone`, every handler would get its own copy of the dishes. (It wouldn't even compile, because `Mutex` can't be cloned. Rust stops you, this time.)
6. **Passing another feature's error straight up.** `OrderService` turns `MenuError` into `OrderError` with `map_err`, so the orders handler has one error type to match on.
7. **Trusting the client's total.** Prices come from the menu, on the server. Leave the field out of `NewOrder` and it can't be sent.
8. **Assuming Rust stops cycles.** It does between crates, not between modules. Read your `use` lines.

## Check your understanding
<!-- bite: d44ec224-9d83-4ad3-a760-f8a7f7a2fad1 -->

1. You make `src/menu/prices.rs` and write a function in it, but nothing can find the function. What's missing?
2. Give two reasons to put the app in `lib.rs` instead of `main.rs`.
3. `MenuService` is `pub`, and has a `store` field. Why can't `handlers.rs`, in the same feature, write `menu.store`?
4. What does `pub use service::MenuService;` in `menu/mod.rs` let the rest of the crate do, and what does it let you change later without breaking anyone?
5. Why does `MenuService` hold an `Arc<MenuStore>`, while the `Mutex` is inside `MenuStore`?
6. Where does a `MenuError::NotFound` become a 404, and why not in the service?
7. Why is moving an order from "ready" back to "pending" a 409, but ordering 21 plates a 422?
8. Go refuses an import cycle between packages. What does Rust do with `menu` using `orders` and `orders` using `menu`, and how could you make the compiler refuse it?

<details>
<summary>Answers, after your attempt</summary>

1. `mod prices;` in `src/menu/mod.rs`. A file isn't part of the crate until a module declaration names it. (And the function needs `pub`, or `pub(super)`, if anything outside `prices` should call it.)
2. Tests in `tests/` can build the whole app by calling `mama_put::app(...)`, which they couldn't do with a binary crate. Other programs (a migration tool, a second service) can live in `src/bin/` and use the same library. And `main.rs` can only use what's `pub`, which keeps the library's front door honest.
3. Fields are private to the module where the struct is written, here `menu::service`, even if the struct is `pub`. `handlers` is a different module. The handler has to go through the service's methods, so it can't skip the rules.
4. It lets everyone write `menu::MenuService` instead of `menu::service::MenuService`, without the `service` module being public. You can later move `MenuService` to another file inside the menu, or split `service.rs` in two, and nothing outside the menu changes.
5. The `Mutex` guards the data, so it sits with the data in the store, and no caller ever touches the lock. The `Arc` is for sharing: every handler gets a clone of the service, and they must all share one store. Cloning an `Arc` adds an owner; it doesn't copy the dishes.
6. In `impl IntoResponse for MenuError`, in `handlers.rs`. The service is for rules and knows nothing about HTTP, so a background job, a test or the GraphQL API can use it too. Only the HTTP layer decides what a rule's "no" means as a status code.
7. 409 Conflict means the request is fine but clashes with the current state of things: the order has already moved on. 422 means the request itself can never work as sent: 21 plates is never allowed.
8. Rust compiles it without a word, because modules in one crate are compiled as one unit. To make it refuse, put the features in separate crates in a Cargo workspace; Cargo won't allow crates to depend on each other in a circle.

</details>

## Practice
<!-- bite: e541f43b-e883-4294-8e64-29c3f66fd612 -->

1. Write `GET /orders?status=pending` for the kitchen, behind the staff key: a `ListParams` with `status: Option<Status>`, a `list` method on the store and service, and a route in the kitchen router.
2. Add a rule: no order may be for more than ₦50,000. Add a variant to `OrderError`, and see which `match` the compiler sends you to.
3. Make `menu::MenuStore` stop being re-exported (remove it from `pub use`), and fix `lib.rs` so it still builds. Where should the sample dishes be made now?
4. Move `kitchen_only` and `StaffKey` into a module of their own, `src/http/staff.rs`, with `src/http.rs` becoming `src/http/mod.rs`. Keep `crate::http::kitchen_only` working for the features with `pub use`.
5. Add `use crate::orders::OrderService;` to `menu/service.rs` and build, to see for yourself that Rust allows it. Then take it out.

**Done when** `main.rs` is under 25 lines, each feature has its model, store, service and handlers in their own files, `mod.rs` re-exports what the outside needs and nothing more, the six menu routes and three order routes work with the status codes above, `cargo clippy` is quiet, and you can say for any `use` line which way its arrow points.

## Before moving on
<!-- bite: 3e77c2d5-fb6e-4b08-89db-716455d6b1b3 -->

Mama Put is now a library with a short program in front of it. Each feature has its own folder and its own front counter, with the store, the rules and the routes each in a file of their own, and errors that become status codes in exactly one place. You've seen Rust's privacy wall from both sides, and that keeping the arrows pointing one way is a habit, not a compiler rule.

There's one thing `app()` still does by hand: it builds every store and service itself, with the sample dishes, so a test can't give it an empty menu or a fake store. Next lesson: state and dependency injection, with one `AppState`, `FromRef`, and the store behind a trait, so tests can swap it.

## Related
<!-- bite: 8706d0e0-93fc-4ce3-a8d7-845d37f7f90c -->

- [[backend/frameworks/axum/05-state-and-dependency-injection|Next: State and Dependency Injection]]
- [[backend/frameworks/net-http/04-structuring-a-go-service|The same lesson in net/http]] — `cmd/` and `internal/`, and import cycles that don't compile
- [[backend/03-structuring-a-backend/index|Structuring a Backend]] — layers, and organising by feature
- [[languages/03-rust/index|The Rust course]] — modules, traits and error handling in the language itself

## About this lesson
<!-- bite: c57cab0e-e6bd-4238-8be8-1b157df5f78e -->

**Level:** Intermediate. Lesson 4 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, tower-http 0.7 and thiserror 2. Covers a library crate beside the binary and why, how `mod` finds files, privacy by default for items and for struct fields separately, `pub use` re-exports as a feature's front counter, `crate::` and `super::` paths, organising by feature into model, store, service and handlers, interior mutability with the lock inside the store and `Arc` in the service, per-feature error enums with thiserror and `IntoResponse`, `map_err` between features, the orders feature with an ordered `Status` enum and a status check under the lock, a `StaffKey` newtype with no `Debug`, the two privacy errors (E0616, E0603), why Rust allows cycles between modules but not crates, and naming types in Rust compared with Go.
