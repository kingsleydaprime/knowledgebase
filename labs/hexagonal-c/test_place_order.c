#include <assert.h>
#include <stdio.h>

#include "in_memory.h"

int main(void) {
    memory_orders m = {0};
    long generous = 1000000, strict = 100;
    order_repository orders = memory_orders_port(&m);
    payment_gateway ok = fake_payments_port(&generous), declines = fake_payments_port(&strict);
    order out;
    assert(place_order(&orders, &ok, "o1", "c1", 250000, &out) == PLACE_OK && out.paid && m.count == 1);
    assert(place_order(&orders, &declines, "o2", "c1", 250000, &out) == PLACE_DECLINED && m.count == 1);
    puts("ok: use case runs on in-memory adapters");
    return 0;
}
