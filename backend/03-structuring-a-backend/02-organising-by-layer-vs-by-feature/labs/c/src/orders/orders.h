/* orders.h — the orders feature's public API.
 * `struct orders` is declared but not defined here: callers hold a pointer
 * and can't see or touch its fields. That's an opaque type. */
#ifndef ORDERS_H
#define ORDERS_H

#include <stdbool.h>

typedef struct orders orders;
typedef bool (*user_exists_fn)(const char *user_id); /* what orders needs from users */

orders *orders_new(user_exists_fn user_exists);
void orders_free(orders *o);
/* Returns the new order's id, or 0 if the user is unknown. */
int orders_place(orders *o, const char *user_id, long total_kobo);
long orders_total_kobo(const orders *o);

#endif
