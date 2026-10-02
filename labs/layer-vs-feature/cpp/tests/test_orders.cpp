#include <cassert>
#include <iostream>

#include "orders/orders.hpp"

int main() {
    shop::users::Users users;
    shop::orders::Orders orders(users);
    auto first = orders.place("u1", 500000);
    assert(first && first->id == 1 && first->total_kobo == 500000);
    assert(orders.place("u1", 1)->id == 2);
    assert(!orders.place("nobody", 1));
    std::cout << "ok: orders tests passed\n";
}
