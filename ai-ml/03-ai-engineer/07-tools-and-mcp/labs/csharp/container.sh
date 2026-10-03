#!/bin/sh
# Builds and checks the lab in the .NET SDK container, then has the official MCP client (on the host)
# check the server, which it starts inside the same image with `podman run -i`, over stdio.
set -eu
lab=$(basename "$(dirname "$(dirname "$PWD")")")/labs # e.g. 07-tools-and-mcp/labs
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
nuget="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/nuget" # restored packages, kept between runs
mkdir -p "$tmp/$lab" "$nuget"
cp -r ../shared "$tmp/$lab/shared"
cp -r . "$tmp/$lab/csharp"
podman run --rm -v "$tmp":/ai:Z -v "$nuget":/root/.nuget/packages:Z -w "/ai/$lab/csharp" mcr.microsoft.com/dotnet/sdk:10.0 sh check.sh
sh ../shared/conformance.sh podman run -i --rm -v "$tmp":/ai:Z -w "/ai/$lab/csharp" mcr.microsoft.com/dotnet/sdk:10.0 dotnet /ai/out/Tools.dll serve
