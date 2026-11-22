---
id: 2067d878-5908-4df1-a4fd-f0eef8eba075
---

# GraphQL

**GraphQL is a way of asking an API for data where the client writes down exactly which fields it wants, across several related things, and gets back exactly that, in one request.** A REST API has fixed answers at fixed addresses; a GraphQL API has one address and a typed description of everything it can answer, called the **schema**. In Rust, `async-graphql` builds that schema from ordinary Rust types, so the schema can't disagree with the code that answers it.

## Before you start
<!-- bite: 0fff609d-5b61-4394-856a-dcbfcd9b38d6 -->

You should have:

1. Finished [[backend/frameworks/axum/20-real-time|lesson 20]], so `cargo test` runs 69 tests.

After this lesson you will be able to:

1. Say when GraphQL helps, and when REST is simpler.
2. Build a GraphQL schema from Rust types with async-graphql, and publish it as a file that's checked against the code.
3. Write resolvers that call the same services as REST, with the same rules and the same error codes.
4. Fix the N+1 problem with a dataloader.
5. Refuse queries that would be too much work, before running them.
6. Test GraphQL through the whole app and below it.

## What to install
<!-- bite: 3dbc1ed1-8c99-4555-ac46-1f1d9a166b2d -->

```bash
cargo add async-graphql --no-default-features --features dataloader
cargo add async-graphql-axum
```

1. **`async-graphql`** is the GraphQL server library most Rust projects use. Its default features include a file-upload type, an email checker and two in-browser playgrounds, none of which we need, so we turn them off and add only `dataloader` (step 5). Every feature you don't turn on is code you don't have to trust.
2. **`async-graphql-axum`** connects it to Axum: an extractor for GraphQL requests and a response type.

## Where we stopped
<!-- bite: 196929d4-d347-4fba-8bea-4a3ea7b2e3e7 -->

The new phone app's order screen shows an order, its dish, and the customer's last few orders underneath, each with its dish. With REST, that's:

1. `GET /v2/orders/42`
2. `GET /v2/menu/1` for the dish
3. `GET /v2/auth/me`
4. `GET /v2/orders?limit=3`, then a `GET /v2/menu/{id}` for each of those dishes.

Six or seven round trips on a 3G connection in a market, each one waiting for the last. And each answer carries fields the screen doesn't show. Lesson 9's `fields=` helps with the extra fields; it can't help with the round trips.

The phone team asks: can we ask for all of it, in one go?

## The kid version
<!-- bite: 5db3aa50-74a2-46b5-9917-3808171d62ae -->

At a REST restaurant, the menu has set plates. Plate 1: rice, stew, chicken. Plate 2: beans, plantain. If you want rice *and* plantain, you order two plates and leave half of each.

At a GraphQL restaurant, you write your own order on a slip: "rice, plantain, one piece of chicken, and the drinks list". The kitchen knows everything it can make, and sends exactly that, on one tray.

**Where the picture stops working.** A greedy customer could write "every dish, and for each dish, every customer who ordered it, and for each customer, every dish *they* ordered..." on one slip. A real kitchen would laugh. Our server has to be taught to refuse, and step 7 is how.

## Terms used in this lesson
<!-- bite: 3fe2c437-0f17-40de-86a7-442009a29c6f -->

1. **Schema**: This is the typed description of everything the API offers, written in GraphQL's own language, called **SDL** (schema definition language).
2. **Type**: This is a shape, like `Dish`, with fields `id`, `name` and `price`.
3. **Query**: This is a read. The client sends a query document listing the fields it wants.
4. **Mutation**: This is a write, like `placeOrder`.
5. **Resolver**: This is the code that works out one field's value. The server calls resolvers to build the answer.
6. **Code-first** and **schema-first**: Code-first means writing Rust types and letting the library produce the schema, as async-graphql does. Schema-first means writing the SDL by hand and generating code from it, as Go's gqlgen does.
7. **N+1 problem**: This is when fetching a list of N things runs one query for the list, then N more queries, one per item, for something each item needs.
8. **Dataloader**: This is a helper that collects every "load dish 1", "load dish 4", "load dish 1" made at nearly the same moment, and turns them into one query.
9. **Connection**: This is GraphQL's usual shape for a page of a list: `edges`, each with a `node` and a `cursor`, and `pageInfo`.
10. **Complexity**: This is a number worked out for each query before it runs, roughly "how much work could this be?". Queries over a limit are refused.

## Step 1: when GraphQL helps
<!-- bite: 9def4d8e-1315-4831-b061-1bcd7b58705b -->

GraphQL is good at one thing: **a client that needs many related things, shaped its own way**. A phone screen that shows an order, its dish and five other orders is exactly that. So are dashboards, and apps with many different screens built by a separate team.

It's not free. Every request can be different, so HTTP caching (lesson 19's `ETag` and `Cache-Control`) mostly stops working; a GraphQL `POST` isn't cached by anything in between. Errors come back with status 200 (step 6), so monitoring needs to look inside responses. And clients can ask for expensive combinations you never planned for (step 7).

So Mama Put keeps REST for what REST is good at (the cached public menu, webhooks, file uploads, simple integrations) and adds GraphQL for the phone app's screens. Both call the same services, so a rule lives in one place and both doors obey it.

## Step 2: the types
<!-- bite: ea286c37-01ad-4705-9c93-62b8e5ce6bd3 -->

async-graphql is **code-first**: we write Rust, and it writes the schema. Each GraphQL type wraps one of our domain types and says, field by field, what clients see. `src/graph/types.rs` starts:

```rust
//! The GraphQL types. Each wraps a domain type and says, field by field, what clients may see.

use async_graphql::{Context, Enum, Error, InputObject, Object, SimpleObject, ID, connection::{Connection, Edge}, dataloader::DataLoader};
use axum::http::StatusCode;

use super::{
    errors::{gql, number},
    loaders::DishLoader,
};
use crate::{
    auth::User,
    http::ApiError,
    menu::Dish,
    money::Kobo,
    orders::{Order, OrderFilter, OrderService},
};

/// Money in kobo, as in v2: ₦1 is 100.
#[derive(SimpleObject)]
pub struct Money {
    amount: i64,
    currency: &'static str,
}

impl From<Kobo> for Money {
    fn from(kobo: Kobo) -> Self {
        Money { amount: kobo.0, currency: "NGN" }
    }
}

pub struct DishNode(pub Dish);

#[Object(name = "Dish")]
impl DishNode {
    async fn id(&self) -> ID {
        ID(self.0.id.to_string())
    }
    async fn name(&self) -> &str {
        &self.0.name
    }
    async fn price(&self) -> Money {
        self.0.price.into()
    }
    async fn available(&self) -> bool {
        self.0.available
    }
    async fn special(&self) -> bool {
        self.0.special
    }
    async fn portions_left(&self) -> i32 {
        self.0.portions_left
    }
    async fn photo_url(&self) -> Option<String> {
        self.0.photo.as_ref().map(|name| format!("/uploads/{name}"))
    }
    async fn thumbnail_url(&self) -> Option<String> {
        self.0.thumb.as_ref().map(|name| format!("/uploads/{name}"))
    }
}

/// Where an order has got to.
// `remote` makes this our own `orders::Status`, so `.into()` converts between them.
#[derive(Enum, Clone, Copy, PartialEq, Eq)]
#[graphql(name = "OrderStatus", remote = "crate::orders::Status")]
pub enum OrderStatus {
    Pending,
    Ready,
    Collected,
}
```

1. **`#[derive(SimpleObject)]`** turns a struct into a GraphQL type, one field each. Good for plain data like `Money`.
2. **`#[Object]` on an `impl`** is for types whose fields need code. Each `async fn` is a field, and its body is the resolver. `DishNode` wraps our `Dish`, so the domain type stays free of GraphQL, the way lesson 10 kept it free of JSON. Field names become camelCase on their own: `portions_left` is `portionsLeft`.
3. **`ID`** is GraphQL's type for identifiers. On the wire it's always a string, `"42"`, even though ours are numbers inside, so clients never do maths on an id. `ID(self.0.id.to_string())` builds one.
4. **`#[derive(Enum)]` with `remote`** makes a GraphQL enum that converts to and from our own `orders::Status`, so `self.0.status.into()` just works. GraphQL enum values are written in capitals by convention: `PENDING`.
5. **Doc comments become the schema's descriptions**, which every GraphQL tool shows to clients. So `///` is for them ("Where an order has got to") and `//` is for us. I learned that from reading the first schema it wrote, which told clients about "lesson 15's key".

Then orders, users and the mutation's input and output:

```rust
pub struct OrderNode(pub Order);

#[Object(name = "Order")]
impl OrderNode {
    async fn id(&self) -> ID {
        ID(self.0.id.to_string())
    }
    async fn quantity(&self) -> i32 {
        self.0.quantity
    }
    async fn total(&self) -> Money {
        self.0.total.into()
    }
    async fn status(&self) -> OrderStatus {
        self.0.status.into()
    }
    async fn paid(&self) -> bool {
        self.0.paid
    }
    /// The dish ordered.
    // Through the request's loader: twenty orders cost one query for their dishes, not twenty.
    async fn dish(&self, ctx: &Context<'_>) -> Result<DishNode, Error> {
        let loader = ctx.data_unchecked::<DataLoader<DishLoader>>();
        match loader.load_one(self.0.dish_id).await {
            Ok(Some(dish)) => Ok(DishNode(dish)),
            Ok(None) => Err(gql(ApiError::internal(format!("order {} points at no dish", self.0.id)))),
            Err(e) => Err(gql(ApiError::internal(e))),
        }
    }
}

pub struct UserNode(pub User);

#[Object(name = "User")]
impl UserNode {
    async fn id(&self) -> ID {
        ID(self.0.id.to_string())
    }
    async fn name(&self) -> &str {
        &self.0.name
    }
    /// This user's orders, oldest first.
    // A list costs `first` times what each item asks for.
    #[graphql(complexity = "first as usize * child_complexity")]
    async fn orders(
        &self,
        ctx: &Context<'_>,
        #[graphql(default = 10, validator(minimum = 1, maximum = 50))] first: i32,
        after: Option<String>,
    ) -> Result<Connection<i64, OrderNode>, Error> {
        let after = after.as_ref().map(|cursor| number(&ID(cursor.clone()))).transpose()?;
        let filter = OrderFilter { status: None, customer_id: Some(self.0.id), after, limit: first.into() };
        let (orders, next) = ctx.data_unchecked::<OrderService>().list(&filter).await.map_err(gql)?;
        let mut page = Connection::new(after.is_some(), next.is_some());
        page.edges.extend(orders.into_iter().map(|order| Edge::new(order.id, OrderNode(order))));
        Ok(page)
    }
}

#[derive(InputObject)]
pub struct PlaceOrderInput {
    pub dish_id: ID,
    #[graphql(validator(minimum = 1, maximum = 20))]
    pub quantity: i32,
    /// A name you choose for this attempt. Send the same key again (after a timeout, say) and you get
    /// the same order back, not a second one.
    #[graphql(validator(min_length = 1, max_length = 255))]
    pub idempotency_key: String,
}

/// What placing an order returns.
// A payload, not the order itself, so it can gain fields without breaking anyone.
#[derive(SimpleObject)]
pub struct PlaceOrderPayload {
    pub order: OrderNode,
}
```

Four things to notice:

1. **`Option<String>` is nullable, everything else isn't.** `photoUrl: String` may be `null`; `name: String!` never is. The Rust type decides, so the schema can't promise a non-null field the code might leave empty.
2. **`orders` takes arguments.** `#[graphql(default = 10, validator(minimum = 1, maximum = 50))]` gives `first` a default and limits, checked before the resolver runs, like lesson 6's `validator`.
3. **`Connection<i64, OrderNode>`** builds the standard page shape: `edges` with `node` and `cursor`, `pageInfo` with `hasNextPage` and `endCursor`. The cursor is the order's id, the same "after this id" as lesson 9's kitchen pages. (Clients must still treat it as an opaque string.)
4. **The mutation takes one `input` and returns a payload.** `placeOrder(input: PlaceOrderInput!)` can gain input fields later without breaking anyone, and `PlaceOrderPayload` can gain, say, a `checkoutUrl` next to `order`. Lesson 15's idempotency key is part of the input: GraphQL has one address for everything, so there's no route for lesson 15's middleware to sit on, and the key goes where the data goes.

## Step 3: resolvers call the same services
<!-- bite: 79153131-c2b9-4cd1-b183-8b5cae674763 -->

`src/graph/query.rs`:

```rust
use async_graphql::{Context, Error, ID, Object, connection::{Connection, CursorType, Edge}};

use super::{
    errors::{gql, number, who},
    types::{DishNode, OrderNode, PlaceOrderInput, PlaceOrderPayload, UserNode, bad_cursor},
};
use crate::{
    auth::PgAuthStore,
    http::ApiError,
    menu::{DishFilter, MenuError, MenuService},
    orders::{NewOrder, OrderService},
};

pub struct Query;

#[Object]
impl Query {
    /// The menu, a page at a time. Anyone may read it.
    #[graphql(complexity = "first as usize * child_complexity")]
    async fn menu(
        &self,
        ctx: &Context<'_>,
        #[graphql(default = 20, validator(minimum = 1, maximum = 100))] first: i32,
        after: Option<String>,
        #[graphql(validator(min_length = 1, max_length = 80))] search: Option<String>,
    ) -> Result<Connection<usize, DishNode>, Error> {
        // The cursor is the position of the last dish seen, so the page starts just after it.
        let start = match after {
            Some(cursor) => usize::decode_cursor(&cursor).map_err(|_| bad_cursor())? + 1,
            None => 0,
        };
        let filter = DishFilter {
            available: None,
            special: None,
            min_price: None,
            max_price: None,
            name_contains: search,
            sort: Vec::new(),
            limit: first.into(),
            offset: start as i64,
        };
        let (dishes, total) = ctx.data_unchecked::<MenuService>().list(&filter).await.map_err(gql)?;
        let mut page = Connection::new(start > 0, start + dishes.len() < total as usize);
        page.edges.extend(dishes.into_iter().enumerate().map(|(i, dish)| Edge::new(start + i, DishNode(dish))));
        Ok(page)
    }

    /// One dish, or `null` if there's no such dish.
    async fn dish(&self, ctx: &Context<'_>, id: ID) -> Result<Option<DishNode>, Error> {
        match ctx.data_unchecked::<MenuService>().get(number(&id)?).await {
            Ok(dish) => Ok(Some(DishNode(dish))),
            Err(MenuError::NotFound(_)) => Ok(None),
            Err(e) => Err(gql(e)),
        }
    }

    /// Whoever is logged in, or `null` for nobody.
    async fn me(&self, ctx: &Context<'_>) -> Result<Option<UserNode>, Error> {
        let Ok(who) = who(ctx) else { return Ok(None) };
        let user = ctx.data_unchecked::<PgAuthStore>().find(who.user_id).await.map_err(ApiError::internal).map_err(gql)?;
        Ok(user.map(UserNode))
    }

    /// One of your orders.
    // Someone else's is "not found", as in REST. Nullable on purpose: if it fails, only this field
    // is lost, and the rest of the answer survives.
    async fn order(&self, ctx: &Context<'_>, id: ID) -> Result<Option<OrderNode>, Error> {
        let order = ctx.data_unchecked::<OrderService>().get(number(&id)?, who(ctx)?).await.map_err(gql)?;
        Ok(Some(OrderNode(order)))
    }
}

pub struct Mutation;

#[Object]
impl Mutation {
    /// Places an order for whoever is logged in.
    // The same rules as `POST /v2/orders`: they're in the service.
    async fn place_order(&self, ctx: &Context<'_>, input: PlaceOrderInput) -> Result<PlaceOrderPayload, Error> {
        let who = who(ctx)?;
        let new = NewOrder { dish_id: number(&input.dish_id)?, quantity: input.quantity };
        let orders = ctx.data_unchecked::<OrderService>();
        let order = orders.place(new, Some(who.user_id), Some(&input.idempotency_key)).await.map_err(gql)?;
        Ok(PlaceOrderPayload { order: OrderNode(order) })
    }
}
```

Read what isn't there: no SQL, no rules. `menu` calls `MenuService::list`, cached by lesson 19. `order` calls `OrderService::get`, which hides other customers' orders as "not found" (lesson 13). `placeOrder` calls `OrderService::place`, with the shop hours, the guarded `UPDATE` for the last plate, and lesson 15's database key. **GraphQL is another door into the same house.** A rule added to a service reaches both doors at once.

`ctx.data_unchecked::<MenuService>()` takes a service out of the schema's data (step 4 puts it there). "Unchecked" means "panic if it's missing", which is fine for things the schema is always built with; a test catches it the first time.

And the small helpers, `src/graph/errors.rs`:

```rust
use async_graphql::{Context, Error, ErrorExtensions, ID};
use axum::http::StatusCode;

use crate::{auth::Identity, http::ApiError};

/// Any of our errors, as GraphQL shows it: the same calm words and the same stable `code` as REST's
/// problem details. An internal error was already logged by `ApiError::internal`, and says nothing more.
pub(super) fn gql(err: impl Into<ApiError>) -> Error {
    let err: ApiError = err.into();
    Error::new(err.detail).extend_with(|_, extensions| extensions.set("code", err.code))
}

/// Who's asking, for fields that need a login.
pub(super) fn who(ctx: &Context<'_>) -> Result<Identity, Error> {
    ctx.data_opt::<Identity>().copied().ok_or_else(|| {
        gql(ApiError::new(StatusCode::UNAUTHORIZED, "unauthenticated", "Log in first", "This needs a login: send `Authorization: Bearer <token>`."))
    })
}

/// GraphQL's `ID` is always a string on the wire. Ours are numbers inside.
pub(super) fn number(id: &ID) -> Result<i64, Error> {
    id.parse().map_err(|_| gql(ApiError::new(StatusCode::BAD_REQUEST, "bad-id", "Not an id", format!("{:?} isn't one of our ids.", id.as_str()))))
}
```

`who` is how a resolver asks for a login; step 4 puts the `Identity` in each request. `number` turns an `ID` back into our number, refusing anything else with a clear `bad-id`.

## Step 4: serving it
<!-- bite: b790cf1e-a709-49c4-b5e5-910621c5d3ff -->

`src/graph/mod.rs`:

```rust
pub type MamaPutSchema = Schema<Query, Mutation, EmptySubscription>;

/// Builds the schema once, at start-up, with the services every resolver may use.
/// `introspection`: whether clients may download the schema (yes while developing; no in production).
pub fn schema(menu: MenuService, orders: OrderService, users: PgAuthStore, introspection: bool) -> MamaPutSchema {
    let builder = Schema::build(Query, Mutation, EmptySubscription)
        .data(menu)
        .data(orders)
        .data(users)
        .limit_depth(10) // no `dish { orders { dish { orders ... } } }` ten levels down
        .limit_complexity(300); // and no query that could be too much work: see `complexity` on lists
    if introspection { builder.finish() } else { builder.disable_introspection().finish() }
}

/// `POST /graphql`. POST only: no queries in URLs, and no GET that changes anything.
pub fn router<S>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    MamaPutSchema: FromRef<S>,
    MenuService: FromRef<S>,
    Keys: FromRef<S>,
{
    Router::new().route("/graphql", post(graphql))
}

async fn graphql(
    State(schema): State<MamaPutSchema>,
    State(menu): State<MenuService>,
    who: Option<AuthUser>,
    request: GraphQLRequest,
) -> GraphQLResponse {
    let request = prepare(request.into_inner(), who.map(|AuthUser(who)| who), menu);
    schema.execute(request).await.into()
}

/// What every request carries for its resolvers: who's asking, if anyone, and its own dataloader.
pub fn prepare(request: Request, who: Option<Identity>, menu: MenuService) -> Request {
    let request = match who {
        Some(who) => request.data(who), // resolvers that need a login find it here
        None => request,
    };
    // A fresh loader for every request: what it remembers must never outlive the request.
    request.data(DataLoader::new(loaders::DishLoader(menu), tokio::spawn))
}
```

1. **The schema is built once**, at start-up, with the services as its data. `MamaPutSchema` is cheap to clone (it's an `Arc` inside), so it goes in `AppState` like everything else.
2. **`POST` only.** async-graphql can also read queries from a `GET` with the query in the URL. We don't route `GET` at all: queries in URLs end up in logs, and a `GET` must never change anything, while GraphQL mutations would happily run.
3. **`Option<AuthUser>`.** Anyone may read the menu, so a missing token isn't an error here. But a token that *was* sent must be valid: lesson 12's `AuthUser` gets an `OptionalFromRequestParts` impl, in `src/auth/extract.rs`, which is how Axum 0.8 lets an extractor be optional:

```rust
/// `Option<AuthUser>`: `None` when no token was sent at all. A token that *was* sent must still be valid:
/// a bad one is a 401, never quietly treated as nobody.
impl<S> OptionalFromRequestParts<S> for AuthUser
where
    S: Send + Sync,
    Keys: FromRef<S>,
{
    type Rejection = ApiError;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Option<Self>, Self::Rejection> {
        if !parts.headers.contains_key(header::AUTHORIZATION) {
            return Ok(None);
        }
        <AuthUser as FromRequestParts<S>>::from_request_parts(parts, state).await.map(Some)
    }
}
```

   No `Authorization` header: `None`. A bad one: 401, never quietly "nobody". Otherwise a client with an expired token would see the menu, then be told it isn't logged in, with no idea why.
4. **`prepare`** puts the identity and a fresh dataloader (step 5) into each request. Tests use it too, so they build requests exactly as the app does.
5. **Introspection**, a client asking the server for its whole schema, is how GraphQL tools learn what fields exist. It's on while developing and off in production, where clients use the published schema file (step 8).
6. **No playground page.** async-graphql can serve GraphiQL, a GraphQL editor that runs in the browser. Its page loads unpinned scripts from a public CDN and runs inline scripts, which lesson 14's content security policy rightly forbids. Use a desktop GraphQL client against your laptop instead.

In `src/lib.rs`, next to the webhooks, outside `/v1` and `/v2`:

```rust
        // Outside the versions: GraphQL changes by adding fields and deprecating old ones (see the lesson).
        .merge(graph::router().layer(http::no_store()))
```

`no_store`, because `me` is personal. And `main` builds the schema:

```rust
    // Clients may download the GraphQL schema while we develop; in production, they use the published file.
    let introspection = std::env::var("APP_ENV").as_deref() != Ok("production");
    let graph = graph::schema(menu.clone(), orders.clone(), PgAuthStore::new(pool.clone()), introspection);
```

Try it:

```bash
curl -s localhost:8080/graphql -H 'Content-Type: application/json' \
  -d '{"query":"{ menu(first: 2) { edges { cursor node { id name price { amount } } } pageInfo { hasNextPage endCursor } } }"}'
```

```json
{"data":{"menu":{"edges":[{"cursor":"0","node":{"id":"1","name":"Jollof rice","price":{"amount":150000}}},{"cursor":"1","node":{"id":"2","name":"Beans and plantain","price":{"amount":120000}}}],"pageInfo":{"hasNextPage":true,"endCursor":"1"}}}}
```

One request, exactly the fields asked for, and `"id":"1"` is a string, as `ID` promises. The next page is `menu(first: 2, after: "1")`.

## Step 5: the N+1 problem, and a dataloader
<!-- bite: 575e5dde-a8a7-49a1-8201-83eb3281556a -->

Look at this harmless-looking query:

```graphql
{ me { orders(first: 20) { edges { node { id dish { name } } } } } }
```

Without care: one query for the 20 orders, then `Order.dish` runs 20 times, and that's 20 queries for dishes, many of them the same dish (half of Mama's orders are jollof). 21 queries for one small screen. That's the **N+1 problem**, and every GraphQL API meets it.

A dataloader fixes it. Each `load_one(id)` doesn't query at once: it waits a moment to see what else is asked for, then calls *your* load function **once** with every id collected. `src/graph/loaders.rs`:

```rust
use std::{collections::HashMap, sync::Arc};

use async_graphql::dataloader::Loader;

use crate::menu::{Dish, MenuError, MenuService};

/// Collects every "dish 1", "dish 4", "dish 1" asked for in the same moment, and fetches them in one query.
pub(super) struct DishLoader(pub MenuService);

impl Loader<i64> for DishLoader {
    type Value = Dish;
    type Error = Arc<MenuError>; // every caller in the batch gets the same error, so it must be shareable

    async fn load(&self, ids: &[i64]) -> Result<HashMap<i64, Dish>, Self::Error> {
        let dishes = self.0.many(ids).await.map_err(Arc::new)?;
        // A map, not a list: Postgres returns rows in any order, and each caller must get its own dish.
        Ok(dishes.into_iter().map(|dish| (dish.id, dish)).collect())
    }
}
```

and `MenuService::many`, which is one query: `SELECT ... FROM dishes WHERE id = ANY($1)`. `Order.dish`, from step 2, asks the loader instead of the service.

How does "waits a moment" work? async-graphql resolves the 20 `dish` fields of a list concurrently, as 20 futures. Each calls `load_one`, which puts its id in the loader's batch and waits. The loader starts its fetch on a task of its own (that's what `tokio::spawn` in `DataLoader::new` is for) after a tiny delay, 1 ms by default, long enough for all 20 to have joined. Then every caller gets its own dish out of the one answer.

Three rules the loader holds us to:

1. **Answer with a map.** Postgres returns rows in any order, so a plain list matched up by position is an easy bug: Ada's order shows Bayo's dish. A `HashMap` from id to dish can't get that wrong.
2. **One loader per request.** The loader also remembers what it loaded, so dish 1 asked for twice is fetched once. That memory is a cache, and a cache shared between requests would serve stale dishes, or, for anything personal, one customer's data to another. `prepare` makes a fresh one for every request.
3. **Errors are shared.** Every caller in a batch gets the same error, so the error type must be `Clone`. `MenuError` isn't, so it's wrapped in an `Arc`, which is.

The test counts the database calls: 20 orders, alternating two dishes, `dish { name }` on each, **one** query for dishes. Without the loader, it's twenty.

## Step 6: errors
<!-- bite: e0ddabe0-5b12-4471-95b7-686430bd9c53 -->

GraphQL reports errors differently from REST. The HTTP status is **200**, and the body has `data` (what worked) and `errors` (what didn't), side by side. Ask for an order that isn't there, and `me`, in one query:

```bash
curl -s localhost:8080/graphql -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"{ order(id: \"999\") { id } me { name orders(first: 2) { edges { node { id status dish { name } } } } } }"}'
```

```json
{
    "data": {
        "me": {
            "name": "Ada",
            "orders": {
                "edges": [
                    { "node": { "id": "6", "status": "PENDING", "dish": { "name": "Beans and plantain" } } },
                    { "node": { "id": "8", "status": "PENDING", "dish": { "name": "Beans and plantain" } } }
                ]
            }
        }
    },
    "errors": [
        {
            "message": "there's no order 999",
            "locations": [{ "line": 1, "column": 3 }],
            "path": ["order"],
            "extensions": { "code": "order-not-found" }
        }
    ]
}
```

`order` failed; `me` still worked, and the screen gets both. That's a feature, but it means clients must always read `errors`, not just the status.

Three details:

1. **The message and code are REST's.** `gql` turns any of our errors into an `ApiError` first, with lesson 7's `From` impls, then into a GraphQL error with its `detail` as the message and its `code` in `extensions`. So `order-not-found` means the same in both doors, and an internal error is logged by `ApiError::internal` and says only "Something went wrong on our side." Nothing about our database ever reaches a client.
2. **`order` is nullable on purpose.** If a non-null field fails, GraphQL can't put `null` there, so it nulls its *parent* instead. For a top-level field, that's the whole `data`, and `me` would be lost with it. Return `Option` for fields that can fail on their own.
3. **async-graphql leaves the failed field out.** The GraphQL specification says a failed nullable field should be `null`; above, `order` simply isn't in `data`. I expected `"order": null`, and the test told me otherwise. Clients in JavaScript won't notice (`undefined` and `null` are both "nothing"), but a strict client should treat a missing field as `null`, and look at `errors` for why.

And one more kind of error, before anything runs: a query the schema doesn't allow. `quantity: 50` fails the input's validator, and the whole mutation is refused with `the value is 50, must be less than or equal to 20`. A query naming a field that doesn't exist is refused the same way, before any resolver is called.

## Step 7: refusing expensive queries
<!-- bite: 64efc5dc-3a78-4540-bd33-d6e68a9d3f79 -->

Remember the greedy customer. GraphQL lets a client nest as deep as the schema allows, and ask for a hundred of everything at each level. Two limits, set when the schema is built:

1. **`limit_depth(10)`**: no query nested more than ten levels.
2. **`limit_complexity(300)`**: every field costs 1, and a list costs `first` times what each of its items asks for. That's what `#[graphql(complexity = "first as usize * child_complexity")]` on `menu` and `orders` says.

So `menu(first: 20) { edges { node { id name } } }` costs about 20 × 2, fine. `menu(first: 100)` with five fields per dish is over 500, and it's refused **before anything runs**:

```json
{"data":null,"errors":[{"message":"Query is too complex."}]}
```

Lesson 6's 16 KB body limit still applies too: no phone screen's query is anywhere near that.

These limits work on the query's *shape*, before it runs. They can't know how many orders a customer really has. For that, every list has a `maximum` on `first`, and lesson 19's rate limits can count GraphQL requests like any other.

## Step 8: the schema as a file, and changing it
<!-- bite: 121d2bbc-0324-4d76-94f0-8c7eb2142c31 -->

Code-first has one weakness: there's no schema file for the phone team to read, or to review when it changes. So we make one, and check it. `schema.sdl()` writes the schema as SDL; a test compares it with `schema.graphql` at the root of the project:

```rust
/// The schema is made from the Rust types, so the file clients read is checked against them.
#[sqlx::test]
async fn the_published_schema_is_the_real_one(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let schema = graph::schema(app.menu(), app.orders(), PgAuthStore::new(app.pool.clone()), true);
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/schema.graphql");
    if std::env::var("UPDATE_SCHEMA").is_ok() {
        std::fs::write(path, schema.sdl()).unwrap();
    }
    let published = std::fs::read_to_string(path).expect("run once with UPDATE_SCHEMA=1 to write schema.graphql");
    assert_eq!(published, schema.sdl(), "the schema changed: check it's only additions, then run with UPDATE_SCHEMA=1");
}
```

```bash
UPDATE_SCHEMA=1 cargo test --test graphql the_published_schema
```

writes the file the first time. Here is part of it:

```graphql
type Query {
	"""
	The menu, a page at a time. Anyone may read it.
	"""
	menu(first: Int! = 20, after: String, search: String): DishConnection!
	"""
	One dish, or `null` if there's no such dish.
	"""
	dish(id: ID!): Dish
	"""
	Whoever is logged in, or `null` for nobody.
	"""
	me: User
	"""
	One of your orders.
	"""
	order(id: ID!): Order
}
```

From then on, any change to the types that changes the schema fails the test, and the diff of `schema.graphql` shows exactly what changed for clients. Commit it, and a reviewer sees "`Order` gained `createdAt`" without reading any Rust. That's the best of both: types are the truth, and the file is the readable copy.

**Why `/graphql` isn't under `/v2`.** GraphQL APIs usually don't version by URL. Clients ask for exactly the fields they use, so **adding** a field or a type breaks nobody: old clients don't ask for it. To change a field, add the new one, mark the old one with `#[graphql(deprecation = "use price")]`, which tools show to clients, and remove it only once your logs show nobody asks for it. The `schema.graphql` diff makes a removal impossible to miss. Lesson 10's rule still holds, as a different practice: never change what an existing field means.

## Step 9: testing
<!-- bite: e2296d37-f824-45eb-80da-9b4f4c7ac948 -->

`tests/graphql.rs` has six tests. Most send real HTTP requests through the whole app with `TestApp`, using a small helper:

```rust
/// Sends a GraphQL query through the whole app, as a phone would.
async fn ask(app: &TestApp, token: Option<&str>, query: &str, variables: Value) -> Value {
    let mut call = app.post("/graphql").json(json!({"query": query, "variables": variables}));
    if let Some(token) = token {
        call = call.bearer(token);
    }
    let reply = call.send().await;
    assert_eq!(reply.status, StatusCode::OK, "GraphQL answers 200, with any errors in the body");
    reply.body
}
```

1. `one_request_for_the_whole_order_screen`: the phone team's query, and the whole answer compared at once: exactly the fields asked for, ids as strings.
2. `a_failed_field_is_null_and_the_rest_still_arrives`: step 6's answer, `unauthenticated` for nobody, and a forged token is a 401 before GraphQL runs at all.
3. `a_retried_mutation_is_the_same_order`: `placeOrder` twice with one key is one order; without a login it's `unauthenticated`; 50 plates is refused.
4. `a_query_that_could_be_too_much_work_is_refused`: `first: 100` refused, `first: 20` fine.
5. `twenty_orders_cost_one_query_for_their_dishes`, below HTTP.
6. `the_published_schema_is_the_real_one`, from step 8.

The dataloader test needs to count database calls, so it builds its own `MenuService` around a store that counts, and runs the schema directly:

```rust
#[sqlx::test]
async fn twenty_orders_cost_one_query_for_their_dishes(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let ada = app.user("ada@example.com", "customer").await;
    let (jollof, beans) = (app.dish("Jollof rice", 1500, 40).await, app.dish("Beans", 1200, 40).await);
    for i in 0..20 {
        app.order(&ada, if i % 2 == 0 { jollof } else { beans }).await;
    }

    let queries = Arc::new(AtomicUsize::new(0));
    let menu = MenuService::new(Arc::new(Counting { inner: PgMenuStore::new(app.pool.clone()), queries: queries.clone() }), Cache::in_memory());
    let schema = graph::schema(menu.clone(), app.orders(), PgAuthStore::new(app.pool.clone()), true);
    let request = Request::new("{ me { orders(first: 20) { edges { node { dish { name } } } } } }");
    let who = Identity { user_id: 1, role: Role::Customer };
    let answer = schema.execute(graph::prepare(request, Some(who), menu)).await;

    assert!(answer.errors.is_empty(), "{:?}", answer.errors);
    assert_eq!(answer.data.into_json().unwrap()["me"]["orders"]["edges"].as_array().unwrap().len(), 20);
    assert_eq!(queries.load(Ordering::SeqCst), 1, "one query for every dish, not twenty");
}
```

`Counting` implements lesson 5's `MenuStore` trait by passing every call to the real `PgMenuStore`, adding one to a counter on `find` and `find_many`. That's lesson 5's design paying off again: any store will do, including one that spies. `TestApp` gains `menu()` and `orders()`, for tests below HTTP.

```bash
cargo test
```

75 tests, all passing.

## The Rust in this lesson
<!-- bite: 0163a902-0288-4a4a-bcd8-6a808277787e -->

1. **`#[derive(SimpleObject)]`**, **`#[Object]`**, **`#[derive(InputObject)]`**, **`#[derive(Enum)]`**: async-graphql's macros, which turn Rust types into GraphQL types and an `impl` into resolvers.
2. **Procedural macros reading doc comments**: `///` comments are attributes the macro can read, and async-graphql copies them into the schema.
3. **`#[graphql(remote = "...")]`**: An enum that mirrors another crate's or module's enum, with conversions both ways made for you.
4. **Newtype wrappers**, `pub struct DishNode(pub Dish)`: A new type around an existing one, to give it different behaviour (here, GraphQL) without touching the original.
5. **`ctx.data_unchecked::<T>()`** and **`data_opt::<T>()`**: Values looked up by their type, the way Axum's `Extension` works.
6. **`OptionalFromRequestParts`**: Axum 0.8's way of making an extractor usable as `Option<T>`, deciding for itself what counts as "absent" and what's an error.
7. **`Arc<E>` to share an error**: Wrapping a value in `Arc` makes it cheap to clone, even when the value itself can't be cloned.
8. **`impl Trait for Type` with an `async fn`**: Traits can have async methods in Rust now (`Loader::load`), without `#[async_trait]`, when the trait is written for it.
9. **`concat!(env!("CARGO_MANIFEST_DIR"), "/schema.graphql")`**: The project's folder, known when compiling, joined to a file name: a path that works wherever the tests run from.
10. **`.transpose()`**: Turns an `Option<Result<T, E>>` into a `Result<Option<T>, E>`, so `?` can be used on an optional value that might fail to parse.

## Your project so far
<!-- bite: bb89cd69-9faf-4d9e-ace4-f9c50d5fd859 -->

```text
mama-put/
├── Cargo.toml                    ← async-graphql (dataloader only), async-graphql-axum
├── schema.graphql                ← NEW: the published schema, checked against the code by a test
├── src/
│   ├── main.rs                   ← builds the schema; introspection off when APP_ENV=production
│   ├── lib.rs                    ← POST /graphql, outside the versions, with no_store
│   ├── graph/                    ← NEW
│   │   ├── mod.rs                ← schema (depth and complexity limits), router, handler, prepare
│   │   ├── types.rs              ← Money, Dish, OrderStatus, Order (dish through the loader), User, input, payload
│   │   ├── query.rs              ← Query (menu, dish, me, order) and Mutation (placeOrder)
│   │   ├── loaders.rs            ← DishLoader: many dishes, one query
│   │   └── errors.rs             ← gql (REST's words and codes), who, number
│   ├── auth/extract.rs           ← Option<AuthUser>: no token is nobody; a bad token is a 401
│   └── menu/
│       ├── store.rs              ← find_many: WHERE id = ANY($1)
│       └── service.rs            ← many
└── tests/
    ├── common/mod.rs             ← TestApp builds the schema; menu() and orders()
    └── graphql.rs                ← NEW: 6 tests
```

## Common mistakes
<!-- bite: 838e08e0-9cb0-4c9c-a424-7876a430d286 -->

1. **Rules in resolvers.** Two doors, two copies of a rule, and one day they disagree. Resolvers call services.
2. **No dataloader.** Every list of N things costs N+1 queries. Batch with a loader.
3. **A loader shared between requests.** Its memory is a cache: stale data, or one customer's data to another. One per request.
4. **Matching batch results by position.** Rows come back in any order. Answer with a map.
5. **No depth or complexity limit.** One query can ask for millions of rows. Limit both, and cost lists by `first`.
6. **Non-null fields that can fail.** One failure nulls the parent, and can take the whole answer with it. Make them nullable.
7. **Raw error messages to clients.** They can show internal details. Go through `ApiError`.
8. **A bad token treated as nobody.** The client can't tell why it's suddenly logged out. A bad token is a 401.
9. **Introspection and a playground in production.** Both are for developers. Publish the schema file instead.
10. **Notes for yourself in doc comments.** They're the public descriptions. Use `//` for notes.

## Check your understanding
<!-- bite: 73a584d2-d3b8-44c7-acab-27c9b7cb8236 -->

1. What does GraphQL do better than REST, and what does it make harder?
2. Why does Mama Put keep REST and add GraphQL, instead of replacing one with the other?
3. Where do the rules for placing an order live, and why does that matter with two doors?
4. Walk through what the dataloader does for `me { orders(first: 20) { edges { node { dish { name } } } } }`.
5. Why must a dataloader's results be a map, and why must each request have its own?
6. Why is `order` nullable, and what does async-graphql do when it fails?
7. How does `limit_complexity` know `menu(first: 100)` is too much, before running it?
8. There's no schema file in code-first GraphQL. How does Mama Put still publish one, and keep it honest?

<details>
<summary>Answers, after your attempt</summary>

1. A client can get many related things, shaped its own way, in one request, with exactly the fields it needs. It makes HTTP caching mostly useless, errors come back as 200 so monitoring must read bodies, and clients can ask for expensive combinations, so limits are needed.
2. Each is better at different things: REST for the cached public menu, webhooks, uploads and simple integrations; GraphQL for app screens that need many related things. Both call the same services, so having two costs little.
3. In the services: `OrderService::place` checks the shop hours, the dish, the quantity, and takes plates with the guarded `UPDATE`. Both REST and GraphQL call it, so a rule can't be in one door and missing from the other.
4. One query fetches the 20 orders. Then 20 `dish` resolvers each call `load_one` with a dish id, at nearly the same moment. The loader collects the ids, waits a millisecond, and makes one `WHERE id = ANY($1)` query for all of them, then gives each resolver its own dish from the answer.
5. A map because Postgres returns rows in any order, and matching by position would give orders the wrong dishes. Its own because the loader remembers what it loaded, and that memory shared between requests would be a cache with stale and possibly someone else's data.
6. Because if a non-null field fails, its parent becomes `null`, and for a top-level field that's all of `data`, so `me` would be lost too. When it fails, async-graphql leaves the field out of `data` (the spec says `null`) and puts the error in `errors`.
7. From the query's shape: every field costs 1, and the `complexity` on `menu` multiplies what each dish asks for by `first`. 100 dishes with five fields each is over 500, more than 300, so it's refused before any resolver runs.
8. `schema.sdl()` writes the schema the code makes; a test compares it with `schema.graphql`, which is committed. Any change to the types that changes the schema fails the test until the file is updated, so the file always matches, and its diff shows clients exactly what changed.

</details>

## Practice
<!-- bite: bc3c3fd4-c942-4233-bcaa-471b79647cd5 -->

1. Add `createdAt` to `Order` (you'll need it in the domain `Order` and the store's queries first), update `schema.graphql`, and look at the diff.
2. Add `orders` to `Dish`, for staff only: the orders for that dish today. Use `who` and lesson 13's policy, and give it a `complexity`.
3. Rename `Dish.price` to `Dish.cost` the safe way: add `cost`, deprecate `price`, and check both in a test.
4. Add a `dish` field to the test's `Counting` store count, and show that `{ a: dish(id: "1") { name } b: dish(id: "1") { name } }` asks the store at most twice.
5. Write a test that a query 11 levels deep is refused.

**Done when** `curl` on `POST /graphql` answers the phone team's order screen in one request; twenty orders' dishes cost one query; a failed field leaves the rest of the answer; `menu(first: 100)` with five fields is refused; `schema.graphql` is committed and checked; and `cargo test` runs 75 tests and passes.

## Before moving on
<!-- bite: 8a0bd839-5c05-4ed7-b4f5-3803b6f03aa4 -->

Mama Put now has two doors for its clients: REST, for everything HTTP caches and integrations like, and GraphQL, for app screens that want exactly their fields in one trip. Both lead to the same services, with the same rules and the same error codes.

Both are for clients on the other side of the internet. Next, a different kind of client: another of our own programs, which wants to ask about dishes many times a second, with types agreed in advance and checked by the compiler on both sides. That's gRPC.

## Related
<!-- bite: 09f7d063-d561-4a30-9043-b88f160e99a5 -->

- [[backend/frameworks/axum/22-grpc|Next: gRPC]]
- [[backend/frameworks/net-http/21-graphql|The same lesson in net/http]] — schema-first with gqlgen, and the binding traps that brings
- [[backend/frameworks/axum/05-state-and-dependency-injection|State and Dependency Injection]] — why a counting store slots straight in
- [[backend/frameworks/axum/09-listing|Listing]] — the cursors GraphQL's connections build on

## About this lesson
<!-- bite: 78e7dec1-8634-487c-89de-31feb6a1fa3b -->

**Level:** Advanced. Lesson 21 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8 and async-graphql 7.2. Covers when GraphQL helps and what it costs, code-first types with `SimpleObject`, `Object`, `Enum` with `remote` and `InputObject`, doc comments as public descriptions, connections, an input and payload for mutations with the idempotency key inside, resolvers that call the same services as REST, serving on `POST` only with an optional `AuthUser`, no playground and introspection off in production, a per-request dataloader against N+1, errors that reuse REST's codes and what async-graphql does with a failed field, depth and complexity limits, a published `schema.graphql` checked by a test and evolving without versions, and testing through the app and below it with a counting store.
