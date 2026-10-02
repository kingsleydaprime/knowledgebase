#!/bin/sh
# Plain javac, no Maven: the jars are downloaded once from Maven Central into a cache.
set -eu
export LC_ALL=C
jars="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/jars"
mkdir -p "$jars"
cp=""
fetch() { # group path, artifact, version
    [ -f "$jars/$2-$3.jar" ] || curl -fsSL -o "$jars/$2-$3.jar" "https://repo1.maven.org/maven2/$1/$2/$3/$2-$3.jar"
    cp="$cp${cp:+:}$jars/$2-$3.jar"
}
fetch com/fasterxml/jackson/core jackson-core 2.22.3
fetch com/fasterxml/jackson/core jackson-databind 2.22.3
fetch com/fasterxml/jackson/core jackson-annotations 2.22
fetch com/fasterxml/jackson/datatype jackson-datatype-jsr310 2.22.3
fetch com/github/victools jsonschema-generator 4.38.0
fetch com/fasterxml classmate 1.7.3
fetch org/slf4j slf4j-api 2.0.17   # victools logs through SLF4J;
fetch org/slf4j slf4j-nop 2.0.17   # the no-op binding keeps it quiet
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -cp "$cp" -d "$out" src/invoice/*.java
java -ea -cp "$out:$cp" invoice.InvoicesCheck
