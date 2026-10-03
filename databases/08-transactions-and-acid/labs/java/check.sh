#!/bin/sh
# Plain javac, no Maven: the PostgreSQL JDBC driver is downloaded once into a cache.
# Run it through ../shared/with-postgres.sh, which starts the throwaway database and sets PGPORT.
set -eu
export LC_ALL=C
jars="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/jars"
mkdir -p "$jars"
jar="$jars/postgresql-42.7.13.jar"
[ -f "$jar" ] || curl -fsSL -o "$jar" "https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.13/postgresql-42.7.13.jar"
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all -Werror -cp "$jar" -d "$out" src/isolation/*.java
java -ea -cp "$out:$jar" isolation.IsolationCheck
