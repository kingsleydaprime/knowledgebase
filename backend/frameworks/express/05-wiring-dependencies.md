---
id: 692006ca-0458-448c-8595-9dba9e9bb29f
---

# Wiring Dependencies

**Wiring dependencies means handing each part of your app the things it needs (its dependencies) from the outside, instead of letting it grab them itself.** Express has no built-in system for this, unlike NestJS or Spring. So in Express you do it with plain functions, in one place at startup, and that one place is the only file that knows how the whole app fits together.

## Before you start
<!-- bite: 0a88b4e7-aba8-4dd5-94af-000da3423eed -->

You should have the feature folders from [[backend/frameworks/express/04-structuring-an-express-app|lesson 4]]: routes, a service and a repository for `menu/` and `orders/`, plus `app.ts` and `server.ts`.

After this lesson you will be able to:

1. Turn a module that imports its own dependencies into a factory function that receives them.
2. Write a composition root: one function in `server.ts` that builds and connects everything.
3. Swap a real piece for a fake one without changing any other file.

## Where we stopped
<!-- bite: 02427e4f-ed0b-4576-93c9-e599b49889ad -->

Lesson 4 ended on this line in `orders.service.ts`:

```ts
import { menuService } from "../menu/menu.service.ts";
```

It looks harmless. But it means the orders service decides for itself *which* menu it uses, and the answer is always "the real one". Three problems come out of that:

1. **Testing.** To test "you can't order an unavailable dish", you want a fake menu with exactly one unavailable dish. You can't give it one, because the service imports the real menu.
2. **The database.** In lesson 8 the repositories need a database connection. Where does each one get it? If every file imports a global connection, you can't open the connection late, close it cleanly, or point tests at a different database.
3. **Hidden shape.** To know what the orders service depends on, you have to read its imports. Nothing in its signature tells you.

## The kid version
<!-- bite: e05caf3c-b3f8-4dfc-819f-ef9765110c92 -->

Think of the cook in Mama's kitchen again. In lesson 4, the cook walked to the market himself every morning and bought whatever rice he found. If you wanted him to try a new rice, you had to change his route to the market.

Now Mama buys the ingredients and **hands** them to the cook when he arrives. The cook just cooks with what he's given. Want to try a new rice? Mama hands him a different bag. The cook doesn't change at all.

**Where the picture stops working.** In code, "handing over" happens once, when the app starts, not every morning. After that, every request uses the same pieces.

## Terms used in wiring
<!-- bite: 1a01df0b-03d7-4141-9d97-f9cbe7765b45 -->

1. **Dependency**: This is something a piece of code needs in order to work. The orders service needs the menu service and the orders repository. Those are its dependencies.
2. **Factory function**: This is a function that builds and returns something. `createOrdersService(deps)` builds an orders service from the dependencies you pass in.
3. **Dependency injection**: This is also called **DI**. It is the name for handing dependencies in from the outside instead of importing them inside. "Injection" sounds big; in Express it is just passing arguments.
4. **Composition root**: This is the one place, usually at startup, where every real piece is built and connected. In our app it's a function in `server.ts`.
5. **Fake**: This is a simple stand-in for a real dependency, used in tests. A fake menu service might just return one hard-coded dish.

[[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|Dependency Injection and Wiring]] explains the idea in any language. Here's the Express way.

## Step 1: describe what each piece needs
<!-- bite: 308f1d2e-82b7-473c-b733-61dc4ad0f935 -->

First, give each dependency a type that says what it can do, not which file it comes from. Add to `src/menu/menu.types.ts`:

```ts
export type MenuRepository = {
  list(): Promise<Dish[]>;
  findById(id: string): Promise<Dish | null>;
  create(input: NewDish): Promise<Dish>;
  update(id: string, changes: DishChanges): Promise<Dish | null>;
  remove(id: string): Promise<boolean>;
};
```

This type is a promise about behaviour: "anything that can do these five things is a menu repository". The in-memory array can. The PostgreSQL one in lesson 8 will. A test fake can. The service will only ever see this type, never the file behind it.

## Step 2: turn modules into factories
<!-- bite: de0c6808-3695-4bb4-a456-d194db008dcb -->

`src/menu/menu.repository.ts` becomes a function that returns a fresh repository:

```ts
import type { Dish, MenuRepository } from "./menu.types.ts";

export function createInMemoryMenuRepository(seed: Dish[] = []): MenuRepository {
  const dishes = [...seed];
  let nextId = dishes.length + 1;

  return {
    async list() {
      return [...dishes];
    },
    async findById(id) {
      return dishes.find((d) => d.id === id) ?? null;
    },
    async create(input) {
      const dish: Dish = { id: String(nextId++), ...input, available: true };
      dishes.push(dish);
      return dish;
    },
    async update(id, changes) {
      const dish = dishes.find((d) => d.id === id);
      if (!dish) return null;
      Object.assign(dish, changes);
      return dish;
    },
    async remove(id) {
      const index = dishes.findIndex((d) => d.id === id);
      if (index === -1) return false;
      dishes.splice(index, 1);
      return true;
    },
  };
}
```

Two good things happened already. The starting dishes come in as `seed`, so a test can start with exactly the dishes it needs. And each call makes a **new** repository with its own array, so one test can't leave dishes behind for the next.

The service receives its repository:

```ts
// src/menu/menu.service.ts
import type { MenuRepository, NewDish, DishChanges } from "./menu.types.ts";

export function createMenuService(deps: { menuRepository: MenuRepository }) {
  const { menuRepository } = deps;
  return {
    async list(onlyAvailable: boolean) {
      const dishes = await menuRepository.list();
      return onlyAvailable ? dishes.filter((d) => d.available) : dishes;
    },
    get: (id: string) => menuRepository.findById(id),
    add: (input: NewDish) => menuRepository.create(input),
    change: (id: string, changes: DishChanges) => menuRepository.update(id, changes),
    remove: (id: string) => menuRepository.remove(id),
  };
}

export type MenuService = ReturnType<typeof createMenuService>;
```

`ReturnType<typeof createMenuService>` means "whatever this function returns". We get the service's type for free, without writing it twice.

And now the line that started all this. The orders service *receives* the menu:

```ts
// src/orders/orders.service.ts
import type { MenuService } from "../menu/menu.service.ts";
import type { OrdersRepository } from "./orders.types.ts";

export function createOrdersService(deps: {
  ordersRepository: OrdersRepository;
  menuService: MenuService;
}) {
  const { ordersRepository, menuService } = deps;
  return {
    async place(dishId: string, quantity: number) {
      // ...the same rules as lesson 4, using menuService and ordersRepository
    },
    get: (id: string) => ordersRepository.findById(id),
  };
}
```

Look at the import. It's `import type`: the orders service only borrows the *shape* of a menu service. It no longer loads the menu code at all. And its parameters now say, in one place, exactly what it needs.

## Step 3: routers receive their services
<!-- bite: a50694f6-f04f-428b-ab6b-b4d8d8dd040a -->

```ts
// src/menu/menu.routes.ts
import express from "express";
import type { MenuService } from "./menu.service.ts";
import { kitchenOnly } from "../shared/kitchen-only.ts";

export function createMenuRouter(deps: { menuService: MenuService }) {
  const { menuService } = deps;
  const router = express.Router();

  router.get("/", async (req, res) => {
    res.json(await menuService.list(req.query.available === "true"));
  });

  // ...loadDish and the other routes, exactly as before, using menuService

  return router;
}
```

The handlers inside don't change at all. They still say `menuService.list(...)`. The only difference is where `menuService` came from: a parameter instead of an import.

`createApp` receives everything the routers need:

```ts
// src/app.ts
import express from "express";
import type { MenuService } from "./menu/menu.service.ts";
import type { OrdersService } from "./orders/orders.service.ts";
import { createMenuRouter } from "./menu/menu.routes.ts";
import { createOrdersRouter } from "./orders/orders.routes.ts";
import { logRequests } from "./shared/log-requests.ts";
import { notFound } from "./shared/not-found.ts";
import { errorHandler } from "./shared/error-handler.ts";

export type AppDeps = {
  menuService: MenuService;
  ordersService: OrdersService;
};

export function createApp(deps: AppDeps) {
  const app = express();
  app.use(logRequests);
  app.use(express.json());
  app.use("/menu", createMenuRouter(deps));
  app.use("/orders", createOrdersRouter(deps));
  app.use(notFound);
  app.use(errorHandler);
  return app;
}
```

## Step 4: the composition root
<!-- bite: 79767957-0d13-4fb2-a8b2-305b5ecfb695 -->

Now everything receives and nothing grabs. Someone has to do the building. That's `server.ts`, and only `server.ts`:

```ts
// src/server.ts
import { createApp } from "./app.ts";
import { createInMemoryMenuRepository } from "./menu/menu.repository.ts";
import { createInMemoryOrdersRepository } from "./orders/orders.repository.ts";
import { createMenuService } from "./menu/menu.service.ts";
import { createOrdersService } from "./orders/orders.service.ts";

function buildDeps() {
  const menuRepository = createInMemoryMenuRepository([
    { id: "1", name: "Jollof rice", priceNaira: 1500, available: true },
    { id: "2", name: "Beans and plantain", priceNaira: 1200, available: true },
  ]);
  const ordersRepository = createInMemoryOrdersRepository();

  const menuService = createMenuService({ menuRepository });
  const ordersService = createOrdersService({ ordersRepository, menuService });

  return { menuService, ordersService };
}

const app = createApp(buildDeps());
app.listen(3000, () => console.log("Mama Put API on http://localhost:3000"));
```

Read `buildDeps` from top to bottom and you're reading the app's whole wiring diagram: repositories first, then the services that use them, then the app that uses the services. It's the only place in the codebase that names a *real* implementation.

So when lesson 8 brings PostgreSQL, this is the change:

```ts
const menuRepository = createPgMenuRepository(pool);   // was createInMemoryMenuRepository(...)
```

One line, in one file. Every service, router and test carries on.

## What this buys you: a test with a fake
<!-- bite: 0d025392-9a19-4e65-8743-f18d86e00a50 -->

Here's the payoff from the first problem. This test needs no server and no real menu:

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { createOrdersService } from "./orders.service.ts";
import { createInMemoryOrdersRepository } from "./orders.repository.ts";

test("can't order a dish that's finished", async () => {
  const fakeMenu = {
    get: async () => ({ id: "9", name: "Ofada", priceNaira: 2000, available: false }),
  };
  const orders = createOrdersService({
    ordersRepository: createInMemoryOrdersRepository(),
    menuService: fakeMenu as any,
  });

  const result = await orders.place("9", 1);

  assert.deepEqual(result, { ok: false, reason: "dish-unavailable" });
});
```

Run it with `node --test src/orders/orders.service.test.ts`. The fake menu does one thing: say "this dish exists, but it's finished". The test is about the orders rule and nothing else. (`as any` is there because the fake only has `get`. In [[backend/frameworks/express/16-testing|lesson 16]] we write fakes that match the full type.)

## Why not a container?
<!-- bite: fce893c5-0cae-4122-b5b9-beb7f9e3961b -->

NestJS and Spring have a **DI container**: a library that reads your classes and builds them in the right order automatically. Express doesn't, and you don't need one. For an app this size, `buildDeps` is twenty readable lines that anyone can follow, with no magic and no decorators. If the wiring ever gets painful (hundreds of services), libraries like `awilix` exist. Most Express apps never get there.

## The TypeScript in this lesson
<!-- bite: d6474cdb-1ae7-4bc6-9286-7df09ce8e1e9 -->

1. **`export type MenuRepository = { list(): Promise<Dish[]>; ... }`**: A type can describe functions, not just data. `list(): Promise<Dish[]>` means "something called `list` that takes nothing and gives back a promise of dishes". Any object with all five of these functions *is* a MenuRepository, whatever file it came from. TypeScript only cares about the shape. This is sometimes called **structural typing**.
2. **`function createInMemoryMenuRepository(seed: Dish[] = []): MenuRepository`**: Two new things. `= []` is a **default value**: if you call it without a seed, `seed` is an empty array. And `: MenuRepository` after the brackets is the **return type**: TypeScript checks that what we return really has all five functions.
3. **Closures again**: The object it returns has functions that use `dishes` and `nextId`, variables that live inside `createInMemoryMenuRepository`. Each call makes fresh copies of those variables, which is why each repository has its own private array. Nothing outside can touch `dishes` except through the five functions.
4. **`deps: { menuRepository: MenuRepository }`**: The parameter is an object with named fields. Passing objects instead of a list of arguments means the order doesn't matter, and adding a dependency later doesn't break any caller.
5. **`const { menuRepository } = deps`**: Destructuring again, pulling the field out so we can write `menuRepository` instead of `deps.menuRepository`.
6. **`get: (id: string) => menuRepository.findById(id)`**: An arrow function without curly braces gives back whatever is after the arrow. It's short for `(id) => { return menuRepository.findById(id); }`.
7. **`ReturnType<typeof createMenuService>`**: Read it from the inside. `typeof createMenuService` means "the type of this function". `ReturnType<...>` means "the type of whatever that function gives back". So `MenuService` is the shape of a menu service, worked out from the code, and it can never be out of date.
8. **`fakeMenu as any`**: `any` switches TypeScript's checking off for that value. We use it here because the fake only has `get`, not every function a real menu service has. It's fine in a small test, and it's a smell anywhere else.
9. **`test("...", async () => { ... })` and `assert.deepEqual(a, b)`**: From Node's built-in test runner. `test` names a test and runs the function. `assert.deepEqual` checks two values have exactly the same contents, field by field, and fails the test if not.

## Common mistakes
<!-- bite: cebce6cf-87f2-4971-865a-bf09785db84b -->

1. **Half wiring.** The service receives a repository but still imports a global logger or config. Then that one thing can't be swapped. Pass it in too.
2. **Building dependencies inside handlers.** `createMenuService(...)` inside a route runs on every request, and each request gets its own empty repository. Build once, at startup.
3. **Real implementations imported outside the composition root.** If a route file imports `createInMemoryMenuRepository`, the wiring has leaked.
4. **Passing everything to everything.** Each factory should ask only for what it uses. A long `deps` list is a sign the piece does too much.

## Check your understanding
<!-- bite: eeebb4c3-064e-41e7-87ae-ef8a52eba4c4 -->

1. Which file is allowed to import `createInMemoryMenuRepository`, and why only that one?
2. Why does `orders.service.ts` use `import type` for the menu service?
3. In the old version (lesson 4), what would you have had to do to test the orders rules with a fake menu?

<details>
<summary>Answers, after your attempt</summary>

1. `server.ts`, the composition root (and tests, which build their own). It's the only place that decides which real implementation the app uses, so swapping one means changing one line.
2. It only needs the *shape* of a menu service to check its code. The actual menu service arrives as an argument, so it never has to load the menu code.
3. Something awkward: change the import, or use a tool that intercepts imports. With wiring, you just pass a different object.

</details>

## Practice
<!-- bite: 9c4680d2-3aec-4763-b0bd-2051c53ec869 -->

1. Convert the orders repository and the orders router to factories, the same way as the menu.
2. Pass the staff key for `kitchenOnly` in through `createApp` instead of writing `"jollof123"` in the file. (Hint: `kitchenOnly` becomes `createKitchenOnly(staffKey)`, which returns the middleware.)
3. Write one more test with a fake menu: ordering 21 plates gives `bad-quantity`, and the fake menu's `get` is never called. (Hint: have the fake count its calls.)

**Done when** `grep -rn "createInMemory" src` shows matches only in `server.ts` and in test files, and `node --test` passes both tests.

## Your project so far
<!-- bite: 29115fa2-6626-4c0f-b098-2cf7b92d6057 -->

```text
mama-put-api/
├── package.json
├── package-lock.json
├── tsconfig.json
└── src/
    ├── server.ts                      ← buildDeps(): the composition root, then listen
    ├── app.ts                         ← createApp(deps), and the AppDeps type
    ├── menu/
    │   ├── menu.types.ts              ← Dish, NewDish, DishChanges, MenuRepository
    │   ├── menu.repository.ts         ← createInMemoryMenuRepository(seed)
    │   ├── menu.service.ts            ← createMenuService(deps), MenuService type
    │   └── menu.routes.ts             ← createMenuRouter(deps)
    ├── orders/
    │   ├── orders.types.ts            ← Order, OrderStatus, OrdersRepository
    │   ├── orders.repository.ts       ← createInMemoryOrdersRepository()
    │   ├── orders.service.ts          ← createOrdersService(deps), OrdersService type
    │   ├── orders.service.test.ts     ← the first tests, using a fake menu
    │   └── orders.routes.ts           ← createOrdersRouter(deps)
    └── shared/
        ├── log-requests.ts
        ├── kitchen-only.ts            ← createKitchenOnly(staffKey) after the practice
        ├── not-found.ts
        └── error-handler.ts
```

What changed since lesson 4: every `create...` is now a function that **receives** its dependencies, and `server.ts` is the only file that builds the real ones. Tests sit next to the file they test, ending in `.test.ts`.

## Before moving on
<!-- bite: 104cb4c3-9d58-4c4b-80f1-31395795bdc7 -->

Every piece of Mama Put API now receives what it needs, and `server.ts` is the one place that builds and connects it all. That made our first real test possible.

Now remember the hole from [[backend/frameworks/express/02-routing|lesson 2]]? We still trust whatever the client sends. `{"priceNaira": "free"}` with no name goes straight to the repository. Wiring made the inside of the app clean. Now we have to guard the door, and that's validation, the next lesson.

## Related
<!-- bite: a8740070-8df2-4755-b4f2-1c5a8583057d -->

- [[backend/frameworks/express/06-validation|Next: Validation]]
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|Dependency Injection and Wiring]] — the idea in every language
- [[backend/frameworks/nestjs/index|NestJS]] — what a DI container does for you, and what it costs

## About this lesson
<!-- bite: 5584f8fc-0afe-49e9-9cd1-4867ab70a91e -->

**Level:** Intermediate. Lesson 5 of [[backend/frameworks/express/index|Express]]. Covers dependency types, factory functions, `ReturnType` for service types, routers and `createApp` that receive their dependencies, the composition root in `server.ts`, and a first unit test with a fake.
