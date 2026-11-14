#!/bin/sh
# Python itself won't notice a new member until it runs. mypy, with assert_never, does.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
uv run -q --no-project --with mypy mypy --strict fees.py >/dev/null
echo "ok: mypy is happy with the complete match"
sed 's/^    TRANSFER = "transfer"$/    TRANSFER = "transfer"\n    USSD = "ussd"/' fees.py > "$work/fees.py"
if uv run -q --no-project --with mypy mypy --strict "$work/fees.py" >"$work/err.txt" 2>&1; then echo "FAIL: mypy missed USSD"; exit 1; fi
grep -q 'Argument 1 to "assert_never" has incompatible type "Literal\[Method.USSD\]"' "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: mypy refused the unhandled USSD member"
