//! The same fee rules two ways. Open: a trait, so new methods are new types.
//! Closed: an enum, so a new method is a new variant the compiler makes you handle everywhere.
use std::collections::HashMap;

// ---- Open for extension: a trait object per payment method ----
pub trait FeeRule {
    fn fee(&self, amount_kobo: u64) -> u64;
}
pub struct Card;
impl FeeRule for Card {
    fn fee(&self, amount_kobo: u64) -> u64 {
        amount_kobo * 29 / 1000
    }
}
pub struct Transfer;
impl FeeRule for Transfer {
    fn fee(&self, _: u64) -> u64 {
        50
    }
}

pub fn open_rules() -> HashMap<&'static str, Box<dyn FeeRule>> {
    HashMap::from([
        ("card", Box::new(Card) as Box<dyn FeeRule>),
        ("transfer", Box::new(Transfer)),
    ])
}

// ---- Closed: an enum and one exhaustive match ----
pub enum Method {
    Card,
    Transfer,
}

pub fn fee(method: &Method, amount_kobo: u64) -> u64 {
    match method {
        Method::Card => amount_kobo * 29 / 1000,
        Method::Transfer => 50,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn both_designs_agree() {
        let rules = open_rules();
        assert_eq!(rules["card"].fee(10_000), 290);
        assert_eq!(rules["transfer"].fee(10_000), 50);
        assert_eq!(fee(&Method::Card, 10_000), 290);
        assert_eq!(fee(&Method::Transfer, 10_000), 50);
    }
}
