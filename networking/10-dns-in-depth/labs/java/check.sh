#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all -Werror -d "$out" src/dns/*.java
java -ea -cp "$out" dns.DnsCheck
