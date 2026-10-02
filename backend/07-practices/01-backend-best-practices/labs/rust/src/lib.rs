//! A token bucket over an injected clock. In Axum services, the `governor` crate (via
//! `tower_governor`) provides this as middleware.
use std::collections::HashMap;
use std::time::Duration;

pub trait Clock {
    /// Time since an arbitrary start; only differences matter.
    fn now(&self) -> Duration;
}

pub struct TokenBucket<C: Clock> {
    capacity: f64,
    per_second: f64,
    clock: C,
    buckets: HashMap<String, (f64, Duration)>,
}

#[derive(Debug, PartialEq)]
pub enum Decision {
    Allowed,
    Limited { retry_after_secs: u64 },
}

impl<C: Clock> TokenBucket<C> {
    pub fn new(capacity: f64, per_second: f64, clock: C) -> Self {
        TokenBucket {
            capacity,
            per_second,
            clock,
            buckets: HashMap::new(),
        }
    }

    pub fn take(&mut self, key: &str) -> Decision {
        let now = self.clock.now();
        let (tokens, at) = self
            .buckets
            .get(key)
            .copied()
            .unwrap_or((self.capacity, now));
        let tokens = (tokens + (now - at).as_secs_f64() * self.per_second).min(self.capacity);
        if tokens >= 1.0 {
            self.buckets.insert(key.into(), (tokens - 1.0, now));
            Decision::Allowed
        } else {
            self.buckets.insert(key.into(), (tokens, now));
            Decision::Limited {
                retry_after_secs: ((1.0 - tokens) / self.per_second).ceil() as u64,
            }
        }
    }

    pub fn clock(&self) -> &C {
        &self.clock
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;

    struct FakeClock(Cell<Duration>);
    impl Clock for FakeClock {
        fn now(&self) -> Duration {
            self.0.get()
        }
    }

    #[test]
    fn burst_then_refill() {
        let mut bucket = TokenBucket::new(3.0, 0.5, FakeClock(Cell::new(Duration::ZERO)));
        for _ in 0..3 {
            assert_eq!(bucket.take("u1"), Decision::Allowed);
        }
        assert_eq!(
            bucket.take("u1"),
            Decision::Limited {
                retry_after_secs: 2
            }
        );
        assert_eq!(bucket.take("u2"), Decision::Allowed);
        bucket.clock().0.set(Duration::from_secs(2));
        assert_eq!(bucket.take("u1"), Decision::Allowed);
    }
}
