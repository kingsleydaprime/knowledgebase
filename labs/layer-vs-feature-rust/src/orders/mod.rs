// The orders feature. `repository` is declared without `pub`, so nothing outside
// `orders` can name it — the compiler enforces the boundary.
mod repository;

use crate::users::Users;
pub use repository::Order;
use repository::Repository;

#[derive(Debug, PartialEq)]
pub enum PlaceError {
    UnknownUser,
}

pub struct Orders<'a> {
    users: &'a Users,
    repository: Repository,
}

impl<'a> Orders<'a> {
    pub fn new(users: &'a Users) -> Self {
        Orders {
            users,
            repository: Repository::default(),
        }
    }

    pub fn place(&mut self, user_id: &str, total_kobo: u64) -> Result<Order, PlaceError> {
        if !self.users.exists(user_id) {
            return Err(PlaceError::UnknownUser);
        }
        Ok(self.repository.insert(user_id, total_kobo))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn places_an_order_for_a_known_user() {
        let users = Users::new();
        let mut orders = Orders::new(&users);
        let order = orders.place("u1", 500_000).unwrap();
        assert_eq!(
            order,
            Order {
                id: 1,
                user_id: "u1".into(),
                total_kobo: 500_000
            }
        );
    }

    #[test]
    fn rejects_an_unknown_user() {
        let users = Users::new();
        let mut orders = Orders::new(&users);
        assert_eq!(orders.place("nobody", 1), Err(PlaceError::UnknownUser));
    }
}
