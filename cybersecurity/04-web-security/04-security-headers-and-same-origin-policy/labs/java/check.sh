#!/bin/sh
# Origin is a "restricted" header in java.net.http; this property lets the test set it.
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -d "$out" src/headers/Server.java
java -ea -Djdk.httpclient.allowRestrictedHeaders=origin -cp "$out" headers.Server
