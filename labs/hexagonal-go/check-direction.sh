#!/bin/sh
# The adapter imports the domain, so a domain that imports the adapter is an import cycle —
# which Go refuses. The dependency rule is enforced by the compiler.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r . "$work/src"
cat > "$work/src/domain/sneak.go" <<'GO'
package domain

import "shop/adapters/memory"

var _ = memory.Payments{}
GO
if (cd "$work/src" && go build ./... 2>"$work/err.txt"); then echo "FAIL: the domain imported an adapter"; exit 1; fi
grep -q "import cycle not allowed" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: go build refused domain -> adapters (import cycle)"
