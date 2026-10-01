#pragma once
// C++23: std::expected<T, E> holds either a value or an error — no exception thrown.
#include <expected>
#include <map>
#include <span>
#include <string>
#include <variant>

namespace orders {

struct Item { std::string sku; int quantity; };

struct EmptyOrder {};
struct OutOfStock { std::string sku; };
using PlaceError = std::variant<EmptyOrder, OutOfStock>;

class Repository {  // the only code that knows how stock is stored
public:
    explicit Repository(std::map<std::string, int> stock) : stock(std::move(stock)) {}
    std::map<std::string, int> stock;
    int create() { return ++orders_; }
private:
    int orders_ = 0;
};

// The service: business rules, returning a value or a domain error.
inline std::expected<int, PlaceError> place(Repository& repo, std::span<const Item> items) {
    if (items.empty()) return std::unexpected(EmptyOrder{});
    for (const auto& item : items) {
        if (repo.stock[item.sku] < item.quantity) return std::unexpected(OutOfStock{item.sku});
    }
    for (const auto& item : items) repo.stock[item.sku] -= item.quantity;
    return repo.create();
}

// The controller's mapping. std::visit with one overload per error type.
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

inline int status_for(const std::expected<int, PlaceError>& result) {
    if (result) return 201;
    return std::visit(overloaded{
        [](const EmptyOrder&) { return 400; },
        [](const OutOfStock&) { return 409; },
    }, result.error());
}

}  // namespace orders
