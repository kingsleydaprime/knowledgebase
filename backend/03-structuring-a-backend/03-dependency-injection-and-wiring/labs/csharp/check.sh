#!/bin/sh
# Runs inside the .NET SDK container: restore, build and run the checks.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Audit "$work/"
output=$(dotnet run --project "$work/Audit" 2>&1) || { echo "build or run failed:"; echo "$output"; exit 1; }
echo "$output"
echo "$output" | grep -q "Cannot consume scoped service 'RequestContext' from singleton 'CaptiveAuditService'"
echo "$output" | grep -q "scoped: ada: viewed invoice, bayo: viewed invoice"
