#pragma once
// Private to the orders target: this directory is a PRIVATE include path.
#include <string>
#include <vector>

#include "orders/orders.hpp"

namespace shop::orders {

class Repository {
public:
    Order insert(const std::string& user_id, long total_kobo) {
        orders_.push_back({static_cast<int>(orders_.size()) + 1, user_id, total_kobo});
        return orders_.back();
    }

private:
    std::vector<Order> orders_;
};

}  // namespace shop::orders
