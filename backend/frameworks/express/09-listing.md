---
id: 3fd09ac2-33dd-4ec9-bd4d-e04729907d1b
---

# Pagination, Filtering, Searching, Sorting and Field Selection

**These five are the ways a client asks for *part* of a list instead of all of it: pagination gives it a page at a time, filtering keeps only matching items, searching matches by text, sorting chooses the order, and field selection chooses which fields of each item come back.** You use them every day without thinking. Scrolling a shop's products 20 at a time, ticking "under ₦5,000", typing "rice" in a search box, choosing "newest first". Every one of those is a query parameter the backend has to understand.

## Before you start
<!-- bite: 31fd3ca9-d7ca-48fa-84c5-4b11b1e16d89 -->

You should have Postgres working from [[backend/frameworks/express/08-data-with-postgres|lesson 8]], with the menu and orders in the database.

After this lesson you will be able to:

1. Page through a list with offset pagination, and say when it breaks.
2. Page through a busy, changing list with cursor pagination.
3. Turn filter, search, sort and field query parameters into SQL without ever letting the client write SQL.
4. Return lists in one predictable shape, with paging information in `meta`.

## Where we stopped
<!-- bite: 3e2cab34-dcb8-4215-9972-b3b42b6ddc35 -->

Lesson 8 ended with a picture of Mama Put six months from now: thousands of orders, and `GET /orders` sending every single one. Here's what different people actually want from those lists:

1. **The kitchen screen**: pending orders, oldest first, 20 at a time, and it must never skip or repeat an order while new ones keep arriving.
2. **A customer on the phone app**: rice dishes, under ₦2,000, cheapest first.
3. **Someone searching**: "egusi".
4. **A slow phone on bad network**: only each dish's name and price, nothing else.

Remember the rule from [[backend/frameworks/express/02-routing|lesson 2]]: a path parameter says *which thing*, a query parameter says *how you want it*. All four wishes are "how", so all four are query parameters on the same two routes, `GET /menu` and `GET /orders`.

## The kid version
<!-- bite: 8c7db051-9086-42fb-a836-ca1df4964089 -->

Mama's notebook now has hundreds of pages of orders. When the kitchen asks "what's next?", she doesn't read them the whole book.

She opens to where they stopped, reads the next 20 (**pagination**). If they ask "only the pending ones" she skips the rest (**filtering**). "Anyone who ordered egusi?" she runs her finger down looking for the word (**searching**). "Oldest first" she reads from the top (**sorting**). And if they only need the dish name and quantity, she doesn't read out the customer's phone number (**field selection**).

**Where the picture stops working.** Mama can say "we stopped at page 12". With a list that keeps growing at the top, page 12 isn't the same page five minutes later. That's why the kitchen needs a bookmark, not a page number. We'll build both.

## Terms used in listing
<!-- bite: 6b96376b-63de-473b-81d7-fc28aad1670d -->

1. **Pagination**: This is splitting a long list into pages and returning one page per request.
2. **Limit**: This is how many items one page holds. The client chooses, within a maximum we set.
3. **Offset pagination**: This is also called **page-number pagination**. The client says "page 3" and we skip the first `(3 − 1) × limit` items. Easy to understand, and it lets you jump to any page.
4. **Cursor pagination**: This is also called **keyset pagination**. Instead of a page number, each page comes with a **cursor**, a bookmark that says "the last item you saw". The next request says "items after this bookmark".
5. **Filter**: This is a condition that keeps only some items, like `status=pending` or `maxPrice=2000`.
6. **Search**: This is matching items by text the user typed, like `q=egusi`.
7. **Sort**: This is the order items come back in, like `sort=-priceNaira` (a minus sign means highest first).
8. **Field selection**: This is also called **sparse fieldsets**. The client lists the fields it wants, like `fields=id,name,priceNaira`, and gets only those.
9. **Allow-list**: This is a fixed list of values we accept. Sort fields and selectable fields come from allow-lists, never straight from the client.

## Step 1: decide the query parameters
<!-- bite: 23cb2962-94c2-4c06-9126-f2c7b517788d -->

Write them down first, as a contract, before any code:

| Parameter | Example | Meaning |
|---|---|---|
| `page` | `page=2` | which page (menu only) |
| `limit` | `limit=20` | items per page, 1–100, default 20 |
| `cursor` | `cursor=eyJ0Ij...` | "after this bookmark" (orders only) |
| `available` | `available=true` | only dishes Mama is selling now |
| `minPrice`, `maxPrice` | `maxPrice=2000` | price range in naira |
| `status` | `status=pending` | orders in that status |
| `q` | `q=egusi` | search dish names |
| `sort` | `sort=priceNaira,-name` | comma-separated, `-` means descending |
| `fields` | `fields=id,name,priceNaira` | only these fields |

And the answer always looks like this:

```json
{
  "data": [ { "id": "2", "name": "Beans and plantain", "priceNaira": 1200 } ],
  "meta": { "page": 1, "limit": 20, "total": 37, "totalPages": 2 }
}
```

That's the `{ data, meta }` envelope from [[backend/frameworks/express/07-errors|lesson 7]] earning its keep: there's a place for paging information that doesn't get mixed up with the dishes.

## Step 2: validate the menu's query
<!-- bite: 37cc5fa2-1f23-45d6-a76d-cf59713eacc1 -->

Everything in a query string is text, and any of it could be nonsense, so it all goes through zod first. `src/menu/menu.schemas.ts`:

```ts
const DISH_SORT_FIELDS = ["name", "priceNaira", "createdAt"] as const;
const DISH_FIELDS = ["id", "name", "priceNaira", "available", "portionsLeft"] as const;

const sortList = <F extends string>(allowed: readonly F[]) =>
  z
    .string()
    .max(100)
    .transform((value) => value.split(",").map((part) => part.trim()).filter(Boolean))
    .pipe(
      z.array(
        z.string().refine((part) => allowed.includes(part.replace(/^-/, "") as F), {
          message: `Sort by one of: ${allowed.join(", ")}`,
        }),
      ),
    )
    .transform((parts) =>
      parts.map((part) => ({
        field: part.replace(/^-/, "") as F,
        direction: part.startsWith("-") ? ("desc" as const) : ("asc" as const),
      })),
    );

const fieldList = <F extends string>(allowed: readonly F[]) =>
  z
    .string()
    .max(200)
    .transform((value) => value.split(",").map((part) => part.trim()).filter(Boolean))
    .pipe(z.array(z.enum(allowed as unknown as [F, ...F[]])));

export const ListMenuQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).max(10_000).default(1),
    limit: z.coerce.number().int().min(1).max(100).default(20),
    available: z.stringbool().optional(),
    minPrice: z.coerce.number().int().min(0).optional(),
    maxPrice: z.coerce.number().int().min(0).optional(),
    q: z.string().trim().min(1).max(50).optional(),
    sort: sortList(DISH_SORT_FIELDS).default([{ field: "name", direction: "asc" }]),
    fields: fieldList(DISH_FIELDS).optional(),
  })
  .refine((query) => query.minPrice === undefined || query.maxPrice === undefined || query.minPrice <= query.maxPrice, {
    message: "minPrice can't be more than maxPrice",
    path: ["minPrice"],
  });

export type ListMenuQuery = z.infer<typeof ListMenuQuerySchema>;
```

That looks like a lot, so take it piece by piece:

1. **`page` and `limit`** use `z.coerce.number()`, because `"2"` arrives as text. Both have a **maximum**. Without `max(100)`, someone sends `limit=1000000` and your server tries to build a million-item response. Limits are protection, not decoration.
2. **`.default(...)`** fills in a value when the parameter is missing. Most requests won't say `page=1`, and that's fine.
3. **`sortList`** turns `"priceNaira,-name"` into `[{ field: "priceNaira", direction: "asc" }, { field: "name", direction: "desc" }]`. Each field is checked against the **allow-list**. `sort=password` or `sort=1;DROP TABLE` is a 400, not a query.
4. **`fieldList`** turns `"id,name"` into `["id", "name"]`, also against an allow-list.
5. **The `refine`** catches `minPrice=3000&maxPrice=1000`, which can't match anything. Saying so is kinder than silently returning nothing.

Why build `sortList` and `fieldList` as functions? Because orders need the same thing with different allowed fields. Write the idea once, use it twice.

## Step 3: offset pagination for the menu
<!-- bite: 33efd493-9f6b-404a-94db-043fc0b78e74 -->

The repository's `list` grows from "everything" to "the page you asked for". `src/menu/menu.types.ts`:

```ts
export type MenuListOptions = Omit<ListMenuQuery, "fields">;
export type Page<T> = { items: T[]; total: number };

export type MenuRepository = {
  list(options: MenuListOptions): Promise<Page<Dish>>;
  // ...findById, create, update, remove as before
};
```

And in `menu.pg-repository.ts`, the query is built from parts:

```ts
const SORT_COLUMNS = {
  name: "name",
  priceNaira: "price_naira",
  createdAt: "created_at",
} as const;

function escapeLike(text: string) {
  return text.replace(/[\\%_]/g, (char) => "\\" + char);
}

async list(options) {
  const where: string[] = [];
  const values: unknown[] = [];
  const add = (value: unknown) => {
    values.push(value);
    return `$${values.length}`;
  };

  if (options.available !== undefined) where.push(`available = ${add(options.available)}`);
  if (options.minPrice !== undefined) where.push(`price_naira >= ${add(options.minPrice)}`);
  if (options.maxPrice !== undefined) where.push(`price_naira <= ${add(options.maxPrice)}`);
  if (options.q) where.push(`name ILIKE ${add(`%${escapeLike(options.q)}%`)}`);

  const whereSql = where.length ? `WHERE ${where.join(" AND ")}` : "";
  const orderSql = options.sort
    .map((s) => `${SORT_COLUMNS[s.field]} ${s.direction === "desc" ? "DESC" : "ASC"}`)
    .concat("id ASC")
    .join(", ");

  const limit = add(options.limit);
  const offset = add((options.page - 1) * options.limit);

  const { rows } = await pool.query<DishRow & { total: string }>(
    `SELECT *, count(*) OVER () AS total
       FROM dishes
       ${whereSql}
      ORDER BY ${orderSql}
      LIMIT ${limit} OFFSET ${offset}`,
    values,
  );

  return { items: rows.map(toDish), total: rows[0] ? Number(rows[0].total) : 0 };
},
```

This is the same safe pattern as `update` in lesson 8, grown up. Read it with the two rules in mind:

1. **Every value goes through `add()`**, which pushes it into `values` and gives back a placeholder like `$3`. The client's `maxPrice` or search text never touches the SQL text.
2. **Every column name comes from our own constant** (`SORT_COLUMNS`), looked up with a field that zod already checked against the allow-list. The client chooses *which of our words* to use, never the words themselves.

Three smaller things worth noticing:

1. **`ILIKE`** is Postgres's case-insensitive "contains". `%egusi%` matches "Pounded yam and egusi". But `%` and `_` are special inside `LIKE` (any text, any one character), so a search for `100%` would match far too much. `escapeLike` puts a backslash before them so they're treated as plain characters.
2. **`.concat("id ASC")`** adds a **tie-breaker**. If two dishes cost the same, Postgres may return them in any order, and a dish can then appear on page 1 *and* page 2, or on neither. Sorting by `id` last makes the order fully decided. Every paginated list needs a tie-breaker.
3. **`count(*) OVER ()`** returns the total number of matching rows on every row, in the same query, so we don't need a second `SELECT count(*)`. It's how we fill in `total` and `totalPages`.

The service passes it through, and the route builds `meta`:

```ts
// src/menu/menu.routes.ts
router.get("/", async (req, res) => {
  const { fields, ...options } = validate(ListMenuQuerySchema, req.query, "query");
  const page = await menuService.list(options);
  res.json({
    data: page.items.map((dish) => pick(dish, fields)),
    meta: {
      page: options.page,
      limit: options.limit,
      total: page.total,
      totalPages: Math.ceil(page.total / options.limit),
    },
  });
});
```

```bash
curl -s "http://localhost:3000/menu?maxPrice=2000&sort=priceNaira&limit=2"
curl -s "http://localhost:3000/menu?q=EGUSI"
curl -s "http://localhost:3000/menu?sort=password"     # 400, not a query
```

## Step 4: field selection
<!-- bite: 10f8e0e2-0e9e-49e1-91f1-d4dba70990d4 -->

`pick` is small, in `src/shared/pick.ts`:

```ts
export function pick<T extends { id: string }, K extends keyof T>(item: T, fields?: K[]) {
  if (!fields || fields.length === 0) return item;
  const result: Partial<T> = { id: item.id } as Partial<T>;
  for (const field of fields) result[field] = item[field];
  return result;
}
```

`GET /menu?fields=name,priceNaira` now answers `{ "id": "1", "name": "Jollof rice", "priceNaira": 1500 }` for each dish. We always keep `id`, because a client can't do much with an item it can't point back to.

Is this saving the database any work? No, we still read whole rows and drop fields at the end. For a dish with five small fields that's fine. The saving is in what travels over the network to a slow phone. If one field were huge (a long description, a photo), you'd also leave it out of the `SELECT`. And if clients choosing exactly the fields they want is the *main* thing your API does, that's GraphQL's whole idea, which we meet in [[backend/frameworks/express/21-graphql|lesson 21]].

## Step 5: where offset pagination breaks
<!-- bite: 65143391-f153-49ba-8312-7d35919f3892 -->

Now the kitchen screen. Try it with offset pagination in your head first.

The cook opens page 1 of pending orders, oldest first: orders 1–20. While she's cooking, order 7 is marked ready, so it's no longer pending. She taps "next": page 2 is "skip 20, take 20". But everything after order 7 moved up one place. Order 21 is now the 20th pending order, so it sits on page 1, which she's already seen. **Order 21 is skipped.** Nobody cooks it. A customer waits forever.

Turn it around: new orders keep arriving, and a list sorted newest first shifts *down*, so the same order appears on two pages. Either way, page numbers on a changing list lie.

There's a second, slower problem. `OFFSET 50000` makes Postgres read and throw away 50,000 rows to give you 20. The deeper you page, the slower it gets.

## Step 6: cursor pagination for orders
<!-- bite: d2e8b9bc-aee0-417d-9f33-e28f26462bc3 -->

The fix: instead of "skip 20", say "after the last one I saw".

The kitchen sorts by `created_at`, oldest first, with `id` as the tie-breaker. The bookmark is the `created_at` and `id` of the last order on the page. The next page is "orders that come after that pair":

```sql
SELECT * FROM orders
 WHERE status = $1
   AND (created_at, id) > ($2, $3)
 ORDER BY created_at ASC, id ASC
 LIMIT $4
```

`(created_at, id) > ($2, $3)` compares the pair, like comparing dates first, then the id when dates are equal. No skipping, no counting. Orders marked ready behind the bookmark don't move it. New orders arrive *after* it, so they'll show up when the cook gets there. And it's just as fast on page 5,000 as on page 1, with the right index.

The client shouldn't have to care what's inside the bookmark, so we pack it into one opaque piece of text. `src/shared/cursor.ts`:

```ts
import { z } from "zod";
import { AppError } from "./errors.ts";

const CursorSchema = z.object({ t: z.iso.datetime(), id: z.string().regex(/^\d+$/) });
export type Cursor = z.infer<typeof CursorSchema>;

export function encodeCursor(cursor: Cursor) {
  return Buffer.from(JSON.stringify(cursor)).toString("base64url");
}

export function decodeCursor(text: string): Cursor {
  try {
    return CursorSchema.parse(JSON.parse(Buffer.from(text, "base64url").toString("utf8")));
  } catch {
    throw new AppError("invalid", "bad-cursor", "The cursor is not valid. Start again from the first page.");
  }
}
```

A cursor is the JSON `{"t":"2026-11-21T12:00:00.000Z","id":"482"}` in **base64url**, a way of writing any data as letters, digits, `-` and `_` so it's safe in a URL. It isn't secret (anyone can decode it), but it's *opaque*: clients just pass it back. And because it's decoded with zod, a tampered cursor is a clean 400.

The orders query schema:

```ts
// src/orders/orders.schemas.ts
export const ListOrdersQuerySchema = z.object({
  status: z.enum(["pending", "ready", "collected"]).optional(),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  cursor: z.string().max(200).optional(),
});
```

The repository method, in `orders.pg-repository.ts`:

```ts
async listOldestFirst({ status, limit, after }) {
  const where: string[] = [];
  const values: unknown[] = [];
  const add = (value: unknown) => {
    values.push(value);
    return `$${values.length}`;
  };

  if (status) where.push(`status = ${add(status)}`);
  if (after) where.push(`(created_at, id) > (${add(after.t)}, ${add(after.id)})`);

  const { rows } = await pool.query<OrderRow>(
    `SELECT * FROM orders
      ${where.length ? `WHERE ${where.join(" AND ")}` : ""}
      ORDER BY created_at ASC, id ASC
      LIMIT ${add(limit + 1)}`,
    values,
  );

  const hasMore = rows.length > limit;
  const items = rows.slice(0, limit).map(toOrder);
  const last = items.at(-1);
  return { items, next: hasMore && last ? { t: last.createdAt, id: last.id } : null };
},
```

The trick in that last part: we ask for **one more** than the limit. If 21 rows come back for a limit of 20, we know there's another page without a second count query, we send back 20, and the 20th becomes the next bookmark. If 20 or fewer come back, this was the last page and `next` is `null`.

The route:

```ts
router.get("/", kitchenOnly, async (req, res) => {
  const query = validate(ListOrdersQuerySchema, req.query, "query");
  const page = await ordersService.listOldestFirst({
    status: query.status,
    limit: query.limit,
    after: query.cursor ? decodeCursor(query.cursor) : undefined,
  });
  res.json({
    data: page.items,
    meta: { limit: query.limit, nextCursor: page.next ? encodeCursor(page.next) : null },
  });
});
```

```bash
curl -s -H "X-Staff-Key: jollof123" "http://localhost:3000/orders?status=pending&limit=2"
# { "data": [ ...2 orders... ], "meta": { "limit": 2, "nextCursor": "eyJ0IjoiMjAy..." } }

curl -s -H "X-Staff-Key: jollof123" "http://localhost:3000/orders?status=pending&limit=2&cursor=eyJ0IjoiMjAy..."
```

There's no `total` and no "jump to page 9". That's the trade: cursors give you correct, fast "next, next, next", which is exactly what a kitchen screen or an infinite-scroll feed needs. Offset gives you "page 9 of 12", which suits a menu that rarely changes.

## Step 7: indexes, so it stays fast
<!-- bite: 0de72b61-64ae-40e4-95a6-4e0118881824 -->

A filter or sort with no index makes Postgres read the whole table. At 50 rows you won't notice. At 500,000 you will. `migrations/004_listing_indexes.sql`:

```sql
-- Store order times to the millisecond, so a cursor can hold them exactly (see below).
ALTER TABLE orders ALTER COLUMN created_at TYPE timestamptz(3);

CREATE INDEX orders_status_created_id_idx ON orders (status, created_at, id);
CREATE INDEX dishes_price_idx ON dishes (price_naira);
```

Why that `ALTER`? Here's a bug that would have bitten us. Postgres stores times to the **microsecond** (`12:00:00.123456`). A JavaScript `Date`, and so `toISOString()`, only keeps **milliseconds** (`12:00:00.123`). The bookmark would hold a time slightly *earlier* than the real row, so `(created_at, id) > (bookmark)` would be true for the last order of the page itself, and every page would start by repeating it. `timestamptz(3)` tells Postgres to keep only milliseconds, so the database and the cursor hold exactly the same value. A bookmark must be exact, or it isn't a bookmark.

The orders index matches the kitchen's query exactly: filter by `status`, then walk in `created_at, id` order from the bookmark. Postgres can jump straight to the bookmark and read the next 21 entries. [[databases/index|Databases]] explains how indexes work inside.

(The `ILIKE '%egusi%'` search can't use an ordinary index, because the match can start anywhere in the name. For a menu of 50 dishes that's fine. For a big catalogue you'd add Postgres's `pg_trgm` extension and a trigram index, or use full-text search. That's the moment to look it up, not before.)

## The TypeScript in this lesson
<!-- bite: 8c818588-4e45-4874-a7dd-33df303d5950 -->

1. **`as const` on an array**: `["name", "priceNaira", "createdAt"] as const` makes the type exactly those three words, read-only. That's what lets zod and `SORT_COLUMNS` agree on the allowed fields.
2. **`readonly F[]`**: An array type that can't be changed. Arrays made with `as const` are read-only, so a function that receives one must say `readonly`.
3. **`const sortList = <F extends string>(allowed: readonly F[]) => ...`**: A generic arrow function. `F` is "whichever words you allowed". Called with the dish fields, `F` is `"name" | "priceNaira" | "createdAt"`; with order fields, something else.
4. **`.transform(...)` and `.pipe(...)` in zod**: `transform` changes the value after it passes (text into a list). `pipe` sends the changed value into another schema to be checked again (the list into "array of allowed words"). Text in, clean list out.
5. **`.filter(Boolean)`**: Drops empty parts, so `"name,,price"` or a trailing comma doesn't create an empty field. `Boolean` used as a function returns false for empty text.
6. **`part.replace(/^-/, "")`**: Removes a `-` only at the very start (`^`), turning `"-name"` into `"name"`.
7. **`("desc" as const)`**: Makes TypeScript keep the exact word `"desc"` instead of widening it to `string`, so `direction` is typed `"asc" | "desc"`.
8. **`z.enum(allowed as unknown as [F, ...F[]])`**: `z.enum` wants a list with at least one item, typed as "first item, then any more". Our list is typed more loosely, so we tell TypeScript to treat it that way. `as unknown as` is a two-step assertion for when TypeScript won't accept one step. Use it rarely, and only where you can see it's true.
9. **`Omit<ListMenuQuery, "fields">`**: The menu query without `fields`, because field selection happens in the route, not in the database.
10. **`type Page<T> = { items: T[]; total: number }`**: A generic **type**. `Page<Dish>` is a page of dishes; `Page<Order>`, a page of orders. One shape, any item.
11. **`const { fields, ...options } = ...`**: Destructuring with **rest**: take `fields` out by name, and put everything else into `options`.
12. **`const add = (value: unknown) => { ...; return `$${values.length}`; }`**: A small closure that remembers `values` and hands back the next placeholder.
13. **`K extends keyof T`** in `pick`: `K` must be one of the field names of `T`, so `pick(dish, ["password"])` is a type error.
14. **`Buffer.from(...).toString("base64url")`**: `Buffer` is Node's type for raw bytes. Here: turn text into bytes, then the bytes into URL-safe base64.
15. **`catch { ... }` with no `(err)`**: When you don't need the error itself, you can leave the brackets out.
16. **`items.at(-1)`**: The last item of an array (`-1` counts from the end). It's `undefined` if the array is empty, which is why we check `last` before using it.
17. **`Math.ceil(37 / 20)`**: Rounds up, so 37 dishes at 20 per page is 2 pages, not 1.85.

## Your project so far
<!-- bite: 7be5812b-2966-4860-b6ae-77d8517a142e -->

```text
mama-put-api/
├── .env  ·  .env.example  ·  .gitignore  ·  package.json  ·  tsconfig.json
├── migrations/
│   ├── 001_create_dishes.sql
│   ├── 002_create_orders.sql
│   ├── 003_add_dish_description.sql   ← from lesson 8's practice
│   └── 004_listing_indexes.sql        ← NEW: millisecond order times, and indexes for the kitchen list and price filter
└── src/
    ├── server.ts  ·  app.ts
    ├── db/        pool.ts · transaction.ts · migrate.ts · seed.ts
    ├── menu/
    │   ├── menu.schemas.ts            ← ListMenuQuerySchema: page, limit, filters, q, sort, fields
    │   ├── menu.types.ts              ← MenuListOptions, Page<T>; list() takes options
    │   ├── menu.repository.ts         ← in-memory list() does the same filtering in plain code
    │   ├── menu.pg-repository.ts      ← list(): safe WHERE, ORDER BY with a tie-breaker, LIMIT/OFFSET, total
    │   ├── menu.service.ts
    │   └── menu.routes.ts             ← GET / returns { data, meta: { page, limit, total, totalPages } }
    ├── orders/
    │   ├── orders.schemas.ts          ← ListOrdersQuerySchema: status, limit, cursor
    │   ├── orders.types.ts            ← listOldestFirst() on OrdersRepository
    │   ├── orders.repository.ts
    │   ├── orders.pg-repository.ts    ← listOldestFirst(): keyset query, limit + 1
    │   ├── orders.service.ts
    │   ├── orders.service.test.ts
    │   └── orders.routes.ts           ← GET / (kitchen only) returns { data, meta: { nextCursor } }
    └── shared/
        ├── cursor.ts                  ← NEW: encodeCursor, decodeCursor
        ├── pick.ts                    ← NEW: field selection
        └── errors.ts · request-id.ts · validate.ts · log-requests.ts
            kitchen-only.ts · not-found.ts · error-handler.ts
```

(From here on, folders that didn't change are shown on one line.)

## Common mistakes
<!-- bite: c732b42d-89a3-4683-824a-bd554a7b6372 -->

1. **No maximum `limit`.** One request for a million rows can take the server down. Cap it.
2. **No tie-breaker in `ORDER BY`.** Items jump between pages. Always end with a unique column like `id`.
3. **Sort fields straight from the client.** `ORDER BY ${req.query.sort}` is SQL injection. Allow-list, then look up your own column name.
4. **Forgetting to escape `%` and `_` in searches.** The search works, just wrongly.
5. **Offset pagination on a list that changes all the time.** Items get skipped or repeated. Use a cursor.
6. **Cursors that leak or can be forged into something harmful.** Decode and validate them like any other input.
7. **A cursor less precise than the column.** Microseconds in the database, milliseconds in the cursor, and every page repeats its last item. Make them match.
8. **Filters with no index.** Fast on your laptop, slow in production. Add the index with the filter.
9. **A different list shape on each route.** Every list is `{ data, meta }`.

## Check your understanding
<!-- bite: 5db6ce8a-e842-4e28-9ebe-74bf0adb0308 -->

1. Why is `limit` capped at 100?
2. The menu is sorted by `priceNaira`, and three dishes cost ₦1,500. What can go wrong without `id ASC` at the end of the `ORDER BY`?
3. Why does the kitchen use a cursor and the menu use page numbers?
4. A client sends `sort=-price_naira`. What happens, and why is that good?
5. Why does `listOldestFirst` fetch `limit + 1` rows?

<details>
<summary>Answers, after your attempt</summary>

1. To protect the server and the database. Without a cap, a single request could ask for every row there is.
2. Postgres can return those three in a different order each time, so one may appear on two pages, or be skipped. `id` makes the order fully decided.
3. Orders change all the time (new ones arrive, old ones get marked ready), so page numbers would skip or repeat orders. A cursor marks a real position in the list. The menu rarely changes, and customers like seeing "page 2 of 3".
4. A 400, because the allow-list has `priceNaira`, not `price_naira`. The client only ever uses the API's names; the database's names stay hidden, and nothing it sends reaches the SQL as text.
5. To know if there's another page without running a count. If the extra row exists, there's more; we drop it and use the last kept order as the bookmark.

</details>

## Practice
<!-- bite: 58476ac4-0cd7-4634-be1b-524557176f3d -->

1. Give `GET /orders` a `sort` parameter that allows only `createdAt` and `-createdAt` (newest first for the "recent orders" screen). With `-createdAt`, the cursor condition must flip to `<`. Make both directions work.
2. Add `fields` to `GET /orders`, using the same `fieldList` helper.
3. Add a customer-facing filter `GET /menu?ids=1,3,7` that returns just those dishes (useful for showing a cart). Cap it at 50 ids.

**Done when** paging through pending orders newest first, while marking some of them ready in another terminal, never skips or repeats an order; `fields=id,status` works on orders; and `ids=1,abc` gets a 400.

## Before moving on
<!-- bite: 9527aa98-5a0e-4b37-bf29-b7dee9059265 -->

Mama Put's lists are now fast, safe and predictable: pages for the menu, bookmarks for the kitchen, and filters, search, sorting and field selection that the client controls but can never turn into SQL.

Now Mama has a new problem, and it's a happy one. Paystack works in **kobo**, not naira, and the phone app team wants prices as `{ amount, currency }` so they can show "₦1,500.00" properly. That changes the shape of every dish in every response. But last month's app, still on thousands of customers' phones, expects `priceNaira`. Change it, and their app breaks. Don't change it, and the new app can't move forward. That's what API versioning is for, and it's the next lesson.

## Related
<!-- bite: 42c417b5-1cfe-4ab3-9b90-9f514eb45eb4 -->

- [[backend/frameworks/express/10-versioning|Next: Versioning]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — designing resources and their query parameters
- [[databases/index|Databases]] — indexes, and why keyset pagination is fast

## About this lesson
<!-- bite: ef01c309-0a6a-4b8b-a8ad-53169ca30449 -->

**Level:** Intermediate. Lesson 9 of [[backend/frameworks/express/index|Express]]. Covers designing list query parameters, validating them with zod (coercion, defaults, maximums, allow-lists, `transform` and `pipe`), offset pagination with `count(*) OVER ()`, safe dynamic `WHERE` and `ORDER BY`, tie-breakers, `ILIKE` search with escaping, field selection, why offset breaks on changing lists, cursor (keyset) pagination with opaque base64url cursors and the `limit + 1` trick, and indexes for both.
