#include "orders.h"

#include <string.h>

static int *stock_slot(repository *repo, const char *sku) {
    for (int i = 0; i < repo->count; i++) {
        if (strcmp(repo->skus[i], sku) == 0) return &repo->stock[i];
    }
    return NULL;
}

place_result orders_place(repository *repo, const item *items, int n, int *order_id, const char **failed_sku) {
    if (n == 0) return PLACE_EMPTY_ORDER;
    for (int i = 0; i < n; i++) {
        int *slot = stock_slot(repo, items[i].sku);
        if (!slot || *slot < items[i].quantity) {
            *failed_sku = items[i].sku;
            return PLACE_OUT_OF_STOCK;
        }
    }
    for (int i = 0; i < n; i++) *stock_slot(repo, items[i].sku) -= items[i].quantity;
    *order_id = ++repo->orders;
    return PLACE_OK;
}

int status_for(place_result r) {
    switch (r) {
        case PLACE_OK: return 201;
        case PLACE_EMPTY_ORDER: return 400;
        case PLACE_OUT_OF_STOCK: return 409;
    }
    return 500; /* unreachable for valid values; -Wswitch warns if a new code is unhandled */
}
