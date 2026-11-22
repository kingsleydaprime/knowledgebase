---
id: b7930326-92d6-4913-86d8-f10220dc0f3a
---

# Pagination, Filtering, Searching, Sorting and Field Selection

**Listing means answering "show me some of these" well: a page at a time (pagination), only the ones that match (filtering and searching), in the order asked for (sorting), with only the fields wanted (field selection).** Every list in every API needs it, because a list that sends everything works with three dishes and falls over with three thousand orders. In Rust, the interesting part is building SQL whose *shape* changes with each request, safely, and that's sqlx's `QueryBuilder`.

## Before you start
<!-- bite: 732b0102-b787-41e4-8f92-47f7d145da95 -->

You should have:

1. Finished [[backend/frameworks/axum/08-data-with-postgres|lesson 8]], so the menu and orders are in PostgreSQL and `cargo test` passes.
2. Read [[backend/02-api-design/index|API design]] for the idea of resources and query parameters, if you want it first. Not required.

After this lesson you will be able to:

1. Design a list's query parameters in the API's own words, and refuse unknown ones.
2. Validate a whole query string at once, with a `ValidatedQuery` extractor and custom rules.
3. Build SQL whose filters and order change per request, with `QueryBuilder`, without ever pasting a client's text into it.
4. Search with `ILIKE` safely, and index it with trigrams.
5. Page with an offset where that's right, and with a cursor where it isn't, and say why.
6. Send only the fields a client asked for.

## What to install
<!-- bite: 91c4f4d5-d05a-4903-9e4a-ffb40d1db7c7 -->

```bash
cargo add base64
cargo add serde_json --features preserve_order
```

1. **`base64`** turns bytes into text that's safe in a URL, for the cursor (step 6).
2. **`serde_json`** you've had all along, through Axum. Now we use it directly, to trim fields from a dish (step 5). `preserve_order` keeps a JSON object's keys in the order they were added, so a trimmed dish's fields still come out in the same order as a whole one's.

## Where we stopped
<!-- bite: 36101e10-4753-44d8-8810-7ad519b45364 -->

`GET /menu` loads every dish from the database and sends them all. The only filter is `?available=`, done in Rust after loading everything. There's no way to ask for "dishes under ₦2,000, cheapest first", or "the ones with egusi in the name", or "just names and prices, for the phone's small screen".

And the kitchen has no list of orders at all. It can look one up by id, if it knows the id.

## The kid version
<!-- bite: 6b0faad1-11cc-47c5-ba78-e650fbd81433 -->

Mama's order notebook has hundreds of pages. When the kitchen asks "what's still waiting?", she doesn't read out the whole book. She flips to the waiting ones (filtering), starts from the oldest (sorting), reads twenty (a page), and puts her finger on the last one she read, so next time she carries on from there (a cursor).

**Where the picture stops working.** Mama's finger stays on the page while she's away. Our server keeps nothing between requests: the "finger" goes to the client, written on a slip (the cursor), and the client hands it back with the next request.

## Terms used in this lesson
<!-- bite: 02be2fbd-3c6d-4225-8cea-8296c03cd99e -->

1. **Pagination**: This is sending a list a page at a time, with a way to ask for the next page.
2. **Offset pagination**: This is "skip the first N, then give me 20". Simple, and it allows "page 9 of 12", but it can skip or repeat items when the list changes between pages.
3. **Cursor pagination**: This is also called **keyset pagination**. Each page comes with a **cursor**, a bookmark meaning "the last item you saw", and the next request asks for items after it.
4. **Allowlist**: This is a fixed list of accepted values. Anything not on it is refused. It's how a client's text can choose a column without ever becoming SQL.
5. **Dynamic SQL**: This is SQL whose shape (which conditions, which order) is put together while the program runs, per request.
6. **Trigram index**: This is a Postgres index on every three-letter piece of a text, so a search for "gus" inside a name can be fast.

## Step 1: decide the query parameters
<!-- bite: bfc576d2-b472-47ac-a526-b82189033b0f -->

Before any code, the design. The same parameters as the Go and Express versions of Mama Put:

| Parameter | Example | Means | On |
|---|---|---|---|
| `limit` | `limit=20` | at most this many items (1 to 100, default 20) | both |
| `offset` | `offset=40` | skip this many first | menu |
| `cursor` | `cursor=eyJhZnRlciI6Mn0` | after this bookmark | orders |
| `available` | `available=true` | only dishes still available | menu |
| `special` | `special=true` | only today's specials | menu |
| `minPrice`, `maxPrice` | `maxPrice=2000` | a price range, in naira | menu |
| `q` | `q=egusi` | dish names containing this, any case | menu |
| `sort` | `sort=priceNaira,-name` | comma-separated, `-` for biggest first | menu |
| `fields` | `fields=name,priceNaira` | only these fields | menu |
| `status` | `status=pending` | only orders in this status | orders |

Three decisions hide in that table:

1. **Names use the API's words**, the same `priceNaira` the JSON uses, never the database's `price_naira`. Clients shouldn't know or care what the columns are called.
2. **`limit` has a maximum.** Without one, `limit=1000000` is the "send everything" request we're getting rid of.
3. **Every parameter is checked, and an unknown one is a 400.** `?maxprice=2000` with a small p would otherwise be silently ignored, and the customer would see dishes they can't afford and think the filter is broken. It's lesson 6's `deny_unknown_fields`, for the query.

And `GET /menu/specials` from lesson 2 is now just `GET /menu?special=true&available=true`. Keep the old route for now (old clients use it); lesson 10 is about retiring routes properly.

## Step 2: the filter, in Mama's words
<!-- bite: a780aa0e-461b-449f-bc1f-02902983d85c -->

The service and store shouldn't see a query string. They get a plain struct saying what to list. In `src/menu/model.rs`:

```rust
/// Which dishes to list, in what order, and which page. Plain data: no HTTP, no SQL.
#[derive(Clone, Debug)]
pub struct DishFilter {
    pub available: Option<bool>,
    pub special: Option<bool>,
    pub min_price: Option<i64>,
    pub max_price: Option<i64>,
    pub name_contains: Option<String>,
    pub sort: Vec<DishSort>,
    pub limit: i64,
    pub offset: i64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DishSort {
    pub field: DishField,
    pub descending: bool,
}
```

And the allowlist: every field a client may sort by or ask for, as an enum, with its API name and its column:

```rust
/// Every field of a dish, by its API name and its column. The only names `sort` and `fields` accept.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DishField {
    Id,
    Name,
    PriceNaira,
    Available,
    Special,
    PortionsLeft,
}

impl DishField {
    pub const ALL: [DishField; 6] = [
        DishField::Id,
        DishField::Name,
        DishField::PriceNaira,
        DishField::Available,
        DishField::Special,
        DishField::PortionsLeft,
    ];

    /// The name clients use, in the JSON and in `sort` and `fields`.
    pub fn api_name(self) -> &'static str {
        match self {
            DishField::Id => "id",
            DishField::Name => "name",
            DishField::PriceNaira => "priceNaira",
            DishField::Available => "available",
            DishField::Special => "special",
            DishField::PortionsLeft => "portionsLeft",
        }
    }

    /// The column in the `dishes` table. Only ever one of these fixed names reaches the SQL.
    pub fn column(self) -> &'static str {
        match self {
            DishField::Id => "id",
            DishField::Name => "name",
            DishField::PriceNaira => "price_naira",
            DishField::Available => "available",
            DishField::Special => "special",
            DishField::PortionsLeft => "portions_left",
        }
    }

    pub fn from_api_name(name: &str) -> Option<DishField> {
        DishField::ALL.into_iter().find(|f| f.api_name() == name)
    }
}
```

This enum is the security of the whole lesson. A column name can't be a bind parameter (SQL doesn't allow `ORDER BY $1` to mean a column), so the column has to be written into the SQL itself. If a client's `sort=` text went straight into the SQL, that would be SQL injection. Instead, the client's text is only ever *looked up* in this list (`from_api_name`), and what reaches the SQL is `column()`: one of six fixed strings written in our code, `&'static str`. A name that isn't on the list is refused before any SQL exists.

Both `match`es have to name every variant, so adding a field to the enum and forgetting its column is a compile error.

## Step 3: the query string, checked all at once
<!-- bite: ae6f76d3-aa14-49ad-b1c8-8995ce01a88f -->

The handler's view of the query string, in `src/menu/handlers.rs`:

```rust
/// `GET /menu`'s query string, in the API's own words.
#[derive(Deserialize, Validate)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct ListParams {
    #[serde(default = "twenty")]
    #[validate(range(min = 1, max = 100, message = "must be from 1 to 100"))]
    limit: i64,
    #[serde(default)]
    #[validate(range(min = 0, message = "can't be negative"))]
    offset: i64,
    available: Option<bool>,
    special: Option<bool>,
    #[validate(range(min = 1, message = "must be at least ₦1"))]
    min_price: Option<i64>,
    #[validate(range(min = 1, message = "must be at least ₦1"))]
    max_price: Option<i64>,
    #[validate(length(min = 1, max = 80, message = "must be 1 to 80 characters"))]
    q: Option<String>,
    #[validate(custom(function = "known_sort"))]
    sort: Option<String>,
    #[validate(custom(function = "known_fields"))]
    fields: Option<String>,
}

fn twenty() -> i64 {
    20
}
```

The same tools as lesson 6, for a query string: serde reads the types, `deny_unknown_fields` refuses `maxprice`, validator checks the values. Two rules are our own:

```rust
/// `sort=priceNaira,-name`: each name must be a dish field, with `-` in front for "biggest first".
fn known_sort(raw: &str) -> Result<(), ValidationError> {
    let all_known = raw.split(',').all(|part| DishField::from_api_name(part.strip_prefix('-').unwrap_or(part)).is_some());
    if all_known { Ok(()) } else { Err(unknown_field_message()) }
}

/// `fields=name,priceNaira`: each name must be a dish field.
fn known_fields(raw: &str) -> Result<(), ValidationError> {
    if raw.split(',').all(|name| DishField::from_api_name(name).is_some()) {
        Ok(())
    } else {
        Err(unknown_field_message())
    }
}

fn unknown_field_message() -> ValidationError {
    let names: Vec<&str> = DishField::ALL.iter().map(|f| f.api_name()).collect();
    ValidationError::new("unknown_field").with_message(format!("each name must be one of: {}", names.join(", ")).into())
}
```

1. **`#[validate(custom(function = "known_sort"))]`** calls our function with the field's value. On an `Option`, only when it was sent.
2. **`strip_prefix('-')`** gives `Some("name")` for `"-name"` and `None` for `"name"`; `.unwrap_or(part)` takes the whole part when there was no `-`.
3. **`.all(...)`** is `true` only if every name passes.
4. **The message lists the names that do work.** A client developer who sent `sort=price` learns, in one answer, that it's `priceNaira`.

Because the custom rules are validator rules, they're reported **with** the others, in one answer. A query with three mistakes hears about three.

### `ValidatedQuery`, the query's `ValidatedJson`

In `src/http/extract.rs`, beside `ValidatedJson`:

```rust
/// Like `Query<T>`, but the values have also passed `T`'s validation rules.
pub struct ValidatedQuery<T>(pub T);

impl<S, T> FromRequestParts<S> for ValidatedQuery<T>
where
    S: Send + Sync,
    T: DeserializeOwned + Validate,
{
    type Rejection = ApiError;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let Query(value) = Query::<T>::from_request_parts(parts, state).await?;
        value.validate()?;
        Ok(ValidatedQuery(value))
    }
}
```

**`FromRequestParts`**, not `FromRequest`: the query is in the request's head, so this extractor never touches the body, and can sit anywhere in a handler's arguments. It gets the head as `&mut Parts`. **`Query::<T>`** is *our* `Query` from lesson 7, so a type error is already an `ApiError`. Add `ValidatedQuery` to the `pub use extract::{...}` line in `src/http/mod.rs`, and `http::request::Parts` to the file's imports.

## Step 4: dynamic SQL, safely, with `QueryBuilder`
<!-- bite: cd1fea11-297a-4853-867b-b7732079ff16 -->

`query_as!` needs its SQL written out in full, fixed, at compile time. That's what lets it check the SQL. But this list's SQL has a different shape on every request: with or without `AND special = ...`, ordered by price or by name. So for this one query, we build the SQL at run time, with sqlx's **`QueryBuilder`**.

The store trait's `list` takes the filter, and returns the page and the total, in `src/menu/store.rs`:

```rust
    /// One page of dishes, and how many match the filter in all.
    async fn list(&self, filter: &DishFilter) -> Result<(Vec<Dish>, i64), StoreError>;
```

```rust
    async fn list(&self, filter: &DishFilter) -> Result<(Vec<Dish>, i64), StoreError> {
        let mut count = QueryBuilder::new("SELECT count(*) FROM dishes");
        push_filters(&mut count, filter);
        let total: i64 = count.build_query_scalar().fetch_one(&self.pool).await?;

        let mut select =
            QueryBuilder::new("SELECT id, name, price_naira, available, special, portions_left FROM dishes");
        push_filters(&mut select, filter);
        select.push(" ORDER BY ");
        for sort in &filter.sort {
            select.push(sort.field.column());
            select.push(if sort.descending { " DESC, " } else { " ASC, " });
        }
        select.push("id"); // always last, so dishes that tie come back in the same order every time
        select.push(" LIMIT ").push_bind(filter.limit);
        select.push(" OFFSET ").push_bind(filter.offset);

        let dishes = select.build_query_as::<Dish>().fetch_all(&self.pool).await?;
        Ok((dishes, total))
    }
```

with the filters in one function both queries share:

```rust
/// Adds the `WHERE` for a filter. Values go in as bind parameters; only fixed text is pushed as SQL.
fn push_filters(query: &mut QueryBuilder<Postgres>, filter: &DishFilter) {
    query.push(" WHERE true");
    if let Some(available) = filter.available {
        query.push(" AND available = ").push_bind(available);
    }
    if let Some(special) = filter.special {
        query.push(" AND special = ").push_bind(special);
    }
    if let Some(min) = filter.min_price {
        query.push(" AND price_naira >= ").push_bind(min);
    }
    if let Some(max) = filter.max_price {
        query.push(" AND price_naira <= ").push_bind(max);
    }
    if let Some(text) = &filter.name_contains {
        query.push(" AND name ILIKE ").push_bind(format!("%{}%", escape_like(text)));
    }
}
```

**`QueryBuilder` has exactly two ways to add to the SQL, and the difference is the whole point:**

1. **`.push(text)`** adds text to the SQL itself. We only ever push fixed text from our code: `" AND available = "`, or a `column()` from the allowlist.
2. **`.push_bind(value)`** adds a `$1`, `$2`, ... to the SQL, and sends the value separately, exactly like lesson 8's bind parameters. Every value from the client goes this way.

So `/menu?available=true&maxPrice=2000&sort=-priceNaira` builds:

```sql
SELECT id, name, price_naira, available, special, portions_left FROM dishes
 WHERE true AND available = $1 AND price_naira <= $2
 ORDER BY price_naira DESC, id LIMIT $3 OFFSET $4
```

with `true`, `2000`, `20` and `0` sent beside it. The client chose the shape, from a menu of shapes we wrote; it never wrote any SQL.

Some details:

1. **`WHERE true`** is a trick so every condition can start with `AND`, whether it's the first or not. Postgres ignores it.
2. **`id` is always last in `ORDER BY`.** Two dishes at ₦1,200 could otherwise come back in either order, and a page boundary between them could show one twice and the other never.
3. **Two queries: a count and a page.** `meta.total` says how many match in all, so a client can show "page 2 of 4". The count uses the same `push_filters`, so the two can never disagree about what matches.
4. **`build_query_as::<Dish>()`** turns each row into a `Dish`, by column name. That needs one more derive on `Dish`: `#[derive(..., sqlx::FromRow)]`.
5. **`QueryBuilder<Postgres>`** says which database's SQL this is. (In sqlx 0.9 it has no lifetime parameter; older guides write `QueryBuilder<'_, Postgres>`.)

### What dynamic SQL costs

**This query isn't checked by the compiler.** `QueryBuilder` builds text while the program runs, so sqlx can't send it to the database at compile time. Misspell `price_naira` in `column()`, and you'll find out from a 500. That's the price of a query whose shape changes. Two things keep it small: the allowlist means there are only a few shapes, and a test of the list (practice 1) runs them. Everywhere the shape *is* fixed, keep `query_as!`. The kitchen's list, in step 6, stays checked.

### Searching, safely

`q=egusi` becomes `name ILIKE '%egusi%'`: **`ILIKE`** is Postgres's case-insensitive `LIKE`, and `%` means "anything". So `EGUSI`, `Egusi` and `egusi` all find "Egusi and pounded yam".

But `%` and `_` (any one character) are special inside the pattern. A customer searching for "50%" means the text "50%", not "50 followed by anything". So their text is escaped before the `%`s are put round it:

```rust
/// So a search for `50%` means the text "50%", not "50 followed by anything".
fn escape_like(text: &str) -> String {
    text.replace('\\', "\\\\").replace('%', "\\%").replace('_', "\\_")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn like_wildcards_are_escaped() {
        assert_eq!(escape_like("50%_off"), "50\\%\\_off");
    }
}
```

This isn't about SQL injection (the text is still a bind parameter, so it can't become SQL). It's about the search meaning what the customer typed. The backslash is escaped first, so a customer's own `\` can't escape our escapes.

### An index the search can use

A normal index can't help `ILIKE '%gus%'`: the search can start anywhere in the name, so Postgres would read every row. A **trigram index** can. It indexes every three-letter piece of each name (`"egu"`, `"gus"`, `"usi"`, ...), so a search can find the rows that contain all of its pieces. And the kitchen's list (step 6) wants orders in one status, by id. A migration for both, `migrations/0003_listing_indexes.sql`:

```sql
-- The kitchen's list: orders in one status, oldest first.
CREATE INDEX orders_status_id_idx ON orders (status, id);

-- Searching dish names with ILIKE '%...%'. A normal index can't help a search
-- that starts with a wildcard; a trigram index can.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX dishes_name_trgm_idx ON dishes USING gin (name gin_trgm_ops);
```

```bash
sqlx migrate run
```

`pg_trgm` comes with Postgres, and every managed Postgres (Supabase, Neon, RDS) allows it. With a few dishes, Postgres will ignore both indexes and just read the table, which is faster at that size. They're for when there are thousands.

## Step 5: the menu's list, with offset pages and field selection
<!-- bite: 041b1e24-a56f-424b-bae5-f8faeaf5e691 -->

The service passes the filter straight through:

```rust
    /// One page of dishes, and how many match in all.
    pub async fn list(&self, filter: &DishFilter) -> Result<(Vec<Dish>, i64), MenuError> {
        Ok(self.store.list(filter).await?)
    }
```

A list response needs somewhere to say where the page sits. In `src/http/error.rs`, beside `Data`:

```rust
/// A page of a list: `{"data": [...], "meta": {...}}`, with `meta` saying where this page sits.
#[derive(Serialize)]
pub struct Page<T, M> {
    pub data: Vec<T>,
    pub meta: M,
}

impl<T: Serialize, M: Serialize> IntoResponse for Page<T, M> {
    fn into_response(self) -> Response {
        Json(self).into_response()
    }
}
```

`M` is generic because the two kinds of page say different things: an offset page has a total, a cursor page has a next cursor. (This is the room beside `data` that lesson 7 promised.)

The handler:

```rust
#[derive(Serialize)]
struct OffsetMeta {
    limit: i64,
    offset: i64,
    total: i64,
}

async fn list(
    State(menu): State<MenuService>,
    ValidatedQuery(params): ValidatedQuery<ListParams>,
) -> Result<Page<Value, OffsetMeta>, ApiError> {
    // The rules above have passed, so every name in `sort` and `fields` is known.
    let sort = params.sort.as_deref().map(parse_sort).unwrap_or_default();
    let fields: Option<Vec<DishField>> = params.fields.as_deref().map(|raw| raw.split(',').filter_map(DishField::from_api_name).collect());

    let filter = DishFilter {
        available: params.available,
        special: params.special,
        min_price: params.min_price,
        max_price: params.max_price,
        name_contains: params.q,
        sort,
        limit: params.limit,
        offset: params.offset,
    };
    let (dishes, total) = menu.list(&filter).await?;

    let data = dishes.iter().map(|dish| only_fields(dish, fields.as_deref())).collect();
    Ok(Page { data, meta: OffsetMeta { limit: filter.limit, offset: filter.offset, total } })
}

fn parse_sort(raw: &str) -> Vec<DishSort> {
    raw.split(',')
        .filter_map(|part| {
            let (descending, name) = match part.strip_prefix('-') {
                Some(name) => (true, name),
                None => (false, part),
            };
            DishField::from_api_name(name).map(|field| DishSort { field, descending })
        })
        .collect()
}
```

1. **`params.sort.as_deref().map(parse_sort).unwrap_or_default()`**: `Option<String>` to `Option<&str>`, then parse it if it's there, else an empty `Vec` (no sorting asked for; just `id`).
2. **`filter_map`** keeps only the names that parse. They all will, because `known_sort` already passed, but the code doesn't have to trust that.

### Field selection

`fields=name,priceNaira` should send `{"id":1,"name":"Jollof rice","priceNaira":1500}` for each dish. A `Dish` is a struct, with all its fields, always. So for this, we turn each dish into JSON and remove the keys not asked for:

```rust
/// The dish as JSON, keeping only the fields asked for (and always its id).
fn only_fields(dish: &Dish, fields: Option<&[DishField]>) -> Value {
    let mut json = serde_json::to_value(dish).expect("a Dish always turns into JSON");
    if let (Some(fields), Value::Object(map)) = (fields, &mut json) {
        map.retain(|key, _| key == "id" || fields.iter().any(|f| f.api_name() == key));
    }
    json
}
```

1. **`serde_json::Value`** is "any JSON at all": an object, array, string, number, `true`/`false` or `null`, as an enum. `to_value` turns a `Dish` into a `Value::Object`.
2. **`if let (Some(fields), Value::Object(map)) = (fields, &mut json)`** matches two things at once: fields were asked for, *and* the JSON is an object. Only then do we trim.
3. **`map.retain(...)`** keeps the `id` (a client always needs to know which dish it is) and the fields asked for.
4. **`.expect(...)`**: turning a `Dish` into JSON can't fail (it has no maps with non-text keys, nothing exotic), so if it ever does, that's a bug, and a panic is right.

Field selection doesn't make the *database* do less (it still reads every column). It makes the response smaller, which matters for a phone on a slow connection. If a list's rows were wide (a long description, a photo URL list), you'd also choose the columns in the SQL.

## Step 6: cursor pagination for the kitchen
<!-- bite: aadd4270-baa3-4002-a533-c2c9220b0d77 -->

### Where offset pagination breaks

The kitchen screen shows pending orders, oldest first, 20 per page. It loads page 1 (`offset=0`): orders 1 to 20. While the cook is reading, orders 3 and 7 are marked ready, so they're no longer pending. Now the cook taps "next" (`offset=20`). The list has shifted up by two, so items 21 and 22 slid into page 1's positions. Page 2 starts at what used to be item 23. **Orders 21 and 22 were never shown.** Two customers wait forever for food nobody started.

Offset means "skip N rows *as the list is now*", and the list changed. And it gets slow: `OFFSET 10000` makes Postgres find and throw away 10,000 rows first.

### After a bookmark, instead

A cursor says "after *this* order", not "after N orders". Order ids only go up (Postgres hands them out in order), so id order is the order they were placed in, and "after order 22" is `WHERE id > 22`. It doesn't matter what happened to the orders before it.

The filter, in `src/orders/model.rs`:

```rust
/// Which orders the kitchen wants, and where the page starts.
#[derive(Clone, Debug)]
pub struct OrderFilter {
    pub status: Option<Status>,
    /// Only orders with a bigger id than this: the cursor, unpacked.
    pub after: Option<i64>,
    pub limit: i64,
}
```

The store, in `src/orders/store.rs`. The shape of this query never changes, so it stays a **checked** query:

```rust
    async fn list(&self, filter: &OrderFilter) -> Result<Vec<Order>, StoreError> {
        // The shape never changes, only the values, so this one can stay a checked query.
        let orders = sqlx::query_as!(
            Order,
            r#"SELECT id, dish_id, quantity, total_naira, status AS "status: Status" FROM orders
               WHERE ($1::text IS NULL OR status = $1) AND id > $2
               ORDER BY id
               LIMIT $3"#,
            filter.status.map(Status::as_str),
            filter.after.unwrap_or(0),
            filter.limit
        )
        .fetch_all(&self.pool)
        .await?;
        Ok(orders)
    }
```

1. **`($1::text IS NULL OR status = $1)`** is an optional filter in fixed SQL: send `NULL` for "any status", and the first half is true for every row. `::text` tells Postgres the type of `$1`, which it can't guess from `IS NULL` alone.
2. **`filter.status.map(Status::as_str)`**: `Option<Status>` to `Option<&str>`, passing the function itself to `map`.
3. **`id > $2` with `ORDER BY id`** is the cursor. With the `(status, id)` index from step 4, Postgres jumps straight to the bookmark instead of counting rows, so page 500 is as fast as page 1.

The service asks for one more than a page:

```rust
    /// One page of the kitchen's list, and the id to carry on after, if there's more.
    pub async fn list(&self, filter: &OrderFilter) -> Result<(Vec<Order>, Option<i64>), OrderError> {
        // Ask for one more than a page. If it comes back, there's a next page.
        let mut orders = self.store.list(&OrderFilter { limit: filter.limit + 1, ..filter.clone() }).await?;
        let more = orders.len() as i64 > filter.limit;
        orders.truncate(filter.limit as usize);
        let next = if more { orders.last().map(|o| o.id) } else { None };
        Ok((orders, next))
    }
```

If the extra order comes back, there's a next page, so we drop it and point the cursor at the last order we kept. If not, this is the last page, and there's no cursor. One query, and no count.

### The cursor itself

The client shouldn't build cursors, or depend on what's inside them (we might change it to a time and an id one day). So the bookmark is packed into one opaque piece of text. In `src/orders/handlers.rs`:

```rust
/// What's inside a cursor. Clients never see this: they get it packed into an opaque string.
#[derive(Serialize, Deserialize)]
struct Bookmark {
    after: i64,
}

fn pack(bookmark: &Bookmark) -> String {
    URL_SAFE_NO_PAD.encode(serde_json::to_vec(bookmark).expect("a Bookmark always turns into JSON"))
}

fn unpack(cursor: &str) -> Result<Bookmark, ApiError> {
    let bytes = URL_SAFE_NO_PAD.decode(cursor).ok();
    bytes.and_then(|b| serde_json::from_slice(&b).ok()).ok_or_else(|| {
        ApiError::new(
            StatusCode::BAD_REQUEST,
            "bad-cursor",
            "Cursor can't be read",
            "Use the nextCursor from the last page, as it was.",
        )
    })
}
```

**`URL_SAFE_NO_PAD`** is base64 using only letters, digits, `-` and `_`, with no `=` at the end, so it goes in a URL without escaping. `{"after":2}` becomes `eyJhZnRlciI6Mn0`. It isn't secret (anyone can decode it), and it doesn't need to be: a client that forges one can only skip ahead in a list it was allowed to see. Lesson 13 decides who may see which orders.

The handler, and its query string:

```rust
/// `GET /orders`'s query string: the kitchen's list.
#[derive(Deserialize, Validate)]
#[serde(deny_unknown_fields)]
struct ListParams {
    status: Option<Status>,
    #[serde(default = "twenty")]
    #[validate(range(min = 1, max = 100, message = "must be from 1 to 100"))]
    limit: i64,
    cursor: Option<String>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct CursorMeta {
    limit: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    next_cursor: Option<String>,
}

async fn list(
    State(orders): State<OrderService>,
    ValidatedQuery(params): ValidatedQuery<ListParams>,
) -> Result<Page<Order, CursorMeta>, ApiError> {
    let after = params.cursor.as_deref().map(unpack).transpose()?.map(|b| b.after);
    let filter = OrderFilter { status: params.status, after, limit: params.limit };
    let (data, next) = orders.list(&filter).await?;
    let next_cursor = next.map(|after| pack(&Bookmark { after }));
    Ok(Page { data, meta: CursorMeta { limit: params.limit, next_cursor } })
}
```

**`.map(unpack).transpose()?`**: `map` gives an `Option<Result<Bookmark, ApiError>>`. **`transpose`** swaps it into a `Result<Option<Bookmark>, ApiError>`, so `?` can return the error. No cursor is fine (`Ok(None)`, the first page); a bad cursor is a 400.

`status: Option<Status>` reads `?status=pending` with the same serde rules as the JSON, so `?status=cooked` is refused at the door. And the route goes in the kitchen router, behind the staff key:

```rust
    let kitchen = Router::new()
        .route("/orders", get(list))
        .route("/orders/{id}/status", patch(set_status))
```

`POST /orders` (public) and `GET /orders` (kitchen) share a path, merged as in lesson 3.

## Trying it
<!-- bite: af49782f-44e3-4f59-b901-c582aad9613c -->

```bash
cargo run
```

From a run of this lesson's code, with three more dishes added and a few orders placed:

```bash
curl -s 'localhost:8080/menu?limit=2'
# {"data":[{"id":1,"name":"Jollof rice",...},{"id":2,"name":"Beans and plantain",...}],
#  "meta":{"limit":2,"offset":0,"total":6}}

curl -s 'localhost:8080/menu?available=true&maxPrice=2000&sort=-priceNaira&fields=name,priceNaira'
# {"data":[{"id":1,"name":"Jollof rice","priceNaira":1500},{"id":2,"name":"Beans and plantain","priceNaira":1200},
#          {"id":6,"name":"50% off suya","priceNaira":900},{"id":4,"name":"Moi moi","priceNaira":700}],
#  "meta":{"limit":20,"offset":0,"total":4}}

curl -s 'localhost:8080/menu?q=EGUSI'
# {"data":[{"id":3,"name":"Egusi and pounded yam",...}],"meta":{"limit":20,"offset":0,"total":1}}

curl -s 'localhost:8080/menu?q=50%25'
# just "50% off suya": the % is the text, not "anything"

curl -s 'localhost:8080/menu?limit=500&sort=price&fields=colour'
# 400 {"code":"invalid-fields",...,"errors":[
#   {"field":"fields","message":"each name must be one of: id, name, priceNaira, available, special, portionsLeft"},
#   {"field":"limit","message":"must be from 1 to 100"},
#   {"field":"sort","message":"each name must be one of: id, name, priceNaira, available, special, portionsLeft"}]}

curl -s 'localhost:8080/menu?maxprice=2000'
# 400 {"code":"bad-query",...,"detail":"Failed to deserialize query string: maxprice: unknown field `maxprice`,
#   expected one of `limit`, `offset`, `available`, `special`, `minPrice`, `maxPrice`, `q`, `sort`, `fields`"}
```

And the kitchen's list, two at a time:

```bash
curl -s -H 'x-staff-key: sekret' 'localhost:8080/orders?status=pending&limit=2'
# {"data":[{"id":1,...},{"id":2,...}],"meta":{"limit":2,"nextCursor":"eyJhZnRlciI6Mn0"}}

curl -s -H 'x-staff-key: sekret' 'localhost:8080/orders?status=pending&limit=2&cursor=eyJhZnRlciI6Mn0'
# {"data":[{"id":3,...},{"id":4,...}],"meta":{"limit":2}}      ← no nextCursor: the last page

curl -s -H 'x-staff-key: sekret' 'localhost:8080/orders?cursor=nonsense'
# 400 {"code":"bad-cursor",...,"detail":"Use the nextCursor from the last page, as it was."}
```

Mark order 1 ready between the two pages, and page 2 still starts at order 3. Nothing is skipped.

There's no `total` and no "jump to page 9" on the kitchen's list. That's the trade: cursors give you correct, fast "next, next, next", which is what a kitchen screen or an infinite-scroll feed needs. Offsets give you "page 9 of 12", which suits a menu that rarely changes. Use each where it fits.

## The Rust in this lesson
<!-- bite: 37291163-3192-45ae-871a-960d9d90d51b -->

1. **An enum as an allowlist**, with `match` methods mapping each variant to fixed `&'static str`s.
2. **`sqlx::QueryBuilder`, `.push()` and `.push_bind()`**: dynamic SQL, where only fixed text is pushed and every value is bound.
3. **`build_query_as::<T>()` and `build_query_scalar()`**, with **`#[derive(sqlx::FromRow)]`**: run a built query into a struct or one value.
4. **`#[validate(custom(function = "..."))]`** and **`ValidationError::new(...).with_message(...)`**: your own rule, reported with the others.
5. **`FromRequestParts`** and **`&mut Parts`**: an extractor that only reads the request's head.
6. **`str::split`, `strip_prefix`, `Iterator::all`, `filter_map`**: pulling a comma-separated list apart.
7. **`serde_json::Value`** and **`Map::retain`**: JSON of any shape, and removing keys.
8. **Matching a tuple, `if let (Some(a), Value::Object(b)) = (x, &mut y)`**: two patterns at once.
9. **`Option::transpose`**: `Option<Result<T, E>>` into `Result<Option<T>, E>`, so `?` works.
10. **Passing a method as a function, `.map(Status::as_str)`**.
11. **Struct update with a clone, `OrderFilter { limit: ..., ..filter.clone() }`**.
12. **`Vec::truncate`**: keep the first N.
13. **A generic struct with two type parameters, `Page<T, M>`**, and its `IntoResponse` for any `T` and `M` that serialize.
14. **`base64::Engine` and `URL_SAFE_NO_PAD`**: a trait brought into scope so its `encode` and `decode` work on the engine.

## Your project so far
<!-- bite: 0929057e-1854-4691-88fd-0536ca997338 -->

```text
mama-put/
├── Cargo.toml             ← + base64; serde_json (preserve_order)
├── migrations/
│   ├── 0001_create_dishes.sql
│   ├── 0002_create_orders.sql
│   └── 0003_listing_indexes.sql   ← (status, id) on orders; pg_trgm on dish names
└── src/
    ├── http/
    │   ├── error.rs       ← + Page<T, M>
    │   └── extract.rs     ← + ValidatedQuery (FromRequestParts)
    ├── menu/
    │   ├── model.rs       ← + DishFilter, DishSort, DishField (the allowlist); Dish: FromRow
    │   ├── store.rs       ← list(filter) with QueryBuilder: count and page; push_filters; escape_like + test
    │   ├── service.rs     ← list(filter); specials as a filter
    │   └── handlers.rs    ← ListParams with custom rules; parse_sort; only_fields; OffsetMeta
    └── orders/
        ├── model.rs       ← + OrderFilter
        ├── store.rs       ← list(filter): a checked query, id > cursor
        ├── service.rs     ← list: one more than a page
        └── handlers.rs    ← GET /orders (kitchen); Bookmark, pack, unpack; CursorMeta
```

## Common mistakes
<!-- bite: 1f4aa0d6-12d4-476c-9e0c-8689481a46b1 -->

1. **Pushing client text with `.push()`.** That's SQL injection with extra steps. Values go through `.push_bind()`; names go through an allowlist.
2. **No maximum on `limit`.** `limit=1000000` is "send everything" again.
3. **Sorting without a tie-breaker.** Equal prices come back in any order, and pages overlap. Always end with `id`.
4. **Offset pagination on a list that changes.** Items get skipped or shown twice. Use a cursor.
5. **A cursor the client builds.** Then you can never change what's in it. Make it opaque.
6. **`ILIKE` without escaping.** A search for "50%" matches everything starting "50".
7. **Silently ignoring an unknown parameter.** `?maxprice=` that does nothing looks like a broken filter. Refuse it.
8. **Reaching for `QueryBuilder` when the shape is fixed.** You give up the compile-time check for nothing. `($1 IS NULL OR ...)` keeps optional filters in a checked query.
9. **Column names in the API.** `sort=price_naira` ties clients to your database forever. Use the API's names and map them.

## Check your understanding
<!-- bite: 42f3ddfd-7b0d-44c3-b042-dc44456c7e33 -->

1. Why can't a column name in `ORDER BY` be a bind parameter, and how does `DishField` keep `sort=` safe anyway?
2. What's the difference between `.push()` and `.push_bind()` on a `QueryBuilder`, and what may go into each?
3. What does the menu's list lose by using `QueryBuilder` instead of `query_as!`, and how do we limit the damage?
4. Why does every `ORDER BY` end with `id`?
5. A customer searches for `50%`. What does `escape_like` change, and is that about security?
6. Describe exactly how the kitchen screen skips orders with offset pagination.
7. How does the service know there's a next page without counting?
8. The kitchen's list has an optional status filter but stays a checked query. How?

<details>
<summary>Answers, after your attempt</summary>

1. Because a bind parameter is always a value, never a name in the SQL: `ORDER BY $1` sorts by a constant. So the column must be written into the SQL text. `DishField` makes the client's text only a lookup key: what's written into the SQL is `column()`, one of six fixed strings from our code, and any other name is refused before the SQL is built.
2. `.push()` adds text to the SQL itself, so only fixed text from our code may go in: keywords, operators, allowlisted column names. `.push_bind()` adds a `$n` placeholder and sends the value separately, so every value from the client goes there.
3. The compile-time check: the SQL is built at run time, so a mistake shows up as an error when the query runs. The allowlist keeps the possible shapes few, a test of the list runs them, and the queries whose shape is fixed stay `query_as!`.
4. So rows that tie on the requested sort always come back in the same order. Without it, two dishes at the same price can swap between requests, and a page boundary between them shows one twice and the other never.
5. It puts a backslash before `%`, `_` and `\`, so they mean themselves in the `ILIKE` pattern, and the search finds names containing the text "50%". It isn't about security, since the text is a bind parameter either way; it's about the search meaning what was typed.
6. Page 1 shows the first 20 pending orders. Two of them are marked ready, so the pending list shifts up by two. Page 2 asks to skip 20, which now skips two orders that page 1 never showed, so those two are never seen.
7. It asks the store for one more than the page size. If that extra order comes back, there's a next page: it's dropped, and the cursor points at the last order kept. If not, this is the last page.
8. With `($1::text IS NULL OR status = $1)`: the SQL is fixed, and sending `NULL` makes the condition true for every row. The shape never changes, so `query_as!` can check it.

</details>

## Practice
<!-- bite: 370cdb7c-33bf-40a3-a513-4bb910fef723 -->

1. Write a `#[sqlx::test]` for `PgMenuStore::list` that runs every sort field, both ways, so a typo in `column()` fails a test instead of a customer's request.
2. Refuse `minPrice` bigger than `maxPrice`, with a struct-level validator rule: `#[validate(schema(function = "..."))]` on `ListParams`.
3. Add `GET /orders?dishId=1` to the kitchen's list, keeping the query checked.
4. Change the cursor to carry the order's `created_at` and `id`, and sort by both. What would you need to change in the migration's index? (`sqlx` needs its `time` or `chrono` feature to read a `timestamptz`.)
5. Make `fields=` also choose the columns in the SQL. Is it worth it for six small columns?

**Done when** `GET /menu` filters, searches, sorts and pages in SQL with every value bound and every name allowlisted, all its query mistakes come back in one answer, unknown parameters are refused, a search for `50%` means the text, fields can be trimmed, the kitchen's `GET /orders` pages with a cursor that never skips an order, the indexes are in a migration, and `cargo test` passes.

## Before moving on
<!-- bite: 2a3a1ffc-7303-45d4-a782-7604229dc685 -->

Mama Put's lists now behave like a real API's: a page at a time, filtered and sorted in the database, searched safely, trimmed for small screens, and, for the kitchen, paged with a cursor that can't skip an order. And you've seen where Rust's compile-time SQL checks stop, at dynamic SQL, and how to keep that gap small.

Now Mama has a new problem, and it's a happy one. Paystack works in **kobo**, not naira, and the phone team wants prices as `{"amount": 150000, "currency": "NGN"}`. That changes the shape of every dish in every response. But last month's app, on thousands of phones, expects `priceNaira`. Next lesson: versioning, with v1 and v2 side by side, and retiring v1 properly.

## Related
<!-- bite: 6766d056-a113-42ad-a605-cf6d9b601f11 -->

- [[backend/frameworks/axum/10-versioning|Next: Versioning]]
- [[backend/frameworks/net-http/09-listing|The same lesson in net/http]] — a query reader that collects every mistake, and building SQL by hand
- [[backend/frameworks/axum/08-data-with-postgres|Data with PostgreSQL]] — bind parameters, and the checked queries this lesson sometimes gives up
- [[databases/index|Databases]] — indexes, and why `OFFSET` gets slow

## About this lesson
<!-- bite: 73036952-1f13-47e1-8260-b64f0a9d6d18 -->

**Level:** Intermediate → Advanced. Lesson 9 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, sqlx 0.9 and PostgreSQL 18. Covers designing list parameters in the API's words with a maximum `limit`, a `ValidatedQuery` extractor with `FromRequestParts`, custom validator rules reported together, an enum allowlist mapping API names to columns, dynamic SQL with `QueryBuilder`'s `push` and `push_bind`, a count and a page sharing one filter function, `id` as the last sort key, what dynamic SQL loses and how to keep checked queries where the shape is fixed, `ILIKE` search with escaped wildcards and a `pg_trgm` index, field selection through `serde_json::Value` with `preserve_order`, a generic `Page<T, M>` envelope, why offset pagination skips items in a changing list, cursor pagination with one extra row, opaque base64 cursors, and `Option::transpose`.
