/* in_memory.h — driven adapters. They include the domain, never the reverse. */
#ifndef IN_MEMORY_H
#define IN_MEMORY_H

#include "domain.h"

typedef struct { order saved[8]; int count; } memory_orders;
order_repository memory_orders_port(memory_orders *m);
payment_gateway fake_payments_port(long *decline_above);

#endif
