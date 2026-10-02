#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
g++ -std=c++23 -Wall -Wextra -Werror -o "$out/models" models.cpp
"$out/models"
