---
id: 9b98edb7-9730-4a59-b1f4-cb24f6e177af
---

# Versioning

**Versioning an API means letting it change in ways that would break existing clients, without breaking them: old clients keep the old version, new clients get the new one, and the old one is retired on a date everyone was told about.** In Axum, the versions are just routers nested under `/v1` and `/v2`. The interesting part is Rust's: one set of handlers, written once, made generic over a **version trait** whose associated types are each version's shapes.

## Before you start
<!-- bite: 35614707-cff7-4e54-bdf6-acc18e7620f6 -->

You should have:

1. Finished [[backend/frameworks/axum/09-listing|lesson 9]], so the menu and orders have filtered, sorted, paged lists, and `cargo test` passes.
2. Met traits with associated types, like `Iterator`'s `type Item`. If not, skim [[languages/03-rust/09-traits|Traits]].

After this lesson you will be able to:

1. Say which changes break clients and which don't, and prefer adding to changing.
2. Choose between versioning in the path, a header, the media type or the query.
3. Keep the app's own types separate from what each version sends, and store money in kobo.
4. Write handlers once, generic over a `MenuVersion` trait with associated types, and serve v1 and v2 from them.
5. Validate nested JSON and report its fields as `price.amount`.
6. Deprecate v1 with `Deprecation`, `Sunset` and `Link` headers, and answer 410 Gone after the date.

## Where we stopped
<!-- bite: 73283865-1be9-46ec-8fdb-149ca0aaf8c9 -->

Paystack works in **kobo**, not naira (₦1 is 100 kobo), and the phone team wants prices as `{"amount": 150000, "currency": "NGN"}`, so they can show "₦1,500.00" properly and one day sell in another currency. That changes the shape of every dish and every order in every response. But last month's app, on thousands of customers' phones, reads `priceNaira`. Change it, and their app shows nothing, or worse, the wrong price. Don't change it, and the new app can't move forward.

## The kid version
<!-- bite: 744320f7-8508-43cf-aca7-8d319bbd49f4 -->

Mama prints a new menu card, with prices in a new style. But some regulars still carry last year's card, folded in their pockets, and order from it. So for a while, Mama keeps both cards at the stall. Same pots, same food, same kitchen. Just two cards.

She writes on the old card: "This card stops being accepted on 1 June." When June comes, someone who hands her the old card gets a polite "this card has expired, here's the new one", not a confused look.

**Where the picture stops working.** Mama can see who's holding the old card. Our server can't see the customers, only their requests. So it counts the requests still using v1, and that count, not the date alone, tells us when it's safe to switch v1 off.

## Terms used in this lesson
<!-- bite: 4fe5d8f1-af6b-43d8-a6a4-1c5772e8feb9 -->

1. **Breaking change**: This is a change that makes a working client stop working, like renaming a field it reads.
2. **API version**: This is a named, stable set of shapes and behaviours, like v1 and v2. Within a version, only safe changes are made.
3. **Domain type**: This is a type shaped for the code, like `Dish` with its price in kobo. It's never sent to clients as it is.
4. **Wire type**: This is a type shaped for one version's clients, like `DishV1` with `priceNaira`. It's what goes over the network.
5. **Associated type**: This is a type that each implementation of a trait chooses, written `type Dish: ...;` in the trait. It lets `V1` and `V2` each name their own shapes.
6. **Deprecation**: This is announcing that a version will stop working, while it still works.
7. **Sunset**: This is the date it stops working.

## Step 1: what counts as breaking
<!-- bite: 8dfebb9b-233d-49f6-813c-4a483d3359cf -->

Before choosing *how* to version, know *when* you need to. Most changes don't need a new version at all.

**Safe, in the same version:**

1. Adding a new route.
2. Adding a new **optional** field to a response, like `description`. Clients that don't know it ignore it.
3. Adding a new **optional** query parameter or body field.
4. Making a validation rule looser, like allowing names up to 120 characters.

**Breaking, needs a new version:**

1. Removing or renaming a field (`priceNaira` → `price`).
2. Changing a field's type or meaning. `price` in naira becoming `price` in kobo, with the same name, is the most dangerous of all, because nothing *looks* broken: the old app just shows ₦150,000 jollof.
3. Making an optional input field required.
4. Making validation stricter.
5. Changing status codes, error codes, or the response envelope.
6. Changing what a filter or a sort means.

A good habit: **add, don't change.** If clients can have the new thing next to the old thing, you don't need a new version. We could add `price` beside `priceNaira` in v1, and often that's the right call. We'll build a real v2 anyway, because one day you'll need to, and because v2 also lets new clients *send* prices in kobo.

One thing to admit: `deny_unknown_fields` from lesson 6 makes one "safe" change unsafe for *us*. A client that sends a new optional field to an old server gets a 400. That's the trade we chose: typos are caught, and servers must be updated before clients start sending new fields.

## Step 2: the four ways to say which version
<!-- bite: f434a029-7b29-449c-aa2f-ad9bfa2c89d3 -->

| Way | Looks like | Good | Costs |
|---|---|---|---|
| **In the path** | `GET /v2/menu` | obvious in every log line, browser and `curl`; easy to route and cache | the URL changes |
| **In a header** | `Api-Version: 2` | URLs stay clean | invisible in a browser, easy to forget; caches must be told (`Vary`) |
| **By media type** | `Accept: application/vnd.mamaput.v2+json` | the most correct by HTTP's rules | awkward to type and test |
| **By query parameter** | `GET /menu?api-version=2` | easy to add | mixes versions with filters |

There's a fifth style worth knowing: **dated versions**, like Stripe's `Stripe-Version: 2026-11-01`. Every breaking change gets a date, and each client is pinned to the date it signed up. Powerful, and a lot of work.

For Mama Put we choose **the path**, like the Go and Express versions. It's what most public APIs do, and anyone can see the version in a log line. Practice 4 does it with a header instead; the handlers wouldn't change at all.

## Step 3: separate what the app knows from what it sends
<!-- bite: e23b3e3d-a838-4f17-a349-b35426acde03 -->

Up to now, `Dish` has done two jobs: it's what the store returns and the service works with, *and*, through `#[derive(Serialize)]`, it's exactly what clients receive. With two versions, one struct can't be both `priceNaira` and `price`. So the jobs split:

1. **`Dish` is the domain type.** It's shaped for the code, holds the price in kobo as a type of its own, and doesn't derive `Serialize` at all. It's never sent as it is.
2. **Each version has its own wire types**: `DishV1`, `DishV2`.
3. **`From` converts** one into the other.

That's more typing, and it's what stops a renamed field in your Rust from silently renaming a field in your public API. Once the shapes are separate, the API only changes when you change a wire type, on purpose.

### Money, in kobo

First, a type for money, so nobody mixes up naira and kobo again. `src/money.rs`, and `pub mod money;` in `lib.rs`:

```rust
//! Money, kept in kobo, so amounts are always whole numbers.

use serde::{Deserialize, Serialize};
use validator::Validate;

/// An amount of money in kobo. ₦1 is 100 kobo.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, sqlx::Type)]
#[sqlx(transparent)]
pub struct Kobo(pub i64);

impl Kobo {
    pub fn from_naira(naira: i64) -> Kobo {
        Kobo(naira * 100)
    }

    /// Whole naira, rounding down: all that v1 can show.
    pub fn naira(self) -> i64 {
        self.0 / 100
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum Currency {
    #[serde(rename = "NGN")]
    Ngn,
}

/// How v2 sends and receives money: `{"amount": 150000, "currency": "NGN"}`.
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize, Validate)]
#[serde(deny_unknown_fields)]
pub struct Amount {
    #[validate(range(min = 1, max = 100_000_000, message = "must be from 1 kobo to ₦1,000,000"))]
    pub amount: i64,
    pub currency: Currency,
}

impl From<Kobo> for Amount {
    fn from(kobo: Kobo) -> Amount {
        Amount { amount: kobo.0, currency: Currency::Ngn }
    }
}

impl From<Amount> for Kobo {
    fn from(amount: Amount) -> Kobo {
        Kobo(amount.amount)
    }
}
```

1. **`Kobo` is a newtype** around `i64`. A function that takes a `Kobo` won't accept a naira amount by accident: `Kobo(1500)` and `1500` are different types, and the compiler keeps them apart. Money is the classic place where that saves you.
2. **`#[sqlx(transparent)]`** says "store it as whatever's inside": a `Kobo` is a `bigint` in Postgres.
3. **`Currency` has one variant.** Today Mama only takes naira, so `"currency": "USD"` is refused by serde. When she takes cedis, it's one more variant, and every `match` on it will ask what to do.
4. **`From` both ways** means `.into()` converts wherever the types are known.

### Store kobo, without the API noticing

`migrations/0004_prices_in_kobo.sql`:

```sql
-- Paystack works in kobo, and so do we from now on. ₦1 is 100 kobo.
ALTER TABLE dishes RENAME COLUMN price_naira TO price_kobo;
UPDATE dishes SET price_kobo = price_kobo * 100;

ALTER TABLE orders RENAME COLUMN total_naira TO total_kobo;
UPDATE orders SET total_kobo = total_kobo * 100;
```

sqlx runs each migration in a transaction, so it's either fully done or not at all. Run `sqlx migrate run`, then build: **the compiler now lists every query that mentions `price_naira`**, because lesson 8's checked queries ask the database, and that column is gone. That's the payoff of checked SQL, on the day you need it most. In each one, `price_naira` becomes `price_kobo AS "price: Kobo"` (and `total_naira` becomes `total_kobo AS "total: Kobo"`), and values sent in use the number inside: `new.price.0`.

One honest warning. This migration is safe here because Mama Put isn't live yet: we stop the app, migrate, start the new code. On a live system, the old code would still be reading `price_naira` for a few seconds after the rename, and fail. Live systems change columns in steps ("add the new column, write both, switch reads, drop the old"), which lesson 39 shows.

### The domain types

`src/menu/model.rs` loses every serde attribute. What's left is shaped for the code:

```rust
//! The menu's own types, shaped for the code. None of them is sent to clients as it is:
//! each API version has its own shapes, in `versions.rs`.

use crate::money::Kobo;

#[derive(Clone, Debug, PartialEq, sqlx::FromRow)]
pub struct Dish {
    pub id: i64,
    pub name: String,
    #[sqlx(rename = "price_kobo")]
    pub price: Kobo,
    pub available: bool,
    pub special: bool,
    pub portions_left: i32,
}

#[derive(Debug)]
pub struct NewDish {
    pub name: String,
    pub price: Kobo,
    pub available: bool,
    pub special: bool,
    pub portions_left: i32,
}

#[derive(Debug, Default)]
pub struct DishChanges {
    pub name: Option<String>,
    pub price: Option<Kobo>,
    pub available: Option<bool>,
    pub special: Option<bool>,
    pub portions_left: Option<i32>,
}
```

`DishFilter`'s `min_price` and `max_price` become `Option<Kobo>`, and `DishField::PriceNaira` becomes `DishField::Price`, whose `column()` is `"price_kobo"`. `DishField` no longer has an `api_name`, because that depends on the version. The service's rules compare kobo: `if new.price <= Kobo(0)`.

`#[sqlx(rename = "price_kobo")]` is for lesson 9's `QueryBuilder` list, which builds a `Dish` from columns by name; the checked queries rename it themselves, with `AS "price: Kobo"`. In `orders/model.rs`, `Order` loses `Serialize` the same way, and its `total_naira: i64` becomes `total: Kobo`. `NewOrder` and `StatusChange` stay as they are: they have no money in them, so they're the same in both versions.

## Step 4: one set of handlers, two versions
<!-- bite: 53aeb4e3-7e02-4493-bbff-2ab540ef3c45 -->

Here's the key idea: **versions differ at the edge, not inside.** v1 and v2 share the same `MenuService`, the same rules, the same store and the same database. Only the shapes at the door change.

In Go, you'd pass each handler a value saying which version it's serving, and `switch` on it. In Rust, there's a neater way: **a trait for a version, whose associated types are its shapes.** `src/menu/versions.rs`:

```rust
//! What each API version sends and receives for the menu. Versions differ here, at the door,
//! and nowhere else: v1 and v2 share one service, one store and one database.

use serde::{Deserialize, Serialize, de::DeserializeOwned};
use validator::Validate;

use super::model::{Dish, DishChanges, DishField, NewDish};
use crate::money::{Amount, Kobo};

/// One version of the menu API: its wire types, and how it names things.
pub trait MenuVersion: Send + Sync + 'static {
    /// Where this version's routes live: `/v1` or `/v2`.
    const PREFIX: &'static str;
    /// What the price field is called, in the JSON and in `sort` and `fields`.
    const PRICE: &'static str;

    type Dish: Serialize + From<Dish> + Send;
    type NewDish: DeserializeOwned + Validate + Into<NewDish> + Send;
    type DishChanges: DeserializeOwned + Validate + Into<DishChanges> + Send;

    /// `minPrice=` and `maxPrice=`, read in this version's unit.
    fn price_filter(value: i64) -> Kobo;

    /// The API name of a field, in this version.
    fn field_name(field: DishField) -> &'static str {
        match field {
            DishField::Id => "id",
            DishField::Name => "name",
            DishField::Price => Self::PRICE,
            DishField::Available => "available",
            DishField::Special => "special",
            DishField::PortionsLeft => "portionsLeft",
        }
    }

    fn field_named(name: &str) -> Option<DishField> {
        DishField::ALL.into_iter().find(|&f| Self::field_name(f) == name)
    }
}
```

Read the trait as a form each version fills in:

1. **`const PREFIX` and `const PRICE`**: **associated constants**. Each version says where it lives and what it calls the price.
2. **`type Dish: Serialize + From<Dish> + Send;`**: an **associated type**. "Each version has *some* type it sends for a dish. Whatever it is, it can be written as JSON, and made from a domain `Dish`." `NewDish` and `DishChanges` are the same idea the other way round: read from JSON, checked by validator, turned *into* the domain type.
3. **`fn price_filter(value: i64) -> Kobo;`**: `?maxPrice=2000` means ₦2,000 in v1 and 2,000 kobo in v2. Each version says how to read it.
4. **`fn field_name` has a body**: a **default method**. Every version gets it for free; only the price's name differs, through `Self::PRICE`.

The two versions are empty structs, there only to be named, and each fills in the form:

```rust
/// The first version: prices in whole naira.
pub struct V1;

/// Prices in kobo, as an amount and a currency.
pub struct V2;

impl MenuVersion for V1 {
    const PREFIX: &'static str = "/v1";
    const PRICE: &'static str = "priceNaira";
    type Dish = DishV1;
    type NewDish = NewDishV1;
    type DishChanges = DishChangesV1;

    fn price_filter(naira: i64) -> Kobo {
        Kobo::from_naira(naira)
    }
}

impl MenuVersion for V2 {
    const PREFIX: &'static str = "/v2";
    const PRICE: &'static str = "price";
    type Dish = DishV2;
    type NewDish = NewDishV2;
    type DishChanges = DishChangesV2;

    fn price_filter(kobo: i64) -> Kobo {
        Kobo(kobo)
    }
}
```

The wire types are in the same file. v1's are exactly what clients have always had, now converting from kobo:

```rust
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DishV1 {
    id: i64,
    name: String,
    price_naira: i64,
    available: bool,
    special: bool,
    portions_left: i32,
}

impl From<Dish> for DishV1 {
    fn from(d: Dish) -> Self {
        DishV1 {
            id: d.id,
            name: d.name,
            price_naira: d.price.naira(),
            available: d.available,
            special: d.special,
            portions_left: d.portions_left,
        }
    }
}
```

and `NewDishV1` is lesson 6's `NewDish`, moved here, with a `From` that turns `price_naira` into `Kobo::from_naira(...)`. v2's carry an `Amount`:

```rust
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DishV2 {
    id: i64,
    name: String,
    price: Amount,
    available: bool,
    special: bool,
    portions_left: i32,
}

#[derive(Debug, Deserialize, Validate)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct NewDishV2 {
    #[validate(length(min = 1, max = 80, message = "must be 1 to 80 characters"))]
    name: String,
    #[validate(nested)]
    price: Amount,
    #[serde(default = "yes")]
    available: bool,
    #[serde(default)]
    special: bool,
    #[serde(default)]
    #[validate(range(min = 0, max = 1000, message = "must be from 0 to 1,000"))]
    portions_left: i32,
}
```

**`#[validate(nested)]`** says "run `Amount`'s own rules too". (The `DishChangesV1` and `DishChangesV2` types follow the same pattern.) The fields of wire types are private: nothing outside `versions.rs` builds or reads them, they only go in and out through `From`.

### The handlers, generic over the version

Now the payoff. In `src/menu/handlers.rs`, each handler takes a type parameter `V: MenuVersion` and uses `V`'s types:

```rust
async fn get_one<V: MenuVersion>(State(menu): State<MenuService>, Path(id): Path<i64>) -> Result<Data<V::Dish>, ApiError> {
    Ok(Data(menu.get(id).await?.into()))
}

async fn add<V: MenuVersion>(
    State(menu): State<MenuService>,
    ValidatedJson(new): ValidatedJson<V::NewDish>,
) -> Result<impl IntoResponse, ApiError> {
    let dish = menu.add(new.into()).await?;
    let location = [(header::LOCATION, format!("{}/menu/{}", V::PREFIX, dish.id))];
    Ok((StatusCode::CREATED, location, Data(V::Dish::from(dish))))
}
```

1. **`ValidatedJson<V::NewDish>`**: for v1 that's `ValidatedJson<NewDishV1>`, which reads `priceNaira`; for v2, `ValidatedJson<NewDishV2>`, which reads `price`. Same line, two meanings.
2. **`new.into()`** turns whichever it was into the domain `NewDish`. The service never knows which version asked.
3. **`V::Dish::from(dish)`** turns the domain `Dish` into this version's shape on the way out.
4. **`V::PREFIX`** puts the right version in the `Location` header.

And the router picks which version each route serves:

```rust
/// The menu's routes for one API version: reads for everyone, writes for the kitchen.
/// The same handlers serve every version; `V` decides the shapes at the door.
pub fn router<S, V>(staff_key: StaffKey) -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    MenuService: FromRef<S>,
    V: MenuVersion,
{
    let public = Router::new()
        .route("/menu", get(list::<V>))
        .route("/menu/specials", get(specials::<V>))
        .route("/menu/{id}", get(get_one::<V>));

    let kitchen = Router::new()
        .route("/menu", post(add::<V>))
        .route("/menu/{id}", patch(change::<V>).delete(remove))
        .route_layer(middleware::from_fn_with_state(staff_key, kitchen_only));

    public.merge(kitchen)
}
```

**`get_one::<V>`** is the turbofish from lesson 6: "the `get_one` for this `V`". The compiler makes a separate copy of each handler for `V1` and for `V2`, each with its own types, checked separately. There's no `match version` anywhere, and no way to send a v2 dish from a v1 route: the types wouldn't line up. (`remove` has no `V`: it sends nothing back but a 204, so it's the same in every version.)

### The list, per version

Lesson 9's `ListParams` becomes generic too, so `sort` and `fields` accept each version's own names:

```rust
/// `GET /menu`'s query string, in this version's own words.
#[derive(Deserialize, Validate)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct ListParams<V: MenuVersion> {
    #[serde(default = "twenty")]
    #[validate(range(min = 1, max = 100, message = "must be from 1 to 100"))]
    limit: i64,
    #[serde(default)]
    #[validate(range(min = 0, message = "can't be negative"))]
    offset: i64,
    available: Option<bool>,
    special: Option<bool>,
    #[validate(range(min = 1, message = "must be at least 1"))]
    min_price: Option<i64>,
    #[validate(range(min = 1, message = "must be at least 1"))]
    max_price: Option<i64>,
    #[validate(length(min = 1, max = 80, message = "must be 1 to 80 characters"))]
    q: Option<String>,
    #[validate(custom(function = "known_sort::<V>"))]
    sort: Option<String>,
    #[validate(custom(function = "known_fields::<V>"))]
    fields: Option<String>,
    #[serde(skip)]
    version: PhantomData<V>,
}
```

1. **`PhantomData<V>`** is a field of size zero that says "this struct is about `V`". A struct can't have a type parameter it never uses, and nothing else in `ListParams` mentions `V`. `#[serde(skip)]` means it's never read from the query.
2. **`custom(function = "known_sort::<V>")`** calls the rule for this version: `known_sort` uses `V::field_named`, so `sort=priceNaira` is valid on v1 and refused on v2, with a message listing v2's names.

`list` reads `min_price` and `max_price` with `V::price_filter`, and `only_fields` trims the `V::Dish`'s JSON, whichever shape it is.

### Orders

Orders get the same treatment, with a smaller trait, because only the total differs. `src/orders/versions.rs`:

```rust
pub trait OrderVersion: Send + Sync + 'static {
    const PREFIX: &'static str;
    type Order: Serialize + From<Order> + Send;
}

impl OrderVersion for crate::menu::V1 {
    const PREFIX: &'static str = "/v1";
    type Order = OrderV1;
}

impl OrderVersion for crate::menu::V2 {
    const PREFIX: &'static str = "/v2";
    type Order = OrderV2;
}
```

**One type can implement two traits.** `V1` is a `MenuVersion` *and* an `OrderVersion`, so "version 1" is one name across the whole API. `OrderV1` has `total_naira`, `OrderV2` has `total: Amount`, each with a `From<Order>`. The order handlers become generic in the same way: `place::<V>`, `get_one::<V>`, `list::<V>`, `set_status::<V>`.

## Step 5: a bug the new shape found
<!-- bite: 473b2167-7106-4b3f-9af2-bd3192b59577 -->

Send v2 a price of 0 kobo, and the answer is a 400 `invalid-fields`... with no `errors` list at all. The client is told something is wrong, and not what.

Here's why. Lesson 7's `From<ValidationErrors>` read `errors.field_errors()`, which gives the errors of *this* struct's own fields. But `price.amount` belongs to the nested `Amount`, and validator reports it as a whole struct of errors under `price`. `field_errors()` skips those. Nothing nested existed until now, so nobody noticed.

The fix walks the errors all the way down, in `src/http/extract.rs`:

```rust
/// Every bad field, including inside nested structs (`price.amount`) and lists (`items[0].quantity`).
fn collect_fields(errors: &ValidationErrors, prefix: &str, out: &mut Vec<FieldError>) {
    for (field, kind) in errors.errors() {
        let name = if prefix.is_empty() { camel_case(field) } else { format!("{prefix}.{}", camel_case(field)) };
        match kind {
            ValidationErrorsKind::Field(errors) => out.extend(errors.iter().map(|e| FieldError {
                field: name.clone(),
                message: e.message.as_deref().unwrap_or(&e.code).to_string(),
            })),
            ValidationErrorsKind::Struct(inner) => collect_fields(inner, &name, out),
            ValidationErrorsKind::List(items) => {
                for (i, inner) in items {
                    collect_fields(inner, &format!("{name}[{i}]"), out);
                }
            }
        }
    }
}
```

and `From<ValidationErrors>` starts with `let mut fields = Vec::new(); collect_fields(&errors, "", &mut fields);`, then sorts as before.

1. **`ValidationErrorsKind`** has three variants: errors on a plain field, a nested struct's errors, or a list's errors by position. The `match` must handle all three, so lists (lesson 17's basket of several dishes) are covered before they exist.
2. **It calls itself** for nested structs and lists: a **recursive** function. Each level adds its name to the `prefix`, so `price` then `amount` becomes `price.amount`.

Now a v2 dish with no name and a price of 0:

```text
"errors":[{"field":"name","message":"must be 1 to 80 characters"},
          {"field":"price.amount","message":"must be from 1 kobo to ₦1,000,000"}]
```

## Step 6: both versions in one app
<!-- bite: 1abb399d-3bfb-4e93-bec1-a43d740b4a2f -->

In `src/lib.rs`'s `app`:

```rust
    let key = &state.staff_key;
    let v1 = Router::new()
        .merge(menu::router::<_, menu::V1>(key.clone()))
        .merge(orders::router::<_, menu::V1>(key.clone()))
        .layer(middleware::from_fn_with_state(state.v1.clone(), http::deprecated));
    let v2 = Router::new()
        .merge(menu::router::<_, menu::V2>(key.clone()))
        .merge(orders::router::<_, menu::V2>(key.clone()));

    Router::new()
        .route("/", get(|| async { "Mama Put is open!" }))
        .nest("/v1", v1.clone())
        .merge(v1) // the old paths with no version, /menu and /orders, are v1 too
        .nest("/v2", v2)
        .fallback(http::route_not_found)
        .method_not_allowed_fallback(http::method_not_allowed)
        .with_state(state)
        .layer(layers)
```

1. **`menu::router::<_, menu::V1>(...)`**: the `_` lets the compiler work out the state type (it's `AppState`, from `with_state` below); `menu::V1` picks the version.
2. **`v1` gets a layer of its own**, the deprecation middleware (step 7), so every v1 route carries it and no v2 route does.
3. **`.nest("/v1", v1.clone())`** puts every v1 route under `/v1`: `/menu/{id}` becomes `/v1/menu/{id}`.
4. **`.merge(v1)` as well.** Clients from before this lesson call `/menu` and `/orders`, with no version. Those *are* v1, so the same v1 router is merged in at the root too. A route clients use is a promise; you don't break it because you've started numbering versions. (A `Router` is cheap to clone: its routes are shared, not copied.)

From a run of this lesson's code:

```bash
curl -s localhost:8080/v1/menu/2
# {"data":{"id":2,"name":"Beans and plantain","priceNaira":1200,"available":true,"special":false,"portionsLeft":22}}
curl -s localhost:8080/v2/menu/2
# {"data":{"id":2,"name":"Beans and plantain","price":{"amount":120000,"currency":"NGN"},"available":true,...}}
curl -s localhost:8080/menu/2
# the v1 answer: the old path still works

curl -s -X POST localhost:8080/v2/menu -H 'x-staff-key: sekret' -H 'content-type: application/json' \
  -d '{"name":"Puff puff","price":{"amount":20050,"currency":"NGN"},"portionsLeft":60}'
# 201 {"data":{"id":7,"name":"Puff puff","price":{"amount":20050,"currency":"NGN"},...}}
curl -s localhost:8080/v1/menu/7
# {"data":{"id":7,"name":"Puff puff","priceNaira":200,...}}
```

That last one is worth noticing. v1 can only show whole naira, so ₦200.50 shows as 200. That's v1's honest limit, and a good reason for its clients to move. A unit test in `versions.rs` pins it down:

```rust
    #[test]
    fn v1_can_only_show_whole_naira() {
        let dish = Dish {
            id: 1,
            name: "Puff puff".into(),
            price: Kobo(20050),
            available: true,
            special: false,
            portions_left: 60,
        };
        assert_eq!(DishV1::from(dish.clone()).price_naira, 200);
        assert_eq!(DishV2::from(dish).price.amount, 20050);
    }
```

The lists speak each version's language:

```bash
curl -s 'localhost:8080/v2/menu?sort=-price&fields=name,price&limit=2&maxPrice=200000'
# {"data":[{"id":1,"name":"Jollof rice","price":{"amount":150000,"currency":"NGN"}},...],"meta":{...}}
curl -s 'localhost:8080/v2/menu?sort=priceNaira'
# 400 ..."errors":[{"field":"sort","message":"each name must be one of: id, name, price, available, special, portionsLeft"}]
curl -s 'localhost:8080/v1/menu?sort=-priceNaira&fields=name,priceNaira&limit=2&maxPrice=2000'
# {"data":[{"id":1,"name":"Jollof rice","priceNaira":1500},{"id":2,"name":"Beans and plantain","priceNaira":1200}],...}
```

`maxPrice=200000` on v2 and `maxPrice=2000` on v1 are the same ₦2,000.

### The header way, in a sentence

To choose the version from an `Api-Version` header instead of the path, you'd keep the two routers exactly as they are, and put a small middleware in front that reads the header and sends the request to one or the other (practice 4). Two things to get right if you do: send **`Vary: Api-Version`**, so caches know the answer depends on that header, and default to **the oldest supported version** when there's none, so clients that never heard of versioning keep getting what they always got. With path versioning, you need neither: the URLs differ. That's one of the quiet reasons it's popular.

## Step 7: deprecating v1
<!-- bite: 79200e39-9665-4fd1-bdae-e1a1af09bbe3 -->

A version you never retire is a version you maintain forever. Retiring one well is four things.

**1. Tell clients, in every response.** Two standard headers do it. `Deprecation` (RFC 9745) says when the version was deprecated, as `@` and a Unix time. `Sunset` (RFC 8594) says when it stops working, as an HTTP date. A `Link` points to the migration guide. `src/http/deprecation.rs`:

```rust
/// When a version was deprecated, when it stops, and where to read about moving on.
#[derive(Clone)]
pub struct Deprecation {
    pub version: &'static str,
    pub deprecated_at: Timestamp,
    pub sunset_at: Timestamp,
    pub guide: &'static str,
    pub clock: Clock,
}

/// Wraps a whole version. Before the sunset: answers as usual, with headers saying it's going.
/// After: 410 Gone, saying where to go instead.
pub async fn deprecated(State(policy): State<Deprecation>, req: Request, next: Next) -> Response {
    if policy.clock.now() >= policy.sunset_at {
        let detail = format!(
            "API {} stopped working on {}. See {}",
            policy.version,
            policy.sunset_at.strftime("%-d %B %Y"),
            policy.guide
        );
        return ApiError::new(StatusCode::GONE, "version-retired", "This API version has been retired", detail)
            .into_response();
    }

    // Who's still on it? This line becomes a metric in lesson 37.
    let client = req.headers().get(header::USER_AGENT).and_then(|v| v.to_str().ok()).unwrap_or("").to_owned();
    // Inside `nest("/v1", ...)` the path has lost its `/v1`; the original is kept for us.
    let path = req.extensions().get::<OriginalUri>().map_or(req.uri().path(), |uri| uri.path()).to_owned();
    tracing::info!(version = policy.version, path, client, "deprecated version used");

    let mut response = next.run(req).await;
    let headers = response.headers_mut();
    let deprecation = format!("@{}", policy.deprecated_at.as_second());
    let sunset = policy.sunset_at.strftime("%a, %d %b %Y %H:%M:%S GMT").to_string();
    let link = format!("<{}>; rel=\"deprecation\"", policy.guide);
    for (name, value) in [("deprecation", deprecation), ("sunset", sunset), ("link", link)] {
        headers.insert(name, HeaderValue::from_str(&value).expect("these headers are plain text"));
    }
    response
}
```

1. **It takes a `Clock`**, for the same reason the orders service does: so a test can check "after the sunset it answers 410" without waiting until June.
2. **`strftime`** formats a moment as text. `%a, %d %b %Y %H:%M:%S GMT` is the date format HTTP headers use; a `Timestamp` is always formatted in UTC, which is what `GMT` means here. `as_second()` is the Unix time.
3. **`OriginalUri`**: inside a nested router, Axum strips the prefix, so `req.uri().path()` is `/menu/2` for a call to `/v1/menu/2`. The first run of this lesson's code logged exactly that, and couldn't tell `/v1/menu/2` from the old `/menu/2`. Axum keeps the full URI in the request's extensions as `OriginalUri`; `map_or` falls back to the plain path if it's not there.

The policy is built in `main` and carried in `AppState`, in a new field `v1: http::Deprecation`:

```rust
    let v1 = Deprecation {
        version: "v1",
        deprecated_at: "2026-12-01T00:00:00Z".parse()?,
        sunset_at: "2027-06-01T00:00:00Z".parse()?,
        guide: "https://mamaput.example/docs/moving-to-v2",
        clock: Clock::system(),
    };
    let state = AppState { menu, orders, staff_key: StaffKey::from_env()?, v1 };
```

```bash
curl -si localhost:8080/v1/menu/1 | grep -iE "^(deprecation|sunset|link)"
# deprecation: @1796083200
# sunset: Tue, 01 Jun 2027 00:00:00 GMT
# link: <https://mamaput.example/docs/moving-to-v2>; rel="deprecation"
```

and v2's responses have none of them.

**2. Measure who's still on it.** That log line fires for every v1 request, with the client's user agent:

```text
INFO request{method=GET path="/v1/menu/2" ...}: mama_put::http::deprecation: deprecated version used version="v1" path="/v1/menu/2" client="curl/8.18.0"
```

In lesson 37 it becomes a proper metric, "v1 requests per day". You switch v1 off when that number is near zero, not just because the calendar says so.

**3. Tell people directly.** Headers are for programs. Humans need an email, a changelog entry, a note in the docs. If the phone app is yours, ship an update that moves to v2 *before* the sunset.

**4. Switch it off kindly.** From the sunset, the middleware answers **410 Gone** with a problem saying what happened and where to go. A clear 410 is far better than a confusing 404 or, worse, quietly sending v2 data to a v1 client. Two tests check both sides of the date, at the bottom of `deprecation.rs`:

```rust
    async fn ask_at(now: &str) -> Response {
        let app = Router::new()
            .route("/menu", get(|| async { "the menu" }))
            .layer(middleware::from_fn_with_state(policy_at(now), deprecated));
        app.oneshot(Request::get("/menu").body(Body::empty()).unwrap()).await.unwrap()
    }

    #[tokio::test]
    async fn before_the_sunset_it_works_and_warns() {
        let response = ask_at("2027-01-15T12:00:00Z").await;
        assert_eq!(response.status(), StatusCode::OK);
        assert_eq!(response.headers()["sunset"], "Tue, 01 Jun 2027 00:00:00 GMT");
    }

    #[tokio::test]
    async fn from_the_sunset_it_is_gone() {
        let response = ask_at("2027-06-01T00:00:00Z").await;
        assert_eq!(response.status(), StatusCode::GONE);
    }
```

(`policy_at(now)` builds v1's policy with `Clock::fixed` stopped at `now`.) **`oneshot`** sends one request through a router and gives back the response, with no network and no port: a `Router` is a Tower `Service`, and `tower::ServiceExt::oneshot` calls it once. It needs tower's `util` feature: `cargo add tower --features util`. Lesson 16 builds the whole test suite on it.

`cargo test` now runs 11: the database tests from lesson 8, the unit tests, and these two.

## The Rust in this lesson
<!-- bite: 60c2cc0a-35be-4de6-862e-7fca1ecc8356 -->

1. **Domain types and wire types**, connected with `From` both ways, and `.into()`.
2. **A newtype for money, `struct Kobo(pub i64)`**, with **`#[sqlx(transparent)]`** to store it as what's inside.
3. **Traits with associated types, `type Dish: Serialize + From<Dish> + Send;`**: each implementation chooses its own type, with bounds.
4. **Associated constants, `const PREFIX: &'static str;`**.
5. **Default methods** in a trait, using `Self::PRICE`.
6. **Empty structs as type-level names, `pub struct V1;`**, and one type implementing two traits.
7. **Generic handlers, `async fn get_one<V: MenuVersion>(...)`**, chosen with the turbofish, `get(get_one::<V>)`.
8. **`PhantomData<V>`**: a zero-size field that lets a struct mention a type it doesn't store.
9. **`#[validate(nested)]`**, and **`ValidationErrorsKind`**'s three variants.
10. **A recursive function**, `collect_fields`, building names as it goes down.
11. **`Router::nest`**, and **`OriginalUri`** for the full path inside a nested router.
12. **`Timestamp::strftime`, `as_second`, and parsing a `Timestamp` from text with `.parse()?`**.
13. **`tower::ServiceExt::oneshot`**: one request through a router, in a test.

## Your project so far
<!-- bite: 306ccf3f-5a96-470b-a6e7-e48a80c8bfee -->

```text
mama-put/
├── Cargo.toml             ← tower + util
├── migrations/
│   └── 0004_prices_in_kobo.sql
└── src/
    ├── main.rs            ← + the v1 Deprecation policy
    ├── lib.rs             ← + pub mod money; AppState.v1; /v1 (deprecated, also at the root) and /v2
    ├── money.rs           ← Kobo, Currency, Amount
    ├── http/
    │   ├── deprecation.rs ← Deprecation, deprecated (headers, then 410), 2 oneshot tests
    │   └── extract.rs     ← collect_fields: nested and list errors as price.amount, items[0]
    ├── menu/
    │   ├── model.rs       ← domain only: Dish (price: Kobo), NewDish, DishChanges, DishField::Price
    │   ├── versions.rs    ← MenuVersion, V1, V2; DishV1/V2, NewDishV1/V2, DishChangesV1/V2; 3 tests
    │   ├── handlers.rs    ← every handler generic over V; ListParams<V>
    │   └── store.rs       ← price_kobo AS "price: Kobo"
    └── orders/
        ├── model.rs       ← Order { total: Kobo }; NewOrder and StatusChange shared by both versions
        ├── versions.rs    ← OrderVersion for V1 and V2; OrderV1, OrderV2
        └── handlers.rs    ← every handler generic over V
```

## Common mistakes
<!-- bite: 0aaca994-af10-437e-b3f9-f7a7b68a680b -->

1. **Changing a field's meaning without changing its name.** `price` in kobo where it used to be naira: nothing errors, and every old client shows prices 100 times too big.
2. **One struct for the database, the code and the wire.** A rename in Rust renames your public API. Keep domain and wire types apart.
3. **A `match version` inside handlers.** It grows with every version and every handler. Let the trait's associated types carry the difference.
4. **Breaking the unversioned paths.** Clients use `/menu`. Keep serving it, as v1.
5. **Defaulting to the newest version** when a client doesn't say. Every new version then breaks every old client.
6. **Header versioning without `Vary`.** A cache hands the v2 answer to a v1 client.
7. **Switching a version off by date alone.** Measure who's still using it.
8. **A 404 after the sunset.** Say 410 Gone, and where to go.
9. **Trusting `req.uri()` inside a nested router.** The prefix is gone; use `OriginalUri`.

## Check your understanding
<!-- bite: 5f22b18d-6d30-4f83-9b84-3338a2efd91d -->

1. Which is more dangerous: renaming `priceNaira` to `price`, or keeping the name `priceNaira` and storing kobo in it? Why?
2. Why does `Dish` no longer derive `Serialize`?
3. In `MenuVersion`, what does `type NewDish: DeserializeOwned + Validate + Into<NewDish> + Send;` promise, and who chooses the type?
4. How does `ValidatedJson<V::NewDish>` read `priceNaira` on one route and `price` on another, from the same line of code?
5. Why does `ListParams<V>` need a `PhantomData<V>` field?
6. A v2 dish with a price of 0 got a 400 with no `errors`. Why, and what fixed it?
7. Why is the v1 router both nested under `/v1` and merged at the root?
8. What does `deprecated` log, and why is that line important for retiring v1?

<details>
<summary>Answers, after your attempt</summary>

1. Keeping the name. A renamed field breaks old clients loudly: the field they read is missing. The same name with a new meaning breaks them silently: they show ₦150,000 jollof and nothing errors.
2. Because it's the domain type, shaped for the code, and it's never sent as it is. Each version has its own wire type to send. If `Dish` were still `Serialize`, a handler could send it straight out and leak the code's shape into the API.
3. That whatever type a version picks can be read from JSON into owned data, has validator rules, can be turned into the domain `NewDish`, and can move between threads. Each version chooses its own type in its `impl MenuVersion`: `NewDishV1` for `V1`, `NewDishV2` for `V2`.
4. The handler is generic: `add::<V1>` and `add::<V2>` are two separate copies made by the compiler. In the first, `V::NewDish` is `NewDishV1`, which reads `priceNaira`; in the second, it's `NewDishV2`, which reads `price`.
5. Because a struct can't have a type parameter it doesn't use, and nothing else in `ListParams` mentions `V`. The parameter is there so the custom rules can be `known_sort::<V>`. `PhantomData<V>` uses `V` without storing anything, and `#[serde(skip)]` keeps it out of the query.
6. validator reports a nested struct's errors as a struct of errors under `price`, and lesson 7's code only read `field_errors()`, this struct's own fields, so `price.amount` was skipped. `collect_fields` walks nested structs and lists too, building names like `price.amount`.
7. Nested under `/v1` for clients that ask for v1 by name, and merged at the root because clients from before versioning call `/menu` and `/orders`, and those are v1. Both go through v1's deprecation layer.
8. The version, the full path and the client's user agent, for every v1 request. Counting those lines (lesson 37 makes it a metric) tells you who still uses v1, so you can switch it off when almost nobody does, not just when the date comes.

</details>

## Practice
<!-- bite: 20d956c1-8687-4f6f-ad3a-37b0755962ed -->

1. Add a `description: Option<String>` to dishes, in **both** versions, without a new version. Which kind of change from step 1 is it, and what does `deny_unknown_fields` mean for clients that send it to an old server?
2. Write a `#[sqlx::test]` that adds a dish through v2's types at ₦200.50 and reads it back through v1's, checking the 200.
3. Make the `Deprecation` log line skip the user agent when it's empty, and add `version` to the request's span instead of each line.
4. Choose the version from an `Api-Version` header instead: a `from_fn` middleware that reads it (default `1`), and calls one of two routers, built from the same `menu::router::<_, V1>` and `::<_, V2>`. Send `Vary: Api-Version`. What's harder to see in the logs now?
5. Set the sunset to yesterday in `main`, and check every v1 path, including `/menu`, now answers 410 with the guide's link, while v2 is untouched.

**Done when** prices are stored in kobo, `Dish` and `Order` are domain types with no serde, v1 and v2 are served by the same generic handlers with each version's wire types, v1 is also served at the old unversioned paths, nested validation errors are reported as `price.amount`, every v1 response carries `Deprecation`, `Sunset` and `Link`, v1 answers 410 after its sunset, and `cargo test` passes.

## Before moving on
<!-- bite: 86641df1-368e-496f-9914-ec684f42456c -->

Mama Put can now change without breaking anyone. The code has its own types, each version has its shapes, and the handlers are written once, with the compiler making one copy per version. v1 tells every client when it's going, logs who still uses it, and leaves politely on the date.

The phone team has a new question, though: "what exactly does v2 send and accept?" Right now the honest answer is "read the Rust". Next lesson: API docs, with an OpenAPI description generated from the same types the handlers use, so the docs can't drift from the code.

## Related
<!-- bite: b565f012-37a5-466b-8d43-82ef0099282d -->

- [[backend/frameworks/axum/11-api-docs|Next: API Docs]]
- [[backend/frameworks/net-http/10-versioning|The same lesson in net/http]] — a `Version` value passed to handlers, and a mux inside a mux
- [[backend/02-api-design/index|API Design]] — resources, and what makes a change breaking
- [[languages/03-rust/09-traits|Traits]] — associated types, constants and default methods

## About this lesson
<!-- bite: 26639003-19c1-423e-af71-a7fd6739f485 -->

**Level:** Advanced. Lesson 10 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, sqlx 0.9, validator 0.21 and jiff 1.0. Covers breaking and safe changes, the four ways to name a version, domain types separated from per-version wire types, a `Kobo` newtype with `#[sqlx(transparent)]` and a migration to kobo that checked queries flag, a `MenuVersion` trait with associated types, constants and default methods so handlers are written once and instantiated per version with the turbofish, `PhantomData` for a generic query struct, `#[validate(nested)]` and a recursive walk of `ValidationErrorsKind` for `price.amount`, v1 nested under `/v1` and merged at the root, a deprecation middleware with `Deprecation`, `Sunset` and `Link` headers, `OriginalUri` inside nested routers, a 410 after the sunset tested with a fixed clock and `oneshot`, and what header versioning would need (`Vary`, defaulting to the oldest).
