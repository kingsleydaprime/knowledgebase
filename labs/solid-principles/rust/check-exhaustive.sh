#!/bin/sh
# Add a USSD variant to the closed enum but not to the match: the build must fail.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
sed -i 's/^    Transfer,$/    Transfer,\n    Ussd,/' "$work/src/lib.rs"
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: the missing case compiled"; exit 1; fi
grep -q "error\[E0004\]: non-exhaustive patterns: \`&Method::Ussd\` not covered" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: rustc refused the unhandled Ussd variant (E0004)"
