#!/bin/sh
# Runs check.sh in the .NET SDK container. The project links files from the tools and evals labs, so a
# copy of those, laid out as in the vault, is mounted: the vault's own files are never relabelled.
set -eu
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
nuget="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/nuget" # restored packages, kept between runs
mkdir -p "$nuget" "$tmp/07-tools-and-mcp/labs/csharp/Tools" "$tmp/12-evals/labs/csharp/Evals" "$tmp/08-agents/labs"
cp ../../../07-tools-and-mcp/labs/csharp/Tools/Tools.cs "$tmp/07-tools-and-mcp/labs/csharp/Tools/"
cp -r ../../../07-tools-and-mcp/labs/shared "$tmp/07-tools-and-mcp/labs/"
cp ../../../12-evals/labs/csharp/Evals/Evals.cs "$tmp/12-evals/labs/csharp/Evals/"
cp -r . "$tmp/08-agents/labs/csharp"
podman run --rm -v "$tmp":/ai:Z -v "$nuget":/root/.nuget/packages:Z -w /ai/08-agents/labs/csharp mcr.microsoft.com/dotnet/sdk:10.0 sh check.sh
