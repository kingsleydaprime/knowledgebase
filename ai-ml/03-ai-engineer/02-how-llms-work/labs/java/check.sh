#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all -Werror -d "$out" src/decoding/*.java
java -ea -cp "$out" decoding.Decoding
