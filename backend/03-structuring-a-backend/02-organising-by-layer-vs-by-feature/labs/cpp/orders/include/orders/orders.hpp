#pragma once
#include <memory>
#include <optional>
#include <string>

#include "users/users.hpp"

namespace shop::orders {

struct Order {
    int id;
    std::string user_id;
    long total_kobo;
};

class Repository;  // defined in a private header; callers never see it

// The orders feature's public API.
class Orders {
public:
    explicit Orders(const users::Users& users);
    ~Orders();
    std::optional<Order> place(const std::string& user_id, long total_kobo);

private:
    const users::Users& users_;
    std::unique_ptr<Repository> repository_;
};

}  // namespace shop::orders
