#!/bin/sh
# Build and run; then add METHOD_USSD to the enum and expect -Wswitch-enum -Werror to refuse.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
FLAGS="-std=c17 -Wall -Wextra -Wswitch-enum -Werror"
gcc $FLAGS -o "$work/fees" fees.c && "$work/fees"
sed 's/METHOD_CARD, METHOD_TRANSFER }/METHOD_CARD, METHOD_TRANSFER, METHOD_USSD }/' fees.c > "$work/bad.c"
if gcc $FLAGS -o "$work/bad" "$work/bad.c" 2>"$work/err.txt"; then echo "FAIL: compiled"; exit 1; fi
grep -q "enumeration value 'METHOD_USSD' not handled in switch" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: gcc refused the switch that doesn't handle METHOD_USSD"
