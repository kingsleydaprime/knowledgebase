#!/bin/sh
# Build and run; then add Ussd to the variant without an overload and expect a compile error.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
g++ -std=c++20 -Wall -Wextra -Werror -o "$work/fees" fees.cpp && "$work/fees"
sed -e 's/^struct Transfer {};$/struct Transfer {};\nstruct Ussd {};/' \
    -e 's/std::variant<Card, Transfer>/std::variant<Card, Transfer, Ussd>/' fees.cpp > "$work/bad.cpp"
if g++ -std=c++20 -o "$work/bad" "$work/bad.cpp" 2>"$work/err.txt"; then echo "FAIL: compiled"; exit 1; fi
# The error is long; its key line says no overload can be invoked with a `const Ussd&`.
grep -q "no type named 'type' in 'struct std::invoke_result<.*, const Ussd&>'" "$work/err.txt" || { head -20 "$work/err.txt"; exit 1; }
echo "ok: g++ refused the visit that has no overload for Ussd"
