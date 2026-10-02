#include "domain/domain.hpp"

namespace domain {

PlaceResult place_order(OrderRepository& orders, PaymentGateway& payments,
                        const std::string& id, const std::string& customer, long kobo) {
    if (kobo <= 0) return PlaceResult::InvalidTotal;
    if (!payments.charge(customer, kobo)) return PlaceResult::Declined;
    orders.save(Order{id, kobo, true});
    return PlaceResult::Ok;
}

}  // namespace domain
