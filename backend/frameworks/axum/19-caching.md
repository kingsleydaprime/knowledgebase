---
id: 67643dcb-c8df-4592-90b7-8741e12295df
---

# Caching

**Caching means keeping a copy of an answer, so the next person who asks the same question gets the copy instead of the server working it out again.** It makes reads fast and saves the database, and it has one danger: a copy can be out of date. So a good cache has two parts, keeping copies and keeping them honest. In Mama Put, the menu is kept in Redis for ten seconds, every edit makes the old copies unreachable at once, and a broken cache only makes the app slower, never wrong.

## Before you start
<!-- bite: f8a351a4-ae7b-4449-826e-77db743d5c46 -->

You should have:

1. Finished [[backend/frameworks/axum/18-background-jobs|lesson 18]], so the worker runs jobs and `cargo test` runs 60 tests.
2. Docker, or Redis installed on your computer.

After this lesson you will be able to:

1. Decide what to cache, and how old a copy may be, for each kind of data.
2. Write a cache-aside helper that survives Redis being down and turns a stampede into one query.
3. Keep the cache honest with generations, and know why every copy still needs a TTL.
4. Use HTTP caching (`ETag`, 304, `Cache-Control`) so phones often don't download the menu at all.
5. Share rate limits across every copy of the app, with a fallback.
6. Say what must never go in a cache, and test the cache.

## Where we stopped
<!-- bite: 22759627-d561-43a4-9df6-5d4a85aed378 -->

Lunchtime at Mama Put. Every phone that opens the app asks for the menu, and every time, Postgres works it out again: the same rows, sorted the same way, hundreds of times a minute. The menu changes a few times a day.

And lesson 14 left a known weakness: the login limit lives in each copy of the app's memory. Run three copies (lesson 36 will), and a guessing program gets three times the tries. Restart one, and its counts are gone.

## The kid version
<!-- bite: fda8a4f2-ec5f-4303-b652-8c8532889754 -->

Mama's regulars all ask the same question: "what do you have today?" She could walk to the kitchen and look in every pot each time. Instead, she writes the day's list on a board by the door. People read the board; Mama only walks to the kitchen when the board might be wrong.

The trick is wiping the board at the right moment. When the jollof runs out, she rubs it off straight away. And even if she forgets, she rewrites the whole board every so often, so it's never wrong for long.

The board is the cache. Rubbing it off is invalidation. Rewriting it every so often is the TTL.

**Where the picture stops working.** Mama has one board. Our app runs on several servers, and they must all read the same board, or one server shows jollof long after another has rubbed it off. That's why the copies live in Redis, which every server shares, and not in each server's memory.

## Terms used in this lesson
<!-- bite: 80fd6356-00ac-4ed0-821f-be76bc0b73bd -->

1. **Cache**: This is a store of copies of answers, kept to be handed out again. Ours is a Redis server.
2. **Hit** and **miss**: A hit is when the copy is there; a miss is when it isn't, and the real answer must be worked out.
3. **TTL**: This stands for **time to live**. It's how long a copy is kept before it's thrown away by itself.
4. **Cache-aside**: This is the most common way to use a cache: look for a copy; on a miss, ask the database, keep a copy, then answer.
5. **Invalidation**: This is making sure old copies stop being used once the real data changes.
6. **Stampede**: This is many requests missing the same key at the same moment, and all of them asking the database at once.
7. **Eviction**: This is the cache throwing copies away to make room when its memory is full.
8. **`ETag`**: This is a short fingerprint of a response's body, sent as a header. A client that already has a copy sends it back in `If-None-Match`, and if nothing changed, the answer is **304 Not Modified** with no body.

## Step 1: what to cache, and how stale is OK
<!-- bite: faeb31b1-637e-42db-86c5-d69eede18296 -->

A cache is a deliberate lie: "this is the answer", when really it's "this *was* the answer a few seconds ago". So the question for each thing is: **how old an answer can we live with?**

| Data | Read often? | Changes | Can be stale for | Cache? |
|---|---|---|---|---|
| Dish names, prices, photos | Very | A few times a day | Seconds, if edits clear it | Yes |
| `portionsLeft` | Very | Every order | About 10 seconds | Yes, with a short TTL |
| One customer's orders | A little | Often | Not at all | No |
| An order's payment status | Sometimes | Once | Not at all | No |
| The OpenAPI document | Rarely | Every deploy | Until the next deploy | Already built into the program (lesson 11) |

The tricky one is `portionsLeft`. It changes every time someone orders. If the cache says "3 left" when really there's 1, is that dangerous?

No, and the reason matters. **The cache can show an old number; an order can't use one.** Placing an order runs lesson 8's guarded `UPDATE ... WHERE portions_left >= $2` on the real database. If the cached menu said 3 and there's really 1, Ada's order for 2 is refused, correctly, with `not-enough-portions`. The cache is for *showing*; decisions are made against Postgres.

So: cache the menu for 10 seconds, and clear it at once when staff edit a dish. Don't cache orders at all.

## What to install
<!-- bite: 4a153aa4-0e02-4cec-8509-3a3931210b26 -->

**Two Redis servers, not one.** A cache should throw away its least-used copies when it's full; they can always be made again. But rate-limit counters must *not* be thrown away: evict a guessing program's counter and it gets a fresh ten tries. One Redis server has one eviction policy for everything in it, so they get one each:

```bash
docker run -d --name mama-put-cache -p 6380:6379 redis:7 \
  redis-server --maxmemory 64mb --maxmemory-policy allkeys-lru --save ""
docker run -d --name mama-put-limits -p 6381:6379 redis:7 \
  redis-server --maxmemory 16mb --maxmemory-policy noeviction --save ""
```

1. **`--maxmemory 64mb`**: never use more than this.
2. **`--maxmemory-policy allkeys-lru`** for the cache: when full, delete the **l**east **r**ecently **u**sed keys. **`noeviction`** for the limits: when full, refuse new keys, and never delete one.
3. **`--save ""`**: don't write to disk. If either restarts empty, that's fine: the cache fills up again in seconds, and the limits start a new minute.

That's the general rule: **keep things you can't lose apart from things you can.** (The other subjects in this vault have a third Redis already, for their job queues. Ours are in Postgres, from lesson 18.)

In `.env`:

```text
CACHE_REDIS_URL=redis://localhost:6380/0
LIMITS_REDIS_URL=redis://localhost:6381/0
```

And the Rust client:

```bash
cargo add redis --no-default-features --features tokio-comp,connection-manager
```

**`redis`** is the Redis client most Rust projects use. `tokio-comp` makes it work with Tokio, and `connection-manager` adds a connection that remakes itself when it breaks (step 2).

## Step 2: a cache-aside helper
<!-- bite: e4bfc056-ed2d-46ef-a24c-bb336505f02e -->

The cache needs three things from Redis: get a value, set a value with a TTL, and add one to a counter (step 4 is what that's for). As a trait, so tests can use a map. `src/cache/mod.rs` starts:

```rust
//! Copies of answers, kept for a few seconds so Postgres doesn't work them out again.
//! A broken cache makes the app slower, never broken.

mod memory;
mod redis_store;

use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
    time::Duration,
};

use async_trait::async_trait;
use serde::{Serialize, de::DeserializeOwned};

pub use memory::MemoryStore;
pub use redis_store::{RedisStore, connect_lazily};

/// What the cache needs from wherever it keeps copies. Redis in real life; a map in tests.
#[async_trait]
pub trait CacheStore: Send + Sync {
    async fn get(&self, key: &str) -> Result<Option<Vec<u8>>, CacheError>;
    async fn set(&self, key: &str, value: &[u8], ttl: Duration) -> Result<(), CacheError>;
    /// Adds one to a number, starting from 0, and returns the new number.
    async fn incr(&self, key: &str) -> Result<i64, CacheError>;
}

/// The cache couldn't be reached, or answered nonsense. Never shown to a client.
#[derive(Debug, thiserror::Error)]
#[error("cache: {0}")]
pub struct CacheError(pub String);
```

The Redis side, `src/cache/redis_store.rs`:

```rust
use std::time::Duration;

use async_trait::async_trait;
use redis::{
    AsyncCommands, Client, RedisError,
    aio::{ConnectionManager, ConnectionManagerConfig},
};

use super::{CacheError, CacheStore};

/// A connection to Redis that's made on first use and remade when it breaks, with short timeouts:
/// a slow Redis must cost a request a fifth of a second at most, never a hang.
pub fn connect_lazily(url: &str) -> Result<ConnectionManager, RedisError> {
    let config = ConnectionManagerConfig::new()
        .set_connection_timeout(Some(Duration::from_millis(200)))
        .set_response_timeout(Some(Duration::from_millis(200)))
        .set_number_of_retries(0);
    Client::open(url)?.get_connection_manager_lazy(config)
}

/// Copies kept in Redis. Cheap to clone: every clone shares one connection.
#[derive(Clone)]
pub struct RedisStore {
    redis: ConnectionManager,
}

impl RedisStore {
    pub fn new(redis: ConnectionManager) -> Self {
        RedisStore { redis }
    }
}

fn failed(e: RedisError) -> CacheError {
    CacheError(e.to_string())
}

#[async_trait]
impl CacheStore for RedisStore {
    async fn get(&self, key: &str) -> Result<Option<Vec<u8>>, CacheError> {
        self.redis.clone().get(key).await.map_err(failed)
    }

    async fn set(&self, key: &str, value: &[u8], ttl: Duration) -> Result<(), CacheError> {
        let millis = u64::try_from(ttl.as_millis()).unwrap_or(u64::MAX).max(1);
        self.redis.clone().pset_ex(key, value, millis).await.map_err(failed)
    }

    async fn incr(&self, key: &str) -> Result<i64, CacheError> {
        self.redis.clone().incr(key, 1).await.map_err(failed)
    }
}
```

(The file isn't called `redis.rs`, because inside the `cache` module a module called `redis` and the crate called `redis` would have the same name.)

A `ConnectionManager` is one connection to Redis, shared by everything that clones it. Many requests can send commands over it at once (Redis answers them in order), so there's no pool to size. It's **lazy**: it doesn't connect until the first command, so the app starts even when Redis is down. And when the connection breaks, it remakes it on the next command.

The settings are the important part. A cache that answers in 200 milliseconds is barely worth having, so **200 ms is the most any one Redis call will wait**, connecting or answering. And **no retries**: I first set one retry, stopped Redis, and every menu read took 0.7 to 0.9 seconds, as each Redis call waited for a reconnect to fail twice. With no retries it was 70 ms. The next request tries again anyway.

Now the helper itself:

```rust
/// Cheap to clone: every clone shares one store and one set of loading lines.
#[derive(Clone)]
pub struct Cache {
    store: Arc<dyn CacheStore>,
    /// One line per key being loaded right now. The first in line loads; the rest wait, then read its copy.
    loading: Arc<Mutex<HashMap<String, Arc<tokio::sync::Mutex<()>>>>>,
}

impl Cache {
    pub fn new(store: Arc<dyn CacheStore>) -> Self {
        Cache { store, loading: Arc::default() }
    }

    /// A cache in this program's memory: for tests.
    pub fn in_memory() -> Self {
        Cache::new(Arc::new(MemoryStore::default()))
    }

    /// The copy kept under `key`, or else `load`'s answer, kept for `ttl` (plus up to a tenth, at random).
    /// Errors are passed on and never kept.
    pub async fn get_or_load<T, E, F, Fut>(&self, key: &str, ttl: Duration, load: F) -> Result<T, E>
    where
        T: Serialize + DeserializeOwned,
        F: FnOnce() -> Fut,
        Fut: Future<Output = Result<T, E>>,
    {
        if let Some(copy) = self.read(key).await {
            return Ok(copy);
        }
        // Everyone missing this key right now waits in one line. If the one loading gives up
        // (their request is dropped), their turn ends with it, and the next in line loads instead.
        let line = self.line_for(key);
        let turn = line.lock().await;
        let answer = match self.read(key).await {
            Some(copy) => Ok(copy), // loaded by whoever was ahead of us
            None => match load().await {
                Ok(value) => {
                    self.write(key, &value, ttl).await;
                    Ok(value)
                }
                Err(e) => Err(e),
            },
        };
        drop(turn);
        self.leave_line(key, &line);
        answer
    }

    /// The current number for a family of keys, like "menu". Every key in the family has it inside.
    pub async fn generation(&self, family: &str) -> i64 {
        match self.store.get(&format!("gen:{family}")).await {
            Ok(Some(bytes)) => String::from_utf8_lossy(&bytes).parse().unwrap_or(0),
            Ok(None) => 0,
            Err(e) => {
                tracing::warn!(family, cause = %e, "cache generation read failed");
                0
            }
        }
    }

    /// A new generation: every old key in the family is never read again, and soon expires.
    pub async fn bump(&self, family: &str) {
        if let Err(e) = self.store.incr(&format!("gen:{family}")).await {
            tracing::error!(family, cause = %e, "cache bump FAILED: old copies may show until they expire");
        }
    }

    async fn read<T: DeserializeOwned>(&self, key: &str) -> Option<T> {
        match self.store.get(key).await {
            Ok(Some(bytes)) => serde_json::from_slice(&bytes).ok(), // a copy we can't read is a miss
            Ok(None) => None,
            Err(e) => {
                tracing::warn!(key, cause = %e, "cache read failed, using the database");
                None
            }
        }
    }

    async fn write<T: Serialize>(&self, key: &str, value: &T, ttl: Duration) {
        let bytes = serde_json::to_vec(value).expect("cached values are always JSON");
        // Copies made at the same moment shouldn't all expire at the same moment.
        let random = f64::from(getrandom::u32().unwrap_or(0)) / f64::from(u32::MAX);
        if let Err(e) = self.store.set(key, &bytes, ttl + ttl.mul_f64(random / 10.0)).await {
            tracing::warn!(key, cause = %e, "cache write failed");
        }
    }

    fn line_for(&self, key: &str) -> Arc<tokio::sync::Mutex<()>> {
        self.loading.lock().unwrap().entry(key.to_owned()).or_default().clone()
    }

    /// The last one out takes the line away, so the map doesn't grow for ever.
    fn leave_line(&self, key: &str, line: &Arc<tokio::sync::Mutex<()>>) {
        let mut lines = self.loading.lock().unwrap();
        if Arc::strong_count(line) == 2 {
            lines.remove(key); // only the map and us still hold it
        }
    }
}
```

(`MemoryStore`, in `src/cache/memory.rs`, is the same three methods over a `HashMap` behind a `Mutex`, for tests.)

Three protections are built in, each for a real failure.

**1. Redis down means slower, not broken.** `read` turns any error into a miss, with a log line; `write` and `bump` log and carry on. So when Redis can't be reached, every request goes to Postgres, exactly as before this lesson. The only cost is time.

**2. A stampede becomes one query.** Picture 12:30. The menu's copy expires. In the next 50 milliseconds, 200 requests miss. Without care, that's 200 identical queries hitting Postgres at once, at its busiest moment. So everyone who misses a key joins a **line** for it, a `tokio::sync::Mutex` kept per key. The first in line loads; the rest wait. When their turn comes, each reads the cache *again*, finds the copy the first one wrote, and never touches Postgres.

This line is where Rust differs most from Go. Go's version of this helper had a trap: the first caller's load ran on behalf of everyone waiting, so if *that* customer closed their app, the load was cancelled, and everyone waiting got "context canceled". The fix needed a special context that ignores cancelling. Here, there's nothing to fix. If the first caller's request is dropped, their future is dropped, and their `turn` (a `MutexGuard`) is dropped with it, which unlocks the line. The next in line reads, misses, and loads instead. Nobody else sees an error. Dropping is cancelling, and cleaning up after a cancel is just `Drop`.

`std::sync::Mutex` guards the map of lines, because it's held for a moment and never across an `.await`. `tokio::sync::Mutex` is each line, because it *is* held across `.await`: the whole load happens while it's locked. `leave_line` removes a line when nobody else holds it. `Arc::strong_count` counts the map's copy and ours, so 2 means nobody else is waiting.

**3. Jitter spreads out expiry.** Cache 50 things at the same moment with the same TTL, and they all expire at the same moment too: 50 misses together. A random extra, up to a tenth of the TTL, spreads them out.

And note what `get_or_load` is: a **method with type parameters of its own**, `T`, `E`, `F` and `Fut`, on a `Cache` that isn't generic at all. Go doesn't allow that (methods can't add type parameters there), so Go's version is a plain function. Rust does. `load` is any closure that returns a future: `|| async { ... }`, the closure-returning-a-future shape you'll see all through async Rust.

## Step 3: cache at the right layer
<!-- bite: 0784dbe9-dbe4-414b-8441-e6290e887b10 -->

Where does the cache go? Not around the whole HTTP response. v1 and v2 send different shapes for the same dish (lesson 10), and field selection (lesson 9) changes the shape again. Cache whole responses, and one day a v1 answer is handed to a v2 phone.

So we cache the **data**, in the menu service, and the version's shapes are made *after* the cache, on every request:

```text
request → handler → V::Dish::from(dish) ← MenuService → cache → store → Postgres
                                              ↑ cached here: the same dishes for everyone
```

In `src/menu/service.rs`:

```rust
/// How old a copy of the menu may be. Edits clear it at once; this is the backstop, and the limit
/// on how stale `portionsLeft` can get (orders don't clear it: see the lesson).
const MENU_TTL: Duration = Duration::from_secs(10);
```

and the reads:

```rust
    /// One page of dishes, and how many match in all. The same for everyone, so it's cached.
    pub async fn list(&self, filter: &DishFilter) -> Result<(Vec<Dish>, i64), MenuError> {
        let generation = self.cache.generation("menu").await;
        // Each different filter is a different answer, so it gets its own key: a hash of every field.
        let hash = Sha256::digest(format!("{filter:?}"));
        let key = format!("menu:{generation}:list:{}", hex::encode(&hash[..12]));
        self.cache.get_or_load(&key, MENU_TTL, || async { Ok(self.store.list(filter).await?) }).await
    }
```

```rust
    pub async fn get(&self, id: i64) -> Result<Dish, MenuError> {
        let key = format!("menu:{}:dish:{id}", self.cache.generation("menu").await);
        self.cache.get_or_load(&key, MENU_TTL, || async { self.store.find(id).await?.ok_or(MenuError::NotFound(id)) }).await
    }
```

(`MenuService::new` now takes the `Cache` too. `main` builds it from `CACHE_REDIS_URL`, and so does lesson 18's worker, because the photo job changes the menu and must clear the API's copies.)

A few things to see:

1. **Each different filter is a different answer**, so each gets its own key. `format!("{filter:?}")` writes out every field of the `DishFilter` (that's what `#[derive(Debug)]` gives it), and a SHA-256 hash of that text keeps the key a sensible length. The filter has already been checked by lesson 9's `ValidatedQuery`, so there's a limited set of shapes. **Never build cache keys from raw, unchecked input**: a stranger could fill your cache with junk keys.
2. **Nothing about *who* is asking goes in the key.** The menu is the same for everyone. If a query ever depended on the caller ("dishes I've favourited"), it would need the user's id in the key, or, better, not be cached in a shared cache at all.
3. **Errors aren't kept.** `get`'s `load` turns "no such dish" into `MenuError::NotFound`, and `get_or_load` passes errors on without keeping them, so the next request asks again. (Keeping "not found" for a few seconds is called **negative caching**. It helps when attackers ask for missing ids on purpose. Add it when you need it.)
4. **The domain `Dish` is kept as JSON.** That needs `Serialize` and `Deserialize` on `Dish` (and `Kobo`, with `#[serde(transparent)]`, so it's just the number). Lesson 10 kept JSON out of domain types, and this doesn't break that rule: clients never see this JSON. It's our own copy, read back by the same program. If a deploy renames a field, copies made by the *old* program don't decode, `read` treats them as misses, and they're replaced. The 10-second TTL means that lasts seconds.
5. **`specials` goes through `list`** now, so it's cached too.
6. **The guarded `UPDATE` still decides orders.** `OrderService::place` reads the dish through `menu.get`, so it may see a cached dish. That's fine for its friendly early checks ("no such dish", "not available"). The plates are taken by lesson 8's guarded statement, which reads the real row.

## Step 4: keeping it honest, with generations
<!-- bite: 2041752e-36ad-434d-a6d9-23c83cb26be4 -->

Now the hard part, the one in the famous joke ("there are only two hard things in computer science: cache invalidation and naming things").

When Mama changes the price of jollof, which keys must go? `menu:...:dish:1`, obviously. But also *every* list that contains jollof: page 1, page 1 sorted by price, the search for "rice", the filter for "under ₦2,000"... We don't know which of those exist, and searching Redis for them (`KEYS menu:*`) is slow and blocks Redis while it runs.

So we don't find them. We make them unreachable. Every menu key has a **generation number** in it: `menu:7:list:...`. When anything on the menu changes, `bump("menu")` adds one with Redis's `INCR`. Now every request builds keys starting `menu:8:`, which don't exist yet, so they miss and load fresh data. The old `menu:7:` keys are never read again, and their TTLs clear them away.

One `INCR`, and the whole menu cache is new. It costs one extra tiny Redis read per request (the generation), and that's worth it.

Every write in `MenuService` ends with a bump:

```rust
    pub async fn add(&self, mut new: NewDish) -> Result<Dish, MenuError> {
        new.name = new.name.trim().to_string();
        if new.name.is_empty() {
            return Err(MenuError::NoName);
        }
        if new.price <= Kobo(0) {
            return Err(MenuError::BadPrice);
        }
        let dish = self.store.add(new).await?;
        self.cache.bump("menu").await; // after the write: never before
        Ok(dish)
    }
```

and `change`, `set_photo`, `set_processed_photo` (only when it changed something) and `remove` the same.

The order matters: **write to the database first, then bump.** Bump first, and a request in between could load the *old* data under the *new* generation, and keep it for 10 seconds.

And what if the bump fails, because the cache Redis is down at that moment? The old copies stay until their TTL runs out: at most 10 seconds of stale menu. That's why there's a TTL at all, even though edits clear the cache: it's the backstop that limits how wrong the cache can ever be. **Always set a TTL**, even on things you clear by hand.

Placing an order changes `portionsLeft` but doesn't bump. That's the choice from step 1: at lunch, bumping on every order would empty the cache every few seconds, and the cache would do nothing. Ten seconds of slightly old portion counts is the price, and the guarded `UPDATE` makes it safe to pay.

Against real Redis:

```bash
for i in 1 2 3; do curl -s -o /dev/null -w "menu read $i: %{time_total}s\n" localhost:8080/v2/menu; done
redis-cli -p 6380 --scan
```

```text
menu read 1: 0.032329s
menu read 2: 0.002606s
menu read 3: 0.002591s
menu:0:list:e5990e91b1ee821f1e6f539a
```

32 ms for the first, from Postgres; under 3 ms after, from the copy. Edit a dish, and `redis-cli -p 6380 get gen:menu` says `1`: every key now starts `menu:1:`.

## Step 5: HTTP caching, so phones don't even ask
<!-- bite: 91be490d-4c6c-46a6-8a24-39924241b3de -->

Redis saves Postgres the work. HTTP caching can save the *download*.

**`ETag` and 304.** An `ETag` is a short fingerprint of a response's body. When the phone asks again, it sends `If-None-Match: <that fingerprint>`. If the new body has the same fingerprint, we answer **304 Not Modified** with no body, and the phone uses the copy it has. On a slow mobile connection, 200 bytes of headers instead of the whole menu is a real difference.

Axum doesn't add ETags to the JSON you send; that's for you to choose. (tower-http's `ServeDir`, which serves lesson 14's photos, already does for files.) `src/http/caching.rs`:

```rust
//! HTTP caching: an `ETag` so a phone that already has the answer gets a tiny 304, and `Cache-Control`
//! saying who may keep a copy, and for how long.

use axum::{
    body::Body,
    http::{HeaderMap, HeaderValue, StatusCode, header},
    response::{IntoResponse, Response},
};
use base64::{Engine, engine::general_purpose::URL_SAFE_NO_PAD};
use serde::Serialize;
use sha2::{Digest, Sha256};
use tower_http::set_header::SetResponseHeaderLayer;

/// For the menu: the same for everyone, so any cache (the phone, a CDN) may keep it for 10 seconds.
pub const PUBLIC_10S: HeaderValue = HeaderValue::from_static("public, max-age=10");

/// `body` as JSON, with an `ETag`. If the request's `If-None-Match` already names that `ETag`,
/// the answer is 304 with no body: the client uses the copy it has.
pub fn cacheable(request: &HeaderMap, body: &impl Serialize, cache_control: HeaderValue) -> Response {
    let bytes = serde_json::to_vec(body).expect("a response body is always JSON");
    let hash = Sha256::digest(&bytes);
    let etag = format!("\"{}\"", URL_SAFE_NO_PAD.encode(&hash[..12]));

    let has_it = request
        .get(header::IF_NONE_MATCH)
        .and_then(|v| v.to_str().ok())
        .is_some_and(|tags| tags.split(',').any(|tag| tag.trim() == etag || tag.trim() == "*"));
    let mut response = if has_it {
        StatusCode::NOT_MODIFIED.into_response()
    } else {
        ([(header::CONTENT_TYPE, "application/json")], Body::from(bytes)).into_response()
    };
    let headers = response.headers_mut();
    headers.insert(header::ETAG, HeaderValue::from_str(&etag).expect("base64 is a valid header"));
    headers.insert(header::CACHE_CONTROL, cache_control);
    response
}

/// For anything personal (orders, payments, accounts): no copy anywhere, not even on the phone's disk.
pub fn no_store() -> SetResponseHeaderLayer<HeaderValue> {
    SetResponseHeaderLayer::if_not_present(header::CACHE_CONTROL, HeaderValue::from_static("no-store"))
}
```

1. **The fingerprint is a hash of the body's bytes**, so the same answer always has the same `ETag`, on any server, after any restart.
2. **A 304 still carries `ETag` and `Cache-Control`**, as the HTTP rules require, but no body.
3. **`Cache-Control: public, max-age=10`** tells the phone, and any shared cache between us (a CDN, lesson 36), that it may reuse this answer for 10 seconds without asking at all. The menu is the same for everyone, so `public` is right.
4. **`no-store` for anything personal.** Orders, payments and accounts must never be kept, not even on the phone's disk: a shared computer at a cyber café shouldn't keep Ada's order history. It's a Tower layer from tower-http, `if_not_present` so a route can still choose otherwise.

This saves the download, not our work: we still build the body to fingerprint it. Redis is what saves our work. Together, a lunchtime menu refresh is one Redis read, a hash, and 200 bytes on the wire.

The menu's `list` and `get_one` handlers take the request's headers, and answer with `cacheable` instead of `Data`:

```rust
async fn get_one<V: MenuVersion>(
    State(menu): State<MenuService>,
    headers: HeaderMap,
    Path(id): Path<i64>,
) -> Result<Response, ApiError> {
    let dish: V::Dish = menu.get(id).await?.into();
    Ok(cacheable(&headers, &Envelope { data: dish }, PUBLIC_10S))
}
```

`Envelope` is lesson 7's `{"data": ...}` shape, its field now `pub` so it can be built here. And in `src/lib.rs`, the personal routers get `no_store`:

```rust
        .merge(orders::router::<_, version::V2>().route_layer(idempotent.clone()).layer(http::no_store()))
        .merge(payments::router().route_layer(idempotent).layer(http::no_store()))
        .merge(auth::router(state.login_limiter.clone()).layer(http::no_store()))
```

(v1's orders router too.) A `layer` on a router wraps only that router's routes, so the menu keeps its own `Cache-Control`.

```bash
curl -si localhost:8080/v2/menu | grep -iE '^(HTTP|etag|cache-control)'
curl -si localhost:8080/v2/menu -H 'If-None-Match: "1BWjKLor-HeUZfio"' | grep -iE '^(HTTP|etag)'
```

```text
HTTP/1.1 200 OK
etag: "1BWjKLor-HeUZfio"
cache-control: public, max-age=10
HTTP/1.1 304 Not Modified
etag: "1BWjKLor-HeUZfio"
```

Change a dish, and the same `If-None-Match` gets a 200 with the new menu: a new body is a new fingerprint.

## Step 6: rate limits, shared at last
<!-- bite: 21f77d56-dfd8-42a1-92bc-17b2d01e8bd7 -->

Now that Redis is running, the login counts can live there, so every copy of the app sees the same numbers. In the limits Redis, of course, never the cache one.

The simplest shared limit is a **fixed window**: count requests per address per minute, in a key that expires soon after its minute ends. `src/http/shared_limit.rs`:

```rust
//! A rate limit every copy of the app shares, counted in Redis. If Redis can't be reached,
//! each copy falls back to its own in-memory limit (lesson 14's), so there's always a limit.

use std::{
    net::IpAddr,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

use axum::{
    extract::{Request, State},
    http::{HeaderValue, StatusCode, header},
    middleware::Next,
    response::{IntoResponse, Response},
};
use redis::aio::ConnectionManager;

use super::{ApiError, ClientIp, RateLimiter};

/// `limit` requests per `window` for each client address, counted in Redis.
#[derive(Clone)]
pub struct SharedLimit {
    /// `None`: no Redis at all (in tests), so only the fallback counts.
    redis: Option<ConnectionManager>,
    name: &'static str,
    limit: i64,
    window: Duration,
    fallback: RateLimiter,
}

impl SharedLimit {
    pub fn new(redis: ConnectionManager, name: &'static str, limit: i64, window: Duration, fallback: RateLimiter) -> Self {
        SharedLimit { redis: Some(redis), name, limit, window, fallback }
    }

    /// Only this program's own memory: for tests, and for running without Redis.
    pub fn local(fallback: RateLimiter) -> Self {
        SharedLimit { redis: None, name: "local", limit: 0, window: Duration::from_secs(60), fallback }
    }

    /// Counts one request from `ip`. `Err` says how long to wait.
    pub async fn take(&self, ip: IpAddr) -> Result<(), Duration> {
        let Some(redis) = &self.redis else {
            return self.fallback.check(ip, Instant::now());
        };
        let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("after 1970").as_secs();
        let window = self.window.as_secs();
        // One key per address per window: `rl:login:203.0.113.7:29591365`. A new window is a new key.
        let key = format!("rl:{}:{ip}:{}", self.name, now / window);
        let counted: redis::RedisResult<(i64,)> = redis::pipe()
            .atomic() // MULTI ... EXEC: nothing can land between the two
            .incr(&key, 1)
            .expire(&key, window as i64) // gone soon after its window ends
            .ignore()
            .query_async(&mut redis.clone())
            .await;
        match counted {
            Ok((count,)) if count > self.limit => Err(Duration::from_secs(window - now % window)),
            Ok(_) => Ok(()),
            Err(e) => {
                tracing::warn!(cause = %e, "shared rate limit unreachable; using this server's own");
                self.fallback.check(ip, Instant::now())
            }
        }
    }
}
```

1. **One key per address per window.** `now / window` is the number of the current minute since 1970, so `rl:login:203.0.113.7:29923000` is this address's count for this minute, and the next minute is a new key starting from nothing. The `EXPIRE` only clears old keys away.
2. **`redis::pipe().atomic()`** sends `INCR` and `EXPIRE` together, in one round trip, as one Redis transaction (`MULTI` ... `EXEC`), so no other command can land between them. `.ignore()` drops `EXPIRE`'s answer, so the result is just the count, as a one-item tuple.
3. **If Redis can't be reached, it falls back to lesson 14's in-memory buckets.** Failing open completely would switch off the login limit exactly when someone has knocked Redis over; failing closed would lock every customer out. The local limit is the middle way: per server, but still a limit.
4. **`SharedLimit::local`** has no Redis at all. `TestApp` uses it, so tests keep lesson 14's limit and need no Redis.

The middleware is lesson 14's, calling `take` instead of `check`. `auth::router` takes a `SharedLimit`, `AppState.login_limiter` is one, and `main` builds it:

```rust
    // Ten tries a minute from one address, counted across every copy of the app: plenty for a person,
    // useless for a guessing program. If that Redis is down, each copy keeps lesson 14's own limit.
    let fallback = RateLimiter::new(10, Duration::from_secs(6), http.behind_proxy);
    let limits = cache::connect_lazily(&env("LIMITS_REDIS_URL")?)?;
    let login_limiter = SharedLimit::new(limits, "login", 10, Duration::from_secs(60), fallback);
    let staff_key = StaffKey::from_env()?;
```

A fixed window has one known weakness: a caller can use all ten tries at 12:00:59 and ten more at 12:01:00, twenty in two seconds. For a login limit, that's fine: it still stops a guessing program from making thousands of tries.

```bash
for i in $(seq 1 11); do
  curl -s -o /dev/null -w "%{http_code} " localhost:8080/v2/auth/login \
    -H 'content-type: application/json' -d '{"email":"nobody@example.com","password":"guess-guess-guess"}'
done
redis-cli -p 6381 --scan
```

```text
401 401 401 401 401 401 401 401 401 401 429
rl:login:127.0.0.1:29923000
```

Ten wrong guesses, then 429 with `retry-after: 12`, the seconds left in this minute. The key's value is `11`, and its TTL `60`.

## Step 7: the cache going down, for real
<!-- bite: 6f8e390e-bc00-4bfe-9f58-55a66c417d06 -->

Stop the cache Redis while the app runs:

```bash
redis-cli -p 6380 shutdown nosave
curl -s -o /dev/null -w "menu with the cache down: %{http_code} in %{time_total}s\n" localhost:8080/v2/menu
```

```text
menu with the cache down: 200 in 0.071403s
```

and the log says why it was slower:

```text
WARN request{method=GET path="/v2/menu" ...}: mama_put::cache: cache read failed, using the database key="menu:0:list:e5990e91b1ee821f1e6f539a" cause=cache: Connection refused (os error 111)
```

Start it again, and the next read is back to 3 ms, with no restart of the app: the `ConnectionManager` remade its connection by itself.

## Step 8: what the cache must never hold
<!-- bite: 07e67a15-a907-4ba9-ad2b-baff3dc75922 -->

Before testing, one list worth keeping on the wall:

1. **Anything personal in a shared key.** Orders, payments, profiles. If it belongs to one person, it doesn't go in a cache everyone reads.
2. **Anything a decision rests on.** Plates left when placing an order, a user's role for a permission check, a payment's status for "may the kitchen cook this". Decide from the database.
3. **Secrets.** Tokens, keys, password hashes. A cache is a copy, and copies leak.
4. **Whole responses with a version or a view in them.** Cache the data; shape it per request.

## Step 9: testing the cache
<!-- bite: d46e5058-312c-4dfe-b7d8-88163469b3e4 -->

`Settings` in `tests/common/mod.rs` gains `cache: Cache`, `Cache::in_memory()` unless a test says otherwise, and `TestApp` keeps it as `app.cache`. Most whole-app tests behave the same with or without a cache, which is itself a good test: all 60 from before still pass. `tests/caching.rs` adds five.

**The one that matters most**, that an edit shows at once, and that orders still decide from Postgres:

```rust
#[sqlx::test]
async fn a_new_price_shows_straight_away(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let dish = app.dish("Jollof rice", 1500, 40).await;
    let price = || async { app.get(&format!("/v2/menu/{dish}")).send().await.body["data"]["price"]["amount"].clone() };

    assert_eq!(price().await, 150000);
    assert_eq!(price().await, 150000, "the second read comes from the cache");
    let change = app.patch(&format!("/v1/menu/{dish}")).header("x-staff-key", STAFF_KEY).json(json!({"priceNaira": 2000})).send().await;
    assert_eq!(change.status, StatusCode::OK);
    assert_eq!(price().await, 200000, "the edit cleared every copy");

    // Orders don't clear it: the cache may show an old count, but the order is decided by Postgres.
    sqlx::query!("UPDATE dishes SET portions_left = 0 WHERE id = $1", dish).execute(&app.pool).await.unwrap();
    assert_eq!(app.get(&format!("/v2/menu/{dish}")).send().await.body["data"]["portionsLeft"], 40, "an old count, for up to 10 s");
    let ada = app.user("ada@example.com", "customer").await;
    let order = app.post("/v2/orders").bearer(&ada).json(json!({"dishId": dish, "quantity": 1})).send().await;
    order.assert_problem(StatusCode::UNPROCESSABLE_ENTITY, "not-enough-portions");
}
```

**A broken cache**, a `CacheStore` whose every method fails: the menu still answers 200, and an edit still succeeds although its bump fails.

**The stampede**, with no database at all, just a slow pretend load that counts its calls:

```rust
#[tokio::test]
async fn a_stampede_is_one_load() {
    let cache = Cache::in_memory();
    let loads = Arc::new(AtomicUsize::new(0));
    let load = || async {
        loads.fetch_add(1, Ordering::SeqCst);
        tokio::time::sleep(Duration::from_millis(50)).await; // a slow query, at lunchtime
        Ok::<_, CacheError>("the menu".to_string())
    };

    let answers = join_all((0..20).map(|_| cache.get_or_load("menu:0:list:x", Duration::from_secs(10), load))).await;
    assert!(answers.iter().all(|a| a.as_deref().ok() == Some("the menu")));
    assert_eq!(loads.load(Ordering::SeqCst), 1, "twenty requests, one query");

    // The one loading gives up half-way (its request is dropped). The next in line loads instead.
    let first = cache.get_or_load("menu:0:list:y", Duration::from_secs(10), load);
    let gave_up = tokio::time::timeout(Duration::from_millis(10), first).await;
    assert!(gave_up.is_err());
    let next = cache.get_or_load("menu:0:list:y", Duration::from_secs(10), load).await;
    assert_eq!(next.as_deref().ok(), Some("the menu"), "someone else's give-up isn't our error");
}
```

`tokio::time::timeout` gives up on the first load after 10 ms, and dropping it is exactly what a closed app does to a request. The next caller still gets the menu.

**The ETag**: a `GET`, the same `GET` with its `ETag` in `If-None-Match` gets 304 with no body, and after an edit the same `If-None-Match` gets 200. And **nothing personal is kept**: `/v2/orders` and `/v2/auth/me` say `no-store`.

**A mutation check.** Take the `bump` out of `change` and run the tests. Two fail:

```text
test a_new_price_shows_straight_away ... FAILED
test a_phone_that_has_the_menu_gets_a_304 ... FAILED
assertion `left == right` failed: the edit cleared every copy
  left: Number(150000)
 right: 200000
```

Put it back.

```bash
cargo test
```

65 tests, all passing. (The Redis code itself isn't run by the tests: `MemoryStore` and `SharedLimit::local` stand in. Steps 4 to 7 are where it was checked against real Redis.)

## The Rust in this lesson
<!-- bite: 7652b013-9dd8-4363-86ec-2ac3a8ec819f -->

1. **A generic method on a type that isn't generic**, `fn get_or_load<T, E, F, Fut>(&self, ...)`: Rust lets a method bring type parameters of its own.
2. **`F: FnOnce() -> Fut, Fut: Future<Output = Result<T, E>>`**, and calling it with **`|| async { ... }`**: A closure that, when called, gives back a future. It's how you pass "some async work, to run later" to a function.
3. **`std::sync::Mutex` and `tokio::sync::Mutex`, side by side**: The first for things held for a moment, never across `.await`; the second for things held *across* `.await`.
4. **A `MutexGuard` dropped by cancelling**: When a future is dropped, everything it owns is dropped, locks included. That's why a cancelled load can't block the line.
5. **`Arc::strong_count`**: How many `Arc`s point at the same value right now.
6. **`entry(key).or_default()`**: Gets a map's value for a key, putting in a fresh default one first if there isn't one.
7. **`#[serde(transparent)]`**: A wrapper type that turns into JSON as just its inner value: `Kobo(150000)` is `150000`.
8. **`format!("{filter:?}")`**: The `Debug` text of a value, with every field: here, the source of a cache key.
9. **`AsyncCommands`**: The redis crate's trait that gives a connection methods like `get`, `pset_ex` and `incr`. Their answer type is chosen by what you ask for, `Option<Vec<u8>>` or `i64`.
10. **`redis::pipe().atomic()...query_async::<(i64,)>`**: Several commands in one round trip, in one Redis transaction. The answer's type is a tuple, one item per command not `.ignore()`d.
11. **`const` values**, `pub const PUBLIC_10S: HeaderValue = HeaderValue::from_static(...)`: Made when the program is compiled, so using one costs nothing.
12. **`Option::is_none_or`**: True for `None`, or for `Some` whose value passes the test.
13. **A module named after a crate**: Inside `cache`, a module called `redis` would hide the `redis` crate, so it's `redis_store`.

## Your project so far
<!-- bite: b6fbfc9e-b6a4-431f-957e-2c44151c2cc0 -->

```text
mama-put/
├── .env                          ← CACHE_REDIS_URL, LIMITS_REDIS_URL
├── Cargo.toml                    ← redis (tokio-comp, connection-manager)
├── src/
│   ├── main.rs                   ← a Cache on the cache Redis; SharedLimit on the limits Redis
│   ├── bin/worker.rs             ← the same Cache, so processed photos clear the API's copies
│   ├── lib.rs                    ← no_store on orders, payments and auth
│   ├── cache/                    ← NEW
│   │   ├── mod.rs                ← CacheStore, Cache: get_or_load (lines per key), generation, bump, jitter
│   │   ├── redis_store.rs        ← RedisStore; connect_lazily with 200 ms timeouts and no retries
│   │   └── memory.rs             ← MemoryStore, for tests
│   ├── http/
│   │   ├── caching.rs            ← NEW: cacheable (ETag, 304, Cache-Control), no_store
│   │   ├── shared_limit.rs       ← NEW: SharedLimit (fixed window in Redis, falls back to RateLimiter)
│   │   └── error.rs              ← Envelope.data is pub
│   ├── menu/
│   │   ├── service.rs            ← list and get through the cache; every write bumps "menu"
│   │   ├── handlers.rs           ← list and get_one answer with cacheable
│   │   └── model.rs              ← Dish: Serialize, Deserialize (for the cache only)
│   ├── auth/handlers.rs          ← the login routes use SharedLimit
│   └── money.rs                  ← Kobo: Serialize, Deserialize, transparent
└── tests/
    ├── common/mod.rs             ← Settings.cache; SharedLimit::local
    └── caching.rs                ← NEW: 5 tests
```

## Common mistakes
<!-- bite: f3d5a0de-3a58-4c78-b781-d548a74fb8af -->

1. **Caching what a decision rests on.** Show from the cache; decide from the database.
2. **No TTL, because edits clear the cache.** One failed clear and the copy lives for ever. Always set a TTL.
3. **Bumping before writing.** A read in between keeps the old data under the new generation.
4. **Finding keys to delete with `KEYS`.** Slow, and it blocks Redis. Use generations.
5. **A cache error that fails the request.** The cache is a shortcut, not the truth. Log it and use the database.
6. **Long timeouts, or retries, on the cache.** A cache that takes a second is worse than no cache.
7. **One Redis for copies and counters.** Eviction throws away counters too. Keep what you can't lose apart.
8. **Caching whole responses.** Versions and field selection change the shape. Cache the data; shape it per request.
9. **Cache keys from unchecked input.** Check first, then hash.
10. **Personal responses without `no-store`.** Phones and shared computers keep them.

## Check your understanding
<!-- bite: d1b6027b-e9ad-4eb9-910f-1068addade04 -->

1. Why is it safe for the cached menu to show an old `portionsLeft`?
2. Redis is down. What happens to `GET /v2/menu`, and how long does it take?
3. 200 requests miss the same key at once. How many queries reach Postgres, and how?
4. The first request in line closes its app half-way through the load. What do the others see, and why is there nothing to fix in Rust?
5. How does one `INCR` make every cached list stale, without finding them?
6. Why must `add` write to Postgres *before* bumping the generation?
7. What does a phone get for `GET /v2/menu` with an `If-None-Match` that matches, and what does it save?
8. Why do the rate-limit counters live in a different Redis from the cache?

<details>
<summary>Answers, after your attempt</summary>

1. Because nothing is decided from it. An order takes plates with lesson 8's guarded `UPDATE` on the real row, so if the cache says 3 and there's 1, an order for 2 is refused correctly. The cache only shows.
2. It still answers 200. Every cache read fails within the 200 ms timeout, is logged and treated as a miss, and the request goes to Postgres. In practice it took about 70 ms.
3. One. Everyone who misses joins the key's line; the first loads and writes the copy, and the rest, when their turn comes, read the cache again and find it.
4. They see the menu. The dropped request's future is dropped, and its lock with it, so the next in line reads, misses and loads instead. In Rust, cancelling is dropping, and a lock is released on drop, so the cancel can't leave anyone stuck or pass its error on.
5. Every menu key has the generation inside it. `INCR` changes the generation, so every request now builds different keys, which miss and load fresh data. The old keys are never read again and expire by their TTL.
6. If it bumped first, a request between the bump and the write could load the old row and keep it under the new generation, for the whole TTL.
7. A 304 with no body, so it uses its own copy. It saves downloading the menu, though the server still builds the body to fingerprint it.
8. Because the cache must be allowed to evict when it's full, and counters must never be evicted: an evicted counter gives a guessing program fresh tries. One Redis server has one eviction policy.

</details>

## Practice
<!-- bite: fa6ffdc0-523a-437f-bce6-8625ca19f51b -->

1. Above `OrderService::get`, write one sentence saying why orders aren't cached, using step 1's table and step 8's list.
2. Add negative caching to `MenuService::get`: keep "no such dish" for 5 seconds. Write a test that a second request for a missing dish doesn't reach the store. (Hint: wrap a `MenuStore` that counts its calls.)
3. Write a test for `SharedLimit` against a real Redis, that runs only when `LIMITS_REDIS_URL` is set (`#[ignore]`, run with `cargo test -- --ignored`).
4. Add `Cache-Control: no-store` to `GET /v2/payments/{reference}` and check it in `nothing_personal_is_kept`. Is it already there? Why?
5. Count hits and misses: add two counters to `Cache`, and log them every minute from a task. Lesson 35 turns them into graphs.

**Done when** the second `GET /v2/menu` comes from Redis, an edit shows on the next read, a matching `If-None-Match` gets 304, eleven bad logins get a 429 counted in the limits Redis, stopping the cache Redis leaves the menu working, and `cargo test` runs 65 tests and passes.

## Before moving on
<!-- bite: 09bb0a6f-fbdb-48b4-bfe8-59c8cb96ded1 -->

The menu is fast now: one Redis read at lunchtime instead of a query, a 304 when the phone already has it, honest within a moment of every edit, and harmless when Redis is down. The login limit holds across every copy of the app.

But every answer is still something a phone has to *ask* for. The kitchen screen asks "any new orders?" every few seconds, all day, and nearly every answer is "no". It should be told the moment an order is paid, instead. That's real-time updates, the next lesson.

## Related
<!-- bite: f0ba6487-23e9-4539-abeb-cafc30c69273 -->

- [[backend/frameworks/axum/20-real-time|Next: Real-time Updates]]
- [[backend/frameworks/net-http/19-caching|The same lesson in net/http]] — `singleflight`, and the cancelled-load trap Rust doesn't have
- [[backend/frameworks/axum/14-security|Security]] — the rate limit this lesson shares
- [[backend/frameworks/axum/09-listing|Listing]] — the filters the cache keys are made from

## About this lesson
<!-- bite: f30ab8fa-ab27-4217-9540-96e51c0f5f68 -->

**Level:** Advanced. Lesson 19 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), Axum 0.8, redis 1.8 and Redis 7. Covers deciding what to cache and how stale is acceptable, two Redis servers for copies and counters, a lazy `ConnectionManager` with short timeouts and no retries, a cache-aside helper that fails open, a per-key line of async mutexes against stampedes and why cancelling needs no special care in Rust, jitter, caching data rather than responses, generations for invalidation and why a TTL is still needed, `ETag`, 304, `Cache-Control` and `no-store`, a fixed-window rate limit in Redis with an in-memory fallback, what never to cache, and testing with an in-memory store, a broken store and a mutation check.
