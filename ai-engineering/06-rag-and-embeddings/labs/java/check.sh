#!/bin/sh
# Plain javac, no Maven: the Jackson 3 jars (for reading the shared JSON) are downloaded once into a cache.
set -eu
export LC_ALL=C
jars="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/jars"
mkdir -p "$jars"
cp=""
fetch() { # group path, artifact, version
    [ -f "$jars/$2-$3.jar" ] || curl -fsSL -o "$jars/$2-$3.jar" "https://repo1.maven.org/maven2/$1/$2/$3/$2-$3.jar"
    cp="$cp${cp:+:}$jars/$2-$3.jar"
}
fetch tools/jackson/core jackson-core 3.2.3
fetch tools/jackson/core jackson-databind 3.2.3
fetch com/fasterxml/jackson/core jackson-annotations 2.22
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -cp "$cp" -d "$out" src/rag/*.java
java -ea -cp "$out:$cp" rag.RagCheck
