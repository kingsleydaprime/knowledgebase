#!/bin/sh
# Python allows the reversed import; import-linter's layers contract refuses it.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
uv run -q --no-project --with import-linter lint-imports >/dev/null
echo "ok: the contract holds"
cp -r shop pyproject.toml "$work/"
printf '\nfrom shop.adapters import memory  # noqa: E402\n' >> "$work/shop/domain/__init__.py"
if (cd "$work" && uv run -q --no-project --with import-linter lint-imports >"$work/out.txt" 2>&1); then echo "FAIL: the reversed import passed"; exit 1; fi
grep -q "shop.domain -> shop.adapters.memory" "$work/out.txt" || { cat "$work/out.txt"; exit 1; }
echo "ok: import-linter refused shop.domain -> shop.adapters"
