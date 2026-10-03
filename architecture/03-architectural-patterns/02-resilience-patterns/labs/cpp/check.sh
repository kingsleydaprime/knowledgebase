#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
g++ -std=c++20 -Wall -Wextra -Werror -pthread -o "$out/resilience" resilience.cpp
"$out/resilience"
