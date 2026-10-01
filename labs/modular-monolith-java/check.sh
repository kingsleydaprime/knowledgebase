#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -d "$out" src/shop/Shop.java
java -ea -cp "$out" shop.Shop
