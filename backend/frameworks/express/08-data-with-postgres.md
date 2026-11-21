---
id: 48e7bf25-c673-4ae2-9b19-b29da607abe2
---

# Data with PostgreSQL

**A database is a program that stores your app's data safely on disk, so it survives restarts, and lets many requests read and change it at once without stepping on each other.** PostgreSQL (often just "Postgres") is one of the most trusted databases there is. Banks, governments and most of the startups you've heard of run on it. In this lesson, Mama Put API moves its menu and orders out of arrays and into Postgres.

## Before you start
<!-- bite: 6fae7de0-4a0a-43dc-9c6f-a7bf45d87bec -->

You should have the app from [[backend/frameworks/express/07-errors|lesson 7]]: one response shape, `AppError`, and services that throw.

You need **Docker** or **Podman** installed, to run Postgres without installing it on your laptop. (If you already have Postgres installed, that's fine too.) You should be able to read a simple SQL statement like `SELECT * FROM dishes WHERE id = 1`. If SQL is new, read the first lessons of [[databases/index|Databases]] alongside this one.

After this lesson you will be able to:

1. Connect an Express app to Postgres with a connection pool.
2. Create and change tables with migrations that run in order, once.
3. Write a repository that uses parameterised queries, so SQL injection can't happen.
4. Use a transaction so "take the portions and create the order" either fully happens or doesn't happen at all, even when two customers order the last plate at the same moment.

## Where we stopped
<!-- bite: f07031d1-b033-457b-9439-78df63357b8a -->

Lesson 7 ended with three problems:

1. **Everything vanishes on restart.** The arrays live in memory. Mama's new ofada rice, every customer's order: gone.
2. **Only one copy of the app can run.** If we ran two copies of the app to handle more customers, each would have its own arrays and they'd disagree.
3. **The last plate problem.** Mama only cooks so much. Two customers order the last plate of jollof at the same moment. Both requests check "is there jollof?", both see "yes", both orders go through. One customer pays for food that doesn't exist.

A database solves all three. And because we built the repositories as async factories in lessons 4 and 5, the rest of the app barely notices the change.

## The kid version
<!-- bite: 962466e6-9763-4f44-8abe-cb803c952a8d -->

Up to now, Mama has been keeping her orders in her head. It works until she sleeps (restart), or until her sister helps at a second stand (two copies) and neither knows what the other sold.

So Mama gets a big notebook that stays at the shop: the database. Everyone writes in it, everyone reads from it. And she adds a rule for the last plate: you don't just *look* in the pot and then serve. You take the plate out of the pot and write the order down **in one movement**, and nobody else can touch that pot while you're doing it.

**Where the picture stops working.** A notebook can only be used by one person at a time. Postgres lets thousands of requests read and write at once, and only makes them wait when they touch the *same* row at the same moment.

## Terms used in this lesson
<!-- bite: c96ac88f-810f-4a5d-a057-e312a6096c78 -->

1. **Table**: This is a set of rows that all have the same columns, like a spreadsheet tab. We'll have a `dishes` table and an `orders` table.
2. **Connection**: This is an open line between your app and the database. Opening one takes time (tens of milliseconds), so you don't want to open a new one for every request.
3. **Connection pool**: This is a small set of connections the app opens once and reuses. A request borrows a connection, runs its queries, and gives it back. `pg.Pool` does this for us.
4. **Migration**: This is a file that changes the database's structure: create a table, add a column. Migrations are numbered and run in order, and each runs exactly once on each database. They're how your laptop, your test database and production all end up with the same tables.
5. **Parameterised query**: This is a query where values are sent separately from the SQL text, as `$1`, `$2`. The database never mixes them into the SQL, so a value can never be run as SQL. This is what stops **SQL injection**.
6. **Transaction**: This is a group of SQL statements that succeed or fail together. You start with `BEGIN`, end with `COMMIT` to keep everything, or `ROLLBACK` to undo everything.
7. **Constraint**: This is a rule the database itself enforces, like "price must be positive" or "an order's dish must exist". It's the last line of defence if a bug gets past your code.

## Step 1: start Postgres
<!-- bite: 5810ded9-4637-4ca3-abce-5796937c71eb -->

```bash
docker run --name mama-put-db -d \
  -e POSTGRES_PASSWORD=mamaput -e POSTGRES_DB=mama_put \
  -p 5432:5432 postgres:17
```

(With Podman, write `podman` instead of `docker`; everything else is the same.) That starts Postgres in the background, with a database called `mama_put`, listening on port 5432. In [[backend/frameworks/express/26-production-config-and-docker|lesson 26]] the whole system starts with one Docker Compose command. For now, one container is enough.

Install the Postgres client library for Node, and its types:

```bash
npm install pg
npm install --save-dev @types/pg
```

## Step 2: keep the password out of the code
<!-- bite: 95a65b1e-5945-41c9-9087-b4e038f4873f -->

The app needs to know where the database is. That's a **connection string**, and it has a password in it, so it must never be written in the code or committed to git.

Create `.env` in the project root:

```text
DATABASE_URL=postgres://postgres:mamaput@localhost:5432/mama_put
STAFF_KEY=jollof123
```

Add `.env` to `.gitignore`. Then create `.env.example`, which *is* committed, so teammates know what to fill in:

```text
DATABASE_URL=postgres://user:password@localhost:5432/mama_put
STAFF_KEY=change-me
```

Node can read `.env` files itself. Update the scripts in `package.json`:

```json
"scripts": {
  "dev": "node --env-file=.env --watch src/server.ts",
  "migrate": "node --env-file=.env src/db/migrate.ts",
  "seed": "node --env-file=.env src/db/seed.ts",
  "check": "tsc --noEmit"
}
```

`--env-file=.env` loads the file into `process.env` before your code runs, so `process.env.DATABASE_URL` holds the string. In [[backend/frameworks/express/26-production-config-and-docker|lesson 26]] we check every setting properly when the app starts.

## Step 3: the tables, as migrations
<!-- bite: 0d3cd574-d14f-462f-ba4a-afbade31bfca -->

Make a `migrations/` folder in the project root (not in `src/`, because it's SQL, not app code).

`migrations/001_create_dishes.sql`:

```sql
CREATE TABLE dishes (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name          text    NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
  price_naira   integer NOT NULL CHECK (price_naira > 0),
  available     boolean NOT NULL DEFAULT true,
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

A few things worth slowing down for:

1. **`GENERATED ALWAYS AS IDENTITY`**: Postgres picks the next `id` itself: 1, 2, 3. No more `nextId++`, and no two orders can ever get the same id, even from two copies of the app.
2. **`portions_left`** is new. It's the pot: how many plates Mama has left. It can never go below zero, because of the `CHECK`.
3. **The `CHECK`s repeat some rules from our zod schemas and services.** That's on purpose. Zod gives the client a nice message. The database is the guard of last resort: if a bug ever skips the service, the database still refuses a negative price.
4. **`REFERENCES dishes (id)`** is a **foreign key**: an order can't point at a dish that doesn't exist, and a dish with orders can't be deleted out from under them.
5. **Names are `snake_case`** in the database (`price_naira`) and `camelCase` in TypeScript (`priceNaira`). That's normal. The repository translates between them.

## Step 4: a small migration runner
<!-- bite: 9b72dae2-dad6-4bca-b4a7-f0b9ce2c527b -->

Tools like `node-pg-migrate`, Prisma Migrate and drizzle-kit run migrations for you, and in a big project you'd use one. But a runner is only about 30 lines, and writing one shows you exactly what those tools do.

`src/db/migrate.ts`:

```ts
import { readdir, readFile } from "node:fs/promises";
import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const folder = new URL("../../migrations/", import.meta.url);

await pool.query(`
  CREATE TABLE IF NOT EXISTS schema_migrations (
    name       text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
  )`);

const applied = new Set(
  (await pool.query("SELECT name FROM schema_migrations")).rows.map((row) => row.name),
);
const files = (await readdir(folder)).filter((f) => f.endsWith(".sql")).sort();

for (const file of files) {
  if (applied.has(file)) continue;
  const sql = await readFile(new URL(file, folder), "utf8");
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query(sql);
    await client.query("INSERT INTO schema_migrations (name) VALUES ($1)", [file]);
    await client.query("COMMIT");
    console.log(`applied ${file}`);
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
}

await pool.end();
```

1. It keeps a table, `schema_migrations`, listing every file already applied.
2. It reads the `.sql` files in name order. That's why they start with `001_`, `002_`.
3. Each new file runs **inside a transaction**, together with recording its name. If the SQL fails halfway, both are undone, so a migration is never "half applied".

```bash
npm run migrate
# applied 001_create_dishes.sql
# applied 002_create_orders.sql

npm run migrate
# (nothing: both already applied)
```

Run it twice and predict the second output before you look. The golden rule: **never edit a migration that has already run anywhere else.** To change a table, write `003_...`. Editing `001` would leave your database and your teammate's different, with no record of why.

The seed script puts Mama's starting menu in, so you have something to look at. `src/db/seed.ts`:

```ts
import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const { rows } = await pool.query("SELECT count(*)::int AS n FROM dishes");
if (rows[0].n === 0) {
  await pool.query(`
    INSERT INTO dishes (name, price_naira, available, portions_left) VALUES
      ('Jollof rice', 1500, true, 40),
      ('Beans and plantain', 1200, true, 25),
      ('Pounded yam and egusi', 2500, false, 0)`);
  console.log("seeded the menu");
}
await pool.end();
```

```bash
npm run seed
```

## Step 5: the pool
<!-- bite: 1aefc41a-2619-4bdf-ac5e-decf79fdc91b -->

`src/db/pool.ts`:

```ts
import pg from "pg";

export function createPool(connectionString: string) {
  const pool = new pg.Pool({ connectionString, max: 10 });
  pool.on("error", (err) => {
    console.error("idle database connection failed", err);
  });
  return pool;
}

export type Queryable = pg.Pool | pg.PoolClient;
```

`max: 10` means at most ten connections at once. If eleven requests need the database at the same instant, the eleventh waits a few milliseconds for one to be returned. That's a good thing: Postgres slows down badly with too many connections, and the pool protects it. ([[databases/index|Databases]] explains why.)

`Queryable` is "either the pool, or one borrowed connection". Both have a `.query()` method, and the repository will accept either. That matters for transactions.

## Step 6: the menu repository, for real
<!-- bite: 3b14b33e-08b4-4b81-94c5-2a9446f52829 -->

The `Dish` type gets the new field:

```ts
// src/menu/menu.types.ts
export type Dish = {
  id: string;
  name: string;
  priceNaira: number;
  available: boolean;
  portionsLeft: number;
};
```

(Add `portionsLeft: z.number().int().min(0).max(500)` to `NewDishSchema` too, so the kitchen can say how much it cooked.)

`src/menu/menu.pg-repository.ts`:

```ts
import type pg from "pg";
import type { Dish, MenuRepository, NewDish, DishChanges } from "./menu.types.ts";
import { conflict } from "../shared/errors.ts";

type DishRow = {
  id: string;
  name: string;
  price_naira: number;
  available: boolean;
  portions_left: number;
};

function toDish(row: DishRow): Dish {
  return {
    id: row.id,
    name: row.name,
    priceNaira: row.price_naira,
    available: row.available,
    portionsLeft: row.portions_left,
  };
}

const COLUMNS = {
  name: "name",
  priceNaira: "price_naira",
  available: "available",
  portionsLeft: "portions_left",
} as const;

export function createPgMenuRepository(pool: pg.Pool): MenuRepository {
  return {
    async list() {
      const { rows } = await pool.query<DishRow>("SELECT * FROM dishes ORDER BY id");
      return rows.map(toDish);
    },

    async findById(id) {
      const { rows } = await pool.query<DishRow>("SELECT * FROM dishes WHERE id = $1", [id]);
      return rows[0] ? toDish(rows[0]) : null;
    },

    async create(input: NewDish) {
      const { rows } = await pool.query<DishRow>(
        `INSERT INTO dishes (name, price_naira, portions_left)
         VALUES ($1, $2, $3)
         RETURNING *`,
        [input.name, input.priceNaira, input.portionsLeft],
      );
      return toDish(rows[0]);
    },

    async update(id, changes: DishChanges) {
      const sets: string[] = [];
      const values: unknown[] = [];
      for (const [field, column] of Object.entries(COLUMNS)) {
        const value = changes[field as keyof DishChanges];
        if (value !== undefined) {
          values.push(value);
          sets.push(`${column} = $${values.length}`);
        }
      }
      values.push(id);
      const { rows } = await pool.query<DishRow>(
        `UPDATE dishes SET ${sets.join(", ")} WHERE id = $${values.length} RETURNING *`,
        values,
      );
      return rows[0] ? toDish(rows[0]) : null;
    },

    async remove(id) {
      try {
        const result = await pool.query("DELETE FROM dishes WHERE id = $1", [id]);
        return result.rowCount === 1;
      } catch (err) {
        if ((err as { code?: string }).code === "23503") {
          throw conflict("dish-has-orders", "This dish has orders, so it can't be deleted. Mark it unavailable instead.");
        }
        throw err;
      }
    },
  };
}
```

Go through it slowly. Each method does the same thing the in-memory version did, and it satisfies the same `MenuRepository` type. That's the promise from lesson 5 being kept.

1. **`$1`, `$2`, ...** are placeholders. The values travel in the array beside the SQL. We **never** build SQL by pasting values in.
2. **`RETURNING *`** makes `INSERT` and `UPDATE` hand back the row they wrote, so we don't need a second query to read it.
3. **`toDish`** translates a database row (`price_naira`) into our TypeScript shape (`priceNaira`). The rest of the app never sees a database row.
4. **`id` is already text.** Postgres's `bigint` can hold numbers bigger than JavaScript can safely store, so `pg` hands them over as strings. Our ids were text all along, so nothing changes.
5. **`update`** builds `SET name = $1, price_naira = $2` from only the fields that were sent. Look where the column names come from: the `COLUMNS` constant **we** wrote, never from the request. The values still go through placeholders. That's the one safe way to build dynamic SQL.
6. **`remove`** catches Postgres error `23503`, "foreign key violation": the dish has orders pointing at it. We turn that into a clear 409 conflict with advice, instead of a 500.

## Why placeholders matter: SQL injection
<!-- bite: f77db9dc-c778-449a-9f84-78ff26d2422b -->

Here's what you must never write:

```ts
// ☠ NEVER
pool.query(`SELECT * FROM dishes WHERE id = ${id}`);
```

Validation already checks that `id` is digits. But imagine one route forgot. A request for `/menu/1;DROP TABLE orders` puts that text straight into the SQL, and Postgres runs both statements. Every order is gone.

With `WHERE id = $1` and `[id]`, Postgres receives the SQL and the value **separately**. The value `1;DROP TABLE orders` is just a strange id that matches nothing. There's no way for a value to become SQL. Validation and placeholders together: two locks on the same door.

## Step 7: the last plate, with a transaction
<!-- bite: c7e71431-69f8-490b-96fd-69f4b7c46498 -->

Now the hard problem. Mama has 1 plate of jollof left. Ada and Bayo order at the same moment.

The obvious code looks like this:

```ts
const dish = await menu.findById(id);          // Ada sees 1 left. Bayo sees 1 left.
if (dish.portionsLeft < quantity) throw ...;   // both pass
await menu.update(id, { portionsLeft: dish.portionsLeft - quantity }); // both set 0
await orders.create(...);                      // two orders, one plate
```

Between "look" and "take", the other request slipped in. This is called a **race condition**, and it's the kind of bug that never shows up when you test alone on your laptop, then shows up every Friday at lunch.

The fix has two parts.

**Part 1: look and take in one statement.**

```sql
UPDATE dishes
   SET portions_left = portions_left - $2
 WHERE id = $1 AND available AND portions_left >= $2
RETURNING price_naira
```

Postgres locks the row while it updates it. If Ada's update goes first, Bayo's update waits; then it checks `portions_left >= 1` again, finds 0, and updates **nothing**. No row comes back, so we know he was too late. No race.

**Part 2: take the plate and write the order together.** If we take the portion and then the order insert fails (a bug, the server crashes in between), Mama's pot shows one plate fewer and nobody has an order. A transaction makes both happen, or neither.

`src/db/transaction.ts`:

```ts
import type pg from "pg";

export async function inTransaction<T>(
  pool: pg.Pool,
  work: (tx: pg.PoolClient) => Promise<T>,
): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await work(client);
    await client.query("COMMIT");
    return result;
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
}
```

It borrows **one** connection (a transaction only exists on one connection), runs your work on it between `BEGIN` and `COMMIT`, rolls back if anything throws, and always gives the connection back. That `finally` matters: forget `release()` and after ten orders the pool is empty and the whole app freezes.

Where does the transaction live? It must see both the `dishes` and `orders` tables, so we give the orders repository one job that needs both: **place an order, taking the portions**. The orders repository type becomes:

```ts
// src/orders/orders.types.ts
export type OrdersRepository = {
  placeTakingPortions(dishId: string, quantity: number): Promise<Order | null>;
  findById(id: string): Promise<Order | null>;
  updateStatus(id: string, status: OrderStatus): Promise<Order | null>;
};
```

`src/orders/orders.pg-repository.ts`:

```ts
import type pg from "pg";
import type { Order, OrdersRepository } from "./orders.types.ts";
import { inTransaction } from "../db/transaction.ts";

type OrderRow = {
  id: string;
  dish_id: string;
  quantity: number;
  total_naira: number;
  status: Order["status"];
  created_at: Date;
};

function toOrder(row: OrderRow): Order {
  return {
    id: row.id,
    dishId: row.dish_id,
    quantity: row.quantity,
    totalNaira: row.total_naira,
    status: row.status,
    createdAt: row.created_at.toISOString(),
  };
}

export function createPgOrdersRepository(pool: pg.Pool): OrdersRepository {
  return {
    placeTakingPortions(dishId, quantity) {
      return inTransaction(pool, async (tx) => {
        const taken = await tx.query<{ price_naira: number }>(
          `UPDATE dishes SET portions_left = portions_left - $2
            WHERE id = $1 AND available AND portions_left >= $2
           RETURNING price_naira`,
          [dishId, quantity],
        );
        if (taken.rowCount === 0) return null;

        const { rows } = await tx.query<OrderRow>(
          `INSERT INTO orders (dish_id, quantity, total_naira)
           VALUES ($1, $2, $3)
           RETURNING *`,
          [dishId, quantity, taken.rows[0].price_naira * quantity],
        );
        return toOrder(rows[0]);
      });
    },

    async findById(id) {
      const { rows } = await pool.query<OrderRow>("SELECT * FROM orders WHERE id = $1", [id]);
      return rows[0] ? toOrder(rows[0]) : null;
    },

    async updateStatus(id, status) {
      const { rows } = await pool.query<OrderRow>(
        "UPDATE orders SET status = $2 WHERE id = $1 RETURNING *",
        [id, status],
      );
      return rows[0] ? toOrder(rows[0]) : null;
    },
  };
}
```

(Add `createdAt: string` to the `Order` type. The database fills it in, and we'll need it for sorting and paging in [[backend/frameworks/express/09-listing|lesson 9]].)

Notice the price comes from the `UPDATE ... RETURNING price_naira`, the price **at the moment of ordering**, read inside the transaction. If Mama changes the price a second later, this order keeps the price the customer saw.

And the service? It keeps the business rules and gives the "too late" answer its business meaning:

```ts
// src/orders/orders.service.ts
async place(dishId: string, quantity: number): Promise<Order> {
  if (quantity > 20) {
    throw ruleBroken("too-many-plates", "You can order at most 20 plates at once.");
  }
  const dish = await menuService.get(dishId);           // throws notFound
  if (!dish.available) {
    throw ruleBroken("dish-unavailable", `${dish.name} is finished for today.`);
  }
  const order = await ordersRepository.placeTakingPortions(dishId, quantity);
  if (!order) {
    throw ruleBroken("not-enough-portions", `There isn't enough ${dish.name} left for ${quantity}.`);
  }
  return order;
}
```

Is it a bit odd that the *orders* repository updates the *dishes* table? A little, and it's a real trade-off. The alternative is a "unit of work": the service opens the transaction and passes it to both repositories. That's cleaner on paper, but then the service has to know about database connections. For one operation like this, keeping the transaction inside one repository method is simpler and very common. If you find yourself needing many cross-table transactions, that's when the unit of work earns its keep.

## Step 8: one line in the composition root
<!-- bite: e396f5b7-a9bc-4668-bf2f-76c03f977d9e -->

```ts
// src/server.ts
import { createApp } from "./app.ts";
import { createPool } from "./db/pool.ts";
import { createPgMenuRepository } from "./menu/menu.pg-repository.ts";
import { createPgOrdersRepository } from "./orders/orders.pg-repository.ts";
import { createMenuService } from "./menu/menu.service.ts";
import { createOrdersService } from "./orders/orders.service.ts";
import { createKitchenOnly } from "./shared/kitchen-only.ts";

const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) throw new Error("DATABASE_URL is not set");

const pool = createPool(databaseUrl);
const menuRepository = createPgMenuRepository(pool);
const ordersRepository = createPgOrdersRepository(pool);
const menuService = createMenuService({ menuRepository });
const ordersService = createOrdersService({ ordersRepository, menuService });
const kitchenOnly = createKitchenOnly(process.env.STAFF_KEY ?? "");

createApp({ menuService, ordersService, kitchenOnly }).listen(3000, () =>
  console.log("Mama Put API on http://localhost:3000"),
);
```

Compare it with lesson 5. `createInMemoryMenuRepository` became `createPgMenuRepository(pool)`. Nothing in `menu.service.ts`, `menu.routes.ts` or `app.ts` changed for the menu. Lessons 4 and 5 were paying for this moment.

(The in-memory repositories stay. Tests use them in [[backend/frameworks/express/16-testing|lesson 16]], so update `createInMemoryOrdersRepository` to match the new type: it takes the in-memory menu repository and does the same check-and-take in plain code.)

## Trying the last plate
<!-- bite: edea349a-4531-43c5-aace-0f71eab9fad0 -->

```bash
npm run dev

# Set jollof to exactly 1 portion
curl -s -X PATCH http://localhost:3000/menu/1 -H "Content-Type: application/json" \
  -H "X-Staff-Key: jollof123" -d '{"portionsLeft":1}'

# Two orders at the same moment (the & runs the first in the background)
curl -s -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d '{"dishId":"1","quantity":1}' &
curl -s -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d '{"dishId":"1","quantity":1}'
```

Predict before you run it: how many get `201`, and what does the other one get? Exactly one gets the order. The other gets `422 not-enough-portions`. Run it ten times; it's never two.

Then stop the app, start it again, and `curl http://localhost:3000/orders/1`. The order is still there. Okay!!!!! Mama's notebook works.

## The TypeScript in this lesson
<!-- bite: c3b7e96b-ab26-48e2-b6fa-b511c09de320 -->

1. **`import type pg from "pg"` and `import pg from "pg"`**: In the repositories we only need pg's *types* (`pg.Pool`, `pg.PoolClient`), so `import type` is enough. In `pool.ts` and `migrate.ts` we actually create a pool with `new pg.Pool(...)`, so we need the real import.
2. **`await` at the top of a file (`migrate.ts`)**: In a module (`"type": "module"`), you can use `await` outside any function. The script simply waits at that line. This is called **top-level await**, and it's perfect for small scripts.
3. **`new URL("../../migrations/", import.meta.url)`**: `import.meta.url` is the address of the current file. Building a `URL` from it finds the `migrations` folder relative to *this file*, whatever folder you ran the command from.
4. **`new Set(...)` and `applied.has(file)`**: A `Set` is a collection with no duplicates and a fast "is this in it?" check.
5. **`` `UPDATE dishes SET ${sets.join(", ")} WHERE id = $${values.length}` ``**: Careful, two different `$` meanings in one line. `${...}` is the template string dropping in a value. The `$` just before it is a plain character. So `$${values.length}` produces text like `$3`, Postgres's placeholder.
6. **`pool.query<DishRow>(...)`**: The `<DishRow>` tells TypeScript what each row looks like, so `rows[0].price_naira` is known to be a number. TypeScript can't check the database really returns that; it's a promise you make, like `as`. That's why `toDish` is in one place: one promise to keep.
7. **`as const`**: On `COLUMNS`, it tells TypeScript "these values will never change", so the types are the exact words (`"price_naira"`), not just `string`.
8. **`Object.entries(COLUMNS)`**: Gives the object's fields as a list of `[key, value]` pairs, so we can loop over them: `["priceNaira", "price_naira"]`, and so on.
9. **`field as keyof DishChanges`**: `keyof DishChanges` means "one of the field names of DishChanges". `Object.entries` only promises text keys, so we assure TypeScript that `field` is one of those names.
10. **`(err as { code?: string }).code`**: Postgres errors carry a `code`, but a caught error is `unknown`. This assertion says "treat it as something that may have a `code`". The `?` keeps it honest: it might not.
11. **`async function inTransaction<T>(..., work: (tx: pg.PoolClient) => Promise<T>): Promise<T>`**: Generic again. `T` is whatever your `work` returns. Pass work that returns an `Order | null`, and `inTransaction` returns `Promise<Order | null>`. One helper, any result type.
12. **`try { } catch { } finally { }`**: `try` runs the code; `catch` runs only if something threw; `finally` runs **no matter what**, success or failure. That's why `client.release()` lives in `finally`.
13. **`Order["status"]`**: The type of the `status` field of `Order`, so the row type reuses `"pending" | "ready" | "collected"` instead of repeating it.
14. **`process.env.STAFF_KEY ?? ""`**: Use the setting, or an empty text if it's missing. (An empty key means nobody gets in, which is the safe direction. Lesson 26 refuses to start without it.)

## Your project so far
<!-- bite: 999bf21d-21fc-48a9-a3f4-3cba4600f878 -->

```text
mama-put-api/
├── .env                          ← NEW: DATABASE_URL, STAFF_KEY (never committed)
├── .env.example                  ← NEW: the same settings with fake values (committed)
├── .gitignore                    ← node_modules/ and .env
├── package.json                  ← pg added; dev, migrate, seed, check scripts
├── package-lock.json
├── tsconfig.json
├── migrations/
│   ├── 001_create_dishes.sql     ← NEW: the dishes table, with portions_left and CHECKs
│   └── 002_create_orders.sql     ← NEW: the orders table, with a foreign key to dishes
└── src/
    ├── server.ts                 ← builds the pool and the Postgres repositories
    ├── app.ts
    ├── db/
    │   ├── pool.ts               ← NEW: createPool(), the Queryable type
    │   ├── transaction.ts        ← NEW: inTransaction()
    │   ├── migrate.ts            ← NEW: the migration runner (npm run migrate)
    │   └── seed.ts               ← NEW: Mama's starting menu (npm run seed)
    ├── menu/
    │   ├── menu.schemas.ts       ← NewDish now includes portionsLeft
    │   ├── menu.types.ts         ← Dish now has portionsLeft
    │   ├── menu.repository.ts    ← the in-memory version, kept for tests
    │   ├── menu.pg-repository.ts ← NEW: the same MenuRepository, on Postgres
    │   ├── menu.service.ts
    │   └── menu.routes.ts
    ├── orders/
    │   ├── orders.schemas.ts
    │   ├── orders.types.ts       ← Order has createdAt; OrdersRepository has placeTakingPortions
    │   ├── orders.repository.ts  ← in-memory version, updated to the new type
    │   ├── orders.pg-repository.ts ← NEW: the transaction that takes portions and writes the order
    │   ├── orders.service.ts     ← "not-enough-portions" rule
    │   ├── orders.service.test.ts
    │   └── orders.routes.ts
    └── shared/
        ├── errors.ts
        ├── request-id.ts
        ├── validate.ts
        ├── log-requests.ts
        ├── kitchen-only.ts
        ├── not-found.ts
        └── error-handler.ts
```

## Common mistakes
<!-- bite: 0d79f39d-f733-4ed7-bfaf-4f99a352f60c -->

1. **Pasting values into SQL.** `` `WHERE id = ${id}` `` is SQL injection waiting to happen. Always `$1` and an array.
2. **A new connection per request.** Use the pool. Opening connections is slow, and Postgres falls over with too many.
3. **Forgetting `client.release()`.** The pool runs dry and every request hangs. Always release in `finally`.
4. **Running a transaction on `pool.query`.** Each `pool.query` may use a *different* connection, so `BEGIN` on one and `COMMIT` on another does nothing useful. A transaction needs one borrowed client for all its statements.
5. **Check-then-act.** Reading a value, deciding in JavaScript, then writing it back is a race. Put the condition in the `UPDATE`'s `WHERE`.
6. **Editing an old migration.** Write a new one.
7. **Committing `.env`.** Passwords in git stay in git history forever, even after you delete the file. If it happens, change the password.
8. **Letting database rows leak out.** If a route sends `price_naira`, a row escaped the repository. Map every row.

## Check your understanding
<!-- bite: 442ed07b-3fcb-475d-a196-4cd3c5140621 -->

1. Why does `id` come back from Postgres as text, and why doesn't that break our app?
2. What would go wrong if `placeTakingPortions` did the `UPDATE` and the `INSERT` with `pool.query` instead of inside `inTransaction`?
3. Mama runs two copies of the app behind a load balancer. Does the last-plate fix still work? Why?
4. A client sends `PATCH /menu/1` with `{"price_naira; DROP TABLE dishes": 1}`. What happens?

<details>
<summary>Answers, after your attempt</summary>

1. `bigint` can hold numbers larger than JavaScript can represent exactly, so `pg` returns them as strings to be safe. Our ids were already text throughout the app (from the URL, in the types), so nothing changes.
2. They might run on different connections with no transaction around them. If the insert failed after the update, a portion would be taken with no order. Also, the update and insert wouldn't be guaranteed to happen together.
3. Yes. The protection is in Postgres, which both copies share: the row lock and the `portions_left >= $2` condition. The app copies don't need to know about each other.
4. Zod strips the unknown field, so `changes` is empty and the `refine` rule from lesson 6 answers 400. Even if it got through, the repository only takes column names from its own `COLUMNS` list, so the strange key is never used.

</details>

## Practice
<!-- bite: ed3ecc59-aa2d-4d18-aa57-9f49d96c2871 -->

1. Write `migrations/003_add_dish_description.sql`, which adds an optional `description text` column (at most 300 characters). Run `npm run migrate`. Then carry it through: the schema, the type, `toDish`, `COLUMNS`, and the insert.
2. Add a rule to `orders.pg-repository.ts`'s `updateStatus`: only move forward. Do it in SQL, with a `WHERE` that only matches allowed changes (pending → ready, ready → collected), so two kitchen staff clicking at once can't skip a step. Return `null` if nothing matched, and have the service throw `conflict("bad-status-change", ...)`.
3. Try the race again with 20 parallel orders for 5 portions (`for i in $(seq 20); do curl ... & done; wait`). Count the 201s.

**Done when** `npm run migrate` applies only `003`, a dish with a description survives a restart, the status can't go backwards even with two parallel requests, and the 20-for-5 test gives exactly five 201s.

## Before moving on
<!-- bite: 079c9f0e-affa-40db-bc2b-626656032a03 -->

Mama Put API now keeps everything in Postgres. Data survives restarts, two copies of the app agree, and the last plate goes to exactly one customer.

But think about what happens in six months. Thousands of orders. The kitchen screen asks for `GET /orders` and gets **all of them** in one response: slow for us, slow for the phone, and mostly useless. The kitchen wants "pending orders, newest first, 20 at a time". Customers want "rice dishes under ₦2,000". That's pagination, filtering, searching and sorting, and the next lesson builds them, safely, on top of SQL.

## Related
<!-- bite: eabce692-a667-4de6-b0e7-b3128a87b309 -->

- [[backend/frameworks/express/09-listing|Next: Pagination, Filtering, Searching, Sorting and Field Selection]]
- [[backend/04-data-and-persistence/01-databases-in-the-backend|Databases in the Backend]] — the idea in any framework
- [[databases/index|Databases]] — how Postgres works inside: indexes, transactions and locks
- [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]] — the other half of "don't do it twice", which we build in lesson 15

## About this lesson
<!-- bite: 894ba8e7-aca8-488c-b568-17d395a23fbd -->

**Level:** Intermediate. Lesson 8 of [[backend/frameworks/express/index|Express]]. Covers running Postgres in a container, `.env` files with `node --env-file`, migrations and a small runner, a seed script, `pg.Pool`, a Postgres repository behind the same interface as the in-memory one, row mapping, parameterised queries and SQL injection, safe dynamic `UPDATE`s, foreign-key errors as conflicts, a conditional `UPDATE` to stop the last-plate race, and a transaction helper. Written against `pg` 8 and PostgreSQL 17.
