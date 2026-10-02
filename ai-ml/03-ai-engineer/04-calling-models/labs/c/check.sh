#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
gcc -std=c17 -Wall -Wextra -Werror -o "$out/sse" sse.c
"$out/sse"
