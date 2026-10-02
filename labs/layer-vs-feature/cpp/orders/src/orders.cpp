#include "orders/orders.hpp"

#include "repository.hpp"

namespace shop::orders {

Orders::Orders(const users::Users& users) : users_(users), repository_(std::make_unique<Repository>()) {}
Orders::~Orders() = default;

std::optional<Order> Orders::place(const std::string& user_id, long total_kobo) {
    if (!users_.exists(user_id)) return std::nullopt;
    return repository_->insert(user_id, total_kobo);
}

}  // namespace shop::orders
