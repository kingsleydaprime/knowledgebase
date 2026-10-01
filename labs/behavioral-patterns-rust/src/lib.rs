//! Typestate: each state is its own type, and each type only has the methods that state allows.
//! An illegal transition isn't rejected at runtime — it doesn't compile.
use std::marker::PhantomData;

pub struct Pending;
pub struct Paid;
pub struct Shipped;
pub struct Delivered;
pub struct Cancelled;

/// Observer: listeners registered by the composition root, called after each transition.
pub type Listener = Box<dyn Fn(&str, &str, &str)>;

pub struct Order<S> {
    pub id: String,
    listeners: Vec<Listener>,
    state: PhantomData<S>,
}

impl<S> Order<S> {
    // Moves the order into its next state, telling every listener. `self` is consumed,
    // so the old-state value can't be used again.
    fn to<T>(self, from: &str, to: &str) -> Order<T> {
        for listener in &self.listeners {
            listener(&self.id, from, to);
        }
        Order {
            id: self.id,
            listeners: self.listeners,
            state: PhantomData,
        }
    }
}

impl Order<Pending> {
    pub fn new(id: &str, listeners: Vec<Listener>) -> Self {
        Order {
            id: id.into(),
            listeners,
            state: PhantomData,
        }
    }
    pub fn pay(self) -> Order<Paid> {
        self.to("pending", "paid")
    }
    pub fn cancel(self) -> Order<Cancelled> {
        self.to("pending", "cancelled")
    }
}

impl Order<Paid> {
    pub fn ship(self) -> Order<Shipped> {
        self.to("paid", "shipped")
    }
    pub fn cancel(self) -> Order<Cancelled> {
        self.to("paid", "cancelled")
    }
}

impl Order<Shipped> {
    pub fn deliver(self) -> Order<Delivered> {
        self.to("shipped", "delivered")
    }
    // No `cancel` here: a shipped order has no way to be cancelled.
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;
    use std::rc::Rc;

    #[test]
    fn happy_path_with_an_observer() {
        let audit = Rc::new(RefCell::new(Vec::new()));
        let log = Rc::clone(&audit);
        let listener: Listener =
            Box::new(move |_, from, to| log.borrow_mut().push(format!("{from}->{to}")));

        let _delivered = Order::new("o1", vec![listener]).pay().ship().deliver();
        assert_eq!(
            *audit.borrow(),
            ["pending->paid", "paid->shipped", "shipped->delivered"]
        );
    }
}
