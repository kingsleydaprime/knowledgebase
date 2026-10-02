#!/bin/sh
# Java compiles a domain -> adapters import without complaint; jdeps reveals it.
# In a real project, an ArchUnit test (layeredArchitecture() ... mayNotAccessAnyLayer) fails the build.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
javac -Xlint:all -Werror -d "$work/ok" $(find src -name '*.java')
java -ea -cp "$work/ok" shop.Check
cp -r src "$work/src"
cat > "$work/src/shop/domain/Sneak.java" <<'JAVA'
package shop.domain;

final class Sneak {
    Object reach() { return new shop.adapters.Memory.Orders(); }
}
JAVA
javac -d "$work/bad" $(find "$work/src" -name '*.java')
echo "ok: javac compiled the reversed dependency — nothing in the language stops it"
jdeps -verbose:package "$work/bad" | grep -Eq "shop\.domain +-> +shop\.adapters" || { echo "FAIL: jdeps didn't show it"; exit 1; }
echo "ok: jdeps shows shop.domain -> shop.adapters"
