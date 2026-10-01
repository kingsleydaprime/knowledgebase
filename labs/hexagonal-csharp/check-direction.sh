#!/bin/sh
# Runs inside the .NET SDK container. Run the check; then make Shop.Domain reference
# Shop.Adapters — a project cycle, which the build refuses.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Shop.Domain Shop.Adapters Shop.Check "$work/"
dotnet run --project "$work/Shop.Check"
(cd "$work/Shop.Domain" && dotnet add reference ../Shop.Adapters/Shop.Adapters.csproj >/dev/null)
if dotnet build "$work/Shop.Check" >"$work/err.txt" 2>&1; then echo "FAIL: domain -> adapters built"; exit 1; fi
grep -q "error MSB4006: There is a circular dependency" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: the build refused Shop.Domain -> Shop.Adapters (MSB4006)"
