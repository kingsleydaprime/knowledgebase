---
id: 141124ed-1497-4eb1-878b-6f1c25fc12f3
---

# Caching with Redis

**A cache is a place where you keep a copy of an answer you've already worked out, so the next person who asks the same question gets the copy, quickly, instead of you working it out again.** Mama Put's menu is asked for hundreds of times a minute at lunch, and it changes a few times a day. Asking Postgres every single time is like Mama walking to the market to check prices for every customer, when she could just write them on a board.

## Before you start
<!-- bite: 201f2c81-95bd-4113-9b6c-0dcbe0dd8bf1 -->

You should have Redis running and the background jobs from [[backend/frameworks/express/18-background-jobs|lesson 18]].

After this lesson you will be able to:

1. Decide what's worth caching, and how stale each thing is allowed to be.
2. Run a second Redis set up for caching, and say why it can't share the queue's settings.
3. Write a cache-aside helper, and cache the menu at the right layer.
4. Keep the cache honest when the menu changes, with generation numbers.
5. Stop a stampede when a popular key expires, and keep working when Redis is down.
6. Use HTTP caching (`Cache-Control`, `ETag`) so phones don't even ask, and move the rate limits from lesson 14 into Redis.

## Where we stopped
<!-- bite: 4a1ecbe1-cbf8-4968-aa0c-a17c9f5d730e -->

Count the menu requests. Every phone that opens the app asks for `GET /v2/menu`. Each time, Postgres reads the dishes, counts them for `meta.total`, sorts them, and we turn them into JSON. At 12:30, with a few hundred customers looking, that's the same query, with the same answer, hundreds of times a minute.

Postgres can handle it today. But it's work for nothing, it makes every other query (placing orders, which matter more) wait in line behind it, and the day Mama is featured on a food blog, it won't handle it.

## The kid version
<!-- bite: 590c2a50-56b3-48f3-80f7-2e5b0d676892 -->

Ada asks Mama "how much is jollof?". Mama checks her notebook: ₦1,500. Bayo asks the same. Mama checks the notebook again. Then Chidi.

So Mama writes the prices on a board by the counter. Now nobody asks her; they read the board.

But when Mama changes the price of jollof, she must remember to change the board. If she forgets, the board lies.

The board is the cache. Rubbing it out and writing it again is **invalidation**, and forgetting to do that is the bug every cache has at least once.

**Where the picture stops working.** Mama's board shows one thing for everyone. Our cache must be careful when different people should see different answers (staff see more than customers). Copy the wrong person's answer, and Ada sees things only staff should.

## Terms used in caching
<!-- bite: e431c31c-8c64-4fdf-a1f9-e51ac2dffb66 -->

1. **Cache hit** and **cache miss**: A hit means the answer was in the cache. A miss means it wasn't, so we work it out and usually store it.
2. **TTL (time to live)**: This is how long a cached copy is kept before Redis deletes it by itself.
3. **Stale**: A cached copy is stale when the real answer has changed but the copy hasn't.
4. **Invalidation**: This is removing or replacing a cached copy because the real data changed.
5. **Cache-aside**: This is the most common way to cache: look in the cache; on a miss, read the database, store the result in the cache, return it. The app manages the cache; the database doesn't know it exists.
6. **Stampede**: This is when a popular cached copy expires and many requests miss at the same moment, all running the same expensive query together.
7. **Eviction**: This is Redis deleting keys to make room when its memory is full.
8. **HTTP caching**: This is caching done by the client or a proxy, guided by headers like `Cache-Control` and `ETag`, so some requests never reach us at all.

## Step 1: what to cache, and how stale is OK
<!-- bite: 8de1e895-7ed5-4e99-be3c-78fba32fbad0 -->

A cache is a deliberate lie: "this is the answer", when really it's "this *was* the answer a few seconds ago". So the question for each thing is: **how old an answer can we live with?**

| Data | Read often? | Changes | Can be stale for | Cache? |
|---|---|---|---|---|
| Dish names, prices, photos | Very | A few times a day | Seconds, if edits clear it | Yes |
| `portionsLeft` | Very | Every order | ~10 seconds | Yes, with a short TTL |
| One customer's orders | A little | Often | Not at all | No |
| An order's payment status | Sometimes | Once | Not at all | No |
| The OpenAPI spec | Rarely | Every deploy | Until the next deploy | In memory, not Redis |

The tricky one is `portionsLeft`. It changes every time someone orders. If the cache says "3 left" when really there's 1, is that dangerous?

No, and the reason is important. **The cache can show an old number; the order can't use one.** Placing an order runs lesson 8's conditional `UPDATE ... WHERE portions_left >= $2` on the real database. If the cached menu said 3 and there's really 1, Ada's order for 2 is refused correctly, with "not enough portions". The cache is for *looking*, the database is for *deciding*. Never let a cached value make a decision that matters, like "is this allowed" or "is there enough".

So: cache the menu, with a short TTL (10 seconds), and clear it straight away when staff edit a dish. Orders aren't cached at all.

## Step 2: a second Redis, for the cache
<!-- bite: 131c9c17-4060-413c-9bc3-498dfaf23e2b -->

Lesson 18 set the queue's Redis to `noeviction`: when memory is full, refuse new data, never delete old. That's right for jobs and wrong for a cache. A cache that's full *should* throw away the least-used copies; they can always be worked out again.

One Redis server has one eviction policy. So the cache gets its own:

```bash
docker run -d --name mama-put-cache -p 6380:6379 redis:7 \
  redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru --save ""
```

1. **`--maxmemory 128mb`**: never use more than this.
2. **`--maxmemory-policy allkeys-lru`**: when full, delete the **l**east **r**ecently **u**sed keys.
3. **`--save ""`**: don't write to disk. If the cache restarts empty, that's fine; it fills up again in a few seconds.

In `.env`:

```text
CACHE_REDIS_URL=redis://localhost:6380
```

That's the general rule: **keep things you can't lose apart from things you can.** Queues and rate-limit counters in one Redis; cached copies in another.

## Step 3: a cache-aside helper
<!-- bite: 68d5db43-56af-48de-8dd4-b487bcd5b7bb -->

`src/shared/cache.ts`:

```ts
import { Redis } from "ioredis";

export type Cache = {
  getOrLoad<T>(key: string, ttlSeconds: number, load: () => Promise<T>): Promise<T>;
  generation(namespace: string): Promise<number>;
  bump(namespace: string): Promise<void>;
};

export function createRedisCache(url: string, log: (m: string, d: object) => void): Cache {
  const redis = new Redis(url, {
    commandTimeout: 200,        // a cache that's slow is worse than no cache
    maxRetriesPerRequest: 1,
    enableOfflineQueue: false,  // if Redis is down, fail at once instead of queueing commands
  });
  redis.on("error", (err) => log("cache redis error", { error: err.message }));

  const inFlight = new Map<string, Promise<unknown>>();

  async function read(key: string): Promise<string | null> {
    try {
      return await redis.get(key);
    } catch (err) {
      log("cache read failed, using the database", { key, error: (err as Error).message });
      return null;
    }
  }

  async function write(key: string, value: string, ttlSeconds: number) {
    const jitter = Math.floor(Math.random() * Math.max(1, ttlSeconds / 10));
    await redis.set(key, value, "EX", ttlSeconds + jitter).catch(() => {});
  }

  return {
    async getOrLoad<T>(key: string, ttlSeconds: number, load: () => Promise<T>): Promise<T> {
      const hit = await read(key);
      if (hit !== null) return JSON.parse(hit) as T;

      // Someone in THIS process is already loading it? Wait for theirs.
      const pending = inFlight.get(key);
      if (pending) return pending as Promise<T>;

      const loading = (async () => {
        try {
          const value = await load();
          await write(key, JSON.stringify(value), ttlSeconds);
          return value;
        } finally {
          inFlight.delete(key);
        }
      })();
      inFlight.set(key, loading);
      return loading;
    },

    async generation(namespace) {
      const value = await read(`gen:${namespace}`);
      return value === null ? 0 : Number(value);
    },

    async bump(namespace) {
      await redis.incr(`gen:${namespace}`).catch((err) =>
        log("cache bump FAILED, stale data possible until TTL", { namespace, error: err.message }),
      );
    },
  };
}
```

Three protections are built in, each for a real failure.

**1. Redis down means slower, not broken.** If a read fails, `read` logs it and returns `null`, which counts as a miss, so we go to Postgres. If a write fails, we ignore it. `commandTimeout: 200` means a struggling Redis costs at most 200 ms, not a hung request. `enableOfflineQueue: false` stops ioredis from saving up commands while disconnected and then sending a flood when it reconnects. A cache must **fail open**: the app works without it, just slower. (Compare the queue Redis from lesson 18, which must *not* fail open: a lost job is lost work.)

**2. A stampede becomes one query.** Picture 12:30. The menu's copy expires. In the next 50 milliseconds, 200 requests miss. Without care, that's 200 identical queries hitting Postgres at once, at its busiest moment. `inFlight` is a map of "loads in progress": the first request starts the load and stores its promise; the next 199 find the promise and wait for the same answer. One query instead of 200. (This is per process. With three servers, at most three queries, which is fine.)

**3. Jitter spreads out expiry.** If you cache 50 things at the same moment with the same TTL, they all expire at the same moment too, and you get 50 misses together. A random extra second or so, `jitter`, spreads them out.

## Step 4: cache at the right layer
<!-- bite: 434a71a6-b4d4-46af-b946-701d63905288 -->

Where does the cache go? Not around the whole HTTP response. Remember who sees what: staff see `portionsLeft` and internal fields customers don't (lesson 13), and v1 and v2 have different shapes (lesson 10). Cache whole responses, and one day a staff member's response lands in the cache and every customer sees it.

So we cache the **data**, in the menu service, and let the presenters (which know about versions and roles) run *after* the cache, on every request:

```text
request → route → presenter(v2, actor) ← menu service → cache → repository → Postgres
                                          ↑ cached here: the same rows for everyone
```

In `src/menu/menu.service.ts`:

```ts
import { createHash } from "node:crypto";

const MENU_TTL = 10;

function keyFor(generation: number, query: DishQuery) {
  const hash = createHash("sha256").update(JSON.stringify(query)).digest("base64url").slice(0, 16);
  return `menu:${generation}:list:${hash}`;
}

export function createMenuService({ menuRepository, cache }: { menuRepository: MenuRepository; cache: Cache }) {
  return {
    async list(query: DishQuery) {
      const generation = await cache.generation("menu");
      return cache.getOrLoad(keyFor(generation, query), MENU_TTL, () => menuRepository.list(query));
    },

    async get(id: string) {
      const generation = await cache.generation("menu");
      const dish = await cache.getOrLoad(`menu:${generation}:dish:${id}`, MENU_TTL, () => menuRepository.findById(id));
      if (!dish) throw notFound("Dish", id);
      return dish;
    },

    async create(actor: AuthUser, input: NewDish) {
      // ...permission check as before
      const dish = await menuRepository.create(input);
      await cache.bump("menu");
      return dish;
    },
    // update, remove, setPhoto, setProcessedPhoto: the same, bump after the write
  };
}
```

`query` is the validated listing query from lesson 9: page or cursor, filters, search, sort. Each different query is a different answer, so each gets its own key. Turning the whole query into a short hash keeps keys a sensible length. And because `query` has already passed through zod, there's a limited set of shapes. Never build cache keys from raw, unvalidated input: an attacker sending a million random query strings fills your cache with a million useless keys and pushes out the useful ones.

What isn't cached: anything with `fields=` (lesson 9's field selection) is fine, because the presenter picks fields after the cache. But nothing about *who* is asking goes in the key, and nothing about who is asking comes out of the repository. If a query ever depended on the actor (say, "dishes I've favourited"), it would either include the user id in the key or, better, not be cached in this shared way at all.

## Step 5: keeping it honest, with generations
<!-- bite: 7eb6e493-6f4b-452c-abf9-ef9e2fa81d91 -->

Now the hard part, the one in the famous joke ("there are only two hard things in computer science: cache invalidation and naming things").

When Mama changes the price of jollof, which keys must go? `menu:…:dish:1`, obviously. But also *every* list that contains jollof: page 1, page 1 sorted by price, the search for "rice", the filter for "under ₦2,000"... We don't know which of those exist, and searching Redis for them (`KEYS menu:*`) is slow and blocks Redis for everyone while it runs.

So we don't find them. We make them unreachable. Every menu key starts with a **generation number**: `menu:7:list:...`. When anything on the menu changes, `bump("menu")` adds one to the generation. Now every request builds keys starting `menu:8:`, which don't exist yet, so they miss and load fresh data. The old `menu:7:` keys are never read again, and quietly expire within 10 seconds (or get evicted, because nobody uses them).

One `INCR`, and the whole menu cache is new. It costs one extra tiny Redis read per request (the generation), which is worth it.

The order of things in `create` matters: **write to the database first, then bump.** Bump first, and a request in between could load the *old* data under the *new* generation and keep it for 10 seconds.

And what if the bump fails, because the cache Redis is down at that moment? The old data stays until its TTL runs out: at most 10 seconds of stale menu. That's why the TTL exists even though we invalidate: it's the backstop that limits how wrong the cache can ever be. **Always set a TTL**, even on things you invalidate by hand.

Placing an order changes `portionsLeft` but doesn't bump the generation. That's the choice from step 1: at lunch, bumping on every order would empty the cache every few seconds, and the cache would do nothing. Ten seconds of slightly old portion counts is the price, and the conditional `UPDATE` makes it safe to pay.

Lesson 18's worker sets processed photos, so it bumps too. The worker builds the cache the same way, from `CACHE_REDIS_URL`.

## Step 6: HTTP caching, so phones don't even ask
<!-- bite: ffb53f73-8c2e-4c70-814a-e155fd246aeb -->

Redis saves Postgres the work. HTTP caching can save the *request*.

**`ETag` and 304.** Express already gives every `res.json` response an `ETag` header: a short fingerprint of the body. When the phone asks again, it sends `If-None-Match: <that fingerprint>`. If the new body has the same fingerprint, Express answers **304 Not Modified** with no body. The phone uses the copy it has. On a slow mobile connection, sending 200 bytes of headers instead of 20 KB of menu is a real difference.

Try it:

```bash
curl -i http://localhost:3000/v2/menu
# ETag: W/"1a3f-..."
curl -i http://localhost:3000/v2/menu -H 'If-None-Match: W/"1a3f-..."'
# HTTP/1.1 304 Not Modified
```

(Express still builds the response to work out the fingerprint, so this saves bandwidth, not our work. Redis is what saves our work.)

**`Cache-Control`** tells clients and proxies how long they may reuse a response without asking at all:

```ts
router.get("/", async (req, res) => {
  // ...
  res.set("Cache-Control", req.user ? "private, max-age=0, must-revalidate" : "public, max-age=10");
  res.json({ data, meta });
});
```

1. **`public, max-age=10`** for logged-out visitors: anyone (the phone, a CDN in front of us) can reuse this for 10 seconds.
2. **`private`** when someone is logged in, because staff responses contain more. `private` means "only this person's own device may keep it", never a shared proxy.

And for anything personal (orders, payments, `/auth`), send `Cache-Control: no-store`. A shared computer at a cyber café shouldn't keep Ada's order history on its disk. A small middleware on those routers does it once.

## Step 7: rate limits, shared at last
<!-- bite: 03a3921e-6863-4dbb-a9fc-2e210aa931a4 -->

Lesson 14 left a known weakness: the rate-limit counts live in each server's memory, so three servers means triple the limit, and a restart resets everyone. Now that Redis is running:

```bash
npm install rate-limit-redis
```

```ts
// src/shared/rate-limits.ts
import { RedisStore } from "rate-limit-redis";
import type { Redis } from "ioredis";

export function createRateLimits(redis: Redis) {
  const store = (prefix: string) =>
    new RedisStore({
      prefix: `rl:${prefix}:`,
      sendCommand: (command: string, ...args: string[]) => redis.call(command, ...args) as never,
    });

  return {
    generalLimit: rateLimit({ /* ...as in lesson 14 */ store: store("general") }),
    loginLimit: rateLimit({ /* ...as in lesson 14 */ store: store("login") }),
  };
}
```

Which Redis? The **queue** one, from lesson 18, not the cache. Rate-limit counters must not be evicted to make room: evict Ada's attacker's counter and they get a fresh five guesses. They expire on their own when their window ends, so they don't pile up.

`createRateLimits` takes the Redis client from `server.ts`, like every other dependency, instead of making its own. Tests pass in a fake, or use the default memory store.

## Step 8: testing the cache
<!-- bite: 16c658b7-c083-4110-ab2d-ee594a20d0f3 -->

1. **An in-memory `Cache`** for the fast tests: a `Map` with the same three methods, and TTLs that tests can ignore. Most HTTP tests should behave the same with or without a cache, which is itself a good test.
2. **The invalidation test**, the one that matters most:

```ts
it("shows the new price straight after staff change it", async () => {
  const { app, login } = await buildTestApp({ cache: "memory" });
  const { token } = await login("staff");

  const before = await request(app).get("/v2/menu/1");
  await request(app).patch("/v2/menu/1").set("Authorization", `Bearer ${token}`).send({ price: { amount: 200000, currency: "NGN" } });
  const after = await request(app).get("/v2/menu/1");

  assert.notEqual(before.body.data.price.amount, after.body.data.price.amount);
  assert.equal(after.body.data.price.amount, 200000);
});
```

3. **The "Redis is down" test**: build the app with a cache whose every method throws, and check `GET /v2/menu` still answers 200. That's the fail-open promise, checked.
4. **The stampede test**: a fake repository that counts calls and takes 50 ms; fire 20 `list` calls at once; check the repository ran **once**.

## The TypeScript in this lesson
<!-- bite: 0cd1dc93-cd1e-43e0-8a18-c428b3ef178a -->

1. **`getOrLoad<T>(key: string, ttlSeconds: number, load: () => Promise<T>): Promise<T>`**: A generic method. Whatever type `load` gives, `getOrLoad` gives back the same, so `cache.getOrLoad(..., () => menuRepository.findById(id))` returns `Promise<Dish | null>` without any casting at the call site.
2. **`JSON.parse(hit) as T`**: `JSON.parse` returns `any`. `as T` says "trust me, it's the same shape we stored". It's a promise TypeScript can't check, which is why only `getOrLoad` writes and reads these keys.
3. **`new Map<string, Promise<unknown>>()`**: A map from keys to promises. `unknown` because different keys hold different types; the `as Promise<T>` on the way out matches what that key stores.
4. **`(async () => { ... })()`**: An async arrow function, called immediately. It gives us a promise we can store in `inFlight` *before* it finishes, which is the whole trick.
5. **`try { ... } finally { inFlight.delete(key) }`**: `finally` runs whether the load succeeds or throws, so a failed load never leaves a stuck promise in the map.
6. **`.catch(() => {})`**: Ignores a failed promise. Only for things that truly don't matter, like a cache write.
7. **`redis.set(key, value, "EX", seconds)`**: Not TypeScript but worth reading: `EX` sets the TTL in seconds in the same command, so a key can never exist without one.
8. **`` `menu:${generation}:list:${hash}` ``**: A template string building a structured key. The `:` separators are a Redis habit, so keys read like paths.
9. **`.digest("base64url").slice(0, 16)`**: The hash as URL-safe text, cut to 16 characters. That's still 96 bits, more than enough to tell queries apart.
10. **`sendCommand: (command: string, ...args: string[]) => redis.call(command, ...args) as never`**: rate-limit-redis works with any Redis client; you give it a function that sends a raw command. `...args` collects the rest of the arguments. `as never` quiets a mismatch between the two libraries' return types; it's safe because the library only uses the reply as data.

## Your project so far
<!-- bite: f6e6abed-da14-426e-b935-24817255f21e -->

```text
mama-put-api/
├── .env · .env.example           ← NEW: CACHE_REDIS_URL (port 6380)
├── package.json                  ← NEW: rate-limit-redis
├── migrations/   001 … 013
├── uploads/photos/ · openapi/ · test/integration/
└── src/
    ├── server.ts                 ← builds the cache and passes the queue Redis to the rate limits
    ├── worker.ts                 ← builds the cache too, so processed photos bump the menu
    ├── shared/
    │   ├── cache.ts              ← NEW: getOrLoad (fail open, single-flight, jitter), generation, bump
    │   ├── cache.memory.ts       ← NEW: the Map-based cache for tests
    │   ├── no-store.ts           ← NEW: Cache-Control: no-store for personal routes
    │   └── rate-limits.ts        ← createRateLimits(redis) with RedisStore
    ├── menu/
    │   ├── menu.service.ts       ← list and get go through the cache; every write bumps "menu"
    │   ├── menu.routes.ts        ← Cache-Control: public for visitors, private for logged-in
    │   └── menu.cache.test.ts    ← NEW: new price after edit, Redis down, stampede
    └── jobs/ · payments/ · webhooks/ · orders/ · auth/ · admin/ · docs/ · db/ · types/ · test-support/
```

## Common mistakes
<!-- bite: cb153831-a4f5-44d4-b7ac-5f2f2e6bfe06 -->

1. **Caching whole responses that depend on who's asking.** Staff data reaches customers. Cache the shared data and present it per request.
2. **Letting a cached value make a decision.** "Cache says 3 portions, so allow it." The database decides; the cache only shows.
3. **No TTL.** If one invalidation is ever missed, the data is wrong forever.
4. **Invalidating before writing.** A request in between re-caches old data. Write, then bump.
5. **Finding keys with `KEYS`.** It blocks Redis while it scans every key. Use generations (or delete exact keys you know).
6. **A cache that breaks the app when it's down.** Short timeouts, no offline queue, catch and fall through to the database.
7. **Cache and queue in the same Redis.** One eviction policy can't suit both.
8. **Cache keys from raw input.** Validate first, or attackers fill your cache with junk.
9. **`public` on responses for logged-in users**, or caching personal data at all. Use `private` or `no-store`.

## Check your understanding
<!-- bite: d561cb10-ee6c-4350-9a00-763bc9893736 -->

1. The cache says jollof has 2 portions left; really it has 0. Ada orders 1. What happens, and why is it safe?
2. Why does the cache need a separate Redis from the queue?
3. Mama changes the price of jollof. Which cache keys get deleted?
4. 300 requests miss the menu key at the same moment, spread over 3 servers. How many Postgres queries run?
5. The cache Redis goes down at 12:30. What do customers notice?
6. Why do we bump *after* writing to Postgres, not before?

<details>
<summary>Answers, after your attempt</summary>

1. She sees "2 left", taps order, and the conditional `UPDATE` on the real `portions_left` finds 0 and updates nothing, so she gets `not-enough-portions`. A bit disappointing, but correct: the cache only affected what she *saw*, never what was *allowed*.
2. A queue must never lose data, so its Redis uses `noeviction` and writes to disk. A cache should throw away old copies when full (`allkeys-lru`) and doesn't need the disk. One Redis server can only have one eviction policy.
3. None, directly. `bump("menu")` increases the generation, so every new request builds new keys and the old ones are simply never read again. They expire within the TTL.
4. At most three: one per server, thanks to the `inFlight` map. The other 297 wait for their server's single load.
5. Almost nothing, maybe slightly slower menus. Reads fail within 200 ms and fall through to Postgres; writes are ignored. The app works without the cache. (Postgres gets busier, so it's worth an alert, which lesson 27 adds.)
6. If we bumped first, a request arriving between the bump and the write would miss the new generation's key, load the *old* data from Postgres, and cache it under the *new* generation, where it would stay for the whole TTL.

</details>

## Practice
<!-- bite: 4b98f86b-e090-45c0-a962-c671be71aab2 -->

1. Write `cache.memory.ts` and the four tests from step 8.
2. Add `bump("menu")` to every menu write, including `setPhoto` and the worker's `setProcessedPhoto`. Write a test for each.
3. Add the `no-store` middleware to the orders, payments and auth routers, and a test that checks the header.
4. Cache the OpenAPI JSON from lesson 11 in memory: build it once at start-up, not on every request.
5. Add a counter of cache hits and misses (a simple object with two numbers is fine for now) and show it in `GET /v2/admin/queues`. Lesson 27 turns it into a real metric.

**Done when** `GET /v2/menu` hits Postgres at most once every 10 seconds under repeated requests (check with Postgres's logs or the counter), a staff edit shows on the very next request, stopping the cache container leaves the menu working, a repeated request with `If-None-Match` gets 304, and the login rate limit holds across two copies of the server running on different ports.

## Before moving on
<!-- bite: fc38fd98-b043-4944-8d38-5419a618b304 -->

The menu now comes from memory in a millisecond, stays honest when Mama edits it, survives the cache dying, and doesn't stampede at lunch. The rate limits are finally shared between servers.

But look at the kitchen. The cooks still have to *refresh* their screen to see new orders. In a lunch rush, a paid order can sit unseen for a minute because nobody pressed refresh. Caching made reads faster. The kitchen doesn't want faster reads; it wants to be **told** the moment something changes. That's real-time updates, next.

## Related
<!-- bite: c9fdb0e9-314f-432c-9081-acf97a70efd1 -->

- [[backend/frameworks/express/20-real-time|Next: Real-time Updates]]
- [[backend/frameworks/express/09-listing|Pagination, Filtering, Searching, Sorting and Field Selection]] — the queries whose answers we now cache
- [[backend/frameworks/express/14-security|Security]] — where the rate limits started
- [[backend/frameworks/express/18-background-jobs|Background Jobs and Queues]] — the other Redis, and why it's set up differently

## About this lesson
<!-- bite: b2b4fd5c-cb54-4e20-8ec3-7dab6590edcf -->

**Level:** Intermediate → Advanced. Lesson 19 of [[backend/frameworks/express/index|Express]]. Covers deciding what to cache and how stale each thing may be, why a cached value must never make a decision, a separate Redis for caching with `allkeys-lru` and no persistence, a cache-aside helper that fails open with short timeouts, prevents stampedes with single-flight loading and spreads expiry with jitter, caching data below the presenters so roles and versions stay correct, cache keys from validated queries, invalidation by generation numbers instead of finding keys, writing before invalidating, TTLs as the backstop, `ETag` and 304, `Cache-Control` public, private and no-store, rate limits in Redis with `rate-limit-redis`, and testing invalidation, failure and stampedes.
