#!/bin/sh
# Runs inside the .NET SDK container, with the lesson's labs/ folder mounted at /labs.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Prompts "$work/"
dotnet run --project "$work/Prompts" -- /labs/shared
