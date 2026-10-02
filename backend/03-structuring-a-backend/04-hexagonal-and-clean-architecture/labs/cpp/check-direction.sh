#!/bin/sh
# Build and test; then make the domain include an adapter header. The domain target links
# nothing, so the adapters' include directory isn't on its path, and the build fails.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cmake -S . -B "$work/build" >/dev/null && cmake --build "$work/build" -j >/dev/null
ctest --test-dir "$work/build" --output-on-failure >/dev/null || { echo "tests failed"; exit 1; }
echo "ok: use case runs on in-memory adapters"
cp -r . "$work/src"
sed -i 's|#include "domain/domain.hpp"|#include "domain/domain.hpp"\n#include "adapters/memory.hpp"|' "$work/src/domain/src/domain.cpp"
cmake -S "$work/src" -B "$work/bad" >/dev/null
if cmake --build "$work/bad" --target domain >"$work/err.txt" 2>&1; then echo "FAIL: built"; exit 1; fi
grep -q "adapters/memory.hpp: No such file or directory" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: the domain target refused to include an adapter header"
