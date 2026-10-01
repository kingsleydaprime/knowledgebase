#include "orders.h"

#include <stdlib.h>

/* The definition lives only here, so only this file can read the fields. */
struct orders {
    user_exists_fn user_exists;
    int count;
    long total_kobo;
};

/* static: a private helper — other files can't call it, even if they declare it. */
static int next_id(orders *o) { return ++o->count; }

orders *orders_new(user_exists_fn user_exists) {
    orders *o = calloc(1, sizeof *o);
    if (o) o->user_exists = user_exists;
    return o;
}

void orders_free(orders *o) { free(o); }

int orders_place(orders *o, const char *user_id, long total_kobo) {
    if (!o->user_exists(user_id)) return 0;
    o->total_kobo += total_kobo;
    return next_id(o);
}

long orders_total_kobo(const orders *o) { return o->total_kobo; }
