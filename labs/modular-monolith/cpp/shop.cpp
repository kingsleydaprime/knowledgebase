// shop.cpp — a bus of std::function handlers; orders deduplicates with an unordered_set.
#include <cassert>
#include <functional>
#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

struct PaymentSucceeded { std::string event_id, order_id; long amount_kobo; };

class Bus {
public:
    explicit Bus(bool deliver_twice) : deliver_twice_(deliver_twice) {}
    void subscribe(std::function<void(const PaymentSucceeded&)> h) { handlers_.push_back(std::move(h)); }
    void publish(const PaymentSucceeded& e) {
        for (int round = 0; round < (deliver_twice_ ? 2 : 1); ++round)
            for (const auto& h : handlers_) h(e);
    }
private:
    bool deliver_twice_;
    std::vector<std::function<void(const PaymentSucceeded&)>> handlers_;
};

struct Orders {
    std::unordered_map<std::string, long> paid;
    std::unordered_set<std::string> seen;
    Orders(Bus& bus, bool idempotent) {
        bus.subscribe([this, idempotent](const PaymentSucceeded& e) {
            if (idempotent && !seen.insert(e.event_id).second) return;   // .second is false for a repeat
            paid[e.order_id] += e.amount_kobo;
        });
    }
};

int main() {
    Bus naive_bus(true);
    Orders naive(naive_bus, false);
    naive_bus.publish({"evt_1", "o1", 500'000});
    assert(naive.paid["o1"] == 1'000'000);

    Bus bus(true);
    Orders orders(bus, true);
    bus.publish({"evt_1", "o1", 500'000});
    bus.publish({"evt_2", "o1", 250'000});
    assert(orders.paid["o1"] == 750'000);
    std::cout << "ok: naive consumer double-counts; idempotent one doesn't\n";
}
