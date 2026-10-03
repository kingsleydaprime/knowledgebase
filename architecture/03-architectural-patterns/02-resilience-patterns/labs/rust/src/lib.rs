//! A tick-by-tick simulation of a cascade, Little's law, and a bulkhead.
//! The same numbers as the TypeScript lab. One tick is 100 ms.
use std::collections::VecDeque;
use std::future::Future;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;
use tokio::sync::Semaphore;

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Kind {
    Search,
    Profile,
}
const KINDS: [Kind; 2] = [Kind::Search, Kind::Profile];

#[derive(Default, Debug, PartialEq)]
pub struct Counts {
    pub ok: usize,
    pub failed: usize,
    pub timed_out: usize,
    pub rejected: usize,
    pub unfinished: usize,
}

pub struct Config {
    /// The pool each kind uses, as an index into `sizes`: the same index means a shared pool.
    pub pool_of: fn(Kind) -> usize,
    /// Workers per pool, in the order pools start work.
    pub sizes: Vec<usize>,
    pub queue_limit: usize,
    pub dependency_timeout_ticks: usize,
}

pub struct Load {
    pub ticks: usize,
    pub arrivals_per_tick: fn(Kind) -> usize,
    pub service_ticks: fn(Kind) -> usize,
    pub client_timeout_ticks: usize,
}

struct Request {
    kind: Kind,
    arrived: usize,
    ends_at: usize,
    failed: bool,
}

/// Returns (search, profile) counts.
pub fn simulate(c: &Config, l: &Load) -> (Counts, Counts) {
    let mut counts: [Counts; 2] = Default::default(); // indexed by `kind as usize`
    let mut queues: Vec<VecDeque<Request>> = c.sizes.iter().map(|_| VecDeque::new()).collect();
    let mut running: Vec<Vec<Request>> = c.sizes.iter().map(|_| Vec::new()).collect();
    for t in 0..l.ticks {
        for busy in &mut running {
            // 1. finished work frees its worker
            busy.retain(|r| {
                if r.ends_at > t {
                    return true;
                }
                if r.failed {
                    counts[r.kind as usize].failed += 1;
                } else {
                    counts[r.kind as usize].ok += 1;
                }
                false
            });
        }
        for queue in &mut queues {
            // 2. callers who waited too long give up
            queue.retain(|r| {
                let gave_up = t - r.arrived >= l.client_timeout_ticks;
                if gave_up {
                    counts[r.kind as usize].timed_out += 1;
                }
                !gave_up
            });
        }
        for kind in KINDS {
            // 3. new requests arrive, or are turned away
            let queue = &mut queues[(c.pool_of)(kind)];
            for _ in 0..(l.arrivals_per_tick)(kind) {
                if queue.len() >= c.queue_limit {
                    counts[kind as usize].rejected += 1; // load shedding
                } else {
                    queue.push_back(Request {
                        kind,
                        arrived: t,
                        ends_at: 0,
                        failed: false,
                    });
                }
            }
        }
        for (pool, queue) in queues.iter_mut().enumerate() {
            // 4. free workers take requests, oldest first
            while running[pool].len() < c.sizes[pool] {
                let Some(mut r) = queue.pop_front() else {
                    break;
                };
                let needs = (l.service_ticks)(r.kind);
                let limit = if r.kind == Kind::Search {
                    c.dependency_timeout_ticks
                } else {
                    usize::MAX
                };
                (r.ends_at, r.failed) = (t + needs.min(limit), needs > limit);
                running[pool].push(r);
            }
        }
    }
    for r in queues.iter().flatten().chain(running.iter().flatten()) {
        counts[r.kind as usize].unfinished += 1;
    }
    let [search, profile] = counts;
    (search, profile)
}

/// Little's law: requests in the system = arrival rate × time each one stays.
pub fn workers_needed(per_second: f64, seconds: f64) -> f64 {
    per_second * seconds
}

#[derive(Debug, PartialEq)]
pub enum Refused {
    Full,
    WaitedTooLong,
}

/// tokio's Semaphore is fair: places go to waiters in the order they asked, so a latecomer can't barge in.
/// It has no queue limit, so a counter turns away callers beyond `max_queue`.
pub struct Bulkhead {
    places: Semaphore,
    waiting: AtomicUsize,
    max_queue: usize,
}

impl Bulkhead {
    pub fn new(max_concurrent: usize, max_queue: usize) -> Self {
        Self {
            places: Semaphore::new(max_concurrent),
            waiting: AtomicUsize::new(0),
            max_queue,
        }
    }

    pub async fn run<T>(
        &self,
        max_wait: Duration,
        f: impl Future<Output = T>,
    ) -> Result<T, Refused> {
        let _place = match self.places.try_acquire() {
            Ok(place) => place,
            Err(_) => {
                if self.waiting.fetch_add(1, Ordering::SeqCst) >= self.max_queue {
                    self.waiting.fetch_sub(1, Ordering::SeqCst);
                    return Err(Refused::Full); // a fast "no" beats a slow failure
                }
                // Dropping the acquire future on timeout takes the caller out of the queue.
                let got = tokio::time::timeout(max_wait, self.places.acquire()).await;
                self.waiting.fetch_sub(1, Ordering::SeqCst);
                got.map_err(|_| Refused::WaitedTooLong)?
                    .expect("never closed")
            }
        };
        Ok(f.await) // the place goes back when _place is dropped, even if f panics
    }

    pub fn free(&self) -> usize {
        self.places.available_permits()
    }

    pub fn waiting(&self) -> usize {
        self.waiting.load(Ordering::SeqCst)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use tokio::sync::Notify;

    const NONE: usize = usize::MAX;
    fn healthy() -> Load {
        Load {
            ticks: 600,
            arrivals_per_tick: |k| if k == Kind::Search { 2 } else { 3 },
            service_ticks: |k| if k == Kind::Search { 2 } else { 1 },
            client_timeout_ticks: 20,
        }
    }
    fn degraded() -> Load {
        Load {
            service_ticks: |k| if k == Kind::Search { 50 } else { 1 },
            ..healthy()
        }
    }
    fn shared(timeout: usize) -> Config {
        Config {
            pool_of: |_| 0,
            sizes: vec![50],
            queue_limit: NONE,
            dependency_timeout_ticks: timeout,
        }
    }

    #[test]
    fn littles_law() {
        assert_eq!(workers_needed(20.0, 0.2) + workers_needed(30.0, 0.1), 7.0);
        assert_eq!(workers_needed(20.0, 5.0), 100.0);
    }

    #[test]
    fn the_same_numbers_as_typescript() {
        let (search, profile) = simulate(&shared(NONE), &healthy());
        assert_eq!((search.ok, profile.ok), (1196, 1797));
        let (_, profile) = simulate(&shared(NONE), &degraded());
        assert_eq!((profile.ok, profile.timed_out), (72, 1668));
        assert_eq!(simulate(&shared(30), &degraded()).1.ok, 270);
        let (search, profile) = simulate(&shared(10), &degraded());
        assert_eq!((profile.ok, search.failed), (1797, 1180));
        let walls = Config {
            pool_of: |k| if k == Kind::Search { 0 } else { 1 },
            sizes: vec![20, 30],
            queue_limit: 10,
            dependency_timeout_ticks: 30,
        };
        let (search, profile) = simulate(&walls, &degraded());
        assert_eq!(profile.ok, 1797);
        assert_eq!(
            search,
            Counts {
                ok: 0,
                failed: 380,
                timed_out: 190,
                rejected: 600,
                unfinished: 30
            }
        );
    }

    #[tokio::test(start_paused = true)] // a fake clock: the waits below take no real time
    async fn a_limit_a_short_queue_and_an_immediate_no() {
        let bulkhead = Arc::new(Bulkhead::new(2, 1));
        let release = Arc::new(Notify::new());
        let calls: Vec<_> = (0..3)
            .map(|_| {
                let (b, r) = (bulkhead.clone(), release.clone());
                tokio::spawn(async move { b.run(Duration::from_secs(5), r.notified()).await })
            })
            .collect();
        while bulkhead.waiting() < 1 {
            tokio::task::yield_now().await;
        }
        assert_eq!(
            bulkhead.run(Duration::from_secs(5), async {}).await,
            Err(Refused::Full)
        );
        for _ in 0..3 {
            release.notify_one();
            tokio::task::yield_now().await;
        }
        for call in calls {
            assert_eq!(call.await.unwrap(), Ok(()));
        }
        assert_eq!((bulkhead.free(), bulkhead.waiting()), (2, 0));
    }

    #[tokio::test(start_paused = true)]
    async fn a_freed_place_goes_to_the_waiter_not_a_latecomer() {
        let bulkhead = Arc::new(Bulkhead::new(1, 2));
        let order = Arc::new(std::sync::Mutex::new(Vec::new()));
        let call = |name: &'static str, delay_ms: u64| {
            let (b, o) = (bulkhead.clone(), order.clone());
            tokio::spawn(async move {
                tokio::time::sleep(Duration::from_millis(delay_ms)).await;
                b.run(Duration::from_secs(5), async {
                    o.lock().unwrap().push(name);
                    tokio::time::sleep(Duration::from_secs(1)).await;
                })
                .await
            })
        };
        let calls = [
            call("first", 0),
            call("waiter", 10),
            call("latecomer", 1000),
        ]; // arrives as first finishes
        for c in calls {
            c.await.unwrap().unwrap();
        }
        assert_eq!(*order.lock().unwrap(), ["first", "waiter", "latecomer"]);
    }

    #[tokio::test(start_paused = true)]
    async fn a_caller_who_stops_waiting_leaves_the_queue() {
        let bulkhead = Arc::new(Bulkhead::new(1, 1));
        let release = Arc::new(Notify::new());
        let (b, r) = (bulkhead.clone(), release.clone());
        let first = tokio::spawn(async move { b.run(Duration::from_secs(5), r.notified()).await });
        tokio::task::yield_now().await;
        assert_eq!(
            bulkhead.run(Duration::from_secs(2), async {}).await,
            Err(Refused::WaitedTooLong)
        );
        assert_eq!(bulkhead.waiting(), 0);
        release.notify_one();
        first.await.unwrap().unwrap();
        assert_eq!(bulkhead.free(), 1); // the place came back instead of going to the caller who left
    }
}
