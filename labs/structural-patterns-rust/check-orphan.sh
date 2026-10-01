#!/bin/sh
# The orphan rule: implementing a foreign trait (std's Display) for a foreign type (Vec) is refused.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
cat >> "$work/src/lib.rs" <<'RS'

impl std::fmt::Display for Vec<u64> {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result { write!(f, "{}", self.len()) }
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: compiled"; exit 1; fi
grep -q "error\[E0117\]: only traits defined in the current crate can be implemented for types defined outside of the crate" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: rustc applied the orphan rule (E0117) — wrap the type in a newtype instead"
