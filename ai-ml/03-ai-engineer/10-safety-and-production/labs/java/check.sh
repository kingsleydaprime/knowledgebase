#!/bin/sh
# Plain javac, no Maven. Compiles the tools lab's Tools.java (Jackson 3, networknt) and the evals lab's
# Evals.java (Jackson 2) alongside this lab: the two Jacksons live in different packages, so both fit.
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
fetch com/fasterxml/jackson/core jackson-core 2.22.3
fetch com/fasterxml/jackson/core jackson-databind 2.22.3
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -Xlint:all,-serial -Werror -cp "$cp" -d "$out" src/safety/*.java \
    ../../../07-tools-and-mcp/labs/java/src/support/Tools.java ../../../12-evals/labs/java/src/evals/Evals.java
java -ea -cp "$out:$cp" safety.SafetyCheck
