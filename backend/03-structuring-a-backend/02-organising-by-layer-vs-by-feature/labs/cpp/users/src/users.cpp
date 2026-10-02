#include "users/users.hpp"

#include <array>
#include <string_view>

namespace shop::users {

namespace {  // anonymous namespace: visible only in this file
constexpr std::array<std::string_view, 1> known_ids{"u1"};
}

bool Users::exists(std::string_view id) const {
    for (auto known : known_ids) {
        if (known == id) return true;
    }
    return false;
}

}  // namespace shop::users
