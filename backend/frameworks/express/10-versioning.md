---
id: a466f0aa-cc69-4949-bd65-2594530644bc
---

# Versioning

**API versioning is how you change the shape of your API without breaking the apps that already use it: you keep the old version running for old clients, offer the new one beside it, and retire the old one on a date you announce.** You've seen this from the other side every time an app said "please update to keep using this". Somewhere behind it, a backend was serving two versions while people moved over.

## Before you start
<!-- bite: dc4ad1f7-34e8-426b-9c09-8514f9c192b7 -->

You should have the list endpoints from [[backend/frameworks/express/09-listing|lesson 9]], answering in the `{ data, meta }` shape.

After this lesson you will be able to:

1. Tell a breaking change from a safe one.
2. Version an API in the path, in a header, by media type, or by query parameter, and say what each costs.
3. Run v1 and v2 side by side in one Express app, sharing every service and repository.
4. Deprecate a version properly: headers, a sunset date, usage tracking, and finally switching it off.

## Where we stopped
<!-- bite: 0ea710b0-c25e-4264-b407-07717b5f2312 -->

Lesson 9 ended with a happy problem. Paystack, which we use for payments in [[backend/frameworks/express/17-payments-and-webhooks|lesson 17]], counts money in **kobo** (₦1 = 100 kobo), and the phone app team wants prices like this:

```json
{ "price": { "amount": 150000, "currency": "NGN" } }
```

instead of today's:

```json
{ "priceNaira": 1500 }
```

It's a better shape. It can carry kobo, so ₦1,499.50 becomes possible, and the currency is written down instead of assumed. But thousands of customers still have last month's app on their phones, and that app reads `priceNaira`. People don't update apps quickly. Some never do. Ship the new shape on the same URL, and every one of those phones shows "₦undefined".

## The kid version
<!-- bite: 4c2f0eb7-a19e-4d17-99f0-0bb46531733e -->

Mama Put prints a menu card. One day she changes the layout: prices move to the right, dishes are grouped differently. If she just swapped every card overnight, the regular customers who order by pointing at "the third thing on the left" would get the wrong food.

So she keeps the old cards on the left side of the counter and puts the new cards on the right. She tells everyone: "the old cards go away at the end of June". By July, everyone has moved over, and she throws the old cards away.

**Where the picture stops working.** Mama can see who's still using the old card. An API has to *measure* it, by logging which version each request used, or it will never know when it's safe to switch the old one off.

## Terms used in versioning
<!-- bite: beaab3aa-3c07-4a9c-a76a-05d4c0dd4803 -->

1. **Breaking change**: This is a change that makes a correctly written old client stop working. Renaming `priceNaira` is breaking.
2. **Non-breaking change**: This is also called a **backward-compatible change**. It's a change old clients don't notice, like adding a new optional field.
3. **Version**: This is a named, frozen shape of the API. Inside one version, you only ever make non-breaking changes.
4. **Deprecation**: This is announcing that a version is old and will go away, while it still works.
5. **Sunset**: This is the date a deprecated version stops working.
6. **Presenter**: This is a small function that turns our internal data (a `Dish`) into one version's public shape. Different versions, different presenters, same data underneath.
7. **Tolerant reader**: This is a client that ignores fields it doesn't know about. Clients written this way make adding fields safe.

## Step 1: what counts as breaking
<!-- bite: 978c79cc-335b-4e01-b89b-4681c46366ec -->

Before choosing *how* to version, know *when* you need to. Most changes don't need a new version at all.

**Safe, in the same version:**

1. Adding a new endpoint, like `GET /menu/specials`.
2. Adding a new **optional** field to a response, like `description`. (Tolerant readers ignore it.)
3. Adding a new **optional** query parameter or body field.
4. Making a validation rule looser, like allowing names up to 120 characters instead of 80.

**Breaking, needs a new version:**

1. Removing or renaming a field (`priceNaira` → `price`).
2. Changing a field's type or meaning (`price` in naira → `price` in kobo, even with the same name, and that one is the most dangerous, because nothing *looks* broken).
3. Making an optional input field required.
4. Making validation stricter, like names now at most 40 characters.
5. Changing status codes, error codes, or the response envelope.
6. Changing what a filter or sort means.

A good habit: **add, don't change.** If you can give clients the new thing *next to* the old thing, you don't need a new version. Here we could add `price` alongside `priceNaira` in v1. Often that's the right call. We'll do a real v2 anyway, because one day you'll need it, and because v2 also lets new clients send kobo when they *create* dishes.

## Step 2: the four ways to say which version
<!-- bite: 733453d1-3fe8-4faa-b311-366239f33f95 -->

| Way | Looks like | Good | Costs |
|---|---|---|---|
| **In the path** | `GET /v2/menu` | obvious, easy to test in a browser or `curl`, easy to route, cache and log | the URL changes; some say a version isn't part of a resource's identity |
| **In a header** | `Api-Version: 2` | URLs stay clean | invisible in a browser, easy to forget; caches must be told it matters (`Vary`) |
| **By media type** | `Accept: application/vnd.mamaput.v2+json` | the most "correct" by HTTP's rules: same resource, different representation | awkward to type and test; few people know it |
| **By query parameter** | `GET /menu?api-version=2` | easy to add to any URL | mixes versioning with filters; easy to drop by accident |

There's a fifth style worth knowing: **dated versions**, like Stripe's `Stripe-Version: 2026-11-01`. Every breaking change gets a date, and each client is pinned to the date it signed up. It's powerful and a lot of work, best for big public APIs.

For Mama Put we choose **the path** for the main API. It's what most public APIs do, and anyone can see the version in a log line or a browser bar. But all four ride on the same idea underneath, so we'll build the header way too, and you'll see it's a small difference.

## Step 3: one service, two presenters
<!-- bite: 63673935-903f-45bb-9800-ea88c5f4c85f -->

Here's the key idea: **versions differ at the edge, not inside.** v1 and v2 share the same `menuService`, the same rules, the same repository and the same database. Only two things change per version:

1. How a `Dish` is **shown** (the presenter).
2. How a request body is **read** (the input schema).

`src/menu/menu.versions.ts`:

```ts
import { z } from "zod";
import type { Dish } from "./menu.types.ts";
import type { NewDish } from "./menu.schemas.ts";
import { NewDishSchema } from "./menu.schemas.ts";

export type MenuVersion = {
  presentDish(dish: Dish): Record<string, unknown>;
  NewDishBody: z.ZodType<NewDish>;
};

export const menuV1: MenuVersion = {
  presentDish: (dish) => ({
    id: dish.id,
    name: dish.name,
    priceNaira: dish.priceNaira,
    available: dish.available,
    portionsLeft: dish.portionsLeft,
  }),
  NewDishBody: NewDishSchema,
};

const MoneySchema = z.object({
  amount: z.number().int().positive().multipleOf(100, "Amount is in kobo; whole naira only for now"),
  currency: z.literal("NGN"),
});

export const menuV2: MenuVersion = {
  presentDish: (dish) => ({
    id: dish.id,
    name: dish.name,
    price: { amount: dish.priceNaira * 100, currency: "NGN" },
    available: dish.available,
    portionsLeft: dish.portionsLeft,
  }),
  NewDishBody: z
    .object({
      name: z.string().trim().min(1).max(80),
      price: MoneySchema,
      portionsLeft: z.number().int().min(0).max(500),
    })
    .transform((body) => ({
      name: body.name,
      priceNaira: body.price.amount / 100,
      portionsLeft: body.portionsLeft,
    })),
};
```

Look at v2's `NewDishBody`. It reads the v2 shape from the client, then **transforms** it into the same `NewDish` the service has always taken. The service never learns that v2 exists. That's the whole trick: each version is a translator at the door.

(Notice the honest limit in `multipleOf(100)`. Our database still stores whole naira, so v2 can *show* kobo but only *accept* whole naira for now. The real fix is a migration that stores kobo, `price_kobo`, and after it both presenters read from that. That's the practice task. Versioning the API first, and the storage second, is a normal and safe order.)

## Step 4: routers that take a version
<!-- bite: 3c3a89c1-c7d8-4cfd-9182-933f74506d8d -->

The menu router receives its version like any other dependency:

```ts
// src/menu/menu.routes.ts
export function createMenuRouter(deps: {
  menuService: MenuService;
  kitchenOnly: express.RequestHandler;
  version: MenuVersion;
}) {
  const { menuService, kitchenOnly, version } = deps;
  const router = express.Router();

  router.get("/", async (req, res) => {
    const { fields, ...options } = validate(ListMenuQuerySchema, req.query, "query");
    const page = await menuService.list(options);
    res.json({
      data: page.items.map((dish) => pick(version.presentDish(dish), fields)),
      meta: { page: options.page, limit: options.limit, total: page.total, totalPages: Math.ceil(page.total / options.limit) },
    });
  });

  router.get("/:id", async (req, res) => {
    const { id } = validate(DishIdSchema, req.params, "params");
    res.json({ data: version.presentDish(await menuService.get(id)) });
  });

  router.post("/", kitchenOnly, async (req, res) => {
    const input = validate(version.NewDishBody, req.body, "body");
    const dish = await menuService.add(input);
    res.status(201).location(`${req.baseUrl}/${dish.id}`).json({ data: version.presentDish(dish) });
  });

  // PATCH and DELETE the same way
  return router;
}
```

`req.baseUrl` is the path the router was mounted at, `/v1/menu` or `/v2/menu`, so the `Location` header always points into the version the client used.

(Field selection: `fields=priceNaira` makes sense in v1 and `fields=price` in v2. The practice makes each version carry its own allowed fields.)

Then each version is one router that holds its features. `src/api.ts`:

```ts
import express from "express";
import type { AppDeps } from "./app.ts";
import type { MenuVersion } from "./menu/menu.versions.ts";
import { createMenuRouter } from "./menu/menu.routes.ts";
import { createOrdersRouter } from "./orders/orders.routes.ts";

export function createApiRouter(deps: AppDeps, versions: { menu: MenuVersion }) {
  const api = express.Router();
  api.use("/menu", createMenuRouter({ ...deps, version: versions.menu }));
  api.use("/orders", createOrdersRouter(deps));
  return api;
}
```

And `app.ts` mounts both:

```ts
app.use("/v1", deprecated(v1Policy), createApiRouter(deps, { menu: menuV1 }));
app.use("/v2", createApiRouter(deps, { menu: menuV2 }));
```

```bash
curl -s http://localhost:3000/v1/menu/1
# {"data":{"id":"1","name":"Jollof rice","priceNaira":1500,...}}

curl -s http://localhost:3000/v2/menu/1
# {"data":{"id":"1","name":"Jollof rice","price":{"amount":150000,"currency":"NGN"},...}}
```

Same dish, same database row, two shapes. Old phones keep working; new phones get kobo.

What about the old, unversioned paths like `/menu` that last month's app calls? Mount v1 there too, as an alias, so nothing breaks today:

```ts
app.use("/", deprecated(v1Policy), createApiRouter(deps, { menu: menuV1 }));
```

Put it **after** `/v1` and `/v2`, so those match first. (Remember: first match wins.)

## Step 5: the header way
<!-- bite: fc626fd3-fa59-4150-a386-31926c1e738f -->

If you'd rather keep URLs clean, here's the same thing, choosing the version from a header. A small middleware decides, and remembers its choice:

```ts
// src/shared/choose-version.ts
import type { Request, Response, NextFunction } from "express";
import { AppError } from "./errors.ts";

const SUPPORTED = ["1", "2"] as const;
type Version = (typeof SUPPORTED)[number];

export function chooseVersion(defaultVersion: Version) {
  return (req: Request, res: Response, next: NextFunction) => {
    const fromHeader = req.get("Api-Version");
    const fromAccept = req.get("Accept")?.match(/application\/vnd\.mamaput\.v(\d+)\+json/)?.[1];
    const fromQuery = typeof req.query["api-version"] === "string" ? req.query["api-version"] : undefined;
    const asked = fromHeader ?? fromAccept ?? fromQuery ?? defaultVersion;

    if (!SUPPORTED.includes(asked as Version)) {
      next(new AppError("invalid", "unsupported-version", `API version ${asked} is not supported. Use one of: ${SUPPORTED.join(", ")}.`));
      return;
    }
    res.locals.apiVersion = asked;
    res.vary("Api-Version");
    res.vary("Accept");
    next();
  };
}
```

It reads the header way, the media type way and the query way, in that order, and falls back to a default. That one middleware covers three of the four styles.

Then the router picks the presenter for each request instead of being given one:

```ts
const versions = { "1": menuV1, "2": menuV2 };
// inside a handler:
const version = versions[res.locals.apiVersion as "1" | "2"];
```

`res.vary(...)` matters more than it looks. It adds a `Vary` header to the response, telling any cache in between (a CDN, a proxy, the phone's own cache) "the answer depends on this request header". Without it, a cache could store the v2 answer and hand it to a v1 client. With path versioning you don't need `Vary`, because the URLs are different. That's one of the quiet reasons path versioning is popular.

What should the default be when a client sends no version? **The oldest supported version**, so clients that never heard of versioning keep getting what they always got. Defaulting to "latest" means every new version breaks them.

## Step 6: deprecating v1
<!-- bite: 51698e33-502b-48e9-978e-04a8777512dc -->

A version you never retire is a version you maintain forever. Retiring one well is four things.

**1. Tell clients, in every response.** Two standard headers do this. `Deprecation` says when the version was deprecated, and `Sunset` says when it stops working. A `Link` points to the migration guide.

```ts
// src/shared/deprecated.ts
import type { Request, Response, NextFunction } from "express";

export type DeprecationPolicy = {
  deprecatedAt: Date;
  sunsetAt: Date;
  guide: string;
};

export function deprecated(policy: DeprecationPolicy) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (Date.now() >= policy.sunsetAt.getTime()) {
      res.status(410).type("application/problem+json").json({
        type: "https://mamaput.example/problems/version-retired",
        title: "Version retired",
        status: 410,
        detail: `This API version stopped working on ${policy.sunsetAt.toDateString()}. See ${policy.guide}`,
        code: "version-retired",
      });
      return;
    }
    res.set("Deprecation", `@${Math.floor(policy.deprecatedAt.getTime() / 1000)}`);
    res.set("Sunset", policy.sunsetAt.toUTCString());
    res.set("Link", `<${policy.guide}>; rel="deprecation"`);
    console.info({ event: "deprecated-version-used", version: "v1", path: req.originalUrl, client: req.get("User-Agent") });
    next();
  };
}
```

And the policy:

```ts
const v1Policy = {
  deprecatedAt: new Date("2026-12-01T00:00:00Z"),
  sunsetAt: new Date("2027-06-01T00:00:00Z"),
  guide: "https://mamaput.example/docs/moving-to-v2",
};
```

```bash
curl -si http://localhost:3000/v1/menu/1 | head -8
# HTTP/1.1 200 OK
# Deprecation: @1796083200
# Sunset: Tue, 01 Jun 2027 00:00:00 GMT
# Link: <https://mamaput.example/docs/moving-to-v2>; rel="deprecation"
```

**2. Measure who's still on it.** That `console.info` line is a log event for every v1 request, with the client's user agent. In [[backend/frameworks/express/25-observability|lesson 25]] it becomes a proper metric: "v1 requests per day". You switch v1 off when that number is near zero, not when the calendar says so.

**3. Tell people directly.** Headers are for programs. Humans need an email, a changelog entry, a note in the docs. If the phone app is yours, ship an update that moves to v2 *before* the sunset, and maybe a "please update" screen when v1 calls start returning deprecation headers.

**4. Switch it off kindly.** After the sunset date, the middleware answers **410 Gone** with a problem that says what happened and where to go. A clear 410 is far better than a confusing 404 or, worse, quietly returning v2 data to a v1 client.

## The same idea everywhere
<!-- bite: 3f742d1e-17e7-4fb8-a4ed-62f41f2209eb -->

Versioning isn't only for REST routes. Anything other programs depend on has a shape, and shapes need versions:

1. **Webhooks you send** (lesson 17): partners' code reads your payloads, so version them too.
2. **Events between services** (lesson 23): the notifications service reads `order.placed`. Change its shape, and you break it. Events carry a version number.
3. **gRPC** (lesson 22): Protocol Buffers have their own rules for safe changes, and you'll see they're the same rules as Step 1.

## The TypeScript in this lesson
<!-- bite: 0ce21f22-5776-494e-9d7c-0b8d208578b1 -->

1. **`z.ZodType<NewDish>`**: The type of "any zod schema whose *output* is a `NewDish`". v1's plain schema qualifies, and so does v2's schema with a `transform` at the end, because what comes out is a `NewDish`. That's how two very different input shapes can share one field in `MenuVersion`.
2. **`const menuV1: MenuVersion = { ... }`**: Writing the type after the name makes TypeScript check the object has everything `MenuVersion` needs, and nothing of the wrong type.
3. **`Record<string, unknown>`**: "an object with any text keys and values we won't make promises about". The presenter's output is just JSON to send, so this is honest.
4. **`z.literal("NGN")`**: A schema that accepts exactly that one value and nothing else.
5. **`{ ...deps, version: versions.menu }`**: Spread `deps` into a new object and add one more field. `deps` itself isn't changed.
6. **`(typeof SUPPORTED)[number]`**: `typeof SUPPORTED` is the type of the array `["1", "2"]`. Indexing it with `[number]` means "the type of any item in it": `"1" | "2"`. So the allowed versions are written once, as a value, and the type comes from it.
7. **`req.get("Accept")?.match(...)?.[1]`**: `?.` is **optional chaining**: if the thing before it is `undefined`, stop and give `undefined` instead of crashing. Here: no `Accept` header, or no match, both just give `undefined`. `[1]` is the first bracketed group in the pattern, the version digits.
8. **`fromHeader ?? fromAccept ?? fromQuery ?? defaultVersion`**: A chain of `??`: take the first one that isn't `undefined`.
9. **`typeof req.query["api-version"] === "string"`**: A query value could be text, a list (`?api-version=1&api-version=2`), or missing. Checking `typeof` makes sure it's one piece of text before we use it.
10. **`new Date("2026-12-01T00:00:00Z")`, `.getTime()`, `.toUTCString()`**: A `Date` is a moment in time. The `Z` means UTC. `getTime()` gives milliseconds since 1970; dividing by 1000 gives the seconds the `Deprecation` header wants. `toUTCString()` gives the HTTP date format the `Sunset` header wants.

## Your project so far
<!-- bite: 52d1938f-2e05-4991-a3b3-01042eb5f14c -->

```text
mama-put-api/
├── .env  ·  .env.example  ·  .gitignore  ·  package.json  ·  tsconfig.json
├── migrations/   001 … 004
└── src/
    ├── server.ts
    ├── app.ts                    ← mounts /v1 (deprecated), /v2, and / as a v1 alias
    ├── api.ts                    ← NEW: createApiRouter(deps, versions), one router per version
    ├── db/        pool.ts · transaction.ts · migrate.ts · seed.ts
    ├── menu/
    │   ├── menu.versions.ts      ← NEW: MenuVersion, menuV1, menuV2 (presenters and input schemas)
    │   ├── menu.routes.ts        ← takes a version; presents every dish through it
    │   └── menu.schemas.ts · menu.types.ts · menu.repository.ts · menu.pg-repository.ts · menu.service.ts
    ├── orders/    (unchanged)
    └── shared/
        ├── deprecated.ts         ← NEW: Deprecation, Sunset and Link headers; 410 after sunset
        ├── choose-version.ts     ← NEW: the header / media type / query alternative
        └── cursor.ts · pick.ts · errors.ts · request-id.ts · validate.ts
            log-requests.ts · kitchen-only.ts · not-found.ts · error-handler.ts
```

## Common mistakes
<!-- bite: 1220f6f5-ed43-4e30-bfa5-bf57d455872d -->

1. **Versioning for every change.** Adding a field isn't breaking. Save new versions for real breaks, and prefer "add, don't change".
2. **Copying the whole app per version.** Two copies of every service means every bug fix twice. Versions differ at the edge: presenters and input schemas.
3. **Defaulting to the latest version.** Clients that send no version break on every release. Default to the oldest supported one.
4. **Header versioning without `Vary`.** Caches serve one version's answer to the other version's clients.
5. **Changing the meaning of a field without renaming it.** `price` silently switching from naira to kobo makes every old client charge 100 times too much. Change the name, or change the version.
6. **No sunset date.** "Deprecated" with no end date means nobody moves.
7. **Switching off a version nobody measured.** Log or count usage per version, and look before you pull the plug.

## Check your understanding
<!-- bite: a5ee638c-194e-493d-95f7-52b1a5dde4e5 -->

1. Which of these need a new version? (a) adding `description` to dishes; (b) making `portionsLeft` required when creating a dish; (c) adding `GET /menu/specials`; (d) changing the error `code` `dish-unavailable` to `dish-finished`.
2. Why does `menuService` know nothing about v1 and v2?
3. You switch to header versioning and forget `res.vary("Api-Version")`. Describe a bug a customer might see.
4. What should happen when a v1 request arrives on 2 June 2027?

<details>
<summary>Answers, after your attempt</summary>

1. (b) and (d). (b) breaks old clients that don't send `portionsLeft`; (d) breaks any client checking for the old code. (a) and (c) are additions that old clients don't notice.
2. Because versions only change how data is shown and read at the edge. The rules (what a dish is, who can order what) are the same in every version, so they live once, in the service.
3. A cache stores the v2 answer for `GET /menu/1`, then serves it to an old phone. The old app looks for `priceNaira`, finds nothing, and shows "₦undefined" or crashes.
4. The `deprecated` middleware answers 410 Gone, with a problem explaining that v1 was retired on 1 June 2027 and linking the migration guide.

</details>

## Practice
<!-- bite: 619a4006-0d8d-4cb7-a4d7-feea0f0ad367 -->

1. Move prices to kobo for real. Write `migrations/005_price_kobo.sql` that adds `price_kobo integer`, fills it with `price_naira * 100`, makes it `NOT NULL`, and drops `price_naira`. Do the same for orders (`total_naira` → `total_kobo`, `Order.totalKobo`). Change `Dish` to `priceKobo`, update both presenters (v1 divides by 100, v2 shows it as is), and drop v2's `multipleOf(100)`. From here on, the lessons use kobo.
2. Give each version its own allowed `fields` and sort fields (`priceNaira` in v1, `price` in v2), so `GET /v2/menu?fields=priceNaira` is a 400.
3. Turn on the header way on a separate path, `/menu-h`, using `chooseVersion("1")`, and check all three styles give v2: `-H "Api-Version: 2"`, `-H "Accept: application/vnd.mamaput.v2+json"`, and `?api-version=2`.

**Done when** v1 and v2 show the same dish correctly after the kobo migration, ₦1,499.50 can be created through v2 and shows as `1499.5` in v1, v1 responses carry `Deprecation` and `Sunset` headers, and setting `sunsetAt` to yesterday makes v1 answer 410.

## Before moving on
<!-- bite: 21c63384-0676-4908-aec3-4ad1e5b7b5a6 -->

Mama Put API can now change without breaking anyone: breaking changes go in a new version, versions differ only at the edge, and old versions are announced, measured and retired properly.

But how does the phone app team *know* what v2 looks like? Right now they read our code, or ask us on WhatsApp. Every field, every query parameter, every error code exists only in TypeScript files they can't see. They need documentation, and it must never fall out of date with the code. That's OpenAPI, the next lesson.

## Related
<!-- bite: 65ecc454-4c98-4aff-9517-2bc638b76e3b -->

- [[backend/frameworks/express/11-api-docs|Next: API Docs with OpenAPI]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — designing an API that needs fewer versions
- [[backend/frameworks/nestjs/index|NestJS]] — has URI, header and media-type versioning built in, for comparison

## About this lesson
<!-- bite: 1f93b24b-cd8b-4480-a50a-55e401c67160 -->

**Level:** Intermediate. Lesson 10 of [[backend/frameworks/express/index|Express]]. Covers breaking versus non-breaking changes, path, header, media-type, query and dated versioning, presenters and input schemas per version over one shared service, a router per version, choosing a version from headers with `Vary`, defaulting to the oldest version, the `Deprecation` (RFC 9745), `Sunset` (RFC 8594) and `Link` headers, usage logging, and 410 after the sunset date.
