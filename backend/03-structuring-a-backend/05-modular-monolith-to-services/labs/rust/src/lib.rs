//! Modules talk through a channel: payments sends events, orders receives them.
//! std::sync::mpsc is the standard library's multi-producer, single-consumer channel.
use std::collections::{HashMap, HashSet};
use std::sync::mpsc::{Receiver, Sender, channel};

#[derive(Clone, Debug)]
pub struct PaymentSucceeded {
    pub event_id: String,
    pub order_id: String,
    pub amount_kobo: u64,
}

pub struct Payments {
    tx: Sender<PaymentSucceeded>,
    n: u32,
    pub deliver_twice: bool, // simulates a broker's at-least-once delivery
}

impl Payments {
    pub fn record_success(&mut self, order_id: &str, amount_kobo: u64) {
        self.n += 1;
        let event = PaymentSucceeded {
            event_id: format!("evt_{}", self.n),
            order_id: order_id.into(),
            amount_kobo,
        };
        if self.deliver_twice {
            self.tx.send(event.clone()).unwrap();
        }
        self.tx.send(event).unwrap();
    }
}

#[derive(Default)]
pub struct Orders {
    pub paid: HashMap<String, u64>,
    seen: HashSet<String>,
}

impl Orders {
    /// Handles every event waiting on the channel. `insert` returns false for a repeat.
    pub fn drain(&mut self, rx: &Receiver<PaymentSucceeded>, idempotent: bool) {
        for event in rx.try_iter() {
            if idempotent && !self.seen.insert(event.event_id.clone()) {
                continue;
            }
            *self.paid.entry(event.order_id).or_default() += event.amount_kobo;
        }
    }
}

pub fn wire(deliver_twice: bool) -> (Payments, Receiver<PaymentSucceeded>) {
    let (tx, rx) = channel();
    (
        Payments {
            tx,
            n: 0,
            deliver_twice,
        },
        rx,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn naive_consumer_double_counts() {
        let (mut payments, rx) = wire(true);
        let mut orders = Orders::default();
        payments.record_success("o1", 500_000);
        orders.drain(&rx, false);
        assert_eq!(orders.paid["o1"], 1_000_000);
    }

    #[test]
    fn idempotent_consumer_counts_each_event_once() {
        let (mut payments, rx) = wire(true);
        let mut orders = Orders::default();
        payments.record_success("o1", 500_000);
        payments.record_success("o1", 250_000);
        orders.drain(&rx, true);
        assert_eq!(orders.paid["o1"], 750_000);
    }
}
