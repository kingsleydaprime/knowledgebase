---
id: c54ec047-409f-4f79-8b03-a3f65ae9e495
---

# Testing

**A test is a small program that runs a piece of your code with known inputs and checks the result, so the computer, not you, does the "did I break anything?" checking, every time you change something.** For fifteen lessons we've checked Mama Put API by hand with `curl`. This lesson turns those checks into tests that run in seconds, so you can change code without being afraid of it.

## Before you start
<!-- bite: 44cbc077-29e6-445f-a7b4-400500a21e36 -->

You should have idempotent orders from [[backend/frameworks/express/15-idempotency|lesson 15]]. You've already written one test, in [[backend/frameworks/express/05-wiring-dependencies|lesson 5]], with a fake menu.

After this lesson you will be able to:

1. Choose the right kind of test for each thing: unit, HTTP, integration, and contract.
2. Test the whole Express app, middleware and all, without starting a server or opening a port.
3. Test the Postgres repositories against a real throwaway database, including the race conditions from lessons 8 and 15.
4. Check that real responses match the documented schemas.
5. Organise tests so they're fast, independent and trustworthy.

## Where we stopped
<!-- bite: 279118ce-a094-460c-81b1-9628a83e5501 -->

Count the `curl` checks from the last fifteen lessons: wrong passwords, refresh token reuse, Ada reading Bayo's order, the last plate, 20 orders for 5 portions, replayed idempotency keys, too-big photos, deprecated v1 headers. Easily a hundred.

Tomorrow you change one line in the auth service. Which of those hundred checks might it break? You don't know, so either you run them all by hand (you won't), or you ship and hope. Tests end that choice.

## The kid version
<!-- bite: 09344448-5d4b-40f0-b7ae-bcf6787147cc -->

Before Mama Put opens each morning, Mama tastes every pot. Not a whole plate, just a spoon from each. If the stew is too salty, she finds out now, not from a customer at lunch.

Tests are those spoons. A quick taste of every important thing, every time anything changes, before customers find the problem.

**Where the picture stops working.** Mama tastes what she cooked today. Tests also taste what you cooked *last month*: every old bug you fixed gets a test, so it can never quietly come back.

## Terms used in testing
<!-- bite: 808d1f72-c5ce-494a-a3c2-3e28946462b1 -->

1. **Unit test**: This tests one small piece, like the orders service, on its own, with fakes standing in for what it depends on. It runs in milliseconds.
2. **HTTP test**: This sends real requests through the whole Express app (routing, middleware, validation, error handling) but with in-memory repositories. Ours use **supertest**, which calls the app directly, with no port.
3. **Integration test**: This tests our code together with a real outside system, here a real Postgres database.
4. **Contract test**: This checks that what we send matches what we promised: our responses against our documented schemas.
5. **Fixture**: This is the data a test starts from, like "a dish with 1 portion left and a customer called Ada".
6. **Flaky test**: This is a test that sometimes passes and sometimes fails with no code change. Flaky tests are worse than no tests, because people learn to ignore failures.

## Step 1: which tests, how many
<!-- bite: 72cd8023-e423-47d9-9c61-c8d91fd59b2c -->

Different tests catch different bugs, at different costs:

| Kind | Example | Speed | Catches |
|---|---|---|---|
| Unit | "21 plates is `too-many-plates`" | ~1 ms | wrong business rules |
| HTTP | "`POST /v2/orders` without a token is 401 with the problem shape" | ~5 ms | wrong routes, middleware order, status codes, response shapes |
| Integration | "20 parallel orders for 5 portions give exactly 5" | ~50 ms | wrong SQL, missing constraints, races |
| Contract | "every dish in `GET /v2/menu` matches `DishV2Schema`" | ~5 ms | docs and code drifting apart |

Write **many** unit and HTTP tests, because they're fast and pinpoint the problem. Write **fewer** integration tests, for the things only a real database can show: SQL, constraints, transactions and races. That's the usual shape, sometimes drawn as a pyramid: lots at the bottom, fewer at the top.

## Step 2: the test runner
<!-- bite: fe41f2db-740c-43be-b9b7-fc8974dd99f3 -->

We use Node's built-in test runner, `node:test`. No extra packages to install for it, and it runs our `.ts` files directly, like everything else.

```bash
npm install --save-dev supertest @types/supertest
```

In `package.json`:

```json
"scripts": {
  "test": "node --test \"src/**/*.test.ts\"",
  "test:integration": "node --env-file=.env.test --test --test-concurrency=1 \"test/integration/**/*.test.ts\"",
  "test:watch": "node --test --watch \"src/**/*.test.ts\""
}
```

1. **`npm test`** runs the fast tests: unit, HTTP and contract. They need nothing running.
2. **`npm run test:integration`** runs the database tests, one file at a time (`--test-concurrency=1`), because they share one database.
3. **`--watch`** reruns the tests every time you save.

Tests live next to the file they test (`orders.service.test.ts` beside `orders.service.ts`), except the integration tests, which get their own `test/integration/` folder because they need a database.

## Step 3: unit tests for the rules
<!-- bite: e7282cb9-4b7d-444b-80d9-3570a3424bc9 -->

You wrote one in lesson 5. Here's the orders service properly, using the in-memory repositories (which is why we kept them):

```ts
// src/orders/orders.service.test.ts
import { describe, it, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { createOrdersService } from "./orders.service.ts";
import { createInMemoryOrdersRepository } from "./orders.repository.ts";
import { createInMemoryMenuRepository } from "../menu/menu.repository.ts";
import { createMenuService } from "../menu/menu.service.ts";
import type { AuthUser } from "../auth/auth.types.ts";

const ada: AuthUser = { id: "1", role: "customer" };
const bayo: AuthUser = { id: "2", role: "customer" };
const cook: AuthUser = { id: "3", role: "staff" };

describe("orders service", () => {
  let orders: ReturnType<typeof createOrdersService>;

  beforeEach(() => {
    const menuRepository = createInMemoryMenuRepository([
      { id: "1", name: "Jollof rice", priceKobo: 150000, available: true, portionsLeft: 3 },
      { id: "2", name: "Egusi", priceKobo: 250000, available: false, portionsLeft: 0 },
    ]);
    const menuService = createMenuService({ menuRepository });
    orders = createOrdersService({
      ordersRepository: createInMemoryOrdersRepository(menuRepository),
      menuService,
    });
  });

  it("charges price × quantity", async () => {
    const order = await orders.place(ada, "1", 2);
    assert.equal(order.totalKobo, 300000);
  });

  it("refuses more than 20 plates", async () => {
    await assert.rejects(orders.place(ada, "1", 21), { code: "too-many-plates" });
  });

  it("refuses a finished dish", async () => {
    await assert.rejects(orders.place(ada, "2", 1), { code: "dish-unavailable" });
  });

  it("refuses when there aren't enough portions", async () => {
    await assert.rejects(orders.place(ada, "1", 4), { code: "not-enough-portions" });
  });

  it("hides other customers' orders as not found", async () => {
    const bayos = await orders.place(bayo, "1", 1);
    await assert.rejects(orders.get(ada, bayos.id), { code: "order-not-found" });
    assert.equal((await orders.get(cook, bayos.id)).id, bayos.id);
  });
});
```

Look at the shape every test has:

1. **Arrange**: `beforeEach` builds a fresh menu and service for **every** test, so no test can leave dishes or orders behind for the next one. Tests that depend on each other's leftovers are the biggest cause of flaky tests.
2. **Act**: one call, like `orders.place(ada, "1", 21)`.
3. **Assert**: check the result, here with `assert.rejects(..., { code })`, which passes only if the promise fails with an error whose `code` matches.

The test names read as the rules: "charges price × quantity", "refuses more than 20 plates". A failing test tells you which rule broke, in words.

## Step 4: HTTP tests, through the whole app
<!-- bite: 48dcf7a7-3b54-4e4f-8eda-c3bfc0f38884 -->

Unit tests can't see a mistake like "the error handler is above the routes" or "POST /orders forgot `requireUser`". For that, send real requests through the real app.

This is where lesson 4's `app.ts` / `server.ts` split and lesson 5's `createApp(deps)` pay off. A test can build the whole app with in-memory pieces:

```ts
// src/test-support/test-app.ts
import { createApp } from "../app.ts";
import { createAccessTokens } from "../auth/tokens.ts";
import type { PasswordHasher } from "../auth/password.ts";
// ...the in-memory repositories and the factories

export const fastHasher: PasswordHasher = {
  hash: async (password) => `plain:${password}`,
  verify: async (hash, password) => hash === `plain:${password}`,
};

export async function buildTestApp() {
  const accessTokens = createAccessTokens("test-secret-that-is-long-enough-for-hs256");
  const users = createInMemoryUsersRepository();
  // ...build every repository and service exactly like server.ts, but in memory
  const app = createApp({ /* all the deps */ });

  async function login(role: "customer" | "staff" | "admin" = "customer") {
    const user = await users.create({ email: `${role}-${users.size()}@test.example`, name: role, passwordHash: "x" });
    await users.updateRole(user.id, role);
    return { user, token: await accessTokens.sign({ id: user.id, role }) };
  }

  return { app, login, users };
}
```

Two shortcuts make these tests fast and focused. The **fast hasher** skips argon2 (which is slow on purpose; 50 ms per hash adds up over hundreds of tests). And **`login`** signs a token directly instead of going through `/auth/login`. The auth routes have their own tests; every other test just needs "a logged-in customer".

The fast hasher is fine *because* it's only ever built in test files. The composition root in `server.ts` is the only place that picks the real one.

Now, real requests:

```ts
// src/orders/orders.routes.test.ts
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import request from "supertest";
import { buildTestApp } from "../test-support/test-app.ts";

describe("POST /v2/orders", () => {
  it("needs a login", async () => {
    const { app } = await buildTestApp();
    const res = await request(app)
      .post("/v2/orders")
      .set("Idempotency-Key", "test-key-0001")
      .send({ dishId: "1", quantity: 1 });

    assert.equal(res.status, 401);
    assert.equal(res.body.code, "login-required");
    assert.match(res.headers["content-type"], /application\/problem\+json/);
    assert.ok(res.headers["www-authenticate"]);
  });

  it("places an order and replays it for the same key", async () => {
    const { app, login } = await buildTestApp();
    const { token } = await login();
    const send = () =>
      request(app)
        .post("/v2/orders")
        .set("Authorization", `Bearer ${token}`)
        .set("Idempotency-Key", "test-key-0002")
        .send({ dishId: "1", quantity: 2 });

    const first = await send();
    const second = await send();

    assert.equal(first.status, 201);
    assert.equal(second.status, 201);
    assert.equal(second.headers["idempotent-replayed"], "true");
    assert.equal(second.body.data.id, first.body.data.id);
  });

  it("lists every problem in a bad body", async () => {
    const { app, login } = await buildTestApp();
    const { token } = await login();
    const res = await request(app)
      .post("/v2/orders")
      .set("Authorization", `Bearer ${token}`)
      .set("Idempotency-Key", "test-key-0003")
      .send({ quantity: "two" });

    assert.equal(res.status, 400);
    assert.deepEqual(res.body.errors.map((e: { path: string }) => e.path).sort(), ["dishId", "quantity"]);
  });
});
```

`request(app)` hands each request straight to the Express app in memory. Nothing listens on a port, so tests never fight over port 3000 and run in parallel safely.

(The idempotency store needs an in-memory version for these tests too. It's a `Map` with the same three methods; write it in the practice.)

## Step 5: a table of permissions
<!-- bite: fd743109-081f-48ec-a975-85d6c17fb44a -->

Authorization has many combinations (three roles, many actions) and they're easy to get wrong in one corner. Write them as a table, and let one loop test them all:

```ts
// src/auth/permissions.routes.test.ts
const cases = [
  { role: "customer", method: "post",   path: "/v2/menu",   status: 403 },
  { role: "staff",    method: "post",   path: "/v2/menu",   status: 201 },
  { role: "customer", method: "delete", path: "/v2/menu/1", status: 403 },
  { role: "staff",    method: "patch",  path: "/v2/orders/1/status", status: 200 },
  { role: "customer", method: "patch",  path: "/v2/orders/1/status", status: 403 },
  { role: "staff",    method: "patch",  path: "/v2/admin/users/1/role", status: 403 },
  { role: "admin",    method: "patch",  path: "/v2/admin/users/1/role", status: 200 },
] as const;

for (const c of cases) {
  it(`${c.role} ${c.method.toUpperCase()} ${c.path} → ${c.status}`, async () => {
    const { app, login, seed } = await buildTestApp();
    await seed.anOrder();
    const { token } = await login(c.role);
    const res = await request(app)[c.method](c.path)
      .set("Authorization", `Bearer ${token}`)
      .send(validBodyFor(c.path));
    assert.equal(res.status, c.status);
  });
}
```

Each row becomes its own test, with a readable name like `customer DELETE /v2/menu/1 → 403`. The table *is* the policy from lesson 13, checked against the running app. Add a route, add a row. (`validBodyFor` returns a sensible body for each path, so the test checks permission, not validation.)

## Step 6: contract tests against the documented schemas
<!-- bite: dd28fc5f-dbc5-4cd4-971f-23359505b4c2 -->

Lesson 11 generated our docs from zod schemas. So the simplest way to test "does the API match its docs?" is to check real responses against those same schemas:

```ts
import { DishV2Schema } from "../menu/menu.versions.ts";
import { z } from "zod";

it("GET /v2/menu matches the documented shape", async () => {
  const { app } = await buildTestApp();
  const res = await request(app).get("/v2/menu?limit=5");
  assert.equal(res.status, 200);
  z.array(DishV2Schema.strict()).parse(res.body.data);
  assert.equal(typeof res.body.meta.total, "number");
});
```

`.strict()` makes the check fail if the response has **extra** fields the docs don't mention, not just missing ones. That catches the quiet leak where a new column (say, an internal note) starts appearing in every response because someone spread a whole row into a presenter.

## Step 7: integration tests on a real database
<!-- bite: bd7b7c8e-6dda-4b3a-b54c-ae4c3f1a20fe -->

Some bugs only exist in SQL: a typo in a column name, a missing constraint, a race. For those, nothing replaces a real Postgres.

Make a separate test database, so tests can't touch your development data:

```bash
docker exec -it mama-put-db createdb -U postgres mama_put_test
```

`.env.test`:

```text
DATABASE_URL=postgres://postgres:mamaput@localhost:5432/mama_put_test
```

A helper prepares it, `test/integration/db.ts`:

```ts
import pg from "pg";
import { execFileSync } from "node:child_process";

export const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

export function migrate() {
  execFileSync("node", ["--env-file=.env.test", "src/db/migrate.ts"], { stdio: "inherit" });
}

export async function resetData() {
  await pool.query(
    "TRUNCATE idempotency_keys, refresh_tokens, orders, users, dishes RESTART IDENTITY CASCADE",
  );
}
```

`TRUNCATE ... RESTART IDENTITY` empties the tables and resets the ids to 1, so every test starts from the same clean state. (It's also why `.env.test` must point at the *test* database. Run this against your real one and the data is gone. Some teams add a check that refuses to run unless the database name ends in `_test`. Do it.)

Now the test that matters most, the last plate from lesson 8:

```ts
// test/integration/orders.race.test.ts
import { describe, it, before, beforeEach, after } from "node:test";
import assert from "node:assert/strict";
import { pool, migrate, resetData } from "./db.ts";
import { createPgOrdersRepository } from "../../src/orders/orders.pg-repository.ts";

describe("placing orders against Postgres", () => {
  before(migrate);
  beforeEach(resetData);
  after(() => pool.end());

  it("sells exactly 5 plates when 20 customers race for 5 portions", async () => {
    await pool.query(
      "INSERT INTO dishes (name, price_kobo, portions_left) VALUES ('Jollof rice', 150000, 5)",
    );
    await pool.query(
      "INSERT INTO users (email, name, password_hash) VALUES ('ada@test.example', 'Ada', 'x')",
    );
    const orders = createPgOrdersRepository(pool);

    const results = await Promise.all(
      Array.from({ length: 20 }, (_, i) => orders.placeTakingPortions("1", 1, "1", `race-${i}`)),
    );

    const placed = results.filter((order) => order !== null);
    assert.equal(placed.length, 5);
    const { rows } = await pool.query("SELECT portions_left FROM dishes WHERE id = 1");
    assert.equal(rows[0].portions_left, 0);
  });
});
```

`Promise.all` starts all 20 at once, so they really do race inside Postgres. If anyone ever "simplifies" `placeTakingPortions` back into "read, check, then update", this test fails. That's what tests are for: they remember *why* the code looks the way it does, after everyone has forgotten.

A neat extra: write one set of tests for "what a menu repository must do", and run it against **both** the in-memory and the Postgres repository. Then the in-memory one, which all the fast tests rely on, can never quietly behave differently from the real one.

## Step 8: what makes tests trustworthy
<!-- bite: bc578a74-15d4-489c-b204-a38a1e73b407 -->

1. **Independent.** Every test builds its own state. Run them in any order, or one alone, and they pass the same.
2. **Deterministic.** No real clocks, no randomness you can't control. For "refresh tokens expire after 30 days", don't wait 30 days: `node:test` can fake time with `mock.timers`, or let the code take a "now" function as a dependency.
3. **Testing behaviour, not wiring.** "Placing 21 plates is refused" survives a refactor. "The service called `findById` exactly once" breaks every time you tidy the code, while the behaviour stays the same.
4. **One reason to fail.** A test that checks ten things tells you less when it fails than ten small tests.
5. **A test for every bug.** When something breaks in production, first write the test that fails *because* of the bug, then fix it. That bug can never come back silently.

How much is enough? Don't chase a coverage number. `node --test --experimental-test-coverage` shows which lines never ran; look at the list and ask "is any of this a rule or a security check?". An untested error branch in the auth service matters far more than an untested log line.

## The TypeScript in this lesson
<!-- bite: 9d38551c-1f0c-40f5-8c66-fb65de61f411 -->

1. **`import { describe, it, beforeEach } from "node:test"`**: `describe` groups tests under a name, `it` is one test, and `beforeEach` runs before every test in its group. `before` and `after` run once, around the whole group.
2. **`import assert from "node:assert/strict"`**: Node's checking functions. `assert.equal(a, b)` checks `a === b`; `assert.deepEqual` compares contents; `assert.match` checks text against a pattern; `assert.ok` checks something is truthy; `assert.rejects` checks a promise fails.
3. **`let orders: ReturnType<typeof createOrdersService>`**: Declared without a value, then assigned fresh in `beforeEach`. The type is worked out from the factory.
4. **`request(app)[c.method](c.path)`**: `c.method` is `"post"`, `"patch"` or `"delete"`, and `request(app)` has a method for each. Square brackets call the method whose name is in the variable.
5. **`as const` on the `cases` array**: Keeps each `role` and `method` as its exact word instead of `string`, so `login(c.role)` and `[c.method]` type-check.
6. **`` it(`${c.role} ${c.method.toUpperCase()} ...`) ``**: Test names can be built with template strings, so each generated test has a clear name.
7. **`res.body.errors.map((e: { path: string }) => e.path)`**: `res.body` is `any` in supertest, so we say what each error looks like where we use it.
8. **`Array.from({ length: 20 }, (_, i) => ...)`**: Makes an array of 20 items by calling the function with each index. `_` is a common name for a parameter you don't use.
9. **`Promise.all([...])`**: Starts every promise at once and waits until all of them finish, giving their results in order.
10. **`results.filter((order) => order !== null)`**: Keeps the successful orders. (TypeScript 5.5 and later understands that the result has no `null`s in it.)
11. **`execFileSync("node", [...], { stdio: "inherit" })`**: Runs another program and waits for it, showing its output. Here, our own migration runner, against the test database.

## Your project so far
<!-- bite: 304aac39-ac1a-478d-8aa0-1c79d8d01e7c -->

```text
mama-put-api/
├── .env · .env.example · .gitignore · tsconfig.json
├── .env.test                     ← NEW: points at mama_put_test (never your real database)
├── package.json                  ← supertest; test, test:integration, test:watch scripts
├── migrations/   001 … 010
├── uploads/photos/ · openapi/
├── test/
│   └── integration/
│       ├── db.ts                 ← NEW: pool, migrate(), resetData() with TRUNCATE
│       ├── orders.race.test.ts   ← NEW: 20 customers, 5 portions, exactly 5 orders
│       └── repositories.test.ts  ← NEW: the same repository tests, run on in-memory and Postgres
└── src/
    ├── test-support/
    │   └── test-app.ts           ← NEW: buildTestApp(), fastHasher, login(role), seed helpers
    ├── auth/
    │   ├── auth.routes.test.ts   ← NEW: signup, wrong password, refresh reuse
    │   └── permissions.routes.test.ts ← NEW: the role × route table
    ├── menu/
    │   └── menu.routes.test.ts   ← NEW: listing, contract test against DishV2Schema
    ├── orders/
    │   ├── orders.service.test.ts ← the rules (from lesson 5, grown up)
    │   └── orders.routes.test.ts ← NEW: 401, idempotent replay, every problem listed
    ├── shared/
    │   └── idempotency.memory-store.ts ← NEW: the Map-based store for tests
    └── server.ts · app.ts · api.ts · types/ · admin/ · docs/ · db/
```

## Common mistakes
<!-- bite: 12f99a10-d43b-403b-9fe0-a38880196b82 -->

1. **Tests that share state.** One test's leftover dish makes another pass or fail. Fresh state for every test.
2. **Integration tests against your development database.** `TRUNCATE` will empty it. Use a separate `_test` database, and check the name.
3. **Real argon2 in every HTTP test.** Hundreds of tests at 50 ms each. Use the fast hasher in tests, and test the real one once.
4. **Testing how, not what.** Checking which functions were called breaks on every refactor. Check what the caller sees.
5. **Only the happy path.** Most bugs live in errors and edge cases: the 401, the 404 for someone else's order, the 21st plate.
6. **Ignoring a flaky test.** Find out why it's flaky. It's often a real race in your code.
7. **No test for a bug you fixed.** Then it comes back.

## Check your understanding
<!-- bite: 98839f85-aed6-4a72-a75a-1aa82f40d009 -->

1. Which kind of test would catch each? (a) The error handler was moved above the routes. (b) The 20-plate limit was changed to 2,000 by mistake. (c) `placeTakingPortions` was rewritten as "read, check, update". (d) A presenter started sending `password_hash`.
2. Why does `buildTestApp` sign tokens directly instead of calling `/auth/login`?
3. Why do the integration tests run one file at a time, but the HTTP tests can run in parallel?
4. What does `.strict()` add to the contract test?

<details>
<summary>Answers, after your attempt</summary>

1. (a) An HTTP test: errors would come back in the wrong shape. (b) A unit test of the orders service. (c) The integration race test: it only fails with real concurrent transactions. (d) A contract test with `.strict()`, which fails on fields the schema doesn't list.
2. Because the auth routes have their own tests. Every other test just needs a logged-in user; going through login each time would be slower and would make every test fail when login breaks, hiding where the real problem is.
3. The integration tests share one real database and empty it between tests, so two running at once would wipe each other's data. HTTP tests each build their own in-memory app, so nothing is shared.
4. It fails on *extra* fields, not just missing or wrong ones. That catches internal data leaking into responses.

</details>

## Practice
<!-- bite: 63063017-16c8-4ed2-b0c8-cfef15a4991c -->

1. Write the in-memory idempotency store (a `Map` keyed by `` `${userId}:${key}` ``) and make the idempotent-replay HTTP test pass.
2. Add rows to the permissions table for every route you have, including the photo upload and order cancel.
3. Write an integration test for refresh-token reuse: use a refresh token twice, in parallel, and check that exactly one succeeds and that afterwards *no* refresh token for that user works.
4. Break something on purpose (swap `>` for `>=` in the 20-plate rule) and check exactly one test fails, with a name that tells you what's wrong. Then put it back.

**Done when** `npm test` passes in a few seconds with no database running, `npm run test:integration` passes against `mama_put_test`, and every `curl` check from lessons 6 to 15 has a test that would catch it breaking.

## Before moving on
<!-- bite: bd155695-469d-4a24-a60c-1aa4833fdcf9 -->

Mama Put API is now tested at every level: the rules, every route through the real middleware, the permissions table, the documented shapes, and the races, on a real database.

Which means we can finally build the scary things with confidence. And the scariest is money. So far, "placing an order" just writes a row. Mama wants to be *paid*. That means talking to Paystack: sending customers to pay, and then believing Paystack, and only Paystack, when it calls *us* back to say "Ada paid ₦3,000". That's payments and webhooks, the next lesson.

## Related
<!-- bite: 07fca867-5dc1-49a2-b59f-49e97dd6c800 -->

- [[backend/frameworks/express/17-payments-and-webhooks|Next: Payments and Webhooks]]
- [[backend/07-practices/02-testing-a-backend|Testing a Backend]] — the idea in any framework
- [[backend/07-practices/03-load-and-performance-testing|Load and Performance Testing]] — the tests that ask "how many customers before it falls over?"

## About this lesson
<!-- bite: dc2b53e1-2801-4efc-b924-1ec6d4ffd170 -->

**Level:** Intermediate → Advanced. Lesson 16 of [[backend/frameworks/express/index|Express]]. Covers unit, HTTP, integration and contract tests and how many of each, `node:test` with `describe`, `it`, hooks and `assert`, arrange-act-assert, a `buildTestApp` built from in-memory dependencies with a fast hasher and signed test tokens, supertest without a port, table-driven permission tests, contract tests with strict zod schemas, integration tests on a separate Postgres database with `TRUNCATE … RESTART IDENTITY`, testing a real race with `Promise.all`, shared repository tests for both implementations, and what makes tests independent, deterministic and worth keeping.
