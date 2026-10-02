#!/bin/sh
# Prove the boundary is real: users tries to use orders' private repository module.
set -eu
export LC_ALL=C  # plain ASCII compiler messages, whatever the locale
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
cat >> "$work/src/users.rs" <<'RS'

pub fn sneak() {
    let _ = crate::orders::repository::Order { id: 0, user_id: String::new(), total_kobo: 0 };
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then
  echo "FAIL: users reached orders' private module and it compiled"; exit 1
fi
grep -q "error\[E0603\]: module \`repository\` is private" "$work/err.txt"
echo "ok: the compiler refused the cross-feature access"
