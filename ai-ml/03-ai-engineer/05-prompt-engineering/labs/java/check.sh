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
fetch com/samskivert jmustache 1.16
fetch com/fasterxml/jackson/core jackson-core 2.22.3
fetch com/fasterxml/jackson/core jackson-databind 2.22.3
fetch com/fasterxml/jackson/core jackson-annotations 2.22
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -cp "$cp" -d "$out" src/prompts/*.java
java -ea -cp "$out:$cp" prompts.PromptsCheck
