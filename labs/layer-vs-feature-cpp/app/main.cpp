// The composition root.
#include <iostream>

#include "orders/orders.hpp"
#include "users/users.hpp"

int main() {
    shop::users::Users users;
    shop::orders::Orders orders(users);
    for (const char* id : {"u1", "nobody"}) {
        auto order = orders.place(id, 500000);
        std::cout << id << ": " << (order ? "order " + std::to_string(order->id) : "rejected") << '\n';
    }
}
