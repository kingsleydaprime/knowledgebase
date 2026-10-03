#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all -Werror -d "$out" src/scaling/*.java
java -ea -cp "$out" scaling.ScalingCheck
