#!/bin/sh
# Runs check.sh in the .NET SDK container, on a copy of this lab: the vault's own files are never relabelled.
# The certificates are made out here, with the host's OpenSSL, so the container needs no tools of its own.
set -eu
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
nuget="${XDG_CACHE_HOME:-$HOME/.cache}/knowledgebase-labs/nuget" # restored packages, kept between runs
mkdir -p "$nuget"
cp -r . "$tmp/csharp"
sh ../shared/make-certs.sh "$tmp/certs"
podman run --rm -v "$tmp":/lab:Z -v "$nuget":/root/.nuget/packages:Z -w /lab/csharp mcr.microsoft.com/dotnet/sdk:10.0 sh check.sh
