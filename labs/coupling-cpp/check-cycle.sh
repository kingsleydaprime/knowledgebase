#!/bin/sh
# C++: the same header cycle, with classes. Forward-declare one side and hold it by pointer or reference.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cat > "$work/order.hpp" <<'CPP'
#pragma once
#include "payment.hpp"
class Order { public: int id = 0; Payment payment; };
CPP
cat > "$work/payment.hpp" <<'CPP'
#pragma once
#include "order.hpp"
class Payment { public: int amount = 0; Order order; };
CPP
echo '#include "order.hpp"' > "$work/main.cpp"
if g++ -std=c++20 -c "$work/main.cpp" -o "$work/main.o" 2>"$work/err.txt"; then echo "FAIL: compiled"; exit 1; fi
grep -q "'Order' does not name a type" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: the header cycle fails: 'Order' does not name a type"

cat > "$work/payment.hpp" <<'CPP'
#pragma once
class Order;                                       // forward declaration instead of the include
class Payment { public: int amount = 0; const Order* order = nullptr; };
CPP
g++ -std=c++20 -Wall -Wextra -Werror -c "$work/main.cpp" -o "$work/main.o"
echo "ok: a forward declaration and a pointer break the cycle"
