#!/bin/sh
# Compile and run the checks with assertions on.
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -d "$out" src/orders/*.java
java -ea -cp "$out" orders.Check
