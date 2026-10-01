#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -d "$out" src/rates/*.java
java -ea -cp "$out" rates.Check
