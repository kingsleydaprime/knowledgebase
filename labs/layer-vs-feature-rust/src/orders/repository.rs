// Private to the orders module.
#[derive(Debug, Clone, PartialEq)]
pub struct Order {
    pub id: u32,
    pub user_id: String,
    pub total_kobo: u64,
}

#[derive(Default)]
pub(super) struct Repository {
    orders: Vec<Order>,
}

impl Repository {
    pub(super) fn insert(&mut self, user_id: &str, total_kobo: u64) -> Order {
        let order = Order {
            id: self.orders.len() as u32 + 1,
            user_id: user_id.into(),
            total_kobo,
        };
        self.orders.push(order.clone());
        order
    }
}
