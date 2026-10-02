#include "in_memory.h"

static void memory_save(void *self, const order *o) {
    memory_orders *m = self;
    m->saved[m->count++] = *o;
}
static bool fake_charge(void *self, const char *customer, long kobo) {
    (void)customer;
    return kobo <= *(long *)self;
}

order_repository memory_orders_port(memory_orders *m) { return (order_repository){m, memory_save}; }
payment_gateway fake_payments_port(long *limit) { return (payment_gateway){limit, fake_charge}; }
