#!/bin/sh
# Runs inside the .NET SDK container. Run; then add Ussd to the enum and expect CS8509 as an error.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Fees "$work/ok" && dotnet run --project "$work/ok"
cp -r Fees "$work/bad"
sed -i 's/^enum Method { Card, Transfer }$/enum Method { Card, Transfer, Ussd }/' "$work/bad/Program.cs"
if dotnet build "$work/bad" >"$work/err.txt" 2>&1; then echo "FAIL: the missing case compiled"; exit 1; fi
grep -q "error CS8509: The switch expression does not handle all possible values of its input type" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: the compiler refused the switch that doesn't handle Ussd (CS8509)"
