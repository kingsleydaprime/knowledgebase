#pragma once
#include <string>

namespace domain {

struct Order { std::string id; long total_kobo; bool paid; };

// Ports: abstract classes the domain owns.
struct OrderRepository { virtual ~OrderRepository() = default; virtual void save(const Order&) = 0; };
struct PaymentGateway { virtual ~PaymentGateway() = default; virtual bool charge(const std::string&, long) = 0; };

enum class PlaceResult { Ok, InvalidTotal, Declined };

PlaceResult place_order(OrderRepository& orders, PaymentGateway& payments,
                        const std::string& id, const std::string& customer, long kobo);

}  // namespace domain
