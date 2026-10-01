#include "domain.h"

#include <stdio.h>

place_result place_order(const order_repository *orders, const payment_gateway *payments,
                         const char *id, const char *customer, long kobo, order *out) {
    if (kobo <= 0) return PLACE_INVALID_TOTAL;
    if (!payments->charge(payments->self, customer, kobo)) return PLACE_DECLINED;
    snprintf(out->id, sizeof out->id, "%s", id);
    out->total_kobo = kobo;
    out->paid = true;
    orders->save(orders->self, out);
    return PLACE_OK;
}
