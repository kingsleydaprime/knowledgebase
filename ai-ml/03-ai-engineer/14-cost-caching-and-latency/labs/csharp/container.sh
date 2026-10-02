#!/bin/sh
# Runs check.sh in the .NET SDK container. The project links a file from the evals lab, so a copy of
# both, laid out as in the vault, is mounted: the vault's own files are never relabelled for the container.
set -eu
lab=$(basename "$(dirname "$(dirname "$PWD")")")/labs/csharp # e.g. 13-reliability-and-plumbing/labs/csharp
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/12-evals/labs/csharp/Evals" "$tmp/$(dirname "$lab")"
cp ../../../12-evals/labs/csharp/Evals/Evals.cs "$tmp/12-evals/labs/csharp/Evals/"
cp -r ../../../12-evals/labs/shared "$tmp/12-evals/labs/"
cp -r . "$tmp/$lab"
podman run --rm -v "$tmp":/ai:Z -w "/ai/$lab" mcr.microsoft.com/dotnet/sdk:10.0 sh check.sh
