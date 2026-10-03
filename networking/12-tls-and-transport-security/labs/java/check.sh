#!/bin/sh
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
sh ../shared/make-certs.sh "$out/certs"
javac -Xlint:all -Werror -d "$out" src/tls/*.java
java -ea -cp "$out" tls.TlsCheck "$out/certs"
