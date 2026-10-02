#include <cassert>
#include <iostream>

#include "adapters/memory.hpp"

int main() {
    adapters::InMemoryOrders orders;
    adapters::FakePayments generous(1'000'000), strict(100);
    assert(domain::place_order(orders, generous, "o1", "c1", 250'000) == domain::PlaceResult::Ok);
    assert(domain::place_order(orders, strict, "o2", "c1", 250'000) == domain::PlaceResult::Declined);
    assert(orders.saved.size() == 1);
    std::cout << "ok: use case runs on in-memory adapters\n";
}
