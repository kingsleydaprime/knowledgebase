#!/bin/sh
# Plain javac, no Maven: the SQLite JDBC driver (which bundles SQLite's native library) is downloaded once into a cache.
set -eu
export LC_ALL=C
jars="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/jars"
mkdir -p "$jars"
jar="$jars/sqlite-jdbc-3.53.4.0.jar"
[ -f "$jar" ] || curl -fsSL -o "$jar" "https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.53.4.0/sqlite-jdbc-3.53.4.0.jar"
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all -Werror -cp "$jar" -d "$out" src/outbox/*.java
java -ea --enable-native-access=ALL-UNNAMED -cp "$out:$jar" outbox.OutboxCheck
