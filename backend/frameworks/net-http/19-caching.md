---
id: 5da6b177-4ba4-467b-a1ba-77132e0cdd3d
---

# Caching with Redis

**A cache is a place to keep a copy of an answer you've already worked out, so the next person who asks gets the copy instead of making you work it out again.** The menu that every phone asks for at lunchtime is the same forty dishes each time; a cache turns hundreds of identical database queries into one. The hard part isn't keeping copies. It's knowing when a copy has become wrong.

## Before you start
<!-- bite: cfe0e332-216d-4764-a065-164a5b0c5199 -->

You should have:

1. Finished [[backend/frameworks/net-http/18-background-jobs|lesson 18]], with Redis running for the queue.
2. Met lesson 9's `ListQuery`, lesson 13's role-based views, and lesson 14's rate limiter.

After this lesson you will be able to:

1. Decide what to cache, for how long, and what must never be decided from a cached value.
2. Run a second Redis set up as a cache, and talk to it with go-redis, so a slow or broken cache only makes the app slower, never broken.
3. Write a cache-aside helper that turns a stampede into one query with `singleflight`.
4. Cache at the right layer, and clear a whole family of keys at once with a generation number.
5. Send `ETag` and `Cache-Control`, so phones sometimes don't even need the body, and share rate-limit counts across servers in Redis.

## Where we stopped
<!-- bite: 83a4ffae-4017-458f-aafc-0582434ea288 -->

Count the menu requests. Every phone that opens the app asks for `GET /v2/menu`. Each time, Postgres reads the dishes, counts them for `meta.total`, sorts them, and we turn them into JSON. At 12:30, with a few hundred customers looking, that's the same query, with the same answer, hundreds of times a minute.

Postgres can handle it today. But it's work for nothing, it makes every other query (placing orders, which matter more) wait in line behind it, and the day Mama is featured on a food blog, it won't handle it.

## The kid version
<!-- bite: da183bd8-bd24-4f67-95ea-c5fe8f78c6f5 -->

Ada asks Mama "how much is jollof?". Mama checks her notebook: ₦1,500. Bayo asks the same. Mama checks the notebook again. Then Chidi.

So Mama writes the prices on a board by the counter. Now nobody asks her; they read the board.

But when Mama changes the price of jollof, she must remember to change the board. If she forgets, the board lies.

The board is the cache. Rubbing it out and writing it again is **invalidation**, and forgetting to do that is the bug every cache has at least once.

**Where the picture stops working.** Mama's board shows one thing for everyone. Our cache must be careful when different people should see different answers (the kitchen sees `portionsLeft`; customers don't). Copy the wrong person's answer, and Ada sees things only staff should.

## Terms used in this lesson
<!-- bite: 82a9fe7e-3395-4ed0-b941-0a3ecf8601a2 -->

1. **Cache hit** and **cache miss**: A hit means the answer was in the cache. A miss means it wasn't, so we work it out and usually store it.
2. **TTL**: This stands for **time to live**. It's how long a cached copy is kept before Redis deletes it by itself.
3. **Stale**: A cached copy is stale when the real answer has changed but the copy hasn't.
4. **Invalidation**: This is removing or replacing a cached copy because the real data changed.
5. **Cache-aside**: This is the most common way to cache: look in the cache; on a miss, read the database, store the result, return it. The app manages the cache; the database doesn't know it exists.
6. **Stampede**: This is when a popular cached copy expires and many requests miss at the same moment, all running the same expensive query together.
7. **Eviction**: This is Redis deleting keys to make room when its memory is full.
8. **Fail open**: This means that when the cache breaks, the app carries on without it. (Lesson 12's checks fail *closed*; a cache must fail *open*.)
9. **HTTP caching**: This is caching done by the client or a proxy, guided by headers like `Cache-Control` and `ETag`, so some requests never reach us, or get a tiny answer.

## Step 1: what to cache, and how stale is OK
<!-- bite: 751b3712-0882-4c5a-b2c4-2e1cd897a9d7 -->

A cache is a deliberate lie: "this is the answer", when really it's "this *was* the answer a few seconds ago". So the question for each thing is: **how old an answer can we live with?**

| Data | Read often? | Changes | Can be stale for | Cache? |
|---|---|---|---|---|
| Dish names, prices, photos | Very | A few times a day | Seconds, if edits clear it | Yes |
| `portionsLeft` | Very | Every order | About 10 seconds | Yes, with a short TTL |
| One customer's orders | A little | Often | Not at all | No |
| An order's payment status | Sometimes | Once | Not at all | No |
| The OpenAPI spec | Rarely | Every deploy | Until the next deploy | Already in the program (lesson 11) |

The tricky one is `portionsLeft`. It changes every time someone orders. If the cache says "3 left" when really there's 1, is that dangerous?

No, and the reason is important. **The cache can show an old number; the order can't use one.** Placing an order runs lesson 8's guarded `UPDATE ... WHERE portions_left >= $2` on the real database. If the cached menu said 3 and there's really 1, Ada's order for 2 is refused correctly, with `not-enough-portions`. The cache is for *looking*; the database is for *deciding*. Never let a cached value make a decision that matters, like "is this allowed" or "is there enough".

So: cache the menu, with a short TTL (10 seconds), and clear it straight away when staff edit a dish. Orders aren't cached at all.

## What to install
<!-- bite: 74414545-527e-4f6e-877a-2d4412f106da -->

**A second Redis, for the cache.** Lesson 18 set the queue's Redis to `noeviction`: when memory is full, refuse new data, never delete old. That's right for jobs and wrong for a cache. A full cache *should* throw away the least-used copies; they can always be worked out again. One Redis server has one eviction policy, so the cache gets its own:

```bash
docker run -d --name mama-put-cache -p 6380:6379 redis:7 \
  redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru --save ""
```

1. **`--maxmemory 128mb`**: never use more than this.
2. **`--maxmemory-policy allkeys-lru`**: when full, delete the **l**east **r**ecently **u**sed keys.
3. **`--save ""`**: don't write to disk. If the cache restarts empty, that's fine; it fills up again in a few seconds.

That's the general rule: **keep things you can't lose apart from things you can.** Queues and rate-limit counters in one Redis; cached copies in another.

In `.env`:

```text
CACHE_REDIS_URL=redis://localhost:6380/0
```

**The Go packages:** go-redis, the Redis client almost every Go project uses, and `singleflight` from the Go team:

```bash
go get github.com/redis/go-redis/v9
go get golang.org/x/sync/singleflight
```

## Step 2: a cache-aside helper
<!-- bite: 139ded03-9903-42c2-969a-82c3e9f06bff -->

The cache needs three operations: get a value, set a value with a TTL, and add one to a counter (step 4 is what that's for). Declared as an interface, so tests can use a map:

`internal/cache/cache.go`:

```go
// Package cache keeps copies of answers. A broken cache makes the app slower, never broken.
package cache

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"math/rand/v2"
	"time"

	"golang.org/x/sync/singleflight"
)

// Store is what the cache needs from Redis. ErrMiss means "not there".
type Store interface {
	Get(ctx context.Context, key string) ([]byte, error)
	Set(ctx context.Context, key string, value []byte, ttl time.Duration) error
	Incr(ctx context.Context, key string) error
}

var ErrMiss = errors.New("cache miss")

type Cache struct {
	store   Store
	log     *slog.Logger
	loading singleflight.Group
}

func New(store Store, log *slog.Logger) *Cache { return &Cache{store: store, log: log} }

// GetOrLoad returns the cached value for key, or runs load, caches its result and returns it.
func GetOrLoad[T any](ctx context.Context, c *Cache, key string, ttl time.Duration,
	load func(context.Context) (T, error)) (T, error) {

	if b, err := c.store.Get(ctx, key); err == nil {
		var v T
		if json.Unmarshal(b, &v) == nil {
			return v, nil
		}
	} else if !errors.Is(err, ErrMiss) {
		c.log.Warn("cache read failed, using the database", "key", key, "error", err)
	}

	// Everyone missing this key right now waits for ONE load.
	v, err, _ := c.loading.Do(key, func() (any, error) {
		loadCtx := context.WithoutCancel(ctx) // one impatient caller mustn't cancel everyone's load
		v, err := load(loadCtx)
		if err != nil {
			return v, err
		}
		if b, err := json.Marshal(v); err == nil {
			jitter := rand.N(ttl/10 + 1)
			if err := c.store.Set(loadCtx, key, b, ttl+jitter); err != nil {
				c.log.Warn("cache write failed", "key", key, "error", err)
			}
		}
		return v, nil
	})
	if err != nil {
		var zero T
		return zero, err
	}
	return v.(T), nil
}

// Generation is the current number for a family of keys (step 4).
func (c *Cache) Generation(ctx context.Context, family string) string {
	b, err := c.store.Get(ctx, "gen:"+family)
	if err != nil {
		if !errors.Is(err, ErrMiss) {
			c.log.Warn("cache generation read failed", "family", family, "error", err)
		}
		return "0"
	}
	return string(b)
}

// Bump starts a new generation, so every old key in the family is never read again.
func (c *Cache) Bump(ctx context.Context, family string) {
	if err := c.store.Incr(ctx, "gen:"+family); err != nil {
		c.log.Error("cache bump FAILED, stale data possible until TTL", "family", family, "error", err)
	}
}
```

And the Redis side, `internal/cache/redis.go`:

```go
package cache

import (
	"context"
	"errors"
	"time"

	"github.com/redis/go-redis/v9"
)

type Redis struct{ rdb *redis.Client }

// NewRedis connects with short timeouts: a slow cache is worse than no cache.
func NewRedis(url string) (*Redis, error) {
	opt, err := redis.ParseURL(url)
	if err != nil {
		return nil, err
	}
	opt.DialTimeout = 200 * time.Millisecond
	opt.ReadTimeout = 200 * time.Millisecond
	opt.WriteTimeout = 200 * time.Millisecond
	opt.PoolTimeout = 200 * time.Millisecond
	opt.MaxRetries = 1
	return &Redis{rdb: redis.NewClient(opt)}, nil
}

func (r *Redis) Get(ctx context.Context, key string) ([]byte, error) {
	b, err := r.rdb.Get(ctx, key).Bytes()
	if errors.Is(err, redis.Nil) {
		return nil, ErrMiss
	}
	return b, err
}

func (r *Redis) Set(ctx context.Context, key string, value []byte, ttl time.Duration) error {
	return r.rdb.Set(ctx, key, value, ttl).Err()
}

func (r *Redis) Incr(ctx context.Context, key string) error { return r.rdb.Incr(ctx, key).Err() }

func (r *Redis) Close() error { return r.rdb.Close() }
```

Three protections are built in, each for a real failure.

**1. Redis down means slower, not broken.** If a read fails, `GetOrLoad` logs it and carries on as if it were a miss, so we go to Postgres. If a write fails, we log it and still return the value. The 200 ms timeouts mean a struggling Redis costs at most a fifth of a second, not a hung request. `redis.Nil` is go-redis's way of saying "no such key"; `Get` turns it into our own `ErrMiss`, so nothing above this file knows about go-redis. A cache must **fail open**. (Compare the queue Redis from lesson 18, which must *not*: a lost job is lost work.)

**2. A stampede becomes one query.** Picture 12:30. The menu's copy expires. In the next 50 milliseconds, 200 requests miss. Without care, that's 200 identical queries hitting Postgres at once, at its busiest moment. `singleflight.Group` is the Go team's answer: `Do(key, fn)` runs `fn` for the first caller with that key, and every other caller with the same key, while the first is still running, **waits for the same result**. One query instead of 200. (This is per process. With three servers, at most three queries, which is fine.)

There's a trap inside it, and `context.WithoutCancel` is the fix. The first caller's `fn` runs on behalf of everyone waiting. If it used the first caller's context and *that* customer closed their app, the load would be cancelled, and all 199 others would get "context canceled" too. So the load runs on a context that keeps the values (the logger, the request ID) but can't be cancelled by one impatient caller. Lesson 15 used the same tool for the same reason.

**3. Jitter spreads out expiry.** Cache 50 things at the same moment with the same TTL, and they all expire at the same moment too: 50 misses together. A random extra, up to a tenth of the TTL, spreads them out.

**Why `GetOrLoad[T]` is a function, not a method.** You might expect `c.GetOrLoad[menu.Dish](...)`. Go doesn't allow it: **methods can't have their own type parameters**. A type can be generic (`type List[T any] struct`), and its methods can use `T`, but a method on a non-generic type can't introduce a new one. So the generic part is a plain function that takes the `*Cache` as its first argument. It reads a little differently, and it's the normal Go way.

## Step 3: cache at the right layer
<!-- bite: 24be213c-4f8b-484c-8cd4-171fc76f2fcf -->

Where does the cache go? Not around the whole HTTP response. Remember who sees what: the kitchen sees `portionsLeft` and customers don't (lesson 13), and v1 and v2 have different shapes (lesson 10). Cache whole responses, and one day a cook's response lands in the cache and every customer sees the stock levels.

So we cache the **data**, in the menu service, and let the presenters (which know about versions and views) run *after* the cache, on every request:

```text
request → handler → presenter(version, view) ← menu.Service → cache → store → Postgres
                                                  ↑ cached here: the same dishes for everyone
```

In `internal/menu/service.go`:

```go
const menuTTL = 10 * time.Second

type Service struct {
	store Store
	cache *cache.Cache
}

func listKey(gen string, q ListQuery) string {
	b, _ := json.Marshal(q)
	sum := sha256.Sum256(b)
	return "menu:" + gen + ":list:" + base64.RawURLEncoding.EncodeToString(sum[:12])
}

func (s *Service) List(ctx context.Context, q ListQuery) (Page, error) {
	gen := s.cache.Generation(ctx, "menu")
	return cache.GetOrLoad(ctx, s.cache, listKey(gen, q), menuTTL, func(ctx context.Context) (Page, error) {
		return s.store.List(ctx, q)
	})
}

func (s *Service) Get(ctx context.Context, id int64) (Dish, error) {
	gen := s.cache.Generation(ctx, "menu")
	key := "menu:" + gen + ":dish:" + strconv.FormatInt(id, 10)
	return cache.GetOrLoad(ctx, s.cache, key, menuTTL, func(ctx context.Context) (Dish, error) {
		return s.store.Find(ctx, id)
	})
}

func (s *Service) Add(ctx context.Context, in NewDish) (Dish, error) {
	d, err := s.store.Add(ctx, in)
	if err != nil {
		return Dish{}, err
	}
	s.cache.Bump(ctx, "menu")
	return d, nil
}

// Update, Remove, SetPhoto and SetProcessedPhoto: the same. Write, then Bump.
```

(`Page` is whatever lesson 9's `List` returns: the dishes and the total. `NewService` takes the `*cache.Cache`; `run` and lesson 18's worker both build one from `CACHE_REDIS_URL`, because the worker's processed photos must bump too.)

A few things to see:

1. **Each different query is a different answer**, so each gets its own key. The query is turned into JSON, hashed, and the first 12 bytes of the hash keep the key a sensible length. And `q` has already been checked by lesson 9's `Query` reader, so there's a limited set of shapes. **Never build cache keys from raw, unchecked input**: an attacker sending a million random query strings would fill the cache with a million useless keys and push out the useful ones.
2. **Nothing about *who* is asking goes in the key, or comes out of the store.** The view (kitchen or customer) is chosen by the presenter, after the cache. If a query ever depended on the caller (say, "dishes I've favourited"), it would need the user ID in the key, or, better, not be cached in this shared way at all.
3. **Errors aren't cached.** If `Find` returns `ErrDishNotFound`, `GetOrLoad` returns the error and stores nothing, so the next request asks again. (Caching "not found" for a few seconds is called **negative caching**, and it helps when attackers ask for missing IDs on purpose. Add it only when you need it.)
4. **The domain `Dish` is cached as JSON**, with Go's own field names, since it has no `json` tags (lesson 10). That's fine: it's our internal copy, read back by the same program. But if a deploy renames a field, the copies made by the *old* program decode with that field empty. Our 10-second TTL makes that harmless; for long TTLs, put a version in the key prefix (`menu:v2:...`) and change it when the type changes.

## Step 4: keeping it honest, with generations
<!-- bite: 58bf9213-9c90-4120-b7da-4f5b65dd202c -->

Now the hard part, the one in the famous joke ("there are only two hard things in computer science: cache invalidation and naming things").

When Mama changes the price of jollof, which keys must go? `menu:...:dish:1`, obviously. But also *every* list that contains jollof: page 1, page 1 sorted by price, the search for "rice", the filter for "under ₦2,000"... We don't know which of those exist, and searching Redis for them (`KEYS menu:*`) is slow and blocks Redis for everyone while it runs.

So we don't find them. We make them unreachable. Every menu key has a **generation number** in it: `menu:7:list:...`. When anything on the menu changes, `Bump(ctx, "menu")` adds one to the generation, with Redis's `INCR`. Now every request builds keys starting `menu:8:`, which don't exist yet, so they miss and load fresh data. The old `menu:7:` keys are never read again, and quietly expire within 10 seconds (or get evicted, because nobody uses them).

One `INCR`, and the whole menu cache is new. It costs one extra tiny Redis read per request (the generation), which is worth it.

The order of things in `Add` matters: **write to the database first, then bump.** Bump first, and a request in between could load the *old* data under the *new* generation and keep it for 10 seconds.

And what if the bump fails, because the cache Redis is down at that moment? The old data stays until its TTL runs out: at most 10 seconds of stale menu. That's why the TTL exists even though we invalidate: it's the backstop that limits how wrong the cache can ever be. **Always set a TTL**, even on things you invalidate by hand.

Placing an order changes `portionsLeft` but doesn't bump the generation. That's the choice from step 1: at lunch, bumping on every order would empty the cache every few seconds, and the cache would do nothing. Ten seconds of slightly old portion counts is the price, and the guarded `UPDATE` makes it safe to pay.

## Step 5: HTTP caching, so phones don't even ask
<!-- bite: 25befb06-a7cb-4f1e-8a99-22a257829fd2 -->

Redis saves Postgres the work. HTTP caching can save the *request*, or at least its body.

**`ETag` and 304.** An `ETag` is a short fingerprint of a response's body. When the phone asks again, it sends `If-None-Match: <that fingerprint>`. If the new body has the same fingerprint, we answer **304 Not Modified** with no body, and the phone uses the copy it has. On a slow mobile connection, 200 bytes of headers instead of 20 KB of menu is a real difference.

Express adds ETags to every JSON response by itself. Go's server doesn't (it does for files served with `http.ServeContent`, like lesson 14's photos, but not for what you write yourself). So `httpx` gets one more writer, in `internal/httpx/json.go`:

```go
// WriteCacheable writes a success like WriteData, with an ETag, and answers 304
// when the client already has exactly this body.
func WriteCacheable(w http.ResponseWriter, r *http.Request, data, meta any, cacheControl string) error {
	body, err := json.Marshal(envelope{Data: data, Meta: meta})
	if err != nil {
		return fmt.Errorf("encode response: %w", err)
	}
	sum := sha256.Sum256(body)
	etag := `"` + base64.RawURLEncoding.EncodeToString(sum[:12]) + `"`

	h := w.Header()
	h.Set("ETag", etag)
	h.Set("Cache-Control", cacheControl)
	h.Add("Vary", "Authorization")

	if match := r.Header.Get("If-None-Match"); match != "" && strings.Contains(match, etag) {
		w.WriteHeader(http.StatusNotModified)
		return nil
	}
	h.Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(body)
	return nil
}
```

The menu's `list` and `get` handlers use it instead of `WriteData` and `WriteList`.

1. **The fingerprint is a hash of the body bytes**, so the same answer always has the same ETag, on any server, after any restart.
2. **The 304 still carries `ETag`, `Cache-Control` and `Vary`**, as the HTTP rules require, but no body and no `Content-Type`.
3. **`Vary: Authorization`**: the kitchen and customers get different bodies from the same URL. `Vary` tells every cache in between that the answer depends on that header, so a copy made for one token is never handed to a request with another.

This saves bandwidth, not our work: we still build the body to fingerprint it. The Redis cache is what saves our work. Together, a lunchtime menu refresh is one Redis read, a hash, and 200 bytes on the wire.

**`Cache-Control`** tells clients and proxies how long they may reuse a response without asking at all. The menu handler chooses:

```go
func cacheControlFor(r *http.Request) string {
	if _, ok := auth.IdentityFrom(r.Context()); ok {
		return "private, max-age=0, must-revalidate"
	}
	return "public, max-age=10"
}
```

1. **`public, max-age=10`** for logged-out visitors: anyone (the phone, a CDN in front of us) may reuse this for 10 seconds without asking.
2. **`private, max-age=0, must-revalidate`** when someone is logged in: only their own device may keep it, never a shared proxy, and it must ask (with `If-None-Match`) every time. The 304 makes asking cheap.

And for anything personal (orders, payments, `/v2/auth`), send `Cache-Control: no-store`. A shared computer at a cyber café shouldn't keep Ada's order history on its disk. One tiny middleware, `httpx.NoStore`, sets it; wrap the orders, payments and auth handlers' `Register` muxes with it, or add it in each `Register`.

```bash
curl -si localhost:8080/v2/menu | grep -E '^(HTTP|Etag|Cache-Control)'
# HTTP/1.1 200 OK
# Cache-Control: public, max-age=10
# Etag: "Zr8Kq2mM1xQh3Ylf"

curl -si localhost:8080/v2/menu -H 'If-None-Match: "Zr8Kq2mM1xQh3Ylf"' | head -1
# HTTP/1.1 304 Not Modified
```

## Step 6: rate limits, shared at last
<!-- bite: f4650648-4211-4c31-8b38-a86758a929ae -->

Lesson 14 left a known weakness: the buckets live in each server's memory, so three servers means triple the limit, and a restart resets everyone. Now that Redis is running, the counts can live there.

Which Redis? The **queue** one, from lesson 18, not the cache. Rate-limit counters must not be evicted to make room: evict an attacker's counter and they get a fresh five guesses. They expire by themselves when their window ends, so they don't pile up.

The simplest shared limit is a **fixed window**: count requests per caller per minute, in a key that expires at the end of the minute. `internal/httpx/redislimit.go`:

```go
// RedisLimit allows `limit` requests per `window` for each key, shared by every server.
type RedisLimit struct {
	rdb      *redis.Client
	prefix   string
	limit    int64
	window   time.Duration
	fallback *Limiters // used when Redis can't be reached
}

func NewRedisLimit(rdb *redis.Client, prefix string, limit int64, window time.Duration, fallback *Limiters) *RedisLimit {
	return &RedisLimit{rdb: rdb, prefix: prefix, limit: limit, window: window, fallback: fallback}
}

func (l *RedisLimit) key(id string) string {
	slot := time.Now().Unix() / int64(l.window.Seconds())
	return fmt.Sprintf("rl:%s:%s:%d", l.prefix, id, slot)
}

// Take counts one request. It says whether it's allowed, and how long to wait if not.
func (l *RedisLimit) Take(ctx context.Context, id string) (bool, time.Duration) {
	key := l.key(id)
	var count *redis.IntCmd
	_, err := l.rdb.TxPipelined(ctx, func(p redis.Pipeliner) error {
		count = p.Incr(ctx, key)
		p.ExpireNX(ctx, key, l.window)
		return nil
	})
	if err != nil {
		return l.fallback.For(id).Allow(), l.fallback.RetryAfter()
	}
	if count.Val() > l.limit {
		return false, l.untilNextWindow()
	}
	return true, 0
}

// Used says how many have been counted in this window, without counting one.
func (l *RedisLimit) Used(ctx context.Context, id string) int64 {
	n, err := l.rdb.Get(ctx, l.key(id)).Int64()
	if err != nil && !errors.Is(err, redis.Nil) {
		return 0 // can't tell: let it through; the fallback still counts failures
	}
	return n
}

func (l *RedisLimit) untilNextWindow() time.Duration {
	w := int64(l.window.Seconds())
	return time.Duration(w-time.Now().Unix()%w) * time.Second
}
```

1. **`TxPipelined`** sends `INCR` and `EXPIRE` together, in one round trip, as one transaction (`MULTI`/`EXEC`), so no other command can land between them.
2. **`ExpireNX`** sets the expiry only if the key doesn't have one yet (Redis 7), so the window ends at the same time however many requests come in. The slot number in the key (the minute since 1970, for a one-minute window) means each window is its own key.
3. **If Redis can't be reached, it falls back to lesson 14's in-memory buckets.** Failing open completely would switch off the login limit exactly when someone has knocked Redis over; failing closed would lock every customer out. The local limit is the middle way: per server, but still a limit.
4. **`Used`** looks without counting, for the login limit, which only counts failures. The login handler becomes: if `Used` is already at the limit, 429; otherwise try the login, and on `ErrWrongLogin`, `Take`.

A fixed window is simpler than lesson 14's token bucket, with one known weakness: a caller can send the whole limit at 12:00:59 and again at 12:01:00, twice the limit in two seconds. For a general limit and a login limit, that's fine. If you ever need the smoother behaviour shared across servers, `github.com/go-redis/redis_rate` does a token-bucket-style limit in Redis, from the go-redis team.

`run` builds the queue Redis's client once (`redis.ParseURL(getenv("REDIS_URL"))`) and passes it in, like every other dependency. `apptest` keeps lesson 14's in-memory `Limiters`.

## Step 7: what the cache must never hold
<!-- bite: 3f5eff24-5bc6-4a22-b67a-afe15f54b8fd -->

Before testing, one list worth keeping on the wall:

1. **Anything personal in a shared key.** Orders, payments, profiles. If it belongs to one person, it doesn't go in a cache everyone reads.
2. **Anything a decision rests on.** Stock levels for placing an order, a user's role for a permission check, a payment's status for "may the kitchen cook this". Decide from the database.
3. **Secrets.** Tokens, keys, password hashes. A cache is a copy, and copies leak.
4. **Whole responses with a view in them.** Cache the data; present per request.

## Step 8: testing the cache
<!-- bite: 79e4b9eb-d85f-4c2d-9768-5f60d142df16 -->

1. **An in-memory `Store`** for the fast tests: a map behind a mutex, with the three methods. (`Incr` parses the stored value with `strconv.ParseInt`, adds one, and stores it back.) `apptest.New` uses it. Most HTTP tests should behave the same with or without a cache, which is itself a good test.
2. **The invalidation test**, the one that matters most:

```go
func TestNewPriceShowsStraightAway(t *testing.T) {
	a := apptest.New(t)
	staff := a.Login(t, auth.RoleStaff)
	type dish struct {
		Data struct {
			Price struct{ Amount int64 } `json:"price"`
		} `json:"data"`
	}

	before := apptest.Decode[dish](t, a.Do(t, "GET", "/v2/menu/1", nil))
	a.Do(t, "PATCH", "/v2/menu/1", map[string]any{"price": map[string]any{"amount": 200000, "currency": "NGN"}},
		apptest.Token(staff))
	after := apptest.Decode[dish](t, a.Do(t, "GET", "/v2/menu/1", nil))

	if before.Data.Price.Amount == 200000 || after.Data.Price.Amount != 200000 {
		t.Errorf("price before %d, after %d; want it to change to 200000",
			before.Data.Price.Amount, after.Data.Price.Amount)
	}
}
```

3. **The "Redis is down" test**: build the cache with a `Store` whose every method returns an error, and check `GET /v2/menu` still answers 200. That's the fail-open promise, checked.
4. **The stampede test**: a load function that counts its calls and sleeps 50 ms; call `GetOrLoad` from 20 goroutines at once with the same key; check the load ran **once**. Then cancel one caller's context half-way, and check the other 19 still get the value.
5. **The ETag test**: a `GET`, then the same `GET` with its `ETag` in `If-None-Match`: 304, no body. Then change the dish, and the same `If-None-Match` gets 200 with the new body.

## The Go in this lesson
<!-- bite: 193e828e-40c1-43a0-a670-6d2dfd97b183 -->

1. **`singleflight.Group`** and **`g.Do(key, fn)`**: Runs `fn` once per key at a time; callers that arrive while it's running wait and share its result. It returns the value, the error, and whether the result was shared.
2. **Methods can't have type parameters**: so `GetOrLoad[T]` is a function taking `*Cache`. Go infers `T` from the `load` function, so the call is just `cache.GetOrLoad(ctx, s.cache, key, ttl, load)`.
3. **`v.(T)`**: `Do` returns `any`; the type assertion turns it back into a `T`. It can't fail here, because only our `load` puts values in.
4. **`var zero T; return zero, err`**: The zero value of a type parameter, for the error path.
5. **`redis.ParseURL(url)`** and the options struct: go-redis reads a `redis://` URL into `*redis.Options`, whose fields you can change before `NewClient`.
6. **`rdb.Get(ctx, key).Bytes()`** and **`redis.Nil`**: Every go-redis command returns a command value; `.Bytes()`, `.Int64()` or `.Err()` give its result. `redis.Nil` is the error for "no such key".
7. **`rdb.TxPipelined(ctx, func(p redis.Pipeliner) error {...})`**: Queues several commands and sends them together, as one `MULTI`/`EXEC` transaction. The command values (`count`) are filled in when it returns.
8. **`sum[:12]`**: A slice of the first 12 bytes of a 32-byte array. Enough of a SHA-256 to be unique for cache keys and ETags, and shorter to read.
9. **`time.Now().Unix() / int64(window.Seconds())`**: Integer division throws away the remainder, so every second inside one window gives the same slot number.
10. **`h.Add("Vary", ...)`**: Lesson 14 again: `Add`, because CORS may already have set a `Vary`.

## Your project so far
<!-- bite: c08ca910-3577-4833-b063-cb183cbd5860 -->

```text
mama-put/
├── .env                           ← CACHE_REDIS_URL (a second Redis, allkeys-lru)
├── go.mod                         ← redis/go-redis/v9, x/sync
├── cmd/
│   ├── api/main.go                ← cache Redis, cache.New, queue Redis client for rate limits
│   └── worker/main.go             ← builds the cache too, so processed photos bump the menu
└── internal/
    ├── cache/                     ← NEW package
    │   ├── cache.go               ← Store, ErrMiss, GetOrLoad[T] (singleflight, jitter, fail open), Generation, Bump
    │   ├── redis.go               ← the Redis Store: 200 ms timeouts, one retry
    │   └── memory.go              ← NEW: the in-memory Store for tests
    ├── httpx/
    │   ├── json.go                ← WriteCacheable: ETag, 304, Cache-Control, Vary
    │   ├── nostore.go             ← NEW: Cache-Control: no-store for personal routes
    │   └── redislimit.go          ← NEW: fixed-window limits in Redis, in-memory fallback
    ├── menu/
    │   ├── service.go             ← List and Get through the cache; every write bumps "menu"
    │   └── handlers.go            ← WriteCacheable, cacheControlFor
    ├── auth/
    │   └── handlers.go            ← login limit uses RedisLimit (Used, then Take on failure)
    └── apptest/
        └── apptest.go             ← the memory cache store
```

## Common mistakes
<!-- bite: c6bb92bf-1926-4b56-88b1-4d6d8ba49610 -->

1. **Deciding from a cached value.** Stock, roles, payment status: decide from the database.
2. **Caching whole responses that depend on who's asking.** Cache data; present per request.
3. **One Redis for the queue and the cache.** One eviction policy can't suit both. Two.
4. **No TTL "because we invalidate".** The day a bump fails, the copy lives for ever.
5. **Bumping before writing.** A request in between caches the old data under the new generation.
6. **`KEYS pattern` to find what to invalidate.** It blocks Redis. Use generations.
7. **A cache that fails closed.** If the menu breaks when Redis does, the cache has made you less reliable. Fail open, with short timeouts.
8. **Using the first caller's context inside `singleflight`.** One cancelled request cancels everyone's load. `context.WithoutCancel`.
9. **Cache keys from unchecked input.** Attackers fill your cache with junk. Key on validated queries only.
10. **No `Vary` when the body depends on a header.** A shared cache hands one person's answer to another.
11. **Personal answers without `no-store`.** They stay on shared computers' disks.
12. **Rate-limit counters in the cache Redis.** Eviction resets attackers' counts. Keep them in the `noeviction` one.

## Check your understanding
<!-- bite: a38fb24e-4097-4d73-8ef6-cd08570e0917 -->

1. The cached menu says 3 portions of jollof are left; really there's 1. Ada orders 2. What happens, and why is that safe?
2. Mama changes the price of jollof. Which cached lists are cleared, and how, without knowing their keys?
3. 200 requests miss the menu at once, on one server. How many Postgres queries run? What if the first request's customer closes the app half-way?
4. Why does the kitchen's menu not leak to customers, when both read from the same cache?
5. The cache Redis is switched off. What happens to `GET /v2/menu`, and to a price change?
6. Why do rate-limit counts go in the queue's Redis, not the cache's?

<details>
<summary>Answers, after your attempt</summary>

1. The order runs the guarded `UPDATE ... WHERE portions_left >= 2` against Postgres, which has 1, so no row changes and Ada gets `not-enough-portions`. It's safe because the cache is only used for showing the menu; placing an order decides from the database.
2. All of them. The write is followed by `Bump(ctx, "menu")`, which increments the generation. Every new request builds keys with the new number, so they miss and load fresh data; the old keys are never read again and expire within the TTL.
3. One: `singleflight` lets the first request load and makes the other 199 wait for its result. The load runs with `context.WithoutCancel`, so the first customer leaving doesn't cancel it; everyone still gets the menu.
4. Because the cache holds the same dishes for everyone, with no view in them. The presenter runs after the cache, on every request, and only adds `portionsLeft` when the caller may write the menu.
5. Reads fail quickly (200 ms at most), are logged, and go to Postgres, so the menu still works, just with no caching. A price change still saves; the bump fails and is logged, but since nothing could be read from the cache anyway, nobody sees stale data. When the cache comes back, any old copies left in it expire within 10 seconds.
6. Because the cache Redis evicts keys when it's full. An evicted counter is a reset limit: an attacker's failed logins would be forgotten. The queue's Redis never evicts, and the counters expire on their own.

</details>

## Practice
<!-- bite: a84e8380-9b46-4944-b3d5-d5e1a322ecf1 -->

1. Write `cache.Memory`, the in-memory `Store`, with TTLs that really expire (store the expiry time and check it in `Get`), and use it in `apptest`.
2. Write the stampede test and the cancelled-caller test from step 8.
3. Add `httpx.NoStore`, apply it to the orders, payments and auth routes, and check with `curl -sI` that `/v2/orders/1` says `no-store` and `/v2/menu` doesn't.
4. Add negative caching for missing dishes: when `Find` returns `ErrDishNotFound`, store a small marker for 5 seconds, and return the same error from the marker. Make sure adding a dish with that ID (it can't happen with identity columns, but pretend) would be cleared by the generation bump.
5. Count hits and misses: give `Cache` two `atomic.Int64` counters and log their totals once a minute. Lesson 27 turns them into metrics.

**Done when** a repeat of `GET /v2/menu` within 10 seconds doesn't reach Postgres (watch the request log, or count queries); a price change shows on the very next request; stopping the cache Redis leaves the menu working; a repeat with `If-None-Match` gets 304; the login limit holds across two copies of the API running on different ports; and `make test` passes.

## Before moving on
<!-- bite: 6656abd7-46b4-4f81-9108-15b719641887 -->

Mama Put API now remembers answers it's already worked out. The menu comes from a cache that fails open, turns stampedes into one query, is cleared in one step by a generation bump, and never mixes up who sees what. Phones get ETags and 304s, personal answers are never stored, and rate limits finally hold across every server.

There's one screen this doesn't help: the kitchen's. Right now it asks `GET /v2/orders?status=pending` every few seconds, to see if anything new has arrived. Most of those requests get the same answer as last time; and an order that arrives just after a refresh waits until the next one. The kitchen wants new orders to *appear*, the moment they're paid. That's real-time updates, the next lesson.

## Related
<!-- bite: 9a1b9e2d-52a9-470d-92bd-8d336981948d -->

- [[backend/frameworks/net-http/20-real-time|Next: Real-time Updates]]
- [[backend/frameworks/express/19-caching|The same lesson in Express]] — ioredis, an in-flight map, and Express's own ETags
- [[backend/frameworks/net-http/08-data-with-postgres|Data with PostgreSQL]] — the guarded `UPDATE` that makes stale counts safe

## About this lesson
<!-- bite: 24765bec-47f8-4d19-976e-869c329f2bb4 -->

**Level:** Advanced. Lesson 19 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, go-redis v9, `golang.org/x/sync/singleflight` and Redis 7. Covers what to cache and how stale is acceptable, separate Redis instances for queues and caches, a fail-open cache-aside helper with short timeouts and jitter, stampede protection with `singleflight` and `context.WithoutCancel`, why generic helpers are functions, caching data below the presenters, invalidation by generation, hand-written ETags with `Vary`, `Cache-Control` for public, private and personal answers, and fixed-window rate limits shared in Redis with a local fallback.
