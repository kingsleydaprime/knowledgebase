/* orders.h — in C, a domain error is a return code; the result travels through a pointer. */
#ifndef ORDERS_H
#define ORDERS_H

typedef enum { PLACE_OK, PLACE_EMPTY_ORDER, PLACE_OUT_OF_STOCK } place_result;

typedef struct { const char *sku; int quantity; } item;

typedef struct {            /* the repository: the only code that knows how stock is stored */
    const char *skus[8];
    int stock[8];
    int count;
    int orders;
} repository;

/* The service. On success *order_id is set; on PLACE_OUT_OF_STOCK, *failed_sku is. */
place_result orders_place(repository *repo, const item *items, int n, int *order_id, const char **failed_sku);

/* The controller's mapping, in one place. */
int status_for(place_result r);

#endif
