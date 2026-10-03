#!/bin/sh
# Runs inside the .NET SDK container; container.sh mounts a copy of this lab.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
dotnet run --project Joins
