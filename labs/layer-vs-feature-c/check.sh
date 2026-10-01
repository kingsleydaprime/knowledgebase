#!/bin/sh
# Build and test, then prove the two C boundaries hold: opaque types and static functions.
set -eu
export LC_ALL=C  # plain ASCII quotes in compiler messages, whatever the locale
CC="${CC:-gcc}"
FLAGS="-std=c17 -Wall -Wextra -Werror -Isrc"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

$CC $FLAGS -o "$work/test" tests/test_orders.c src/orders/orders.c
"$work/test"
$CC $FLAGS -o "$work/shop" src/main.c src/orders/orders.c src/users/users.c
[ "$("$work/shop")" = "order 1
order 0" ] && echo "ok: the app runs"

# 1. Another feature reads a field of the opaque struct.
cat > "$work/peek.c" <<'C'
#include "orders/orders.h"
long peek(orders *o) { return o->total_kobo; }
C
if $CC $FLAGS -c "$work/peek.c" -o "$work/peek.o" 2>"$work/err1.txt"; then
  echo "FAIL: read a private field"; exit 1
fi
grep -q "invalid use of incomplete typedef 'orders'" "$work/err1.txt"
echo "ok: the compiler refused to read a private field"

# 2. Another feature calls orders' static helper by declaring it itself.
cat > "$work/sneak.c" <<'C'
#include "orders/orders.h"
int next_id(orders *o);
int sneak(orders *o) { return next_id(o); }
int main(void) { return 0; }
C
if $CC $FLAGS -o "$work/sneak" "$work/sneak.c" src/orders/orders.c 2>"$work/err2.txt"; then
  echo "FAIL: called a static function"; exit 1
fi
grep -q "undefined reference to .next_id." "$work/err2.txt"
echo "ok: the linker refused to call a private function"
