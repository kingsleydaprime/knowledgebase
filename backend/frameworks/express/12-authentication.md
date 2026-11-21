---
id: 73b7dfa1-7c7c-45ed-aeb2-c50d1c436dea
---

# Authentication

**Authentication is how your backend finds out *who* is making a request: the customer proves who they are once, by logging in, and from then on every request carries proof that it comes from them.** Every app you've ever logged into does this. You type your email and password once, and after that the app just *knows* it's you, on every screen, for days, until you log out or it asks you to log in again.

## Before you start
<!-- bite: b53e0406-f01b-49ed-95b7-d6caed5b8e68 -->

You should have the documented v1 and v2 API from [[backend/frameworks/express/11-api-docs|lesson 11]], on Postgres.

After this lesson you will be able to:

1. Store passwords safely, so even a stolen database doesn't give away anyone's password.
2. Explain sessions and tokens, and choose between them.
3. Build sign-up, log-in, refresh and log-out with short-lived access tokens and rotating refresh tokens.
4. Put the logged-in user on `req.user`, properly typed, and require a login on the routes that need one.

## Where we stopped
<!-- bite: 29589ed5-dc6c-4fbc-be58-83c499cccdc6 -->

Lesson 11 ended by looking at our only "security": `X-Staff-Key: jollof123`.

1. It's **one shared secret**. Every cook knows it. When a cook leaves, every other cook needs a new key.
2. It **never expires**. Anyone who sees it once, in a log or over a shoulder, has it forever.
3. **Customers have no accounts.** Anyone can place an order, and nothing records whose order it is.

From this lesson, every order belongs to a customer, and the API knows which customer is calling. (Who is *allowed* to do what, like "only staff can change the menu" and "you can only see your own orders", is the next lesson, authorization. Here we first need to know who's who.)

## The kid version
<!-- bite: 01e37774-e7b9-44b7-bb0d-3af5ec9e5ac1 -->

When you first join Mama Put's regulars, you show your face and give your name (signing up). She writes you in her book. Next time, you show your face again and she checks the book (logging in).

But showing your face for every single plate would be slow. So once she recognises you, she gives you a **wristband** for the day. Every time you order, you just show the wristband. It's only good until evening (it **expires**), so if you lose it, nobody can use it for long.

At the end of the day, you can trade your wristband for a fresh one without showing your face again, as long as you also hand in a special **token card** she gave you. Each card can only be traded once.

The wristband is an **access token**. The card is a **refresh token**.

**Where the picture stops working.** Mama can see if someone else is wearing your wristband. A server can't: whoever holds a valid token *is* you, as far as the server knows. That's why tokens expire quickly and must be kept secret.

## Terms used in authentication
<!-- bite: 9dd93f3e-424b-4193-b613-aeafef28342a -->

1. **Authentication**: This is also written **authn**. It's proving who you are. Logging in is authentication.
2. **Authorization**: This is also written **authz**. It's deciding what you're allowed to do, once we know who you are. That's lesson 13.
3. **Credential**: This is the thing you prove yourself with. Here, an email and a password.
4. **Password hash**: This is a scrambled version of a password, made by a one-way function. You can check a password against it, but you can't turn it back into the password. We store hashes, **never** passwords.
5. **Session**: This is a record the *server* keeps saying "this browser belongs to Ada", with a random session ID that the browser sends back, usually in a cookie.
6. **Token**: This is a piece of text the *client* keeps and sends with every request, usually in the `Authorization: Bearer <token>` header.
7. **JWT**: This stands for **JSON Web Token**. It's a token that carries information (like "user 42, role customer, expires at 3pm") plus a signature, so the server can check it wasn't changed without looking anything up.
8. **Access token**: This is a short-lived token (ours lasts 15 minutes) sent with every request.
9. **Refresh token**: This is a long-lived, single-use token used only to get a new access token, so the customer doesn't have to log in every 15 minutes.

## Step 1: never store passwords
<!-- bite: 51269502-769a-454b-91cd-2573dc99067e -->

Here's the rule everything else rests on: **if your database is stolen, nobody's password should come with it.** People reuse passwords. If Ada's Mama Put password is also her email password, a leak from us empties her bank account.

So we store a **hash**. And not just any hash: a *slow* one designed for passwords. Fast hashes like SHA-256 are built to run billions of times a second, which is exactly what an attacker guessing passwords wants. Password hashes like **argon2** are deliberately slow and memory-hungry, so each guess costs real time and real memory, and they add a random **salt** to each hash, so two people with the same password get different hashes.

```bash
npm install argon2 jose
```

`src/auth/password.ts`:

```ts
import argon2 from "argon2";

export type PasswordHasher = {
  hash(password: string): Promise<string>;
  verify(hash: string, password: string): Promise<boolean>;
};

export const argon2Hasher: PasswordHasher = {
  hash: (password) => argon2.hash(password, { type: argon2.argon2id }),
  verify: (hash, password) => argon2.verify(hash, password),
};
```

Try it in a scratch file:

```ts
import { argon2Hasher } from "./src/auth/password.ts";

const hash = await argon2Hasher.hash("jollof-is-life");
console.log(hash);
// $argon2id$v=19$m=65536,t=3,p=4$<random salt>$<hash>

console.log(await argon2Hasher.verify(hash, "jollof-is-life"));  // true
console.log(await argon2Hasher.verify(hash, "jollof-is-lyf"));   // false
```

Run the first line twice. Predict: are the two hashes the same? They're different every time, because the salt is random. Yet `verify` works for both, because the salt and the settings are stored *inside* the hash text (`m=65536,t=3,p=4` means 64 MB of memory, 3 passes, 4 lanes). That's also why a hasher is a dependency: in tests we can pass a fast fake.

## Step 2: sessions or tokens?
<!-- bite: 5e8dd4af-7783-40b9-a0ee-3bc99a2f9643 -->

Once Ada has logged in, how does the next request prove it's her? Two main ways:

**Sessions.** The server creates a record ("session `a8f3...` belongs to user 42"), stores it (in Postgres or Redis), and gives the browser the random ID in a cookie. Every request sends the cookie, and the server looks the session up.

1. Easy to end: delete the record and that login is over, immediately.
2. Needs a lookup on every request.
3. Fits websites best, because browsers send cookies automatically.

**Tokens (JWTs).** The server signs a small message ("user 42, customer, expires 15:00") and gives it to the client. Every request sends it in a header. The server checks the signature, with no lookup.

1. No lookup per request, and any service with the key can check it, which matters when we add a second service in lesson 25.
2. Fits phone apps and other programs best.
3. Hard to end early: a signed token stays valid until it expires, even if you change your mind.

Mama Put's main client is a **phone app**, and we'll soon have more than one service. So we use tokens, and we fix their weakness by making them **short-lived**: an access token lasts 15 minutes. To avoid logging in every 15 minutes, the app also gets a **refresh token** that we *do* store, so we can cancel it. That pair (short JWT plus stored, cancellable refresh token) gives most of the benefits of both.

(If you were building a website only, sessions with an `httpOnly` cookie are often the simpler, better choice. The `express-session` package does them. Neither choice is wrong. Choose for your clients.)

## Step 3: the tables
<!-- bite: 43e445cd-4969-408a-acba-63336b946204 -->

`migrations/006_create_users.sql`:

```sql
CREATE TABLE users (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email         text NOT NULL,
  name          text NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
  password_hash text NOT NULL,
  role          text NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'staff', 'admin')),
  created_at    timestamptz(3) NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX users_email_idx ON users (lower(email));
```

The unique index is on `lower(email)`, so `Ada@Example.com` and `ada@example.com` can't be two accounts.

`migrations/007_create_refresh_tokens.sql`:

```sql
CREATE TABLE refresh_tokens (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  token_hash  text NOT NULL UNIQUE,
  expires_at  timestamptz NOT NULL,
  used_at     timestamptz,
  revoked_at  timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now()
);
```

`migrations/008_orders_belong_to_customers.sql`:

```sql
ALTER TABLE orders ADD COLUMN customer_id bigint REFERENCES users (id);
CREATE INDEX orders_customer_id_idx ON orders (customer_id);
```

`customer_id` can be empty because the orders placed before this lesson have no customer. Every new order will have one.

Notice `refresh_tokens` stores a **hash** of the token too, not the token. If the table leaks, the tokens in it are useless.

## Step 4: signing and checking access tokens
<!-- bite: 8b2a6905-5d55-4dd5-b443-80a2e7b6e5f1 -->

`src/auth/auth.types.ts`:

```ts
export type Role = "customer" | "staff" | "admin";
export type AuthUser = { id: string; role: Role };
```

`src/auth/tokens.ts`:

```ts
import { SignJWT, jwtVerify } from "jose";
import { z } from "zod";
import type { AuthUser } from "./auth.types.ts";

const ISSUER = "mama-put-api";
const AUDIENCE = "mama-put-app";

const ClaimsSchema = z.object({
  sub: z.string().regex(/^\d+$/),
  role: z.enum(["customer", "staff", "admin"]),
});

export function createAccessTokens(secret: string) {
  const key = new TextEncoder().encode(secret);

  return {
    sign(user: AuthUser) {
      return new SignJWT({ role: user.role })
        .setProtectedHeader({ alg: "HS256" })
        .setSubject(user.id)
        .setIssuer(ISSUER)
        .setAudience(AUDIENCE)
        .setIssuedAt()
        .setExpirationTime("15m")
        .sign(key);
    },

    async verify(token: string): Promise<AuthUser> {
      const { payload } = await jwtVerify(token, key, {
        issuer: ISSUER,
        audience: AUDIENCE,
        algorithms: ["HS256"],
      });
      const claims = ClaimsSchema.parse(payload);
      return { id: claims.sub, role: claims.role };
    },
  };
}

export type AccessTokens = ReturnType<typeof createAccessTokens>;
```

A JWT is three pieces of base64url joined by dots: a **header** (`{"alg":"HS256"}`), a **payload** (`{"sub":"42","role":"customer","exp":...}`) and a **signature**. The signature is made from the first two plus our secret key. Change one letter of the payload (`"role":"admin"`) and the signature no longer matches, so `jwtVerify` refuses it.

Paste a token into a JWT decoder website and you'll see the payload in plain text. **A JWT is signed, not encrypted.** Never put anything secret in it. A user id and a role are fine.

Each option in `jwtVerify` closes a real hole:

1. **`algorithms: ["HS256"]`**: only accept the one algorithm we use. Some old libraries accepted a token that said `"alg": "none"` and skipped the check entirely.
2. **`issuer` and `audience`**: only accept tokens *we* made *for this app*. When there's a second service with its own tokens, this stops one service's tokens working at another.
3. **Expiry**: `jwtVerify` checks `exp` automatically. A token from yesterday is refused.

And then we still run the payload through zod. The signature proves *we* made it; zod proves it has the shape our code expects.

The secret goes in `.env`. Make a long random one:

```bash
node -e "console.log(require('node:crypto').randomBytes(32).toString('base64url'))"
```

```text
JWT_SECRET=<paste it here>
```

Anyone with this secret can make tokens for any user, including admins. Treat it like the database password.

## Step 5: refresh tokens
<!-- bite: cb94e90b-17b2-4a25-96a0-e458917eb5a6 -->

A refresh token doesn't need to carry information, it just needs to be impossible to guess. So it's 32 random bytes, and we keep only its hash:

```ts
// src/auth/refresh-tokens.ts
import { randomBytes, createHash } from "node:crypto";

export function newRefreshToken() {
  return randomBytes(32).toString("base64url");
}

export function hashToken(token: string) {
  return createHash("sha256").update(token).digest("hex");
}
```

Wait, didn't Step 1 say "never use a fast hash"? For **passwords**, yes, because people choose guessable passwords and an attacker can try millions. A refresh token is 32 *random* bytes: there are more possible tokens than atoms in the planet, so guessing is hopeless however fast the hash. A fast hash is right here, and it lets us look the token up by its hash in one indexed query.

The repository, in `src/auth/refresh-tokens.pg-repository.ts`, has four methods: `create(userId, tokenHash, expiresAt)`, `findByHash(tokenHash)`, `revokeAllForUser(userId)`, and the important one:

```ts
async markUsed(id: string): Promise<boolean> {
  const result = await pool.query(
    "UPDATE refresh_tokens SET used_at = now() WHERE id = $1 AND used_at IS NULL",
    [id],
  );
  return result.rowCount === 1;
},
```

Recognise it? It's the last-plate trick from [[backend/frameworks/express/08-data-with-postgres|lesson 8]]. If two requests try to use the same refresh token at the same moment, only one `UPDATE` matches `used_at IS NULL`. The other gets `false`.

## Step 6: the auth service
<!-- bite: 6b23be6e-6819-4673-84ac-23d85706777f -->

`src/auth/auth.schemas.ts`:

```ts
import { z } from "zod";

const Email = z.string().trim().toLowerCase().max(254).pipe(z.email());
const Password = z.string().min(10, "Use at least 10 characters").max(128);

export const SignupSchema = z.object({
  email: Email,
  name: z.string().trim().min(1).max(80),
  password: Password,
});

export const LoginSchema = z.object({ email: Email, password: z.string().max(128) });
export const RefreshSchema = z.object({ refreshToken: z.string().min(20).max(200) });
```

Notice the password has a **maximum**, 128. argon2 is deliberately slow, so a 10-megabyte "password" would tie up the server. Length rules: at least 10, at most 128, and no silly "must contain a symbol" rules. Length beats complexity.

`src/auth/auth.service.ts`:

```ts
import { AppError, conflict } from "../shared/errors.ts";
import type { PasswordHasher } from "./password.ts";
import type { AccessTokens } from "./tokens.ts";
import type { UsersRepository, RefreshTokensRepository } from "./auth.repositories.ts";
import { newRefreshToken, hashToken } from "./refresh-tokens.ts";

const REFRESH_TOKEN_DAYS = 30;
const DAY_MS = 24 * 60 * 60 * 1000;

const wrongLogin = () =>
  new AppError("unauthenticated", "wrong-email-or-password", "The email or password is wrong.");
const badRefresh = (code: string) =>
  new AppError("unauthenticated", code, "Please log in again.");

export function createAuthService(deps: {
  users: UsersRepository;
  refreshTokens: RefreshTokensRepository;
  accessTokens: AccessTokens;
  hasher: PasswordHasher;
  dummyHash: string;
}) {
  const { users, refreshTokens, accessTokens, hasher, dummyHash } = deps;

  async function issueTokens(user: { id: string; role: "customer" | "staff" | "admin" }) {
    const refreshToken = newRefreshToken();
    await refreshTokens.create(user.id, hashToken(refreshToken), new Date(Date.now() + REFRESH_TOKEN_DAYS * DAY_MS));
    return {
      accessToken: await accessTokens.sign({ id: user.id, role: user.role }),
      refreshToken,
      expiresIn: 15 * 60,
    };
  }

  return {
    async signup(input: { email: string; name: string; password: string }) {
      if (await users.findByEmail(input.email)) {
        throw conflict("email-taken", "An account with this email already exists. Try logging in.");
      }
      const user = await users.create({
        email: input.email,
        name: input.name,
        passwordHash: await hasher.hash(input.password),
      });
      return issueTokens(user);
    },

    async login(input: { email: string; password: string }) {
      const user = await users.findByEmail(input.email);
      const passwordOk = await hasher.verify(user?.passwordHash ?? dummyHash, input.password);
      if (!user || !passwordOk) throw wrongLogin();
      return issueTokens(user);
    },

    async refresh(refreshToken: string) {
      const record = await refreshTokens.findByHash(hashToken(refreshToken));
      if (!record || record.revokedAt || record.expiresAt.getTime() < Date.now()) {
        throw badRefresh("invalid-refresh-token");
      }
      if (!(await refreshTokens.markUsed(record.id))) {
        await refreshTokens.revokeAllForUser(record.userId);
        throw badRefresh("refresh-token-reused");
      }
      const user = await users.findById(record.userId);
      if (!user) throw badRefresh("invalid-refresh-token");
      return issueTokens(user);
    },

    async logout(refreshToken: string) {
      const record = await refreshTokens.findByHash(hashToken(refreshToken));
      if (record) await refreshTokens.revokeAllForUser(record.userId);
    },
  };
}
```

Four careful decisions are hiding in there. Each one is a real attack being stopped.

**1. Login never says which part was wrong.** "No account with that email" tells an attacker which emails are customers. So both cases give the same answer: "The email or password is wrong."

**2. Login takes the same time either way.** If the email doesn't exist and we answered straight away, it would reply in 2 ms; a real account with a wrong password takes about 50 ms, because argon2 runs. An attacker can *time* the answer and learn which emails exist anyway. So when there's no user, we still run `verify` against a **dummy hash**, made once at startup. Both paths take the same time.

**3. Refresh tokens are single-use, and they rotate.** Every refresh gives back a *new* refresh token and marks the old one used. So a stolen refresh token stops working the moment the real app uses it.

**4. Reuse means theft.** If a refresh token that's *already been used* comes back, two people have it: the real app and a thief. We can't tell which is which, so we revoke **every** refresh token that user has. Both get logged out; the real customer logs in again with their password, and the thief can't. This is called **refresh token rotation with reuse detection**.

And signup checks for an existing email for a friendly message, but there's still a tiny race (two signups with the same email at the same moment). The unique index catches it: map Postgres error `23505` ("unique violation") to the same `email-taken` conflict in `users.create`, just like we mapped `23503` in lesson 8.

## Step 7: `req.user`, typed
<!-- bite: 62ffeb59-6838-46d4-8d44-7d91e2951787 -->

The middleware reads the token and puts the user on the request:

```ts
// src/auth/authenticate.ts
import type { Request, Response, NextFunction } from "express";
import type { AccessTokens } from "./tokens.ts";
import { AppError } from "../shared/errors.ts";

export function createAuthenticate(accessTokens: AccessTokens) {
  return async function authenticate(req: Request, res: Response, next: NextFunction) {
    const header = req.get("Authorization");
    if (!header) return next();

    const [scheme, token] = header.split(" ");
    if (scheme !== "Bearer" || !token) {
      throw new AppError("unauthenticated", "bad-authorization-header", "Send the header as: Authorization: Bearer <token>");
    }
    try {
      req.user = await accessTokens.verify(token);
    } catch {
      throw new AppError("unauthenticated", "invalid-token", "Your login has expired or is not valid. Please refresh or log in again.");
    }
    next();
  };
}

export function requireUser(req: Request, res: Response, next: NextFunction) {
  if (!req.user) throw new AppError("unauthenticated", "login-required", "Please log in first.");
  next();
}
```

Two pieces with two jobs. `authenticate` runs on every request: no header means "anonymous, carry on"; a bad header or token means 401. `requireUser` goes on the routes that need a login.

But TypeScript will refuse `req.user = ...`, because Express's `Request` type has no `user` field. This is where the trick from your old note comes in. We **add a field to Express's own type**:

```ts
// src/types/express.d.ts
import type { AuthUser } from "../auth/auth.types.ts";

declare global {
  namespace Express {
    interface Request {
      user?: AuthUser;
    }
  }
}

export {};
```

Express's types put `Request` in a global namespace called `Express`, and TypeScript lets you **reopen** an interface and add to it. Now, everywhere in the app, `req.user` is `AuthUser | undefined`. It's optional (the `?`) because on routes without `requireUser`, there may be nobody logged in, and TypeScript makes you check.

This file is only types, so Node never runs it; `tsconfig.json` includes everything under `src/`, so TypeScript and your editor see it. (Your old note had `role` and `serverRole` from another project, the same trick with a different user shape.)

One more detail for 401s. The HTTP rules say a 401 should tell the client how to authenticate. In the error handler, for the `unauthenticated` kind:

```ts
if (err.kind === "unauthenticated") res.set("WWW-Authenticate", 'Bearer realm="mama-put"');
```

## Step 8: the routes, and wiring
<!-- bite: 613907f7-b63e-4865-9ae5-659f4c378c11 -->

`src/auth/auth.routes.ts`:

```ts
export function createAuthRouter(deps: { authService: AuthService; users: UsersRepository }) {
  const { authService, users } = deps;
  const router = express.Router();

  router.post("/signup", async (req, res) => {
    const input = validate(SignupSchema, req.body, "body");
    res.status(201).json({ data: await authService.signup(input) });
  });

  router.post("/login", async (req, res) => {
    const input = validate(LoginSchema, req.body, "body");
    res.json({ data: await authService.login(input) });
  });

  router.post("/refresh", async (req, res) => {
    const { refreshToken } = validate(RefreshSchema, req.body, "body");
    res.json({ data: await authService.refresh(refreshToken) });
  });

  router.post("/logout", async (req, res) => {
    const { refreshToken } = validate(RefreshSchema, req.body, "body");
    await authService.logout(refreshToken);
    res.sendStatus(204);
  });

  router.get("/me", requireUser, async (req, res) => {
    const user = await users.findById(req.user!.id);
    res.json({ data: { id: user!.id, email: user!.email, name: user!.name, role: user!.role } });
  });

  return router;
}
```

`/me` never sends `passwordHash`. The users repository returns it (login needs it), but nothing that faces the outside world ever includes it.

In `createApiRouter`, mount it and run `authenticate` for everything:

```ts
api.use(deps.authenticate);
api.use("/auth", createAuthRouter(deps));
api.use("/menu", createMenuRouter({ ...deps, version: versions.menu }));
api.use("/orders", createOrdersRouter(deps));
```

And orders now belong to whoever places them:

```ts
router.post("/", requireUser, async (req, res) => {
  const input = validate(PlaceOrderSchema, req.body, "body");
  const order = await ordersService.place(req.user!.id, input.dishId, input.quantity);
  res.status(201).location(`${req.baseUrl}/${order.id}`).json({ data: order });
});
```

(`place` gains a `customerId` parameter, the orders repository stores it in `customer_id`, and `Order` gets `customerId`.)

In `server.ts`, the new pieces:

```ts
const jwtSecret = process.env.JWT_SECRET;
if (!jwtSecret || jwtSecret.length < 32) throw new Error("JWT_SECRET must be set, at least 32 characters");

const accessTokens = createAccessTokens(jwtSecret);
const users = createPgUsersRepository(pool);
const refreshTokens = createPgRefreshTokensRepository(pool);
const authService = createAuthService({
  users, refreshTokens, accessTokens,
  hasher: argon2Hasher,
  dummyHash: await argon2Hasher.hash("not-a-real-password"),
});
const authenticate = createAuthenticate(accessTokens);
```

## Trying it
<!-- bite: cccd4bb1-25d1-4058-b1a0-3aaa5aeb0e10 -->

```bash
npm run migrate

# Sign up
curl -s -X POST http://localhost:3000/v2/auth/signup -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","name":"Ada","password":"jollof-is-life"}'
# {"data":{"accessToken":"eyJhbGciOi...","refreshToken":"q3Zt...","expiresIn":900}}

TOKEN=eyJhbGciOi...     # paste your access token

curl -s http://localhost:3000/v2/auth/me -H "Authorization: Bearer $TOKEN"
# {"data":{"id":"1","email":"ada@example.com","name":"Ada","role":"customer"}}

# Order, logged in
curl -s -X POST http://localhost:3000/v2/orders -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"dishId":"1","quantity":2}'

# Order, not logged in: 401 login-required, with a WWW-Authenticate header
curl -si -X POST http://localhost:3000/v2/orders -H "Content-Type: application/json" \
  -d '{"dishId":"1","quantity":2}' | head -5
```

Then try the attacks:

1. Change one character in the middle of `$TOKEN` and call `/me`. Predict the answer: 401 `invalid-token`.
2. Log in with a wrong password, then with an email that doesn't exist. Same answer both times.
3. Call `/auth/refresh` with your refresh token. It works and gives you a new pair. Call it again with the **old** refresh token. Predict: 401 `refresh-token-reused`, and now the *new* refresh token is dead too.

## The TypeScript in this lesson
<!-- bite: dcb04938-eb94-4b93-8c1c-1416e18d348a -->

1. **`import { SignJWT, jwtVerify } from "jose"`**: **Named imports**: take these two specific things from the package. A package can export many things; braces pick the ones you need.
2. **`new SignJWT({...}).setSubject(...).setIssuer(...)...sign(key)`**: A **builder**: each method sets one thing and returns the same builder, so you can chain them, and the last call (`sign`) produces the result. It reads like a sentence.
3. **`new TextEncoder().encode(secret)`**: Turns text into raw bytes (a `Uint8Array`), which is what signing keys are made of.
4. **`Promise<AuthUser>`** on `verify`: the function is `async`, so it returns a promise; once awaited, it's an `AuthUser`.
5. **`user?.passwordHash ?? dummyHash`**: Read it in two parts. `user?.passwordHash`: if `user` is `null`, stop and give `undefined` instead of crashing. Then `?? dummyHash`: if that's `undefined`, use the dummy. Together: "the user's hash if there is a user, otherwise the dummy".
6. **`if (!(await refreshTokens.markUsed(record.id)))`**: The brackets matter. `await` first, to get the true or false, then `!` to flip it. Without the inner brackets, `!` would apply to the promise itself, which is always "something", so `!promise` is always false.
7. **`const [scheme, token] = header.split(" ")`**: **Array destructuring**: the first piece goes into `scheme`, the second into `token`. `"Bearer abc".split(" ")` gives `["Bearer", "abc"]`.
8. **`declare global { namespace Express { interface Request { user?: AuthUser } } }`**: `declare` says "this describes something that exists elsewhere; there's no code here". `global` means "the world-wide scope, not this file". `interface Request` reopens Express's existing type and adds a field. Interfaces, unlike `type`s, can be reopened like this, which is called **declaration merging**.
9. **`export {}`**: A file with no imports or exports is treated as an old-style script, and `declare global` only works in a module. This empty export makes the file a module. It looks odd; it's needed.
10. **`req.user!.id`**: The `!` after a value is a **non-null assertion**: "I promise this isn't `undefined`". Here it's true, because `requireUser` ran first and would have thrown. TypeScript can't see that across middleware, so we tell it. Use `!` only where you can point at the reason it's safe.
11. **`24 * 60 * 60 * 1000`**: Milliseconds in a day, written so you can read it: hours, minutes, seconds, milliseconds.
12. **`await` at the top of `server.ts`**: Making the dummy hash needs `await`, and top-level await (from lesson 8) lets `server.ts` wait for it before starting.

## Your project so far
<!-- bite: fa5454e3-aa14-424a-b9c6-28301e1c994b -->

```text
mama-put-api/
├── .env                          ← now also JWT_SECRET
├── .env.example  ·  .gitignore  ·  package.json (argon2, jose)  ·  tsconfig.json
├── migrations/
│   ├── 001 … 005
│   ├── 006_create_users.sql            ← NEW: users, roles, unique lower(email)
│   ├── 007_create_refresh_tokens.sql   ← NEW: hashed, expiring, single-use refresh tokens
│   └── 008_orders_belong_to_customers.sql ← NEW: orders.customer_id
├── openapi/      v1.json · v2.json (regenerate: auth routes and bearer security added)
└── src/
    ├── server.ts                 ← builds tokens, hasher, dummy hash, auth service, authenticate
    ├── app.ts  ·  api.ts         ← api.ts runs authenticate, mounts /auth
    ├── types/
    │   └── express.d.ts          ← NEW: req.user, typed (declaration merging)
    ├── auth/
    │   ├── auth.types.ts         ← NEW: Role, AuthUser
    │   ├── auth.schemas.ts       ← NEW: Signup, Login, Refresh
    │   ├── auth.repositories.ts  ← NEW: UsersRepository, RefreshTokensRepository types
    │   ├── users.pg-repository.ts           ← NEW (maps 23505 to email-taken)
    │   ├── refresh-tokens.pg-repository.ts  ← NEW (markUsed is the atomic check)
    │   ├── password.ts           ← NEW: argon2id hasher
    │   ├── tokens.ts             ← NEW: sign and verify access tokens
    │   ├── refresh-tokens.ts     ← NEW: random tokens and their SHA-256 hashes
    │   ├── auth.service.ts       ← NEW: signup, login, refresh (rotation and reuse detection), logout
    │   ├── authenticate.ts       ← NEW: authenticate and requireUser
    │   └── auth.routes.ts        ← NEW: /signup, /login, /refresh, /logout, /me
    ├── docs/  db/  menu/          (unchanged; docs gain the auth routes)
    ├── orders/                   ← POST requires a user; orders record customerId
    └── shared/                   ← error-handler adds WWW-Authenticate on 401s
```

## Common mistakes
<!-- bite: 3b53598a-a245-4cfa-b4d9-978f94e6d535 -->

1. **Storing passwords, or fast hashes of them.** Use argon2id (or bcrypt). Never MD5, SHA-1 or plain SHA-256 for passwords.
2. **"No account with that email."** It tells attackers who your customers are. One message for both cases, and the same timing.
3. **No maximum password length.** A huge password makes argon2 eat your CPU. Cap it.
4. **Secrets in JWTs.** They're readable by anyone. Ids and roles only.
5. **Accepting any algorithm, issuer or audience.** Pin all three in `jwtVerify`.
6. **Long-lived access tokens.** A stolen 30-day token is a 30-day problem. Keep access short and refresh with rotation.
7. **Refresh tokens stored in plain text.** Store their hashes.
8. **A weak or committed `JWT_SECRET`.** Anyone with it can become admin. Long, random, in `.env`, never in git.
9. **Sending `passwordHash` in a response.** Choose the fields that go out, every time.

## Check your understanding
<!-- bite: b78a6039-c95c-48ee-9598-0bcb3cd5acbe -->

1. Why does Mama Put use argon2 for passwords but SHA-256 for refresh tokens?
2. A thief copies Ada's refresh token. Ada's app refreshes first. What happens when the thief tries to use it?
3. Someone decodes their access token, changes `"role":"customer"` to `"role":"admin"`, and sends it. What happens, and which line stops it?
4. Why does login verify against a dummy hash when there's no such user?
5. Why is `req.user` optional (`user?:`) in the type?

<details>
<summary>Answers, after your attempt</summary>

1. Passwords are chosen by people and often guessable, so each guess must be made slow and expensive: argon2. Refresh tokens are 32 random bytes, impossible to guess no matter how fast the hash, so a fast hash is fine and lets us look them up quickly.
2. Ada's refresh marked that token used and gave her a new one. The thief's attempt finds a used token, so we treat it as theft: every refresh token for Ada is revoked, and the thief gets 401 `refresh-token-reused`. Ada has to log in again with her password; the thief can't.
3. The signature no longer matches the changed payload, so `jwtVerify` throws and `authenticate` answers 401 `invalid-token`. Without our secret, nobody can make a valid signature for the changed token.
4. So that "no such email" and "wrong password" take the same time. Otherwise an attacker could time the answers and learn which emails have accounts.
5. Because on routes without `requireUser`, nobody may be logged in. The `?` makes TypeScript force us to handle that case, or use `!` where `requireUser` guarantees it.

</details>

## Practice
<!-- bite: 9567c54e-1e31-4f71-a42f-0d3a3e7d2de9 -->

1. Add `PATCH /auth/me` to change your name, and `POST /auth/change-password`, which needs the current password, and revokes all refresh tokens afterwards (so other phones are logged out).
2. Replace `kitchenOnly`'s shared key with a check that `req.user.role` is `"staff"` or `"admin"`. Make yourself staff with `UPDATE users SET role = 'staff' WHERE email = '...'` in `psql`. (Lesson 13 turns this into a proper system; this is the first step.)
3. Update the OpenAPI document: add a `bearerAuth` security scheme (`type: http`, `scheme: bearer`, `bearerFormat: JWT`), the auth routes, and `security` on `POST /orders`.

**Done when** signup, login, `/me`, refresh, reuse detection and logout all behave as in "Trying it"; the staff key is gone; and the Swagger page's "Authorize" button lets you paste a token and place an order from the browser.

## Before moving on
<!-- bite: 27566879-b73d-42f2-9af9-4adbbc0fcf97 -->

Mama Put API now knows who's calling. Passwords are hashed, access tokens are short and signed, refresh tokens rotate and catch thieves, and `req.user` is typed everywhere.

But knowing *who* someone is doesn't say what they *may do*. Right now, Ada is logged in, so she can call `GET /orders/7`, which is Bayo's order, with his phone number on it soon. And after practice 2, any staff member can delete the whole menu, including the cook who only started yesterday. That's authorization, the next lesson.

## Related
<!-- bite: 858dcc99-ddab-4d0a-80bd-13ae384f30e2 -->

- [[backend/frameworks/express/13-authorization|Next: Authorization]]
- [[backend/05-auth/01-authentication-flows|Authentication Flows]] — the idea in any framework
- [[backend/05-auth/03-oauth-provider-integrations|OAuth Provider Integrations]] — "Log in with Google", built on the same pieces
- [[cybersecurity/index|Cybersecurity]] — why these attacks work

## About this lesson
<!-- bite: 90bf0bdc-4e76-4155-b49c-e6719e96d506 -->

**Level:** Intermediate → Advanced. Lesson 12 of [[backend/frameworks/express/index|Express]]. Covers password hashing with argon2id, sessions versus tokens, users and refresh-token tables, signing and verifying JWTs with jose (pinned algorithm, issuer and audience), random refresh tokens stored as hashes, rotation with reuse detection, constant-time-ish login with a dummy hash, the `authenticate` and `requireUser` middleware, typing `req.user` with declaration merging, and `WWW-Authenticate` on 401s.
