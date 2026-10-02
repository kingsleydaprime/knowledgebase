#!/bin/sh
# Try to cancel a shipped order. With typestate, the method doesn't exist: E0599.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
cat >> "$work/src/lib.rs" <<'RS'

pub fn cancel_after_shipping() {
    let _ = Order::new("o2", vec![]).pay().ship().cancel();
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: cancelled a shipped order"; exit 1; fi
grep -q "error\[E0599\]: no method named \`cancel\` found for struct \`Order<Shipped>\`" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: rustc refused to cancel a shipped order (E0599)"
