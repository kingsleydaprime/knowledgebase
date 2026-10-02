//! Rules and ports. This crate has no dependencies.
#[derive(Debug, Clone, PartialEq)]
pub struct Order {
    pub id: String,
    pub total_kobo: u64,
    pub paid: bool,
}

#[derive(Debug, PartialEq)]
pub enum PlaceError {
    InvalidTotal,
    Declined,
}

// Ports: traits the domain defines and adapters implement.
pub trait OrderRepository {
    fn save(&mut self, order: Order);
}
pub trait PaymentGateway {
    fn charge(&self, customer_id: &str, kobo: u64) -> bool;
}

pub fn place_order(
    orders: &mut impl OrderRepository,
    payments: &impl PaymentGateway,
    id: &str,
    customer_id: &str,
    kobo: u64,
) -> Result<Order, PlaceError> {
    if kobo == 0 {
        return Err(PlaceError::InvalidTotal);
    }
    if !payments.charge(customer_id, kobo) {
        return Err(PlaceError::Declined);
    }
    let order = Order {
        id: id.into(),
        total_kobo: kobo,
        paid: true,
    };
    orders.save(order.clone());
    Ok(order)
}
