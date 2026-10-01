#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
gcc -std=c17 -Wall -Wextra -Werror -o "$out/test" test_orders.c orders.c
"$out/test"
