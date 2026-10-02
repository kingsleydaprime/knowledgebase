#pragma once
#include <vector>

#include "domain/domain.hpp"

namespace adapters {

struct InMemoryOrders final : domain::OrderRepository {
    std::vector<domain::Order> saved;
    void save(const domain::Order& o) override { saved.push_back(o); }
};

struct FakePayments final : domain::PaymentGateway {
    long decline_above;
    explicit FakePayments(long limit) : decline_above(limit) {}
    bool charge(const std::string&, long kobo) override { return kobo <= decline_above; }
};

}  // namespace adapters
