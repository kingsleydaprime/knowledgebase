/* orders.c — State as a 2D transition table; Observer as an array of function pointers. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef enum { PENDING, PAID, SHIPPED, DELIVERED, CANCELLED, STATUS_COUNT } status;
typedef enum { PAY, SHIP, DELIVER, CANCEL, ACTION_COUNT } action;
#define NONE (-1)

/* transitions[from][action] = to, or NONE if not allowed */
static const int transitions[STATUS_COUNT][ACTION_COUNT] = {
    [PENDING] = {[PAY] = PAID, [SHIP] = NONE, [DELIVER] = NONE, [CANCEL] = CANCELLED},
    [PAID] = {[PAY] = NONE, [SHIP] = SHIPPED, [DELIVER] = NONE, [CANCEL] = CANCELLED},
    [SHIPPED] = {[PAY] = NONE, [SHIP] = NONE, [DELIVER] = DELIVERED, [CANCEL] = NONE},
    [DELIVERED] = {NONE, NONE, NONE, NONE},
    [CANCELLED] = {NONE, NONE, NONE, NONE},
};

typedef void (*listener)(void *ctx, status from, status to);

typedef struct {
    status current;
    struct { listener fn; void *ctx; } listeners[4];
    int listener_count;
} order;

static void on_change(order *o, listener fn, void *ctx) {
    o->listeners[o->listener_count].fn = fn;
    o->listeners[o->listener_count++].ctx = ctx;
}

/* Returns 0 on success, -1 for an illegal transition (and tells no one). */
static int apply(order *o, action a) {
    int next = transitions[o->current][a];
    if (next == NONE) return -1;
    status from = o->current;
    o->current = (status)next;
    for (int i = 0; i < o->listener_count; i++) o->listeners[i].fn(o->listeners[i].ctx, from, o->current);
    return 0;
}

static void count_changes(void *ctx, status from, status to) { (void)from; (void)to; ++*(int *)ctx; }

int main(void) {
    int changes = 0;
    order o = {.current = PENDING};
    on_change(&o, count_changes, &changes);
    assert(apply(&o, PAY) == 0 && apply(&o, SHIP) == 0);
    assert(apply(&o, CANCEL) == -1 && o.current == SHIPPED && changes == 2);
    assert(apply(&o, DELIVER) == 0 && o.current == DELIVERED && changes == 3);
    puts("ok: transition table and function-pointer listeners");
    return 0;
}
