#!/bin/sh
# Runs check.sh in the .NET SDK container. The project links the structured-output lab's Invoice.cs, so a
# copy of both, laid out as in the vault, is mounted: the vault's own files are never relabelled.
set -eu
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/11-structured-output/labs/csharp/Invoices" "$tmp/09-multimodal/labs"
cp ../../../11-structured-output/labs/csharp/Invoices/Invoice.cs "$tmp/11-structured-output/labs/csharp/Invoices/"
cp -r . "$tmp/09-multimodal/labs/csharp"
podman run --rm -v "$tmp":/ai:Z -w /ai/09-multimodal/labs/csharp mcr.microsoft.com/dotnet/sdk:10.0 sh check.sh
