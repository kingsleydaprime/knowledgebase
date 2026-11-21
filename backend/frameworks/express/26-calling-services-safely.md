---
id: c4f1f5f1-7e30-44e1-ae0b-907f11767269
---

# Calling Other Services Safely

**Calling another service safely means expecting it to be slow, down, or overloaded at any moment, and making sure that when it is, your service fails quickly and gently instead of hanging, piling on more load, or falling over with it. It also means proving who you are when you call, and checking who's calling you.** One service calling another is the most common way a small problem becomes a whole-system outage. This lesson is the set of habits that stop that.

## Before you start
<!-- bite: 10f525b5-03d4-4f64-a336-8c85f49478ab -->

You should have the two services from [[backend/frameworks/express/25-splitting-out-a-microservice|lesson 25]], with notifications calling the API's `GetContact` and `GetDish` over gRPC.

After this lesson you will be able to:

1. Explain how one slow service can take down the services that call it.
2. Give every call a deadline, and pass the remaining time on to the next call.
3. Retry only what's safe to retry, a limited number of times, with backoff and jitter.
4. Build a circuit breaker, and give each call a fallback where one makes sense.
5. Authenticate services to each other with short-lived signed tokens, check permissions per call, and encrypt the traffic.

## Where we stopped
<!-- bite: 40245ba5-9ff2-4cf9-b8d7-4963d7f61165 -->

Picture lunchtime next Friday:

1. The API is busy, and its database is slow for a minute. `GetContact` normally takes 5 ms; now it takes 4 seconds.
2. Notifications has no deadline on its calls, so each one waits the whole 4 seconds. Its consumer handles 10 messages at once, so 10 calls are waiting.
3. Messages pile up in the stream. Notifications' code, seeing errors when calls finally time out somewhere, retries immediately. Then again.
4. The API, already slow, now gets three times as many `GetContact` calls as usual, from the retries. It slows down more. Customers' order requests on the API, which share the same database and CPU, start timing out too.

Nothing was broken. One database was slow for a minute. But the way notifications *called* the API turned a slow minute into an outage for customers placing orders. That chain reaction is called a **cascading failure**, and it's the classic way distributed systems go down.

And separately, there's the hole lesson 25 left open: anything on the internal network can call `GetContact` and read any customer's email and phone number.

## The kid version
<!-- bite: a9cdba02-81f0-4881-ae7f-7cb734ed35c4 -->

Mama sends her boy to the market for tomatoes. She says: "Be back in 30 minutes, whatever happens."

If the tomato seller's queue is long, the boy waits... until 25 minutes, then comes home with whatever he has. He doesn't stand there all day while Mama's stew burns.

If the seller was out of tomatoes this morning, and again at noon, Mama doesn't send him a third time at 12:30. She says "the tomato seller is closed today; use tinned tomatoes", and tries again tomorrow.

And the seller only gives the boy Mama's usual order if he shows Mama's card. A stranger saying "Mama sent me" gets nothing.

The 30 minutes is a deadline. Not sending him a third time is a circuit breaker. Tinned tomatoes are a fallback. The card is service authentication.

**Where the picture stops working.** The boy can see the queue and judge it. A service can't see inside the one it calls; it only sees how long answers take and how often they fail. So everything here is decided from those two numbers.

## Terms used in calling services safely
<!-- bite: 6b65f454-026a-4c57-b02a-dd0a3cb7ca24 -->

1. **Cascading failure**: This is when a problem in one service spreads to the services that call it, and then to the services that call *them*.
2. **Deadline**: This is the latest time a caller will wait for an answer. A **timeout** is the same idea written as a duration ("500 ms").
3. **Deadline propagation**: This is passing the remaining time on to the next call, so a service doesn't start work that its caller has already stopped waiting for.
4. **Retry storm**: This is when many callers retry at once, multiplying the load on a service that's already struggling.
5. **Jitter**: This is randomness added to retry waits, so callers don't all retry at the same instant.
6. **Circuit breaker**: This is a switch in the caller that stops calling a service for a while after too many failures, fails at once instead, and then tries again carefully.
7. **Fallback**: This is what you do instead when a call fails: a default, a cached answer, or "try later".
8. **Bulkhead**: This is a limit on how many calls to one service can be in progress at once, so one slow service can't take up every resource you have. (Named after the walls in a ship that stop one leak from sinking the whole ship.)
9. **Service identity**: This is proof of *which service* is calling, as opposed to which user.

## Step 1: why waiting is the enemy
<!-- bite: 9998a55c-6915-4fcf-bc41-4a1ea5a82cc8 -->

Every call that's waiting holds something: a slot in the consumer, memory, a database connection, a request that a user is waiting on. Waiting calls pile up faster than you'd think.

If a service gets 100 calls a second and each takes 5 ms, about **half a call** is in progress at any moment. If each takes 4 seconds, **400 calls** are in progress at once, each holding its resources. Same traffic, 800 times the resources, just from slowness. That's why a *slow* dependency is often worse than a *dead* one: a dead one fails quickly and frees everything; a slow one quietly holds it all.

So the rules come down to: **don't wait long, don't wait for things that won't come, and don't make it worse.**

## Step 2: deadlines everywhere, and passed on
<!-- bite: d1fbdc2c-ad33-4aa4-85b7-6c6f35a0bbd5 -->

Lesson 22 put a deadline on every gRPC call. Now make it a rule in one place, `notifications/src/clients/call.ts`:

```ts
import * as grpc from "@grpc/grpc-js";

export type CallOptions = { timeoutMs: number; metadata?: grpc.Metadata };

export function unary<Req, Res>(
  fn: (req: Req, metadata: grpc.Metadata, options: grpc.CallOptions, cb: (err: grpc.ServiceError | null, res: Res) => void) => void,
  req: Req,
  { timeoutMs, metadata = new grpc.Metadata() }: CallOptions,
): Promise<Res> {
  return new Promise((resolve, reject) => {
    fn(req, metadata, { deadline: Date.now() + timeoutMs }, (err, res) => (err ? reject(err) : resolve(res)));
  });
}
```

Every call goes through `unary`, and `timeoutMs` is required, so there's no way to forget it.

How long? Look at how long the call normally takes when things are healthy (lesson 27's metrics will tell you exactly), and set the deadline at a few times the slow end of normal. `GetContact` normally takes 5 ms, and on a bad day 50 ms; a 300 ms deadline gives it room without letting a sick API hold us for seconds.

**Pass the remaining time on.** Suppose the API's `GetContact` handler itself had to call a third service. If notifications gave it 300 ms and 250 have gone, the API should give the third service at most 50, not a fresh 300. Otherwise it does work nobody's waiting for. gRPC tells a server the caller's deadline (`call.getDeadline()`), and a gRPC call made inside a handler can take `{ parent: call }` in its options to inherit it. For HTTP, there's no standard, so services often send their deadline in a header and the next service honours it.

## Step 3: retry carefully, or not at all
<!-- bite: b7a128cb-be1c-48f7-aacb-0454d398dd76 -->

Retries fix brief blips: a restart, a dropped connection. They also cause retry storms. So every retry needs four answers:

1. **Is the call safe to repeat?** `GetContact` and `GetDish` only read, so yes. A call that *does* something (charge a card, send a text) is only safe to retry if it's idempotent, with a key, like lesson 15.
2. **Is the error worth retrying?** Only temporary ones: `UNAVAILABLE` (lesson 22 kept that code for exactly this). Never `NOT_FOUND`, `INVALID_ARGUMENT` or `PERMISSION_DENIED`: they'll fail the same way every time. Be careful with `DEADLINE_EXCEEDED`: the service was slow, and asking it again may only add load.
3. **How many times?** Few: two retries at most. Three layers each retrying three times means one failure becomes 27 calls at the bottom.
4. **How long to wait?** A little, growing, with jitter: 50 ms, then 100 ms, each plus a random amount.

`notifications/src/clients/retry.ts`:

```ts
import * as grpc from "@grpc/grpc-js";

const RETRYABLE = new Set([grpc.status.UNAVAILABLE, grpc.status.RESOURCE_EXHAUSTED]);

export async function withRetry<T>(attempt: () => Promise<T>, retries = 2, baseMs = 50): Promise<T> {
  for (let i = 0; ; i++) {
    try {
      return await attempt();
    } catch (err) {
      const code = (err as grpc.ServiceError).code;
      if (i >= retries || !RETRYABLE.has(code)) throw err;
      const wait = baseMs * 2 ** i;
      await new Promise((r) => setTimeout(r, wait + Math.random() * wait));
    }
  }
}
```

And remember the retries we *already* have. The notifications consumer doesn't ack a message whose handler failed, so the stream gives it back later (lesson 25). That's a slow, outer retry, minutes apart. So the inner retry only needs to cover a blip of a few hundred milliseconds. Two quick retries inside, the stream's slow retry outside, and nothing in between. Count your retries across all layers, every time you add one.

(gRPC can also do retries itself, configured per method in a "service config" given to the client. It's a fine alternative; writing it out here shows what it does.)

## Step 4: the circuit breaker
<!-- bite: 409ff59b-f51e-44ff-a88b-ba0badfc937d -->

Retries help with blips. When the API is properly down or struggling for minutes, every call still waits for its deadline and fails, and every one of them adds load. Better to notice, and **stop calling for a while**.

A circuit breaker has three states:

```text
     too many failures                 cool-down over
CLOSED ──────────────────► OPEN ──────────────────► HALF-OPEN
  ▲   (calls go through)    (calls fail at once)      (let one call try)
  │                                                     │
  └──────────── it worked ◄─────────────────────────────┤
                                 it failed: back to OPEN ┘
```

`notifications/src/clients/breaker.ts`:

```ts
export class CircuitOpenError extends Error {
  constructor(name: string) {
    super(`${name} is unavailable (circuit open)`);
    this.name = "CircuitOpenError";
  }
}

export function createBreaker(name: string, options = { failuresToOpen: 5, windowMs: 10_000, coolDownMs: 15_000 }) {
  let state: "closed" | "open" | "half-open" = "closed";
  let failures: number[] = [];       // times of recent failures
  let openedAt = 0;
  let trialInFlight = false;

  function recordFailure(now: number) {
    failures = failures.filter((t) => now - t < options.windowMs);
    failures.push(now);
    if (state === "half-open" || failures.length >= options.failuresToOpen) {
      state = "open";
      openedAt = now;
    }
  }

  return {
    get state() {
      return state;
    },
    async run<T>(work: () => Promise<T>): Promise<T> {
      const now = Date.now();
      if (state === "open") {
        if (now - openedAt < options.coolDownMs) throw new CircuitOpenError(name);
        state = "half-open";
      }
      if (state === "half-open") {
        if (trialInFlight) throw new CircuitOpenError(name);
        trialInFlight = true;
      }
      try {
        const result = await work();
        state = "closed";
        failures = [];
        return result;
      } catch (err) {
        recordFailure(Date.now());
        throw err;
      } finally {
        trialInFlight = false;
      }
    },
  };
}
```

In words:

1. **Closed** (normal): calls go through. Failures are counted over the last 10 seconds.
2. Five failures in 10 seconds: **open**. For 15 seconds, every call fails *at once* with `CircuitOpenError`, without touching the network. The API gets a rest, and notifications stops wasting its own time on calls that will fail.
3. After 15 seconds: **half-open**. Exactly one trial call goes through. If it works, back to closed. If not, open again for another 15 seconds.

Should *every* failure count? A `NOT_FOUND` means the API is working fine and answered "no such customer". Count only failures that say the service is unwell: `UNAVAILABLE`, `DEADLINE_EXCEEDED`, `INTERNAL`. (That's a small change to `run`, in the practice.)

There's a library for this, `opossum`, which adds events and statistics. The one above is small enough to understand completely, which is worth a lot when it's deciding whether your service calls another.

## Step 5: fallbacks, and putting it together
<!-- bite: 36c9c1fa-e866-479b-9acf-2f39eb8a2169 -->

When a call fails, after deadlines, retries and the breaker, what then? It depends on what the data is for:

1. **The dish name** in "Your jollof rice is ready". Nice to have. If `GetDish` fails, say "Your order 42 is ready". A slightly plainer message is better than a late one.
2. **The customer's phone number.** Essential: we can't send a text without it. No fallback: throw, don't ack, and let the stream retry in a few minutes.
3. **Cache what changes rarely.** Dish names change a few times a year. Keep them in notifications' memory for 10 minutes, and many messages won't call `GetDish` at all. Contact details change more and are personal, so don't keep them longer than one message needs.

`notifications/src/clients/menu.ts`:

```ts
export function createMenuClient(raw: MenuGrpcClient, auth: ServiceAuth) {
  const breaker = createBreaker("api.menu");
  const names = new Map<string, { name: string; until: number }>();

  return {
    async dishName(id: string): Promise<string | null> {
      const cached = names.get(id);
      if (cached && cached.until > Date.now()) return cached.name;
      try {
        const dish = await breaker.run(() =>
          withRetry(async () =>
            unary(raw.GetDish.bind(raw), { id }, { timeoutMs: 300, metadata: await auth.metadata("menu:read") }),
          ),
        );
        names.set(id, { name: dish.name, until: Date.now() + 10 * 60_000 });
        return dish.name;
      } catch {
        return null;            // the handler words the message without it
      }
    },
  };
}
```

The order matters: the **breaker outside, the retries inside**. One "call" to the breaker is a whole attempt, retries and all. If the retries were outside the breaker, a single message would count as three failures.

And the **customers client** is the same, without the fallback: on failure it throws, so the message waits in the stream.

**Bulkheads.** The consumer reads `COUNT 10` messages at a time and handles them one after another, so at most a handful of calls to the API are ever in flight from each copy. That's a bulkhead already. If one service ever calls several others in parallel, give each its own small limit (a counter of calls in progress, or a library like `p-limit`), so one slow dependency can't use up every slot.

## Step 6: who's calling?
<!-- bite: 4f415b67-6f38-45e9-8db2-58f85a797043 -->

Now the open door from lesson 25. `GetContact` returns personal data, and right now it trusts anyone who can reach port 50051. "It's on the internal network" isn't enough: one compromised container, one misconfigured firewall, one curious engineer, and every customer's phone number is readable.

The API needs to know **which service** is calling and **what it's allowed to do**. The same idea as users (lessons 12 and 13), for programs.

There are two common approaches, and production systems often use both:

1. **Mutual TLS (mTLS).** Each service has its own certificate. Both sides check the other's certificate when connecting, so the connection is encrypted *and* each side knows who the other is. Strong, but managing certificates is work; service meshes (like Istio or Linkerd) exist largely to do it for you.
2. **Signed service tokens.** Each service has its own private key. For each call, it sends a short-lived JWT, signed with that key, saying who it is and what it wants to do. The receiver checks the signature with that service's **public** key.

We'll do tokens, because they need nothing new to run and they carry *permissions*, not just identity. Then we'll turn on TLS for encryption.

**Notifications signs.** It has its own key pair (ES256), the private half in its config, never anywhere else:

```ts
// notifications/src/clients/service-auth.ts
import { SignJWT, importPKCS8 } from "jose";
import * as grpc from "@grpc/grpc-js";

export async function createServiceAuth(privateKeyPem: string) {
  const key = await importPKCS8(privateKeyPem, "ES256");
  const cache = new Map<string, { token: string; until: number }>();

  async function token(scope: string) {
    const hit = cache.get(scope);
    if (hit && hit.until > Date.now()) return hit.token;
    const signed = await new SignJWT({ scope })
      .setProtectedHeader({ alg: "ES256" })
      .setIssuer("notifications")
      .setSubject("service:notifications")
      .setAudience("mama-put-api")
      .setIssuedAt()
      .setExpirationTime("2m")
      .sign(key);
    cache.set(scope, { token: signed, until: Date.now() + 90_000 });   // reuse for 90 s of its 2 minutes
    return signed;
  }

  return {
    async metadata(scope: string) {
      const metadata = new grpc.Metadata();
      metadata.set("authorization", `Bearer ${await token(scope)}`);
      return metadata;
    },
  };
}
```

**The API checks.** It holds each calling service's **public** key, from config, `api/src/grpc/service-auth.ts`:

```ts
import { jwtVerify, importSPKI } from "jose";
import * as grpc from "@grpc/grpc-js";

type Caller = { service: string; scopes: Set<string> };

export async function createServiceAuthCheck(publicKeys: Record<string, string>) {
  const keys = new Map<string, Awaited<ReturnType<typeof importSPKI>>>();
  for (const [service, pem] of Object.entries(publicKeys)) keys.set(service, await importSPKI(pem, "ES256"));

  return async function requireService(call: grpc.ServerUnaryCall<unknown, unknown>, scope: string): Promise<Caller> {
    const header = String(call.metadata.get("authorization")[0] ?? "");
    const token = header.startsWith("Bearer ") ? header.slice(7) : "";
    const issuer = token ? decodeIssuer(token) : null;
    const key = issuer ? keys.get(issuer) : undefined;
    if (!key) throw grpcError(grpc.status.UNAUTHENTICATED, "service token required");

    try {
      const { payload } = await jwtVerify(token, key, { issuer, audience: "mama-put-api", algorithms: ["ES256"] });
      const scopes = new Set(String(payload.scope ?? "").split(" "));
      if (!scopes.has(scope)) throw grpcError(grpc.status.PERMISSION_DENIED, `needs ${scope}`);
      return { service: issuer!, scopes };
    } catch (err) {
      if ((err as { code?: number }).code === grpc.status.PERMISSION_DENIED) throw err;
      throw grpcError(grpc.status.UNAUTHENTICATED, "invalid service token");
    }
  };
}
```

(`decodeIssuer` reads the `iss` claim from the token *without* trusting it, using jose's `decodeJwt`, only to pick which public key to check with. The check itself is `jwtVerify`. `grpcError` builds the `{ code, details }` object from lesson 22.)

and at the top of each handler:

```ts
async GetContact(call, callback) {
  try {
    const caller = await requireService(call, "customers:read-contact");
    const contact = await customers.contactFor(caller, call.request.customerId);
    callback(null, contact);
  } catch (err) {
    callback(toGrpcError(err));
  }
},
```

What this gives us:

1. **Only services we know** (whose public key is in the API's config) can call at all.
2. **Each service only does what it's allowed.** Notifications has `customers:read-contact` and `menu:read`. A future reporting service might get `menu:read` only, and asking for a contact gives `PERMISSION_DENIED`.
3. **Tokens are short-lived** (2 minutes), so a stolen token is useless soon. They're signed fresh, and cached briefly so we don't sign one per call.
4. **The private key never leaves its service.** The API only has public keys, which can't sign anything. If the API were broken into, the attacker still couldn't pretend to be notifications.
5. **Audience again** (lesson 24): a token for `mama-put-api` can't be replayed at some other service.
6. **The caller is passed to the service**, like the user in lesson 13. `customers.contactFor(caller, ...)` can log "notifications read customer 7's contact", which is exactly the record you want when someone asks who has seen their data.

Generate a key pair once per service:

```bash
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out notifications-private.pem
openssl pkey -in notifications-private.pem -pubout -out notifications-public.pem
```

The private file goes into notifications' secrets (lesson 28); the public one into the API's config. Neither goes in git.

### Encrypting the traffic

Tokens prove who's calling, but with `createInsecure()` anyone who can watch the internal network can read the token and the contact details as they pass. In production, turn on TLS:

```ts
// API server
grpc.ServerCredentials.createSsl(caCert, [{ private_key: serverKey, cert_chain: serverCert }], false);

// notifications client
grpc.credentials.createSsl(caCert);
```

Setting the last argument of `createSsl` on the server to `true` also asks the client for *its* certificate, which is mutual TLS: then the connection itself proves which service is on the other end, and the token adds the permissions. Where certificates come from (your own small certificate authority, or a mesh that issues them automatically) is a deployment decision, and lesson 28 sets up the simplest version for Docker Compose.

## Step 7: the same habits for HTTP calls
<!-- bite: 5bb11a38-406c-42d7-a3c0-59aeb14d36b1 -->

Everything above applies to plain HTTP calls too, like lesson 17's calls to Paystack:

1. **Deadline**: `AbortSignal.timeout(10_000)` was already there.
2. **Retries**: only for safe calls. Paystack's `verify` is a read, so a retry is fine; `initialize` creates a transaction, so a blind retry could create two. Lesson 17 made each attempt use a new reference, so a retried `initialize` is a new attempt, not a double charge, and the old one simply expires unpaid.
3. **Circuit breaker**: wrap Paystack calls in one. When Paystack is down, `startCheckout` answers 502 at once ("payments are briefly unavailable") instead of making every customer wait 10 seconds for the same failure.
4. **Fallback**: there's no fallback for taking money. Fail fast and say so clearly.

## Step 8: testing failure on purpose
<!-- bite: 91d9650b-4b7d-44ab-8be3-a55ed05412c7 -->

These behaviours only show up when things go wrong, so tests must make things go wrong:

1. **Deadlines**: a fake gRPC server whose handler waits 1 second; a client with a 100 ms deadline must fail in about 100 ms.
2. **Retries**: a fake that returns `UNAVAILABLE` twice then succeeds gets three calls and a success; one that returns `NOT_FOUND` gets exactly one call.
3. **The breaker**: five failures open it; the sixth call fails without reaching the fake (count the fake's calls); after the cool-down (fake the clock with `mock.timers`), one trial call goes through.
4. **Fallback**: with `GetDish` failing, `order.ready` still produces a text, worded without the dish name.
5. **Auth**: no token gives `UNAUTHENTICATED`; a token signed with the wrong key, `UNAUTHENTICATED`; an expired one, `UNAUTHENTICATED`; a good token without `customers:read-contact`, `PERMISSION_DENIED`; a good token with it, the contact.
6. **The whole chain, by hand**: run both services, stop the API, pay for nothing (no events), then start it and pay. Then pause the API's process (`kill -STOP`) while notifications is handling messages, watch the breaker open in the logs, resume it (`kill -CONT`), and watch the breaker close and the messages go out.

## The TypeScript in this lesson
<!-- bite: cd08befb-dee5-4ea4-b2ad-1db73a41a036 -->

1. **`unary<Req, Res>(fn: (req: Req, metadata, options, cb) => void, req: Req, ...)`**: A generic helper taking *another function* as its first argument, with that function's exact shape written out. Every gRPC client method has this shape, so `unary` works for all of them, typed.
2. **`raw.GetDish.bind(raw)`**: Taking a method off an object loses its `this`. `bind(raw)` makes a copy of the function that always runs with `this` as `raw`, which gRPC clients need.
3. **`{ timeoutMs, metadata = new grpc.Metadata() }: CallOptions`**: Destructuring the options object in the parameter list, with a default for `metadata`.
4. **`for (let i = 0; ; i++)`**: A loop with no end condition. It ends only by `return` (success) or `throw` (giving up).
5. **`class CircuitOpenError extends Error`**: Our own error class, so callers can check `err instanceof CircuitOpenError`. (A class with ordinary fields and a constructor is fine with `erasableSyntaxOnly`; only some TypeScript-only class features, like `constructor(private x)` shorthand, are not.)
6. **`let state: "closed" | "open" | "half-open" = "closed"`**: A variable that can only hold one of those three words.
7. **`get state() { return state; }`**: A *getter*: `breaker.state` reads like a property but runs a function, so the outside can see the state without being able to change it.
8. **`failures.filter((t) => now - t < options.windowMs)`**: Keeps only the failures inside the window, so old failures stop counting.
9. **`new SignJWT({ scope }).setIssuer(...)...sign(key)`**: jose's builder: each method sets one part and returns the builder, so the calls chain. `sign` finishes it.
10. **`importPKCS8` / `importSPKI`**: Read a private key and a public key from PEM text (the `-----BEGIN ...` files openssl writes). `Awaited<ReturnType<typeof importSPKI>>` is "whatever key type `importSPKI` gives back, once its promise finishes", so our map's type follows the library's.
11. **`Record<string, string>`**: An object from service names to public key text, read from config.
12. **`(err as { code?: number }).code`**: Looking at a property on an error of unknown type, by saying what shape we expect it might have.

## Your project so far
<!-- bite: adbe77c1-92c3-47cc-99db-dc8e0aad9249 -->

```text
mama-put/
├── proto/ · contracts/
├── api/
│   ├── .env.example                      ← NEW: SERVICE_PUBLIC_KEYS (service → public key)
│   └── src/
│       ├── grpc/
│       │   ├── service-auth.ts           ← NEW: requireService(call, scope): signature, issuer, audience, scope
│       │   ├── customers.server.ts       ← GetContact requires customers:read-contact, passes the caller on
│       │   └── menu.server.ts            ← requires menu:read
│       ├── payments/paystack.ts          ← wrapped in a circuit breaker
│       └── ...
└── notifications/
    ├── .env.example                      ← NEW: SERVICE_PRIVATE_KEY, API_GRPC_URL
    └── src/
        ├── clients/
        │   ├── call.ts                   ← NEW: unary(): every call needs a timeout
        │   ├── retry.ts                  ← NEW: withRetry: UNAVAILABLE only, 2 retries, backoff + jitter
        │   ├── breaker.ts                ← NEW: closed / open / half-open
        │   ├── service-auth.ts           ← NEW: short-lived ES256 service tokens, cached per scope
        │   ├── menu.ts                   ← breaker(retry(call)), 10-minute name cache, null fallback
        │   └── customers.ts              ← breaker(retry(call)), no fallback: throw and let the stream retry
        ├── handlers.ts                   ← words messages without the dish name when it's missing
        └── *.test.ts                     ← NEW: deadlines, retries, breaker, fallback, auth
```

## Common mistakes
<!-- bite: a09221f0-aafa-4af3-aeb2-0230527f0264 -->

1. **No deadline.** One slow service holds every caller's resources until everything stops.
2. **Retrying everything.** `NOT_FOUND` retried three times is three wasted calls. Retry temporary errors only.
3. **Retries at every layer.** They multiply. Count them all.
4. **Retrying without backoff or jitter.** Everyone retries together and knocks the service over again.
5. **Retrying calls that change things, without a key.** Double texts, double charges.
6. **Retries outside the breaker.** One attempt counts as several failures.
7. **No fallback, or a fallback that lies.** "Order ready" with the wrong dish is worse than no dish name.
8. **Trusting the internal network.** Every service should prove who it is, and only get the permissions it needs.
9. **Long-lived service tokens, or one shared secret for every service.** One leak and everything is open. Per-service keys, short tokens.
10. **Never testing failure.** These paths only run on your worst day. Make them run in tests.

## Check your understanding
<!-- bite: 6fbc8ed5-ba47-48f1-9a20-8ffbc5684185 -->

1. The API's `GetContact` goes from 5 ms to 4 s. Why can that hurt the API's *own* customers, through notifications?
2. Which of these should notifications retry: `UNAVAILABLE`, `NOT_FOUND`, `PERMISSION_DENIED`?
3. Why is the circuit breaker outside the retries and not inside?
4. The breaker is open. A message arrives that needs the customer's phone number. What happens to it?
5. Why does the API hold notifications' *public* key, and not a shared secret?
6. A token for `customers:read-contact` is stolen from the network. What limits the damage?

<details>
<summary>Answers, after your attempt</summary>

1. Without deadlines, notifications' calls wait the full 4 s each, and its retries add more calls on top. The API, already slow, gets more load, and since orders share the API's database and CPU, customers' requests slow down and time out too. A cascading failure.
2. Only `UNAVAILABLE`, which means "temporary". `NOT_FOUND` and `PERMISSION_DENIED` will give the same answer every time.
3. So that one attempt (with its retries) counts as one success or one failure for the breaker. With retries outside, every single attempt would count, and the breaker would open three times too quickly.
4. The customers client throws `CircuitOpenError` at once without calling the API. The handler fails, the message isn't acked, and the stream gives it back later. By then the breaker has probably closed, and the text goes out, a bit late.
5. A public key can only *check* signatures, not make them. If the API were broken into, the attacker couldn't use what it holds to pretend to be notifications. With a shared secret, the API's copy could sign too.
6. It's only valid for 2 minutes, only for the audience `mama-put-api`, and only for that one scope. With TLS on, it can't be read off the network in the first place. And every use is logged with the caller, so misuse can be seen.

</details>

## Practice
<!-- bite: cec34649-032b-4933-9ce2-da2ed5515ead -->

1. Make the breaker count only "service is unwell" errors (`UNAVAILABLE`, `DEADLINE_EXCEEDED`, `INTERNAL`, and `CircuitOpenError` never), and test it.
2. Write `customers.ts` with breaker, retries and no fallback.
3. Add service auth to every gRPC handler in the API, with scopes, and a test for each outcome in step 8.
4. Wrap the Paystack client in a breaker, and make `startCheckout` give a clear `payments-unavailable` error when it's open.
5. Log each breaker state change ("api.menu: closed → open") so lesson 27 can alert on it.
6. Do the `kill -STOP` exercise from step 8 and write down what the logs showed.

**Done when** pausing the API for a minute makes notifications' breaker open within seconds (and its logs show calls failing at once, not after 300 ms each), resuming the API closes it and every waiting message is sent; texts still go out worded without the dish name when only `GetDish` fails; and `grpcurl` without a service token gets `UNAUTHENTICATED` from every API method.

## Before moving on
<!-- bite: 6a882bbe-edd0-4a2c-8d83-2643aa18a7f6 -->

Mama Put's services now call each other the way good neighbours borrow sugar: they ask briefly, don't keep knocking when nobody answers, manage without when they can, and always say who they are.

But look at the last few lessons' "Done when" lines: "watch the logs", "the logs show", "check the breaker opened". Right now, the logs are `console.log` lines in three terminals, each service's separate, with no way to follow one customer's order from the webhook, through the outbox and the stream, into notifications and back to the API over gRPC. When something goes wrong at lunch, how would you even find out, let alone find *where*? That's observability: logs you can search, metrics you can graph and alert on, and traces that follow one request across every service. Part 7 starts there.

## Related
<!-- bite: 66017b40-7083-4312-af3d-c561db0a8674 -->

- [[backend/frameworks/express/27-observability|Next: Observability]]
- [[backend/frameworks/express/22-grpc|gRPC]] — deadlines and status codes, where they started
- [[backend/frameworks/express/15-idempotency|Idempotency]] — what makes a retry of a write safe
- [[backend/frameworks/express/24-mcp-in-production|MCP in Production]] — tokens with audiences and scopes, for people instead of services

## About this lesson
<!-- bite: d156d301-3284-47f1-8556-97cd2ee84f81 -->

**Level:** Advanced. Lesson 26 of [[backend/frameworks/express/index|Express]]. Covers cascading failures and why slow dependencies are worse than dead ones, deadlines on every call through one helper and passing the remaining time on, when and how to retry (safe operations, temporary errors, few attempts, backoff and jitter, counting retries across layers), a circuit breaker with closed, open and half-open states, fallbacks and caller-side caching, bulkheads, service identity with short-lived ES256 tokens signed by each service and checked with public keys, scopes per service, audience, passing the calling service on for auditing, TLS and mutual TLS for gRPC, the same habits for HTTP calls to Paystack, and testing deadlines, retries, the breaker, fallbacks and service auth by making failures happen.
