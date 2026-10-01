#!/bin/sh
# Runs inside the .NET SDK container.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Shop "$work/"
dotnet run --project "$work/Shop"
