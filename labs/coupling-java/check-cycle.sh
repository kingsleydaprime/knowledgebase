#!/bin/sh
# Java compiles a package cycle without complaint. jdeps (shipped with the JDK) shows it.
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -d "$out" src/shop/orders/Orders.java src/shop/payments/Payments.java
echo "ok: javac compiled the cycle without a warning"
jdeps -verbose:package "$out" > "$out/deps.txt"
grep -Eq "shop\.orders +-> +shop\.payments" "$out/deps.txt" || { cat "$out/deps.txt"; exit 1; }
grep -Eq "shop\.payments +-> +shop\.orders" "$out/deps.txt" || { cat "$out/deps.txt"; exit 1; }
echo "ok: jdeps shows both directions: shop.orders <-> shop.payments"
