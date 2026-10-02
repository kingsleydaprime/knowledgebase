#!/bin/sh
# Runs inside the .NET SDK container. Build and run, then prove the app can't reach
# orders' internal repository from another assembly.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r src "$work/src"

output=$(dotnet run --project "$work/src/Shop.App" 2>&1) || { echo "build or run failed:"; echo "$output"; exit 1; }
expected='Order { Id = 1, UserId = u1, TotalKobo = 500000 }
rejected'
[ "$output" = "$expected" ] || { echo "unexpected output:"; echo "$output"; exit 1; }
echo "ok: the app runs"

cat > "$work/src/Shop.App/Sneak.cs" <<'CS'
static class Sneak
{
    public static object Reach() => new Shop.Orders.OrdersRepository();
}
CS
if dotnet build "$work/src/Shop.App" >"$work/err.txt" 2>&1; then
  echo "FAIL: the app reached orders' internal repository and it compiled"; exit 1
fi
grep -q "error CS0122: 'OrdersRepository' is inaccessible due to its protection level" "$work/err.txt"
echo "ok: the compiler refused the cross-feature access"
