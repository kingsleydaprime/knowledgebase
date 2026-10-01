#!/bin/sh
# Two headers that include each other, each holding the other's struct by value: impossible.
# Include guards stop the infinite loop, so one struct is always seen before the other is defined.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cat > "$work/order.h" <<'C'
#ifndef ORDER_H
#define ORDER_H
#include "payment.h"
struct order { int id; struct payment payment; };
#endif
C
cat > "$work/payment.h" <<'C'
#ifndef PAYMENT_H
#define PAYMENT_H
#include "order.h"
struct payment { int amount; struct order order; };
#endif
C
echo '#include "order.h"' > "$work/main.c"
if gcc -std=c17 -c "$work/main.c" -o "$work/main.o" 2>"$work/err.txt"; then echo "FAIL: compiled"; exit 1; fi
grep -q "field 'order' has incomplete type" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: the header cycle fails: field 'order' has incomplete type"

# The fix: one side holds a pointer, and a forward declaration replaces the include.
cat > "$work/payment.h" <<'C'
#ifndef PAYMENT_H
#define PAYMENT_H
struct order;                                    /* forward declaration: no include needed */
struct payment { int amount; struct order *order; };
#endif
C
gcc -std=c17 -Wall -Wextra -Werror -c "$work/main.c" -o "$work/main.o"
echo "ok: a forward declaration and a pointer break the cycle"
