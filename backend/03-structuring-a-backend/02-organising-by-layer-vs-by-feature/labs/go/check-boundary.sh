#!/bin/sh
# Prove the boundary is real: copy the project, add a forbidden import, and expect the build to fail.
set -eu
export LC_ALL=C  # plain ASCII compiler messages, whatever the locale
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r . "$work"
cat > "$work/internal/users/sneak.go" <<'GO'
package users

import "shop/internal/orders/internal/store"

var _ = store.Memory{}
GO
if (cd "$work" && go build ./... 2>"$work/err.txt"); then
  echo "FAIL: users imported orders' private store and the build still passed"; exit 1
fi
grep -q "use of internal package shop/internal/orders/internal/store not allowed" "$work/err.txt"
echo "ok: the compiler refused the cross-feature import"
