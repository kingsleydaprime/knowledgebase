#!/bin/sh
# Compile, run, and prove another feature can't reach orders' package-private repository.
set -eu
export LC_ALL=C  # plain ASCII compiler messages, whatever the locale
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
javac -d "$work/out" $(find src -name '*.java')
output=$(java -cp "$work/out" shop.App)
expected='Order[id=1, userId=u1, totalKobo=500000]
rejected: unknown user: nobody'
[ "$output" = "$expected" ] || { echo "unexpected output:"; echo "$output"; exit 1; }
echo "ok: the app runs"

cp -r src "$work/src"
cat > "$work/src/shop/users/Sneak.java" <<'JAVA'
package shop.users;

class Sneak {
    Object reach() { return new shop.orders.OrdersRepository(); }
}
JAVA
if javac -d "$work/bad" $(find "$work/src" -name '*.java') 2>"$work/err.txt"; then
  echo "FAIL: users reached orders' repository and it compiled"; exit 1
fi
grep -q "OrdersRepository is not public in shop.orders; cannot be accessed from outside package" "$work/err.txt"
echo "ok: the compiler refused the cross-feature access"
