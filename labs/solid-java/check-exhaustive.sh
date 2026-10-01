#!/bin/sh
# Compile and run; then add a Ussd record to the sealed hierarchy and expect the switch to fail.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
javac -Xlint:all,-serial -Werror -d "$work/ok" src/fees/Fees.java
java -ea -cp "$work/ok" fees.Fees
mkdir -p "$work/bad"
sed -e 's/permits Card, Transfer/permits Card, Transfer, Ussd/' \
    -e 's/^    public record Transfer() implements Method {}$/    public record Transfer() implements Method {}\n    public record Ussd() implements Method {}/' \
    src/fees/Fees.java > "$work/bad/Fees.java"
if javac -d "$work/bad/out" "$work/bad/Fees.java" 2>"$work/err.txt"; then echo "FAIL: the missing case compiled"; exit 1; fi
grep -q "the switch expression does not cover all possible input values" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: javac refused the switch that doesn't handle Ussd"
