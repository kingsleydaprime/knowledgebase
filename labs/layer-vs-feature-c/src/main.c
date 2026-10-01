/* main.c — the composition root: it hands orders the users check. */
#include <stdio.h>

#include "orders/orders.h"
#include "users/users.h"

int main(void) {
    orders *o = orders_new(users_exists);
    printf("order %d\n", orders_place(o, "u1", 500000));
    printf("order %d\n", orders_place(o, "nobody", 1));
    orders_free(o);
    return 0;
}
