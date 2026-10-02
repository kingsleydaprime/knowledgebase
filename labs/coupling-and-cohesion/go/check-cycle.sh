#!/bin/sh
# Go refuses import cycles between packages at compile time. Build one and watch it fail.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/orders" "$work/payments"
printf 'module shop\n\ngo 1.24\n' > "$work/go.mod"
cat > "$work/orders/orders.go" <<'GO'
package orders

import "shop/payments"

func MarkPaid(id int) string { return "paid" }
func Checkout(id int) string { return payments.Charge(id) }
GO
cat > "$work/payments/payments.go" <<'GO'
package payments

import "shop/orders"

func Charge(id int) string { return orders.MarkPaid(id) }
GO
if (cd "$work" && go build ./... 2>"$work/err.txt"); then echo "FAIL: the cycle compiled"; exit 1; fi
grep -q "import cycle not allowed" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: go build refused the orders <-> payments import cycle"
