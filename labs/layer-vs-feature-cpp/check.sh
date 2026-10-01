#!/bin/sh
# Configure, build, test, then prove another target can't include orders' private header.
set -eu
export LC_ALL=C  # plain ASCII compiler messages, whatever the locale
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

cmake -S . -B "$work/build" -DCMAKE_BUILD_TYPE=Debug >/dev/null
cmake --build "$work/build" -j >/dev/null
ctest --test-dir "$work/build" --output-on-failure >/dev/null || { echo "tests failed"; exit 1; }
echo "ok: orders tests passed"
output=$("$work/build/shop")
[ "$output" = "u1: order 1
nobody: rejected" ] || { echo "unexpected output: $output"; exit 1; }
echo "ok: the app runs"

cp -r . "$work/src"
mkdir -p "$work/src/sneak"
cat > "$work/src/sneak/sneak.cpp" <<'CPP'
#include "repository.hpp"  // orders' private header
int main() { return 0; }
CPP
cat >> "$work/src/CMakeLists.txt" <<'CMAKE'
add_executable(sneak sneak/sneak.cpp)
target_link_libraries(sneak PRIVATE orders)  # links orders, but gets only its PUBLIC headers
CMAKE
cmake -S "$work/src" -B "$work/bad" >/dev/null
if cmake --build "$work/bad" --target sneak >"$work/err.txt" 2>&1; then
  echo "FAIL: another target included orders' private header"; exit 1
fi
grep -q "repository.hpp: No such file or directory" "$work/err.txt"
echo "ok: the build refused orders' private header"
