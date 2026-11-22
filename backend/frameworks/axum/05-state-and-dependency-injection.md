---
id: b5434062-be3a-4423-9bd8-ee8ea835b937
---

# State and Dependency Injection

**Dependency injection means every part of the app is handed the things it needs, instead of building or finding them itself, and one place at the top builds them all and connects them.** In Rust you do it with plain code: services that take their dependencies as arguments, traits that say what a dependency must be able to do, and a `main` that builds everything. In Axum, what `main` builds is the **app state**: one struct holding everything the handlers need.

## Before you start
<!-- bite: cebf4dae-58d9-4dc4-8399-00c5b4bf5cca -->

You should have:

1. Finished [[backend/frameworks/axum/04-structuring-an-axum-service|lesson 4]], so Mama Put is a library crate with `menu` and `orders` modules, each with a model, store, service and handlers.
2. Met traits in Rust. If not, read [[languages/03-rust/09-traits|Traits]] first; this lesson leans on them.

After this lesson you will be able to:

1. Put a store behind a trait, and use it as `Arc<dyn Trait>`.
2. Read the "not dyn compatible" error, and fix it.
3. Treat the clock as a dependency, so a rule about opening hours can be tested at any hour.
4. Hold the app's dependencies in one `AppState`, and let each handler take just the part it needs, with `FromRef`.
5. Build everything in `main`, the one place that knows which parts are real.
6. Write and run your first Rust tests.

## What to install
<!-- bite: 53dc3324-2780-45d5-b27e-2aaf45fce087 -->

```bash
cargo add jiff
```

**`jiff`** is a date and time library. Rust's standard library can measure how long something took (`Instant`, lesson 3), but it doesn't know about dates, hours or time zones. Mama Put needs "what hour is it in Lagos?", so we need jiff.

## Where we stopped
<!-- bite: a4bf0f27-1cea-4670-9bd7-9e38b01081f4 -->

`OrderService` holds an `Arc<OrderStore>` and a `MenuService`, and both stores are memory stores, written into the types. That works when the app runs. But:

1. **Lesson 8 swaps the memory stores for PostgreSQL.** Today, that means changing the services too, even though their rules don't change.
2. **There's no way to test the rules on their own.** `app()` builds the real stores, with Mama's three sample dishes, every time.
3. **Mama closes at 9pm.** A rule about the time can only be tested at that time, unless the time is something you can hand in.

## The kid version
<!-- bite: ec0865aa-40b9-4e03-b9a0-94068ffa436d -->

Mama doesn't grow her own rice. She doesn't care which farm it's from, either. She needs "a bag of rice, good quality", and whoever brings that is fine. If the usual supplier is out, her son buys from the next market, and she cooks exactly the same way.

That's dependency injection. Mama (the service) says what she needs ("rice"), not where it comes from. Someone else (`main`) goes and gets it, and hands it over. When Mama is trying a new recipe, her son can hand her a small practice bag, and nothing about the cooking changes.

**Where the picture stops working.** In real life, Mama checks the bag when it arrives. In Rust, the compiler checks it before the program even runs: if what you hand over can't do what Mama asked for, it won't build.

## Terms used in this lesson
<!-- bite: 4464e166-4dff-473d-a829-b248259fb886 -->

1. **Dependency**: This is something a piece of code needs to do its job. `OrderService` depends on a store, on the menu, and on a clock.
2. **Dependency injection**: This means handing a piece of code its dependencies from outside, as arguments, instead of letting it make them. The name is grander than the idea.
3. **Composition root**: This is the one place in the program where all the real dependencies are built and connected. In Mama Put, it's `main`.
4. **Trait object**: This is a value whose exact type isn't known at compile time, only which trait it implements, written `dyn Trait`. It always sits behind a pointer, like `Arc<dyn MenuStore>`.
5. **Dyn compatible**: This means a trait can be used as `dyn Trait`. Most traits are; a trait with generic methods isn't.
6. **App state**: This is the one struct, `AppState`, that holds everything the handlers need. Axum hands it to the router once, with `with_state`.
7. **`FromRef`**: This is Axum's trait for "you can get a `B` out of an `A`". It lets a handler ask for `State<MenuService>` when the app's state is the whole `AppState`.
8. **Unit test**: This is a small test of one piece of code on its own, written next to the code, that `cargo test` runs.

## Step 1: the store becomes a trait
<!-- bite: 60c01dc3-016d-4b7c-855e-a9116429b0a6 -->

Look at what `MenuService` uses from its store: five methods, `list`, `find`, `add`, `change` and `remove`. That's the whole of what the menu needs from wherever dishes are kept. Say exactly that, as a trait, at the top of `src/menu/store.rs`:

```rust
/// What the menu needs from wherever dishes are kept.
pub trait MenuStore: Send + Sync {
    fn list(&self) -> Vec<Dish>;
    fn find(&self, id: u64) -> Option<Dish>;
    fn add(&self, new: NewDish) -> Dish;
    fn change(&self, id: u64, changes: DishChanges) -> Option<Dish>;
    fn remove(&self, id: u64) -> bool;
}
```

The memory store from lesson 4 keeps its code, under a new name, `MemoryMenuStore`. Its five methods move into an `impl MenuStore for MemoryMenuStore` block, and lose their `pub` (a trait's methods are as public as the trait):

```rust
/// Dishes kept in memory, safe to use from many requests at once.
pub struct MemoryMenuStore {
    inner: Mutex<Inner>,
}

impl MemoryMenuStore {
    pub fn new(dishes: Vec<Dish>) -> Self {
        let next_id = dishes.iter().map(|d| d.id).max().unwrap_or(0) + 1;
        MemoryMenuStore { inner: Mutex::new(Inner { dishes, next_id }) }
    }
}

impl MenuStore for MemoryMenuStore {
    fn list(&self) -> Vec<Dish> {
        self.inner.lock().unwrap().dishes.clone()
    }

    // ... find, add, change and remove, exactly as in lesson 4
}
```

`with_sample_dishes` is gone from the store. Which dishes Mama sells isn't the store's decision; `main` makes it now (step 6).

And `MenuService` holds *any* store, not the memory one:

```rust
#[derive(Clone)]
pub struct MenuService {
    store: Arc<dyn MenuStore>,
}

impl MenuService {
    pub fn new(store: Arc<dyn MenuStore>) -> Self {
        MenuService { store }
    }
```

Nothing else in the service changes. `self.store.list()` works the same: Rust looks up which `list` to call while the program runs.

Read `Arc<dyn MenuStore>` from the inside out:

1. **`dyn MenuStore`**: "some type that implements `MenuStore`; I don't know which until the program runs". Today it's a `MemoryMenuStore`. In lesson 8, a `PgMenuStore`. In a test, whatever the test likes.
2. **`Arc<...>`**: shared, as before. A `dyn` value can be any size, so it always lives behind a pointer. `Arc` is the pointer that can be shared between threads.

**`Send + Sync` after the trait's name** means "anything that implements `MenuStore` must also be safe to send to another thread (`Send`) and to use from several threads at once (`Sync`)". Without it, Rust can't let the store into Axum's state, which is used by requests on every thread. `Mutex` is what makes `MemoryMenuStore` `Sync`, so it qualifies; a store holding a plain `RefCell` (a lock-free, single-thread cell) wouldn't, and the compiler would say so.

Do the same in `src/menu/mod.rs`, so the outside can name both:

```rust
pub use store::{MemoryMenuStore, MenuStore};
```

### Where does the trait go?

In Go, the code that *uses* an interface declares it, because any type with the right methods satisfies it automatically ([[backend/frameworks/net-http/05-wiring-dependencies|lesson 5 of net/http]]). Rust doesn't work that way: a type implements a trait only when someone writes `impl MenuStore for ...`. So the trait goes with the feature that owns the idea, here the menu, beside its first implementation. The service in the same feature uses it, and a Postgres store will implement it.

## Step 2: when the compiler says "not dyn compatible"
<!-- bite: 8cae2986-7aff-4f4e-8005-487032d2ac6a -->

Do the same to orders: a trait `OrderStore`, the memory one renamed `MemoryOrderStore`, and `Arc<dyn OrderStore>` in the service. Copy `set_status` into the trait just as it was in lesson 4:

```rust
pub trait OrderStore: Send + Sync {
    fn insert(&self, dish_id: u64, quantity: u32, total_naira: i64) -> Order;
    fn find(&self, id: u64) -> Option<Order>;
    fn set_status(&self, id: u64, to: Status, allowed: impl Fn(Status) -> bool) -> Option<Result<Order, Status>>;
}
```

and build:

```text
error[E0038]: the trait `OrderStore` is not dyn compatible
  --> src/orders/service.rs:25:16
   |
25 |     store: Arc<dyn OrderStore>,
   |                ^^^^^^^^^^^^^^ `OrderStore` is not dyn compatible
   |
note: for a trait to be dyn compatible it needs to allow building a vtable
  --> src/orders/store.rs:10:8
   |
 6 | pub trait OrderStore: Send + Sync {
   |           ---------- this trait is not dyn compatible...
...
10 |     fn set_status(&self, id: u64, to: Status, allowed: impl Fn(Status) -> bool) -> Option<Result<Order, Status>>;
   |        ^^^^^^^^^^ ...because method `set_status` has generic type parameters
```

Here's what it means. For `dyn OrderStore` to work, Rust builds a small table for each store type, called a **vtable**: one entry per method, saying where that type's `insert`, `find` and `set_status` are. At run time, `self.store.find(1)` looks up the entry and jumps to it.

But `impl Fn(Status) -> bool` as a parameter is a **generic**: it means "a different `set_status` for every kind of closure you pass". Each closure has its own type, so there isn't one `set_status` to put in the table; there could be thousands, and the table can't list them all.

The fix is to take the closure *as* a trait object too:

```rust
    /// Changes the status if `allowed(current)` says so. Checking and changing must happen at once.
    fn set_status(&self, id: u64, to: Status, allowed: &dyn Fn(Status) -> bool) -> Option<Result<Order, Status>>;
```

**`&dyn Fn(Status) -> bool`** is "a borrowed function of that shape; any one". One `set_status`, which calls whatever function it's handed through *its* vtable. The service now passes a reference to its closure, with `&`:

```rust
match self.store.set_status(id, to, &|current| to > current) {
```

The rule to remember: **a trait you'll use as `dyn` can't have generic methods.** Take `&dyn Fn`, or a concrete type, instead.

## Step 3: `dyn`, or generics?
<!-- bite: 79266028-e00f-47be-bb11-1cc2b50a82ab -->

There's another way to let `MenuService` hold any store, without `dyn`:

```rust
pub struct MenuService<S: MenuStore> {
    store: Arc<S>,
}
```

That's a **generic**: the compiler makes a separate `MenuService` for each store type you use, and every call is direct, with no vtable lookup. It's how most of the Rust standard library works.

The cost is that `S` spreads. Every type that holds a `MenuService` now needs an `S` too (`OrderService<S, O>`), so does the app state, and so does every handler's `State<MenuService<S>>`. In a web app, that's a lot of angle brackets for no gain you could measure: one vtable lookup is a few nanoseconds, next to a database call that takes milliseconds.

So: **in a service's dependencies, use `Arc<dyn Trait>`.** Use generics where speed in a tight loop really matters, or in a library others build on. (Lesson 8 adds a wrinkle: database calls are `async fn`, and an `async fn` in a trait isn't dyn compatible either. That lesson shows the way round it.)

## Step 4: the clock is a dependency too
<!-- bite: b0b82e84-5f25-48e0-8a0e-ae2a8783bbf3 -->

Mama opens at 7am and closes at 9pm, Lagos time. Orders outside those hours should be refused. The obvious code is:

```rust
let hour = jiff::ZonedDateTime::now().hour(); // don't
```

But code that reads the clock directly gives a different answer depending on when you run it. The only way to test "closed at 6am" would be to run the test at 6am. So the time becomes something the service is *given*.

A new file, `src/clock.rs`, and `pub mod clock;` in `lib.rs`:

```rust
//! What time it is. A dependency like any other, so tests can choose the time.

use std::sync::Arc;

use jiff::Timestamp;

/// Tells the time. `Clock::system()` in the real app; `Clock::fixed(...)` in tests.
#[derive(Clone)]
pub struct Clock(Arc<dyn Fn() -> Timestamp + Send + Sync>);

impl Clock {
    /// The real time, from the computer's clock.
    pub fn system() -> Self {
        Clock(Arc::new(Timestamp::now))
    }

    /// Always the same moment. For tests.
    pub fn fixed(at: Timestamp) -> Self {
        Clock(Arc::new(move || at))
    }

    pub fn now(&self) -> Timestamp {
        (self.0)()
    }
}
```

1. **A `Timestamp`** is one exact moment, the same everywhere in the world. What hour it *is* depends on where you are; we'll ask that separately.
2. **`dyn Fn() -> Timestamp + Send + Sync`**: any function that takes nothing and returns a moment, safe to share between threads. The clock needs one job, so it doesn't need a trait of its own; a function is enough.
3. **`Clock::system()`** wraps jiff's own `Timestamp::now`. A function's name, without brackets, is a value you can store.
4. **`Clock::fixed(at)`** wraps a closure that always returns `at`. **`move`** makes the closure keep its own copy of `at`, so it can outlive the function that made it.
5. **`(self.0)()`**: `self.0` is the function inside; the brackets around it tell Rust "call the field", not "call a method named `0`".
6. **A newtype again**, like `StaffKey` in lesson 4, so the type says what it is. `Clock` reads better than `Arc<dyn Fn() -> Timestamp + Send + Sync>` everywhere it's used.

Now `OrderService` takes a clock, and finds the Lagos time zone once, when it's made:

```rust
#[derive(Clone)]
pub struct OrderService {
    store: Arc<dyn OrderStore>,
    menu: MenuService,
    clock: Clock,
    lagos: TimeZone,
}

impl OrderService {
    pub fn new(store: Arc<dyn OrderStore>, menu: MenuService, clock: Clock) -> Result<Self, jiff::Error> {
        let lagos = TimeZone::get("Africa/Lagos")?;
        Ok(OrderService { store, menu, clock, lagos })
    }

    pub fn place(&self, new: NewOrder) -> Result<Order, OrderError> {
        let hour = self.clock.now().to_zoned_datetime(self.lagos.clone()).hour();
        if !(7..21).contains(&hour) {
            return Err(OrderError::ShopClosed);
        }
        // ... the quantity, dish and availability checks from lesson 4
```

with a new variant at the top of `OrderError`:

```rust
    #[error("the shop is closed; Mama Put opens at 7am")]
    ShopClosed,
```

1. **`TimeZone::get("Africa/Lagos")`** reads Lagos's time zone rules from the operating system. It can fail (a computer without the rules), so `new` now returns a `Result`, and `?` passes the error up.
2. **`.to_zoned_datetime(lagos).hour()`**: the moment, as a date and time in Lagos, and its hour, from 0 to 23.
3. **`7..21`** is from 7 up to but **not including** 21. So 20:59 is open and 21:00 is closed. (`7..=21` would include 21.)
4. **`ShopClosed` is a 409**, in the `match` in `orders/handlers.rs`, beside `DishUnavailable`: the request is fine, it's the moment that's wrong. Try again in the morning.

Why the time zone, and not just the computer's hour? Because the server might not be in Lagos. Most cloud servers run on **UTC**, an hour behind Lagos. Without it, Mama would open at 8am Lagos time and close at 10pm. Time zones are part of your rules.

(Small Docker images, in lesson 28, don't have time zone rules on them. jiff has a feature that puts a copy inside your program; that lesson switches it on.)

## Step 5: one AppState, and `FromRef`
<!-- bite: 74c5fe5a-f2ad-40b7-bf42-7edab09dbc4a -->

In lesson 4, each feature's router called `.with_state(...)` on its own service. Now we want one place listing everything the handlers can use. In `src/lib.rs`:

```rust
/// Everything the handlers need, built once in `main` (or in a test).
#[derive(Clone, FromRef)]
pub struct AppState {
    pub menu: menu::MenuService,
    pub orders: orders::OrderService,
    pub staff_key: http::StaffKey,
}
```

with `use axum::extract::FromRef;` at the top. (`FromRef`'s derive needs Axum's `macros` feature, which you switched on in lesson 2.)

**`#[derive(FromRef)]`** writes one small piece of code per field: "from an `AppState`, you can get a `MenuService`, by cloning the `menu` field", and the same for `OrderService` and `StaffKey`. That's what lets the handlers stay exactly as they were. `list` still asks for `State<MenuService>`, not the whole `AppState`. Axum sees the router's state is `AppState`, finds `FromRef`, and hands over just the menu.

That matters. A handler that asks for `State<MenuService>` says, in its signature, what it can touch. One that took the whole `AppState` could reach the orders, the staff key and, later, the payment keys.

### Routers that don't know `AppState`

Now the feature routers. The obvious change is `pub fn router() -> Router<AppState>`. But `AppState` lives in `lib.rs`, at the top of the crate, and the menu module would have to use it: an arrow pointing *up*, the thing lesson 4 said to avoid. The menu shouldn't care what else is in the app.

So the router says what it needs from the state, instead of naming the state. In `src/menu/handlers.rs`:

```rust
/// The menu's routes: reads for everyone, writes for the kitchen.
/// Works with any app state that holds a `MenuService`.
pub fn router<S>(staff_key: StaffKey) -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    MenuService: FromRef<S>,
{
    let public = Router::new()
        .route("/menu", get(list))
        .route("/menu/specials", get(specials))
        .route("/menu/{id}", get(get_one));

    let kitchen = Router::new()
        .route("/menu", post(add))
        .route("/menu/{id}", patch(change).delete(remove))
        .route_layer(middleware::from_fn_with_state(staff_key, kitchen_only));

    public.merge(kitchen)
}
```

and add `FromRef` to the `extract::{...}` line at the top.

1. **`router<S>`**: a generic function, for any state type `S`.
2. **`where`** lists what `S` must be. **`Clone + Send + Sync + 'static`** is what Axum asks of every state: it's cloned for each request, shared across threads, and lives as long as the server. **`MenuService: FromRef<S>`** is the menu's one real demand: "I must be able to get a `MenuService` out of it".
3. **No `.with_state(...)` at the end.** The router returned is a `Router<S>`: routes still waiting for their state. `app()` supplies it once, for every feature.
4. **The staff key still goes to `from_fn_with_state` directly.** A middleware's state is its own, separate from the router's, so the key is just passed in.

Do the same in `src/orders/handlers.rs`, with `OrderService: FromRef<S>`.

Forget the `FromRef` line, and the error is the one from lesson 2 again:

```text
error[E0277]: the trait bound `fn(State<OrderService>, Json<...>) -> ... {place}: Handler<..., ...>` is not satisfied
   --> src/orders/handlers.rs:22:32
    |
 22 |         .route("/orders", post(place))
    |                                ^^^^^ unsatisfied trait bound
```

"Your function isn't a handler." This time `#[axum::debug_handler]` can't help, because it needs to know the exact state, and here it's any `S`. When you see this error on a generic router, check the `where` lines first: a handler is asking for a `State<X>`, and nothing promised that `X` can come out of `S`.

### The new `app`

```rust
/// Builds the whole app from what it's given. Builds nothing real itself.
pub fn app(state: AppState) -> Router {
    Router::new()
        .route("/", get(|| async { "Mama Put is open!" }))
        .merge(menu::router(state.staff_key.clone()))
        .merge(orders::router(state.staff_key.clone()))
        .with_state(state)
        .layer(CatchPanicLayer::new())
        .layer(TimeoutLayer::with_status_code(StatusCode::REQUEST_TIMEOUT, Duration::from_secs(10)))
        .layer(middleware::from_fn(http::log_requests))
}
```

`app` takes the state and builds nothing real: no stores, no clock, no environment. It only connects what it's given. **`.with_state(state)` comes after the merges**, so it fills in the state for every route at once. Here, and only here, Rust checks that `AppState` really can give a `MenuService` and an `OrderService`. Take the `orders` field out of `AppState`, and this is where it stops compiling.

## Step 6: main builds everything
<!-- bite: 5d777bb8-333b-4b43-8012-ce4e4cdfc4b3 -->

`src/main.rs` is now the composition root:

```rust
use std::sync::Arc;

use mama_put::{
    AppState,
    clock::Clock,
    http::StaffKey,
    menu::{Dish, MemoryMenuStore, MenuService},
    orders::{MemoryOrderStore, OrderService},
};
use tokio::net::TcpListener;
use tracing::info;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt().with_env_filter("mama_put=info,tower_http=info").init();

    // The one place that decides which store, which clock and which key are real.
    let menu = MenuService::new(Arc::new(MemoryMenuStore::new(sample_dishes())));
    let orders = OrderService::new(Arc::new(MemoryOrderStore::default()), menu.clone(), Clock::system())?;
    let state = AppState { menu, orders, staff_key: StaffKey::from_env()? };

    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    info!(addr = %listener.local_addr()?, "Mama Put API listening");
    axum::serve(listener, mama_put::app(state)).with_graceful_shutdown(shutdown_signal()).await?;
    Ok(())
}

fn sample_dishes() -> Vec<Dish> {
    let dish = |id, name: &str, price_naira, available, special| Dish {
        id,
        name: name.to_string(),
        price_naira,
        available,
        special,
    };
    vec![
        dish(1, "Jollof rice", 1500, true, true),
        dish(2, "Beans and plantain", 1200, true, false),
        dish(3, "Egusi and pounded yam", 2500, false, false),
    ]
}

async fn shutdown_signal() {
    tokio::signal::ctrl_c().await.expect("can't listen for Ctrl+C");
    info!("shutting down");
}
```

Read the three lines in the middle. They're the only place in the program that knows the stores are in memory, that the clock is the real one, and which dishes Mama starts with. Want PostgreSQL? Change the two `Arc::new(...)` lines. A demo where it's always lunchtime? Change `Clock::system()`. Nothing else in the app knows or cares.

**`MemoryOrderStore::default()`**: the store now derives `Default` (an empty list, next id 1) instead of having a `new` that takes nothing.

**`main` returns a `Result`.** `Box<dyn std::error::Error>` means "any kind of error", so every `?` in `main` works: a missing time zone, a missing staff key, a port already in use. If one fails, `main` returns it, and Rust prints it and exits with code 1. One way out, the same for every failure.

For that, `StaffKey::from_env` returns a `Result` now, instead of stopping the program itself, in `src/http.rs`:

```rust
    /// Reads STAFF_KEY from the environment.
    pub fn from_env() -> Result<Self, &'static str> {
        match std::env::var("STAFF_KEY") {
            Ok(key) if !key.is_empty() => Ok(StaffKey::new(&key)),
            _ => Err("set STAFF_KEY to the kitchen's secret key"),
        }
    }
```

1. **`Ok(key) if !key.is_empty()`** is a **match guard**: this arm only matches if the variable is set *and* not empty. `STAFF_KEY= cargo run` (set to nothing) is refused too, which lesson 3's `expect` let through.
2. **`_ =>`** matches everything else: not set, or empty.
3. **`&'static str`** is a piece of text written into the program, which lives as long as it runs. `?` in `main` turns it into a `Box<dyn Error>`.

Run it without the key:

```bash
cargo run
```

```text
Error: "set STAFF_KEY to the kitchen's secret key"
```

## Why there's no DI container
<!-- bite: 8f75be30-3140-4f6b-95c9-e65cb8e7e092 -->

In Spring, NestJS or ASP.NET Core, a **container** builds your objects: you mark a class, and it works out what to pass to its constructor. Rust doesn't have one in common use, and Mama Put won't either.

The reason is what you just wrote. `main` is about thirty lines, and it says exactly what's built and in what order. When something's wrong, you read it. With a container, the wiring is in annotations spread across files, and a mistake shows up when the app starts, or when a request first needs the thing.

Rust's compiler already checks the wiring: pass a store that doesn't implement `MenuStore`, forget a field of `AppState`, or ask for a `State<X>` nothing provides, and it won't build. That's most of what a container gives you, before the program has even run.

## Step 7: your first tests
<!-- bite: 214de19f-388a-40c3-8b78-a42f870f08bd -->

Now the payoff. The orders rules can be tested at any hour, with any menu.

In Rust, unit tests live **in the same file** as the code they test, in a module at the bottom. At the end of `src/orders/service.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::menu::{Dish, MemoryMenuStore};
    use crate::orders::MemoryOrderStore;

    /// A menu with one dish you can order and one that's sold out.
    fn test_menu() -> MenuService {
        let dish = |id, name: &str, price_naira, available| Dish {
            id,
            name: name.to_string(),
            price_naira,
            available,
            special: false,
        };
        MenuService::new(Arc::new(MemoryMenuStore::new(vec![
            dish(2, "Beans and plantain", 1200, true),
            dish(9, "Ofada stew", 3000, false),
        ])))
    }

    /// A clock stopped at half past `hour` on 21 November 2026, Lagos time.
    fn clock_at(hour: i8) -> Clock {
        let lagos = TimeZone::get("Africa/Lagos").unwrap();
        let at = jiff::civil::date(2026, 11, 21).at(hour, 30, 0, 0).to_zoned_datetime(lagos).unwrap();
        Clock::fixed(at.timestamp())
    }

    fn service_at(hour: i8) -> OrderService {
        OrderService::new(Arc::new(MemoryOrderStore::default()), test_menu(), clock_at(hour)).unwrap()
    }

    #[test]
    fn place_works_out_the_total() {
        let order = service_at(12).place(NewOrder { dish_id: 2, quantity: 3 }).unwrap();
        assert_eq!(order.total_naira, 3600);
        assert_eq!(order.status, Status::Pending);
    }

    #[test]
    fn place_refuses() {
        let cases = [
            ("before opening", 6, 2, 1, OrderError::ShopClosed),
            ("at closing time", 21, 2, 1, OrderError::ShopClosed),
            ("no plates", 12, 2, 0, OrderError::BadQuantity),
            ("too many plates", 12, 2, 21, OrderError::BadQuantity),
            ("no such dish", 12, 404, 1, OrderError::NoSuchDish(404)),
            ("sold out", 12, 9, 1, OrderError::DishUnavailable),
        ];
        for (name, hour, dish_id, quantity, want) in cases {
            let got = service_at(hour).place(NewOrder { dish_id, quantity });
            assert_eq!(got, Err(want), "{name}");
        }
    }

    #[test]
    fn status_only_moves_forward() {
        let orders = service_at(12);
        let order = orders.place(NewOrder { dish_id: 2, quantity: 1 }).unwrap();

        assert_eq!(orders.set_status(order.id, Status::Ready).unwrap().status, Status::Ready);
        assert_eq!(
            orders.set_status(order.id, Status::Pending),
            Err(OrderError::BadStatusChange { from: Status::Ready, to: Status::Pending })
        );
    }
}
```

1. **`#[cfg(test)]`** means "only compile this when testing". The tests aren't in the real program at all.
2. **`mod tests`** is a child module of `service`, so **`use super::*`** brings in everything from the file above it, *including private things*. A child module can see its parent's private items (lesson 4), so unit tests can test private functions too.
3. **`#[test]`** marks a function `cargo test` should run. A test passes if it returns without panicking.
4. **`assert_eq!(got, want)`** panics, and fails the test, if the two aren't equal, printing both. That's why the models and errors derive `Debug` and `PartialEq`. The `"{name}"` after them is a message printed on failure, so you know which case it was.
5. **The cases are a list.** `place_refuses` is a **table-driven test**: each row is a name, an hour, a dish, a quantity and the error expected, and one loop checks them all. Adding a case is one line.
6. **`unwrap()` is fine in tests.** If it fails, the test panics, and a panicking test is a failing test, which is what you want.

### The memory store is the fake

In Go's version of this lesson, the test writes a `fakeMenu` type. Here we didn't write any fake at all. `MemoryMenuStore` with two dishes *is* a perfect test menu: fast, no network, set up in three lines. The store trait is for swapping the real store (PostgreSQL) for a memory one, and that's the swap tests need too.

What we did have to make swappable was the clock. **Make the things outside your program injectable: the store, the clock, the network, the environment.** Things inside your program, like `MenuService`, can usually be used for real in a test.

Run them:

```bash
cargo test
```

You should see something like:

```text
running 3 tests
test orders::service::tests::status_only_moves_forward ... ok
test orders::service::tests::place_works_out_the_total ... ok
test orders::service::tests::place_refuses ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

The tests run at the same time, on several threads, so the order of the lines changes from run to run. Then break a rule on purpose (change `7..21` to `7..22`) and run again: `place_refuses` fails, printing what it got, what it wanted, and `at closing time`. Put it back.

## Locking decisions
<!-- bite: 8b638a2d-a8e3-4cec-b6fe-a45274c707eb -->

The lock is now hidden inside each memory store, so it's worth one look at whether it's the right lock, before PostgreSQL replaces it.

1. **`std::sync::Mutex`, held for a moment, never across an `.await`.** That's what we have. It's right for small, quick changes, and the store's design (the lock never leaves a method) makes misuse impossible.
2. **`std::sync::RwLock`** lets many readers in at once, but only one writer. Worth it when reads far outnumber writes *and* each read holds the lock for a while. Copying a short `Vec` of dishes doesn't, so a `Mutex` is just as fast here and simpler.
3. **Not locking at all** is often best. Data that never changes after start-up (settings, the staff key) needs no lock: `Arc` alone shares it. And where one task can own the data and others send it messages (the **actor** pattern), there's nothing to lock. Lesson 20's live kitchen screen works that way.

The rule from lesson 2 still holds: **never hold a lock across an `.await`.** If you do, every other request that needs the lock waits for the slow thing too, and your server serves one request at a time.

## The Rust in this lesson
<!-- bite: b94b108e-dc47-4d05-8126-1bda2eed8948 -->

1. **`trait MenuStore: Send + Sync { ... }`**: a trait, with **supertraits**: anything implementing it must also be `Send` and `Sync`.
2. **`impl MenuStore for MemoryMenuStore`**: implementing your own trait for your own type. A trait's methods have no `pub`; they're as visible as the trait.
3. **`Arc<dyn Trait>`**: a shared trait object; which type is inside is decided at run time, and calls go through a vtable.
4. **Dyn compatibility**: a trait with generic methods (`impl Fn` parameters, `fn x<T>()`) can't be `dyn`. Take `&dyn Fn(...)` instead.
5. **`&dyn Fn(Status) -> bool`**, and passing `&|current| ...`: a borrowed closure as a trait object.
6. **Generics with `where`**: `fn router<S>(...) where S: Clone + ..., MenuService: FromRef<S>`, listing what a type must be able to do.
7. **`'static`**: as a bound, "owns everything it holds, so it can live as long as needed"; as a reference, `&'static str`, text that lives as long as the program.
8. **`#[derive(FromRef)]`**: Axum's derive that lets handlers take one field of the state.
9. **`dyn Fn() -> Timestamp + Send + Sync`** in a struct, and **`(self.0)()`** to call it.
10. **Function names as values**: `Arc::new(Timestamp::now)`.
11. **`move` closures**: the closure owns what it uses, so it can outlive where it was made.
12. **Exclusive ranges, `7..21`**: up to but not including 21.
13. **`#[derive(Default)]`**, and a hand-written `impl Default` for `Inner` with `next_id: 1`.
14. **`main` returning `Result<(), Box<dyn std::error::Error>>`**: any error, with `?`, printed on the way out.
15. **Match guards, `Ok(key) if !key.is_empty() =>`**: an arm that matches only when a condition holds too.
16. **`#[cfg(test)] mod tests`, `#[test]`, `use super::*`, `assert_eq!`**: unit tests beside the code, which can see private items.
17. **Destructuring tuples in a `for` loop**: `for (name, hour, dish_id, quantity, want) in cases`.

## Your project so far
<!-- bite: 0d820e05-2bc5-44a7-8231-11b972bd28a1 -->

```text
mama-put/
├── Cargo.toml             ← + jiff
├── Cargo.lock
└── src/
    ├── main.rs            ← the composition root: stores, clock, sample dishes, AppState; returns Result
    ├── lib.rs             ← AppState (FromRef); app(state) builds nothing real
    ├── clock.rs           ← Clock: system() and fixed()
    ├── http.rs            ← StaffKey (from_env returns Result), log_requests, kitchen_only
    ├── menu/
    │   ├── mod.rs         ← + pub use MemoryMenuStore, MenuStore
    │   ├── model.rs
    │   ├── store.rs       ← trait MenuStore; MemoryMenuStore implements it
    │   ├── service.rs     ← MenuService holds Arc<dyn MenuStore>
    │   └── handlers.rs    ← router<S> where MenuService: FromRef<S>
    └── orders/
        ├── mod.rs         ← + pub use MemoryOrderStore, OrderStore
        ├── model.rs
        ├── store.rs       ← trait OrderStore (set_status takes &dyn Fn); MemoryOrderStore
        ├── service.rs     ← OrderService: Arc<dyn OrderStore>, MenuService, Clock; the shop-hours rule; 3 tests
        └── handlers.rs    ← router<S> where OrderService: FromRef<S>; ShopClosed is 409
```

## Common mistakes
<!-- bite: d8282832-3741-4c29-b475-346b5d03091b -->

1. **A service that builds its own store, or reads the clock.** Then nothing can swap it. Ask for it as an argument.
2. **Forgetting `Send + Sync` on a store trait.** The store and the service compile, and then every handler that uses the service fails with "isn't a handler", far from the cause.
3. **Generic methods on a trait you want as `dyn`.** Not dyn compatible. Take `&dyn Fn`.
4. **Generics everywhere "for speed".** The type parameters spread through every struct and handler, for nanoseconds no one will measure in a web app.
5. **A feature router returning `Router<AppState>`.** The feature now depends on the whole app. Make it generic over `S` with a `FromRef` bound.
6. **Handlers taking `State<AppState>`.** They can reach everything. Ask for the one part you need.
7. **The hour without the time zone.** On a UTC server, Mama opens an hour late.
8. **Faking what you could use for real.** A memory store with two dishes is a better test menu than a hand-written fake.
9. **`expect` in start-up code.** Return the error instead, so `main` has one way out.

## Check your understanding
<!-- bite: 90eb0672-50b9-487f-a7b2-88bac74e34e8 -->

1. What does `Arc<dyn MenuStore>` let `MenuService` do that `Arc<MemoryMenuStore>` didn't, and what does it cost?
2. Why must `MenuStore` say `Send + Sync`?
3. Why is a trait with a method taking `impl Fn(Status) -> bool` not dyn compatible, and what's the fix?
4. Give one reason to choose `Arc<dyn Trait>` over a generic `MenuService<S>` in a web service.
5. Why is the clock passed in, and why doesn't it need a trait of its own?
6. What does `#[derive(FromRef)]` on `AppState` let the `list` handler keep doing?
7. Why is the menu's router generic over `S` instead of returning `Router<AppState>`?
8. Why don't the order tests need a fake menu, when Go's version had one?

<details>
<summary>Answers, after your attempt</summary>

1. It lets the service work with any store that implements the trait: the memory one, a PostgreSQL one in lesson 8, or anything a test likes, without the service changing. The cost is a vtable lookup on each call, a few nanoseconds.
2. The store is shared through `Arc` inside the app state, which is used by requests on every thread. `Send` lets it move between threads, `Sync` lets several use it at once. Without the bound, Rust couldn't prove a `dyn MenuStore` is safe there, and the state wouldn't compile.
3. A `dyn` call goes through a vtable with one entry per method. A generic method is really a different method for every closure type, so there's no single entry to put in the table. Take the closure as `&dyn Fn(Status) -> bool`: one method, which calls whatever function it's given.
4. Generics spread: every struct holding the service, the app state and every handler's `State` would need the type parameter. `dyn` keeps the types simple, and its cost is tiny next to a database call.
5. Code that reads the clock itself gives a different answer depending on when it runs, so "closed at 6am" could only be tested at 6am. Passed in, a test can stop the clock at any hour. It has one job, telling the time, so a function is enough.
6. Ask for `State<MenuService>` instead of the whole `AppState`. Axum uses the generated `FromRef` to get the menu out of the state, and the handler's signature says it can only touch the menu.
7. So the menu module doesn't depend on `AppState`, which lives at the top of the crate and knows about every feature. The router only demands "a `MenuService` can come out of the state", and works in any app, or test, that provides one.
8. Because `MemoryMenuStore` with two test dishes is already fast, in-memory and easy to set up, so a real `MenuService` on top of it is a perfect test menu. Only things outside the program, like the clock, need swapping.

</details>

## Practice
<!-- bite: cf622972-c400-4fb2-a605-a0321c895c20 -->

1. Write tests for `MenuService` in `src/menu/service.rs`: a dish with no name is refused, a price of ₦0 is refused, and a sold-out special isn't in `specials()`.
2. Add a test that orders at exactly 07:00 are accepted. You'll need a `clock_at` that takes minutes too.
3. Mama closes early on Sundays, at 6pm. Add the rule, and a test for it. (`ZonedDateTime` has a `.weekday()`.)
4. Write a `CountingMenuStore` for a test: it wraps a `MemoryMenuStore` and counts how many times `find` was called. Use it to check that `place` looks the dish up exactly once.
5. Try the generic version, `MenuService<S: MenuStore>`, on a copy of the project, and count how many other files have to change before it builds again. Then put it back.

**Done when** both services hold their stores as `Arc<dyn ...>`, `OrderService` takes a `Clock`, `app()` takes an `AppState` and builds nothing real, `main` is the only place that knows the stores are in memory, the program refuses to start without `STAFF_KEY` and says why, and `cargo test` passes with the shop-hours, quantity, dish and status cases.

## Before moving on
<!-- bite: b2e2955a-cb8c-44ee-9f9e-a41b244befbb -->

The app's dependencies are now handed in, not reached for. The stores are traits, so lesson 8's database can slot in without touching a rule. The clock is a dependency, so time-based rules can be tested at any hour. One `AppState` holds everything, each handler takes just its part through `FromRef`, and `main` is the one place that decides what's real. And you've written your first Rust tests.

The service checks a few rules by hand (`if new.name.is_empty()`, `if new.price_naira <= 0`), and the `Json` extractor's errors still look different from ours. Next lesson: input validation, with the `validator` crate, and a `ValidatedJson` extractor of our own, so a handler can't be reached with a body that breaks the rules.

## Related
<!-- bite: 7e9ef6a7-a2a8-47bc-a770-a5599764fd74 -->

- [[backend/frameworks/axum/06-validation|Next: Input Validation]]
- [[backend/frameworks/net-http/05-wiring-dependencies|The same lesson in net/http]] — interfaces declared by the user, a `run` function, and a fake menu
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|Dependency Injection and Wiring]] — the idea, across languages
- [[languages/03-rust/09-traits|Traits]] — traits, trait objects and generics in the language itself
- [[languages/03-rust/13-concurrency|Concurrency]] — `Send`, `Sync`, `Arc` and locks

## About this lesson
<!-- bite: 6222a7e5-735b-4daa-9ed7-f030252aa18a -->

**Level:** Intermediate → Advanced. Lesson 5 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8 and jiff 1.0. Covers stores as traits with `Send + Sync` supertraits, `Arc<dyn Trait>` and vtables, the "not dyn compatible" error and `&dyn Fn` as the fix, `dyn` versus generics in a web service, the clock as an injected function in a `Clock` newtype, a shop-hours rule in Lagos time with jiff and why the time zone matters on UTC servers, one `AppState` with `#[derive(FromRef)]`, feature routers generic over the state with `FromRef` bounds so features don't depend on the app, `main` as the composition root returning `Result<(), Box<dyn Error>>`, why there's no DI container, first unit tests with `#[cfg(test)]`, table-driven cases and `assert_eq!`, using the memory store instead of hand-written fakes, and when to use `Mutex`, `RwLock` or no lock at all.
