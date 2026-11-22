---
id: 53cfe39d-7090-4541-9091-d72408c63dd0
---

# API Docs

**API docs are the description of an API that other developers build against: every route, what it takes, what it sends back, and how it fails.** The standard way to write them is **OpenAPI**, a JSON or YAML file that tools turn into web pages, client code and tests. In Rust, the usual tool is **utoipa**, which builds the OpenAPI file from your own Rust types, so the docs describe what the code really sends.

## Before you start
<!-- bite: 819344a8-e074-4361-a1f3-3dca297a8fd1 -->

You should have:

1. Finished [[backend/frameworks/axum/10-versioning|lesson 10]], so v1 and v2 are served side by side from generic handlers, and `cargo test` passes.
2. Seen a JSON Schema, or be ready to read one. An OpenAPI file uses JSON Schema to describe each body.

After this lesson you will be able to:

1. Say what OpenAPI is, and choose between writing the spec first and generating it from code.
2. Derive schemas from the real wire types with `#[derive(ToSchema)]`.
3. Describe routes with `#[utoipa::path]`, including query parameters, error responses and security.
4. Serve the spec as JSON and as an interactive docs page.
5. Write a test that fails when the docs describe a route the app doesn't have.

## What to install
<!-- bite: a086250c-e516-4b73-a025-7745c2cf8f9f -->

```bash
cargo add utoipa
cargo add utoipa-scalar --features axum
```

1. **`utoipa`** builds an OpenAPI description from Rust: a derive for schemas, an attribute for routes, and a derive that gathers them into one document.
2. **`utoipa-scalar`** serves **Scalar**, a docs page that reads the spec and lets you try each route from the browser.

## Where we stopped
<!-- bite: ba963154-3ab3-4ed4-9ae6-27aacd557dda -->

The phone team asked "what exactly does v2 send and accept?", and the honest answer is "read the Rust". They can't. They need to know that a price is `{"amount", "currency"}` in kobo, that `sort` takes `-price`, that a bad body gets a problem with an `errors` list, and that `POST /v2/menu` needs a staff key. Today, that knowledge is spread across `versions.rs`, `handlers.rs`, `extract.rs` and `deprecation.rs`.

## The kid version
<!-- bite: 6ea942eb-d0e1-4f09-8ffd-5add8e314bcd -->

Mama's regulars know the menu by heart. A new customer doesn't. So Mama paints a board: every dish, what's in it, the price, and "ask at the counter if you want extra pepper". A painted board is only useful if it's right, though. If Mama changes the price of jollof and forgets the board, customers are angrier than if there were no board at all.

The OpenAPI file is the board. utoipa paints it from the pots themselves, so a new price is on the board the moment it's in the pot.

**Where the picture stops working.** Part of our board can't be painted from the pots: the list of routes. So we paint that part by hand, and send someone round every morning to check each route on the board is a real counter (a test). If it isn't, the test fails before any customer sees the board.

## Terms used in this lesson
<!-- bite: 73cb5a9c-2615-429e-ab1c-1703a48936a3 -->

1. **OpenAPI**: This is a standard format for describing an HTTP API: its paths, parameters, bodies, responses and security. Version 3.1 uses JSON Schema for bodies.
2. **Spec**: This is short for specification, the OpenAPI file itself.
3. **Schema**: This is the description of one shape of JSON: its fields, their types, which are required, and their limits.
4. **Spec-first**: This means writing the spec by hand, then generating or checking code against it.
5. **Code-first**: This means writing the code, then generating the spec from it.
6. **Security scheme**: This is the part of a spec that says how a client proves who it is, like "send `X-Staff-Key` in a header".
7. **Contract test**: This is a test that checks the code and the spec agree.

## Code-first or spec-first?
<!-- bite: 52a995ab-2559-4ea4-98fc-a759ec4891e6 -->

The Go version of this lesson writes the spec first, in YAML, and generates Go types from it. Both ways are respectable:

1. **Spec-first** is best when the spec is agreed before the code exists, between teams, or for a public API. The YAML is the contract; the code follows.
2. **Code-first** is best when one team owns both, and the code is where the truth lives. The spec is generated, so it can't describe a field the code doesn't send.

Rust leans code-first, because its type system already says so much: serde's `rename_all`, `Option` for optional fields, enums for fixed sets of values. utoipa reads all of that. And our v2 wire types from lesson 10 are already exactly the shapes clients see, kept apart from the domain types for this very reason.

## Step 1: schemas from the real types
<!-- bite: 0be275ba-3c8e-4eb3-b0ea-1b89e472acdd -->

Add `ToSchema` to every v2 wire type. In `src/menu/versions.rs`:

```rust
#[derive(Serialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct DishV2 {
    id: i64,
    name: String,
    price: Amount,
    available: bool,
    special: bool,
    portions_left: i32,
}
```

and the same on `NewDishV2` and `DishChangesV2`, with `use utoipa::ToSchema;` at the top. **`#[derive(ToSchema)]`** writes a JSON Schema for the struct at compile time, and it reads serde's attributes as it does: `rename_all = "camelCase"` makes the schema say `portionsLeft`, and `Option<String>` makes a field not required. Here's the schema it produced for `DishV2`:

```json
{"type": "object",
 "required": ["id", "name", "price", "available", "special", "portionsLeft"],
 "properties": {"id": {"type": "integer", "format": "int64"}, "name": {"type": "string"},
                "price": {"$ref": "#/components/schemas/Amount"}, "portionsLeft": {"type": "integer", "format": "int32"}, ...}}
```

`price` points at `Amount`'s own schema, because `Amount` derives `ToSchema` too. In `src/money.rs`:

```rust
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize, Validate, ToSchema)]
#[serde(deny_unknown_fields)]
pub struct Amount {
    /// In kobo: ₦1 is 100.
    #[schema(minimum = 1, maximum = 100_000_000, example = 150000)]
    #[validate(range(min = 1, max = 100_000_000, message = "must be from 1 kobo to ₦1,000,000"))]
    pub amount: i64,
    pub currency: Currency,
}
```

1. **A `///` doc comment becomes the field's description** in the spec. Write it for the phone team.
2. **`#[schema(minimum = ..., maximum = ..., example = ...)]`** adds limits and an example. utoipa doesn't read validator's rules, so the limits are written twice, once for checking and once for telling. They sit on neighbouring lines, so a change to one stares at the other. (Practice 2 makes a test that catches them disagreeing.)
3. **`Currency`, an enum, becomes `{"type": "string", "enum": ["NGN"]}`**, from serde's `rename`.

`ToSchema` also goes on `OrderV2`, `NewOrder`, `Status` and `StatusChange` in the orders module, on `FieldError`, and on the response shapes in `src/http/error.rs`:

```rust
#[derive(Serialize, ToSchema)]
pub struct Envelope<T> {
    data: T,
}
```

```rust
#[derive(Serialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct Problem<'a> {
```

`Envelope` and `Problem` become `pub`, and are exported from `http/mod.rs`, so the docs can name them. `Envelope<T>` is generic, and utoipa handles that: the docs can say `Envelope<DishV2>`, and the schema becomes `{"data": DishV2}`. That's the real envelope type `Data` uses, not a copy, so the docs' envelope can't drift from the real one.

The two list `meta` types from lesson 9 move out of the handler files into `error.rs`, beside `Page`, with `ToSchema`, so the docs can name them too:

```rust
/// Where an offset page sits: `limit`, `offset`, and how many match in all.
#[derive(Serialize, ToSchema)]
pub struct OffsetMeta {
    pub limit: i64,
    pub offset: i64,
    pub total: i64,
}

/// Where a cursor page sits. No `nextCursor` means this is the last page.
#[derive(Serialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct CursorMeta {
    pub limit: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub next_cursor: Option<String>,
}
```

## Step 2: the routes
<!-- bite: 978fd051-c6fc-4961-83f0-0afd07173dcf -->

Routes are described with **`#[utoipa::path(...)]`**, an attribute on a function. Normally it goes on the handler itself. Ours can't take it: our handlers are generic (`get_one::<V>`), and `#[utoipa::path]` describes one concrete function. So the routes are described in a module of their own, `src/docs.rs`, with one empty function per route, there only to carry the description. `pub mod docs;` in `lib.rs`.

```rust
//! The OpenAPI description of v2, served at `/v2/openapi.json` and drawn at `/v2/docs`.
//!
//! The schemas are derived from the real wire types, so they can't drift from what the handlers send.
//! The paths are described here, one empty function each, because the real handlers are generic over the
//! API version and `#[utoipa::path]` describes one concrete function. A test checks every path below is a
//! real route, so these can't drift either.
```

Getting one dish:

```rust
/// Get one dish
#[utoipa::path(
    get, path = "/v2/menu/{id}", tag = "menu",
    params(("id" = i64, Path, description = "the dish's id")),
    responses(
        (status = 200, description = "The dish", body = Envelope<DishV2>),
        (status = 404, description = "No such dish", body = Problem, content_type = "application/problem+json"),
    )
)]
pub fn get_dish() {}
```

1. **The doc comment's first line** becomes the route's summary; the rest, its description.
2. **`params`** lists each parameter: its name, Rust type, where it is (`Path` or `Query`) and a description.
3. **`responses`** lists every answer worth knowing about, including failures. The error responses say `content_type = "application/problem+json"`, lesson 7's type, so a client knows to read them as problems.
4. **`body = Envelope<DishV2>`** names the real types. Rename a field in `DishV2` and the docs change with it.

The list shows query parameters, and the refusals lesson 9 built:

```rust
/// List dishes
///
/// Filter, search, sort and page through the menu. Unknown parameters are refused.
#[utoipa::path(
    get, path = "/v2/menu", tag = "menu",
    params(
        ("limit" = Option<i64>, Query, description = "1 to 100; 20 if left out"),
        ("offset" = Option<i64>, Query, description = "skip this many first"),
        ("available" = Option<bool>, Query, description = "only dishes still available, or only finished ones"),
        ("special" = Option<bool>, Query, description = "only today's specials, or only the rest"),
        ("minPrice" = Option<i64>, Query, description = "in kobo"),
        ("maxPrice" = Option<i64>, Query, description = "in kobo"),
        ("q" = Option<String>, Query, description = "names containing this, any case"),
        ("sort" = Option<String>, Query, description = "comma-separated field names, `-` for biggest first: `-price,name`"),
        ("fields" = Option<String>, Query, description = "only these fields (and `id`): `name,price`"),
    ),
    responses(
        (status = 200, description = "A page of dishes", body = Page<DishV2, OffsetMeta>),
        (status = 400, description = "A parameter is unknown or out of range", body = Problem, content_type = "application/problem+json"),
    )
)]
pub fn list_dishes() {}
```

and the kitchen's routes say they need the staff key, with `security`:

```rust
/// Add a dish
#[utoipa::path(
    post, path = "/v2/menu", tag = "menu",
    request_body = NewDishV2,
    security(("staff_key" = [])),
    responses(
        (status = 201, description = "Added; `Location` says where it lives", body = Envelope<DishV2>),
        (status = 400, description = "The body isn't right; `errors` says which fields", body = Problem, content_type = "application/problem+json"),
        (status = 401, description = "No staff key, or the wrong one", body = Problem, content_type = "application/problem+json"),
    )
)]
pub fn add_dish() {}
```

The other six routes follow the same pattern: `change_dish`, `remove_dish`, `place_order`, `get_order`, `list_orders` and `set_order_status`. Each lists its real failures: `remove_dish` has the 409 for a dish with orders, `place_order` the 409 for a closed shop and the 422 for no plates left.

### Gathering it into one document

At the top of `docs.rs`:

```rust
#[derive(OpenApi)]
#[openapi(
    info(title = "Mama Put API", version = "2", description = "Order from Mama Put. Prices are in kobo: ₦1 is 100."),
    paths(list_dishes, get_dish, add_dish, change_dish, remove_dish, place_order, get_order, list_orders, set_order_status),
    components(schemas(DishV2, NewDishV2, DishChangesV2, Amount, Currency, OrderV2, NewOrder, Status, StatusChange, Problem, FieldError)),
    modifiers(&StaffKeyScheme),
    tags((name = "menu", description = "Mama's dishes"), (name = "orders", description = "Placing and cooking orders"))
)]
pub struct ApiDoc;

/// Says what the `staff_key` security in the paths below means: an `X-Staff-Key` header.
struct StaffKeyScheme;

impl Modify for StaffKeyScheme {
    fn modify(&self, openapi: &mut utoipa::openapi::OpenApi) {
        let components = openapi.components.get_or_insert_with(Default::default);
        components.add_security_scheme("staff_key", SecurityScheme::ApiKey(ApiKey::Header(ApiKeyValue::new("X-Staff-Key"))));
    }
}
```

1. **`#[derive(OpenApi)]`** on an empty struct builds the whole document. `ApiDoc::openapi()` returns it, ready to turn into JSON.
2. **`paths(...)`** lists the route functions; **`components(schemas(...))`** the types to describe.
3. **`modifiers(&StaffKeyScheme)`** runs our code on the document after it's built. The paths said `security(("staff_key" = []))`; this says what `staff_key` *is*. `get_or_insert_with(Default::default)` gets the document's components, making an empty set if there are none yet.

Only v2 is documented. v1 is deprecated, and the best docs for a deprecated version are a link to the next one. That's what its `Link` header already says.

## Step 3: serve the spec, and the docs page
<!-- bite: 828db471-8a29-424d-9724-ea3a9a9bd165 -->

In `app`, after the v2 router:

```rust
        .route("/v2/openapi.json", get(|| async { axum::Json(docs::ApiDoc::openapi()) }))
        .merge(Scalar::with_url("/v2/docs", docs::ApiDoc::openapi()))
```

with `use utoipa::OpenApi;` (the trait that gives `openapi()`) and `use utoipa_scalar::{Scalar, Servable};` at the top.

1. **`/v2/openapi.json`** sends the spec. Tools read this: the phone team's code generator, Postman, an AI assistant asked to write a client.
2. **`/v2/docs`** is a web page for people. **`Scalar::with_url`** returns a small router serving it; `merge` adds it to ours. The page itself is a little HTML that loads Scalar's script from a CDN and points it at the spec. (Lesson 14's security headers will need to allow that script.)

Open `http://localhost:8080/v2/docs` in a browser. Every route is there, grouped into "menu" and "orders", with the shapes, the limits, the examples, and a button to send a request. The phone team can try `POST /v2/menu` with a staff key from the page itself.

```bash
curl -s localhost:8080/v2/openapi.json | head -c 200
# {"openapi":"3.1.0","info":{"title":"Mama Put API","description":"Order from Mama Put. Prices are in kobo: ₦1 is 100.",...
```

## Step 4: what the phone team gets for free
<!-- bite: 746117bc-4417-4d2b-980c-80617198492e -->

With a spec, the phone team doesn't hand-write any of the networking code. A generator such as **openapi-generator** reads `/v2/openapi.json` and writes a typed client in Kotlin, Swift or TypeScript: a `Dish` class with an `Amount`, a `getDish(id)` method, the error type. When v2 gains a field, they regenerate. Testers point Postman or Bruno at the spec and get every request ready-made. And because the spec says which errors each route returns, the client knows that a 409 from `place_order` means "show 'the shop is closed'", not "something broke".

## Step 5: keep the spec honest
<!-- bite: 02aa49b7-225c-4ff6-8ed2-1a3eae25d4b9 -->

The schemas can't drift: they're derived from the types the handlers use. The paths can: they're written by hand in `docs.rs`. Rename a route in `handlers.rs`, forget `docs.rs`, and the docs send the phone team to an address that doesn't exist.

So a test checks every documented path is a real route. At the bottom of `docs.rs`:

```rust
    /// Every path and method in the docs must be a real route. It may refuse (no key, no such dish),
    /// but it must never be "no such route" or "wrong method".
    #[sqlx::test]
    async fn every_documented_route_is_real(pool: PgPool) {
        let app = app(pool);
        let spec = ApiDoc::openapi();
        let mut checked = 0;
        for (path, item) in &spec.paths.paths {
            let methods = [("GET", &item.get), ("POST", &item.post), ("PATCH", &item.patch), ("DELETE", &item.delete)];
            for (method, operation) in methods {
                if operation.is_none() {
                    continue;
                }
                let request = Request::builder().method(method).uri(path.replace("{id}", "1")).body(Body::empty()).unwrap();
                let response = app.clone().oneshot(request).await.unwrap();
                let body = to_bytes(response.into_body(), usize::MAX).await.unwrap();
                let code = serde_json::from_slice::<serde_json::Value>(&body).ok().and_then(|v| v["code"].as_str().map(String::from));
                assert!(
                    !matches!(code.as_deref(), Some("route-not-found" | "method-not-allowed")),
                    "{method} {path} is in the docs but isn't a route"
                );
                checked += 1;
            }
        }
        assert_eq!(checked, 9, "every documented operation was checked");
    }
```

(`app(pool)` at the top of the test module builds the real app with real Postgres stores, like `main` does.)

1. **It reads the spec it's testing.** For each path, it looks at which methods the spec documents.
2. **It sends each one to the whole app** with lesson 10's `oneshot`: the real router, every layer, a fresh database. `{id}` becomes `1`.
3. **Any answer is fine except two.** A 401 (no staff key), a 404 for dish 1 (an empty database), a 400 (no body): all prove the route exists. Only lesson 7's `route-not-found` and `method-not-allowed` codes mean the docs are wrong.
4. **`Some("route-not-found" | "method-not-allowed")`** is an **or-pattern**: either string matches.
5. **`assert_eq!(checked, 9)`** checks the test really checked something. A test that loops over nothing passes, and proves nothing.

I misspelt one path in the docs on purpose, `/v2/dishes/{id}`, and ran it:

```text
thread 'docs::tests::every_documented_route_is_real' panicked at src/docs.rs:224:17:
GET /v2/dishes/{id} is in the docs but isn't a route
```

It doesn't check the other way (a route that's missing from the docs), because Axum's `Router` can't list its routes. The `checked == 9` line is a nudge: add a route, and you'll update the number, and remember why.

## The Rust in this lesson
<!-- bite: ff30a6a2-f018-4ff5-ade5-75e239d800fc -->

1. **`#[derive(ToSchema)]`**: a JSON Schema for a type, built at compile time from its fields and serde attributes.
2. **`#[schema(...)]` on fields, and `///` doc comments** as descriptions.
3. **`#[utoipa::path(...)]`**: an attribute describing a route, placed on a function.
4. **`#[derive(OpenApi)]` with `#[openapi(...)]`**: gather paths and schemas into one document; `ApiDoc::openapi()` builds it.
5. **The `Modify` trait**: run your own code on the generated document.
6. **`Option::get_or_insert_with`**: get what's inside, putting a value in first if there's none.
7. **Generic schemas, `Envelope<DishV2>` and `Page<DishV2, OffsetMeta>`**.
8. **Bringing a trait into scope for its method, `use utoipa::OpenApi;`**, so `ApiDoc::openapi()` exists.
9. **Or-patterns, `Some("a" | "b")`**.
10. **`axum::body::to_bytes`**: read a whole response body in a test.

## Your project so far
<!-- bite: 561725ae-2926-4667-9459-c811c5501d35 -->

```text
mama-put/
├── Cargo.toml             ← + utoipa, utoipa-scalar (axum)
└── src/
    ├── lib.rs             ← + pub mod docs; /v2/openapi.json and /v2/docs
    ├── docs.rs            ← ApiDoc, StaffKeyScheme, nine #[utoipa::path] descriptions, 1 test
    ├── money.rs           ← ToSchema on Amount and Currency
    ├── http/
    │   ├── error.rs       ← ToSchema on Problem, Envelope, Page, FieldError; OffsetMeta and CursorMeta moved here
    │   └── mod.rs         ← + exports Envelope, Problem, OffsetMeta, CursorMeta
    ├── menu/
    │   ├── versions.rs    ← ToSchema on DishV2, NewDishV2, DishChangesV2
    │   └── mod.rs         ← + exports the v2 wire types
    └── orders/
        ├── model.rs       ← ToSchema on NewOrder, Status, StatusChange
        └── versions.rs    ← ToSchema on OrderV2
```

## Common mistakes
<!-- bite: e89e3408-b44e-4a51-8386-49f75b6dbf1f -->

1. **Docs written beside the code by hand, in a wiki.** They're wrong within a month. Generate what you can; test what you can't.
2. **A copy of a type just for the docs.** It drifts from the real one. Derive `ToSchema` on the type the handler sends.
3. **Documenting only the happy path.** The phone team needs the 400s, 404s, 409s and 422s most of all.
4. **Leaving out `content_type` on error responses.** Then the docs say errors are `application/json`, and a strict client won't parse them as problems.
5. **A test that loops over an empty list.** It passes forever. Count what was checked.
6. **Documenting a deprecated version as if it were current.** Point to the new one instead.
7. **Limits in the schema that disagree with validator's.** The docs promise one thing and the door enforces another.

## Check your understanding
<!-- bite: 574c5d07-720a-4ad3-850b-88c0c645e0ed -->

1. When is spec-first the better choice, and why does this lesson choose code-first?
2. What does `#[derive(ToSchema)]` on `DishV2` read to know the field is called `portionsLeft` and not `portions_left`?
3. Why are our routes described on empty functions in `docs.rs`, not on the handlers?
4. What does `modifiers(&StaffKeyScheme)` add that the paths' `security(...)` can't?
5. Why does the error response say `content_type = "application/problem+json"`?
6. The docs test accepts a 401 or a 404 as a pass. Why is that right?
7. What drift can the docs test not catch, and why?

<details>
<summary>Answers, after your attempt</summary>

1. Spec-first is better when the spec must be agreed before the code exists, between teams, or for a public API where the document is the contract. This lesson chooses code-first because one team owns both, the Rust types already say most of what a spec needs, and generating the schemas from the real wire types means they can't describe a field the code doesn't send.
2. serde's `#[serde(rename_all = "camelCase")]` attribute on the struct. utoipa reads serde's attributes when it derives the schema.
3. Because our handlers are generic over the API version, and `#[utoipa::path]` describes one concrete function. The empty functions carry the descriptions, and a test makes sure each one matches a real route.
4. The definition of `staff_key`: that it's an API key sent in the `X-Staff-Key` header. The paths only say they need `staff_key`; the security scheme says what that is.
5. Because that's what lesson 7's `write_problems` really sends for every error. A client generated from the spec needs to know error bodies are problem details, not ordinary JSON.
6. Because the test only asks "is this a real route?". A 401 (no staff key) or a 404 for a dish that doesn't exist in an empty test database proves the route was found and ran. Only `route-not-found` and `method-not-allowed` mean the route itself doesn't exist.
7. A route that exists in the app but is missing from the docs. Axum's `Router` can't list its routes, so the test can only start from the spec.

</details>

## Practice
<!-- bite: f3fce5ad-53a7-48a2-b74c-58266caa21cb -->

1. Describe `GET /v2/menu/specials` too, with `deprecated = true` in its `#[utoipa::path]`, and its description pointing to `GET /v2/menu?special=true&available=true`. Update the test's count.
2. Write a test that builds the spec and checks `Amount.amount`'s `minimum` and `maximum` match validator's range, by validating `Amount { amount: 0, .. }` and `Amount { amount: 100_000_001, .. }`.
3. Add `example`s to `NewDishV2`, so the docs page fills in a sensible body when you press "try it".
4. Generate a TypeScript client from `/v2/openapi.json` with `npx @openapitools/openapi-generator-cli generate -i http://localhost:8080/v2/openapi.json -g typescript-fetch -o client`, and read the `DishV2` it wrote.
5. Add the `Deprecation`, `Sunset` and `Link` headers to a hand-written note in the spec's `info.description`, explaining v1's retirement.

**Done when** `/v2/openapi.json` serves an OpenAPI 3.1 document whose schemas come from the real v2 wire types, every v2 route is described with its parameters, failures and security, `/v2/docs` shows it in a browser, and a test fails when a documented route doesn't exist.

## Before moving on
<!-- bite: 714b799b-f1a8-4c40-863b-43723a1f0f63 -->

Mama Put describes itself now. The phone team reads the docs page, generates a client from the spec, and knows every way each route can fail. The shapes are derived from the code, and the routes are checked by a test, so the description stays true.

But the security it describes is a shared password. Every kitchen worker has the same staff key, and customers have no identity at all: anyone can read anyone's order, and there's no "my orders". Next lesson: authentication, with accounts, passwords stored properly, short-lived tokens, and an `AuthUser` extractor that makes "this handler needs a logged-in user" something the compiler checks.

## Related
<!-- bite: d35d08d9-5e78-496b-ba0e-d2cd2e75ba4e -->

- [[backend/frameworks/axum/12-authentication|Next: Authentication]]
- [[backend/frameworks/net-http/11-api-docs|The same lesson in net/http]] — spec-first: YAML, generated types, and a contract test
- [[backend/02-api-design/index|API Design]] — what makes an API pleasant to build against
- [[backend/frameworks/axum/10-versioning|Versioning]] — the v2 wire types these schemas come from

## About this lesson
<!-- bite: 0f328851-967c-4a2c-98a2-bf9a937606a3 -->

**Level:** Intermediate. Lesson 11 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, utoipa 6 and utoipa-scalar 0.4. Covers what OpenAPI is, spec-first versus code-first and why Rust leans code-first, `#[derive(ToSchema)]` on the real v2 wire types reading serde's attributes, `#[schema]` limits and examples, generic schemas for the envelope and pages, `#[utoipa::path]` with path and query parameters, problem-details error responses and security, describing generic handlers on empty functions, `#[derive(OpenApi)]` and a `Modify` for the staff-key security scheme, serving the spec and a Scalar docs page, what a client generator gives the phone team, and a contract test that sends every documented operation to the real app and fails on a route that doesn't exist.
