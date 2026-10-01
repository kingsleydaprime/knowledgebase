// main.rs — the composition root.
use shop::orders::Orders;
use shop::users::Users;

fn main() {
    let users = Users::new();
    let mut orders = Orders::new(&users);
    println!("{:?}", orders.place("u1", 500_000));
    println!("{:?}", orders.place("nobody", 1));
}
