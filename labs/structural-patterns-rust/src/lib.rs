//! Decorators as generic wrapper structs: `Caching<Retrying<FlakyApi>>` is one concrete type,
//! so the compiler can inline the whole stack.
use std::cell::{Cell, RefCell};
use std::collections::HashMap;

pub trait RateSource {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String>;
}

pub struct FlakyApi {
    pub calls: Cell<u32>,
    pub failures: u32,
}
impl RateSource for FlakyApi {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        self.calls.set(self.calls.get() + 1);
        if self.calls.get() <= self.failures {
            return Err("503 from rates API".into());
        }
        Ok(if (base, quote) == ("GBP", "NGN") {
            2000
        } else {
            1
        })
    }
}

pub struct Retrying<S> {
    pub inner: S,
    pub attempts: u32,
}
impl<S: RateSource> RateSource for Retrying<S> {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        let mut last = Err("no attempts".to_string());
        for _ in 0..self.attempts {
            last = self.inner.rate(base, quote);
            if last.is_ok() {
                break;
            }
        }
        last
    }
}

pub struct Caching<S> {
    pub inner: S,
    cache: RefCell<HashMap<String, u64>>,
}
impl<S> Caching<S> {
    pub fn new(inner: S) -> Self {
        Caching {
            inner,
            cache: RefCell::default(),
        }
    }
}
impl<S: RateSource> RateSource for Caching<S> {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        let key = format!("{base}->{quote}");
        if let Some(v) = self.cache.borrow().get(&key) {
            return Ok(*v);
        }
        let v = self.inner.rate(base, quote)?;
        self.cache.borrow_mut().insert(key, v);
        Ok(v)
    }
}

// Adapter, forced by the orphan rule: you may not implement a trait you didn't define for a
// type you didn't define. To make a third-party client a RateSource, wrap it in your own type.
pub mod third_party {
    pub struct FxClient;
    impl FxClient {
        pub fn quote(&self, pair: (&str, &str)) -> f64 {
            if pair.0 == "USD" { 1500.0 } else { 1.0 }
        }
    }
}
pub struct FxAdapter(pub third_party::FxClient); // a "newtype"
impl RateSource for FxAdapter {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        Ok(self.0.quote((base, quote)) as u64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn retry_inside_cache() {
        let stack = Caching::new(Retrying {
            inner: FlakyApi {
                calls: Cell::new(0),
                failures: 2,
            },
            attempts: 3,
        });
        assert_eq!(stack.rate("GBP", "NGN"), Ok(2000));
        assert_eq!(stack.rate("GBP", "NGN"), Ok(2000));
        assert_eq!(stack.inner.inner.calls.get(), 3);
    }

    #[test]
    fn adapter_fits_the_same_stack() {
        assert_eq!(
            Caching::new(FxAdapter(third_party::FxClient)).rate("USD", "NGN"),
            Ok(1500)
        );
    }
}
