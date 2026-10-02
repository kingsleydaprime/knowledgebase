// orders.cpp — State as a std::map table; Observer as std::function listeners;
// Iterator via begin()/end(), so range-for works.
#include <cassert>
#include <functional>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

enum class Status { Pending, Paid, Shipped, Delivered, Cancelled };

class Order {
public:
    using Listener = std::function<void(Status from, Status to)>;

    void on_change(Listener l) { listeners_.push_back(std::move(l)); }

    void apply(const std::string& action) {
        static const std::map<Status, std::map<std::string, Status>> transitions{
            {Status::Pending, {{"pay", Status::Paid}, {"cancel", Status::Cancelled}}},
            {Status::Paid, {{"ship", Status::Shipped}, {"cancel", Status::Cancelled}}},
            {Status::Shipped, {{"deliver", Status::Delivered}}},
        };
        auto state = transitions.find(status_);
        if (state == transitions.end() || !state->second.contains(action))
            throw std::logic_error("cannot " + action + " from this state");
        const Status from = status_;
        status_ = state->second.at(action);
        history_.push_back(status_);
        for (const auto& l : listeners_) l(from, status_);
    }

    Status status() const { return status_; }
    auto begin() const { return history_.begin(); }
    auto end() const { return history_.end(); }

private:
    Status status_ = Status::Pending;
    std::vector<Listener> listeners_;
    std::vector<Status> history_{Status::Pending};
};

int main() {
    int changes = 0;
    Order order;
    order.on_change([&](Status, Status) { ++changes; });
    for (const char* a : {"pay", "ship"}) order.apply(a);

    bool rejected = false;
    try { order.apply("cancel"); } catch (const std::logic_error&) { rejected = true; }
    assert(rejected && order.status() == Status::Shipped && changes == 2);

    int steps = 0;
    for (Status s : order) { (void)s; ++steps; }
    assert(steps == 3);
    std::cout << "ok: table, std::function listeners and range-for history\n";
}
