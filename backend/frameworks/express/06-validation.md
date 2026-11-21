---
id: e4e549c6-77f3-4c94-999e-5a3caa8b1f3e
---

# Input Validation

**Input validation means checking everything a client sends (the body, the path parameters and the query string) before your code uses it, and refusing the request if it's wrong.** Every form you've filled online that said "please enter a valid email" was doing a small part of this. The backend has to do it too, and more strictly, because anyone can send a request straight to your API without going through any form at all.

## Before you start
<!-- bite: b5931645-5d00-4534-9e02-b51574905126 -->

You should have the wired-up app from [[backend/frameworks/express/05-wiring-dependencies|lesson 5]]: factories, `createApp(deps)` and `buildDeps()` in `server.ts`.

After this lesson you will be able to:

1. Describe the shape of good input with a zod schema.
2. Check the body, path parameters and query string of a request, and answer 400 with a clear list of what's wrong.
3. Get a properly typed value out of validation, so the rest of your code can trust it.
4. Tell apart a validation problem (400) from a broken business rule (422).

## Where we stopped
<!-- bite: 60b11114-6781-4f55-8fb6-f05091c2bd84 -->

Back in [[backend/frameworks/express/02-routing|lesson 2]] we left a hole on purpose. This request still works:

```bash
curl -X POST http://localhost:3000/menu \
  -H "Content-Type: application/json" -H "X-Staff-Key: jollof123" \
  -d '{"priceNaira": "free", "available": "maybe", "id": "999"}'
```

Predict what's on the menu afterwards, then run `curl http://localhost:3000/menu` and look.

There's a dish with no name, a price of `"free"`, and depending on how the repository copies fields, maybe a strange `id` too. Our code believed every word. Now imagine that dish reaching a database, a receipt, a Paystack payment for "free" naira. Wiring made the inside of the app clean. Validation guards the door.

## The kid version
<!-- bite: 237a906a-ee5a-48b4-8d99-1185a40555f3 -->

Mama Put has a rule at the counter: before an order goes to the kitchen, the helper reads it back. "One plate of jollof, two meat, no pepper. Is that right?" If the customer says "one plate of... something nice", the helper doesn't send that to the kitchen. She says "please, which food?" and waits for a proper order.

Validation is that helper. The kitchen (your services) only ever sees orders that make sense.

**Where the picture stops working.** The helper can ask follow-up questions. An API can't; it answers once. So when it refuses, it must say *everything* that's wrong in one go, not just the first problem, or the client has to try again and again.

## Terms used in validation
<!-- bite: 3eb36482-1495-4b89-8cd7-b9fec5872a3f -->

1. **Schema**: This is a description of what good input looks like: which fields, what type each one is, and any limits like "at least 1 character". We write schemas with a library called **zod**.
2. **Parsing**: This is checking a value against a schema and, if it passes, getting back a clean, typed copy. zod parses rather than just checks: it gives you back *new* data you can trust, not a yes or no.
3. **Coercion**: This is turning a value from one type into another on purpose, like the text `"true"` from a query string into the boolean `true`.
4. **Stripping**: This is dropping fields the schema doesn't mention. If a client sneaks in `"id": "999"`, it's removed before your code sees it.
5. **Issue**: This is one thing that's wrong with the input, like "name: required". A failed parse gives a list of issues.
6. **400 Bad Request**: This is the status for "your request is malformed; fix it before sending again".

## Why validate at the door, and only there
<!-- bite: 36d69550-eac9-4455-9089-ac511eb36942 -->

You could check fields inside the service, or inside the repository, or everywhere. Don't. Check **once, at the edge**, as the request comes in, and then trust the data everywhere inside.

That's the same idea as the helper at the counter. If the kitchen had to double-check every order too, nobody would cook. And because zod gives back a *typed* value, TypeScript carries the trust inward for you: once something is a `NewDish`, every function that receives it knows the name is text and the price is a whole number.

## Installing zod and writing the first schema
<!-- bite: 9c0db726-23c0-4d7a-8ba3-13292a54d359 -->

```bash
npm install zod
```

Create `src/menu/menu.schemas.ts`:

```ts
import { z } from "zod";

export const NewDishSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(80),
  priceNaira: z.number().int().positive().max(100_000),
});
```

Read it like a sentence: "a new dish is an object with a `name`, which is text, with spaces trimmed off, at least 1 and at most 80 characters, and a `priceNaira`, which is a whole positive number no bigger than 100,000".

Every limit is there for a reason. `trim()` stops `"   "` counting as a name. `max(80)` stops someone sending a 10-megabyte name that fills your database. `int()` stops `1500.75` naira, which Mama can't give change for. `max(100_000)` catches a typo like `15000000` before a customer sees it.

Try it on its own, in a scratch file, before plugging it into Express:

```ts
import { NewDishSchema } from "./src/menu/menu.schemas.ts";

console.log(NewDishSchema.safeParse({ name: "  Ofada rice ", priceNaira: 2000, id: "999" }));
// { success: true, data: { name: "Ofada rice", priceNaira: 2000 } }

console.log(NewDishSchema.safeParse({ priceNaira: "free" }).error?.issues);
// [ { path: ["name"], message: "Invalid input: expected string, received undefined", ... },
//   { path: ["priceNaira"], message: "Invalid input: expected number, received string", ... } ]
```

Look closely at the first result. The name came back trimmed. And `id` is **gone**: `z.object` strips any field it doesn't know about. That stops a client from setting fields you never meant them to set, like an `id`, or later a `role: "admin"`. That kind of attack has a name, **mass assignment**, and stripping shuts it down for free.

The second result lists **both** problems at once. That's the helper saying everything that's wrong in one go.

## One schema, one type
<!-- bite: b2a2f166-3417-40a7-9111-f7c2a9c99707 -->

Here's a quiet win. Remember `NewDish` in `menu.types.ts`, written by hand in lesson 4? Delete it, and get it from the schema instead:

```ts
// src/menu/menu.schemas.ts (continued)
export type NewDish = z.infer<typeof NewDishSchema>;
// { name: string; priceNaira: number }
```

Now there's one source of truth. Add a field to the schema and the type changes with it. They can never drift apart.

Point `menu.types.ts` at it so other files don't need to change their imports:

```ts
// src/menu/menu.types.ts
export type { NewDish, DishChanges } from "./menu.schemas.ts";
```

## The rest of the menu's schemas
<!-- bite: 7e43f103-8f03-4592-8286-950db3ab089b -->

```ts
// src/menu/menu.schemas.ts (continued)

export const DishChangesSchema = NewDishSchema.extend({
  available: z.boolean(),
})
  .partial()
  .refine((changes) => Object.keys(changes).length > 0, {
    message: "Send at least one field to change",
  });

export type DishChanges = z.infer<typeof DishChangesSchema>;

export const DishIdSchema = z.object({
  id: z.string().regex(/^\d+$/, "Dish id must be a number"),
});

export const ListMenuQuerySchema = z.object({
  available: z.stringbool().optional(),
});
```

1. **`DishChangesSchema`** reuses `NewDishSchema`, adds `available`, then makes every field optional with `.partial()`, because a PATCH can change any of them. The `.refine(...)` adds one rule zod can't express by itself: an empty `{}` changes nothing, so refuse it.
2. **`DishIdSchema`** checks the path parameter. `req.params.id` is always text, so we check that it's text made only of digits. `/menu/abc` is now a clear 400, not a mysterious "not found".
3. **`ListMenuQuerySchema`** checks the query string. `z.stringbool()` is coercion: it turns the text `"true"` or `"false"` (also `"1"`, `"0"`, `"yes"`, `"no"`) into a real boolean, and rejects anything else. Remember from lesson 2 that everything in a URL is text. This is where it stops being text.

## A small `validate` helper
<!-- bite: 9b4c9276-e6f3-42f3-b3a4-f9cea26e8f85 -->

We'll check input in many routes, and every time a check fails the answer is the same: 400 with the list of issues. So write it once.

`src/shared/validate.ts`:

```ts
import type { z } from "zod";

export type InputIssue = { in: "body" | "params" | "query"; path: string; message: string };

export class ValidationError extends Error {
  issues: InputIssue[];

  constructor(issues: InputIssue[]) {
    super("The request is not valid");
    this.name = "ValidationError";
    this.issues = issues;
  }
}

export function validate<S extends z.ZodType>(
  schema: S,
  value: unknown,
  where: InputIssue["in"],
): z.infer<S> {
  const result = schema.safeParse(value);
  if (!result.success) {
    throw new ValidationError(
      result.error.issues.map((issue) => ({
        in: where,
        path: issue.path.map(String).join("."),
        message: issue.message,
      })),
    );
  }
  return result.data;
}
```

It does one thing: parse, and either give back the clean typed value or **throw** a `ValidationError` that carries every issue and says where it was (`body`, `params` or `query`).

Why throw instead of answering 400 right there? Because `validate` is called from inside handlers, and throwing lets us answer in one place. Remember from [[backend/frameworks/express/04-structuring-an-express-app|lesson 4]]: in Express 5, anything a handler throws goes to your error handler. So we teach the error handler about this one kind of error:

```ts
// src/shared/error-handler.ts
import type { Request, Response, NextFunction } from "express";
import { ValidationError } from "./validate.ts";

export function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  if (err instanceof ValidationError) {
    res.status(400).json({ error: err.message, issues: err.issues });
    return;
  }
  console.error(err);
  res.status(500).json({ error: "Something went wrong" });
}
```

## Using it in the menu routes
<!-- bite: e483287d-5938-4421-8589-d228bfdcb666 -->

```ts
// src/menu/menu.routes.ts
import express from "express";
import type { Request, Response, NextFunction } from "express";
import type { MenuService } from "./menu.service.ts";
import { validate } from "../shared/validate.ts";
import {
  NewDishSchema,
  DishChangesSchema,
  DishIdSchema,
  ListMenuQuerySchema,
} from "./menu.schemas.ts";

export function createMenuRouter(deps: { menuService: MenuService; kitchenOnly: express.RequestHandler }) {
  const { menuService, kitchenOnly } = deps;
  const router = express.Router();

  async function loadDish(req: Request, res: Response, next: NextFunction) {
    const { id } = validate(DishIdSchema, req.params, "params");
    const dish = await menuService.get(id);
    if (!dish) {
      res.status(404).json({ error: "Dish not found" });
      return;
    }
    res.locals.dish = dish;
    next();
  }

  router.get("/", async (req, res) => {
    const query = validate(ListMenuQuerySchema, req.query, "query");
    res.json(await menuService.list(query.available === true));
  });

  router.get("/:id", loadDish, (req, res) => {
    res.json(res.locals.dish);
  });

  router.post("/", kitchenOnly, async (req, res) => {
    const input = validate(NewDishSchema, req.body, "body");
    const dish = await menuService.add(input);
    res.status(201).location(`/menu/${dish.id}`).json(dish);
  });

  router.patch("/:id", kitchenOnly, loadDish, async (req, res) => {
    const changes = validate(DishChangesSchema, req.body, "body");
    res.json(await menuService.change(res.locals.dish.id, changes));
  });

  router.delete("/:id", kitchenOnly, loadDish, async (req, res) => {
    await menuService.remove(res.locals.dish.id);
    res.sendStatus(204);
  });

  return router;
}
```

Look at the POST handler. Hover over `input` in your editor: it's `{ name: string; priceNaira: number }`. Not `any`. Not whatever the client typed. After that one line, the handler is holding clean, trimmed, typed data, and so is the service it passes it to.

(`kitchenOnly` now arrives through `deps`, which is the practice from lesson 5 done for you. `server.ts` builds it with `createKitchenOnly(staffKey)` and passes it in.)

Now send the bad request from the start of the lesson again:

```bash
curl -s -X POST http://localhost:3000/menu \
  -H "Content-Type: application/json" -H "X-Staff-Key: jollof123" \
  -d '{"priceNaira": "free", "available": "maybe", "id": "999"}'
```

```json
{
  "error": "The request is not valid",
  "issues": [
    { "in": "body", "path": "name", "message": "Invalid input: expected string, received undefined" },
    { "in": "body", "path": "priceNaira", "message": "Invalid input: expected number, received string" }
  ]
}
```

400, both problems listed, and nothing reached the service. `available` and `id` were simply dropped. (The exact wording of zod's messages can change between versions. The shape won't.)

And forgetting the body entirely? In Express 5, `req.body` is `undefined` when no JSON body was sent, so zod answers "expected object, received undefined". One clear 400 instead of a crash.

## Validation is not business rules
<!-- bite: 9fe0f9da-9c56-45a1-9f6b-1ef5b50c2fa1 -->

Now the orders. Here's the schema:

```ts
// src/orders/orders.schemas.ts
import { z } from "zod";

export const PlaceOrderSchema = z.object({
  dishId: z.string().regex(/^\d+$/, "dishId must be a number"),
  quantity: z.number().int().positive(),
});
```

Notice what's **not** there: "no more than 20 plates". That rule lives in `orders.service.ts`, and it should stay there. Why?

1. **Validation asks: is this a sensible request?** Is `quantity` a whole number? Is `dishId` there? Anyone could answer that by looking at the request alone.
2. **Business rules ask: can we do this, right now?** Is the dish available? Is 20 plates our limit? Answering needs knowledge of the business, and sometimes the database.

Rules change for business reasons. When Mama says "for owambe season, 50 plates", that's one line in the service, not a hunt through schemas. And the rule still holds if orders ever come from somewhere other than this route, like a background job or the GraphQL API in [[backend/frameworks/express/21-graphql|lesson 21]].

That's also why the answers differ:

| Problem | Example | Status |
|---|---|---|
| Malformed input | `quantity: "two"` | 400 Bad Request |
| Breaks a business rule | 25 plates, or a finished dish | 422 Unprocessable Content |
| Thing doesn't exist | dish 999 | 404 Not Found |

A client reading 400 knows "my code sent garbage, fix the code". A client reading 422 knows "the request was fine, but the answer is no, show the user why".

## The TypeScript in this lesson
<!-- bite: 08954f84-44ab-471a-9c69-832a0d4848f7 -->

1. **`import { z } from "zod"`**: zod puts everything in one object called `z`: `z.object`, `z.string`, `z.number` and so on. Calling them builds a schema.
2. **Chaining, like `z.string().trim().min(1).max(80)`**: Each call returns a new schema with one more rule added, so you can keep adding rules with dots. It reads left to right.
3. **`100_000`**: The underscore is only for your eyes. It's the number 100000, written so you can count the zeros.
4. **`/^\d+$/`**: This is a **regular expression**, a small pattern for matching text. `^` means "start", `\d+` means "one or more digits", `$` means "end". Together: "only digits, nothing else".
5. **`z.infer<typeof NewDishSchema>`**: `typeof NewDishSchema` is the type of the schema object. `z.infer<...>` reads that schema and gives you the TypeScript type of the data it accepts. One schema, one type.
6. **`export type { NewDish } from "./menu.schemas.ts"`**: This passes a type through from another file, so code importing from `menu.types.ts` keeps working.
7. **`class ValidationError extends Error`**: A **class** is a blueprint for making objects. `extends Error` means a `ValidationError` *is* an `Error`, with everything an error has (a message, a stack trace) plus our own `issues` field. `constructor` runs when you write `new ValidationError(...)`, and `super(...)` hands the message to `Error`'s own constructor.
8. **`err instanceof ValidationError`**: This checks whether an object was made from that class. It's how the error handler tells our validation errors apart from everything else.
9. **`function validate<S extends z.ZodType>(schema: S, ...): z.infer<S>`**: The `<S ...>` makes this a **generic** function: it works for any schema, and `S` stands for whichever schema you pass. `extends z.ZodType` says "S must be a zod schema". The return type `z.infer<S>` then means "the type that *this* schema describes". That's why `validate(NewDishSchema, ...)` gives back a `NewDish`, and `validate(DishIdSchema, ...)` gives back `{ id: string }`, from one function.
10. **`value: unknown`**: `unknown` means "this could be anything, and you must check before using it". It's the safe opposite of `any`. Request input is exactly that: unknown until validated.
11. **`InputIssue["in"]`**: This picks out the type of one field of another type. `InputIssue["in"]` is `"body" | "params" | "query"`, so we don't have to write it twice.
12. **`issue.path.map(String).join(".")`**: `path` is a list like `["items", 0, "quantity"]`. `map(String)` turns each part into text, and `join(".")` glues them with dots: `"items.0.quantity"`.
13. **`express.RequestHandler`**: The type of any middleware or handler. We use it for `kitchenOnly` in `deps`, because the router only needs to know "this is middleware".

## Your project so far
<!-- bite: f3219465-94b0-4a9c-8622-0b8a425d71cc -->

```text
mama-put-api/
├── package.json                  ← now also depends on zod
├── package-lock.json
├── tsconfig.json
└── src/
    ├── server.ts                 ← buildDeps(), now also builds kitchenOnly
    ├── app.ts
    ├── menu/
    │   ├── menu.schemas.ts       ← NEW: NewDish, DishChanges, DishId and ListMenuQuery schemas, and their types
    │   ├── menu.types.ts         ← Dish and MenuRepository; NewDish and DishChanges now come from the schemas
    │   ├── menu.repository.ts
    │   ├── menu.service.ts
    │   └── menu.routes.ts        ← every route validates its params, query or body first
    ├── orders/
    │   ├── orders.schemas.ts     ← NEW: PlaceOrderSchema (shape only; the 20-plate rule stays in the service)
    │   ├── orders.types.ts
    │   ├── orders.repository.ts
    │   ├── orders.service.ts
    │   ├── orders.service.test.ts
    │   └── orders.routes.ts      ← validates before calling the service
    └── shared/
        ├── validate.ts           ← NEW: validate() and ValidationError
        ├── log-requests.ts
        ├── kitchen-only.ts
        ├── not-found.ts
        └── error-handler.ts      ← now answers 400 for ValidationError
```

## Common mistakes
<!-- bite: 8fe184c3-1f83-4b30-9df8-83fe4f45e198 -->

1. **Validating in the service as well as at the door.** Pick the door. Inside, trust the types.
2. **Using the raw `req.body` after validating.** The clean data is what `validate` *returned*. `req.body` still has the untrimmed name and the sneaky `id`.
3. **`z.number()` on a query parameter.** Query values are always text, so it always fails. Use coercion (`z.coerce.number()`, `z.stringbool()`).
4. **No limits on text.** A schema with `z.string()` and no `max` lets someone post a novel. Every text field gets a maximum.
5. **Stopping at the first problem.** zod collects all issues; make sure your 400 sends all of them.
6. **Putting business rules in schemas.** Shape at the door, rules in the service.
7. **Trusting the frontend's checks.** The frontend checks are for a nice experience. Anyone can skip them with `curl`. The backend checks are the real ones.

## Check your understanding
<!-- bite: 36395894-c321-4d9e-b0e6-b04095c5b9dd -->

1. A client sends `{ "name": "Suya", "priceNaira": 800, "available": false }` to `POST /menu`. What does the service receive, and why?
2. Why does `ListMenuQuerySchema` use `z.stringbool()` and not `z.boolean()`?
3. A customer orders 30 plates of jollof. Which file refuses it, and with which status? What about `quantity: -3`?
4. What's the difference between `unknown` and `any`?

<details>
<summary>Answers, after your attempt</summary>

1. `{ name: "Suya", priceNaira: 800 }`. `NewDishSchema` doesn't mention `available`, so zod strips it; new dishes start available, because the repository says so.
2. Query values are always text. `z.boolean()` would reject the text `"true"`. `z.stringbool()` turns it into the boolean `true`.
3. 30 plates passes validation (it's a positive whole number) and is refused by `orders.service.ts` with 422, because the 20-plate limit is a business rule. `-3` is refused at the door with 400: it's not a sensible quantity at all.
4. Both can hold anything. `any` lets you use the value however you like with no checks. `unknown` makes you check what it is first. Request input should be `unknown` until it's validated.

</details>

## Practice
<!-- bite: 2f3e5bc6-ea06-4af3-bd59-fcee1c3c891c -->

1. Validate the orders routes: the body of `POST /orders`, the `:id` of `GET /orders/:id`, and the body of `PATCH /orders/:id/status`, where `status` must be one of `"ready"` or `"collected"` (hint: `z.enum([...])`).
2. Add an optional `note` to orders, text up to 200 characters, like "no pepper, please".
3. Add a query parameter `GET /menu?maxPrice=2000` that only lists dishes at or below that price. Use `z.coerce.number().int().positive().optional()`.

**Done when** each of these gets a 400 listing every problem: `quantity: "two"`, `status: "cooking"`, a 201-character note, `maxPrice=cheap`; and a valid order with a note still gets 201.

## Before moving on
<!-- bite: ee79e573-819f-45eb-9230-e808a24289cd -->

Nothing gets past the door now without matching a schema, and what gets through is typed all the way down.

But look at the error answers in our app. `ValidationError` gives `{ error, issues }`. `loadDish` gives `{ error: "Dish not found" }`. The orders route turns service reasons into `{ error: "dish-unavailable" }`. A crash gives `{ error: "Something went wrong" }`. And successful answers are bare arrays and objects. Four kinds of failure, four ways of saying it, and a client has to know them all. The next lesson gives every response, good or bad, one shape, and moves all the "turn this problem into a status" code into one place.

## Related
<!-- bite: 2d8b649d-1a82-4ad5-8957-ff4c1196c04a -->

- [[backend/frameworks/express/07-errors|Next: Errors and Structured Responses]]
- [[backend/06-cross-cutting/01-validation-and-dtos|Validation and DTOs]] — the idea in any framework
- [[backend/frameworks/express/05-wiring-dependencies|Previous: Wiring Dependencies]]

## About this lesson
<!-- bite: d3f95cf0-c9b5-4d85-b74d-5179ed38fafa -->

**Level:** Intermediate. Lesson 6 of [[backend/frameworks/express/index|Express]]. Covers zod schemas, parsing versus checking, stripping unknown fields (mass assignment), coercion for query and path values, types inferred from schemas, a generic `validate` helper with a `ValidationError`, and the line between validation (400) and business rules (422). Written against zod 4.
