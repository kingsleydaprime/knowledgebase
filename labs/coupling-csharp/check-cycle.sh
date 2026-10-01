#!/bin/sh
# Runs inside the .NET SDK container. Two projects that reference each other can't build.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
for name in Orders Payments; do
  mkdir -p "$work/$name"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>\n' > "$work/$name/$name.csproj"
  echo "namespace $name; public static class Api { }" > "$work/$name/Api.cs"
done
(cd "$work/Orders" && dotnet add reference ../Payments/Payments.csproj >/dev/null)
(cd "$work/Payments" && dotnet add reference ../Orders/Orders.csproj >/dev/null)
if dotnet build "$work/Orders" >"$work/out.txt" 2>&1; then echo "FAIL: the project cycle built"; exit 1; fi
grep -q "error MSB4006: There is a circular dependency" "$work/out.txt" || { cat "$work/out.txt"; exit 1; }
echo "ok: the build refused the Orders <-> Payments project cycle"
