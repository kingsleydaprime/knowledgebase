#!/bin/sh
# Runs inside the .NET SDK container: build once into /ai/out, then run the checks.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
dotnet build Tools -o /ai/out --nologo -v quiet -clp:ErrorsOnly
dotnet /ai/out/Tools.dll
