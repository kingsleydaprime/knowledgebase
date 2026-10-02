#!/bin/sh
# The domain is compiled with only its own folder on the include path, so it can't include an adapter.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
F="-std=c17 -Wall -Wextra -Werror"
gcc $F -Idomain -c domain/domain.c -o "$work/domain.o"                       # domain: sees domain/ only
gcc $F -Idomain -Iadapters -o "$work/test" test_place_order.c adapters/in_memory.c "$work/domain.o"
"$work/test"
cp -r domain adapters "$work/"
sed -i 's|#include "domain.h"|#include "domain.h"\n#include "in_memory.h"|' "$work/domain/domain.c"
if gcc $F -I"$work/domain" -c "$work/domain/domain.c" -o "$work/bad.o" 2>"$work/err.txt"; then echo "FAIL"; exit 1; fi
grep -q "in_memory.h: No such file or directory" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: the domain's build refused to include an adapter header"
