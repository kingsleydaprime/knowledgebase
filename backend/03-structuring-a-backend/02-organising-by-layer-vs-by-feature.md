# Organising by Layer vs by Feature

**[Beginner→Intermediate]** — the folder-structure argument every team has, usually badly. It looks like bikeshedding and isn't: it determines how far you have to scroll to make one change, and how easy it is to delete something. This lesson shows both layouts, **with the wiring, in Express, NestJS, React, Django and Flask** — and a companion lesson does the same for Go, Java, Rust, C, C++ and C#.

## Before you start

You can already:

- Build a create-and-list endpoint in at least one of the frameworks below.
- Say what a controller, a service and a repository are each responsible for → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]].

After this lesson you will be able to:

1. Lay out the same small app both ways in Express, NestJS, React, Django and Flask.
2. Write the **registration code** each framework needs to plug a feature in — `app.use`, `imports: []`, `INSTALLED_APPS`, `register_blueprint`, the router — and say why it lives in exactly one place.
3. Turn a forbidden import between features into a **lint failure**, not a code-review argument.
4. Choose a layout for a given codebase and defend the choice.

**Study route.** Sections 1–5 are the core idea. Then read **only the framework sections you use** — §8 (React) is required if you do any frontend work. Go, Java, Rust, C, C++ and C# are in a companion lesson, [[backend/03-structuring-a-backend/02b-organising-by-feature-in-compiled-languages|organising by feature in compiled languages]]. Stop at *Check your understanding* and answer before opening anything. The practice task at the end is the actual finish line.

**Labs.** The verified examples are in `labs/layer-vs-feature/eslint/` (Express and React), `labs/layer-vs-feature/django-by-feature/`, `labs/layer-vs-feature/django-by-layer/`, `labs/layer-vs-feature/flask/`, and the compiled languages' labs are listed in the companion lesson. From the vault root, `python3 labs/run.py layer-vs-feature/flask` (for example) runs one and checks this page still matches it.

## The kid version first

You're organising a toolbox.

- **By type:** all screwdrivers in one drawer, all wrenches in another, all screws in a third. Tidy. But to fix the bike you open four drawers.
- **By job:** a "bike box", a "plumbing box", each holding everything for that job. To fix the bike you grab one box. But now you own three screwdrivers.

Neither is wrong. **The right one depends on whether you more often do "one job" or "one type of thing."** In software you almost always work on one *feature* at a time — which is a strong hint.

**Where the analogy stops working.** A spare screwdriver costs money; a copied ten-line helper costs nothing to own, but costs you later when the two copies drift apart. And a box on a shelf does nothing until you plug it in — in software, every feature box must be **plugged into the app** somewhere. That plug point is most of what the framework sections below are about.

## 1. Why this exists — one change, counted

The running example for the whole lesson is a small shop with three features: **users**, **products** and **orders**.

The ticket: *"Let customers apply a discount code to an order."* That change needs a new field on the order, validation for the code, a rule in the business logic, a database column, and a test. Before reading further, **predict how many folders you'd touch in each layout below.**

<details>
<summary>After your prediction</summary>

By layer: `controllers/`, `services/`, `repositories/`, `dtos/`, `tests/` — **five folders**, each holding files for all three features you have to skip past. By feature: `orders/` — **one folder**. Nothing else in the codebase changed, so nothing else should have been opened.

</details>

## Terms used in this lesson

1. **Layer**: This is also known as a **technical role**. It is a kind of job a piece of code does regardless of which feature it serves — handling HTTP (controller), business rules (service), talking to the database (repository). A layer folder groups every file that does the same kind of job.
2. **Feature**: This is also known as a **domain module**, a **slice**, or, in Django, an **app**. It is one area of the product a user would recognise, such as orders or users. A feature folder groups every file that serves that area, whatever its technical role.
3. **Change locality**: This is how close together the files are that one change touches. High change locality means one ticket edits one folder.
4. **Public API of a feature**: This is the small set of things a feature allows other code to use, usually re-exported from one file (`index.ts`, `services.py`, a Nest module's `exports`). Everything else in the folder is private by agreement, or by a lint rule.
5. **Composition root**: This is also known as the **wiring point** or **registration point**. It is the one place in the app that knows which features exist and plugs them in — mounting routers, importing modules, listing installed apps. Deleting a feature means deleting its folder and its one line here.
6. **Shared folder**: This is also known as `shared/`, `common/`, `lib/` or `core/`. It holds code that several features genuinely use and that knows nothing about any of them — a database client, a button, an error type.
7. **Boundary enforcement**: This is a tool that makes a forbidden import fail the build. In this lesson that is ESLint's `import/no-restricted-paths` for JavaScript and TypeScript, NestJS's own module system, and `import-linter` for Python. In Go, Java, Rust, C and C++ the compiler or the build system does it, with no extra tool.

## 2. The two layouts

**By layer (by technical role):**
```
src/
├── controllers/   orders.controller.ts  users.controller.ts  payments.controller.ts
├── services/      orders.service.ts     users.service.ts     payments.service.ts
├── repositories/  orders.repo.ts        users.repo.ts        payments.repo.ts
└── dtos/          ...
```

**By feature (by domain concept):**
```
src/
├── orders/     orders.controller.ts  orders.service.ts  orders.repo.ts  orders.dto.ts
├── users/      users.controller.ts   users.service.ts   users.repo.ts
├── payments/   ...
└── shared/     database, logging, auth middleware
```

## 3. The case for by-feature

**1. Change locality.** Adding a field to an order touches the controller, service, repository, DTO, and tests. By feature, that's **one folder**. By layer, it's five folders and a lot of scrolling. Since most work is feature work, by-feature optimises for the common case.

**2. Deletability.** Killing a feature is `rm -rf src/orders/` plus removing one registration line. By layer, you hunt through six directories and *will* leave orphans behind. **How easily you can delete something is an underrated measure of how well it's structured.**

**3. It makes coupling visible.** If `orders/` imports from `payments/internals`, that's obvious in a diff and reviewable. By layer, `orders.service` importing `payments.service` looks identical to every other import — everything is already in the same folder, so nothing stands out.

**4. It's the extraction seam.** If a feature ever becomes its own service, a feature folder is already the boundary. A layer layout has to be untangled first. → [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|monolith → services]]

**5. It scales with the team.** Teams own features, not layers. Ownership maps to folders, and `CODEOWNERS` becomes trivial.

## 4. The case for by-layer

Not nothing, and worth stating fairly:

- **Small projects.** Under ~15 files, feature folders each containing two files is more ceremony than the flat version.
- **It's obvious where things go** when the layers are rigid — no debate about which feature something belongs to.
- **Framework convention.** Rails is by-layer at the top (`app/controllers`, `app/models`), and fighting your framework's conventions has a real cost in tooling and onboarding. Note that **Django is the opposite**: its "apps" are feature folders, and the layers are files inside each one — see §9.

**The verdict: start by-feature, or move to it the moment you have more than a handful of features.** The by-layer structure looks tidy at the start and gets worse every month; by-feature looks slightly over-engineered at the start and gets better. The tell that you needed it a while ago: **a `services/` folder with twenty-five files in it that you scroll to find things in.** A folder is a bad index past about a dozen entries.

## 5. The three questions every framework answers

Every framework section below answers the same three questions. Once you see them, the five frameworks stop looking like five different topics.

1. **Where do the files live?** The folder tree.
2. **Where is the feature plugged in?** The composition root — one file, one line per feature.
3. **What stops one feature reaching into another's internals?** A lint rule, or the framework itself.

The labels on the code blocks below mean: **verified** — the code was run in a scratch project and behaved as described; **fragment** — the wiring only, not a complete runnable project.

---

## 6. Express (TypeScript)

Express has no opinion at all, so you choose the layout and you write the composition root yourself.

### By layer

```
src/
├── app.ts                  creates the app, mounts routes/index.ts
├── server.ts               app.listen(...)
├── routes/
│   ├── index.ts            mounts every router — the composition root
│   ├── orders.routes.ts
│   └── users.routes.ts
├── controllers/
│   ├── orders.controller.ts
│   └── users.controller.ts
├── services/
├── repositories/
└── validators/
```

```ts
// src/routes/orders.routes.ts — fragment
import { Router } from "express";
import * as ordersController from "../controllers/orders.controller";

export const ordersRouter = Router();
ordersRouter.get("/", ordersController.list);
ordersRouter.post("/", ordersController.create);
```

```ts
// src/routes/index.ts — fragment
import { Router } from "express";
import { ordersRouter } from "./orders.routes";
import { usersRouter } from "./users.routes";

export const api = Router();
api.use("/orders", ordersRouter);
api.use("/users", usersRouter);
```

```ts
// src/app.ts — fragment
import express from "express";
import { api } from "./routes";

export const app = express();
app.use(express.json());
app.use("/api", api);
```

### By feature

```
src/
├── app.ts                       composition root: one app.use per feature
├── server.ts
├── features/
│   ├── orders/
│   │   ├── index.ts             public API: the router factory + public types
│   │   ├── orders.controller.ts
│   │   ├── orders.service.ts
│   │   ├── orders.repository.ts
│   │   ├── orders.schema.ts     request validation
│   │   └── orders.test.ts
│   └── users/
│       ├── index.ts
│       └── ...
└── shared/
    ├── db.ts
    ├── errors.ts
    └── middleware/auth.ts
```

Each feature exports **one function that builds its router**. The feature wires its own service and repository inside, so `app.ts` never learns about them:

```ts
// src/features/orders/index.ts — fragment
import { Router } from "express";
import { db } from "../../shared/db";
import { requireAuth } from "../../shared/middleware/auth";
import { makeOrdersController } from "./orders.controller";
import { OrdersRepository } from "./orders.repository";
import { OrdersService } from "./orders.service";

export function ordersRouter(): Router {
  const service = new OrdersService(new OrdersRepository(db));
  const controller = makeOrdersController(service);

  const router = Router();
  router.use(requireAuth);
  router.get("/", controller.list);
  router.post("/", controller.create);
  return router;
}

export type { Order } from "./orders.types";
```

```ts
// src/app.ts — fragment
import express from "express";
import { ordersRouter } from "./features/orders";
import { usersRouter } from "./features/users";
import { errorHandler } from "./shared/errors";

export const app = express();
app.use(express.json());
app.use("/api/users", usersRouter());
app.use("/api/orders", ordersRouter());
app.use(errorHandler); // error handlers go last
```

Deleting orders is now `rm -rf src/features/orders` plus two lines in `app.ts`, and the type checker lists anything else that still referenced it.

### Enforcing the boundary — verified

`eslint-plugin-import`'s `no-restricted-paths` rule works on **resolved file paths**, so it catches `../users/users.repository` and `@/features/users/users.repository` alike. The zones are generated from the folder listing, so adding a feature folder protects it automatically:

```bash
npm i -D eslint eslint-plugin-import typescript-eslint eslint-import-resolver-typescript
```

```js
// eslint.config.js — verified with ESLint 9.39, eslint-plugin-import 2.32
import { readdirSync } from "node:fs";
import importPlugin from "eslint-plugin-import";
import tseslint from "typescript-eslint";

// One zone per (feature, other feature) pair: a feature may import another
// feature's index.ts, and nothing else from it.
const features = readdirSync("./src/features");
const featureZones = features.flatMap((feature) =>
  features
    .filter((other) => other !== feature)
    .map((other) => ({
      target: `./src/features/${feature}`,
      from: `./src/features/${other}`,
      except: ["./index.ts"],
      message: `Import ${other} through features/${other}/index.ts, not its internals.`,
    })),
);

export default tseslint.config({
  files: ["src/**/*.{ts,tsx}"],
  languageOptions: { parser: tseslint.parser },
  plugins: { import: importPlugin },
  settings: { "import/resolver": { typescript: true } },
  rules: {
    "import/no-restricted-paths": [
      "error",
      {
        zones: [
          ...featureZones,
          { target: "./src/shared", from: "./src/features", message: "shared/ must not depend on a feature." },
        ],
      },
    ],
  },
});
```

Run from the project root (the `readdirSync` path is relative to it): `npx eslint src`. Against a test tree, `import { findUser } from "../users"` passed, and these three failed:

```
src/features/orders/bad-alias.ts
  1:26  error  Unexpected path "@/features/users/users.repository" imported in restricted zone. Import users through features/users/index.ts, not its internals  import/no-restricted-paths
src/features/orders/bad.ts
  1:26  error  Unexpected path "../users/users.repository" imported in restricted zone. ...
src/shared/bad-shared.ts
  1:26  error  Unexpected path "../features/users" imported in restricted zone. shared/ must not depend on a feature  import/no-restricted-paths
```

---

## 7. NestJS

Nest is the one framework here that is **by-feature out of the box**, and it enforces part of the boundary at runtime for you.

### By feature — the default

```bash
nest new shop
nest g resource users      # asks: REST API? generate CRUD entry points?
nest g resource orders
```

```
src/
├── main.ts
├── app.module.ts            composition root — the CLI adds each module to imports
├── users/
│   ├── dto/
│   ├── entities/
│   ├── users.controller.ts
│   ├── users.module.ts
│   └── users.service.ts
└── orders/
    ├── dto/
    │   ├── create-order.dto.ts
    │   └── update-order.dto.ts
    ├── entities/order.entity.ts
    ├── orders.controller.ts
    ├── orders.controller.spec.ts
    ├── orders.module.ts
    ├── orders.service.ts
    └── orders.service.spec.ts
```

The **module file is the feature's public API**. `providers` are private; only what is listed in `exports` can be injected by another module:

```ts
// src/users/users.module.ts — fragment
import { Module } from "@nestjs/common";
import { UsersController } from "./users.controller";
import { UsersRepository } from "./users.repository";
import { UsersService } from "./users.service";

@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService], // UsersRepository stays private to this module
})
export class UsersModule {}
```

```ts
// src/orders/orders.module.ts — fragment
import { Module } from "@nestjs/common";
import { UsersModule } from "../users/users.module";
import { OrdersController } from "./orders.controller";
import { OrdersService } from "./orders.service";

@Module({
  imports: [UsersModule], // makes UsersService injectable here
  controllers: [OrdersController],
  providers: [OrdersService],
})
export class OrdersModule {}
```

```ts
// src/app.module.ts — fragment
import { Module } from "@nestjs/common";
import { OrdersModule } from "./orders/orders.module";
import { UsersModule } from "./users/users.module";

@Module({
  imports: [UsersModule, OrdersModule],
})
export class AppModule {}
```

If `OrdersService` asks for `UsersRepository` in its constructor, the app refuses to start with *"Nest can't resolve dependencies of the OrdersService…"*. **That error is the boundary working.** Fix it by asking for `UsersService` instead, not by exporting the repository.

**What Nest does not enforce.** Its check is on dependency injection only. A plain TypeScript `import { hashPassword } from "../users/users.utils"` compiles and runs fine. Add the ESLint rule from §6, with `except: ["./users.module.ts", "./dto"]` style exceptions, if you want imports policed too.

To group features under one folder, generate with a path — `nest g resource modules/orders` — and the files land in `src/modules/orders/`.

### By layer — possible, but fighting the framework

```
src/
├── app.module.ts            registers everything below
├── controllers/   orders.controller.ts   users.controller.ts
├── services/      orders.service.ts      users.service.ts
├── repositories/  orders.repository.ts   users.repository.ts
└── dto/
```

```ts
// src/app.module.ts — fragment
@Module({
  controllers: [OrdersController, UsersController],
  providers: [OrdersService, UsersService, OrdersRepository, UsersRepository],
})
export class AppModule {}
```

It runs. But with a single module there are no `exports`, so **every provider can inject every other one** and the boundary you got for free is gone. `AppModule` also grows by several lines for every feature, forever. In Nest, keep layers *inside* a module folder (`orders/dto/`, `orders/entities/`, and later `orders/controllers/` if a module gets large), not at the top.

---

## 8. React (and Next.js)

**This is the one frontend developers most need.** Most React projects start with type folders — `components/`, `hooks/`, `services/` — because that's what the first tutorial did, and by the time the app has twenty screens `components/` holds eighty files from every part of the product.

### By layer (by type)

```
src/
├── components/   Button.tsx  CartItem.tsx  CartSummary.tsx  ProductCard.tsx  LoginForm.tsx  ...
├── hooks/        useCart.ts  useProducts.ts  useAuth.ts
├── services/     cartApi.ts  productsApi.ts  authApi.ts
├── store/        cartSlice.ts  authSlice.ts
├── types/        cart.ts  product.ts  user.ts
├── pages/        CartPage.tsx  ProductsPage.tsx  LoginPage.tsx
└── utils/
```

Changing how the cart total works touches `components/`, `hooks/`, `services/`, `store/` and `types/`. Deleting the cart means finding every cart file in five folders, and `Button.tsx` (used everywhere) sits beside `CartItem.tsx` (used in one place) with nothing to tell them apart.

### By feature

```
src/
├── main.tsx
├── app/                         composition root
│   ├── App.tsx
│   ├── providers.tsx            query client, theme, auth context
│   ├── router.tsx               maps each URL to a route component
│   └── routes/
│       ├── ProductsRoute.tsx    composes products + cart
│       └── CartRoute.tsx
├── features/
│   ├── cart/
│   │   ├── api/                 getCart.ts  addToCart.ts   (fetching + query hooks)
│   │   ├── components/          CartItem.tsx  CartSummary.tsx  AddToCartButton.tsx
│   │   ├── hooks/               useCartTotal.ts
│   │   ├── types.ts
│   │   └── index.ts             the only file outsiders may import
│   ├── products/
│   └── auth/
└── shared/
    ├── ui/                      Button.tsx  Modal.tsx  Input.tsx  (no business knowledge)
    ├── lib/                     apiClient.ts  formatMoney.ts
    └── hooks/                   useDebounce.ts
```

```ts
// src/features/cart/index.ts — verified
export { AddToCartButton } from "./components/AddToCartButton";
```

A real one also exports `CartSummary`, `useCart`, and `export type { Cart } from "./types"` — whatever the rest of the app genuinely needs, and no more.

### The cross-feature problem, and the React answer

The product list needs an "Add to cart" button. The tempting fix is for `products/` to import from `cart/`. Do that a few times and every feature depends on every other.

The cleaner answer uses something React is built for: **composition**. The product list doesn't know about carts — it accepts a slot. The route, which lives in `app/`, is allowed to know about both features and connects them:

```tsx
// src/features/products/components/ProductList.tsx — verified (lints clean)
type Product = { id: string; name: string };

export function ProductList({ renderAction }: { renderAction: (p: Product) => React.ReactNode }) {
  const products: Product[] = [{ id: "1", name: "Mug" }];
  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>
          {p.name} {renderAction(p)}
        </li>
      ))}
    </ul>
  );
}
```

```tsx
// src/app/routes/ProductsRoute.tsx — verified (lints clean)
import { AddToCartButton } from "@/features/cart";
import { ProductList } from "@/features/products";

export function ProductsRoute() {
  return <ProductList renderAction={(p) => <AddToCartButton productId={p.id} />} />;
}
```

Now `products` can be reused on a wishlist page with a different button, and deleting `cart` breaks only the route that composed it.

### Configuring the `@/` alias (Vite)

```json
// tsconfig.app.json (Vite's template) — add under compilerOptions
"paths": { "@/*": ["./src/*"] }
```

```ts
// vite.config.ts — fragment
import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
});
```

TypeScript needs `paths` to type-check the import; Vite needs `alias` to actually bundle it. Forgetting one gives "works in the editor, fails in the browser" or the reverse.

### Enforcing the boundary — verified

The frontend version is **stricter** than the Express one: features may not import each other at all, and dependencies flow one way — `shared → features → app`.

```js
// eslint.config.js — verified with ESLint 9.39, eslint-plugin-import 2.32
import { readdirSync } from "node:fs";
import importPlugin from "eslint-plugin-import";
import tseslint from "typescript-eslint";

const features = readdirSync("./src/features");

export default tseslint.config({
  files: ["src/**/*.{ts,tsx}"],
  languageOptions: { parser: tseslint.parser },
  plugins: { import: importPlugin },
  settings: { "import/resolver": { typescript: true } },
  rules: {
    "import/no-restricted-paths": [
      "error",
      {
        zones: [
          // 1. Features never import each other. Compose them in app/ instead.
          ...features.map((feature) => ({
            target: `./src/features/${feature}`,
            from: "./src/features",
            except: [`./${feature}`],
          })),
          // 2. One direction only: shared → features → app.
          { target: "./src/features", from: "./src/app" },
          { target: "./src/shared", from: ["./src/features", "./src/app"] },
        ],
      },
    ],
  },
});
```

With the files above, `ProductsRoute.tsx` passes. Adding `import { AddToCartButton } from "@/features/cart"` inside `features/products/` fails with `Unexpected path "@/features/cart" imported in restricted zone`.

This is the structure [Bulletproof React](https://github.com/alan2207/bulletproof-react) documents, and it's worth reading its `docs/project-structure.md` once.

### Next.js App Router

In Next.js the `app/` folder **is** the router — each folder is a URL segment — so it's organised by route, which is close to by-feature for pages but not for logic. Keep it thin:

```
src/
├── app/
│   ├── products/page.tsx        imports from @/features/products and @/features/cart
│   └── cart/page.tsx
├── features/                    same shape as above
└── shared/
```

`create-next-app` already configures the `@/*` alias. Folders prefixed with an underscore (`app/cart/_components/`) are ignored by the router, so small route-only pieces can sit beside their page; anything reused or containing logic goes in `features/`.

---

## 9. Django

### Correcting a common belief: Django is already by-feature

A Django **project** is made of **apps**, and an app is a feature folder: it has its own models, views, URLs, admin, migrations and tests. The layers are *files inside* each app. So the Django-shaped answer to this whole lesson is "one app per feature" — and the by-layer layout is the one you'd have to configure on purpose.

### By feature — apps inside an `apps/` folder (verified, Django 6.1)

```bash
django-admin startproject config .        # the "." keeps manage.py at the top
mkdir -p apps/users apps/orders
touch apps/__init__.py
python manage.py startapp users apps/users
python manage.py startapp orders apps/orders
```

```
shop/
├── manage.py
├── pyproject.toml           import-linter contract lives here
├── config/                  project package: settings + root URLs
│   ├── settings.py          composition root, part 1: INSTALLED_APPS
│   └── urls.py              composition root, part 2: include() per app
└── apps/
    ├── __init__.py
    ├── users/
    │   ├── apps.py
    │   ├── models.py
    │   ├── services.py      not generated — the app's public API, by convention
    │   ├── views.py
    │   ├── urls.py          not generated — create it
    │   ├── admin.py
    │   ├── migrations/
    │   └── tests.py
    └── orders/
        └── ...same shape
```

**Step 1 — fix the generated `apps.py`.** `startapp` writes `name = 'orders'` even when the app is in a subfolder. Leave it and `manage.py check` fails with:

```
django.core.exceptions.ImproperlyConfigured: Cannot import 'users'. Check that 'apps.users.apps.UsersConfig.name' is correct.
```

`name` must be the full Python import path:

```python
# apps/orders/apps.py
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = "apps.orders"
```

**Step 2 — install and route.**

```python
# config/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.users",
    "apps.orders",
]
```

```python
# config/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/orders/", include("apps.orders.urls")),
]
```

```python
# apps/orders/urls.py
from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("", views.order_list, name="list"),
]
```

**Step 3 — cross-app references.** A foreign key names the other app by its **label**, which is the last part of the name: `"users"`, not `"apps.users"`. The same is true for `AUTH_USER_MODEL = "users.User"` if you write a custom user model.

```python
# apps/orders/models.py
from django.db import models


class Order(models.Model):
    customer = models.ForeignKey("users.Customer", on_delete=models.PROTECT)
    total_pence = models.PositiveIntegerField()
```

Behaviour crosses apps through `services.py`, never by reaching into another app's views:

```python
# apps/users/services.py
from .models import Customer


def get_customer(customer_id: int) -> Customer:
    return Customer.objects.get(pk=customer_id)
```

```python
# apps/orders/services.py
from apps.users.services import get_customer

from .models import Order


def place_order(customer_id: int, total_pence: int) -> Order:
    customer = get_customer(customer_id)
    return Order.objects.create(customer=customer, total_pence=total_pence)
```

`makemigrations` then creates `apps/users/migrations/0001_initial.py` and `apps/orders/migrations/0001_initial.py` — **each app owns its own migrations**, which is what makes an app deletable.

### By layer — one app, packages per layer (verified)

```bash
django-admin startproject config .
python manage.py startapp core
rm core/models.py core/views.py
mkdir core/models core/views core/services
```

```
shop/
├── manage.py
├── config/
└── core/
    ├── apps.py
    ├── models/
    │   ├── __init__.py      MUST import every model
    │   ├── order.py
    │   └── user.py
    ├── views/
    │   ├── __init__.py
    │   ├── orders.py
    │   └── users.py
    ├── services/
    ├── urls.py
    ├── admin.py
    └── migrations/          one folder for every table in the project
```

```python
# config/settings.py — add to INSTALLED_APPS
"core",
```

```python
# core/models/__init__.py
from .order import Order
from .user import Customer

__all__ = ["Customer", "Order"]
```

**Why the `__init__.py` imports matter.** Django finds models by importing `core.models` and seeing which classes got defined. With an empty `__init__.py`, nothing imports `order.py`, and `makemigrations` prints **`No changes detected`** — tested. With the two imports, it creates both models.

```python
# core/urls.py
from django.urls import path

from .views import orders, users

urlpatterns = [
    path("orders/", orders.order_list),
    path("users/", users.user_list),
]
```

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
]
```

**What this costs you later.** Every table is named `core_*` (`core_order`), there is one migration history for the whole product, and one `admin.py`. Splitting `core` into apps later means moving models between apps, which needs `SeparateDatabaseAndState` migrations and table renames. **This is the one framework in this lesson where the layout is expensive to change — decide on day one.** By-layer packages *inside* an app (`orders/models/`, `orders/views/`) are fine when one app's `models.py` gets long.

### Enforcing the boundary — verified with import-linter 2.x

```bash
pip install import-linter
```

```toml
# pyproject.toml
[tool.importlinter]
root_package = "apps"

[[tool.importlinter.contracts]]
name = "Apps use each other only through services.py"
type = "forbidden"
source_modules = ["apps.orders"]
forbidden_modules = ["apps.users.models", "apps.users.views"]
allow_indirect_imports = true
```

Run `lint-imports` from the folder containing `manage.py`. A direct `from apps.users.models import Customer` in `apps/orders/views.py` is reported as broken.

**`allow_indirect_imports = true` is not optional here.** Without it, import-linter also follows *chains*: `orders.services → users.services → users.models` counts as orders importing `users.models`, so the correct route through the public API fails the contract. That was the first result when this was tested.

---

## 10. Flask

### Correcting a common belief: Flask has no default

Flask enforces no layout. The **official tutorial** (`flaskr`) is actually feature-ish — one blueprint module per feature, `auth.py` and `blog.py`. The by-layer layout you see most (`app/routes.py`, `app/models.py`, later `app/routes/`, `app/models/`) comes from popular tutorials that start from a single file and split it by type. **Blueprints are Flask's feature-folder tool**, and the application factory is the composition root.

### By layer

```
app/
├── __init__.py          create_app() registers every blueprint
├── extensions.py        db = SQLAlchemy()
├── models/
│   ├── __init__.py      imports every model (same reason as Django)
│   ├── order.py
│   └── user.py
├── routes/
│   ├── orders.py        bp = Blueprint("orders", __name__)
│   └── users.py
├── services/
└── templates/
    ├── orders/
    └── users/
```

### By feature (verified, Flask 3.1 + Flask-SQLAlchemy)

```
app/
├── __init__.py          create_app() — composition root
├── extensions.py        db, migrate, login manager — imports no feature
├── users/
│   ├── __init__.py      defines the blueprint
│   ├── models.py
│   ├── services.py      public API
│   └── routes.py
└── orders/
    ├── __init__.py
    ├── models.py
    ├── services.py
    ├── routes.py
    └── templates/orders/list.html
```

**Why `extensions.py` exists.** Models need `db`. If `db` lived in `app/__init__.py`, then `__init__` imports the blueprints, the blueprints import models, and the models import `__init__` — a circular import. Putting `db` in a file that imports nothing from the app breaks the circle.

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

```python
# app/orders/__init__.py
from flask import Blueprint

bp = Blueprint("orders", __name__, template_folder="templates")

from . import routes  # noqa: E402,F401  (attaches the routes to bp)
```

The import sits at the bottom on purpose: `routes.py` does `from . import bp`, so `bp` must exist before `routes` is imported.

```python
# app/orders/routes.py
from flask import render_template, request

from . import bp, services


@bp.post("/")
def place_order():
    body = request.get_json()
    order = services.place_order(body["customer_id"], body["total_pence"])
    return {"id": order.id, "total_pence": order.total_pence}, 201


@bp.get("/")
def list_orders():
    return render_template("orders/list.html", orders=services.list_orders())
```

```python
# app/orders/services.py
from app.extensions import db
from app.users.services import get_customer

from .models import Order


def place_order(customer_id: int, total_pence: int) -> Order:
    customer = get_customer(customer_id)  # 404s if the customer doesn't exist
    order = Order(customer_id=customer.id, total_pence=total_pence)
    db.session.add(order)
    db.session.commit()
    return order


def list_orders() -> list[Order]:
    return db.session.scalars(db.select(Order)).all()
```

```python
# app/__init__.py
from flask import Flask

from .extensions import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    # The composition root: the only place that knows which features exist.
    from .orders import bp as orders_bp
    from .users import bp as users_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")

    with app.app_context():
        db.create_all()
    return app
```

Set the URL prefix in **one** place. Here it's `register_blueprint`; if you also pass `url_prefix` to `Blueprint(...)`, the registration one wins and the other just misleads.

**Template namespacing.** All blueprints share one template namespace, and the app's own `templates/` folder wins any clash. That is why the file is `orders/templates/orders/list.html` and rendered as `"orders/list.html"` — the extra `orders/` stops two features' `list.html` from colliding.

**Run it.** From the folder containing `app/`:

```python
from app import create_app

app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite://", "TESTING": True})
c = app.test_client()
print(c.post("/api/users/", json={"email": "a@b.c"}).get_json())
print(c.post("/api/orders/", json={"customer_id": 1, "total_pence": 1500}).get_json())
print(c.get("/api/orders/").get_data(as_text=True))
print(c.post("/api/orders/", json={"customer_id": 99, "total_pence": 1}).status_code)
```

```
{'email': 'a@b.c', 'id': 1}
{'id': 1, 'total_pence': 1500}
<li>#1: 1500p</li>
404
```

(The `users/routes.py` and `users/services.py` it relies on are the same shape as orders: a `create_customer` route and service, and `get_customer` using `db.get_or_404`.)

### Enforcing the boundary — verified

```toml
# pyproject.toml
[tool.importlinter]
root_package = "app"

[[tool.importlinter.contracts]]
name = "Shared code never imports a feature"
type = "forbidden"
source_modules = ["app.extensions"]
forbidden_modules = ["app.orders", "app.users"]

[[tool.importlinter.contracts]]
name = "Features use each other only through services"
type = "forbidden"
source_modules = ["app.orders"]
forbidden_modules = ["app.users.models", "app.users.routes"]
allow_indirect_imports = true
```

`lint-imports` → `Contracts: 2 kept, 0 broken.`

---

## 11. Go, Java, Rust, C, C++ and C#

These have their own lesson: [[backend/03-structuring-a-backend/02b-organising-by-feature-in-compiled-languages|organising by feature in compiled languages]]. The short version is worth knowing even if you never write them: **in these languages the compiler or build system enforces feature boundaries** — Go's `internal/` packages, Java's package-private classes, Rust's private modules, C's opaque types and `static` functions, C++'s `PRIVATE` include directories, and C#'s `internal` with one project per feature. And a by-layer layout switches each of those off, because each layer lives in a different package and everything has to be public for the next layer to reach it.

---

## 12. Side by side

| Framework | Default lean | Composition root | Boundary enforced by |
|---|---|---|---|
| Express | none | `app.use(...)` in `app.ts` | ESLint `no-restricted-paths` |
| NestJS | **by feature** | `imports: []` in `AppModule` | module `exports` (injection only) + ESLint |
| Django | **by feature** (apps) | `INSTALLED_APPS` + `include()` | import-linter |
| Flask | none (tutorials vary) | `register_blueprint` in `create_app` | import-linter |
| React | none (tutorials lean by type) | router + providers in `app/` | ESLint `no-restricted-paths` |
| Go | **by feature** (packages) | `main.go` | **the compiler** — `internal/` |
| Java / Spring | by layer in tutorials | `main` / component scan | **the compiler** — package-private · Spring Modulith |
| Rust | **by feature** (modules) | `main.rs` | **the compiler** — private modules · workspace crates |
| C | **by feature** (subsystems) | `main.c` | the compiler and linker — opaque types, `static` |
| C++ | by feature (libraries) | `main.cpp` | **the build** — CMake `PRIVATE` include directories |
| C# / ASP.NET Core | by layer in templates | `Program.cs` | **the compiler** — `internal`, one project per feature |

The last six rows are explained in the companion lesson.

## 13. Getting the details right

**Inside a feature, keep the layers.** By-feature doesn't mean abandoning [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|controller/service/repository]] — it means those three files sit next to each other. Both axes, feature outer, layer inner.

**`shared/` is where this rots.** Every by-feature codebase grows a `shared/`, `common/`, or `utils/`, and it becomes a junk drawer that every feature depends on — which quietly recreates the coupling you were avoiding. Two rules that keep it honest:
- Something belongs in `shared/` when **two or more features already use it** — not when you predict they might.
- `shared/` may never import from a feature. If it needs to, it isn't shared. (Every lint config above encodes this rule.)

**Duplication across features is often correct.** Two features having similar-looking code is fine; prematurely extracting it into `shared/` couples them, and they'll diverge. **Wait for the third occurrence.** The wrong abstraction costs more than the duplication.

**Enforce boundaries mechanically, not by discipline.** Nobody remembers architectural rules under deadline. Every framework section above ends with the rule that makes a forbidden import a build failure. In the compiled languages it costs nothing, because the language already has the boundary — the only mistake is choosing a layout that forces everything public.

## Common pitfalls

1. **Feature folders with layer thinking.** `features/orders/` exists, but the business logic still lives in a top-level `services/` folder. You get the ceremony of both and the benefit of neither.
2. **Barrel files that import themselves.** Inside a feature, import siblings by relative path (`./components/CartItem`), never through your own `index.ts` — that creates circular imports. Keep feature barrels short; a barrel re-exporting a hundred files slows the Vite dev server and can defeat tree-shaking.
3. **Models nobody imports.** Django (`makemigrations` → "No changes detected") and Flask-Migrate (empty autogenerated migration) only see models that were imported. In by-feature Flask, a feature whose blueprint isn't registered has invisible models.
4. **Django `apps.py` name left as generated** → `ImproperlyConfigured: Cannot import 'users'`.
5. **Exporting internals to silence an error.** When Nest says it can't resolve a dependency, adding the repository to `exports` makes the error go away and removes the boundary. Depend on the other feature's service instead.
6. **import-linter `forbidden` without `allow_indirect_imports`** fails even the correct route through `services.py`.
7. **Configuring the `@/` alias in only one tool.** TypeScript and the bundler (Vite, Jest/Vitest) each need it.

## Check your understanding

Answer each before opening its fold.

1. **Predict.** In a by-layer Express app with users, products and orders, you delete the products feature. List every place you'd have to look. Now do the same for the by-feature layout.
2. You move Django apps into `apps/` and get `ImproperlyConfigured: Cannot import 'orders'`. What one-line change fixes it, and why does Django need it?
3. In Django, why is the foreign key written `"users.Customer"` and not `"apps.users.Customer"`?
4. In NestJS, `OrdersService` injects `UsersRepository` and the app won't start. Give the fix that keeps the boundary, and the fix that destroys it.
5. In React, `CartItem` is shown on the cart page and in the checkout summary. Where should it live? Does your answer change if it's a plain row with a picture, a name and a price and knows nothing about carts?
6. Your by-feature Flask app's `flask db migrate` produces an empty migration after you added `payments/models.py`. Name two likely causes.
7. Why must `shared/` never import from a feature, even "just one helper"?

<details>
<summary>Answers — after your attempt</summary>

1. By layer: the products route registration, `controllers/`, `services/`, `repositories/`, `validators/`, tests, and any other service that imported `products.service` — and you only find the last group by searching. By feature: `rm -rf src/features/products`, delete its `app.use` line, and let the type checker list remaining references.
2. Set `name = "apps.orders"` in `apps/orders/apps.py`. Django imports the app by `name`; `startapp` wrote the bare `"orders"`, which isn't importable from the project root.
3. Model references use the **app label**, which defaults to the last segment of `name`. `name` is the import path; the label is the short identifier used in FKs, migrations and table names (`orders_order`).
4. Keep: inject `UsersService`, which `UsersModule` exports, and make sure `OrdersModule` has `imports: [UsersModule]`. Destroy: add `UsersRepository` to `UsersModule.exports`.
5. If only the cart feature uses it — including checkout, when checkout is part of the cart feature — it lives in `features/cart/components/` and is exported from `index.ts` only if something outside needs it. If it's a pure presentational row with no cart knowledge and two features already use it, it's a `shared/ui` component that takes props. The deciding question is "does it know about the cart?", not "is it a component?".
6. The `payments` blueprint isn't registered in `create_app`, so nothing imports `payments/models.py`; or the blueprint is registered but no imported module (routes → services → models) imports the model file.
7. Then `shared/` depends on that feature, every other feature depends on `shared/`, and so every feature now transitively depends on that one. You can no longer delete it or extract it, and the boundary graph has a cycle.

</details>

## Practice — independent task

**Build both, then convert.** Pick Express or Flask for the backend (or a compiled language from the companion lesson, using its own boundary instead of a lint rule), **and** React for the frontend.

**Backend.** Three features — users, products, orders — each with a list and a create endpoint, using an in-memory store or SQLite. Creating an order must call the users feature to check the customer exists.

1. Build it **by layer** first. Commit.
2. Convert it to **by feature** with a composition root and a `shared/` folder. Commit.
3. Add the boundary rule from the framework's section.

**Frontend.** A product list and a cart. The product list shows an "Add to cart" button per product, built with the slot pattern from §8, and the cart shows a running total.

**Edge cases to handle:** an order for a customer that doesn't exist (404, not a crash); a helper that both products and orders use (decide: duplicate or `shared/`, and write one sentence on why).

**Done when:**
- Deleting the products folder plus its single registration line leaves an app that starts, and the users and orders tests still pass.
- Adding a deep import from orders into users' repository or models fails `npx eslint src` or `lint-imports`.
- Nothing in `shared/` imports from `features/` (the linter proves it, not you).
- You can explain, closed-book, which file is your composition root and why there's only one.

## Tradeoffs, limits and extensions

- **Features aren't always obvious.** "Notifications" might be its own feature or a part of orders. Pick, write it down, and move it when the code tells you you were wrong — moving a folder is cheap when boundaries are enforced.
- **Feature-Sliced Design** is a stricter frontend methodology that adds more layers (`entities`, `widgets`, `pages`) on top of the idea here. Worth knowing it exists; this lesson's three-level version covers most apps.
- **Monorepos** take the same idea one level up: each feature becomes a package, and the package manager enforces the boundary.

## Before moving on

You're done when you can lay out the shop app both ways in your main framework from memory, write its composition root, and make a cross-feature import fail the linter.

**Recap.** Folder structure is a **bet about what changes together**. By-layer bets that you'll change all controllers at once; by-feature bets that you'll change one feature end-to-end. The second bet is almost always right, because features are how work arrives — from users, from tickets, from the roadmap. **Organise around the shape of the work, not the shape of the code.** Every framework answers the same three questions: where the files live, where they're plugged in, and what stops them reaching into each other.

**Next.** A well-kept feature layout with enforced boundaries **is** a modular monolith — the structure you want before you ever consider splitting into services, because the boundaries have already been tested where getting them wrong is cheap. → [[backend/03-structuring-a-backend/05-modular-monolith-to-services|modular monolith to services]]

## Related
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — what lives inside each feature folder
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency injection and wiring]] — how the composition root builds each feature
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services|Modular Monolith → Services]] — where good feature boundaries pay off
- [[frontend/03-structuring-a-frontend/01-components-and-composition|Components and composition]] — the React side of the slot pattern
- [[backend/frameworks/javascript/02-express/index|Express]] · [[backend/frameworks/javascript/03-nest/index|NestJS]] · [[backend/frameworks/python/02-django/index|Django]] · [[backend/frameworks/python/03-flask/index|Flask]] · [[backend/frameworks/go/index|Go]] · [[backend/frameworks/java/index|Java]] · [[backend/frameworks/rust/index|Rust]] · [[backend/frameworks/c/index|C]] · [[backend/frameworks/cpp/index|C++]]
- [[concepts/04-best-practices/01-clean-code|Clean Code]] — the duplication-vs-abstraction argument
