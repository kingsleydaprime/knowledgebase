/* domain.h — rules and ports. Includes nothing from adapters/. */
#ifndef DOMAIN_H
#define DOMAIN_H

#include <stdbool.h>

typedef struct { char id[16]; long total_kobo; bool paid; } order;

/* Ports: structs of function pointers the adapters fill in. */
typedef struct { void *self; void (*save)(void *self, const order *o); } order_repository;
typedef struct { void *self; bool (*charge)(void *self, const char *customer, long kobo); } payment_gateway;

typedef enum { PLACE_OK, PLACE_INVALID_TOTAL, PLACE_DECLINED } place_result;

place_result place_order(const order_repository *orders, const payment_gateway *payments,
                         const char *id, const char *customer, long kobo, order *out);

#endif
