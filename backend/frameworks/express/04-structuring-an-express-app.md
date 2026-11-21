---
id: 7ecdcbeb-eb8c-4869-bca1-1a04a9dbeea8
---

# Structuring an Express App

**Structuring an app means deciding which code goes in which file, so that each file has one job and you can find, change and test things without reading everything.** Express doesn't decide this for you. It will run a 2,000-line `server.ts` just as happily as a tidy project, so the structure is your job, and the earlier you do it, the cheaper it is.

## Before you start
<!-- bite: ac0e09b3-add9-41cc-990b-f6f9e41d664c -->

You should have the menu router, the orders router, `loadDish` and `kitchenOnly` from [[backend/frameworks/express/03-middleware|lesson 3]].

After this lesson you will be able to:

1. Split an Express app into feature folders.
2. Explain the job of a route file, a service and a repository, and keep each to its job.
3. Separate "build the app" (`app.ts`) from "start the app" (`server.ts`), and say why that matters.

## Where we stopped
<!-- bite: 1c52df2a-9820-45c0-928c-32a8707a05a0 -->

Open `src/server.ts`. Everything is in there: the `Dish` type, the dishes array, the orders array, the logger, `loadDish`, `kitchenOnly`, two routers, the 404 and the error handler. It works. But try to answer these quickly:

1. Where is the rule "you can't order a dish that isn't available"?
2. If Mama moves the menu into a database, which lines change?
3. How would you test the price total without starting a server?

In one big file, the answers are "somewhere", "lots of them, all over" and "you can't, really". Good structure turns each answer into one file.

## The kid version
<!-- bite: d9ac4142-13df-4300-b81f-4c64dd69b0d3 -->

Mama Put has grown. She now has a proper kitchen with three people:

1. **The waiter** takes the order from the customer and brings back the plate. He doesn't cook and doesn't know where the rice is stored.
2. **The cook** knows the rules: how much a plate costs, that you can't sell jollof once the pot is finished, that nobody gets 50 plates at once.
3. **The storekeeper** knows where everything is kept and fetches it. He doesn't care who ordered or why.

When Mama buys a bigger freezer, only the storekeeper's job changes. The waiter and the cook carry on as before.

**Where the picture stops working.** Real staff can talk to anyone. In code, we'll be strict: the waiter only talks to the cook, and the cook only talks to the storekeeper. That one-way line is what keeps changes small.

## Terms used in structuring
<!-- bite: 33b2d0f2-1aa8-47e3-8838-e89036d52cdd -->

1. **Layer**: This is a group of code with one kind of job. We'll use three layers, and each one only calls the layer below it.
2. **Route file**: This is the waiter. It is also called the **controller** in many frameworks. It reads the request, calls a service, and turns the result into a response. It knows about HTTP. It doesn't know business rules.
3. **Service**: This is the cook. It holds the business rules ("total is price times quantity", "can't order an unavailable dish"). It knows nothing about requests, responses or status codes.
4. **Repository**: This is the storekeeper. It saves and fetches data. Today that's an array; in lesson 8 it's PostgreSQL. Nothing above it should care which.
5. **Feature folder**: This is one folder per part of the business (`menu/`, `orders/`), holding that feature's route file, service and repository together.

[[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers: Controllers, Services, Repositories]] explains these ideas for any framework. Here we do them the Express way.

## The shape we're aiming for
<!-- bite: f7860a9d-441e-4ec2-9143-ae5794b457f8 -->

```text
mama-put-api/
└── src/
    ├── server.ts              ← starts listening (tiny)
    ├── app.ts                 ← builds the Express app
    ├── menu/
    │   ├── menu.types.ts
    │   ├── menu.repository.ts
    │   ├── menu.service.ts
    │   └── menu.routes.ts
    ├── orders/
    │   ├── orders.types.ts
    │   ├── orders.repository.ts
    │   ├── orders.service.ts
    │   └── orders.routes.ts
    └── shared/
        ├── log-requests.ts
        ├── kitchen-only.ts
        ├── not-found.ts
        └── error-handler.ts
```

Why folders by **feature** and not by layer (one `routes/` folder, one `services/` folder)? Because when Mama asks "change how orders work", everything you need is in `orders/`. With layer folders you'd open three folders to change one feature. [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|Organising by Layer vs by Feature]] has the full argument.

Let's build it from the bottom up, starting with the storekeeper.

## The repository: where data lives
<!-- bite: 22b5c076-e7b3-4606-8ef6-45af257604c5 -->

`src/menu/menu.types.ts`:

```ts
export type Dish = {
  id: string;
  name: string;
  priceNaira: number;
  available: boolean;
};

export type NewDish = { name: string; priceNaira: number };
export type DishChanges = Partial<Omit<Dish, "id">>;
```

`src/menu/menu.repository.ts`:

```ts
import type { Dish, NewDish, DishChanges } from "./menu.types.ts";

const dishes: Dish[] = [
  { id: "1", name: "Jollof rice", priceNaira: 1500, available: true },
  { id: "2", name: "Beans and plantain", priceNaira: 1200, available: true },
  { id: "3", name: "Pounded yam and egusi", priceNaira: 2500, available: false },
];
let nextId = 4;

export const menuRepository = {
  async list(): Promise<Dish[]> {
    return [...dishes];
  },

  async findById(id: string): Promise<Dish | null> {
    return dishes.find((d) => d.id === id) ?? null;
  },

  async create(input: NewDish): Promise<Dish> {
    const dish: Dish = { id: String(nextId++), ...input, available: true };
    dishes.push(dish);
    return dish;
  },

  async update(id: string, changes: DishChanges): Promise<Dish | null> {
    const dish = dishes.find((d) => d.id === id);
    if (!dish) return null;
    Object.assign(dish, changes);
    return dish;
  },

  async remove(id: string): Promise<boolean> {
    const index = dishes.findIndex((d) => d.id === id);
    if (index === -1) return false;
    dishes.splice(index, 1);
    return true;
  },
};
```

Why `async`, when an array is instant? Because a database is *not* instant: every database call returns a promise. If the repository is async from day one, then when we swap the array for PostgreSQL in lesson 8, nothing that calls it has to change. We're shaping the storekeeper's job for the freezer we know is coming.

Notice what it **doesn't** do: no `req`, no `res`, no status codes, no rules. Just save and fetch.

## The service: where the rules live
<!-- bite: cb227ab0-489e-481a-9947-4f45d3f72a6d -->

`src/menu/menu.service.ts`:

```ts
import { menuRepository } from "./menu.repository.ts";
import type { NewDish, DishChanges } from "./menu.types.ts";

export const menuService = {
  async list(onlyAvailable: boolean) {
    const dishes = await menuRepository.list();
    return onlyAvailable ? dishes.filter((d) => d.available) : dishes;
  },

  get(id: string) {
    return menuRepository.findById(id);
  },

  add(input: NewDish) {
    return menuRepository.create(input);
  },

  change(id: string, changes: DishChanges) {
    return menuRepository.update(id, changes);
  },

  remove(id: string) {
    return menuRepository.remove(id);
  },
};
```

The menu service is thin, because the menu has few rules. That's fine. The orders service is where the cook really works.

`src/orders/orders.types.ts`:

```ts
export type OrderStatus = "pending" | "ready" | "collected";

export type Order = {
  id: string;
  dishId: string;
  quantity: number;
  totalNaira: number;
  status: OrderStatus;
};
```

(The orders repository looks just like the menu one, with `create`, `findById` and `updateStatus`. Write it yourself in the practice, or copy the menu one and adjust.)

`src/orders/orders.service.ts`:

```ts
import { ordersRepository } from "./orders.repository.ts";
import { menuService } from "../menu/menu.service.ts";
import type { Order } from "./orders.types.ts";

type PlaceOrderResult =
  | { ok: true; order: Order }
  | { ok: false; reason: "dish-not-found" | "dish-unavailable" | "bad-quantity" };

export const ordersService = {
  async place(dishId: string, quantity: number): Promise<PlaceOrderResult> {
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 20) {
      return { ok: false, reason: "bad-quantity" };
    }
    const dish = await menuService.get(dishId);
    if (!dish) return { ok: false, reason: "dish-not-found" };
    if (!dish.available) return { ok: false, reason: "dish-unavailable" };

    const order = await ordersRepository.create({
      dishId,
      quantity,
      totalNaira: dish.priceNaira * quantity,
      status: "pending",
    });
    return { ok: true, order };
  },

  get(id: string) {
    return ordersRepository.findById(id);
  },
};
```

Now you can point at the rules. "No more than 20 plates" is in one place. "Total is price times quantity" is in one place. And there isn't a single `res.status(...)` here. The service says *what went wrong* ("dish-unavailable") and leaves it to the waiter to decide how to say that in HTTP.

One more rule worth noticing: the orders service asks the **menu service** for the dish. It doesn't reach into the menu repository. Features talk to each other through their services, so the menu's rules (like "only available dishes") can't be skipped by accident.

## The route file: talking HTTP
<!-- bite: 416944f5-65e1-4983-b240-a5c6b77070ac -->

`src/menu/menu.routes.ts`:

```ts
import express from "express";
import type { Request, Response, NextFunction } from "express";
import { menuService } from "./menu.service.ts";
import { kitchenOnly } from "../shared/kitchen-only.ts";

export const menuRouter = express.Router();

async function loadDish(req: Request, res: Response, next: NextFunction) {
  const dish = await menuService.get(req.params.id);
  if (!dish) {
    res.status(404).json({ error: "Dish not found" });
    return;
  }
  res.locals.dish = dish;
  next();
}

menuRouter.get("/", async (req, res) => {
  res.json(await menuService.list(req.query.available === "true"));
});

menuRouter.get("/:id", loadDish, (req, res) => {
  res.json(res.locals.dish);
});

menuRouter.post("/", kitchenOnly, async (req, res) => {
  const dish = await menuService.add(req.body);
  res.status(201).location(`/menu/${dish.id}`).json(dish);
});

menuRouter.patch("/:id", kitchenOnly, loadDish, async (req, res) => {
  res.json(await menuService.change(req.params.id, req.body));
});

menuRouter.delete("/:id", kitchenOnly, loadDish, async (req, res) => {
  await menuService.remove(req.params.id);
  res.sendStatus(204);
});
```

And the waiter for orders, turning each service reason into a status code:

```ts
// src/orders/orders.routes.ts
import express from "express";
import { ordersService } from "./orders.service.ts";

export const ordersRouter = express.Router();

ordersRouter.post("/", async (req, res) => {
  const result = await ordersService.place(req.body.dishId, req.body.quantity);
  if (!result.ok) {
    const status = result.reason === "dish-not-found" ? 404 : 422;
    res.status(status).json({ error: result.reason });
    return;
  }
  res.status(201).location(`/orders/${result.order.id}`).json(result.order);
});
```

`422 Unprocessable Content` means "I understood your request, but I can't do it": the dish exists but the pot is finished.

The handlers are `async` now, because services return promises. In **Express 5**, if an async handler throws or its promise rejects, Express passes the error to your error handler for you. In Express 4 it didn't: the request just hung. That's one of the main reasons to use Express 5, and we lean on it in [[backend/frameworks/express/07-errors|lesson 7]].

## Building the app vs starting it
<!-- bite: 9b082a72-8b88-4992-9438-6eb5390c799f -->

`src/app.ts`:

```ts
import express from "express";
import { menuRouter } from "./menu/menu.routes.ts";
import { ordersRouter } from "./orders/orders.routes.ts";
import { logRequests } from "./shared/log-requests.ts";
import { notFound } from "./shared/not-found.ts";
import { errorHandler } from "./shared/error-handler.ts";

export function createApp() {
  const app = express();
  app.use(logRequests);
  app.use(express.json());
  app.use("/menu", menuRouter);
  app.use("/orders", ordersRouter);
  app.use(notFound);
  app.use(errorHandler);
  return app;
}
```

`src/server.ts`:

```ts
import { createApp } from "./app.ts";

const port = 3000;
createApp().listen(port, () => {
  console.log(`Mama Put API on http://localhost:${port}`);
});
```

Why two files? Because `createApp()` *builds* the app without *starting* it. A test can call `createApp()` and send fake requests to it, with no port, no network, and no "port already in use". [[backend/frameworks/express/16-testing|Lesson 16]] does exactly that. `server.ts` stays tiny on purpose: it's the only file that touches the real network.

And `app.ts` now reads like a table of contents. A new teammate can open it and see the whole app's order in ten lines.

## The TypeScript in this lesson
<!-- bite: 8e0dcc49-87a0-4e71-9935-2ce2e32a6283 -->

1. **`export type Dish = ...` and `export const menuRepository = ...`**: `export` makes something available to other files, which bring it in with `import`. Anything not exported stays private to its file, like the `dishes` array, which only the repository can touch.
2. **`Partial<Omit<Dish, "id">>`**: These are **utility types**, built-in tools that make a new type from an old one. `Omit<Dish, "id">` means "a Dish without the `id` field". `Partial<...>` means "all of those fields, but each one optional". Together: "any of name, price or available, but never the id", which is exactly what a change can contain.
3. **`async` and `Promise<Dish[]>`**: An `async` function always gives back a **promise**, an object that says "the answer will arrive later". `Promise<Dish[]>` means "a promise that will hold an array of Dish". Inside another async function, `await` waits for the promise and gives you the value: `const dishes = await menuRepository.list()`.
4. **`Dish | null`**: The `|` means "or". `Promise<Dish | null>` says "you'll get a Dish, or `null` if there isn't one", so TypeScript makes the caller deal with the missing case.
5. **`?? null`**: `a ?? b` means "use `a`, unless it's `null` or `undefined`, then use `b`". `find` gives `undefined` when nothing matches; we turn that into `null` so the repository always answers in one way.
6. **`{ id: String(nextId++), ...input, available: true }`**: The `...` is the **spread** operator. It copies every field of `input` into the new object. So this is "a new object with an id, everything from input, and available set to true".
7. **`Object.assign(dish, changes)`**: This copies the fields of `changes` onto the existing `dish`, changing it in place.
8. **`"pending" | "ready" | "collected"`**: A type made of exact text values. An `OrderStatus` can only ever be one of those three words; `"cooking"` would be an error. This is called a **union of literal types**.
9. **The `PlaceOrderResult` type**: `{ ok: true; order: Order } | { ok: false; reason: ... }` says the result is one of two shapes. After you check `if (!result.ok)`, TypeScript *knows* you're holding the failure shape and lets you read `result.reason`; in the other branch it lets you read `result.order`. This pattern is called a **discriminated union**, and `ok` is the field that tells the shapes apart.
10. **`Number.isInteger(quantity)`**: True only for whole numbers, so `2.5` plates is rejected.
11. **`import ... from "./menu.service.ts"`**: Imports of your own files start with `./` (this folder) or `../` (the folder above), and include the `.ts` ending because Node is running the TypeScript files directly.

## Common mistakes
<!-- bite: ac557911-741a-4f73-a7d6-f82b40686f0c -->

1. **Business rules in route files.** If you see `if (quantity > 20)` next to `res.status`, it's in the wrong layer.
2. **`req` or `res` inside a service.** The service then only works inside a request, and you can't test it or call it from a background job.
3. **One feature reaching into another's repository.** Ask the other feature's service instead.
4. **A `utils/` folder that eats everything.** "Shared" is only for things used by several features, like the error handler.
5. **Calling `listen` inside `app.ts`.** Then every test that imports the app starts a real server.

## Check your understanding
<!-- bite: 96563bf9-cda8-4f27-868a-c64a0249abb5 -->

1. Mama decides orders over 10 plates get 10% off. Which file changes?
2. Lesson 8 replaces the menu array with PostgreSQL. Which files change?
3. Why does the orders service return `{ ok: false, reason: "dish-unavailable" }` instead of calling `res.status(422)`?

<details>
<summary>Answers, after your attempt</summary>

1. Only `orders.service.ts`. It's a business rule.
2. Only `menu.repository.ts`. Because it was async from the start, the service and routes don't change.
3. Because a service doesn't know about HTTP. It says what went wrong in business words. The route file decides that "unavailable" means 422. The same service could be called from a test or a job where there's no response at all.

</details>

## Practice
<!-- bite: a125f03f-22cc-4a1a-86ac-0a53a7280466 -->

1. Finish the split: write `orders.repository.ts`, and move `logRequests`, `kitchenOnly`, `notFound` and `errorHandler` into `src/shared/`, one per file.
2. Add `GET /orders/:id` and `PATCH /orders/:id/status` to `orders.routes.ts`. Put the rule "an order can only go pending → ready → collected, never backwards" in `orders.service.ts`, and answer 409 when it's broken.

**Done when** `server.ts` is under ten lines, no file outside `*.routes.ts` and `shared/` imports anything from Express, and `curl` shows that marking a collected order as "pending" gets 409.

## Your project so far
<!-- bite: ca82787e-4ace-4c0e-9f2f-3bec795ca322 -->

```text
mama-put-api/
├── package.json
├── package-lock.json
├── tsconfig.json
└── src/
    ├── server.ts                 ← createApp().listen(3000)
    ├── app.ts                    ← createApp(): middleware and routers in order
    ├── menu/
    │   ├── menu.types.ts         ← Dish, NewDish, DishChanges
    │   ├── menu.repository.ts    ← the dishes array; list, findById, create, update, remove
    │   ├── menu.service.ts       ← menu rules (list only available, etc.)
    │   └── menu.routes.ts        ← menuRouter, loadDish, HTTP in and out
    ├── orders/
    │   ├── orders.types.ts       ← Order, OrderStatus
    │   ├── orders.repository.ts  ← the orders array; create, findById, updateStatus
    │   ├── orders.service.ts     ← place(): quantity limits, dish checks, the total
    │   └── orders.routes.ts      ← ordersRouter, service reasons → status codes
    └── shared/
        ├── log-requests.ts       ← the request logger
        ├── kitchen-only.ts       ← the staff-key check
        ├── not-found.ts          ← the catch-all 404
        └── error-handler.ts      ← the four-argument error handler
```

Each file now has one job. Only `*.routes.ts`, `app.ts` and `shared/` import Express; services and repositories don't know it exists.

## Before moving on
<!-- bite: b1591e8e-26fb-4bc6-9f55-ad66fca22291 -->

Each file now has one job: routes talk HTTP, services hold rules, repositories hold data, and `app.ts` puts them in order.

But look at this line in `orders.service.ts`: `import { menuService } from "../menu/menu.service.ts"`. The orders service grabs its own dependencies. So in a test, how do you give it a fake menu? Or in lesson 8, a repository that needs a database connection? You'd have to change the imports. The fix is to *hand* each piece what it needs instead of letting it grab, and that's wiring dependencies, the next lesson.

## Related
<!-- bite: cb863691-9df8-422f-a7cd-c46d5c4206d7 -->

- [[backend/frameworks/express/05-wiring-dependencies|Next: Wiring Dependencies]]
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers: Controllers, Services, Repositories]]
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|Organising by Layer vs by Feature]]

## About this lesson
<!-- bite: 703bd3a1-e3d8-4668-95fa-a421d5ea235f -->

**Level:** Intermediate. Lesson 4 of [[backend/frameworks/express/index|Express]]. Covers feature folders, the three layers, async repositories ahead of a database, service results instead of HTTP inside services, and the `app.ts` / `server.ts` split.
