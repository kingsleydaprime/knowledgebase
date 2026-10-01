/* shop.c — a bus as an array of callbacks; orders deduplicates on event id. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct { char event_id[16]; char order_id[8]; long amount_kobo; } payment_succeeded;
typedef void (*handler)(void *ctx, const payment_succeeded *e);

typedef struct {
    struct { handler fn; void *ctx; } handlers[4];
    int count;
    int deliver_twice;   /* simulates a broker's at-least-once delivery */
} bus;

static void subscribe(bus *b, handler fn, void *ctx) { b->handlers[b->count].fn = fn; b->handlers[b->count++].ctx = ctx; }
static void publish(bus *b, const payment_succeeded *e) {
    for (int round = 0; round < (b->deliver_twice ? 2 : 1); round++)
        for (int i = 0; i < b->count; i++) b->handlers[i].fn(b->handlers[i].ctx, e);
}

typedef struct { long paid_o1; char seen[8][16]; int seen_count; int idempotent; } orders;

static void orders_on_payment(void *ctx, const payment_succeeded *e) {
    orders *o = ctx;
    if (o->idempotent) {
        for (int i = 0; i < o->seen_count; i++)
            if (strcmp(o->seen[i], e->event_id) == 0) return;   /* already handled */
        snprintf(o->seen[o->seen_count++], sizeof o->seen[0], "%s", e->event_id);
    }
    if (strcmp(e->order_id, "o1") == 0) o->paid_o1 += e->amount_kobo;
}

static long run(int idempotent) {
    bus b = {.deliver_twice = 1};
    orders o = {.idempotent = idempotent};
    subscribe(&b, orders_on_payment, &o);
    payment_succeeded first = {"evt_1", "o1", 500000}, second = {"evt_2", "o1", 250000};
    publish(&b, &first);
    publish(&b, &second);
    return o.paid_o1;
}

int main(void) {
    assert(run(0) == 1500000);   /* naive: both payments counted twice */
    assert(run(1) == 750000);    /* idempotent: each event once */
    puts("ok: naive consumer double-counts; idempotent one doesn't");
    return 0;
}
