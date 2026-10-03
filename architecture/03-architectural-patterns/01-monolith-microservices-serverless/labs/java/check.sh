#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all -Werror -d "$out" src/architecture/*.java
java -ea -cp "$out" architecture.ArchitectureCheck
