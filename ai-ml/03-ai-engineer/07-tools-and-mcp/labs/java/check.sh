#!/bin/sh
# Plain javac, no Maven: the jars are downloaded once from Maven Central into a cache.
# Then the official MCP client checks the hand-written server (../shared/conformance.sh).
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
fetch tools/jackson/dataformat jackson-dataformat-yaml 3.2.3
fetch org/snakeyaml snakeyaml-engine 3.0.1
fetch com/ethlo/time itu 1.14.0
fetch org/slf4j slf4j-api 2.0.19
fetch org/slf4j slf4j-nop 2.0.19
fetch com/networknt json-schema-validator 3.0.8
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -cp "$cp" -d "$out" src/support/*.java
java -ea -cp "$out:$cp" support.ToolsCheck
sh ../shared/conformance.sh java -cp "$out:$cp" support.McpServer
