/* fees.c — open: a table of function pointers. Closed: an enum and a switch that
 * -Wswitch-enum checks for completeness. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef long (*fee_fn)(long amount_kobo);
static long card_fee(long a) { return a * 29 / 1000; }
static long transfer_fee(long a) { (void)a; return 50; }

/* Open for extension: a new method is a new row. */
static const struct { const char *name; fee_fn fee; } open_rules[] = {
    {"card", card_fee},
    {"transfer", transfer_fee},
};

static long open_fee(const char *name, long amount) {
    for (size_t i = 0; i < sizeof open_rules / sizeof open_rules[0]; i++)
        if (strcmp(open_rules[i].name, name) == 0) return open_rules[i].fee(amount);
    return -1;
}

/* Closed: an enum and one switch. */
typedef enum { METHOD_CARD, METHOD_TRANSFER } method;

static long closed_fee(method m, long amount) {
    switch (m) {
        case METHOD_CARD: return amount * 29 / 1000;
        case METHOD_TRANSFER: return 50;
    }
    return -1;
}

int main(void) {
    assert(open_fee("card", 10000) == 290 && open_fee("transfer", 10000) == 50);
    assert(closed_fee(METHOD_CARD, 10000) == 290 && closed_fee(METHOD_TRANSFER, 10000) == 50);
    puts("ok: function-pointer table and enum switch agree");
    return 0;
}
