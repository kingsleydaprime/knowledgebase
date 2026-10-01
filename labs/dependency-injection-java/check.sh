#!/bin/sh
# Compile and run the checks with assertions on.
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all -Werror -d "$out" src/audit/*.java
java -ea -cp "$out" audit.Check
