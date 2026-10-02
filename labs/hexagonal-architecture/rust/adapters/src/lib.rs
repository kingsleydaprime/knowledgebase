//! Driven adapters, implementing the domain's ports.
use domain::{Order, OrderRepository, PaymentGateway};

#[derive(Default)]
pub struct InMemoryOrders {
    pub saved: Vec<Order>,
}
impl OrderRepository for InMemoryOrders {
    fn save(&mut self, order: Order) {
        self.saved.push(order);
    }
}

pub struct FakePayments {
    pub decline_above: u64,
}
impl PaymentGateway for FakePayments {
    fn charge(&self, _customer_id: &str, kobo: u64) -> bool {
        kobo <= self.decline_above
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use domain::{PlaceError, place_order};

    #[test]
    fn paid_order_is_saved_and_declined_is_not() {
        let mut orders = InMemoryOrders::default();
        let ok = place_order(
            &mut orders,
            &FakePayments {
                decline_above: 1_000_000,
            },
            "o1",
            "c1",
            250_000,
        );
        assert!(ok.unwrap().paid);
        let declined = place_order(
            &mut orders,
            &FakePayments { decline_above: 100 },
            "o2",
            "c1",
            250_000,
        );
        assert_eq!(declined, Err(PlaceError::Declined));
        assert_eq!(orders.saved.len(), 1);
    }
}
