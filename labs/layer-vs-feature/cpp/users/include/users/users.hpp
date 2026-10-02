#pragma once
#include <string_view>

namespace shop::users {

// The users feature's public API.
class Users {
public:
    [[nodiscard]] bool exists(std::string_view id) const;
};

}  // namespace shop::users
