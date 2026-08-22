# NextVibe — Backend Authentication (JWT, OAuth, Guards)

Split out from the original flat `learning.md` (moved to `learning/archive/`). See also
`learning/backend/01-core.md` (NestJS/Prisma fundamentals), `learning/backend/03-modules.md` (domain
modules), `learning/backend/05-realtime.md` (WebSocket gateway authentication specifically),
`learning/00-sys-design.md`, `learning/09-devops.md`, `learning/backend/04-games-ai.md`, and the
`learning/frontend/03-auth.md` file for the frontend side of this same system (token storage,
refresh queue, multi-role cookies, login redirects).

This file covers: password hashing with Argon2, the JWT access/refresh token architecture and
its full lifecycle from login to logout, Google OAuth verification and account linking, email
enumeration prevention, the `@Public()` opt-out guard pattern (secure-by-default auth), debugging
a 401 on login, and how the guard behaves differently on public vs protected routes.

---

## Part 8 — Authentication Deep Dive

The `AuthModule` contains some of the most important patterns in the codebase.

### Password Hashing with Argon2

When a user registers, their password is never stored. Instead:

```typescript
const passwordHash = await argon2.hash(dto.password);
```

Argon2 is the winner of the Password Hashing Competition (2015). It's specifically designed to be slow (expensive to compute) and memory-hard (expensive to brute-force with GPUs). The previous standard was bcrypt, then scrypt. Argon2 is the current gold standard.

**Why not MD5 or SHA256?** Those are general-purpose hash functions designed to be fast. Fast is bad for password hashing — it makes brute-force attacks trivial. An attacker with a GPU can compute billions of MD5 hashes per second. Argon2 is deliberately designed so each hash takes meaningful memory and CPU.

**Why Argon2 specifically over bcrypt?**

bcrypt is not broken. It's been used for decades and is still considered secure. But it was designed in 1999, before GPU-based password cracking was a real threat.

The problem with bcrypt at a hardware level: each bcrypt computation uses very little memory. A modern GPU has thousands of cores and can compute thousands of bcrypt hashes in parallel. An attacker with a consumer GPU can try billions of passwords per day.

Argon2 was designed in 2015 specifically to defeat this attack. It has three tunable parameters:
- **Time cost** — how many iterations to run (like bcrypt's cost factor)
- **Memory cost** — how much RAM each hash requires (e.g., 64MB)
- **Parallelism** — how many threads to use

The memory cost is the key weapon. If each Argon2 hash requires 64MB of RAM, and a GPU has 8GB of VRAM, you can only run 128 hashes simultaneously. bcrypt has no such constraint — you can run thousands in parallel. The memory requirement means GPU attacks on Argon2 are orders of magnitude more expensive than on bcrypt.

There are three Argon2 variants:
- `Argon2d` — fastest, resistant to GPU attacks, but vulnerable to side-channel attacks (timing attacks that infer data by measuring how long an operation takes)
- `Argon2i` — resistant to side-channel attacks, slightly slower
- `Argon2id` — hybrid of the two, and the one recommended for password hashing. Most libraries (including the `argon2` npm package) default to this

**Bottom line:** bcrypt is acceptable. Argon2id is better. If you're starting fresh (as this project is), use Argon2. If you have an existing system on bcrypt, it's not worth migrating — bcrypt is still fine. The difference matters most when someone gets your password hash database and tries to crack it offline.

**Verification:**
```typescript
const passwordValid = await argon2.verify(user.passwordHash, dto.password);
```

You never decrypt a hash. You hash the input again and compare.

### JWT Tokens

JWTs (JSON Web Tokens) are how the API knows who is calling.

After login, the server issues two tokens:
- **Access token** — short-lived (typically 15min-1hr), sent with every API request
- **Refresh token** — long-lived (30 days here), used only to get a new access token

**Why two tokens?** Access tokens can't be revoked — if someone steals one, they can use it until it expires. By keeping them short-lived, the damage window is small. Refresh tokens are long-lived but stored in Redis and can be explicitly deleted (revoked) on logout.

The JWT payload (what's inside the token):
```typescript
{ sub: userId, email, username }
```

`sub` (subject) is the standard JWT claim for the user ID.

**Token rotation:** When you use a refresh token, the old one is deleted from Redis and a new pair is issued. This means a stolen refresh token can only be used once — if the attacker uses it first, the legitimate user's next refresh attempt fails (telling them their session was stolen).

### The Full JWT Flow — Frontend to Backend

This is the complete lifecycle, from first login to a request made three weeks later.

**Step 1: Login**
```
Frontend → POST /auth/login { email, password }
Backend  → returns { accessToken, refreshToken }
Frontend → stores accessToken in memory, refreshToken in secure storage
           (HttpOnly cookie or secure localStorage)
```

**Step 2: Every API request**
```
Frontend → GET /events
           Headers: { Authorization: "Bearer <accessToken>" }
Backend  → JwtAuthGuard intercepts the request
           → verifies the token signature with JWT_ACCESS_SECRET
           → decodes { sub: userId, email, username }
           → attaches user to request as req.user
           → controller runs
```

The access token is verified **without any database query**. This is the whole point of JWTs — they're self-contained. The server just checks the signature. This makes every authenticated request fast.

**Step 3: Access token expires**

The access token expires (15 minutes after login). The next API call returns `401 Unauthorized`. The frontend catches this and does not show the user a login screen. Instead:

```
Frontend → POST /auth/refresh
           Body: { refreshToken: "<stored refresh token>" }
Backend  → verifies the refresh token signature with JWT_REFRESH_SECRET
           → looks up the key "refresh:userId:refreshToken" in Redis
           → if the key exists: token is valid and not revoked
           → deletes the old key (the token is now consumed)
           → issues a NEW access token + NEW refresh token
           → stores the new refresh token key in Redis with 30-day TTL
           → returns { accessToken, refreshToken }
Frontend → updates stored tokens
           → retries the original failed request with the new access token
```

This happens silently. The user never sees a login prompt unless their refresh token has also expired or been revoked.

**Step 4: Logout**
```
Frontend → POST /auth/logout { refreshToken }
Backend  → deletes "refresh:userId:refreshToken" from Redis
           → access token is still technically valid until it expires
             but since it's short-lived, that's an acceptable window
```

**Step 5: Refresh token expires (30 days)**

The Redis key `refresh:userId:refreshToken` has a 30-day TTL. After 30 days of no activity, the key disappears. The next refresh attempt finds no key in Redis and returns `401`. The frontend now shows the login screen. The user was "remembered" for 30 days automatically.

**The security property this design gives you:**
- Stolen access token? Damage window = however long until expiry (currently infinite — bug, see below)
- Stolen refresh token? Usable exactly once. If the attacker uses it first, the real user's next refresh attempt fails, alerting them something is wrong
- Logout from one device? Delete that device's refresh token key — that session is dead
- "Log out everywhere"? Delete all Redis keys matching `refresh:userId:*` — all sessions for that user are instantly revoked, regardless of how many devices they were on

**The current bug:** `expiresIn` is commented out in `generateTokens()`. Access tokens never expire. This eliminates the short-damage-window benefit entirely. Fix this before launch by uncommenting and setting `expiresIn: '15m'` for access tokens. (This is tracked as a P0 security gap in `learning/backend/01-core.md` Part 20 — What is Missing.)

### Google OAuth

```typescript
const ticket = await this.googleClient.verifyIdToken({
  idToken,
  audience: GOOGLE_CLIENT_ID,
});
const payload = ticket.getPayload();
```

The frontend gets an `idToken` from Google's SDK. The backend verifies that token with Google's servers. Google tells you: "this token was issued to this user, for your application." You don't call a Google API yourself — you just verify the cryptographic signature.

**Account linking:** If a user registered with email/password and then tries to log in with Google using the same email, the code links the accounts rather than creating a duplicate. This is critical UX — users shouldn't have two accounts because they forgot which login method they used.

(See `learning/frontend/03-auth.md` Part 37 and Part 43 for two real production bugs in the frontend's Google login button — a wrong cookie expiry that silently killed WebSocket auth, and a `?from=` redirect encoding bug.)

### Security: Email Enumeration Prevention

```typescript
// forgot password
if (!user) return { message: 'If that email exists, a reset link has been sent' };
```

If you return "user not found" when someone submits a non-existent email for password reset, you've told an attacker which emails are registered in your system. Always return the same message regardless of whether the email exists.

### Guards

`JwtAuthGuard` is applied globally in this project. Every route is protected by default. You opt OUT with `@Public()`:

```typescript
@Public()
@Post('webhook/juicyway')
```

This is the "secure by default" pattern. The alternative (protect routes explicitly with `@UseGuards()`) means forgetting to add the guard exposes a route. Secure by default means forgetting to add `@Public()` just means the route requires auth unnecessarily — a much less dangerous mistake. See Part 46 below for the full mechanics of how `@Public()` works.

---

## Part 40 — Debugging a 401 on Login

### The Login Endpoint Architecture

The login route is decorated with `@Public()`:

```typescript
@Public()
@Post('login')
login(@Body() dto: LoginDto) {
  return this.authService.login(dto);
}
```

And the JWT guard handles `@Public()` like this:

```typescript
async canActivate(context: ExecutionContext): Promise<boolean> {
  const isPublic = this.reflector.getAllAndOverride(IS_PUBLIC_KEY, [...]);
  if (isPublic) {
    try {
      await super.canActivate(context);  // attempt auth if token present
    } catch (_) {}                        // swallow the error
    return true;                          // always let through
  }
  return super.canActivate(context);
}
```

On `@Public()` routes the guard **always returns `true`** regardless of whether a token is present or valid. So a 401 on `POST /auth/login` is **never coming from the guard** — it's always coming from the service throwing `UnauthorizedException`.

### The Three Causes of a 401 on Login

**1. Email not found**
```typescript
const user = await this.prisma.user.findUnique({ where: { email: dto.email } });
if (!user || !user.passwordHash) {
  throw new UnauthorizedException('Invalid credentials');
}
```
The user doesn't exist in the database. Check: wrong email, different environment (dev DB vs prod DB), or they never registered.

**2. OAuth user trying email/password login**
Same code block — `!user.passwordHash`. A user who signed up with Google OAuth has no password hash. If they try to log in with email + password, they hit this check. The error message deliberately says "Invalid credentials" (not "use Google OAuth") so you don't leak that the account exists.

**3. Wrong password**
```typescript
const passwordValid = await argon2.verify(user.passwordHash, dto.password);
if (!passwordValid) {
  throw new UnauthorizedException('Invalid credentials');
}
```
The user exists and has a password, but the password is wrong.

### How to Distinguish Them from Logs

The response time tells you which branch was hit:
- **Fast 401 (~5ms)** — user not found or no passwordHash. Prisma query returned immediately, no argon2 run.
- **Slow 401 (~100–200ms)** — wrong password. Argon2 verification ran (intentionally slow to resist brute force), found mismatch.

Looking at the actual logs:
```
POST /v1/auth/login  401  161ms   ← argon2 ran → user found, wrong password
POST /v1/auth/login  401   68ms   ← argon2 didn't run → user not found or no passwordHash
```

### Case Sensitivity

Postgres string comparisons are case-sensitive by default. If a user registered as `John@Gmail.com` and logs in as `john@gmail.com`, `findUnique({ where: { email: 'john@gmail.com' } })` returns null — a fast 401.

Fix: normalise emails to lowercase before storing and before querying.

```typescript
// On registration:
email: dto.email.toLowerCase()

// On login:
where: { email: dto.email.toLowerCase() }
```

---

## Part 46 — The `@Public()` Guard Pattern: How Opt-Out Auth Works

### Secure by Default

The `JwtGuard` is applied globally in `AppModule`:

```typescript
app.useGlobalGuards(new JwtGuard(reflector));
// or in AppModule providers:
{ provide: APP_GUARD, useClass: JwtGuard }
```

This means **every single route** is protected by default. You never forget to add auth to a sensitive endpoint because auth is automatic. You only opt out explicitly with `@Public()`.

The alternative (opt-in auth with `@UseGuards()` on each route) means forgetting to add the guard on a sensitive endpoint exposes it publicly. Secure by default avoids this class of mistake entirely.

### How `@Public()` Works Technically

`@Public()` is a custom decorator that sets metadata on the route handler:

```typescript
export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
```

`SetMetadata` stores a key-value pair on the route handler's metadata. The guard reads it:

```typescript
const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
  context.getHandler(),  // check method-level metadata first
  context.getClass(),    // fall back to class-level metadata
]);
if (isPublic) return true;
```

`getAllAndOverride` means: check the handler first (method decorator), then the class (controller decorator). If either has `isPublic: true`, the route is public.

### The Try/Catch on Public Routes

```typescript
if (isPublic) {
  try {
    await super.canActivate(context);  // attempt to validate JWT if present
  } catch (_) {}                        // ignore if no token or invalid token
  return true;                          // always allow through
}
```

This is subtle: even on `@Public()` routes, the guard *tries* to validate the JWT. Why? Because some public routes benefit from knowing who's calling — even if authentication isn't required.

For example, `GET /events/:id` is public (anyone can view an event) but if the user IS logged in, the response includes `isRsvped: true` and `isCheckedIn: true`. The guard tries to parse the JWT; if it succeeds, `req.user` is populated and the controller can read it with `@CurrentUser()`. If there's no token or it's invalid, the try/catch swallows the error, `req.user` is undefined, and the public response is returned without the user-specific fields.

This is why `@CurrentUser()` on a `@Public()` route returns `undefined` when not authenticated — and you see patterns like `@CurrentUser() user?: JwtPayload` (note the `?`) on those handlers.

(See `learning/backend/03-modules.md` Part 50/51 for the pledges and Ercaspay payment modules, which use this same `@Public()` + optional-user pattern to support both guest and authenticated flows on the same endpoint. See `learning/backend/04-games-ai.md` Part 49 for the anonymous game play system, another major consumer of "public route, optional identity" patterns.)

---

## The general version of this
- [[backend/05-auth/01-authentication-flows|Authentication Flows (concepts)]] — sessions vs tokens, framework-agnostic
- [[backend/05-auth/02-authorization|Authorization]]
- [[concepts/interview/01-apis-auth-and-practices|Interview: auth questions]]

↑ [[projects/README|All projects and the domains they exercise]]

---

## Refresh token rotation needs a grace window (2026-08-21)

Symptom: a run of `POST /api/auth/refresh 401` repeating in the console, and a
session that never recovered without a manual re-login.

### What rotation is, and the trap in it

The refresh endpoint uses **rotating, single-use refresh tokens** whitelisted in
Redis. Each refresh consumes the old token and issues a new pair:

```ts
const exists = await this.redis.exists(redisKey);
if (!exists) throw new UnauthorizedException('Refresh token expired or revoked');

await this.redis.del(redisKey);              // consume it
const tokens = await this.generateTokens(payload);   // issue the replacement
return tokens;
```

Rotation is good security — a stolen refresh token stops working as soon as the
real user refreshes. But look at the ordering. The old token is destroyed
**before** the replacement reaches the browser. If anything goes wrong in that
gap, the client is left holding a token the server has already deleted, and
there is no path back. Things that land in that gap, all routine:

- the client's own abort timeout firing while the API cold-starts (Render free
  tier — the request *is* processed, the response just arrives too late);
- two tabs refreshing at once;
- any retry of a request whose response was lost.

The session isn't compromised in any of these. It's just gone.

### The fix: a short replay window

Keep the tokens that a rotation issued, keyed by the token it retired, for a
minute. A duplicate refresh inside that window gets the same replacement pair
instead of a dead end:

```ts
const graceKey = `refresh:used:${payload.sub}:${refreshToken}`;

if (!exists) {
  const replayed = await this.redis.get(graceKey);
  if (replayed) return JSON.parse(replayed);      // benign duplicate
  throw new UnauthorizedException('Refresh token expired or revoked');
}

await this.redis.del(redisKey);
const tokens = await this.generateTokens(payload);
await this.redis.set(graceKey, JSON.stringify(tokens), 60);
```

60 seconds is the trade-off: long enough to absorb a retry or a cold start,
short enough that a genuinely leaked token isn't reusable for meaningfully
longer than before.

**Don't forget logout.** The grace key has to be deleted there too, or logging
out can be silently undone by an in-flight refresh:

```ts
await this.redis.del(`refresh:${userId}:${refreshToken}`);
await this.redis.del(`refresh:used:${userId}:${refreshToken}`);
```

### The wider lesson: distinguish "denied" from "unavailable"

The proxy route collapsed every failure into 401 — including its own
`catch` block, which fires when the API is simply unreachable:

```ts
} catch {
  return NextResponse.json({ message: "Refresh failed" }, { status: 401 });
}
```

401 means *"your credentials were rejected"*. A network error means *"I don't
know"*. Reporting the second as the first means one bad minute from the API logs
every active user out. The route now returns **401 only when the backend itself
rejected the token (401/403)** and **502 otherwise**, and the client destroys
the session only on 401.

That distinction is a general API design habit worth keeping: **never report an
infrastructure failure as an authorisation failure.** The client's correct
reaction to the two is opposite — give up vs. try again.

Related: the client-side half of this loop is in
[frontend/03-auth.md](../frontend/03-auth.md).

---

## Part N — Making Google sign-in work from the mobile app (2026-08-22)

The backend already had `POST /auth/oauth/google` taking an ID token. It worked
from the web and would have rejected every single sign-in from the phone. The
reason is the one thing about Google OAuth that catches everybody once.

### First: how mobile Google auth actually differs from web

It's worth being precise about this, because the intuition — "mobile needs a
different flow" — is wrong for this codebase, and the thing that *does* differ is
easy to miss.

**The backend endpoint is the same one.** Both platforms send a Google **ID
token** to `POST /v1/auth/oauth/google`. There is no mobile-specific route, and
no OAuth redirect/callback to implement.

```
web:     browser  → Google Identity Services (@react-oauth/google)
                  → credentialResponse.credential   ← an ID token
                  → POST /v1/auth/oauth/google { idToken }

mobile:  app      → native Google Sign-In SDK
                  → getTokens().idToken             ← an ID token
                  → POST /v1/auth/oauth/google { idToken }   ← identical
```

What genuinely differs is only three things:

| | Web | Mobile |
|---|---|---|
| How the ID token is obtained | GIS button in the browser | native SDK |
| The token's `aud` claim | web client ID | Android / iOS client ID |
| Where NextVibe's tokens are stored | httpOnly cookies via a Next.js route | `expo-secure-store` |

The middle row is the entire backend problem, and it's covered next.

**Why there's no authorization code exchange anywhere here.** The classic OAuth
diagram — redirect to provider, get a `code` back, POST it with your client
secret to swap for tokens — is the *server-side web app* flow. This backend never
does it. Both clients use the ID token flow: the provider hands the client a
signed assertion of who the user is, and the client relays it. The backend's only
job is verifying the signature and the audience.

That's why `GOOGLE_CLIENT_SECRET` is in `.env` and read by nothing. Worth
recognising: a client secret is meaningless in a mobile app or a browser anyway —
anything shipped to a user's device isn't secret. That's precisely why the ID
token flow exists.

### One Google project, several client IDs

In the Google Cloud console you create a separate **OAuth client ID per
platform**: Web, Android, iOS. They're not interchangeable. When Google issues
an ID token it stamps the requesting client's ID into the token's `aud`
(audience) claim.

Verification checks that claim:

```typescript
// before — only ever accepts tokens minted for the web client
const ticket = await this.googleClient.verifyIdToken({
  idToken,
  audience: this.configService.get<string>('GOOGLE_CLIENT_ID'),
});
```

An Android token carries `aud = <android client id>`, doesn't match, and throws
— surfacing as a flat `401 Invalid Google token` with nothing to say *which*
check failed. `verifyIdToken` accepts an array, so the fix is to trust every
platform ID you actually own:

```typescript
this.googleAudiences = [
  this.configService.get<string>('GOOGLE_CLIENT_ID'),          // web
  this.configService.get<string>('GOOGLE_CLIENT_ID_ANDROID'),
  this.configService.get<string>('GOOGLE_CLIENT_ID_IOS'),
].filter((id): id is string => !!id && id.trim().length > 0);
```

**Why an allow-list and not "skip the audience check":** `aud` is what stops a
token minted for someone *else's* app being replayed against yours. Any Google
user can get a valid, correctly-signed ID token from any app they sign into —
signature validity alone proves nothing about who it was meant for. Dropping the
check turns "prove this token was issued for us" into "prove this token exists".

Note the type predicate `(id): id is string => ...`. Without it, `.filter()`
leaves the array typed `(string | undefined)[]` and TypeScript rejects it where
a `string[]` is wanted. The predicate is how you tell the compiler what the
filter guarantees at runtime.

### `email_verified` is the claim that matters for account linking

The handler looks a user up by email and, finding one, signs you in as them:

```typescript
let user = await this.prisma.user.findFirst({
  where: { OR: [{ email }, { oauthProvider: 'GOOGLE', oauthId: googleId }] },
});
```

That's account linking, and it's a takeover vector if the email isn't verified.
Google accounts can be created on arbitrary addresses; `email_verified: false`
means Google is passing along an address it has **not** confirmed. If someone
registers a Google account on your user's address, this branch hands them that
user's tokens without a password.

```typescript
if (payload.email_verified === false) {
  throw new UnauthorizedException('Your Google email address is not verified');
}
```

**The general rule: "this identity provider told me an email address" and "this
person controls that email address" are different claims.** Only the second one
justifies linking to an existing account, and only `email_verified` asserts it.

### Optional claims are optional

```typescript
const baseUsername = name.toLowerCase()...   // 500 when `name` is absent
```

`name` is only present when the profile scope was granted, and it goes missing
often enough on mobile to matter. Every field in an OIDC ID token except `sub`
(and `iss`/`aud`/`exp`) should be treated as optional:

```typescript
const baseUsername =
  (name ?? email.split('@')[0] ?? '')
    .toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/g, '').slice(0, 20)
  || 'vibe';
```

Two fallbacks, because the first one can also produce an empty string — an
address of all-punctuation before the `@` strips to `''`, and an empty username
would collide on the uniqueness loop forever.

`sub` is the only stable identifier, which is why it's what gets stored as
`oauthId`. Email addresses can be changed by the user; `sub` cannot.

### What the mobile side does

The app gets a token with `getTokens()` / `getIdToken()` from its Google sign-in
library, configured with the **web** client ID as `webClientId`, and POSTs it to
`/auth/oauth/google` as `{ idToken }`. The backend does the rest. Nothing about
this flow needs `GOOGLE_CLIENT_SECRET` — that's for the server-side authorization
code exchange, which this app doesn't use.
