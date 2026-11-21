---
id: 2794514e-b909-4607-9add-e7deec39714c
---

# Routing

**Routing is how your app decides which function should answer a request, by looking at its method (like GET or POST) and its path (like `/menu/7`).** You meet routing every time you use a website: `/menu` shows the whole menu, `/menu/7` shows one dish, and the same address can mean "show it" or "delete it" depending on the method.

## Before you start
<!-- bite: e4b5ff94-16d2-4f6d-aaf2-cfb90b1dde19 -->

You should have the Mama Put API from [[backend/frameworks/express/01-what-express-is-and-a-first-app|lesson 1]] running with `npm run dev`.

After this lesson you will be able to:

1. Write routes for all the common methods: GET, POST, PATCH and DELETE.
2. Read an ID from the path, filters from the query string, and data from the body.
3. Choose the right status code for each answer.
4. Group related routes with `express.Router()`.

## Where we stopped
<!-- bite: 05698644-1882-427f-864a-1b0a775a0dd3 -->

Remember our menu from lesson 1? It was written straight into the route, and the only thing a client could do was ask for all of it. Mama's kitchen needs more than that:

1. See the whole menu, or only what's available today.
2. See one dish.
3. Add a new dish (she's started selling ofada rice).
4. Change a dish (the price of beans went up again).
5. Remove a dish.

Five jobs. Each one is a route, and the way we tell them apart is the method plus the path.

## Terms used in routing
<!-- bite: 45b8c15c-75dd-43c4-93e9-bf4e801ed916 -->

1. **Method**: This is also called the **HTTP verb**. It is the word at the front of a request that says what kind of action the client wants. GET means "give me", POST means "create this", PATCH means "change part of this", PUT means "replace this", and DELETE means "remove this".
2. **Path**: This is the part of the address after the domain, like `/menu/7`.
3. **Route parameter**: This is a named slot in a path, written with a colon, like `/menu/:id`. When a request for `/menu/7` arrives, Express puts `"7"` into `req.params.id`.
4. **Query string**: This is the part after a `?` in an address, like `?available=true`. It carries optional extras such as filters and page numbers. Express puts it in `req.query`.
5. **Body**: This is the data a client sends inside the request, usually as JSON, when it creates or changes something. Express puts it in `req.body`, but only after you switch on a **body parser**.
6. **Resource**: This is one kind of thing your API is about. The menu is a resource. Each dish is one item of it, with its own path.

## The menu as a resource
<!-- bite: dbe667d0-5d00-4fae-986c-de6c108db5a9 -->

The usual way to design these routes is around the resource, not the action. One path for the whole collection, one path for a single item, and the method says what to do:

| Method | Path | What it does | Status on success |
|---|---|---|---|
| GET | `/menu` | list dishes | 200 OK |
| GET | `/menu/:id` | get one dish | 200 OK |
| POST | `/menu` | add a dish | 201 Created |
| PATCH | `/menu/:id` | change some fields of a dish | 200 OK |
| DELETE | `/menu/:id` | remove a dish | 204 No Content |

Notice there's no `/addDish` or `/deleteDish`. The method already says "add" or "delete", so the path only needs to say *what*. This is the style called REST, and [[backend/02-api-design/01-apis-and-rest|APIs and REST]] explains it properly. Here we just use it.

## A place to keep the dishes
<!-- bite: a1613334-f416-4ecc-9c49-08feef57b9b3 -->

We don't have a database yet; that comes in [[backend/frameworks/express/08-data-with-postgres|lesson 8]]. For now, an array in memory will do. It resets every time the app restarts, which is fine while we're learning.

Replace `src/server.ts` with this start:

```ts
import express from "express";

type Dish = {
  id: string;
  name: string;
  priceNaira: number;
  available: boolean;
};

const dishes: Dish[] = [
  { id: "1", name: "Jollof rice", priceNaira: 1500, available: true },
  { id: "2", name: "Beans and plantain", priceNaira: 1200, available: true },
  { id: "3", name: "Pounded yam and egusi", priceNaira: 2500, available: false },
];
let nextId = 4;

const app = express();
app.use(express.json());
```

That last line, `app.use(express.json())`, is the body parser. Without it, `req.body` is `undefined` even when the client sent JSON. Why it's written with `app.use` is the whole of the next lesson. For now: it reads the JSON body before your routes run.

## Reading the query string: listing dishes
<!-- bite: 9c1c8782-544a-45ad-a96e-14634929139a -->

```ts
app.get("/menu", (req, res) => {
  if (req.query.available === "true") {
    res.json(dishes.filter((d) => d.available));
    return;
  }
  res.json(dishes);
});
```

```bash
curl http://localhost:3000/menu
curl "http://localhost:3000/menu?available=true"
```

Two things to notice. First, the query value is the **text** `"true"`, not the boolean `true`. Everything in a URL is text. Second, the query string is optional: the same route answers both requests. That's what query strings are for, extras that change *how* you get the resource, not *which* resource.

## Reading a route parameter: one dish
<!-- bite: c0aae56d-1da8-436f-829b-e56d231e0fee -->

```ts
app.get("/menu/:id", (req, res) => {
  const dish = dishes.find((d) => d.id === req.params.id);
  if (!dish) {
    res.status(404).json({ error: "Dish not found" });
    return;
  }
  res.json(dish);
});
```

```bash
curl http://localhost:3000/menu/2
curl -i http://localhost:3000/menu/99
```

`:id` is a slot. For `/menu/2`, Express sets `req.params.id` to `"2"` (text again). For `/menu/99` nothing matches in our array, so we answer 404 ourselves. This is a different 404 from lesson 1's: there, *no route* matched. Here the route matched fine, but the dish doesn't exist. Both mean "not found", and the client doesn't need to know which.

See the `return` after the 404? Without it, the code carries on to `res.json(dish)` and tries to answer twice. That's the "Cannot set headers after they are sent" error from lesson 1.

## Reading the body: adding a dish
<!-- bite: 046f4a66-a1e5-4bbb-a484-4774f84335e8 -->

```ts
app.post("/menu", (req, res) => {
  const { name, priceNaira } = req.body;
  const dish: Dish = {
    id: String(nextId++),
    name,
    priceNaira,
    available: true,
  };
  dishes.push(dish);
  res.status(201).location(`/menu/${dish.id}`).json(dish);
});
```

```bash
curl -i -X POST http://localhost:3000/menu \
  -H "Content-Type: application/json" \
  -d '{"name":"Ofada rice","priceNaira":2000}'
```

`-X POST` sets the method, `-H` says "this body is JSON", and `-d` is the body itself. Leave out the `Content-Type` header and predict what happens. (`express.json()` only reads bodies that say they're JSON, so `req.body` stays `undefined`, and the destructuring throws.)

The answer is `201 Created`, not 200, because something new now exists. The `Location` header tells the client where to find it. Good APIs do both, and clients rely on them.

There's a big hole here, sha. We trust whatever the client sends. Send `{"priceNaira": "free"}` with no name and we'll happily save it. Checking the body is [[backend/frameworks/express/06-validation|lesson 6]]. Keep the hole in mind; we'll close it.

## Changing and removing a dish
<!-- bite: 565ffd3f-13bd-4074-98c3-d3bd0aa0485a -->

```ts
app.patch("/menu/:id", (req, res) => {
  const dish = dishes.find((d) => d.id === req.params.id);
  if (!dish) {
    res.status(404).json({ error: "Dish not found" });
    return;
  }
  if (req.body.name !== undefined) dish.name = req.body.name;
  if (req.body.priceNaira !== undefined) dish.priceNaira = req.body.priceNaira;
  if (req.body.available !== undefined) dish.available = req.body.available;
  res.json(dish);
});

app.delete("/menu/:id", (req, res) => {
  const index = dishes.findIndex((d) => d.id === req.params.id);
  if (index === -1) {
    res.status(404).json({ error: "Dish not found" });
    return;
  }
  dishes.splice(index, 1);
  res.sendStatus(204);
});

app.listen(3000, () => console.log("Mama Put API on http://localhost:3000"));
```

PATCH only changes the fields the client sent: beans goes up in price, and its name stays the same. (PUT would replace the whole dish, so the client would have to send every field.) DELETE answers `204 No Content`: it worked, and there's nothing more to say.

```bash
curl -X PATCH http://localhost:3000/menu/2 \
  -H "Content-Type: application/json" -d '{"priceNaira":1400}'
curl -i -X DELETE http://localhost:3000/menu/3
```

## Path parameters or query parameters?
<!-- bite: 92ddd3b6-f4d9-4c4b-9328-6ab91599cad4 -->

You've now used both, so here's the rule for choosing.

1. **A path parameter says *which thing*.** `/menu/2` is dish 2. Take the `2` away and you're asking for something else. If it identifies the resource, it goes in the path.
2. **A query parameter says *how you want it*.** `/menu?available=true` is still the menu, just filtered. Take the query away and you still get the menu. Filters, searches, sorting, page numbers and "which fields to include" all go in the query.

So `GET /orders?customer=ada&status=pending` is the orders list, filtered. And `GET /customers/ada/orders` is "Ada's orders" as its own resource. Both are fine REST. Pick one and use it everywhere.

Query parameters get a whole lesson later, [[backend/frameworks/express/09-listing|Pagination, Filtering, Searching, Sorting and Field Selection]], because once the menu has 500 dishes, "give me everything" stops working.

One more thing you may have noticed: we answer with a bare array here, a dish there, and `{ "error": "..." }` when it fails. Three different shapes. A client has to guess what it'll get. In [[backend/frameworks/express/07-errors|lesson 7]] every response, good or bad, gets one predictable shape.

## The order of routes matters
<!-- bite: 930a0298-9fcc-44c1-8e45-5a579220c179 -->

Mama wants a "today's specials" page. You add it at the bottom:

```ts
app.get("/menu/specials", (req, res) => {
  res.json(dishes.filter((d) => d.priceNaira < 1500));
});
```

Before you try it, predict: what does `GET /menu/specials` return?

It returns `404 Dish not found`. Remember from lesson 1 that Express walks down the routes **in the order you wrote them**. `/menu/:id` comes first, and `:id` matches *any* text, including `"specials"`. So Express runs the one-dish handler with `req.params.id === "specials"`, finds no such dish, and answers 404. Your specials route never gets a turn.

The fix: put fixed paths **before** paths with parameters.

```ts
app.get("/menu/specials", ...);   // first
app.get("/menu/:id", ...);        // then the catch-all slot
```

This "first match wins" rule comes back again and again in Express. Keep it close.

## Grouping routes with a Router
<!-- bite: 1aab885a-c3c6-4bec-a122-7908cf96218a -->

Look at our file. Every menu route starts with `/menu`, and soon we'll have `/orders` and `/auth` too. One long file full of `app.get(...)` gets hard to read fast.

`express.Router()` is a mini app that holds a group of routes. You write the paths relative to where it will be mounted, then plug it in:

```ts
const menuRouter = express.Router();

menuRouter.get("/", (req, res) => { /* list */ });
menuRouter.get("/specials", (req, res) => { /* specials */ });
menuRouter.get("/:id", (req, res) => { /* one dish */ });
menuRouter.post("/", (req, res) => { /* add */ });
menuRouter.patch("/:id", (req, res) => { /* change */ });
menuRouter.delete("/:id", (req, res) => { /* remove */ });

app.use("/menu", menuRouter);
```

`app.use("/menu", menuRouter)` says "any request whose path starts with `/menu`, hand it to this router". Inside, `"/"` means `/menu` and `"/:id"` means `/menu/:id`. Same routes, now in one group. In [[backend/frameworks/express/04-structuring-an-express-app|lesson 4]] each group gets its own file.

## Express 5 path rules
<!-- bite: bd9b00fd-5e93-4a40-a363-6b5b32a041ff -->

If you read older Express tutorials, you'll see paths like `/files/*` or `/menu/:id?`. Express 5 changed these:

1. A wildcard must have a name: `/files/*path`, not `/files/*`. The matched part arrives as `req.params.path`.
2. An optional part goes in braces: `/menu{/:id}`, not `/menu/:id?`.
3. You can't put regular-expression characters like `(`, `)` or `+` straight into a path string any more.

The old forms throw an error when the app starts, which is better than quietly matching the wrong thing.

## The TypeScript in this lesson
<!-- bite: b148cb60-21a2-47a6-a889-476d29c958af -->

1. **`type Dish = { id: string; ... }`**: This creates a **type**, a name for a shape of data. It says "a Dish always has an `id` that is text, a `name` that is text, a `priceNaira` that is a number and an `available` that is true or false". TypeScript then warns you if you build a dish with a missing or wrong field. Types are only for checking; they vanish when the code runs.
2. **`string`, `number`, `boolean`**: These are the basic types: text, numbers (whole or with decimals, TypeScript doesn't separate them), and true/false.
3. **`Dish[]`**: This means "an array of Dish". `const dishes: Dish[] = [...]` says "dishes is a list, and everything in it must be a Dish".
4. **`let nextId = 4`**: `let` makes a name you can change later, which we do with `nextId++`. Use it only when you really need to change the value.
5. **`nextId++`**: This gives you the current value, then adds one. So the first new dish gets 4 and `nextId` becomes 5.
6. **`String(nextId++)`**: This turns the number into text, because our IDs are text (they arrive from the URL as text anyway).
7. **`dishes.find((d) => d.id === req.params.id)`**: `find` walks the array and gives back the first item where your function says true, or `undefined` if none does. `filter` is the same but gives back *all* matching items as a new array. `findIndex` gives back the position instead of the item, or `-1`.
8. **`===` and `!==`**: These compare two values exactly. `"2" === 2` is false, because one is text and one is a number. Always use these, not `==`, which tries to convert things first and surprises people.
9. **`const { name, priceNaira } = req.body`**: This is **destructuring**. It's a short way of writing `const name = req.body.name; const priceNaira = req.body.priceNaira;`.
10. **`if (!dish)`**: `!` means "not". `!dish` is true when `dish` is `undefined`, meaning nothing was found.
11. **`dishes.splice(index, 1)`**: This removes 1 item at that position from the array, changing the array itself.

## Common mistakes
<!-- bite: a32f9c96-9de5-4e17-8eaf-7aae69ee74ed -->

1. **No `express.json()`.** `req.body` is `undefined`, and reading `req.body.name` throws.
2. **The client didn't send `Content-Type: application/json`.** Same symptom. `express.json()` ignores bodies that don't say they're JSON.
3. **Treating params and query as numbers or booleans.** `req.params.id` is `"2"`, not `2`, and `req.query.available` is `"true"`, not `true`. Convert them on purpose.
4. **A parameter route above a fixed one.** `/:id` swallows `/specials`.
5. **Verbs in paths.** `/getDish/2` instead of `GET /menu/2`. The method is already the verb.
6. **Always answering 200.** Created things are 201, empty answers are 204, missing things are 404. Clients make decisions from the status.

## Check your understanding
<!-- bite: 127919d6-e5a1-4ea6-8147-5e095fe61baa -->

1. Which route and which part of `req` would you use for each? (a) all available dishes, (b) dish 5, (c) a new dish's name and price.
2. Why is the answer to a successful POST 201 and not 200?
3. You have `router.get("/:id")` and then `router.get("/popular")`. A request for `/menu/popular` arrives. What runs?

<details>
<summary>Answers, after your attempt</summary>

1. (a) `GET /menu?available=true`, using `req.query.available`. (b) `GET /menu/5`, using `req.params.id`. (c) `POST /menu`, using `req.body`.
2. 201 means "created": a new thing now exists, and the `Location` header says where. 200 only means "it went fine".
3. The `/:id` handler, with `id` set to `"popular"`, because it was registered first and `:id` matches any text. Move `/popular` above it.

</details>

## Practice
<!-- bite: 51cc3f9a-f309-4c53-a0d2-b79bbb7e4a91 -->

Mama Put API needs orders. Using a second array and a second router mounted at `/orders`, add:

1. `POST /orders` with a body like `{ "dishId": "1", "quantity": 2 }`. Answer 201 with the new order, which has an `id`, the `dishId`, the `quantity`, and `status: "pending"`.
2. `GET /orders/:id` returns one order, or 404.
3. `PATCH /orders/:id/status` with `{ "status": "ready" }` changes the status.

Edge cases: ordering a dish that doesn't exist should answer 404, not create an order.

**Done when** you can create an order with `curl`, fetch it, mark it ready, and fetch it again to see the new status.

## Your project so far
<!-- bite: b6055f06-def4-444a-a4d3-b0f4498dfa18 -->

```text
mama-put-api/
├── package.json
├── package-lock.json
├── tsconfig.json
└── src/
    └── server.ts        ← the Dish type, the dishes array, express.json(),
                            and the menu routes (now on a menu router)
```

1. **`src/server.ts`**: now holds the `Dish` type, the in-memory `dishes` array, `express.json()`, a `menuRouter` with all six menu routes (list, specials, one dish, add, change, remove), and the orders routes from the practice. Still one file, on purpose. In lesson 4 it gets split up.

## Before moving on
<!-- bite: 792a145b-2937-472d-944a-e6e18c3a4a46 -->

You can now design a resource's routes, read the three places a request carries data (path, query, body), answer with the right status, and keep related routes together with a Router.

But look at what we keep repeating. Every route that takes an ID does the same "find it or 404". Every route will soon need "is this user logged in?". We switched on `express.json()` with a strange `app.use` line. All of that is **middleware**, the idea Express is really built on. That's the next lesson.

## Related
<!-- bite: 1e3a176d-5ce0-4dc1-a705-b49f7cf719ba -->

- [[backend/frameworks/express/03-middleware|Next: Middleware]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — the design ideas behind these routes
- [[backend/frameworks/express/01-what-express-is-and-a-first-app|Previous: What Express Is, and Your First App]]

## About this lesson
<!-- bite: f7c8bf09-0d3a-4bfe-a92e-6022e54adcfc -->

**Level:** Beginner. Lesson 2 of [[backend/frameworks/express/index|Express]]. Covers routes for every common method, route parameters, query strings, JSON bodies, status codes, route order, `express.Router()`, and the Express 5 path rules.
