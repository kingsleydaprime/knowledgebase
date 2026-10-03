//! A cache in front of a slow store: an LRU cache with expiry, cache-aside with request coalescing, and the
//! arithmetic that says how much a cache takes off the database. The same numbers as the TypeScript lab.
use std::collections::{BTreeMap, HashMap};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, OnceLock};

pub type Clock = Arc<dyn Fn() -> u64 + Send + Sync>; // milliseconds

struct Entry<V> {
    value: V,
    expires: u64,
    used: u64, // when it was last used, as a position in `order`
}

struct Inner<V> {
    entries: HashMap<String, Entry<V>>,
    order: BTreeMap<u64, String>, // last use → key; the first entry is the least recently used
    tick: u64,
}

/// At most `max` entries, evicting the least recently used. The standard library has no LRU (crates such as
/// `lru` and `moka` do), so a HashMap finds entries and a BTreeMap keeps them in order of last use.
pub struct LruCache<V> {
    max: usize,
    now: Clock,
    inner: Mutex<Inner<V>>,
}

impl<V: Clone> LruCache<V> {
    pub fn new(max: usize, now: Clock) -> Self {
        assert!(max >= 1, "a cache needs room for at least one entry");
        LruCache {
            max,
            now,
            inner: Mutex::new(Inner {
                entries: HashMap::new(),
                order: BTreeMap::new(),
                tick: 0,
            }),
        }
    }

    pub fn get(&self, key: &str) -> Option<V> {
        let mut inner = self.inner.lock().unwrap();
        let Inner {
            entries,
            order,
            tick,
        } = &mut *inner;
        let entry = entries.get_mut(key)?;
        order.remove(&entry.used);
        if (self.now)() >= entry.expires {
            entries.remove(key); // expired: treat it as a miss
            return None;
        }
        *tick += 1;
        entry.used = *tick; // now the most recently used
        order.insert(*tick, key.to_string());
        Some(entry.value.clone())
    }

    pub fn set(&self, key: &str, value: V, ttl_ms: u64) {
        let mut inner = self.inner.lock().unwrap();
        let Inner {
            entries,
            order,
            tick,
        } = &mut *inner;
        *tick += 1;
        let expires = (self.now)().saturating_add(ttl_ms); // u64::MAX means "never", and mustn't wrap round
        if let Some(old) = entries.insert(
            key.to_string(),
            Entry {
                value,
                expires,
                used: *tick,
            },
        ) {
            order.remove(&old.used);
        }
        order.insert(*tick, key.to_string());
        if entries.len() > self.max {
            let (_, oldest) = order.pop_first().expect("not empty");
            entries.remove(&oldest);
        }
    }

    pub fn delete(&self, key: &str) {
        let mut inner = self.inner.lock().unwrap();
        if let Some(old) = inner.entries.remove(key) {
            inner.order.remove(&old.used);
        }
    }

    /// Least recently used first.
    pub fn keys(&self) -> Vec<String> {
        self.inner.lock().unwrap().order.values().cloned().collect()
    }
}

pub type Loader<V> = Box<dyn Fn(&str) -> V + Send + Sync>;

/// Check the cache; on a miss, load and fill it. With `coalesce`, concurrent misses share one load.
pub struct CacheAside<V> {
    cache: Arc<LruCache<V>>,
    load: Loader<V>,
    ttl_ms: u64,
    coalesce: bool,
    in_flight: Mutex<HashMap<String, Arc<OnceLock<V>>>>,
    pub hits: AtomicU64,
    pub misses: AtomicU64,
}

impl<V: Clone> CacheAside<V> {
    pub fn new(cache: Arc<LruCache<V>>, load: Loader<V>, ttl_ms: u64, coalesce: bool) -> Self {
        let (hits, misses) = (AtomicU64::new(0), AtomicU64::new(0));
        CacheAside {
            cache,
            load,
            ttl_ms,
            coalesce,
            in_flight: Mutex::new(HashMap::new()),
            hits,
            misses,
        }
    }

    pub fn get(&self, key: &str) -> V {
        if let Some(value) = self.cache.get(key) {
            self.hits.fetch_add(1, Ordering::Relaxed);
            return value;
        }
        if !self.coalesce {
            self.misses.fetch_add(1, Ordering::Relaxed);
            return self.load_and_fill(key);
        }
        let cell = self
            .in_flight
            .lock()
            .unwrap()
            .entry(key.to_string())
            .or_default()
            .clone();
        self.misses.fetch_add(1, Ordering::Relaxed);
        // get_or_init runs exactly one initialiser; every other caller blocks until it's done, then shares the value.
        let mut loaded_here = false;
        let value = cell
            .get_or_init(|| {
                loaded_here = true;
                self.load_and_fill(key)
            })
            .clone();
        if loaded_here {
            self.in_flight.lock().unwrap().remove(key);
        }
        value
    }

    fn load_and_fill(&self, key: &str) -> V {
        let value = (self.load)(key);
        self.cache.set(key, value.clone(), self.ttl_ms);
        value
    }

    /// Write to the store first, then delete the cached copy.
    pub fn write(&self, key: &str, value: V, save: impl FnOnce(&str, V)) {
        save(key, value);
        self.cache.delete(key);
    }
}

pub fn hit_ratio(hits: u64, misses: u64) -> f64 {
    hits as f64 / (hits + misses) as f64
}

pub fn average_read_ms(ratio: f64, cache_ms: f64, store_ms: f64) -> f64 {
    cache_ms + (1.0 - ratio) * store_ms
}

pub fn store_reads_per_second(reads_per_second: f64, ratio: f64) -> f64 {
    reads_per_second * (1.0 - ratio)
}

pub fn jittered(ttl_ms: f64, spread: f64, random: &mut impl FnMut() -> f64) -> f64 {
    ttl_ms * (1.0 - spread + 2.0 * spread * random())
}

/// Key k is requested in proportion to 1/(k+1)^s.
pub fn zipf(keys: usize, s: f64, mut random: impl FnMut() -> f64) -> impl FnMut() -> usize {
    let mut total = 0.0;
    let cumulative: Vec<f64> = (0..keys)
        .map(|k| {
            total += 1.0 / ((k + 1) as f64).powf(s);
            total
        })
        .collect();
    move || {
        let target = random() * total;
        cumulative.partition_point(|&c| c < target) // the first total at or above the target
    }
}

/// mulberry32, the same generator as week 1's lab.
pub fn seeded(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = (a ^ (a >> 15)).wrapping_mul(a | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4_294_967_296.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Condvar;
    use std::sync::atomic::AtomicBool;

    fn clock() -> (Arc<AtomicU64>, Clock) {
        let now = Arc::new(AtomicU64::new(0));
        let read = now.clone();
        (now, Arc::new(move || read.load(Ordering::SeqCst)))
    }

    /// A one-time gate: threads wait at it until the test opens it. Rust's standard library has no latch.
    #[derive(Default)]
    struct Gate {
        open: Mutex<bool>,
        opened: Condvar,
    }

    impl Gate {
        fn wait(&self) {
            let _open = self
                .opened
                .wait_while(self.open.lock().unwrap(), |open| !*open)
                .unwrap();
        }
        fn open(&self) {
            *self.open.lock().unwrap() = true;
            self.opened.notify_all();
        }
    }

    #[test]
    fn a_full_lru_cache_evicts_the_entry_used_longest_ago() {
        let cache = LruCache::new(3, clock().1);
        for k in ["a", "b", "c"] {
            cache.set(k, k.to_uppercase(), 1_000);
        }
        cache.get("a");
        cache.set("d", "D".into(), 1_000);
        assert_eq!(cache.keys(), ["c", "a", "d"]);
        assert_eq!(cache.get("b"), None);
    }

    #[test]
    fn an_entry_expires_after_its_ttl() {
        let (now, clock) = clock();
        let cache = LruCache::new(10, clock);
        cache.set("price:42", 10, 60_000);
        now.store(59_999, Ordering::SeqCst);
        assert_eq!(cache.get("price:42"), Some(10));
        now.store(60_000, Ordering::SeqCst);
        assert_eq!(cache.get("price:42"), None);
    }

    #[test]
    fn cache_aside_first_read_misses_the_rest_hit() {
        let loads = Arc::new(AtomicU64::new(0));
        let counted = loads.clone();
        let load: Loader<String> = Box::new(move |_| {
            counted.fetch_add(1, Ordering::SeqCst);
            "kettle".into()
        });
        let products =
            CacheAside::new(Arc::new(LruCache::new(100, clock().1)), load, 60_000, false);
        for _ in 0..5 {
            assert_eq!(products.get("product:7"), "kettle");
        }
        let (hits, misses) = (
            products.hits.load(Ordering::SeqCst),
            products.misses.load(Ordering::SeqCst),
        );
        assert_eq!((loads.load(Ordering::SeqCst), hits, misses), (1, 4, 1));
        assert_eq!(hit_ratio(hits, misses), 0.8);
    }

    #[test]
    fn the_hit_ratio_decides_what_the_database_sees() {
        assert_eq!(
            [0.8, 0.9, 0.99].map(|h| store_reads_per_second(5_000.0, h).round()),
            [1_000.0, 500.0, 50.0]
        );
        assert_eq!(
            [0.0, 0.8, 0.99].map(|h| format!("{:.1}", average_read_ms(h, 1.0, 20.0))),
            ["21.0", "5.0", "1.2"]
        );
        assert_eq!(store_reads_per_second(5_000.0, 0.0), 5_000.0);
    }

    #[test]
    fn skewed_traffic_a_small_cache_answers_most_reads() {
        let ratios = [500, 2_500, 5_000, 10_000].map(|size| {
            let mut next = zipf(50_000, 1.0, seeded(1));
            let cache = LruCache::new(size, clock().1);
            let (mut hits, mut misses) = (0, 0);
            for i in 0..200_000 {
                let key = next().to_string();
                let hit = cache.get(&key).is_some();
                if !hit {
                    cache.set(&key, true, u64::MAX);
                }
                if i >= 50_000 {
                    if hit { hits += 1 } else { misses += 1 }
                }
            }
            format!("{:.2}", hit_ratio(hits, misses))
        });
        assert_eq!(ratios, ["0.48", "0.65", "0.72", "0.80"]);
    }

    #[test]
    fn a_stampede_unless_misses_share_one_load() {
        for coalesce in [false, true] {
            let (now, clock) = clock();
            let (loads, gate) = (Arc::new(AtomicU64::new(0)), Arc::new(Gate::default()));
            let (counted, held) = (loads.clone(), gate.clone());
            let load: Loader<String> = Box::new(move |_| {
                counted.fetch_add(1, Ordering::SeqCst);
                held.wait(); // the database takes a while: held until all 100 callers have missed
                "kettle".into()
            });
            let cache = Arc::new(LruCache::new(100, clock));
            cache.set("product:7", "kettle".into(), 60_000);
            now.store(60_000, Ordering::SeqCst); // the entry expires as 100 reads arrive
            let products = CacheAside::new(cache, load, 60_000, coalesce);
            std::thread::scope(|s| {
                let readers: Vec<_> = (0..100)
                    .map(|_| s.spawn(|| products.get("product:7")))
                    .collect();
                while products.misses.load(Ordering::SeqCst) < 100 {
                    std::thread::yield_now();
                }
                gate.open();
                assert!(readers.into_iter().all(|r| r.join().unwrap() == "kettle"));
            });
            assert_eq!(loads.load(Ordering::SeqCst), if coalesce { 1 } else { 100 });
        }
    }

    #[test]
    fn delete_on_write_can_still_leave_a_stale_value() {
        let (now, clock) = clock();
        let db = Arc::new(Mutex::new(HashMap::from([("price:42".to_string(), 10)])));
        let (has_read, slow_read) = (Arc::new(Gate::default()), Arc::new(Gate::default()));
        let first = Arc::new(AtomicBool::new(true));
        let (store, signal, held) = (db.clone(), has_read.clone(), slow_read.clone());
        let load: Loader<i32> = Box::new(move |key| {
            let value = store.lock().unwrap()[key]; // the read happens now...
            if first.swap(false, Ordering::SeqCst) {
                signal.open();
                held.wait(); // ...but the answer is delayed
            }
            value
        });
        let prices = CacheAside::new(Arc::new(LruCache::new(100, clock)), load, 60_000, false);
        std::thread::scope(|s| {
            let reader = s.spawn(|| prices.get("price:42"));
            has_read.wait(); // 1. the reader has read 10
            prices.write("price:42", 12, |k, v| {
                db.lock().unwrap().insert(k.to_string(), v); // 2. the writer saves 12 and deletes (nothing)
            });
            slow_read.open();
            assert_eq!(reader.join().unwrap(), 10); // 3. the reader caches the old 10
        });
        assert_eq!(prices.get("price:42"), 10); // stale
        now.store(60_000, Ordering::SeqCst);
        assert_eq!(prices.get("price:42"), 12);
    }

    #[test]
    fn jitter_spreads_out_expiry() {
        let mut random = seeded(3);
        let expiries: Vec<f64> = (0..1_000)
            .map(|_| jittered(60_000.0, 0.1, &mut random))
            .collect();
        assert!(
            expiries
                .iter()
                .all(|&ms| (54_000.0..=66_000.0).contains(&ms))
        );
        let mut per_second = HashMap::new();
        for ms in &expiries {
            *per_second.entry((ms / 1_000.0) as u64).or_insert(0) += 1;
        }
        assert!(per_second.values().max().unwrap() < &120);
    }
}
