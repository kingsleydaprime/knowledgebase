#include <cassert>
#include <iostream>
#include <vector>

#include "orders.hpp"

int main() {
    orders::Repository repo({{"mug", 1}});
    assert(orders::status_for(orders::place(repo, {})) == 400);

    std::vector<orders::Item> too_many{{"mug", 5}};
    auto out = orders::place(repo, too_many);
    assert(orders::status_for(out) == 409);
    assert(std::get<orders::OutOfStock>(out.error()).sku == "mug");

    std::vector<orders::Item> one{{"mug", 1}};
    auto ok = orders::place(repo, one);
    assert(orders::status_for(ok) == 201 && *ok == 1 && repo.stock["mug"] == 0);
    std::cout << "ok: std::expected errors mapped to 400, 409 and 201\n";
}
