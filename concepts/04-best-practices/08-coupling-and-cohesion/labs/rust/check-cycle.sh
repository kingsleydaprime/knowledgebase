#!/bin/sh
# Cargo refuses a cycle between crates. Inside one crate, modules may refer to each other freely.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# 1. Two crates that depend on each other.
mkdir -p "$work/ws/orders/src" "$work/ws/payments/src"
printf '[workspace]\nmembers = ["orders", "payments"]\nresolver = "3"\n' > "$work/ws/Cargo.toml"
printf '[package]\nname = "orders"\nversion = "0.1.0"\nedition = "2024"\n\n[dependencies]\npayments = { path = "../payments" }\n' > "$work/ws/orders/Cargo.toml"
printf '[package]\nname = "payments"\nversion = "0.1.0"\nedition = "2024"\n\n[dependencies]\norders = { path = "../orders" }\n' > "$work/ws/payments/Cargo.toml"
echo 'pub fn mark_paid() {}' > "$work/ws/orders/src/lib.rs"
echo 'pub fn charge() {}' > "$work/ws/payments/src/lib.rs"
if (cd "$work/ws" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: the crate cycle built"; exit 1; fi
grep -q "cyclic package dependency" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: cargo refused the orders <-> payments crate cycle"

# 2. The same cycle between modules of one crate compiles.
mkdir -p "$work/one/src"
printf '[package]\nname = "shop"\nversion = "0.1.0"\nedition = "2024"\n' > "$work/one/Cargo.toml"
cat > "$work/one/src/lib.rs" <<'RS'
pub mod orders {
    pub fn mark_paid() -> &'static str { "paid" }
    pub fn checkout() -> &'static str { crate::payments::charge() }
}
pub mod payments {
    pub fn charge() -> &'static str { crate::orders::mark_paid() }
}
RS
(cd "$work/one" && cargo build --quiet)
echo "ok: modules inside one crate may form a cycle — only crates are checked"
