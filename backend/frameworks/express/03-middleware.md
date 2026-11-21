---
id: 6b7b78e4-edbc-4803-91dc-593df9449e26
---

# Middleware

**Middleware is a function that runs in the middle, between a request arriving and your route answering it, and it can look at the request, change it, answer it, or pass it on.** You've already used one: `express.json()` reads the body before your routes run. Logging every request, checking a login, and catching errors are all middleware too. In Express, almost everything is.

## Before you start
<!-- bite: 2ae60e63-ffd5-4992-9a19-f46af20ffabe -->

You should have the menu routes and the menu router from [[backend/frameworks/express/02-routing|lesson 2]].

After this lesson you will be able to:

1. Explain the middleware chain and what `next()` does.
2. Write your own middleware: a request logger and a "load this dish or 404" step.
3. Attach middleware to the whole app, to one router, or to one route.
4. Predict what goes wrong when middleware is in the wrong order.

## Where we stopped
<!-- bite: 86cc88c8-2f8c-4f6e-b32b-0a171616794a -->

At the end of lesson 2 we noticed three things that didn't fit inside any single route:

1. `app.use(express.json())`, a line that runs for every request, before the routes.
2. "Find the dish or answer 404", copied into GET, PATCH and DELETE.
3. Soon, "is this person logged in?", which many routes will need.

These are all the same kind of thing: work that should happen **around** your routes, not inside one of them. Express's answer is middleware.

## The kid version
<!-- bite: 101fa58a-018f-4717-8d4e-f61f9c91cf05 -->

Back to Mama Put's stand, but now she has helpers. A customer's order passes along a line:

1. The first helper writes the order in the book (a logger).
2. The second checks the customer has paid (a login check).
3. The third checks the pot isn't empty (load the dish or say "finished").
4. Mama dishes the food (your route).

Each helper either passes the order down the line, or stops it and answers the customer straight away ("you haven't paid", "jollof is finished"). Mama only sees orders that got past everybody.

**Where the picture stops working.** The helpers in Express can also act on the way *out*, after Mama has served, like writing down how long the order took. We'll see that in the logger.

## Terms used in middleware
<!-- bite: c749a031-a36c-49a0-9c70-c55ca444cac2 -->

1. **Middleware**: This is a function with the shape `(req, res, next) => { ... }`. It runs before (or instead of) your route handler.
2. **`next`**: This is a function Express gives to each middleware. Calling `next()` means "I'm done, pass the request to the next one in line". Not calling it means "I've answered, stop here".
3. **The chain**: This is also called the **pipeline** or **stack**. It is the list of middleware and routes, in the order you added them, that every request walks through.
4. **`res.locals`**: This is an empty object on every response where middleware can leave things for later steps, like the dish it loaded. It only lives for one request.
5. **Error-handling middleware**: This is middleware with **four** arguments, `(err, req, res, next)`. Express only calls it when something has gone wrong.

## Every route is middleware already
<!-- bite: f8f45f92-b030-4b9e-a5f0-703ef8cbb4d6 -->

Here's the surprise. Look at a route handler from lesson 2:

```ts
app.get("/menu", (req, res) => {
  res.json(dishes);
});
```

That's a middleware that answers and doesn't call `next`. Express keeps one list. `app.use(...)`, `app.get(...)` and `app.post(...)` all add to the same list, in order. When a request comes in, Express walks the list from the top:

1. Does this entry match the request? (`app.use` matches every method; `app.get("/menu")` matches only GET `/menu`.)
2. If yes, run it.
3. If it called `next()`, carry on down the list. If it answered, stop.
4. If it reaches the bottom with no answer, send the default 404.

So when lesson 1 said "Express walks your routes in order", this is what it meant. Routes are just the middleware at the end of the line that answer.

## Writing your first middleware: a logger
<!-- bite: a621f06e-0248-4f0d-a7ae-3a7fb3207029 -->

Mama wants to know what people are asking for. Add this near the top of `src/server.ts`, **before** the routes:

```ts
import type { Request, Response, NextFunction } from "express";

function logRequests(req: Request, res: Response, next: NextFunction) {
  const started = Date.now();
  res.on("finish", () => {
    const ms = Date.now() - started;
    console.log(`${req.method} ${req.originalUrl} → ${res.statusCode} (${ms} ms)`);
  });
  next();
}

app.use(logRequests);
app.use(express.json());
```

Make a few requests and watch the terminal:

```text
GET /menu → 200 (2 ms)
GET /menu/99 → 404 (0 ms)
POST /menu → 201 (1 ms)
```

Read it slowly, because it shows the in-and-out idea from the kid version:

1. On the way **in**, the logger notes the time and calls `next()` so the request carries on.
2. `res.on("finish", ...)` sets up a small function for later. Express runs it when the response has been sent, on the way **out**.
3. By then we know the status code, so we can print it with the time taken.

If you forget `next()`, every request hangs, because the logger neither answers nor passes it on. Try it once on purpose, so you recognise the symptom.

## Order is behaviour
<!-- bite: 7eabdce8-a7d1-4e54-a39d-405f5cd3fc1f -->

Move `app.use(express.json())` *below* your routes and send a POST. Predict first.

`req.body` is `undefined`. The request reached the POST route before the body parser had a chance to run, because the body parser is now further down the list. Nothing crashed in Express. It did exactly what the order said.

This is the most important habit in Express: **when something "isn't running", check the order first.** A rough order that works for most apps:

1. Things that must see every request: logging, request IDs.
2. Security headers and CORS (lesson 10).
3. Body parsers like `express.json()`.
4. Your routers.
5. A catch-all 404.
6. The error handler, always last.

## Middleware for one router or one route
<!-- bite: 896a5419-d0f9-4ac9-bed7-fb021a0285a2 -->

Not everything should run for every request. You can attach middleware at three levels.

**The whole app:** `app.use(fn)`. Runs for everything.

**One router:** `menuRouter.use(fn)`. Runs only for requests that reached that router, so only for paths starting with `/menu`.

**One route:** put it between the path and the handler. You can list as many as you like, and they run left to right:

```ts
menuRouter.patch("/:id", loadDish, (req, res) => { ... });
```

That last one is how we get rid of the repeated "find it or 404".

## Removing the repetition: `loadDish`
<!-- bite: 8e230973-4616-4e3a-842d-6420ddb0fd91 -->

```ts
function loadDish(req: Request, res: Response, next: NextFunction) {
  const dish = dishes.find((d) => d.id === req.params.id);
  if (!dish) {
    res.status(404).json({ error: "Dish not found" });
    return;
  }
  res.locals.dish = dish;
  next();
}
```

It either stops the request with a 404, or leaves the dish in `res.locals` and passes the request on. Now the routes only do their real job:

```ts
menuRouter.get("/:id", loadDish, (req, res) => {
  res.json(res.locals.dish);
});

menuRouter.patch("/:id", loadDish, (req, res) => {
  const dish = res.locals.dish as Dish;
  if (req.body.name !== undefined) dish.name = req.body.name;
  if (req.body.priceNaira !== undefined) dish.priceNaira = req.body.priceNaira;
  if (req.body.available !== undefined) dish.available = req.body.available;
  res.json(dish);
});

menuRouter.delete("/:id", loadDish, (req, res) => {
  const dish = res.locals.dish as Dish;
  dishes.splice(dishes.indexOf(dish), 1);
  res.sendStatus(204);
});
```

Three copies of the same check became one function. Change the 404 message once and every route gets it. That's the payoff of middleware: **one idea, one place**.

(`res.locals` is typed loosely, which is why we write `as Dish`. That's fine for now. In the structure lesson the services return proper types and most of these casts go away.)

## Middleware you install
<!-- bite: ebfb531d-efbc-4ddf-9724-6f8e9ce3b034 -->

Most real apps use a few middleware written by other people. You've met the built-in ones:

1. `express.json()` reads JSON bodies.
2. `express.urlencoded()` reads HTML form bodies.
3. `express.static("public")` serves files, like images, from a folder.

And you'll add some from npm later: `helmet` for security headers and `cors` for browser access ([[backend/frameworks/express/14-security|lesson 14]]), and `pino-http` for proper logs ([[backend/frameworks/express/27-observability|lesson 27]]). They're all the same shape, `(req, res, next)`, which is why they plug straight in with `app.use`.

## The two special ones at the end
<!-- bite: 3f2f2e72-1cf0-4874-8ae6-c0a95a449e59 -->

Two pieces go at the very bottom of every app. We'll build them properly in [[backend/frameworks/express/07-errors|lesson 7]], but you should know what they are now.

**A catch-all 404.** If a request gets past every route, this answers in your API's own JSON shape instead of Express's "Cannot GET" text:

```ts
app.use((req, res) => {
  res.status(404).json({ error: "Not found" });
});
```

**An error handler.** If any middleware or route throws, or calls `next(err)`, Express skips every normal middleware and jumps to the first one with **four** arguments:

```ts
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err);
  res.status(500).json({ error: "Something went wrong" });
});
```

The four arguments are how Express tells it apart. Write three, even if you don't use `next`, and it becomes an ordinary middleware that never sees errors. This is a classic Express bug, and it fails silently.

## The TypeScript in this lesson
<!-- bite: 57ec75e9-b273-4bd8-815f-79050afd01d9 -->

1. **`import type { Request, Response, NextFunction } from "express"`**: This imports **only types**, not code. `Request` and `Response` describe `req` and `res`; `NextFunction` describes `next`. We need the word `type` because Node runs our TypeScript by deleting the types, and `import type` tells it this whole line can be deleted.
2. **`function logRequests(req: Request, res: Response, next: NextFunction)`**: The `: Request` after a parameter is a **type annotation**. Inside `app.get(...)` TypeScript could work out these types by itself. In a function standing on its own, it can't know what will be passed in, so we say.
3. **`res.on("finish", () => { ... })`**: This hands Node a callback to run later, when the response has finished sending. Notice the callback can still use `started`, a variable from the outer function, even though the outer function has long returned. A function that remembers the variables around where it was written is called a **closure**, and you'll use them all the time.
4. **`Date.now()`**: This gives the current time as a number of milliseconds, so subtracting two of them gives how long something took.
5. **`res.locals.dish as Dish`**: `res.locals` can hold anything, so TypeScript doesn't know what `res.locals.dish` is. `as Dish` says "trust me, it's a Dish". This is called a **type assertion**. TypeScript doesn't check it, so use it sparingly. It's a promise you make, and if you're wrong, the bug shows up when the code runs.
6. **`(err: Error, req: Request, res: Response, next: NextFunction)`**: `Error` is the built-in type for errors. The error handler must list all four parameters, even unused ones, because Express counts them to know it's an error handler.

## Common mistakes
<!-- bite: af7ada9d-6350-4baf-993a-64a0d48c82fa -->

1. **Forgetting `next()`.** The request hangs with no error. If a request "just spins", look for a middleware that neither answers nor calls `next`.
2. **Calling `next()` after answering.** The request carries on to a route that answers again: "Cannot set headers after they are sent".
3. **Wrong order.** Body parser after the routes, auth after the route it should protect, error handler above the routes.
4. **An error handler with three arguments.** It's just normal middleware then.
5. **Doing slow work for every request.** App-level middleware runs on *every* request, including the health check. Keep it cheap, or attach it lower down.

## Check your understanding
<!-- bite: df9af6d8-8076-4034-9bbf-83c948669eaf -->

1. What are the two things a middleware can do with a request?
2. You put `app.use(requireLogin)` *after* `app.use("/menu", menuRouter)`. Is the menu protected?
3. Why does the logger use `res.on("finish", ...)` instead of printing straight away?

<details>
<summary>Answers, after your attempt</summary>

1. Answer it (and stop the chain), or call `next()` to pass it on. (It can also change `req` or `res.locals` before passing it on.)
2. No. The menu router answers the request first, so the chain never reaches `requireLogin`. Middleware only protects what comes after it.
3. When the request arrives, we don't know the status code or how long it will take. `finish` fires after the response is sent, when both are known.

</details>

## Practice
<!-- bite: eccb3ebe-0f17-4dde-98de-a5d427a2e675 -->

1. Write a middleware `kitchenOnly` that checks for a header `X-Staff-Key` equal to `"jollof123"`. If it's missing or wrong, answer `401` with `{ "error": "Kitchen staff only" }`. Otherwise call `next()`.
2. Attach it to `POST`, `PATCH` and `DELETE` on the menu, but **not** to the two GETs, so customers can still read the menu.
3. Write a `loadOrder` middleware for your orders router from the lesson 2 practice, and use it the same way as `loadDish`.

(A secret header is not real security. It's a stand-in until we do proper logins in [[backend/frameworks/express/12-authentication|lesson 12]].)

**Done when** `curl -X DELETE /menu/1` without the header gets 401, the same with `-H "X-Staff-Key: jollof123"` gets 204, and `GET /menu` works with no header at all.

## Your project so far
<!-- bite: 77e18a40-e334-45ed-874d-25a5d7e528f1 -->

```text
mama-put-api/
├── package.json
├── package-lock.json
├── tsconfig.json
└── src/
    └── server.ts        ← everything, in this order:
                            types and arrays → logRequests → express.json()
                            → loadDish, kitchenOnly → menu and orders routers
                            → catch-all 404 → error handler → listen
```

1. **`src/server.ts`**: now also has `logRequests`, `loadDish`, `kitchenOnly` (from the practice), the catch-all 404 and the error handler. Read it top to bottom and you're reading the order every request walks through.

## Before moving on
<!-- bite: 6a1ac15b-71c2-46b0-b1fe-71050d6583d1 -->

You now see an Express app the way Express sees it: one list of functions, walked from the top, where each one answers or passes the request on. Order decides behaviour.

But our `server.ts` is getting crowded. Types, the dishes array, the logger, `loadDish`, the menu router, the orders router, `kitchenOnly`, all in one file. Mama's business is growing, and the code needs rooms. That's the next lesson: structuring an Express app.

## Related
<!-- bite: 5221a85b-3bef-48df-a14b-bbfff0e3d9c1 -->

- [[backend/frameworks/express/04-structuring-an-express-app|Next: Structuring an Express App]]
- [[backend/01-foundations/03-the-request-lifecycle/index|The Request Lifecycle]] — the same pipeline, in every framework
- [[backend/frameworks/node/02-error-handling|Error Handling in Node.js]] — what happens below Express when things fail

## About this lesson
<!-- bite: d1b1a2a5-543e-4b5a-948d-872fccc1f337 -->

**Level:** Beginner → Intermediate. Lesson 3 of [[backend/frameworks/express/index|Express]]. Covers the middleware chain, `next()`, the in-and-out logger, order as behaviour, app, router and route level middleware, `res.locals`, and the 404 and error handlers.
