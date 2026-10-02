#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "orders/orders.h"

/* A stub for the users feature: the test decides who exists. */
static bool only_u1(const char *id) { return strcmp(id, "u1") == 0; }

int main(void) {
    orders *o = orders_new(only_u1);
    assert(orders_place(o, "u1", 500000) == 1);
    assert(orders_place(o, "u1", 250000) == 2);
    assert(orders_place(o, "nobody", 1) == 0);
    assert(orders_total_kobo(o) == 750000);
    orders_free(o);
    puts("ok: orders tests passed");
    return 0;
}
