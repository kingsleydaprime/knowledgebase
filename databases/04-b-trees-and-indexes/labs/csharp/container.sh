#!/bin/sh
# Runs check.sh in the .NET SDK container, on a copy of this lab (and ../shared). Run it through
# ../shared/with-postgres.sh: the container shares the host's network, so it reaches the throwaway database on
# 127.0.0.1:$PGPORT.
set -eu
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
nuget="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/nuget" # restored packages, kept between runs
mkdir -p "$nuget"
cp -r . "$tmp/csharp"
cp -r ../shared "$tmp/shared"
podman run --rm --network host -e PGPORT="$PGPORT" -v "$tmp":/lab:Z -v "$nuget":/root/.nuget/packages:Z -w /lab/csharp \
    mcr.microsoft.com/dotnet/sdk:10.0 sh check.sh
