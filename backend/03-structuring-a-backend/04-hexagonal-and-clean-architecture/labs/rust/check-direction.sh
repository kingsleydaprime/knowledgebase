#!/bin/sh
# Make the domain depend on the adapters crate: with adapters already depending on the domain,
# that's a crate cycle, which Cargo refuses.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml domain adapters "$work/"
sed -i 's|^# None.*|adapters = { path = "../adapters" }|' "$work/domain/Cargo.toml"
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: domain -> adapters built"; exit 1; fi
grep -q "cyclic package dependency" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: cargo refused domain -> adapters (cyclic package dependency)"
