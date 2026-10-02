// fees.cpp — open: virtual functions behind an interface. Closed: std::variant + std::visit,
// where a missing overload is a compile error.
#include <cassert>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <variant>

struct FeeRule { virtual ~FeeRule() = default; virtual long fee(long amount) const = 0; };
struct CardRule : FeeRule { long fee(long a) const override { return a * 29 / 1000; } };
struct TransferRule : FeeRule { long fee(long) const override { return 50; } };

struct Card {};
struct Transfer {};
using Method = std::variant<Card, Transfer>;

template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

long fee(const Method& m, long amount) {
    return std::visit(overloaded{
        [&](Card) { return amount * 29 / 1000; },
        [](Transfer) { return 50L; },
    }, m);
}

int main() {
    std::map<std::string, std::unique_ptr<FeeRule>> open;   // open for extension: add an entry
    open["card"] = std::make_unique<CardRule>();
    open["transfer"] = std::make_unique<TransferRule>();
    assert(open["card"]->fee(10000) == 290 && open["transfer"]->fee(10000) == 50);
    assert(fee(Card{}, 10000) == 290 && fee(Transfer{}, 10000) == 50);
    std::cout << "ok: virtual rules and variant visit agree\n";
}
