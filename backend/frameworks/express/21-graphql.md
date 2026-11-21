---
id: baf58e28-bf2d-4ee3-8bc7-9ce889173504
---

# GraphQL

**GraphQL is a way of building an API where the server publishes one typed description of all its data, and each client sends a query saying exactly which pieces it wants, in the shape it wants them. One request, one endpoint, and the answer has exactly the fields asked for, no more and no fewer.** REST says "here are the resources, take what each URL gives you". GraphQL says "here's everything I have; ask for what you need".

## Before you start
<!-- bite: 416b8ce8-ae95-4249-85d3-6d2085ae6795 -->

You should have the whole of Parts 1 to 4, up to [[backend/frameworks/express/20-real-time|lesson 20]]. GraphQL here sits *beside* REST, on top of the same services, so everything you built is reused.

**What to install.** Nothing outside npm. GraphQL is a language and a set of libraries; there's no separate server program or compiler to set up. In the `api` folder:

```bash
npm install graphql graphql-yoga dataloader
```

1. **`graphql`** is the reference GraphQL engine for JavaScript: it reads schemas, checks queries and runs resolvers.
2. **`graphql-yoga`** is the GraphQL server that plugs into Express.
3. **`dataloader`** batches database lookups (step 4).

Step 6 adds one more, `@escape.tech/graphql-armor`, for query limits. The schema in step 1 is just a text file you create, `src/graphql/schema.graphql`; Yoga reads it when the app starts. For syntax colours in your editor, install a GraphQL extension (VS Code has an official one, "GraphQL: Language Feature Support").

After this lesson you will be able to:

1. Read and write a GraphQL schema: types, queries, mutations, inputs, enums, nullability.
2. Serve it from Express with GraphQL Yoga, using the same services, rules and permissions as REST.
3. Fix the N+1 problem with DataLoader.
4. Paginate with connections, turn `AppError`s into GraphQL errors, and handle field-level permissions.
5. Protect a GraphQL API from expensive queries, and say when GraphQL beats REST and when it doesn't.

## Where we stopped
<!-- bite: 72db6839-0753-41c3-9eec-167164bea0cb -->

The new phone app's order screen shows: the order, its dish (name, photo, price), and the customer's last three orders underneath. With REST, that's:

1. `GET /v2/orders/42`
2. `GET /v2/menu/1` (for the dish)
3. `GET /v2/me`
4. `GET /v2/orders?mine=true&limit=3`, then a `GET /v2/menu/:id` for each of those dishes.

Six or seven round trips on a 3G connection in a market, each one waiting for the last. And each response carries fields the screen doesn't show. Lesson 9's `fields=` helps with the extra fields; it can't help with the round trips.

The phone team asks: can we ask for all of it, in one go?

## The kid version
<!-- bite: 1f803762-197e-4eea-b757-4567f4405212 -->

At a REST restaurant, the menu has set plates. Plate 1: rice, stew, chicken. Plate 2: beans, plantain. If you want rice *and* plantain, you order two plates and leave half of each.

At a GraphQL restaurant, you write your own order on a slip: "rice, plantain, one piece of chicken, and the drinks list". The kitchen knows everything it can make, and sends exactly that, on one tray.

**Where the picture stops working.** A greedy customer could write "every dish, and for each dish, every customer who ordered it, and for each customer, every dish *they* ordered..." on one slip. A real kitchen would laugh. Our server has to be taught to refuse slips like that.

## Terms used in GraphQL
<!-- bite: b1aef1d7-7e93-4faa-9f9c-d905e0fa0519 -->

1. **Schema**: This is the typed description of everything the API offers, written in GraphQL's own language (SDL, the schema definition language).
2. **Type**: This is a shape, like `Dish` with fields `id`, `name`, `price`.
3. **Query**: This is a read. Clients send a query document listing the fields they want.
4. **Mutation**: This is a write, like `placeOrder`.
5. **Resolver**: This is the function that works out the value of one field. The server calls resolvers to build the answer.
6. **Context**: This is an object made fresh for every request and passed to every resolver: who's logged in, the services, the loaders.
7. **N+1 problem**: This is when fetching a list of N things runs 1 query for the list and then N more queries, one per item, for something each item needs.
8. **DataLoader**: This is a small library that collects all the "load dish 1", "load dish 4", "load dish 1" calls made during one moment and turns them into one batched query.
9. **Connection**: This is GraphQL's usual shape for a paginated list: `edges`, each with a `node` and a `cursor`, plus `pageInfo`.

## Step 1: the schema
<!-- bite: dc26245a-72b2-4de2-94ef-ae29e824446e -->

`src/graphql/schema.graphql`:

```graphql
type Query {
  menu(first: Int = 20, after: String, search: String): DishConnection!
  dish(id: ID!): Dish
  me: User
  order(id: ID!): Order
}

type Mutation {
  placeOrder(input: PlaceOrderInput!): PlaceOrderPayload!
}

type Money {
  amount: Int!        # in kobo
  currency: String!
}

type Dish {
  id: ID!
  name: String!
  price: Money!
  available: Boolean!
  photoUrl: String
  thumbnailUrl: String
  portionsLeft: Int   # staff only; null for everyone else
}

enum OrderStatus {
  PENDING
  READY
  COLLECTED
}

type Order {
  id: ID!
  dish: Dish!
  quantity: Int!
  total: Money!
  status: OrderStatus!
  paidAt: String
  createdAt: String!
}

type User {
  id: ID!
  name: String!
  orders(first: Int = 10, after: String): OrderConnection!
}

type DishConnection { edges: [DishEdge!]!  pageInfo: PageInfo! }
type DishEdge       { cursor: String!      node: Dish! }
type OrderConnection { edges: [OrderEdge!]! pageInfo: PageInfo! }
type OrderEdge       { cursor: String!      node: Order! }
type PageInfo       { hasNextPage: Boolean! endCursor: String }

input PlaceOrderInput {
  dishId: ID!
  quantity: Int!
  idempotencyKey: String!
}

type PlaceOrderPayload {
  order: Order!
}
```

How to read it:

1. **`!` means "never null".** `name: String!` always has a value. `photoUrl: String` may be `null`. Be careful with `!`: if a resolver ever fails for a non-null field, GraphQL can't put `null` there, so it nulls the *parent* object instead, and that can wipe out a large part of the answer. Mark fields `!` when they truly can't be missing.
2. **Arguments can have defaults**: `first: Int = 20`.
3. **`input` types** are for arguments. Mutations take one `input` object; that keeps them easy to extend later without breaking anyone.
4. **Mutations return a payload type**, not the order directly, for the same reason: next year `PlaceOrderPayload` can gain a `checkoutUrl` field without changing anything existing.
5. **`enum`** is a fixed set of words. GraphQL enums are written in capitals by convention, so `PENDING` here is our `"pending"`.

Now the phone team's screen is **one** request:

```graphql
query OrderScreen($id: ID!) {
  order(id: $id) {
    id
    status
    total { amount currency }
    dish { name thumbnailUrl }
  }
  me {
    name
    orders(first: 3) {
      edges { node { id status dish { name } } }
    }
  }
}
```

And the answer has exactly that shape. Nothing more.

## Step 2: GraphQL Yoga in Express
<!-- bite: 272311b6-4f96-4407-9dc1-c10231653a91 -->

You installed `graphql`, `graphql-yoga` and `dataloader` in "Before you start". Now `src/graphql/yoga.ts`:

```ts
import { readFileSync } from "node:fs";
import { createYoga, createSchema } from "graphql-yoga";
import type { Request, Response } from "express";
import { resolvers } from "./resolvers.ts";
import { createLoaders } from "./loaders.ts";
import { maskError } from "./errors.ts";
import type { AppDeps } from "../app.ts";

const typeDefs = readFileSync(new URL("./schema.graphql", import.meta.url), "utf8");

export function createGraphql(deps: AppDeps) {
  return createYoga<{ req: Request; res: Response }>({
    schema: createSchema({ typeDefs, resolvers }),
    graphqlEndpoint: "/graphql",
    graphiql: deps.environment !== "production",
    maskedErrors: { maskError },
    context: ({ req }) => ({
      user: req.user ?? null,
      services: deps.services,
      loaders: createLoaders(deps.repositories),
    }),
  });
}
```

and in `app.ts`, next to the REST API:

```ts
const graphql = createGraphql(deps);
app.use(graphql.graphqlEndpoint, generalLimit, authenticate, graphql);
```

Mounted before `express.json()`, because Yoga reads the request body itself. `authenticate` from lesson 12 reads the Bearer token if there is one and sets `req.user`, without *requiring* it: in GraphQL, one request can mix public fields (`menu`) and private ones (`me`), so each resolver decides.

`context` runs once per request. Notice `createLoaders(...)` is inside it: loaders must be **fresh for every request** (step 4 says why).

`graphiql` turns on a web page at `/graphql` where you can type queries and explore the schema. Open `http://localhost:3000/graphql` in the browser and try the query above. Off in production; a playground for the whole world isn't needed.

## Step 3: resolvers call the same services
<!-- bite: 8b14c669-e614-4ca8-ae37-90199592538c -->

`src/graphql/resolvers.ts`:

```ts
import { GraphQLError } from "graphql";
import type { GraphqlContext } from "./context.ts";
import { encodeCursor } from "../shared/cursor.ts";
import { can } from "../auth/policy.ts";
import type { Dish } from "../menu/menu.types.ts";
import type { Order } from "../orders/orders.types.ts";

const money = (amountKobo: number) => ({ amount: amountKobo, currency: "NGN" });

function needUser(ctx: GraphqlContext) {
  if (!ctx.user) {
    throw new GraphQLError("Please log in first.", { extensions: { code: "login-required" } });
  }
  return ctx.user;
}

export const resolvers = {
  Query: {
    async menu(_: unknown, args: { first: number; after?: string; search?: string }, ctx: GraphqlContext) {
      const page = await ctx.services.menu.list({
        limit: Math.min(args.first, 50),
        cursor: args.after,
        search: args.search,
      });
      return {
        edges: page.items.map((dish) => ({ cursor: encodeCursor(dish.cursorKey), node: dish })),
        pageInfo: { hasNextPage: page.next !== null, endCursor: page.next ? encodeCursor(page.next) : null },
      };
    },
    dish: (_: unknown, { id }: { id: string }, ctx: GraphqlContext) => ctx.loaders.dish.load(id),
    me: (_: unknown, __: unknown, ctx: GraphqlContext) => (ctx.user ? ctx.services.users.profile(ctx.user) : null),
    order: (_: unknown, { id }: { id: string }, ctx: GraphqlContext) => ctx.services.orders.get(needUser(ctx), id),
  },

  Mutation: {
    async placeOrder(_: unknown, { input }: { input: { dishId: string; quantity: number; idempotencyKey: string } }, ctx: GraphqlContext) {
      const order = await ctx.services.orders.place(needUser(ctx), input.dishId, input.quantity, input.idempotencyKey);
      return { order };
    },
  },

  Dish: {
    price: (dish: Dish) => money(dish.priceKobo),
    portionsLeft: (dish: Dish, _: unknown, ctx: GraphqlContext) =>
      ctx.user && can(ctx.user, "menu:write") ? dish.portionsLeft : null,
  },

  Order: {
    dish: (order: Order, _: unknown, ctx: GraphqlContext) => ctx.loaders.dish.load(order.dishId),
    total: (order: Order) => money(order.totalKobo),
    status: (order: Order) => order.status.toUpperCase(),
  },

  User: {
    orders: (user: { id: string }, args: { first: number; after?: string }, ctx: GraphqlContext) =>
      ctx.services.orders.listMine(needUser(ctx), { limit: Math.min(args.first, 50), cursor: args.after }),
      // (turned into a connection the same way as menu; see the practice)
  },
};
```

Every resolver gets the same four arguments: the **parent** object (the `Order` when resolving `Order.dish`), the field's **arguments**, the **context**, and some info we won't need. Fields without a resolver just read the property of the same name from the parent, so `Dish.name` needs no code.

The thing to notice is what *isn't* here. No SQL. No permission rules. No "20 plates maximum". `placeOrder` calls `ctx.services.orders.place(actor, ...)`, the same function the REST route calls, so it gets the same rules (lesson 6), the same ownership checks (lesson 13), the same last-plate transaction (lesson 8), and the same idempotency constraint in the database (lesson 15). That's why lesson 6 put rules in the service, and why lesson 13 made services take the actor. **A second API on top of the same services is a few hundred lines. A second API with its own copy of the rules is a second set of bugs.**

Two GraphQL-shaped decisions:

1. **Field-level permissions.** `portionsLeft` exists in the type, but its resolver returns `null` unless the user is staff. In REST, lesson 13 did this in the presenter; here, the field's resolver is the presenter. (It's why the field isn't `Int!`.)
2. **Limits on lists.** `Math.min(args.first, 50)`. A client asking for `menu(first: 1000000)` gets 50. Every list argument in a GraphQL API needs a cap.

Idempotency arrives as a field of the input, `idempotencyKey`, instead of a header. GraphQL clients usually can't set per-mutation headers easily, and it puts the key in the schema where everyone can see it's required. Lesson 15's unique `(customer_id, idempotency_key)` constraint does the work: a retry returns the original order.

## Step 4: the N+1 problem, and DataLoader
<!-- bite: 925c10c3-577f-476b-ab85-c403d48e4366 -->

Look at this harmless-looking query:

```graphql
{ me { orders(first: 20) { edges { node { id dish { name } } } } } }
```

Without care: 1 query for the 20 orders, then `Order.dish` runs 20 times, and that's 20 queries for dishes, many of them the same dish (half of Mama's orders are jollof). 21 queries for one small screen. With 50 orders, 51. That's the **N+1 problem**, and every GraphQL API meets it on its first day.

DataLoader fixes it. During one tick of the event loop, it collects every `load(id)` call, then calls *your* batch function once with all the ids.

`src/graphql/loaders.ts`:

```ts
import DataLoader from "dataloader";
import type { Dish } from "../menu/menu.types.ts";
import type { MenuRepository } from "../menu/menu.types.ts";

export function createLoaders(repositories: { menu: MenuRepository }) {
  return {
    dish: new DataLoader<string, Dish | null>(async (ids) => {
      const dishes = await repositories.menu.findByIds([...ids]);
      const byId = new Map(dishes.map((dish) => [dish.id, dish]));
      return ids.map((id) => byId.get(id) ?? null);
    }),
  };
}

export type Loaders = ReturnType<typeof createLoaders>;
```

and `findByIds` is one query:

```sql
SELECT * FROM dishes WHERE id = ANY($1::bigint[])
```

Now those 20 orders cost **two** queries: one for the orders, one for all their dishes. And duplicate ids are loaded once: DataLoader also remembers what it already loaded *in this request*.

Two rules DataLoader is strict about:

1. **Return results in the same order as the ids**, with the same length. Postgres returns rows in any order, which is why we build `byId` and map over `ids`. Return them in the wrong order and Ada's order shows Bayo's dish.
2. **One set of loaders per request.** That memory of "already loaded" is a cache. Share loaders across requests and you'd serve one person's view to another, and keep stale dishes forever. Inside `context`, they're born and die with each request.

## Step 5: errors
<!-- bite: fd90ea31-8974-4bef-80f3-8355c418970b -->

GraphQL reports errors differently from REST. The HTTP status is usually **200**, and the body has `data` (what worked) and `errors` (what didn't), side by side:

```json
{
  "data": { "order": null },
  "errors": [
    {
      "message": "Order 99 was not found.",
      "path": ["order"],
      "extensions": { "code": "order-not-found", "kind": "not_found" }
    }
  ]
}
```

This is a feature: if `me` works and `order` fails, the screen still gets `me`. But it means clients must look at `errors`, not just the status.

Our services throw `AppError`s. By default Yoga **masks** every error it doesn't recognise as safe, replacing the message with "Unexpected error.", which is right: a crashed SQL query shouldn't send its text to the phone. We tell it which errors are safe to show.

`src/graphql/errors.ts`:

```ts
import { GraphQLError } from "graphql";
import { AppError } from "../shared/errors.ts";

export function maskError(error: unknown, message: string) {
  const original = error instanceof GraphQLError ? error.originalError : error;
  if (original instanceof AppError) {
    return new GraphQLError(original.message, {
      extensions: { code: original.code, kind: original.kind, details: original.details },
    });
  }
  if (error instanceof GraphQLError && !error.originalError) return error;   // validation errors from GraphQL itself
  return new GraphQLError(message);                                        // anything else: hidden
}
```

The same promise as lesson 7: business errors in plain words with a stable `code`; unexpected errors hidden from the client and logged in full on our side. The `code` values are the same ones REST uses, so the phone team handles `not-enough-portions` the same way in both.

## Step 6: protecting it from expensive queries
<!-- bite: 966fe413-6c20-415d-b4c4-0a3aec9c25a3 -->

In REST, each URL does a known amount of work. In GraphQL, the *client* writes the query, so the client chooses the work. A friendly client asks for one screen. A hostile one writes:

```graphql
{ menu(first: 50) { edges { node { name
    # imagine Dish had "orders", and Order had "dish"...
} } } }
```

nested ten levels deep, or the same field 500 times under different names (aliases). Each is one small HTTP request, and each can make the server do enormous work.

Defences, from simplest:

1. **Caps on every list** (step 3), so nothing returns a million items.
2. **A maximum depth**, say 6 levels.
3. **A maximum number of aliases** and of fields per query.
4. **A cost limit**: give each field a cost (a list costs more than a number) and refuse queries over a budget.
5. **Rate limiting by cost**, not just by request, for a public API.
6. **Persisted operations**: the phone app's queries are registered when the app is built, and the server only runs those. Nobody can send a new query at all. It's the strongest protection, for an API used only by your own apps.

Items 2 to 4 come ready-made in GraphQL Armor:

```bash
npm install @escape.tech/graphql-armor
```

```ts
import { EnvelopArmorPlugin } from "@escape.tech/graphql-armor";

createYoga({
  // ...
  plugins: [
    EnvelopArmorPlugin({
      maxDepth: { n: 6 },
      maxAliases: { n: 10 },
      costLimit: { maxCost: 3000 },
    }),
  ],
});
```

(Check the library's README for the current option names; they've changed between versions.)

Also: our `generalLimit` rate limit runs before `/graphql`, and the body is small by nature. And since we use Bearer tokens, not cookies, a malicious website can't make Ada's browser send a logged-in GraphQL request: the token isn't attached automatically. If you ever switch to cookies, turn on Yoga's CSRF protection.

## Step 7: GraphQL and the rest of the API
<!-- bite: 795ce2a3-7f6e-4e9d-bb2b-76b09f45b35b -->

**Versioning.** GraphQL APIs usually don't have v1 and v2. Because clients name every field they use, you can **add** freely (old clients don't ask for new fields), and for changes you mark the old field deprecated:

```graphql
type Dish {
  priceNaira: Int @deprecated(reason: "Use price, which is in kobo.")
  price: Money!
}
```

Tools and GraphiQL show the warning. Then you measure which clients still ask for `priceNaira` (lesson 27's logs can record the fields used), and remove it when nobody does. It's lesson 10's "add, don't change", built into the language.

**Docs.** The schema *is* the documentation, and clients can download it (that's **introspection**). Some teams turn introspection off in production so strangers can't map the API; it's a small speed bump, not real security, since the rules are enforced in the services anyway.

**Caching.** REST GETs cache well with HTTP (lesson 19's `ETag`, `Cache-Control`), because each URL is one resource. GraphQL queries are usually POSTs to one URL, so HTTP caching mostly doesn't apply. The Redis cache in the menu service still works for both, because it sits *below* the API layer. Another win for putting it there.

**Files, webhooks, streams.** Uploads, Paystack's webhooks, and the kitchen's SSE stay REST. GraphQL is good at one thing: letting clients read and write a graph of data flexibly.

## Step 8: when GraphQL beats REST
<!-- bite: 8e3f8103-440e-4e5b-a08b-9c7175705bf3 -->

| GraphQL wins when... | REST wins when... |
|---|---|
| Many different clients (phone, web, partner) need different slices of the same data | The API is simple and the same for everyone |
| Screens need nested data from many resources at once | Responses map neatly to resources |
| Network round trips are expensive (mobile, far away) | You want HTTP caching and CDNs to do the work |
| The frontend team wants to move without waiting for new endpoints | Public, third-party users who need simple, predictable URLs and limits |
| You can afford the protection work (cost limits, persisted queries) | You want the least to secure and monitor |

For Mama Put, both: REST stays the main public API, and GraphQL serves the phone app's screens. Because both are thin layers over the same services, keeping two costs very little.

## Step 9: testing
<!-- bite: 511ed8a6-c561-49bf-9a0b-3ee971c73c6d -->

GraphQL is just HTTP, so lesson 16's supertest works:

```ts
it("places an order through GraphQL with the same rules as REST", async () => {
  const { app, login } = await buildTestApp();
  const { token } = await login();
  const query = `mutation ($input: PlaceOrderInput!) { placeOrder(input: $input) { order { id total { amount } } } }`;

  const res = await request(app)
    .post("/graphql")
    .set("Authorization", `Bearer ${token}`)
    .send({ query, variables: { input: { dishId: "1", quantity: 21, idempotencyKey: "gql-test-0001" } } });

  assert.equal(res.status, 200);
  assert.equal(res.body.errors[0].extensions.code, "too-many-plates");
});
```

Also test: `portionsLeft` is `null` for a customer and a number for staff; `order` for someone else's order gives `order-not-found`; a query nested deeper than 6 is refused; and the N+1 fix, with a repository that counts calls, showing 20 orders' dishes load in **one** `findByIds`.

## The TypeScript in this lesson
<!-- bite: 1e34bf17-378d-4d18-b06e-fd92d4159b44 -->

1. **`createYoga<{ req: Request; res: Response }>(...)`**: The `<...>` tells Yoga what extra objects the server gives it on each request. Because we say Express's `req` and `res`, `context: ({ req }) => ...` knows `req.user` exists (lesson 12's declaration merging).
2. **`readFileSync(new URL("./schema.graphql", import.meta.url), "utf8")`**: Reads a file next to this one. `import.meta.url` is this file's own address, so the path works wherever you run the program from.
3. **`(_: unknown, args: {...}, ctx: GraphqlContext)`**: Resolver arguments. `_` is the usual name for a parameter you must accept but don't use (the parent, for top-level queries); `__` when there are two unused ones.
4. **`new DataLoader<string, Dish | null>(...)`**: The first type is the key (an id), the second is what each key loads. `load("1")` then returns `Promise<Dish | null>`.
5. **`[...ids]`**: DataLoader gives a read-only array. Spreading it into `[...]` makes an ordinary array, which our repository expects.
6. **`new Map(dishes.map((dish) => [dish.id, dish]))`**: Builds a map from an array of `[key, value]` pairs, for fast lookups by id.
7. **`byId.get(id) ?? null`**: A missing id gives `undefined` from the map; DataLoader wants `null` (or an error) for "not found".
8. **`error instanceof GraphQLError ? error.originalError : error`**: GraphQL wraps errors thrown by resolvers in a `GraphQLError`; `originalError` is the one we threw. `instanceof` checks the class and narrows the type.
9. **`order.status.toUpperCase()`**: Our status is `"pending"`; the GraphQL enum value is `PENDING`. (Yoga can also map enum values for you through an `OrderStatus` resolver object, `{ PENDING: "pending", ... }`. That's tidier for bigger enums.)
10. **`ReturnType<typeof createLoaders>`**: As always, the type comes from the factory, so adding a loader updates the type by itself.

## Your project so far
<!-- bite: 59f80036-e9c3-475d-97fb-a71d51bd3422 -->

```text
mama-put-api/
├── package.json                  ← NEW: graphql, graphql-yoga, dataloader, @escape.tech/graphql-armor
└── src/
    ├── app.ts                    ← /graphql mounted before express.json, with the rate limit and authenticate
    ├── graphql/
    │   ├── schema.graphql        ← NEW: Query, Mutation, Dish, Order, User, connections, inputs
    │   ├── yoga.ts               ← NEW: createGraphql: schema, context per request, GraphiQL outside production
    │   ├── context.ts            ← NEW: the GraphqlContext type: user, services, loaders
    │   ├── resolvers.ts          ← NEW: thin calls into the same services; field-level portionsLeft
    │   ├── loaders.ts            ← NEW: DataLoader for dishes, fresh per request
    │   ├── errors.ts             ← NEW: maskError: AppError codes shown, everything else hidden
    │   └── graphql.test.ts       ← NEW: same rules as REST, field permissions, depth limit, one batched query
    ├── menu/
    │   └── menu.pg-repository.ts ← NEW: findByIds with = ANY($1::bigint[])
    └── kitchen/ · jobs/ · payments/ · orders/ · auth/ · shared/ · webhooks/ · admin/ · docs/ · db/ · types/
```

## Common mistakes
<!-- bite: 12790b5e-87db-4dbb-a154-48c4e91cd04e -->

1. **Business rules in resolvers.** Then REST and GraphQL disagree. Resolvers call services; services hold the rules.
2. **No DataLoader.** Every list of N items costs N+1 queries.
3. **Loaders shared between requests.** One person's data, or stale data, served to another.
4. **Batch results in the wrong order.** DataLoader matches by position. Map back over the ids.
5. **No limits.** Unlimited `first`, unlimited depth, unlimited aliases: one request can take the server down.
6. **Showing raw errors.** A SQL error's text reaching the phone. Mask everything except your own `AppError`s.
7. **`!` everywhere.** One failing non-null field nulls its parent, and a whole screen goes blank.
8. **Checking only the HTTP status on the client.** GraphQL errors usually come with 200.
9. **Replacing REST with GraphQL for everything.** Webhooks, uploads and streams are better as plain HTTP.

## Check your understanding
<!-- bite: de2c9408-fbe4-477d-8f89-9b043ef685e6 -->

1. Why does `placeOrder` through GraphQL refuse 21 plates, even though no GraphQL code mentions 20?
2. A query asks for 30 orders and each order's dish. How many SQL queries run, with and without DataLoader?
3. Why are loaders created inside `context`, not once at start-up?
4. A customer asks for `portionsLeft`. What do they get, and why isn't the field `Int!`?
5. Why does a GraphQL API usually not need `/v1` and `/v2`?
6. Give one reason Mama Put keeps REST as its main public API.

<details>
<summary>Answers, after your attempt</summary>

1. The resolver calls `ordersService.place`, the same function as REST, and the rule lives there (lesson 6). Any API built on the service gets every rule for free.
2. Without: 1 for the orders plus 30 for the dishes, 31 in all. With DataLoader: 2, one for the orders and one `findByIds` for all their dishes, with duplicate dishes loaded once.
3. Each loader remembers what it loaded. Made once and shared, it would keep stale dishes forever and could hand one user's view of data to another. Made per request, its memory lasts exactly one request.
4. `null`. The resolver only returns the number for staff. The field must be nullable (`Int`, not `Int!`) so `null` is a legal answer; with `Int!`, GraphQL would treat the `null` as an error.
5. Clients name every field they use, so adding fields never breaks anyone, and old fields can be marked `@deprecated` and removed once nobody asks for them.
6. Any of: HTTP caching and CDNs work naturally with REST GETs; it's simpler for outside developers; each URL has a known cost, which is easier to rate-limit and secure; webhooks, uploads and streams are plain HTTP anyway.

</details>

## Practice
<!-- bite: fcb00f28-894c-42cd-94eb-1fef48b84397 -->

1. Turn `User.orders` into a proper `OrderConnection`, like `menu`. Pull the "page into a connection" code into one helper used by both.
2. Map the `OrderStatus` enum with a resolver object instead of `toUpperCase()`.
3. Add a `startPayment(orderId: ID!): Checkout!` mutation (with `reference` and `checkoutUrl`), calling lesson 17's `paymentsService.startCheckout`.
4. Add a log line per GraphQL operation with its name (`OrderScreen`) and how long it took, ready for lesson 27.
5. Write the tests from step 9, including the counting repository for the N+1 test.

**Done when** the phone team's `OrderScreen` query returns everything in one request, a 20-order query runs exactly two SQL queries, `portionsLeft` is `null` for customers, every error `code` matches its REST twin, and a 7-deep query is refused before any resolver runs.

## Before moving on
<!-- bite: d6aad275-d884-4a83-8d54-8f4004633c63 -->

Mama Put API now speaks two languages to the outside world: REST for everyone, GraphQL for the phone app, both on the same services, so the rules can't drift apart.

Both are made for clients far away: phones, browsers, partners. But soon a different kind of client arrives: **our own services**. In Part 6 we split out a notifications service, and it will need to ask the main API things like "what's dish 1 called?" thousands of times a day. For that, JSON over HTTP is slow and loose. Services talking to services want a strict contract, small binary messages, and built-in deadlines. That's gRPC, next.

## Related
<!-- bite: 362c83ce-383e-4d11-9c52-4b2f7afe664e -->

- [[backend/frameworks/express/22-grpc|Next: gRPC]]
- [[backend/frameworks/express/09-listing|Pagination, Filtering, Searching, Sorting and Field Selection]] — the REST answer to "only the fields I need"
- [[backend/frameworks/express/10-versioning|Versioning]] — "add, don't change", which GraphQL builds in
- [[backend/02-api-design/index|API Design]] — REST, GraphQL and gRPC side by side

## About this lesson
<!-- bite: 1444458d-1b6c-4604-b26f-877fd4cbdd92 -->

**Level:** Intermediate → Advanced. Lesson 21 of [[backend/frameworks/express/index|Express]]. Covers the GraphQL schema language (types, nullability, enums, inputs, payload types, connections), GraphQL Yoga mounted in Express with optional authentication and per-request context, resolvers as thin calls into the same services so rules and permissions can't drift, field-level permissions, caps on list sizes, idempotency keys as input fields, the N+1 problem and per-request DataLoaders with ordered batch results, partial results and error masking with stable codes, depth, alias and cost limits with GraphQL Armor and persisted operations, deprecation instead of versions, introspection, why HTTP caching mostly doesn't apply, when GraphQL beats REST, and testing GraphQL with supertest.
