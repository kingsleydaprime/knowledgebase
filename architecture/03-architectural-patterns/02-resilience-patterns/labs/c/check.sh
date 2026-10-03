#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
gcc -std=c17 -Wall -Wextra -Werror -pthread -o "$out/resilience" resilience.c
"$out/resilience"
