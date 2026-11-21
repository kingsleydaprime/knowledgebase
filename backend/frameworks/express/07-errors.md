---
id: dca2774a-0026-4255-ba21-e60e75e1360b
---

# Errors and Structured Responses

**A structured response means every answer your API gives, good or bad, has the same predictable shape, so a client can handle all of them with one piece of code.** Error handling is the part of that for bad answers: deciding what each problem is called, which status it gets, what the client is told, and what *only you* get to see in the logs.

## Before you start
<!-- bite: 03f4758a-ab9c-4e11-b748-eea2f0098e29 -->

You should have validation from [[backend/frameworks/express/06-validation|lesson 6]]: zod schemas, the `validate` helper, and `ValidationError` answered as 400 in the error handler.

After this lesson you will be able to:

1. Design one response shape for success and one for errors, and use them everywhere.
2. Replace "result objects" in services with error classes that say what went wrong in business words.
3. Write one error handler that turns every kind of failure into the right status and shape.
4. Make sure an unexpected crash never shows a stack trace to the client, while you can still find it in your logs.

## Where we stopped
<!-- bite: 4251fac8-78bc-4c87-8211-93002dbe64c1 -->

Lesson 6 ended with this list of how our app answers when something goes wrong:

| Situation | What the client gets now |
|---|---|
| bad input | `400 { error, issues }` |
| dish missing | `404 { error: "Dish not found" }` |
| dish finished | `422 { error: "dish-unavailable" }` |
| no route | `404 { error: "Not found" }` |
| our bug | `500 { error: "Something went wrong" }` |
| broken JSON body | Express's own HTML error page |

And success is a bare array here, a bare object there. Put yourself in the shoes of the person building Mama Put's phone app. For every request they must guess which shape is coming back. That's how bugs are born in the app, not in the API.

Then look inside `orders.routes.ts`:

```ts
const result = await ordersService.place(input.dishId, input.quantity);
if (!result.ok) {
  const status = result.reason === "dish-not-found" ? 404 : 422;
  res.status(status).json({ error: result.reason });
  return;
}
```

Every route that calls a service has to unpack a result and pick a status. Forget one `if`, and a failure is sent as success.

## The kid version
<!-- bite: a749703c-494b-46f7-9c1c-859b02ba2341 -->

When a customer's order can't be served, Mama's helpers used to each say it their own way. One says "e don finish". Another just shakes her head. Another writes "NO" on a paper. Customers got confused.

So Mama made a rule: every problem is told the same way. "Sorry, [what happened]. [What you can do]." And she keeps a notebook behind the counter where she writes the full story ("the gas finished at 2pm because the cylinder was faulty"), which the customer never needs to hear.

The same rule for the API: one polite shape for the client, the full details in your logs.

**Where the picture stops working.** Mama can see the customer's face and explain more if they look lost. An API can't, so the shape must carry enough for a program to decide what to do, like a code it can check, not just words for a human.

## Terms used in error handling
<!-- bite: 2edb7020-0cb0-40cb-935c-630cc751bd15 -->

1. **Response envelope**: This is a fixed outer shape that wraps every successful answer, like `{ "data": ... }`. The real content always sits in the same place, and there's room next to it for extras such as paging information (`meta`), which we need in lesson 9.
2. **Problem details**: This is a standard shape for error answers, written down in an internet standard called RFC 9457. It has fields like `type`, `title`, `status` and `detail`, and its own content type, `application/problem+json`. Using a standard means clients and tools already know how to read it.
3. **Operational error**: This is a failure you expected could happen: bad input, a missing dish, a finished pot. It's part of normal life, and the client should be told clearly.
4. **Programmer error**: This is also called a **bug**. It's a failure you didn't expect: a typo, a `null` you forgot about, a database that's down. The client gets a plain 500 and an ID; you get the full details in the log.
5. **Stack trace**: This is the list of function calls that were running when an error happened. It's gold for you when debugging, and it must never reach a client, because it shows the inside of your code to anyone who asks.
6. **Request ID**: This is a unique label given to each request. Put it in the error answer and in your log, and when a customer says "it failed", you can find exactly what happened.

## Step 1: choose the shapes
<!-- bite: 7d14b13d-b5f6-4cad-967d-a53aeed9cdd2 -->

**Success** always looks like this:

```json
{ "data": { "id": "1", "name": "Jollof rice", "priceNaira": 1500, "available": true } }
```

and lists look like this, with room for extras:

```json
{ "data": [ { "id": "1", "...": "..." } ], "meta": { "count": 2 } }
```

**Errors** follow problem details:

```json
{
  "type": "https://mamaput.example/problems/dish-unavailable",
  "title": "Dish unavailable",
  "status": 422,
  "detail": "Pounded yam and egusi is finished for today.",
  "code": "dish-unavailable",
  "requestId": "6f1c2e3a-0b4d-4c8e-9a7f-2d5e6b8c1a90"
}
```

1. `type` is a link that names the kind of problem. It doesn't have to be a real page, but it can be one later, with docs.
2. `title` is short and the same for every problem of that kind.
3. `status` repeats the HTTP status, so the body makes sense on its own (in a log, say).
4. `detail` is the human explanation for *this* case.
5. `code` is our own extra field, a short word a program can check with `if (problem.code === "dish-unavailable")`. The standard allows extra fields like this.
6. `requestId` is our other extra, so support can find the log line.

Validation errors add one more field, `errors`, with the list of issues from lesson 6.

Is an envelope the only right way? No. Many good APIs send bare objects for success and only use a standard shape for errors. We choose the envelope because it gives us a fixed place for `meta` when we paginate, and because "it's always in `data`" is one less thing for the app developer to remember. Whichever you choose, the rule is the same: **choose once, and never mix**.

## Step 2: one error class, in business words
<!-- bite: a6d3a0d2-1dff-4a9d-aa74-bd09969ccfb8 -->

`src/shared/errors.ts`:

```ts
export type ErrorKind =
  | "invalid"          // the request is malformed
  | "unauthenticated"  // we don't know who you are
  | "forbidden"        // we know who you are, and the answer is no
  | "not_found"        // the thing doesn't exist
  | "conflict"         // it clashes with the current state
  | "rule_broken";     // it breaks a business rule

export class AppError extends Error {
  kind: ErrorKind;
  code: string;
  details?: unknown;

  constructor(kind: ErrorKind, code: string, message: string, details?: unknown) {
    super(message);
    this.name = "AppError";
    this.kind = kind;
    this.code = code;
    this.details = details;
  }
}

export const notFound = (what: string, id: string) =>
  new AppError("not_found", `${what.toLowerCase()}-not-found`, `${what} ${id} was not found.`);

export const ruleBroken = (code: string, message: string) =>
  new AppError("rule_broken", code, message);

export const conflict = (code: string, message: string) =>
  new AppError("conflict", code, message);
```

Notice what's missing: **status codes**. A service will throw `ruleBroken("dish-unavailable", ...)`, which is business language. It has no idea that this means 422 over HTTP. The error handler does that translation, in one place. This keeps the rule from [[backend/frameworks/express/04-structuring-an-express-app|lesson 4]]: services don't know about HTTP.

And `ValidationError` from lesson 6 becomes just one more kind of `AppError`:

```ts
// src/shared/validate.ts
import { AppError } from "./errors.ts";

export class ValidationError extends AppError {
  constructor(issues: InputIssue[]) {
    super("invalid", "invalid-request", "The request is not valid.", issues);
    this.name = "ValidationError";
  }
}
```

## Step 3: services throw instead of returning results
<!-- bite: fa5d4233-8d59-41bb-b7b8-56e08ca44659 -->

`orders.service.ts` gets shorter and clearer:

```ts
import { notFound, ruleBroken } from "../shared/errors.ts";

export function createOrdersService(deps: { ordersRepository: OrdersRepository; menuService: MenuService }) {
  const { ordersRepository, menuService } = deps;
  return {
    async place(dishId: string, quantity: number): Promise<Order> {
      if (quantity > 20) {
        throw ruleBroken("too-many-plates", "You can order at most 20 plates at once.");
      }
      const dish = await menuService.get(dishId);
      if (!dish) throw notFound("Dish", dishId);
      if (!dish.available) {
        throw ruleBroken("dish-unavailable", `${dish.name} is finished for today.`);
      }
      return ordersRepository.create({
        dishId,
        quantity,
        totalNaira: dish.priceNaira * quantity,
        status: "pending",
      });
    },

    async get(id: string): Promise<Order> {
      const order = await ordersRepository.findById(id);
      if (!order) throw notFound("Order", id);
      return order;
    },
  };
}
```

`place` now promises an `Order`, full stop. If it can't keep that promise, it throws. No `{ ok: false }` to unpack. And `get` throws `notFound` itself, so no route ever needs to write "if missing, 404" again. The same goes for `menuService.get`, which you'll change in the practice.

The route shrinks to its real job:

```ts
router.post("/", async (req, res) => {
  const input = validate(PlaceOrderSchema, req.body, "body");
  const order = await ordersService.place(input.dishId, input.quantity);
  res.status(201).location(`/orders/${order.id}`).json({ data: order });
});
```

No `if`. If anything goes wrong, the error flies straight to the error handler, because Express 5 catches errors thrown in async handlers. (In Express 4 it didn't, and this whole style needed a wrapper around every handler. One more reason we're on Express 5.)

Do you see what happened to `loadDish`? It was only there to say "find it or 404". Now `menuService.get` throws `notFound` by itself, so `loadDish` can go. `GET /menu/:id` becomes three lines:

```ts
router.get("/:id", async (req, res) => {
  const { id } = validate(DishIdSchema, req.params, "params");
  res.json({ data: await menuService.get(id) });
});
```

## Step 4: a request ID for every request
<!-- bite: 04765b5a-e4ce-4be9-a974-a7b18db978e6 -->

Before the error handler, one small middleware. `src/shared/request-id.ts`:

```ts
import { randomUUID } from "node:crypto";
import type { Request, Response, NextFunction } from "express";

export function requestId(req: Request, res: Response, next: NextFunction) {
  const id = randomUUID();
  res.locals.requestId = id;
  res.setHeader("X-Request-Id", id);
  next();
}
```

Every response now carries an `X-Request-Id` header. Put it first in `createApp`, before the logger, and make the logger print it too. [[backend/frameworks/express/27-observability|Lesson 27]] takes this further, passing the same ID from service to service.

## Step 5: one error handler for everything
<!-- bite: ecbad8b6-0eec-4b2a-8038-fc0bd587bff8 -->

`src/shared/error-handler.ts`:

```ts
import type { Request, Response, NextFunction } from "express";
import { AppError } from "./errors.ts";
import type { ErrorKind } from "./errors.ts";

const STATUS: Record<ErrorKind, number> = {
  invalid: 400,
  unauthenticated: 401,
  forbidden: 403,
  not_found: 404,
  conflict: 409,
  rule_broken: 422,
};

const PROBLEMS = "https://mamaput.example/problems/";

function sendProblem(
  res: Response,
  status: number,
  code: string,
  title: string,
  detail: string,
  extra: Record<string, unknown> = {},
) {
  res
    .status(status)
    .type("application/problem+json")
    .json({ type: PROBLEMS + code, title, status, detail, code, requestId: res.locals.requestId, ...extra });
}

export function errorHandler(err: unknown, req: Request, res: Response, next: NextFunction) {
  if (res.headersSent) {
    next(err);
    return;
  }

  // 1. Our own errors: we know exactly what they mean.
  if (err instanceof AppError) {
    const extra = err.details === undefined ? {} : { errors: err.details };
    sendProblem(res, STATUS[err.kind], err.code, titleFor(err.code), err.message, extra);
    return;
  }

  // 2. Errors Express's body parser raises for bad JSON or a body that's too big.
  if (isBodyParserError(err)) {
    const tooBig = err.type === "entity.too.large";
    sendProblem(
      res,
      tooBig ? 413 : 400,
      tooBig ? "body-too-large" : "malformed-json",
      tooBig ? "Body too large" : "Malformed JSON",
      tooBig ? "The request body is larger than this API accepts." : "The request body is not valid JSON.",
    );
    return;
  }

  // 3. Anything else is a bug. Log everything; tell the client nothing.
  console.error({ requestId: res.locals.requestId, method: req.method, url: req.originalUrl, err });
  sendProblem(res, 500, "internal-error", "Internal error", "Something went wrong on our side. Quote the request ID if you contact us.");
}

function titleFor(code: string) {
  const words = code.replace(/-/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function isBodyParserError(err: unknown): err is { type: string } {
  return typeof err === "object" && err !== null && "type" in err &&
    (err.type === "entity.parse.failed" || err.type === "entity.too.large");
}
```

Read it as three doors, in order:

1. **Our own `AppError`s.** We look up the status from the kind, and send the code, message and any details (like validation issues) in the problem shape.
2. **Body parser errors.** If a client sends `{"name": "Jollof"` (missing `}`), `express.json()` fails before any route runs. Until now Express answered that with an HTML page. Now it's a proper 400 problem. A body over the size limit is 413, which matters in [[backend/frameworks/express/14-security|lesson 14]].
3. **Everything else is a bug.** We log the whole thing (the error with its stack trace, the request ID, the method and URL) and the client gets a polite 500 with only the request ID. They can't see your code; you can find the exact log line.

And the `res.headersSent` check at the top? If a response had already started going out when the error happened, we can't change its status any more. Handing the error to Express's own handler with `next(err)` closes the connection properly.

The catch-all 404 joins in, using the same shape:

```ts
// src/shared/not-found.ts
import type { Request, Response, NextFunction } from "express";
import { AppError } from "./errors.ts";

export function notFoundRoute(req: Request, res: Response, next: NextFunction) {
  next(new AppError("not_found", "route-not-found", `There is no ${req.method} ${req.path} here.`));
}
```

It doesn't answer by itself; it creates an `AppError` and passes it on with `next(err)`. Everything goes through one door.

## Step 6: success in the envelope
<!-- bite: c269be1a-e0e9-4b53-b740-c7feacc28aa0 -->

Go through the routes and wrap every success in `{ data }`:

```ts
router.get("/", async (req, res) => {
  const query = validate(ListMenuQuerySchema, req.query, "query");
  const dishes = await menuService.list(query.available === true);
  res.json({ data: dishes, meta: { count: dishes.length } });
});
```

`204 No Content` answers stay empty, because "no content" means exactly that.

## Trying every door
<!-- bite: 67f7dabd-5fe2-4a15-a0e4-bb6a1f40d2f3 -->

```bash
curl -s http://localhost:3000/menu/2
# {"data":{"id":"2","name":"Beans and plantain","priceNaira":1200,"available":true}}

curl -s http://localhost:3000/menu/999
# {"type":".../problems/dish-not-found","title":"Dish not found","status":404,
#  "detail":"Dish 999 was not found.","code":"dish-not-found","requestId":"..."}

curl -s -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d '{"dishId":"3","quantity":1}'
# 422 dish-unavailable: "Pounded yam and egusi is finished for today."

curl -s -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d '{"dishId":"1","quantity":1'
# 400 malformed-json

curl -s http://localhost:3000/suya
# 404 route-not-found: "There is no GET /suya here."
```

Now break something on purpose: in `menu.service.ts`, make `list` do `throw new Error("oops")`. Predict what the client sees and what your terminal shows. Then check: the client gets a 500 problem with a request ID, and your terminal shows the full error with its stack, under the same ID. Put the code back afterwards.

## The TypeScript in this lesson
<!-- bite: 400203af-4233-4405-9503-3a71b59289b6 -->

1. **A union type spread over several lines (`| "invalid" | "unauthenticated" ...`)**: The same union of exact words as `OrderStatus` in lesson 4. Starting each line with `|` is just tidy formatting, and the `// comments` explain each word.
2. **`details?: unknown`**: The `?` makes a field **optional**: an `AppError` may or may not have details. Its type is `unknown`, because details can be anything (a list of issues today, something else tomorrow).
3. **`class ValidationError extends AppError`**: A class can extend another class you wrote, not just built-in ones. A `ValidationError` is an `AppError`, which is an `Error`. So `err instanceof AppError` is true for it, and the error handler needs no special case.
4. **`export const notFound = (what: string, id: string) => new AppError(...)`**: A small function that builds an error. Throwing `notFound("Dish", "9")` reads better than spelling out the whole `new AppError(...)` every time.
5. **`` `${what.toLowerCase()}-not-found` ``**: A template string with a method call inside: `"Dish"` becomes `"dish-not-found"`.
6. **`Record<ErrorKind, number>`**: A `Record<K, V>` is an object whose keys are `K` and whose values are `V`. Because the keys are exactly the `ErrorKind` words, TypeScript makes us give a status for **every** kind. Add a new kind later and forget its status, and the code won't type-check. That's a mistake caught before it ships.
7. **`err: unknown` in the error handler**: Anything can be thrown in JavaScript, even a string or a number, so we don't pretend it's an `Error`. We check what it is before using it.
8. **`function isBodyParserError(err: unknown): err is { type: string }`**: The return type `err is { type: string }` makes this a **type guard**. When it returns true, TypeScript knows that inside the `if`, `err` has a `type` field. That's how `err.type` is allowed in door 2.
9. **`"type" in err`**: `in` checks whether an object has a field with that name.
10. **`...extra`**: Spread again: copy any extra fields (like `errors`) into the problem object.
11. **`code.replace(/-/g, " ")`**: Replace every `-` with a space. The `g` after the pattern means "every one, not just the first".
12. **`import { randomUUID } from "node:crypto"`**: Node's built-in way to make a random, practically unique ID.

## Your project so far
<!-- bite: 7b9b1c04-cb75-4594-8858-ee7c63b94759 -->

```text
mama-put-api/
├── package.json
├── package-lock.json
├── tsconfig.json
└── src/
    ├── server.ts
    ├── app.ts                    ← requestId first; notFoundRoute and errorHandler last
    ├── menu/
    │   ├── menu.schemas.ts
    │   ├── menu.types.ts
    │   ├── menu.repository.ts
    │   ├── menu.service.ts       ← get() throws notFound instead of returning null
    │   └── menu.routes.ts        ← no more loadDish; every success is { data }
    ├── orders/
    │   ├── orders.schemas.ts
    │   ├── orders.types.ts
    │   ├── orders.repository.ts
    │   ├── orders.service.ts     ← place() returns an Order or throws; no result objects
    │   ├── orders.service.test.ts ← update: expect a thrown AppError (see practice)
    │   └── orders.routes.ts      ← no status picking; every success is { data }
    └── shared/
        ├── errors.ts             ← NEW: ErrorKind, AppError, notFound, ruleBroken, conflict
        ├── request-id.ts         ← NEW: an ID on every request and response
        ├── validate.ts           ← ValidationError is now an AppError
        ├── log-requests.ts       ← now prints the request ID
        ├── kitchen-only.ts       ← should throw AppError("unauthenticated", ...) (see practice)
        ├── not-found.ts          ← notFoundRoute: passes an AppError on
        └── error-handler.ts      ← three doors: AppError, body parser, bugs
```

## Common mistakes
<!-- bite: 12c6d3ad-672c-4cee-a701-418f89c80fd4 -->

1. **Sending `err.message` for unknown errors.** A database error message can contain table names or even data. Unknown errors get a generic message; the real one goes to the log.
2. **Sending the stack trace "just in development".** It always leaks to production one day. Keep it in the log.
3. **Status codes inside services.** Services throw kinds; the error handler picks statuses.
4. **Catching an error and doing nothing.** `try { ... } catch {}` hides bugs. Catch only when you can do something useful, otherwise let it reach the error handler.
5. **Using 500 for the client's mistakes.** 500 means "our fault". Bad input is 400, a missing thing is 404.
6. **Mixing shapes.** One route that returns a bare array breaks every client that expects `{ data }`.
7. **Returning 200 with `{ "error": ... }` in the body.** Clients, proxies and monitoring all read the status. An error must have an error status.

## Check your understanding
<!-- bite: 3d78dc0a-edb6-41b4-80e7-61e64a79000e -->

1. A service throws `ruleBroken("shop-closed", "Mama Put is closed. We open at 7am.")`. What status and body does the client get?
2. Why doesn't `AppError` store an HTTP status?
3. The database is down, and `menuRepository.list()` throws a connection error. What does the client see? What do you see?
4. Why does `notFoundRoute` call `next(...)` instead of answering by itself?

<details>
<summary>Answers, after your attempt</summary>

1. 422, with `{ type: ".../problems/shop-closed", title: "Shop closed", status: 422, detail: "Mama Put is closed. We open at 7am.", code: "shop-closed", requestId: "..." }` and content type `application/problem+json`.
2. Because services throw it, and services don't know about HTTP. The kind says *what* went wrong; only the error handler decides how to say that in HTTP. The same error could be thrown in a background job, where there's no status at all.
3. The client sees a 500 problem with "Something went wrong on our side" and a request ID. You see the full connection error, its stack trace and the request details in your log, under that same ID.
4. So every error, including "no such route", goes through the same error handler and gets the same shape. One door, one shape.

</details>

## Practice
<!-- bite: a20aeb87-818d-479b-90cb-2dd09951b8d3 -->

1. Make `menuService.get` throw `notFound("Dish", id)` and remove `loadDish`. Make `kitchenOnly` throw `new AppError("unauthenticated", "staff-key-required", "Kitchen staff only.")` instead of answering 401 itself.
2. Make `PATCH /orders/:id/status` throw `conflict("bad-status-change", ...)` when the order would go backwards (collected → pending).
3. Update `orders.service.test.ts`: the "finished dish" test should now check that `place` **throws** an `AppError` with code `dish-unavailable`. Hint: `await assert.rejects(() => orders.place("9", 1), { code: "dish-unavailable" })`.

**Done when** every error you can trigger with `curl` (bad input, missing dish, missing order, finished dish, too many plates, bad status change, no staff key, broken JSON, unknown route) answers with the problem shape and the right status, every success has `data`, and `node --test` passes.

## Before moving on
<!-- bite: 0f8e37ef-52d3-4396-abe9-43e37e4787d2 -->

Mama Put API now speaks one language. Every success is `{ data }`, every failure is a problem with a status, a code and a request ID, and bugs stay in your logs.

But all our data still lives in arrays that vanish on every restart. Mama added ofada rice yesterday, the app restarted, and it's gone. Customers' orders, gone. And two customers can both "buy" the last plate of jollof at the same time, because nothing stops them. A real backend needs a real database, and that's the next lesson.

## Related
<!-- bite: c678341d-96e4-458d-8075-2361866070e8 -->

- [[backend/frameworks/express/08-data-with-postgres|Next: Data with PostgreSQL]]
- [[backend/06-cross-cutting/03-error-handling|Error Handling]] — the idea in any framework
- [[backend/frameworks/node/02-error-handling|Error Handling in Node.js]] — the errors Express never sees (process-level)

## About this lesson
<!-- bite: b597f451-f806-4fac-b062-b2a7bdda8ab5 -->

**Level:** Intermediate. Lesson 7 of [[backend/frameworks/express/index|Express]]. Covers the `{ data, meta }` envelope, problem details (RFC 9457) with a machine-readable `code`, an `AppError` with kinds instead of statuses, services that throw instead of returning results, request IDs, one error handler with three doors (our errors, body parser errors, bugs), and a catch-all 404 that goes through the same door.
