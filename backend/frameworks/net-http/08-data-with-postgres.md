---
id: 8590a402-0e39-429f-a2c1-d9d0a256cbb3
---

# Data with PostgreSQL

**A database keeps your app's data safe on disk, outside the program, so it survives restarts and crashes and can be shared by every copy of the app at once.** PostgreSQL ("Postgres") is the one we use. In Go you talk to it through a **driver**, here `pgx`, using a **pool** of open connections, plain SQL with placeholders, and transactions for anything that must happen all together or not at all.

## Before you start
<!-- bite: f897a4eb-fc0d-4af9-bf0e-68068c1563f4 -->

You should have:

1. Finished [[backend/frameworks/net-http/07-errors|lesson 7]], so every handler returns an error and every answer is `{ data }` or a problem.
2. Docker or Podman installed, so you can run Postgres without installing it on your computer.
3. Written a `SELECT`, an `INSERT` and an `UPDATE` before. If you haven't, [[databases/index|Databases]] starts from zero.

After this lesson you will be able to:

1. Run Postgres in a container and connect to it from Go with a properly sized pool.
2. Keep the connection string out of the code, and load it for local runs.
3. Write migrations as SQL files, embed them in the program, and run them once each.
4. Query with placeholders, and explain exactly why pasting values into SQL is dangerous.
5. Pass the request's context to every query, and say what that buys you.
6. Use a transaction and a guarded `UPDATE` so the last plate goes to one customer, however many order at once.

## Where we stopped
<!-- bite: 696f6b11-5ea7-45b0-9144-5d13131e1e25 -->

Everything lives in memory. Stop the server and Mama's moi moi is gone, and so is every order. Run two copies behind a load balancer and each has its own menu: the kitchen marks jollof finished on one, and customers on the other keep ordering it.

There's a quieter problem too. Mama doesn't have endless jollof. She cooks 40 plates in the morning, and when they're gone, they're gone. The menu needs a `portionsLeft` count, and when two customers order the very last plate at the same moment, only one of them can get it.

## The kid version
<!-- bite: 36e36d3f-c033-40db-8283-505e139c27aa -->

Up to now, Mama has kept the day's orders in her head. When she goes home, they're gone. If her sister helps at a second table, the sister has no idea what Mama promised.

A database is the big notebook on the counter. Everyone writes in the same book, it's still there tomorrow, and when two people reach for the last plate at the same time, the notebook decides who wrote first.

**Where the picture stops working.** A real notebook is in one place. Your database is on another computer (or in a container), and every trip to it takes time and can fail. So your code keeps a few lines to it always open (the pool), and has to be ready for the day the notebook doesn't answer.

## Terms used in this lesson
<!-- bite: 50b2a332-d231-4528-bfe6-0a166620c9c1 -->

1. **Driver**: This is the package that knows how to talk to one kind of database over the network. For Postgres in Go, the best one is `pgx`.
2. **Connection string**: This is one line saying where the database is and how to log in: `postgres://user:password@host:5432/dbname`. It holds a password, so it's a secret.
3. **Connection pool**: This is a set of open connections to the database that requests borrow and give back. Opening a connection is slow, so a pool opens a few and reuses them.
4. **Migration**: This is a numbered file of SQL that changes the database's structure, like creating a table. Migrations run in order, once each, and are never edited after they've run anywhere.
5. **Placeholder**: This is a marker in SQL, like `$1`, where a value goes. The value is sent separately from the SQL, so it can never be read as SQL.
6. **SQL injection**: This is an attack where someone sends text that becomes part of your SQL, so they can read or change data they shouldn't. Placeholders stop it completely.
7. **Transaction**: This is a group of SQL statements that either all happen or none do. It starts with `BEGIN` and ends with `COMMIT` (keep everything) or `ROLLBACK` (undo everything).
8. **Race condition**: This is a bug where the result depends on which of two things happens first, like two requests both seeing "1 plate left".

## What to install
<!-- bite: 4054a6c3-e340-4d03-8d26-db91048e79e9 -->

**Postgres**, in a container:

```bash
docker run --name mama-put-db -d \
  -e POSTGRES_PASSWORD=mamaput -e POSTGRES_DB=mama_put \
  -p 5432:5432 postgres:17
```

(With Podman, write `podman` instead of `docker`.) That starts Postgres in the background with a database called `mama_put` on port 5432. Lesson 28 starts the whole system with one Docker Compose command; for now one container is enough. Next time, start it again with `docker start mama-put-db`.

**The driver**, from the project folder:

```bash
go get github.com/jackc/pgx/v5
```

That one module includes the pool (`pgxpool`) and everything else we use. `go.mod` and `go.sum` update themselves.

**`make`**, to run the project's commands with the settings loaded. Fedora usually has it; if `make --version` fails, `sudo dnf install make`.

## Step 1: keep the password out of the code
<!-- bite: d7423841-0db5-485e-93f7-67b83f736fbd -->

The app needs to know where the database is, and that string has a password in it. It must never be written in the code or committed to git.

Create `.env` in the project root:

```text
DATABASE_URL=postgres://postgres:mamaput@localhost:5432/mama_put
STAFF_KEY=mama-secret
```

Add `.env` to `.gitignore`. Then create `.env.example`, which **is** committed, so teammates know what to fill in:

```text
DATABASE_URL=postgres://user:password@localhost:5432/mama_put
STAFF_KEY=change-me
```

Go doesn't read `.env` files by itself, and the app shouldn't: in production, settings come from the real environment (lesson 28). For running on your laptop, a **Makefile** loads the file and runs the commands. Create `Makefile` in the project root:

```makefile
-include .env
export

run:
	go run -race ./cmd/api

migrate:
	go run ./cmd/migrate

seed:
	go run ./cmd/migrate -seed

test:
	go test -race ./...

.PHONY: run migrate seed test
```

The lines under each name **must start with a tab**, not spaces. `make` is strict about that, and the error (`missing separator`) doesn't say so clearly.

What it does: `-include .env` reads the settings from `.env` (the `-` means "don't fail if it's missing"), and `export` passes all of them to every command. `make run` now starts the API with `DATABASE_URL` and `STAFF_KEY` set. `.PHONY` tells `make` these are command names, not files to build.

## Step 2: the tables, as migrations
<!-- bite: 1fd0e739-d24a-4882-afbe-dd5818286c7f -->

You could create tables by typing SQL into Postgres by hand. Then your laptop, your teammate's laptop and production would each end up slightly different, and nobody would know how. Migrations fix that: every change to the database's structure is a numbered SQL file in git, and every database runs the same files in the same order.

Make a folder `migrations/` in the project root. `migrations/001_create_dishes.sql`:

```sql
CREATE TABLE dishes (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name          text    NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
  price_naira   integer NOT NULL CHECK (price_naira > 0),
  available     boolean NOT NULL DEFAULT true,
  special       boolean NOT NULL DEFAULT false,
  portions_left integer NOT NULL DEFAULT 0 CHECK (portions_left >= 0),
  created_at    timestamptz NOT NULL DEFAULT now()
);
```

`migrations/002_create_orders.sql`:

```sql
CREATE TABLE orders (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  dish_id     bigint  NOT NULL REFERENCES dishes (id),
  quantity    integer NOT NULL CHECK (quantity BETWEEN 1 AND 20),
  total_naira integer NOT NULL CHECK (total_naira > 0),
  status      text    NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending', 'ready', 'collected')),
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX orders_dish_id_idx ON orders (dish_id);
```

A few choices worth seeing:

1. **`GENERATED ALWAYS AS IDENTITY`** makes Postgres choose each new `id`, counting up. No more `nextID` and mutex.
2. **`CHECK` constraints** repeat Mama's rules in the database itself: a price above 0, no negative portions, only three statuses. If a bug in our Go code ever tries to break them, Postgres refuses. The database is the last line of defence, and the only one that holds for every program that ever touches it.
3. **`REFERENCES dishes (id)`** is a **foreign key**: an order can't point at a dish that doesn't exist, and a dish with orders can't be deleted. (Lesson 9's practice deals with what "removing" a dish should then mean.)
4. **`timestamptz`** stores a moment in time, with the time zone handled properly. Always use it, not `timestamp`.
5. **The index on `dish_id`** makes "orders for this dish" fast. Postgres doesn't create indexes for foreign keys by itself.

Now the Go part. We want the migrations **inside** the program, so the program can never be run against the wrong files. Go can do that with `embed`. Create `migrations/migrations.go`, in the same folder as the SQL files:

```go
// Package migrations holds the database migrations, embedded in the program.
package migrations

import "embed"

//go:embed *.sql
var FS embed.FS
```

`//go:embed *.sql` is a **directive**: an instruction to the Go compiler, written as a comment with no space after `//`. It tells the compiler to copy every `.sql` file in this folder into the program, as the variable `FS`. When you build, the SQL is inside the binary; there's no folder to forget to copy onto the server.

## Step 3: a small migration runner
<!-- bite: 39d4d0be-dd54-4e2f-bffa-69584b1f18b0 -->

The runner's job: remember which files have run, and run the rest, in order, each in its own transaction. Make `internal/db/migrate.go`:

```go
package db

import (
	"context"
	"fmt"
	"io/fs"
	"strings"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

const migrateLockID = 7_212_026 // any fixed number; it names the lock

func Migrate(ctx context.Context, pool *pgxpool.Pool, files fs.FS) error {
	conn, err := pool.Acquire(ctx)
	if err != nil {
		return fmt.Errorf("get a connection: %w", err)
	}
	defer conn.Release()

	// Only one migrator at a time, even if two copies of the app start together.
	if _, err := conn.Exec(ctx, "SELECT pg_advisory_lock($1)", migrateLockID); err != nil {
		return fmt.Errorf("take the migration lock: %w", err)
	}
	defer conn.Exec(context.Background(), "SELECT pg_advisory_unlock($1)", migrateLockID)

	if _, err := conn.Exec(ctx, `
		CREATE TABLE IF NOT EXISTS schema_migrations (
			name       text PRIMARY KEY,
			applied_at timestamptz NOT NULL DEFAULT now()
		)`); err != nil {
		return fmt.Errorf("create schema_migrations: %w", err)
	}

	entries, err := fs.ReadDir(files, ".")
	if err != nil {
		return err
	}

	for _, entry := range entries {
		name := entry.Name()
		if !strings.HasSuffix(name, ".sql") {
			continue
		}

		var done bool
		err := conn.QueryRow(ctx,
			"SELECT EXISTS (SELECT 1 FROM schema_migrations WHERE name = $1)", name).Scan(&done)
		if err != nil {
			return err
		}
		if done {
			continue
		}

		sql, err := fs.ReadFile(files, name)
		if err != nil {
			return err
		}

		err = pgx.BeginFunc(ctx, conn, func(tx pgx.Tx) error {
			if _, err := tx.Exec(ctx, string(sql)); err != nil {
				return err
			}
			_, err := tx.Exec(ctx, "INSERT INTO schema_migrations (name) VALUES ($1)", name)
			return err
		})
		if err != nil {
			return fmt.Errorf("migration %s: %w", name, err)
		}
		fmt.Println("applied", name)
	}
	return nil
}
```

Read it top to bottom:

1. **It borrows one connection** from the pool and keeps it for the whole run, because the lock belongs to a connection.
2. **It takes an advisory lock.** That's a lock Postgres keeps for you, named by a number. If two copies of the app run migrations at the same moment (it happens during deploys), the second waits for the first to finish, instead of both trying to create the same table.
3. **It makes `schema_migrations`** if it isn't there: a table with one row per migration that has run.
4. **It lists the files.** `fs.ReadDir` returns them sorted by name, which is why the files start with `001_`, `002_`. Use three digits, so `010` sorts after `009`.
5. **For each file not yet run**, it runs the SQL and records the name, **in one transaction**. If the SQL fails halfway, nothing is recorded and nothing is changed. Fix the file, run again.

The function takes the files as an `fs.FS`, an interface, not the embedded `migrations.FS` directly. A test can pass in a folder of test migrations instead. Lesson 5's habit again.

Now a tiny program to run it, `cmd/migrate/main.go`:

```go
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"

	"mamaput/internal/db"
	"mamaput/migrations"
)

func main() {
	seed := flag.Bool("seed", false, "also add Mama's starting menu, if the menu is empty")
	flag.Parse()

	if err := run(context.Background(), *seed); err != nil {
		fmt.Fprintln(os.Stderr, "migrate:", err)
		os.Exit(1)
	}
}

func run(ctx context.Context, seed bool) error {
	url := os.Getenv("DATABASE_URL")
	if url == "" {
		return errors.New("DATABASE_URL is not set")
	}
	pool, err := db.Open(ctx, url)
	if err != nil {
		return err
	}
	defer pool.Close()

	if err := db.Migrate(ctx, pool, migrations.FS); err != nil {
		return err
	}
	if seed {
		return db.Seed(ctx, pool)
	}
	return nil
}
```

`flag.Bool` declares a command-line option, `-seed`, and `flag.Parse()` reads the ones given. `make seed` runs `go run ./cmd/migrate -seed`.

The seed, at the bottom of `internal/db/migrate.go`:

```go
// Seed adds Mama's starting menu, but only to an empty menu.
func Seed(ctx context.Context, pool *pgxpool.Pool) error {
	_, err := pool.Exec(ctx, `
		INSERT INTO dishes (name, price_naira, available, special, portions_left)
		SELECT * FROM (VALUES
			('Jollof rice',           1500, true,  true,  40),
			('Beans and plantain',    1200, true,  false, 25),
			('Egusi and pounded yam', 2500, false, false, 0)
		) AS starting_menu
		WHERE NOT EXISTS (SELECT 1 FROM dishes)`)
	return err
}
```

The `WHERE NOT EXISTS` makes it safe to run twice: the second time, the menu isn't empty, so nothing is added. Something you can run again without harm is called **idempotent**, a word that gets a whole lesson in lesson 15.

## Step 4: the pool
<!-- bite: cca446e5-b64d-4a39-83e9-b710c0e9d4a3 -->

`cmd/migrate` called `db.Open`. Here it is, `internal/db/db.go`:

```go
// Package db opens the database and runs migrations.
package db

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

func Open(ctx context.Context, url string) (*pgxpool.Pool, error) {
	cfg, err := pgxpool.ParseConfig(url)
	if err != nil {
		return nil, fmt.Errorf("read DATABASE_URL: %w", err)
	}
	cfg.MaxConns = 10
	cfg.MinConns = 2
	cfg.MaxConnLifetime = time.Hour
	cfg.MaxConnIdleTime = 15 * time.Minute

	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		return nil, fmt.Errorf("create the pool: %w", err)
	}

	pingCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	if err := pool.Ping(pingCtx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("reach the database: %w", err)
	}
	return pool, nil
}
```

The pool settings decide whether you survive a busy lunchtime, so each one deserves a sentence:

1. **`MaxConns = 10`**: at most 10 connections open at once. When all 10 are busy, the next query **waits** for one to come free. That's on purpose. Postgres can only handle so many connections (100 by default, shared by everything), and each costs it memory. If you run 3 copies of the app with 10 each, that's 30. Ten busy connections can serve a surprising number of requests, because most queries take a millisecond or two.
2. **`MinConns = 2`**: keep 2 open even when quiet, so the first request after a lull doesn't wait for a new connection.
3. **`MaxConnLifetime = time.Hour`**: replace each connection after an hour. Connections that live forever can collect problems, and when the database moves (a failover), old connections keep pointing at the old place.
4. **`MaxConnIdleTime`**: close connections nobody has used for 15 minutes.

The **ping** at the end checks the database actually answers, with a 5-second limit, **at start-up**. Without it, a wrong password would only show up when the first customer opens the menu. Like the staff key in lesson 3: fail loudly at start, not quietly later.

Run the migrations and the seed now:

```bash
make migrate
# applied 001_create_dishes.sql
# applied 002_create_orders.sql

make migrate
# (nothing: both have already run)

make seed
```

## Step 5: every query gets a context
<!-- bite: 997bacd7-e26e-444a-be5c-1d814e34e703 -->

Before writing the store, one change to every store method, service method and interface: they all take a `context.Context` first, and they all return an `error`.

Why the context? Look at what happens without it. A customer opens the menu on a bad connection and gives up after 3 seconds. Your handler is still waiting on the database, and will be for as long as the query takes, holding a connection the next customer needs. With the context, the moment the client goes away, `r.Context()` is **cancelled**, pgx notices, tells Postgres to stop the query, and the connection goes back to the pool. Lesson 14 adds a deadline to every request, and the same context carries it into every query, with no extra code.

Why the error? Because a database can fail in ways memory couldn't: the network drops, Postgres restarts, a query times out. Every call to it can fail, so every call returns an error.

The rule in Go is simple: **a function that does I/O (network, disk, database) takes a context as its first argument, called `ctx`.** Never store a context in a struct; pass it down.

Here's the new menu `Store` interface in `internal/menu/service.go`:

```go
type ListFilter struct {
	OnlyAvailable bool
	OnlySpecials  bool
}

type Store interface {
	List(ctx context.Context, f ListFilter) ([]Dish, error)
	Find(ctx context.Context, id int64) (Dish, error)
	Add(ctx context.Context, in NewDish) (Dish, error)
	Update(ctx context.Context, id int64, ch DishChanges) (Dish, error)
	Remove(ctx context.Context, id int64) error
}
```

Three other things changed:

1. **IDs are `int64` now.** That's what `bigint` is. The Postgres store returns real numbers, and `httpx.PathID` returns the parsed `int64` instead of the string (change its return type, and `return n, nil`).
2. **`Find` returns an error, not a bool.** "Not found" is `ErrDishNotFound`; anything else is a real failure. Two outcomes no longer fit in a bool.
3. **`Update` takes the changes, not a function.** In lesson 2, the store ran your function while holding its lock. A database can't run Go code; the change has to be said in SQL.

And the types in `internal/menu/menu.go`:

```go
type Dish struct {
	ID           int64     `json:"id,string"`
	Name         string    `json:"name"`
	PriceNaira   int       `json:"priceNaira"`
	Available    bool      `json:"available"`
	Special      bool      `json:"special"`
	PortionsLeft int       `json:"portionsLeft"`
	CreatedAt    time.Time `json:"createdAt"`
}

type NewDish struct {
	Name         string `json:"name"         validate:"required,max=80"`
	PriceNaira   int    `json:"priceNaira"   validate:"required,gt=0,lte=1000000"`
	Special      bool   `json:"special"`
	PortionsLeft int    `json:"portionsLeft" validate:"gte=0,lte=1000"`
}

type DishChanges struct {
	Name         *string `json:"name"         validate:"omitempty,min=1,max=80"`
	PriceNaira   *int    `json:"priceNaira"   validate:"omitempty,gt=0,lte=1000000"`
	Available    *bool   `json:"available"`
	Special      *bool   `json:"special"`
	PortionsLeft *int    `json:"portionsLeft" validate:"omitempty,gte=0,lte=1000"`
}
```

Look at `json:"id,string"`. The `,string` option tells `encoding/json` to write this number **as a JSON string**: `"id":"2"`, exactly as before. Clients built against lesson 7 see no change. It's also kind to JavaScript, which can't hold every `int64` exactly as a number.

## Step 6: the menu store, for real
<!-- bite: 509eef33-0c64-4162-b8e9-71b8f688047f -->

`internal/menu/postgres.go`:

```go
package menu

import (
	"context"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type PostgresStore struct {
	pool *pgxpool.Pool
}

func NewPostgresStore(pool *pgxpool.Pool) *PostgresStore {
	return &PostgresStore{pool: pool}
}

const dishColumns = "id, name, price_naira, available, special, portions_left, created_at"

func scanDish(row pgx.Row) (Dish, error) {
	var d Dish
	err := row.Scan(&d.ID, &d.Name, &d.PriceNaira, &d.Available, &d.Special, &d.PortionsLeft, &d.CreatedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		return Dish{}, ErrDishNotFound
	}
	return d, err
}

func (s *PostgresStore) List(ctx context.Context, f ListFilter) ([]Dish, error) {
	rows, err := s.pool.Query(ctx, `
		SELECT `+dishColumns+` FROM dishes
		 WHERE ($1 = false OR available)
		   AND ($2 = false OR special)
		 ORDER BY id`,
		f.OnlyAvailable, f.OnlySpecials)
	if err != nil {
		return nil, fmt.Errorf("list dishes: %w", err)
	}
	defer rows.Close()

	dishes := []Dish{}
	for rows.Next() {
		d, err := scanDish(rows)
		if err != nil {
			return nil, fmt.Errorf("read dish: %w", err)
		}
		dishes = append(dishes, d)
	}
	return dishes, rows.Err()
}

func (s *PostgresStore) Find(ctx context.Context, id int64) (Dish, error) {
	return scanDish(s.pool.QueryRow(ctx,
		"SELECT "+dishColumns+" FROM dishes WHERE id = $1", id))
}

func (s *PostgresStore) Add(ctx context.Context, in NewDish) (Dish, error) {
	return scanDish(s.pool.QueryRow(ctx, `
		INSERT INTO dishes (name, price_naira, special, portions_left)
		VALUES ($1, $2, $3, $4)
		RETURNING `+dishColumns,
		in.Name, in.PriceNaira, in.Special, in.PortionsLeft))
}

func (s *PostgresStore) Update(ctx context.Context, id int64, ch DishChanges) (Dish, error) {
	return scanDish(s.pool.QueryRow(ctx, `
		UPDATE dishes SET
		       name          = COALESCE($2, name),
		       price_naira   = COALESCE($3, price_naira),
		       available     = COALESCE($4, available),
		       special       = COALESCE($5, special),
		       portions_left = COALESCE($6, portions_left)
		 WHERE id = $1
		RETURNING `+dishColumns,
		id, ch.Name, ch.PriceNaira, ch.Available, ch.Special, ch.PortionsLeft))
}

func (s *PostgresStore) Remove(ctx context.Context, id int64) error {
	tag, err := s.pool.Exec(ctx, "DELETE FROM dishes WHERE id = $1", id)
	if err != nil {
		return fmt.Errorf("remove dish: %w", err)
	}
	if tag.RowsAffected() == 0 {
		return ErrDishNotFound
	}
	return nil
}
```

The parts to understand:

**`Query` and `rows`.** `Query` sends the SQL and gives back `rows`, which you walk with `rows.Next()`, reading each with `Scan`. Two lines people forget: `defer rows.Close()`, which gives the connection back to the pool even if you stop early, and `rows.Err()` at the end, which reports an error that happened partway through reading. `dishes := []Dish{}` starts with an empty slice, not `nil`, so an empty menu is sent as `[]`, not `null`.

**`QueryRow` and `Scan`.** For one row. `Scan` copies each column, in order, into the variable you give it the address of. If there was no row, `Scan` returns `pgx.ErrNoRows`, and `scanDish` turns that into our own `ErrDishNotFound`, so nothing above the store ever sees a pgx error it has to understand.

**`RETURNING`.** Postgres sends back the row it just inserted or changed, with the `id` and `created_at` it filled in. One trip instead of two.

**The PATCH trick, `COALESCE`.** `COALESCE($2, name)` means "use `$2`, unless it's NULL, then keep `name`". pgx sends a nil pointer as NULL. So a field the client didn't send stays as it was, and one they did send is changed, in one statement. The pointer fields from lesson 2 pay off again.

**Filtering in SQL.** `($1 = false OR available)` means "if the filter is off, every row passes; if it's on, only available ones". The database does the filtering, so we never load dishes only to throw them away. Lesson 9 builds a lot more on this.

The menu service passes the context and filter through. For example:

```go
func (s *Service) List(ctx context.Context, onlyAvailable bool) ([]Dish, error) {
	return s.store.List(ctx, ListFilter{OnlyAvailable: onlyAvailable})
}

func (s *Service) Specials(ctx context.Context) ([]Dish, error) {
	return s.store.List(ctx, ListFilter{OnlySpecials: true, OnlyAvailable: true})
}
```

Update the rest the same way, and the handlers to call `h.svc.Get(r.Context(), id)` and so on. Update `MemoryStore` to the new interface too, so the menu service tests still have a fast store (it's in the practice).

## Why placeholders matter: SQL injection
<!-- bite: 3fb8181b-bcb8-4c27-bb2b-0275d4091875 -->

Every value above went in as `$1`, `$2`, never pasted into the SQL text. Here's why that's not a style rule.

Imagine you wrote the dish lookup like this:

```go
// NEVER DO THIS
sql := fmt.Sprintf("SELECT %s FROM dishes WHERE name = '%s'", dishColumns, name)
```

It works for `Jollof rice`. Now someone searches for this name:

```text
x' OR '1'='1
```

The SQL becomes `WHERE name = 'x' OR '1'='1'`, which is true for every row. They've just changed your query. With a bit more effort, the same trick reads other tables (`' UNION SELECT email, password_hash ... FROM customers --`), and on some setups, deletes them.

With a placeholder, the SQL text and the value travel **separately**. Postgres receives `WHERE name = $1` and, apart from it, the value `x' OR '1'='1`. It looks for a dish literally named that, finds none, and that's all. There is no way for a value to become SQL.

The rule: **values always go in placeholders.** The only things you may ever join into SQL text are things **you** wrote in the code, like `dishColumns`. Lesson 9 needs a column name chosen by the client (`?sort=price`), and shows the safe way: an allow-list that maps what the client sent to text you wrote.

## Step 7: the last plate, with a transaction
<!-- bite: 33f49f8d-b79b-43ae-aba3-0d2d8c0f63b3 -->

Now the hard problem. Mama has 1 plate of jollof left. Ada and Bayo order at the same moment.

The obvious code looks like this:

```go
dish, _ := menu.Get(ctx, id)            // Ada sees 1 left. Bayo sees 1 left.
if dish.PortionsLeft < quantity { ... } // both pass
menu.Change(ctx, id, DishChanges{PortionsLeft: ptr(dish.PortionsLeft - quantity)}) // both set 0
orders.Add(ctx, ...)                     // two orders, one plate
```

Between "look" and "take", the other request slipped in. This is a **race condition**, and it's the kind of bug that never shows up when you test alone, then shows up every Friday at lunch. The mutex from lesson 2 can't help now: two copies of the app have two mutexes, and the plates are in the database.

The fix has two parts.

**Part 1: look and take in one statement.**

```sql
UPDATE dishes
   SET portions_left = portions_left - $2
 WHERE id = $1 AND available AND portions_left >= $2
RETURNING price_naira
```

Postgres locks the row while it updates it. If Ada's update goes first, Bayo's **waits**; then Postgres checks `portions_left >= 1` again, finds 0, and updates **nothing**. No row comes back, so we know he was too late. The check and the change are one step that nobody can get between.

**Part 2: take the plate and write the order together.** If we take the portion and then the order insert fails (a bug, the server crashes in between), Mama's pot shows one plate fewer and nobody has an order. A transaction makes both happen, or neither.

pgx has a helper that does the whole dance: `pgx.BeginFunc` starts a transaction, runs your function, **commits** if it returns `nil`, and **rolls back** if it returns an error or panics. You can't forget the rollback, and the connection always goes back to the pool.

First the orders types, in `internal/orders/orders.go`. `Order` gets `ID int64` with `json:"id,string"`, `DishID int64` with `json:"dishId,string"`, and `CreatedAt time.Time`. `NewOrder.DishID` becomes `int64` with `` `json:"dishId,string" validate:"required,gt=0"` ``, so clients still send `"dishId": "1"`. And a new error:

```go
ErrNotEnoughPortions = apperr.New(apperr.RuleBroken, "not-enough-portions", "There isn't enough of that dish left for your order.")
```

The orders `Store` interface in `service.go` becomes:

```go
type Store interface {
	PlaceTakingPortions(ctx context.Context, dishID int64, quantity int) (Order, error)
	Find(ctx context.Context, id int64) (Order, error)
	SetStatus(ctx context.Context, id int64, to Status) (Order, error)
}
```

`internal/orders/postgres.go`:

```go
package orders

import (
	"context"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type PostgresStore struct {
	pool *pgxpool.Pool
}

func NewPostgresStore(pool *pgxpool.Pool) *PostgresStore {
	return &PostgresStore{pool: pool}
}

const orderColumns = "id, dish_id, quantity, total_naira, status, created_at"

func scanOrder(row pgx.Row) (Order, error) {
	var o Order
	err := row.Scan(&o.ID, &o.DishID, &o.Quantity, &o.TotalNaira, (*string)(&o.Status), &o.CreatedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		return Order{}, ErrOrderNotFound
	}
	return o, err
}

func (s *PostgresStore) PlaceTakingPortions(ctx context.Context, dishID int64, quantity int) (Order, error) {
	var order Order
	err := pgx.BeginFunc(ctx, s.pool, func(tx pgx.Tx) error {
		var price int
		err := tx.QueryRow(ctx, `
			UPDATE dishes SET portions_left = portions_left - $2
			 WHERE id = $1 AND available AND portions_left >= $2
			RETURNING price_naira`,
			dishID, quantity).Scan(&price)
		if errors.Is(err, pgx.ErrNoRows) {
			return ErrNotEnoughPortions
		}
		if err != nil {
			return fmt.Errorf("take portions: %w", err)
		}

		order, err = scanOrder(tx.QueryRow(ctx, `
			INSERT INTO orders (dish_id, quantity, total_naira)
			VALUES ($1, $2, $3)
			RETURNING `+orderColumns,
			dishID, quantity, price*quantity))
		return err
	})
	if err != nil {
		return Order{}, err
	}
	return order, nil
}

func (s *PostgresStore) Find(ctx context.Context, id int64) (Order, error) {
	return scanOrder(s.pool.QueryRow(ctx, "SELECT "+orderColumns+" FROM orders WHERE id = $1", id))
}

func (s *PostgresStore) SetStatus(ctx context.Context, id int64, to Status) (Order, error) {
	return scanOrder(s.pool.QueryRow(ctx,
		"UPDATE orders SET status = $2 WHERE id = $1 RETURNING "+orderColumns, id, to))
}
```

Inside `BeginFunc`, every query uses `tx`, **not** `s.pool`. That's the trap. A transaction lives on **one** connection. `s.pool.QueryRow` would borrow a different connection from the pool, outside the transaction, and the rollback wouldn't undo it.

The total is worked out from `price_naira` as the database returned it, inside the transaction, so even if the kitchen changes the price at that exact moment, the order is charged the price the plate was taken at.

You may notice the orders store writes to the `dishes` table, which "belongs" to the menu. That's a deliberate trade-off: one transaction can only span one database, and taking the plate and writing the order must be one transaction. Inside one service sharing one database, that's fine. Lesson 25, where the app becomes two services, is where table ownership gets strict.

The orders service's `Place` keeps its friendly checks (shop hours, quantity, "that dish doesn't exist", "that dish is finished"), then lets the store do the atomic part:

```go
func (s *Service) Place(ctx context.Context, in NewOrder) (Order, error) {
	hour := s.now().In(s.lagos).Hour()
	if hour < 7 || hour >= 21 {
		return Order{}, ErrShopClosed
	}
	if in.Quantity < 1 || in.Quantity > 20 {
		return Order{}, ErrBadQuantity
	}
	dish, err := s.dishes.Get(ctx, in.DishID)
	if err != nil {
		return Order{}, err
	}
	if !dish.Available {
		return Order{}, ErrDishUnavailable
	}
	return s.store.PlaceTakingPortions(ctx, in.DishID, in.Quantity)
}
```

The `dish.Available` check here gives a clearer message in the usual case. It isn't what keeps us safe: the dish could become unavailable a millisecond after this check. The `WHERE ... AND available` in the `UPDATE` is what's actually safe. When the two disagree, the database wins, and the customer gets `not-enough-portions`.

## Step 8: one change in the composition root
<!-- bite: ea35b035-888c-4c1a-87bc-9f17d665a103 -->

`run` in `cmd/api/main.go` builds the pool and the Postgres stores. Here's the middle of it:

```go
dbURL := getenv("DATABASE_URL")
if dbURL == "" {
	return errors.New("DATABASE_URL is not set")
}
pool, err := db.Open(context.Background(), dbURL)
if err != nil {
	return err
}
defer pool.Close()

menuService := menu.NewService(menu.NewPostgresStore(pool))
orderService, err := orders.NewService(orders.NewPostgresStore(pool), menuService, time.Now)
if err != nil {
	return err
}
```

Remove `startingMenu`: the seed does that job now. Add `"context"` and `"mamaput/internal/db"` to the imports.

`defer pool.Close()` only works because `run` **returns** instead of calling `os.Exit` (lesson 5). When the server stops, `run` returns, the deferred close runs, and every connection is closed politely.

And the promise from lesson 5 came true: `menu.Service` and `orders.Service` didn't need to know a database arrived. Their interfaces changed (context and errors, which every real store needs), but no rule moved.

## Trying the last plate
<!-- bite: 688f44f9-2fbc-43ea-bc64-b0364f383b2b -->

```bash
make run
```

In another terminal, set jollof to exactly 1 portion, then send two orders at the same moment. The `&` runs the first in the background:

```bash
curl -s -X PATCH localhost:8080/menu/1 -H "X-Staff-Key: mama-secret" \
  -H "Content-Type: application/json" -d '{"portionsLeft":1}'

curl -s -X POST localhost:8080/orders -H "Content-Type: application/json" \
  -d '{"dishId":"1","quantity":1}' &
curl -s -X POST localhost:8080/orders -H "Content-Type: application/json" \
  -d '{"dishId":"1","quantity":1}'
wait
```

Predict before you run it: how many get a `201`, and what does the other one get? Exactly one gets the order. The other gets a 422 problem with `code: "not-enough-portions"`. Run it ten times; it's never two.

Then stop the server, start it again, and `curl localhost:8080/orders/1`. The order is still there. Okay!!!!! Mama's notebook works.

## Do you need an ORM?
<!-- bite: eedf0150-bdff-4966-84a9-8a379cc7681e -->

In many languages, the next step would be an **ORM**, a library that writes SQL for you from your types. Go has them (GORM is the best known), and most experienced Go teams avoid them. The SQL an ORM writes is SQL you didn't write and can't easily see, and the moments it matters most (the guarded `UPDATE` above, a careful `JOIN`, a query that must use an index) are exactly where it gets in the way.

What Go teams reach for instead, once there are many queries, is **sqlc**: you write the SQL in `.sql` files, and sqlc **generates** the Go functions and structs for each query, checked against your migrations. You keep plain SQL and lose the hand-written `Scan` lines. It's a good next step for Mama Put API, and nothing in this lesson's design would change: sqlc's code would sit inside `PostgresStore`, behind the same `Store` interfaces.

You'll also see `database/sql` in older code and tutorials. It's the standard library's interface for every SQL database, and pgx can be used through it. We use pgx directly because Mama Put API only ever talks to Postgres, and pgx's own API is faster and gives us things `database/sql` can't, like `BeginFunc` and Postgres's own types.

## The Go in this lesson
<!-- bite: 27d985db-949f-4fe5-a755-eedc63f8f6d7 -->

1. **`//go:embed *.sql`** above **`var FS embed.FS`**: A directive that copies matching files into the program when it's built. The comment must sit right above the variable, with no space after `//`.
2. **`fs.FS`, `fs.ReadDir`, `fs.ReadFile`**: `fs.FS` is the standard interface for "a set of files", whether on disk, embedded, or made up in a test. `ReadDir` lists a folder (sorted by name); `ReadFile` reads one file.
3. **`7_212_026`**: Underscores in a number literal are allowed and ignored, just to make long numbers readable.
4. **`defer conn.Exec(context.Background(), ...)`**: You can defer any call. We use `context.Background()` (a context that's never cancelled) for the unlock, so it still runs even if `ctx` was cancelled.
5. **`flag.Bool("seed", false, "...")`** and **`*seed`**: Declares a command-line option and returns a **pointer** to its value, which is filled in by `flag.Parse()`. You read it with `*seed`.
6. **`cfg.MaxConns = 10`**: Setting a field on the config struct `ParseConfig` returned. `MaxConns` is an `int32`; an untyped constant like `10` fits any number type.
7. **`ctx, cancel := context.WithTimeout(ctx, 5*time.Second)`** and **`defer cancel()`**: Makes a context that's cancelled after 5 seconds. Always call `cancel` when you're done, which `defer` guarantees, or the timer lingers.
8. **`rows.Next()`, `rows.Scan(...)`, `rows.Err()`, `defer rows.Close()`**: The four parts of reading many rows. `Next` moves to the next row and returns false at the end.
9. **`row.Scan(&d.ID, &d.Name, ...)`**: `Scan` takes any number of pointers (a variadic `...any`) and fills each one from a column, in order.
10. **`func scanDish(row pgx.Row)`**: `pgx.Row` is an interface with one method, `Scan`. Both a single row from `QueryRow` and `rows` from `Query` have that method, so one helper reads both.
11. **`` `json:"id,string"` ``**: The `,string` option writes a number as a JSON string, and reads it back from one.
12. **`(*string)(&o.Status)`**: A **conversion** between pointer types. `Status` is built on `string`, so a `*Status` can be converted to a `*string`, and `Scan` fills the status through it.
13. **`pgx.BeginFunc(ctx, s.pool, func(tx pgx.Tx) error { ... })`**: Passes a function that does the work. The outer `order` variable is set inside it (a closure, as in lesson 4), and used after.
14. **`tag.RowsAffected()`**: `Exec` returns a **command tag** describing what happened; `RowsAffected` says how many rows the statement changed.
15. **`"SELECT " + dishColumns + " FROM ..."`** with raw strings: Joining strings to build SQL is only ever done with constants written in the code, never with input.

## Your project so far
<!-- bite: 8f44157e-b5f4-442b-b1c7-80feeed411e3 -->

```text
mama-put/
├── .env                         ← NEW: DATABASE_URL, STAFF_KEY (never committed)
├── .env.example                 ← NEW: the same names with fake values (committed)
├── .gitignore                   ← /api, /migrate, .env
├── Makefile                     ← NEW: run, migrate, seed, test, with .env loaded
├── go.mod                       ← now requires github.com/jackc/pgx/v5
├── go.sum
├── migrations/
│   ├── migrations.go            ← NEW: //go:embed *.sql into FS
│   ├── 001_create_dishes.sql    ← NEW: dishes, with portions_left and CHECKs
│   └── 002_create_orders.sql    ← NEW: orders, with a foreign key to dishes
├── cmd/
│   ├── api/
│   │   └── main.go              ← run opens the pool and builds the Postgres stores
│   └── migrate/
│       └── main.go              ← NEW: runs the migrations; -seed adds the starting menu
└── internal/
    ├── apperr/
    │   └── apperr.go
    ├── app/
    │   └── app.go
    ├── db/
    │   ├── db.go                ← NEW: Open (pool settings and a ping)
    │   └── migrate.go           ← NEW: Migrate (advisory lock, one transaction per file), Seed
    ├── httpx/
    │   ├── errors.go
    │   ├── json.go              ← PathID returns an int64
    │   ├── middleware.go
    │   └── requestid.go
    ├── menu/
    │   ├── menu.go              ← Dish has int64 ID, PortionsLeft, CreatedAt
    │   ├── store.go             ← MemoryStore, updated to the new Store (for tests)
    │   ├── postgres.go          ← NEW: PostgresStore, with COALESCE for PATCH
    │   ├── service.go           ← ListFilter; Store takes ctx and returns errors
    │   ├── service_test.go
    │   └── handlers.go          ← passes r.Context() to the service
    └── orders/
        ├── orders.go            ← int64 IDs, CreatedAt, ErrNotEnoughPortions
        ├── postgres.go          ← NEW: PostgresStore; the last-plate transaction
        ├── service.go           ← Store interface: PlaceTakingPortions, Find, SetStatus
        ├── service_test.go      ← a fakeStore replaces the old memory store
        └── handlers.go
```

The orders `MemoryStore` is gone. A store that takes portions from a menu it can't see wasn't worth keeping; the service tests use a small fake store in the test file instead (see the practice), and lesson 16 tests the real transaction against a real Postgres.

## Common mistakes
<!-- bite: 27e76dc5-5805-4add-9c9c-ea8a575c95a1 -->

1. **Pasting values into SQL.** `fmt.Sprintf("... WHERE id = %s", id)` is SQL injection waiting to happen. Always `$1` and an argument.
2. **Using the pool inside a transaction.** `s.pool.QueryRow` inside `BeginFunc` runs outside the transaction. Use `tx` for everything in it.
3. **Forgetting `rows.Close()`.** The connection never goes back, and after ten requests the pool is empty and every request hangs.
4. **Not checking `rows.Err()`.** A failure partway through reading looks like a short list.
5. **Check-then-act.** Reading a value, deciding in Go, then writing it back is a race. Put the condition in the `UPDATE`'s `WHERE`.
6. **`context.Background()` in handlers.** Pass `r.Context()`, so a client who leaves stops the query.
7. **Editing a migration that's already run.** It won't run again, so the change never happens anywhere that already ran it. Write a new one.
8. **Committing `.env`.** A password in git stays in its history forever. If it happens, change the password.
9. **A huge `MaxConns`.** More connections don't make Postgres faster; past a point they make it slower, and three copies of the app can use up its limit.

## Check your understanding
<!-- bite: e9cacd7f-757e-4fb4-81d5-ee6f87611a11 -->

1. What would go wrong if `PlaceTakingPortions` ran the `UPDATE` with `s.pool.QueryRow` and the `INSERT` with `tx.QueryRow`?
2. Mama runs two copies of the app behind a load balancer. Does the last-plate fix still work? Why?
3. A customer's phone loses signal while `GET /menu` is waiting on a slow query. What happens to the query, and why?
4. A client sends `PATCH /menu/1` with `{"name":"x', price_naira = 1 --"}`. What happens?
5. Why does `Migrate` take an advisory lock?

<details>
<summary>Answers, after your attempt</summary>

1. The `UPDATE` would run on another connection, outside the transaction, and be kept at once. If the `INSERT` then failed, the transaction would roll back the insert, but the plate would stay taken: a portion gone and no order.
2. Yes. The protection is in Postgres (the row lock and the `WHERE portions_left >= $2`), not in the app. Both copies send their `UPDATE` to the same database, which handles them one after the other.
3. The server notices the connection closed and cancels `r.Context()`. The handler passed that context to the query, so pgx tells Postgres to cancel it, and the connection goes back to the pool for the next customer.
4. Validation passes (it's a string under 80 characters), and the dish is renamed to exactly that text. The name went in as `$2`, a value, so it was never read as SQL. Mama may not love the dish's new name, but the price is untouched.
5. So that two copies of the app starting at the same time (as happens in a deploy) don't both run the same migration. The second waits until the first has finished, then finds nothing left to do.

</details>

## Practice
<!-- bite: 37690a14-d5be-4b5b-ba88-abd339f2cb1e -->

1. Update `menu.MemoryStore` to the new `menu.Store` interface (context first, errors returned, `int64` IDs, `ListFilter`), and make the menu service tests from lesson 5 pass again.
2. Write a `fakeStore` in `internal/orders/service_test.go` that satisfies `orders.Store`: `PlaceTakingPortions` looks the dish up in `testMenu`, works out the total and returns an order. Update the lesson 5 tests to pass `context.Background()` and `int64` IDs. Add a test case where the fake store returns `ErrNotEnoughPortions`, and check `Place` passes it up.
3. Make status changes safe in SQL. Change `SetStatus` so the `UPDATE` only matches allowed moves: `WHERE id = $1 AND status = $3`, where the service passes the status that must come before (`pending` before `ready`, `ready` before `collected`). If no row comes back, the service must tell "no such order" (a `Find` that fails) from "wrong status" (`ErrBadStatusChange`). Then two kitchen staff tapping at once can't skip a step.
4. Write `migrations/003_add_dish_description.sql`, adding an optional `description text` column, at most 300 characters. Run `make migrate`. Then carry it through: the types, `dishColumns`, `scanDish`, the insert and the update.
5. Try the race with 20 orders for 5 portions: set `portionsLeft` to 5, then `for i in $(seq 20); do curl -s -o /dev/null -w "%{http_code}\n" -X POST ... & done; wait`. Count the 201s.

**Done when** `make test` passes, `make migrate` applies only `003`, a dish with a description survives a restart, the status can't go backwards even with two requests at once, and the 20-for-5 test gives exactly five 201s.

## Before moving on
<!-- bite: 1f94ed8f-d69f-4bac-b687-2bc2d62d3be0 -->

Mama Put API now keeps everything in Postgres. Data survives restarts, two copies of the app agree, every query stops when its client leaves, and the last plate goes to exactly one customer.

But think about six months from now. Thousands of orders. The kitchen screen asks for every order and gets **all of them** in one response: slow for us, slow for the phone, and mostly useless. The kitchen wants "pending orders, newest first, 20 at a time". Customers want "rice dishes under ₦2,000". That's pagination, filtering, searching and sorting, and the next lesson builds them, safely, on top of SQL.

## Related
<!-- bite: e58f0fdd-1b2c-4ac6-98d9-38e9b4bfa94e -->

- [[backend/frameworks/net-http/09-listing|Next: Pagination, Filtering, Searching, Sorting and Field Selection]]
- [[backend/04-data-and-persistence/01-databases-in-the-backend|Databases in the Backend]] — the idea in any framework
- [[databases/index|Databases]] — how Postgres works inside: indexes, transactions and locks
- [[languages/02-go/08-context|Context]] — cancellation and deadlines in the Go course
- [[backend/frameworks/express/08-data-with-postgres|The same lesson in Express]]

## About this lesson
<!-- bite: a15caaf6-d8e6-4d62-a138-3dd720fc5f5a -->

**Level:** Intermediate. Lesson 8 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, pgx v5 and PostgreSQL 17. Rewritten in November 2026 from an older reference note, "Database Access".
