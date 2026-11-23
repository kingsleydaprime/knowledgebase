---
id: ad77293c-5635-4be7-9029-6aed2c57963f
---

# Data with PostgreSQL

**A database is where an app keeps its data so it survives restarts and is shared by every copy of the app, and PostgreSQL is the one most backends reach for first.** In Rust, the usual way to talk to it is **sqlx**: you write plain SQL, and sqlx checks every query against your real database **while the program compiles**. A misspelt column, a wrong type or a missing table is a compile error, not a 500 at lunchtime.

## Before you start
<!-- bite: e7978d08-85c4-44d3-890e-948e04807a65 -->

You should have:

1. Finished [[backend/frameworks/axum/07-errors|lesson 7]], so every error is a problem response and every success is `{"data": ...}`.
2. Docker or Podman installed, so you can run Postgres without installing it on your computer.
3. Written a `SELECT`, an `INSERT` and an `UPDATE` before. If you haven't, [[databases/index|Databases]] starts from zero.

After this lesson you will be able to:

1. Run Postgres in a container and connect to it from Rust with a sized pool.
2. Write migrations as SQL files, run them with sqlx's tool, and have the program run them at start-up too.
3. Write queries that the compiler checks against the real schema, with `query_as!`.
4. Make the lesson 5 store traits async, with `async_trait`, and explain why it's needed.
5. Use a transaction and a guarded `UPDATE` so the last plate goes to one customer, however many order at once.
6. Test against a real database, with a fresh one for every test.

## What to install
<!-- bite: 192e6d2b-cf64-4d9a-977d-b19b4db4f7f4 -->

**Postgres**, in a container:

```bash
docker run --name mama-put-db -d -p 5432:5432 \
  -e POSTGRES_USER=mama -e POSTGRES_PASSWORD=mama-local -e POSTGRES_DB=mamaput \
  postgres:18
```

(`podman` takes exactly the same command.) That starts Postgres 18 in the background, listening on port 5432, with a user `mama` and an empty database `mamaput`. `docker stop mama-put-db` stops it; `docker start mama-put-db` starts it again, with your data still there.

**The crates**:

```bash
cargo add sqlx --features runtime-tokio,postgres,macros,migrate
cargo add async-trait dotenvy
```

1. **`sqlx`** talks to the database. `runtime-tokio` makes it use Tokio; `postgres` is the database; `macros` gives `query!` and `query_as!`, the compile-time checked queries; `migrate` gives the migration runner.
2. **`async-trait`** lets a trait with async methods be used as `dyn` (step 4).
3. **`dotenvy`** reads a `.env` file into the environment, for running on your laptop.

**sqlx's command-line tool**, once per computer:

```bash
cargo install sqlx-cli --no-default-features --features rustls,postgres
```

It runs migrations and creates databases. The flags build only the Postgres part, which makes it much quicker to install. This takes a few minutes; it's compiling a program.

## Where we stopped
<!-- bite: ffed1662-3668-4098-b989-0ff9c592a48c -->

Everything lives in memory. Stop the server and Mama's moi moi is gone, and so is every order. Run two copies behind a load balancer and each has its own menu: the kitchen marks jollof finished on one, and customers on the other keep ordering it.

There's a quieter problem too. Mama doesn't have endless jollof. She cooks 40 plates in the morning, and when they're gone, they're gone. The menu needs a `portionsLeft` count, and when two customers order the very last plate at the same moment, only one of them can get it.

## The kid version
<!-- bite: 2343f054-fcda-474d-bd62-af3418e8e2fc -->

Up to now, Mama has kept the day's orders in her head. When she goes home, they're gone. If her sister helps at a second table, the sister has no idea what Mama promised.

A database is the big notebook on the counter. Everyone writes in the same book, it's still there tomorrow, and when two people reach for the last plate at the same time, the notebook decides who wrote first.

**Where the picture stops working.** A real notebook is in one place. Your database is on another computer (or in a container), and every trip to it takes time and can fail. So your code keeps a few lines to it always open (the pool), and has to be ready for the day the notebook doesn't answer.

## Terms used in this lesson
<!-- bite: 0f80cd6f-8413-4c0e-80cb-e68d5fd31611 -->

1. **Connection string**: This is one line saying where the database is and how to log in: `postgres://user:password@host:5432/dbname`. It holds a password, so it's a secret.
2. **Connection pool**: This is a set of open connections to the database that requests borrow and give back. Opening a connection is slow, so a pool opens a few and reuses them.
3. **Migration**: This is a numbered file of SQL that changes the database's structure, like creating a table. Migrations run in order, once each, and are never edited after they've run anywhere.
4. **Bind parameter**: This is a marker in SQL, like `$1`, where a value goes. The value is sent separately from the SQL, so it can never be read as SQL.
5. **SQL injection**: This is an attack where someone sends text that becomes part of your SQL, so they can read or change data they shouldn't. Bind parameters stop it completely.
6. **Transaction**: This is a group of SQL statements that either all happen or none do. It starts with `BEGIN` and ends with `COMMIT` (keep everything) or `ROLLBACK` (undo everything).
7. **Race condition**: This is a bug where the result depends on which of two things happens first, like two requests both seeing "1 plate left".
8. **Compile-time checked query**: This is a query that sqlx sends to your database while compiling, to ask "is this valid, and what types come back?". If the answer is no, the program doesn't build.

## Step 1: keep the connection string out of the code
<!-- bite: b4e6eb76-d38b-4d39-9448-be59b4374770 -->

The program needs to know where the database is. That's a secret (it has the password), and it's different on your laptop, in CI and in production. So it comes from an environment variable, `DATABASE_URL`, like the staff key.

For your laptop, put both in a file called `.env` at the root of the project:

```text
DATABASE_URL=postgres://mama:mama-local@localhost:5432/mamaput
STAFF_KEY=sekret
```

and **keep it out of git**, in `.gitignore`:

```text
/target
.env
```

Two programs read `.env`: sqlx's macros, while compiling (step 3), and your program, with one line at the top of `main` (step 7). In production there's no `.env`; the real environment variables are set by whatever runs the server, and they win over the file.

## Step 2: the tables, as migrations
<!-- bite: fd971cb0-88b8-416c-9b1c-926d52b59970 -->

You could create tables by typing SQL into Postgres by hand. Then your laptop, your teammate's laptop and production would each end up slightly different, and nobody would know how. Migrations fix that: every change to the database's structure is a numbered SQL file in git, and every database runs the same files in the same order.

Make a folder `migrations/` in the project root. sqlx wants each file named `<number>_<what it does>.sql`. `migrations/0001_create_dishes.sql`:

```sql
CREATE TABLE dishes (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name          text    NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
  price_naira   bigint  NOT NULL CHECK (price_naira > 0),
  available     boolean NOT NULL DEFAULT true,
  special       boolean NOT NULL DEFAULT false,
  portions_left integer NOT NULL DEFAULT 0 CHECK (portions_left >= 0),
  created_at    timestamptz NOT NULL DEFAULT now()
);
```

`migrations/0002_create_orders.sql`:

```sql
CREATE TABLE orders (
  id          bigint  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  dish_id     bigint  NOT NULL REFERENCES dishes (id),
  quantity    integer NOT NULL CHECK (quantity BETWEEN 1 AND 20),
  total_naira bigint  NOT NULL CHECK (total_naira > 0),
  status      text    NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending', 'ready', 'collected')),
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX orders_dish_id_idx ON orders (dish_id);
```

The same two tables as the [[backend/frameworks/net-http/08-data-with-postgres|net/http]] and Express versions, so the same database could serve all three. A few choices worth seeing:

1. **`GENERATED ALWAYS AS IDENTITY`** makes Postgres choose each new `id`, counting up. No more `next_id` and mutex.
2. **`CHECK` constraints** repeat Mama's rules in the database itself: a price above 0, no negative portions, only three statuses. If a bug in our Rust ever tries to break them, Postgres refuses. The database is the last line of defence, and the only one that holds for every program that ever touches it.
3. **`REFERENCES dishes (id)`** is a **foreign key**: an order can't point at a dish that doesn't exist, and a dish with orders can't be deleted (step 6 turns that into a proper answer).
4. **`timestamptz`** stores a moment in time with the time zone handled properly. Always use it, not `timestamp`.
5. **The index on `dish_id`** makes "orders for this dish" fast. Postgres doesn't create indexes for foreign keys by itself.
6. **`bigint` for ids and money, `integer` for counts.** In Rust, `bigint` is `i64` and `integer` is `i32`. Postgres has no unsigned numbers, so the `u64` ids from earlier lessons become `i64`.

Run them:

```bash
sqlx migrate run
```

```text
Applied 1/migrate create dishes (5.368933ms)
Applied 2/migrate create orders (5.821026ms)
```

`sqlx migrate run` reads `DATABASE_URL` from `.env`, runs every migration that hasn't run yet, in order, and records each one in a table of its own, `_sqlx_migrations`. Run it again and it does nothing: they've all run.

**Never edit a migration after it has run anywhere.** sqlx stores a checksum of each file, and refuses to start if one has changed. To change a table, write a new migration (`0003_...sql`) that alters it.

Mama's starting dishes go in a separate file, `seed.sql`, because sample data isn't structure, and production should never get it:

```sql
-- Mama's starting menu. Run once, by hand: psql "$DATABASE_URL" -f seed.sql
INSERT INTO dishes (name, price_naira, available, special, portions_left) VALUES
  ('Jollof rice',           1500, true,  true,  40),
  ('Beans and plantain',    1200, true,  false, 25),
  ('Egusi and pounded yam', 2500, false, false, 0);
```

## Step 3: the pool, and one error for every store
<!-- bite: 4990a5f4-86f4-42b9-9a4b-ac6b2557b03d -->

A new module, `src/db.rs`, and `pub mod db;` in `lib.rs`:

```rust
//! The connection pool, and the one error type every Postgres store returns.

use std::time::Duration;

use sqlx::{PgPool, postgres::PgPoolOptions};

/// Opens a pool of connections. Call once, in `main`.
pub async fn connect(database_url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(10)
        .acquire_timeout(Duration::from_secs(3))
        .connect(database_url)
        .await
}

/// A store couldn't do its job: the database was down, a query failed, a constraint said no.
#[derive(Debug, thiserror::Error)]
#[error(transparent)]
pub struct StoreError(#[from] sqlx::Error);

impl StoreError {
    /// True when Postgres refused because a foreign key still points at the row.
    pub fn is_foreign_key_violation(&self) -> bool {
        matches!(&self.0, sqlx::Error::Database(e) if e.is_foreign_key_violation())
    }
}
```

1. **`PgPool`** is the pool. It's cheap to clone (an `Arc` inside), so every store gets its own clone of the same pool.
2. **`max_connections(10)`**: at most ten open connections from this copy of the app. Postgres allows about 100 in total by default, and every copy of the app, every worker and every admin tool shares them. Ten copies of the app with the default of ten each is already the whole database.
3. **`acquire_timeout(3s)`**: if all ten are busy and none is given back within three seconds, give up with an error instead of waiting forever. A request that waits forever holds memory, a socket and a customer's patience.
4. **`StoreError`** wraps `sqlx::Error`, so the services can say "the store failed" without naming sqlx. **`#[error(transparent)]`** means "print the error inside, as it is", and **`#[from]`** writes `From<sqlx::Error>`, so `?` in a store converts for us.
5. **`is_foreign_key_violation`** looks inside: is it an error *from the database* (`sqlx::Error::Database`), and is it the one where a foreign key said no? `matches!(value, pattern if condition)` is `true` if the value fits the pattern and the condition holds.

## Step 4: async store traits
<!-- bite: 7f0f9904-d5a1-4240-aebf-ecf93d0dbce4 -->

Every database call waits on the network, so every store method becomes `async`. Here's the menu's trait, in `src/menu/store.rs`:

```rust
/// What the menu needs from wherever dishes are kept.
#[async_trait]
pub trait MenuStore: Send + Sync {
    async fn list(&self) -> Result<Vec<Dish>, StoreError>;
    async fn find(&self, id: i64) -> Result<Option<Dish>, StoreError>;
    async fn add(&self, new: NewDish) -> Result<Dish, StoreError>;
    async fn change(&self, id: i64, changes: DishChanges) -> Result<Option<Dish>, StoreError>;
    /// `false` if there was no such dish.
    async fn remove(&self, id: i64) -> Result<bool, StoreError>;
}
```

Why **`#[async_trait]`**? Rust lets you write `async fn` in a trait without it. But then the trait isn't **dyn compatible**, the problem from lesson 5 again. Each `async fn` returns its own hidden future type, different for every implementation, and a vtable can't hold "a different return type per type". `MenuService` holds `Arc<dyn MenuStore>`, so it needs `dyn`.

`#[async_trait]` rewrites each `async fn` to return one type for everyone: `Pin<Box<dyn Future<Output = ...> + Send>>`, "a boxed future". One heap allocation per call, a few nanoseconds, next to a database round trip of a millisecond. Put it on the trait and on every `impl` of it.

Every method now returns a `Result`, because every trip to the database can fail. Notice what *isn't* an error: "no such dish" is `Ok(None)`. The store's job is to say what's there; deciding that a missing dish is a problem is the service's.

The memory stores from lesson 5 are gone. They can't do what Postgres does in step 6 (a guarded update across every copy of the app), and step 9 shows that tests can use a real database just as easily.

## Step 5: the menu store, with checked queries
<!-- bite: 4c4385ab-4d28-4aec-98c4-51b19c9953a4 -->

The rest of `src/menu/store.rs`:

```rust
/// Dishes kept in PostgreSQL.
pub struct PgMenuStore {
    pool: PgPool,
}

impl PgMenuStore {
    pub fn new(pool: PgPool) -> Self {
        PgMenuStore { pool }
    }
}

#[async_trait]
impl MenuStore for PgMenuStore {
    async fn list(&self) -> Result<Vec<Dish>, StoreError> {
        let dishes = sqlx::query_as!(
            Dish,
            "SELECT id, name, price_naira, available, special, portions_left FROM dishes ORDER BY id"
        )
        .fetch_all(&self.pool)
        .await?;
        Ok(dishes)
    }

    async fn find(&self, id: i64) -> Result<Option<Dish>, StoreError> {
        let dish = sqlx::query_as!(
            Dish,
            "SELECT id, name, price_naira, available, special, portions_left FROM dishes WHERE id = $1",
            id
        )
        .fetch_optional(&self.pool)
        .await?;
        Ok(dish)
    }
```

**`sqlx::query_as!(Dish, "SELECT ...", id)`** does three things, and two of them happen while compiling:

1. **At compile time, it sends the SQL to the database** named by `DATABASE_URL` and asks Postgres to check it, without running it. A misspelt column or table is a compile error.
2. **At compile time, it checks the types.** Postgres says the query returns a `bigint`, a `text`, and so on; sqlx checks each matches the field of the same name in `Dish` (`i64`, `String`). Change `price_naira` to `i32` in `Dish` and it won't build. It checks the arguments too: `$1` is compared with a `bigint`, so `id` must be an `i64`.
3. **At run time**, it sends the query with `id` as a **bind parameter**, and builds a `Dish` from each row.

Then **`.fetch_all`** for every row, **`.fetch_optional`** for zero or one (`Option<Dish>`), **`.fetch_one`** for exactly one (an error if there's none).

Here's what the compiler says if you build before running the migrations:

```text
error: error returned from database: relation "dishes" does not exist
  --> src/menu/store.rs:32:22
   |
32 |           let dishes = sqlx::query_as!(
   |  ______________________^
33 | |             Dish,
34 | |             "SELECT id, name, price_naira, available, special, portions_left FROM dishes ORDER BY id"
35 | |         )
   | |_________^
```

It's the database's own error, at the line of the query. That's the deal sqlx offers: **building needs a database.** On your laptop, that's the container. For CI, where there may not be one, `cargo sqlx prepare` saves every query's checked description into a `.sqlx/` folder you commit, and builds use that instead (lesson 39 sets it up).

Adding, changing and removing:

```rust
    async fn add(&self, new: NewDish) -> Result<Dish, StoreError> {
        let dish = sqlx::query_as!(
            Dish,
            "INSERT INTO dishes (name, price_naira, available, special, portions_left)
             VALUES ($1, $2, $3, $4, $5)
             RETURNING id, name, price_naira, available, special, portions_left",
            new.name,
            new.price_naira,
            new.available,
            new.special,
            new.portions_left
        )
        .fetch_one(&self.pool)
        .await?;
        Ok(dish)
    }

    async fn change(&self, id: i64, changes: DishChanges) -> Result<Option<Dish>, StoreError> {
        // COALESCE($2, name): "the new value if one was sent, otherwise keep the old one".
        let dish = sqlx::query_as!(
            Dish,
            "UPDATE dishes SET
                name          = COALESCE($2, name),
                price_naira   = COALESCE($3, price_naira),
                available     = COALESCE($4, available),
                special       = COALESCE($5, special),
                portions_left = COALESCE($6, portions_left)
             WHERE id = $1
             RETURNING id, name, price_naira, available, special, portions_left",
            id,
            changes.name,
            changes.price_naira,
            changes.available,
            changes.special,
            changes.portions_left
        )
        .fetch_optional(&self.pool)
        .await?;
        Ok(dish)
    }

    async fn remove(&self, id: i64) -> Result<bool, StoreError> {
        let result = sqlx::query!("DELETE FROM dishes WHERE id = $1", id).execute(&self.pool).await?;
        Ok(result.rows_affected() == 1)
    }
}
```

1. **`RETURNING ...`** gives back the row as it is after the change, so one round trip both writes and reads. The new `id` comes from Postgres.
2. **`COALESCE($2, name)`** is how `PATCH` works in one statement. `changes.name` is an `Option<String>`; sqlx sends `None` as SQL `NULL`, and `COALESCE` picks the first value that isn't `NULL`. Sent a name? Use it. Didn't? Keep the old one.
3. **`fetch_optional` on the `UPDATE`**: no row matched the `id`, so nothing came back: `None`, and the service says "not found".
4. **`query!`** (no `_as`) when there's nothing to build. `.execute` returns how many rows were touched.

The models gain the new field, `portions_left: i32`, and the ids become `i64`. `Dish` keeps all its fields; `NewDish` and `DishChanges` get a rule:

```rust
    #[serde(default)]
    #[validate(range(min = 0, max = 1000, message = "must be from 0 to 1,000"))]
    pub portions_left: i32,
```

### Why bind parameters matter: SQL injection

You might be tempted to build SQL with `format!`:

```rust
let sql = format!("SELECT * FROM dishes WHERE name = '{name}'"); // never
```

Now a customer searches for the name `x' OR '1'='1`. The SQL becomes `... WHERE name = 'x' OR '1'='1'`, which is true for every row. With `'; DROP TABLE orders; --`, worse. The customer's text became part of your program.

With `$1`, that can't happen. The SQL goes to Postgres first, with a hole in it, and the value is sent separately, as data. However many quotes it has, it's only ever compared as a name. `query!` and `query_as!` make it hard to do anything else: the SQL must be a fixed string written in your code, so there's nowhere to paste a customer's text. (Lesson 9 builds SQL whose shape changes with the request, and still never pastes a value into it.)

## Step 6: services that await, and the last plate
<!-- bite: f66ea948-4c4e-4ef4-839e-cf027062de8a -->

The services await their stores, and their errors gain two variants. `MenuError`, in `src/menu/service.rs`:

```rust
/// Everything that can go wrong with the menu, as far as Mama's rules are concerned.
#[derive(Debug, thiserror::Error)]
pub enum MenuError {
    #[error("there's no dish {0}")]
    NotFound(i64),
    #[error("a dish needs a name")]
    NoName,
    #[error("a price must be more than ₦0")]
    BadPrice,
    #[error("dish {0} has orders, so it can't be removed; mark it unavailable instead")]
    HasOrders(i64),
    #[error(transparent)]
    Store(#[from] StoreError),
}
```

1. **`Store(#[from] StoreError)`**: "the store failed". `#[from]` means `?` on a store call converts a `StoreError` into `MenuError::Store`, so the service code stays short.
2. **`PartialEq` is gone** from the derive, because `sqlx::Error` can't be compared. Tests now use `matches!` (step 9).

Each method gains `async` and `.await`. Two are worth a look:

```rust
    pub async fn get(&self, id: i64) -> Result<Dish, MenuError> {
        self.store.find(id).await?.ok_or(MenuError::NotFound(id))
    }
```

Read it left to right: ask the store, wait for it, return early if the store failed (`?`), then turn "nothing there" into `NotFound`.

```rust
    pub async fn remove(&self, id: i64) -> Result<(), MenuError> {
        match self.store.remove(id).await {
            Ok(true) => Ok(()),
            Ok(false) => Err(MenuError::NotFound(id)),
            Err(e) if e.is_foreign_key_violation() => Err(MenuError::HasOrders(id)),
            Err(e) => Err(e.into()),
        }
    }
```

A dish with orders can't be deleted: the foreign key says no. That's not a bug, it's a rule, so it gets its own variant, and the client gets a 409 telling them what to do instead. Every other store error is passed up as it is (`e.into()` uses the same `From`).

In each `handlers.rs`, the `From` for `ApiError` sends store errors to lesson 7's `internal`:

```rust
            MenuError::HasOrders(_) => (StatusCode::CONFLICT, "dish-has-orders", "Dish has orders"),
            MenuError::Store(e) => return ApiError::internal(e),
```

And every handler awaits: `Ok(Data(menu.get(id).await?))`.

### The last plate

Now the hard problem. Mama has 1 plate of jollof left. Ada and Bayo order at the same moment.

The obvious code looks like this:

```rust
let dish = menu.get(id).await?;               // Ada sees 1 left. Bayo sees 1 left.
if dish.portions_left < quantity { ... }      // both pass
menu.change(id, one_fewer).await?;            // both set it to 0
orders.insert(...).await?;                    // two orders, one plate
```

Between "look" and "take", the other request slipped in. That's a **race condition**, and it's the kind of bug that never shows up when you test alone, then shows up every Friday at lunch. The `Mutex` from lesson 2 can't help now: two copies of the app have two mutexes, and the plates are in the database.

The fix has two parts. **Look and take in one statement**, and **take the plate and write the order together.** `src/orders/store.rs`:

```rust
#[async_trait]
impl OrderStore for PgOrderStore {
    async fn place_taking_portions(&self, dish_id: i64, quantity: i32) -> Result<Option<Order>, StoreError> {
        let mut tx = self.pool.begin().await?;

        // Look and take in one statement, so nobody can get between them.
        let price = sqlx::query_scalar!(
            "UPDATE dishes SET portions_left = portions_left - $2
             WHERE id = $1 AND available AND portions_left >= $2
             RETURNING price_naira",
            dish_id,
            quantity
        )
        .fetch_optional(&mut *tx)
        .await?;

        let Some(price) = price else {
            return Ok(None); // `tx` is dropped here, so the transaction rolls back
        };

        let order = sqlx::query_as!(
            Order,
            r#"INSERT INTO orders (dish_id, quantity, total_naira) VALUES ($1, $2, $3)
               RETURNING id, dish_id, quantity, total_naira, status AS "status: Status""#,
            dish_id,
            quantity,
            price * i64::from(quantity)
        )
        .fetch_one(&mut *tx)
        .await?;

        tx.commit().await?;
        Ok(Some(order))
    }
```

**The guarded `UPDATE`.** `WHERE ... AND portions_left >= $2` means the row is only changed if there are enough plates. Postgres locks the row while it changes it. If Ada's update goes first, Bayo's **waits**; then Postgres checks `portions_left >= 1` again, finds 0, and changes **nothing**. No row comes back (`None`), so we know he was too late. The check and the change are one step nobody can get between.

**The transaction.** If we took the plate and then the order insert failed, Mama's pot would show one plate fewer and nobody would have an order. So:

1. **`self.pool.begin()`** starts a transaction, on one connection borrowed from the pool.
2. **`&mut *tx`** runs each query inside it. (`tx` is a `Transaction`; `*tx` is the connection inside it; `&mut` lends it to the query. The query needs the connection to itself while it runs.)
3. **`tx.commit()`** keeps everything.
4. **Any early return rolls back.** If either `?` returns an error, or the `let ... else` returns `Ok(None)`, `tx` goes out of scope, and its `Drop` sends `ROLLBACK`. No `defer`, no `finally`, no rollback to forget. It's the same RAII that unlocked the mutex guard in lesson 2.

Three more things in there:

1. **`query_scalar!`** returns one column of one row, here the price, as a plain `i64`.
2. **`let Some(price) = price else { ... };`** is **let-else**: "if it's `Some`, name what's inside `price`; otherwise run the block, which must leave the function".
3. **`status AS "status: Status"`** tells sqlx to read the `status` column as our `Status` enum. The enum learns how with one derive, in `src/orders/model.rs`:

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, sqlx::Type)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "text", rename_all = "lowercase")]
pub enum Status {
    Pending,
    Ready,
    Collected,
}

impl Status {
    pub const ALL: [Status; 3] = [Status::Pending, Status::Ready, Status::Collected];

    /// How the status is spelt in JSON and in the database.
    pub fn as_str(self) -> &'static str {
        match self {
            Status::Pending => "pending",
            Status::Ready => "ready",
            Status::Collected => "collected",
        }
    }
}
```

`#[sqlx(type_name = "text", rename_all = "lowercase")]` says "stored as `text`, spelt in lower case": `Status::Ready` is `'ready'`. (`r#"..."#` is a **raw string**: it can hold `"` without escaping, which the `AS "status: Status"` needs.)

The order service checks the dish first, for clear answers, then leaves the real decision to the store:

```rust
        // For a clear answer: does the dish exist, and is it on today?
        let dish = self.menu.get(new.dish_id).await.map_err(|e| match e {
            MenuError::Store(e) => OrderError::Store(e),
            _ => OrderError::NoSuchDish(new.dish_id),
        })?;
        if !dish.available {
            return Err(OrderError::DishUnavailable);
        }
        // The real check happens here, in one guarded statement, whoever else is ordering.
        self.store.place_taking_portions(dish.id, new.quantity).await?.ok_or(OrderError::NotEnoughPortions)
```

The first checks can go stale between the `get` and the store call (the kitchen could mark the dish unavailable in between). That's fine: they only exist to give a precise message. The guarded `UPDATE` repeats `AND available`, and it's the one that can't be raced. `NotEnoughPortions` is a 422 with the code `not-enough-portions`.

### Status changes, in SQL

Lesson 5's `set_status` took a closure that the store ran under its lock. A closure can't run inside Postgres, so the rule moves into the `WHERE`:

```rust
    async fn set_status(&self, id: i64, to: Status, from: &[Status]) -> Result<Option<Order>, StoreError> {
        let from: Vec<&str> = from.iter().map(|s| s.as_str()).collect();
        let order = sqlx::query_as!(
            Order,
            r#"UPDATE orders SET status = $2 WHERE id = $1 AND status = ANY($3)
               RETURNING id, dish_id, quantity, total_naira, status AS "status: Status""#,
            id,
            to.as_str(),
            &from as &[&str]
        )
        .fetch_optional(&self.pool)
        .await?;
        Ok(order)
    }
```

and the service says which statuses may move to `to`, the ones before it:

```rust
    pub async fn set_status(&self, id: i64, to: Status) -> Result<Order, OrderError> {
        let earlier: Vec<Status> = Status::ALL.into_iter().filter(|s| *s < to).collect();
        if let Some(order) = self.store.set_status(id, to, &earlier).await? {
            return Ok(order);
        }
        // Nothing changed. Find out why, to give the right answer.
        match self.store.find(id).await? {
            None => Err(OrderError::NotFound(id)),
            Some(order) => Err(OrderError::BadStatusChange { from: order.status, to }),
        }
    }
```

`status = ANY($3)` is "the status is one of these", with `$3` a Postgres array of text (`&from as &[&str]` tells sqlx which type to send). Same idea as the last plate: check and change in one guarded statement. Two kitchen staff tapping "ready" and "collected" at once can't tangle an order.

## Step 7: one change in the composition root
<!-- bite: af9f72d8-0191-48c2-9764-7d51305abe39 -->

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok(); // reads .env if there is one; real environment variables win
    tracing_subscriber::fmt().with_env_filter("mama_put=info,tower_http=info").init();

    let database_url = std::env::var("DATABASE_URL").map_err(|_| "set DATABASE_URL to the Postgres connection string")?;
    let pool = db::connect(&database_url).await?;
    sqlx::migrate!().run(&pool).await?;
    info!("database ready");

    // The one place that decides which store, which clock and which key are real.
    let menu = MenuService::new(Arc::new(PgMenuStore::new(pool.clone())));
    let orders = OrderService::new(Arc::new(PgOrderStore::new(pool)), menu.clone(), Clock::system())?;
    let state = AppState { menu, orders, staff_key: StaffKey::from_env()? };
```

(the rest of `main` is as before; `sample_dishes` is gone, replaced by `seed.sql`).

1. **`dotenvy::dotenv().ok()`** loads `.env` if there is one. `.ok()` throws away the error, because "no `.env` file" is normal in production.
2. **`sqlx::migrate!()`** copies every file in `migrations/` **into the program**, at compile time. `.run(&pool)` runs any that haven't run on this database. So the program can never be started against a database that's missing a table it needs. (Lesson 39 moves this to a separate step of the deploy, so two copies starting at once don't race.)
3. **Two lines changed in the wiring**, exactly as lesson 5 promised: `PgMenuStore` and `PgOrderStore` instead of the memory stores. Nothing above the stores knew.

## Step 8: trying the last plate
<!-- bite: b2a30566-d141-4090-bb78-ac8296324855 -->

```bash
psql "postgres://mama:mama-local@localhost:5432/mamaput" -f seed.sql
cargo run
```

Set jollof to exactly 1 portion, then send two orders at the same moment. The `&` runs the first in the background:

```bash
curl -s -X PATCH localhost:8080/menu/1 -H 'x-staff-key: sekret' -H 'content-type: application/json' -d '{"portionsLeft":1}'

curl -s -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":1,"quantity":1}' &
curl -s -X POST localhost:8080/orders -H 'content-type: application/json' -d '{"dishId":1,"quantity":1}'
wait
```

Predict before you run it: how many get a `201`? From a run of this code:

```text
{"data":{"id":1,"dishId":1,"quantity":1,"totalNaira":1500,"status":"pending"}}
{"type":"https://mamaput.example/problems/not-enough-portions","title":"Not enough left","status":422,
 "detail":"there isn't enough of that dish left for your order","code":"not-enough-portions",...}
```

Exactly one. Run it ten times; it's never two.

Then try to delete jollof, which now has an order:

```text
{"type":"https://mamaput.example/problems/dish-has-orders","title":"Dish has orders","status":409,
 "detail":"dish 1 has orders, so it can't be removed; mark it unavailable instead",...}
```

Stop the server, start it again, and `curl localhost:8080/orders/1`. The order is still there. Mama's notebook works.

And the day the notebook doesn't answer: I stopped Postgres with the server running and asked for a dish. Three seconds later (the pool's `acquire_timeout`):

```text
{"type":"https://mamaput.example/problems/internal","title":"Something went wrong","status":500,
 "detail":"Something went wrong on our side. Quote the request ID if you contact us.","code":"internal",
 "requestId":"ee4d8ec4-f6e0-4cc7-961d-4c7881d56340"}
```

and in the log, under the same request ID:

```text
ERROR request{method=GET path="/menu/2" request_id="ee4d8ec4-..."}: mama_put::http::error: unexpected error cause=pool timed out while waiting for an open connection
```

Lesson 7's design, doing its job: the client learns nothing about our database, and we learn everything.

## Step 9: tests against a real database
<!-- bite: b1268b59-6adb-4e0b-9630-347ba31b05e3 -->

The memory stores are gone, so the tests from lesson 5 use Postgres too. sqlx makes that easy. At the bottom of `src/orders/service.rs`:

```rust
    /// Real stores on the test's own database, with two dishes: beans (5 left) and ofada (sold out).
    async fn service_at(pool: &PgPool, hour: i8) -> OrderService {
        let menu = MenuService::new(Arc::new(PgMenuStore::new(pool.clone())));
        let dish = |name: &str, price_naira, available, portions_left| NewDish {
            name: name.to_string(),
            price_naira,
            available,
            special: false,
            portions_left,
        };
        menu.add(dish("Beans and plantain", 1200, true, 5)).await.unwrap(); // id 1
        menu.add(dish("Ofada stew", 3000, false, 10)).await.unwrap(); // id 2
        OrderService::new(Arc::new(PgOrderStore::new(pool.clone())), menu, clock_at(hour)).unwrap()
    }

    #[sqlx::test]
    async fn place_works_out_the_total_and_takes_the_plates(pool: PgPool) {
        let orders = service_at(&pool, 12).await;
        let order = orders.place(NewOrder { dish_id: 1, quantity: 3 }).await.unwrap();
        assert_eq!(order.total_naira, 3600);
        assert_eq!(order.status, Status::Pending);

        let left = sqlx::query_scalar!("SELECT portions_left FROM dishes WHERE id = 1").fetch_one(&pool).await.unwrap();
        assert_eq!(left, 2);
    }
```

**`#[sqlx::test]`** does a lot for one line. For each test, it creates a **brand-new database**, runs every migration on it, hands the test a pool for it, and deletes the database afterwards. Tests can run at the same time without seeing each other's dishes, and each starts from empty tables. It needs `DATABASE_URL` (from `.env`) to know where Postgres is, and permission to create databases.

The test that matters most:

```rust
    #[sqlx::test]
    async fn the_last_plate_goes_to_one_customer(pool: PgPool) {
        let orders = service_at(&pool, 12).await;
        sqlx::query!("UPDATE dishes SET portions_left = 1 WHERE id = 1").execute(&pool).await.unwrap();

        // Ten customers order the last plate at the same moment.
        let attempts = (0..10).map(|_| {
            let orders = orders.clone();
            tokio::spawn(async move { orders.place(NewOrder { dish_id: 1, quantity: 1 }).await })
        });
        let mut won = 0;
        for attempt in attempts.collect::<Vec<_>>() {
            if attempt.await.unwrap().is_ok() {
                won += 1;
            }
        }
        assert_eq!(won, 1);
    }
```

1. **`tokio::spawn`** starts each order as its own task, so all ten really run at once, on different connections from the pool.
2. **`async move`** makes each task own its clone of the service; a spawned task may outlive the code that started it, so it can't borrow.
3. **`.collect::<Vec<_>>()` before the loop**: the `map` is lazy, so without collecting first, each task would be spawned only when the loop reached it, one at a time, and there'd be no race at all.
4. **`attempt.await`** waits for a task and gives `Result<Result<Order, OrderError>, JoinError>`: the outer one fails only if the task panicked.

The error tests use **`matches!`**, because errors can't be compared with `==` any more:

```rust
        assert!(matches!(back, Err(OrderError::BadStatusChange { from: Status::Ready, to: Status::Pending })));
```

```bash
cargo test
```

```text
test orders::service::tests::status_only_moves_forward ... ok
test orders::service::tests::place_works_out_the_total_and_takes_the_plates ... ok
test orders::service::tests::the_last_plate_goes_to_one_customer ... ok
test orders::service::tests::place_refuses ... ok
test result: ok. 7 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 1.71s
```

Seven with lesson 6's three. Under two seconds, with four fresh databases.

## Do you need an ORM?
<!-- bite: 64ef9ac9-a563-46a4-9e6b-d39ec25b4a89 -->

Rust has ORMs: **Diesel** (types generated from your schema, queries written in Rust) and **SeaORM** (async, closer to the ORMs of other languages). They're good. Many Rust teams still choose sqlx, for the same reason as Go teams choose plain SQL: the queries that matter most (the guarded `UPDATE`, a careful `JOIN`, a query that must use an index) are the ones an ORM makes harder to see and to write. sqlx gives you most of an ORM's safety, the types checked against the real schema, without hiding the SQL.

## The Rust in this lesson
<!-- bite: d059abd9-3d3c-4135-a74f-a298e3b4af24 -->

1. **`sqlx::query_as!(Type, "SQL", args...)`, `query!`, `query_scalar!`**: queries checked against the database while compiling, building a struct, nothing, or one value.
2. **`.fetch_all`, `.fetch_optional`, `.fetch_one`, `.execute`**: every row, zero or one, exactly one, or just "how many changed".
3. **`#[async_trait]`**: async methods in a trait that can still be `dyn`, by boxing each future.
4. **`Pin<Box<dyn Future + Send>>`**: what `async_trait` returns: a future on the heap, which can't be moved once it's started.
5. **`PgPool`** and **`PgPoolOptions`**: a cheap-to-clone pool, sized and with a timeout.
6. **`#[error(transparent)]` and `#[from]`** in thiserror: wrap another error, print it as it is, and convert into it with `?`.
7. **`matches!(value, pattern if condition)`**: `true` if the value fits.
8. **Transactions, `pool.begin()`, `&mut *tx`, `tx.commit()`**, and **rollback on `Drop`**.
9. **let-else, `let Some(x) = y else { return ...; };`**: name what's inside, or leave.
10. **`#[derive(sqlx::Type)]` with `#[sqlx(type_name = "text", rename_all = "lowercase")]`**: a Rust enum stored as text.
11. **`AS "status: Status"`**: tell a query macro the Rust type of a column.
12. **Raw strings, `r#"..."#`**: text that can hold `"` without escaping.
13. **`pub const ALL: [Status; 3]`**: a constant array on a type.
14. **`tokio::spawn` and `async move`**: run a task on its own; it owns what it uses.
15. **`.collect::<Vec<_>>()`**: run a lazy iterator to the end, now.
16. **`sqlx::migrate!()`**: embed the migrations in the program.
17. **`#[sqlx::test]`**: a fresh, migrated database per test.

## Your project so far
<!-- bite: 98e810c5-aaa0-40bd-bce7-221157a401d1 -->

```text
mama-put/
├── .env                   ← DATABASE_URL, STAFF_KEY (not in git)
├── .gitignore             ← /target, .env
├── Cargo.toml             ← + sqlx (runtime-tokio, postgres, macros, migrate), async-trait, dotenvy
├── migrations/
│   ├── 0001_create_dishes.sql
│   └── 0002_create_orders.sql
├── seed.sql               ← Mama's three starting dishes, run by hand
└── src/
    ├── main.rs            ← .env, pool, migrate!, Pg stores into the services
    ├── lib.rs             ← + pub mod db
    ├── db.rs              ← connect (10 connections, 3 s timeout), StoreError
    ├── clock.rs
    ├── http/ ...
    ├── menu/
    │   ├── model.rs       ← i64 ids, portions_left
    │   ├── store.rs       ← async MenuStore; PgMenuStore with checked queries
    │   ├── service.rs     ← async; HasOrders and Store errors
    │   └── handlers.rs    ← await; Store → ApiError::internal, HasOrders → 409
    └── orders/
        ├── model.rs       ← Status: sqlx::Type, ALL, as_str
        ├── store.rs       ← PgOrderStore: the last plate in a transaction; status change in SQL
        ├── service.rs     ← async; NotEnoughPortions; 4 database tests
        └── handlers.rs    ← await; NotEnoughPortions → 422
```

## Common mistakes
<!-- bite: b9535a0c-3e67-45e2-af0b-fc98cfaeeecb -->

1. **Building before migrating.** sqlx can't check queries against tables that don't exist. `sqlx migrate run` first.
2. **Editing a migration that has run.** sqlx refuses to start. Write a new one.
3. **Pasting values into SQL with `format!`.** SQL injection. Bind parameters, always.
4. **Look, then take.** Two requests both see one plate. Look and take in one guarded statement.
5. **A transaction without `commit`.** It rolls back when `tx` is dropped, silently. Every path that should keep its changes must reach `tx.commit()`.
6. **A pool without a timeout, or one sized "big to be safe".** Requests wait forever, or the database runs out of connections for everyone.
7. **Sending database errors to the client.** `ApiError::internal`; the details go to the log.
8. **Seed data in a migration.** Production gets Mama's sample jollof. Keep it in a separate file.
9. **Forgetting `#[async_trait]` on the `impl`.** It must be on the trait *and* every implementation.

## Check your understanding
<!-- bite: 69d4503b-e269-4c41-8cb5-41f43bd221ab -->

1. What does `query_as!` check at compile time, and what does it need to be able to?
2. Why does `MenuStore` need `#[async_trait]` when Rust allows `async fn` in traits?
3. How does `COALESCE($2, name)` let one `UPDATE` serve every kind of `PATCH`?
4. Ada and Bayo order the last plate at once. Walk through what Postgres does with the two guarded `UPDATE`s.
5. In `place_taking_portions`, what happens to the transaction if the `INSERT` fails, and why didn't we write a rollback?
6. Why is "a dish with orders can't be deleted" a `MenuError` variant, when it starts as a database error?
7. What does `#[sqlx::test]` give each test, and why does it matter for the last-plate test?
8. In the last-plate test, why collect the spawned tasks into a `Vec` before awaiting them?

<details>
<summary>Answers, after your attempt</summary>

1. That the SQL is valid against the real schema (tables and columns exist), that the columns' types match the struct's fields, and that the arguments' types match the parameters. It needs a running database at `DATABASE_URL`, with the migrations applied, or a `.sqlx/` folder from `cargo sqlx prepare`.
2. Because a plain `async fn` in a trait returns a different hidden future type for each implementation, which makes the trait not dyn compatible, and `MenuService` holds `Arc<dyn MenuStore>`. `#[async_trait]` makes every method return the same boxed future type.
3. Each changeable field is sent as an `Option`; `None` arrives as `NULL`, and `COALESCE` picks the first non-`NULL` value, so the column keeps its old value unless a new one was sent.
4. Both try to update the jollof row. Postgres lets one go first and makes the other wait for its row lock. The first finds `portions_left >= 1`, sets it to 0, and returns the price. When the second gets the row, Postgres checks the `WHERE` again, finds 0, and updates nothing, so no row is returned and Bayo gets `NotEnoughPortions`.
5. The `?` returns the error from the function, `tx` goes out of scope, and its `Drop` rolls the transaction back, including the plate taken by the `UPDATE`. Rust's ownership does the rollback, so there's nothing to forget.
6. Because to the customer it's a rule with a clear answer ("mark it unavailable instead"), not a failure. The service recognises the foreign-key violation and turns it into `HasOrders`, a 409, instead of passing up a store error that would become a 500.
7. A new, empty database with every migration applied, and a pool to it, deleted afterwards. The last-plate test changes portions and races ten orders; with its own database, no other test's dishes or orders can change the result.
8. Because `map` is lazy. Without collecting, each task would be spawned only when the loop got to it, and the loop awaits each one before reaching the next, so the orders would run one after another and never race.

</details>

## Practice
<!-- bite: 46d60e5c-80a8-4c0e-98e2-7c7807d8d720 -->

1. Add a migration, `0003_dish_description.sql`, adding an optional `description text` column. Run it, then try to build: which queries does the compiler now want you to change, and why only those?
2. Make `GET /menu?available=true` filter in SQL instead of in Rust. (Lesson 9 does this properly; try it yourself first.)
3. Write a `#[sqlx::test]` for `MenuService::remove`: a dish with an order gives `HasOrders`, one without is removed.
4. Set `max_connections(1)` in `db::connect`, start the server, and fire twenty orders at once with a `for` loop of `curl ... &`. They all still get an answer. Why, and what would that feel like for customers at lunchtime? (The tests don't use `db::connect`; `#[sqlx::test]` makes its own pool.)
5. Make `PATCH /menu/{id}` with `{"portionsLeft": -1}` get past the door (remove the `validate` rule for a moment) and see what Postgres's `CHECK` does. What does the client get, and is that the right answer?

**Done when** the server runs against Postgres in a container, migrations run at start-up, every query is checked by the compiler, data survives a restart, two orders for the last plate never both succeed, a dish with orders can't be deleted and the client is told why, a database outage is a 500 with the cause only in the log, and `cargo test` passes against fresh databases.

## Before moving on
<!-- bite: 1bcd987c-d1af-4fdd-96f4-03a8b91ae83e -->

Mama Put remembers now. The menu and orders live in PostgreSQL, the compiler checks every query against the real tables, the last plate goes to exactly one customer however many copies of the app are running, and the tests run against real databases of their own.

But `GET /menu` still sends every dish, in one go, filtered in Rust after loading them all. With three dishes, that's fine. With the kitchen's order history, it isn't. Next lesson: pagination, filtering, searching, sorting and field selection, with SQL built safely for each request, and cursors for the kitchen's list of orders.

## Related
<!-- bite: a386159d-8d89-47c3-8872-86f1954dd1aa -->

- [[backend/frameworks/axum/09-listing|Next: Pagination, Filtering, Searching, Sorting and Field Selection]]
- [[backend/frameworks/net-http/08-data-with-postgres|The same lesson in net/http]] — pgx, a migration runner by hand, and `BeginFunc`
- [[databases/index|Databases]] — SQL, indexes and transactions from zero
- [[backend/frameworks/axum/05-state-and-dependency-injection|State and Dependency Injection]] — the store traits this lesson fills in

## About this lesson
<!-- bite: 6b52151f-22ff-4b68-959e-6233fddb7259 -->

**Level:** Intermediate → Advanced. Lesson 8 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, sqlx 0.9 and PostgreSQL 18. Covers running Postgres in a container, `DATABASE_URL` in `.env` kept out of git, migrations with `sqlx migrate run` and `sqlx::migrate!()`, seed data kept out of migrations, a sized `PgPool` with an acquire timeout, compile-time checked queries with `query_as!` and what they need to build, `COALESCE` for `PATCH`, bind parameters and SQL injection, async store traits with `#[async_trait]` and why plain `async fn` isn't dyn compatible, a `StoreError` and foreign-key violations as a rule, the last plate with a guarded `UPDATE` inside a transaction that rolls back on `Drop`, status changes guarded in SQL with `ANY`, enums stored as text with `sqlx::Type`, store errors as `ApiError::internal`, and `#[sqlx::test]` with a fresh database per test, including a ten-way race.
