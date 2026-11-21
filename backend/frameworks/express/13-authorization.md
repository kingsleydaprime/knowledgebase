---
id: ae6e523a-df4b-40c5-8433-b0aca9960551
---

# Authorization

**Authorization is deciding what a logged-in person is allowed to do: which routes they may call, and which particular things they may see or change.** Authentication asked "who are you?"; authorization asks "and are *you* allowed to do *this*?". In a shared document, it's the difference between "you're logged in to Google" and "you can view this doc but not edit it".

## Before you start
<!-- bite: 7eb09701-9762-4f27-bd81-b38d9b9aa647 -->

You should have accounts, access tokens and `req.user` from [[backend/frameworks/express/12-authentication|lesson 12]], including its practice task that gave the kitchen a `"staff"` role.

After this lesson you will be able to:

1. Describe who may do what as a small set of roles and rules, written in one place.
2. Check permission at two levels: "may this person call this route?" and "may this person touch *this particular* order?".
3. Make it hard to forget a check, by making services demand to know who's asking.
4. Choose between 401, 403 and 404 for a refusal, and know why the choice matters.

## Where we stopped
<!-- bite: 56ebd58a-5652-4526-a39f-cd09d2e2c29b -->

Lesson 12 ended with two holes:

1. **Ada can read Bayo's order.** She's logged in, so `GET /v2/orders/7` works for her, even though order 7 is Bayo's.
2. **Every staff member can do everything.** The cook who started yesterday can delete the whole menu, or (once we add it) make himself an admin.

The first hole has a famous name. When an API checks that you're logged in, but not that the *thing* you asked for is yours, attackers just change the id in the URL and walk through everyone's data. It's called **broken object level authorization**, and it's the number one risk on OWASP's list of API security risks. Real companies have leaked millions of records this way, by counting `/orders/1`, `/orders/2`, `/orders/3`.

## The kid version
<!-- bite: e003b0c3-f721-4541-a54b-f793dfa585b4 -->

At Mama Put, everyone who comes in has a wristband now (lesson 12). But wristbands have colours:

1. **Green** for customers. You can order food and ask about **your own** order.
2. **Blue** for kitchen staff. You can see every order, mark them ready, and change the menu.
3. **Gold** for Mama herself. Everything, including giving people blue wristbands.

When Ada (green) asks "where's order 7?", the helper doesn't just check she has *a* wristband. She checks the colour, and then checks that order 7 is Ada's. If it's Bayo's, she says "I don't know any order 7", so Ada doesn't even learn it exists.

**Where the picture stops working.** A helper might forget to check once, on a busy day. In code we make forgetting hard, by building the check into the only way to reach the data.

## Terms used in authorization
<!-- bite: f79a8ddb-597b-4ad0-8484-a6fca81ddbab -->

1. **Role**: This is a named group of permissions, like `customer`, `staff` or `admin`. Each user has one.
2. **Permission**: This is also called an **action**. It's one thing someone may do, written like `order:read` or `menu:write`.
3. **Role-based access control**: This is also called **RBAC**. It means deciding permissions by role: "staff may write the menu".
4. **Ownership check**: This is deciding by the thing itself: "a customer may read an order *if it's theirs*". Rules that look at the thing, not just the role, are sometimes called **attribute-based**.
5. **Policy**: This is the written-down set of rules: who may do what, under which conditions. Ours is one file.
6. **Actor**: This is the person (or program) doing something. Services will take the actor as their first argument.
7. **Default deny**: This is the rule that anything not explicitly allowed is refused.

## Step 1: write the policy down, in one place
<!-- bite: 1d2dd119-f7bc-4834-abe1-e05dc33d3af9 -->

Before code, write the table. This is the conversation to have with Mama, not with the compiler:

| Action | customer | staff | admin |
|---|---|---|---|
| read the menu | yes (even logged out) | yes | yes |
| `menu:write` (add, change, remove dishes) | no | yes | yes |
| `order:place` | yes | yes | yes |
| `order:read` one order | **only their own** | yes | yes |
| `order:list` | **only their own** | all | all |
| `order:update-status` | no | yes | yes |
| `user:change-role` | no | no | yes |

Then turn the table into code, exactly. `src/auth/policy.ts`:

```ts
import type { AuthUser } from "./auth.types.ts";

export type Action =
  | "menu:write"
  | "order:place"
  | "order:read"
  | "order:list"
  | "order:list-all"
  | "order:update-status"
  | "user:change-role";

type Resource = { customerId?: string | null };
type Rule = (actor: AuthUser, resource?: Resource) => boolean;

const isStaff = (actor: AuthUser) => actor.role === "staff" || actor.role === "admin";
const owns = (actor: AuthUser, resource?: Resource) =>
  resource?.customerId != null && resource.customerId === actor.id;

const RULES: Record<Action, Rule> = {
  "menu:write": isStaff,
  "order:place": () => true,
  "order:read": (actor, order) => isStaff(actor) || owns(actor, order),
  "order:list": () => true,
  "order:list-all": isStaff,
  "order:update-status": isStaff,
  "user:change-role": (actor) => actor.role === "admin",
};

export function can(actor: AuthUser, action: Action, resource?: Resource): boolean {
  return RULES[action](actor, resource);
}
```

Three things make this good:

1. **It's the table.** Mama could read `RULES` and check it against what she said. When she changes her mind, one line changes.
2. **`Record<Action, Rule>` means every action must have a rule.** Add a new action to the `Action` type and forget its rule, and TypeScript refuses to compile. You can't accidentally leave an action unguarded.
3. **`owns` is careful about `null`.** Orders placed before lesson 12 have no `customerId`. No real user has an empty id today, so comparing would *probably* be fine. But a permission rule should never rest on "that can't happen". If the order has no owner, `owns` says no, out loud.

## Step 2: route-level checks, as middleware
<!-- bite: 99f0aea9-040b-4b00-a9c7-ae5734195b95 -->

Some checks only need the role: "may this person write the menu at all?". Those fit naturally as middleware, before the route runs:

```ts
// src/auth/require-permission.ts
import type { Request, Response, NextFunction } from "express";
import { can } from "./policy.ts";
import type { Action } from "./policy.ts";
import { AppError } from "../shared/errors.ts";

export function requirePermission(action: Action) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) throw new AppError("unauthenticated", "login-required", "Please log in first.");
    if (!can(req.user, action)) {
      throw new AppError("forbidden", "not-allowed", "You don't have permission to do this.");
    }
    next();
  };
}
```

And `kitchenOnly`, the staff key from lesson 3, is finally deleted:

```ts
router.post("/", requirePermission("menu:write"), async (req, res) => { ... });
router.patch("/:id", requirePermission("menu:write"), async (req, res) => { ... });
router.delete("/:id", requirePermission("menu:write"), async (req, res) => { ... });
```

Read the route and the permission is right there. Anyone reviewing the code can see what protects it.

## Step 3: object-level checks, in the service
<!-- bite: 41847419-a2da-4ba6-b341-8daa953d34eb -->

Now the harder hole: Ada and order 7. A middleware can't check it, because it runs *before* the order is loaded. It only knows the id in the URL, not whose order that is.

So the check goes where the order is loaded: the service. And here's the trick that makes it hard to forget: **every service method that touches protected data takes the actor as its first argument.**

```ts
// src/orders/orders.service.ts
import type { AuthUser } from "../auth/auth.types.ts";
import { can } from "../auth/policy.ts";
import { AppError, notFound, ruleBroken } from "../shared/errors.ts";

export function createOrdersService(deps: { ordersRepository: OrdersRepository; menuService: MenuService }) {
  const { ordersRepository, menuService } = deps;

  return {
    async get(actor: AuthUser, id: string): Promise<Order> {
      const order = await ordersRepository.findById(id);
      if (!order || !can(actor, "order:read", order)) throw notFound("Order", id);
      return order;
    },

    async list(actor: AuthUser, options: ListOrdersOptions) {
      const scope = can(actor, "order:list-all") ? {} : { customerId: actor.id };
      return ordersRepository.listOldestFirst({ ...options, ...scope });
    },

    async updateStatus(actor: AuthUser, id: string, status: OrderStatus) {
      if (!can(actor, "order:update-status")) {
        throw new AppError("forbidden", "not-allowed", "Only kitchen staff can change an order's status.");
      }
      const order = await ordersRepository.updateStatus(id, status);
      if (!order) throw conflict("bad-status-change", "That status change isn't allowed.");
      return order;
    },

    async place(actor: AuthUser, dishId: string, quantity: number): Promise<Order> {
      // ...the rules from lessons 7 and 8, with customerId: actor.id
    },
  };
}
```

Look at what this buys:

1. **You can't call `ordersService.get(id)` any more.** TypeScript requires `get(actor, id)`. Every caller, today's REST route, the GraphQL API in lesson 21, a background job, has to say *who* is asking, and the check runs every time. You can forget to write `requirePermission` on a route; you can't forget an argument the compiler demands.
2. **Lists are scoped, not filtered afterwards.** A customer's list adds `customerId = actor.id` to the **database query** (`listOldestFirst` gains an optional `customerId` filter, using the same `add()` pattern from lesson 9). We never load everyone's orders and then throw some away. A list that's filtered in JavaScript is one bug away from leaking.
3. **Ada gets 404 for Bayo's order, not 403.** More on that in a moment.

The route just passes `req.user` along:

```ts
router.get("/:id", requireUser, async (req, res) => {
  const { id } = validate(OrderIdSchema, req.params, "params");
  res.json({ data: await ordersService.get(req.user!, id) });
});

router.get("/", requireUser, async (req, res) => {
  const query = validate(ListOrdersQuerySchema, req.query, "query");
  const page = await ordersService.list(req.user!, { ...query, after: query.cursor ? decodeCursor(query.cursor) : undefined });
  res.json({ data: page.items, meta: { limit: query.limit, nextCursor: page.next ? encodeCursor(page.next) : null } });
});
```

The same `GET /orders` route now serves two people. The kitchen screen gets every pending order; Ada's phone gets Ada's orders. One route, one policy, scoped in the database.

## Step 4: 401, 403 or 404?
<!-- bite: f0082d06-c3f3-4d23-967a-3c92e7444fc6 -->

Three different "no"s, and clients treat them differently:

1. **401 Unauthorized**: "I don't know who you are." No token, or a bad one. The app should send the user to log in.
2. **403 Forbidden**: "I know who you are, and you're not allowed." A customer trying to change the menu. The app should say "you can't do that", not ask them to log in again.
3. **404 Not Found**: "There's no such thing, as far as you're concerned."

For Ada and Bayo's order, we use **404**, on purpose. A 403 would say "order 7 exists, but it's not yours", which tells Ada that order 7 is real, and lets an attacker count how many orders Mama Put gets a day by probing ids. A 404 tells her nothing she didn't know.

The rule of thumb: **if the person shouldn't even know the thing exists, answer 404. If the existence isn't secret, but the action is not allowed, answer 403.** The menu is public, so a customer trying to delete a dish gets 403. Orders are private, so other people's orders are 404.

(Ids that count up, 1, 2, 3, make probing easy even with 404s. Many APIs use random ids, like UUIDs, for private things, so there's nothing to count. That's defence in depth: the policy is what keeps Ada out; random ids just give attackers less to work with.)

## Step 5: changing roles, safely
<!-- bite: e5602420-f73a-44f0-91c5-ed729a416dc5 -->

Mama needs to make new cooks into staff without touching `psql`. Add an admin route:

```ts
// src/admin/admin.routes.ts
router.patch("/users/:id/role", requirePermission("user:change-role"), async (req, res) => {
  const { id } = validate(UserIdSchema, req.params, "params");
  const { role } = validate(z.object({ role: z.enum(["customer", "staff", "admin"]) }), req.body, "body");
  res.json({ data: await adminService.changeRole(req.user!, id, role) });
});
```

And in `adminService.changeRole`:

```ts
async changeRole(actor: AuthUser, userId: string, role: Role) {
  if (!can(actor, "user:change-role")) throw new AppError("forbidden", "not-allowed", "Only an admin can change roles.");
  if (userId === actor.id && role !== "admin") {
    throw ruleBroken("cannot-demote-self", "You can't remove your own admin role. Ask another admin.");
  }
  const user = await users.updateRole(userId, role);
  if (!user) throw notFound("User", userId);
  await refreshTokens.revokeAllForUser(userId);
  console.info({ event: "role-changed", by: actor.id, user: userId, role });
  return user;
}
```

Three details that matter:

1. **The role is inside the access token**, from lesson 12. So after Mama demotes a cook, his *current* token still says `staff` for up to 15 minutes. Revoking his refresh tokens means that when it expires, he can't get a new one with the old role; he has to log in again and gets a token with his new role. If even 15 minutes is too long for your business, check the role from the database on dangerous actions. Short tokens are a trade between speed and how quickly changes take effect.
2. **An admin can't demote themselves**, so Mama Put can never end up with zero admins by accident.
3. **Role changes are logged**, with who did it. Who changed permissions, and when, is exactly what you need to know after something goes wrong. In [[backend/frameworks/express/27-observability|lesson 27]] it becomes a proper audit log.

How does the first admin get made? Once, by hand: `UPDATE users SET role = 'admin' WHERE email = 'mama@example.com'`, or a one-off script. Never a route that anyone can call "if there are no admins yet". That route will be found.

## Step 6: what each role sees
<!-- bite: e039d25a-f3f3-4804-84e8-427122d1fd06 -->

Authorization can also decide *which fields* someone sees. Customers don't need `portionsLeft` (Mama would rather they didn't know the pot is nearly empty; it makes people rush), but the kitchen does.

The presenter from lesson 10 takes the viewer into account:

```ts
presentDish: (dish, viewer?: AuthUser) => ({
  id: dish.id,
  name: dish.name,
  price: { amount: dish.priceKobo, currency: "NGN" },
  available: dish.available,
  ...(viewer && can(viewer, "menu:write") ? { portionsLeft: dish.portionsLeft } : {}),
}),
```

Same route, same data, different view. It's the policy again, deciding at the edge what each actor may see.

## The TypeScript in this lesson
<!-- bite: e12fed12-1257-40ff-8212-227ef0885235 -->

1. **`type Rule = (actor: AuthUser, resource?: Resource) => boolean`**: A type that describes a *function*: it takes an actor and maybe a resource, and gives back true or false. Every rule in the policy has this shape.
2. **`Record<Action, Rule>`**: An object with exactly one rule for every action. Missing one is a compile error. This is how the policy can't have gaps.
3. **`RULES[action](actor, resource)`**: Look up the rule for this action, then call it. Square brackets read a field whose name is in a variable.
4. **`resource?.customerId != null`**: `!=` (with one `=`) is the one place we use loose comparison on purpose: `x != null` is true when `x` is neither `null` nor `undefined`. It's a common, safe idiom for "has a value".
5. **`const owns = (actor, resource?) => ...`** and **`"order:place": () => true`**: Rules are plain functions. A rule that ignores its arguments and returns `true` means "everyone may".
6. **`async get(actor: AuthUser, id: string)`**: Making `actor` a required first parameter is the whole "can't forget" design. TypeScript won't let anyone call `get` without it.
7. **`{ ...options, ...scope }`**: Spread both objects into one. If `scope` is `{ customerId: "1" }`, the result is the options plus that filter. If `scope` is `{}`, the options are unchanged.
8. **`...(condition ? { portionsLeft: ... } : {})`**: Spread an object that is either one field or nothing. It's a neat way to include a field only sometimes.
9. **`req.user!`**: The non-null assertion from lesson 12, safe because `requireUser` or `requirePermission` already ran.

## Your project so far
<!-- bite: 4498343a-2d39-4cca-bedf-1808f79ab35d -->

```text
mama-put-api/
├── .env · .env.example · .gitignore · package.json · tsconfig.json
├── migrations/   001 … 008
├── openapi/      v1.json · v2.json (403s and 404s documented per route)
└── src/
    ├── server.ts · app.ts
    ├── api.ts                    ← mounts /admin too
    ├── types/express.d.ts
    ├── auth/
    │   ├── policy.ts             ← NEW: Action, RULES (the table), can()
    │   ├── require-permission.ts ← NEW: route-level checks
    │   └── auth.types.ts · auth.schemas.ts · auth.repositories.ts · users.pg-repository.ts
    │       refresh-tokens.pg-repository.ts · password.ts · tokens.ts · refresh-tokens.ts
    │       auth.service.ts · authenticate.ts · auth.routes.ts
    ├── admin/
    │   ├── admin.service.ts      ← NEW: changeRole (no self-demotion, revokes tokens, logs)
    │   └── admin.routes.ts       ← NEW: PATCH /admin/users/:id/role
    ├── menu/
    │   ├── menu.routes.ts        ← requirePermission("menu:write") replaces kitchenOnly
    │   └── menu.versions.ts      ← presenters take the viewer; portionsLeft for staff only
    ├── orders/
    │   ├── orders.service.ts     ← every method takes the actor; lists scoped; others' orders are 404
    │   ├── orders.pg-repository.ts ← listOldestFirst accepts a customerId filter
    │   └── orders.routes.ts      ← passes req.user to the service
    ├── docs/  db/
    └── shared/                   ← kitchen-only.ts DELETED
```

## Common mistakes
<!-- bite: 17575528-8d53-4cc0-8a1e-cba1d993d798 -->

1. **Checking login but not ownership.** The number one API security bug. If a route takes an id, ask "whose is it?".
2. **Checks scattered through route files.** Write the policy once, and have routes and services ask it.
3. **Filtering lists in JavaScript.** Scope the query. Don't load other people's data at all.
4. **403 for private things.** It confirms they exist. Use 404 when existence is secret.
5. **Trusting the role from the request body.** `{"role": "admin"}` in a signup body must be ignored (zod stripping does this). Roles come only from your database.
6. **A "make me admin if none exists" route.** Bootstrap the first admin by hand.
7. **Forgetting tokens carry old roles.** After a role change, revoke refresh tokens, and know how long access tokens live.

## Check your understanding
<!-- bite: 1290207a-9e47-4e05-851d-9c81e8ff8e63 -->

1. Why can't a middleware stop Ada from reading Bayo's order?
2. What stops a future developer from adding a GraphQL query that returns any order without a check?
3. A customer calls `DELETE /v2/menu/1`. What status, and why not 404?
4. Mama demotes Tunde from staff to customer at 2:00 pm. Until when can he still change the menu, and how could you make that "never"?

<details>
<summary>Answers, after your attempt</summary>

1. The middleware runs before the order is loaded. It only sees the id `7`, not whose order that is. The check needs the order's `customerId`, so it belongs where the order is loaded: the service.
2. `ordersService.get` requires the actor, and runs the policy inside. The GraphQL code has to call the service (it can't reach the repository directly, by the lesson 4 rule), so it has to pass an actor, and the check runs.
3. 403. The menu is public, so the dish's existence isn't a secret; what's not allowed is the action. 404 is for things the person shouldn't know exist.
4. Until his current access token expires, at most about 2:15 pm. His refresh tokens were revoked, so he can't get another staff token. To make it immediate, check the role from the database for menu writes instead of trusting the token, or keep a list of revoked token ids for the rest of their 15 minutes.

</details>

## Practice
<!-- bite: 156c94b9-7e81-48d5-87e9-fe32ae9b94f3 -->

1. Add `order:cancel`: a customer may cancel **their own** order while it's still `pending`; staff may cancel any pending order. Write the rule in `RULES`, the method in the service, and `POST /orders/:id/cancel`. Cancelling should give the portions back, in a transaction.
2. Write a test (with the in-memory repositories) that Ada gets `notFound` for Bayo's order and her own order works. Write another that Ada's `list` never contains anyone else's order.
3. Show `customerId` only to staff in order responses, through an order presenter like the dish one.

**Done when** Ada can cancel her own pending order and gets 404 for Bayo's, a cancelled order's portions are back on the menu, a customer cancelling a ready order gets 422, and both tests pass.

## Before moving on
<!-- bite: 81ccf22b-ee20-43d5-b994-acdac9d4dc93 -->

Mama Put API now decides what everyone may do: a written policy, role checks on routes, ownership checks in services that can't be skipped, lists scoped in the database, and refusals that leak nothing.

But all of that assumes requests come from our own app, politely, one at a time. Out on the internet, nobody is polite. Someone will try 10,000 passwords against Ada's account. A browser page on another website will try to call our API with a customer's credentials. Someone will upload a "photo" of jollof that's actually a program. That's the security lesson, next.

## Related
<!-- bite: 1c842e75-3982-448f-bbfe-3b036d796819 -->

- [[backend/frameworks/express/14-security|Next: Security]]
- [[backend/05-auth/02-authorization|Authorization]] — the idea in any framework
- [[cybersecurity/index|Cybersecurity]] — the OWASP lists and the attacks behind them

## About this lesson
<!-- bite: 4cb313d4-a48d-413f-a622-3215ad3e3dca -->

**Level:** Intermediate → Advanced. Lesson 13 of [[backend/frameworks/express/index|Express]]. Covers roles and permissions, a policy written once as a typed table, route-level checks with `requirePermission`, object-level checks in services that require the actor, scoping lists in the database, broken object level authorization, choosing 401, 403 or 404, safe role changes (revocation, no self-demotion, logging, bootstrapping the first admin), and role-aware presenters.
