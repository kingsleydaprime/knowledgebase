# Coupling and Cohesion in Other Languages

> **[Beginner→Intermediate]** · A companion to [[concepts/04-best-practices/08-coupling-and-cohesion/index|coupling and cohesion]], whose lab measures coupling in JavaScript projects. The kinds of coupling are the same in every language. What differs is **which dependency cycles the toolchain refuses**, and which tool measures the rest.

## Before you start

You can already:

- Name the kinds of coupling, compute fan-in, fan-out and instability, and explain why a cycle is the worst case → [[concepts/04-best-practices/08-coupling-and-cohesion/index|the main lesson]].
- Read code in at least one language below. Read §1 and your languages.

After this lesson you will be able to:

1. Say whether your language's compiler or build tool refuses dependency cycles, and at which level — package, crate, project or none.
2. Break a cycle in your language: with an event, an interface on the stable side, or a forward declaration.
3. Name the tool that shows your project's dependency graph.

## The kid version

Two friends who each refuse to start their homework until the other finishes theirs will never finish. That's a dependency cycle. Some schools have a rule that stops it before it starts — "you can't wait on someone who's waiting on you" (a **toolchain that refuses cycles**). Others let it happen and you find out at the deadline (**a runtime error**, or no error at all and just a tangled project).

**Where the analogy stops working.** The friends are stuck forever. In most languages a code cycle still *runs* — it just means the two parts can only ever change, be tested and be deployed together. A cycle is a design cost before it's ever a crash.

## 1. Who refuses a cycle

| Language | Level that can't have a cycle | Level where a cycle is allowed | Measuring tool |
|---|---|---|---|
| TypeScript | — (only lint rules) | files and folders | dependency-cruiser, Madge, the main lesson's lab |
| Python | — (some import styles fail at runtime) | modules and packages | import-linter, pydeps |
| Go | **packages** — `import cycle not allowed` | — | `go list -deps`, `go mod graph` |
| Java | modules (JPMS) | **packages** — compiles silently | `jdeps`, ArchUnit |
| Rust | **crates** — `cyclic package dependency` | modules inside a crate | `cargo tree`, cargo-modules |
| C, C++ | values held by both sides — "incomplete type" | pointers, with forward declarations | include-what-you-use, Graphviz from CMake |
| C# | **projects** — `MSB4006` | namespaces inside a project | NDepend, ArchUnitNET |

**The pattern:** wherever a language has a unit of *separate compilation* — Go packages, Rust crates, .NET projects — it refuses cycles between them, because it needs an order to build them in. Inside that unit, it usually doesn't care. So **putting each feature in its own package, crate or project gets cycle detection for free**, which is one more reason for the [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/in-compiled-languages|by-feature layout in compiled languages]].

## Terms used in this lesson

1. **Unit of compilation**: This is the piece a build tool compiles as one — a Go package, a Rust crate, a .NET project, a C or C++ source file.
2. **Forward declaration**: In C and C++, this is a line that names a type without defining it (`struct order;`), so you can hold a pointer to it without including its header.
3. **Partially initialised module**: In Python, this is a module whose code is still running when another module tries to import a name from it — the state a circular import leaves you in.
4. **Dependency graph**: This is a map of which units import which. A cycle is a loop in it.

## 2. Python

Python allows cycles, but **`from module import name` fails if `module` is still being initialised** — which is exactly what a cycle causes. `import module` and accessing `module.name` later often works, which is why circular imports appear to come and go as code changes. The fix is structural: break the cycle.

```python
# cycle/payments.py — ...and payments imports a name from orders: a cycle.
from orders import mark_paid


def charge(order_id):
    return mark_paid(order_id)
```

```python
# fixed/payments.py — payments announces an event instead of calling orders.
import events


def charge(order_id):
    return events.publish({"type": "PaymentSucceeded", "order_id": order_id})
```

```python
import subprocess
import sys
import unittest


def run(folder, code):
    return subprocess.run([sys.executable, "-c", code], cwd=folder, capture_output=True, text=True)


class CycleTests(unittest.TestCase):
    def test_a_from_import_cycle_fails_at_import_time(self):
        result = run("cycle", "import orders")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImportError: cannot import name 'mark_paid' from", result.stderr)  # wording after this varies by version

    def test_the_event_breaks_the_cycle(self):
        result = run("fixed", "import orders; print(orders.checkout(7))")
        self.assertEqual(result.stdout.strip(), "['order 7 paid']")


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`concepts/04-best-practices/08-coupling-and-cohesion/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/08-coupling-and-cohesion/labs/python) — checked with Python 3.14. The error's wording varies between versions; it always starts `ImportError: cannot import name 'mark_paid' from`. To *prevent* cycles rather than discover them, add an import-linter `independence` or `layers` contract, as in [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|layer vs feature]].

## 3. Go

**Go refuses import cycles between packages at compile time.** You can't build a cyclic program, so every Go dependency graph is acyclic by construction. The usual fix is Go's "accept interfaces" habit: `payments` declares the small interface it needs (`type OrderMarker interface { MarkPaid(int) }`) and the composition root passes `orders` in.

```sh
#!/bin/sh
# Go refuses import cycles between packages at compile time. Build one and watch it fail.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/orders" "$work/payments"
printf 'module shop\n\ngo 1.24\n' > "$work/go.mod"
cat > "$work/orders/orders.go" <<'GO'
package orders

import "shop/payments"

func MarkPaid(id int) string { return "paid" }
func Checkout(id int) string { return payments.Charge(id) }
GO
cat > "$work/payments/payments.go" <<'GO'
package payments

import "shop/orders"

func Charge(id int) string { return orders.MarkPaid(id) }
GO
if (cd "$work" && go build ./... 2>"$work/err.txt"); then echo "FAIL: the cycle compiled"; exit 1; fi
grep -q "import cycle not allowed" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: go build refused the orders <-> payments import cycle"
```

**Lab:** [`concepts/04-best-practices/08-coupling-and-cohesion/labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/08-coupling-and-cohesion/labs/go) — prints `ok: go build refused the orders <-> payments import cycle`. Checked with Go 1.26. `go list -deps ./...` and `go mod graph` show the graph.

## 4. Java

**Java compiles a cycle between packages without a word.** Only the module system (`module-info.java`) refuses cycles, between modules. Within an ordinary application, cycles accumulate silently — so you find them with `jdeps`, which ships with the JDK, and prevent them with an **ArchUnit** test (`slices().matching("..shop.(*)..").should().beFreeOfCycles()`) or **Spring Modulith**'s `verify()`.

```java
package shop.payments;

import shop.orders.Orders;

public final class Payments {
    public static String charge(int id) { return Orders.markPaid(id); } // reaches back: a cycle
}
```

```sh
#!/bin/sh
# Java compiles a package cycle without complaint. jdeps (shipped with the JDK) shows it.
set -eu
export LC_ALL=C
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
javac -d "$out" src/shop/orders/Orders.java src/shop/payments/Payments.java
echo "ok: javac compiled the cycle without a warning"
jdeps -verbose:package "$out" > "$out/deps.txt"
grep -Eq "shop\.orders +-> +shop\.payments" "$out/deps.txt" || { cat "$out/deps.txt"; exit 1; }
grep -Eq "shop\.payments +-> +shop\.orders" "$out/deps.txt" || { cat "$out/deps.txt"; exit 1; }
echo "ok: jdeps shows both directions: shop.orders <-> shop.payments"
```

**Lab:** [`concepts/04-best-practices/08-coupling-and-cohesion/labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/08-coupling-and-cohesion/labs/java) — checked with Java 21. `jdeps -verbose:package` prints `shop.orders -> shop.payments` *and* `shop.payments -> shop.orders`.

## 5. Rust

**Cargo refuses cycles between crates**: `cyclic package dependency`. Modules inside one crate may refer to each other in any direction, so a large single crate can still be tangled. For hard boundaries — and free cycle detection — split features into crates in a workspace.

```sh
#!/bin/sh
# Cargo refuses a cycle between crates. Inside one crate, modules may refer to each other freely.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# 1. Two crates that depend on each other.
mkdir -p "$work/ws/orders/src" "$work/ws/payments/src"
printf '[workspace]\nmembers = ["orders", "payments"]\nresolver = "3"\n' > "$work/ws/Cargo.toml"
printf '[package]\nname = "orders"\nversion = "0.1.0"\nedition = "2024"\n\n[dependencies]\npayments = { path = "../payments" }\n' > "$work/ws/orders/Cargo.toml"
printf '[package]\nname = "payments"\nversion = "0.1.0"\nedition = "2024"\n\n[dependencies]\norders = { path = "../orders" }\n' > "$work/ws/payments/Cargo.toml"
echo 'pub fn mark_paid() {}' > "$work/ws/orders/src/lib.rs"
echo 'pub fn charge() {}' > "$work/ws/payments/src/lib.rs"
if (cd "$work/ws" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: the crate cycle built"; exit 1; fi
grep -q "cyclic package dependency" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: cargo refused the orders <-> payments crate cycle"

# 2. The same cycle between modules of one crate compiles.
mkdir -p "$work/one/src"
printf '[package]\nname = "shop"\nversion = "0.1.0"\nedition = "2024"\n' > "$work/one/Cargo.toml"
cat > "$work/one/src/lib.rs" <<'RS'
pub mod orders {
    pub fn mark_paid() -> &'static str { "paid" }
    pub fn checkout() -> &'static str { crate::payments::charge() }
}
pub mod payments {
    pub fn charge() -> &'static str { crate::orders::mark_paid() }
}
RS
(cd "$work/one" && cargo build --quiet)
echo "ok: modules inside one crate may form a cycle — only crates are checked"
```

**Lab:** [`concepts/04-best-practices/08-coupling-and-cohesion/labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/08-coupling-and-cohesion/labs/rust) — checked with Rust 1.96. `cargo tree` shows the crate graph.

## 6. C

There's no import system — headers are pasted in by the preprocessor. Two headers that include each other compile only thanks to include guards, and then one struct is always seen before the other is complete. **Holding each other by value is impossible**; holding one side by pointer, with a **forward declaration** instead of an `#include`, breaks the cycle.

```sh
#!/bin/sh
# Two headers that include each other, each holding the other's struct by value: impossible.
# Include guards stop the infinite loop, so one struct is always seen before the other is defined.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cat > "$work/order.h" <<'C'
#ifndef ORDER_H
#define ORDER_H
#include "payment.h"
struct order { int id; struct payment payment; };
#endif
C
cat > "$work/payment.h" <<'C'
#ifndef PAYMENT_H
#define PAYMENT_H
#include "order.h"
struct payment { int amount; struct order order; };
#endif
C
echo '#include "order.h"' > "$work/main.c"
if gcc -std=c17 -c "$work/main.c" -o "$work/main.o" 2>"$work/err.txt"; then echo "FAIL: compiled"; exit 1; fi
grep -q "field 'order' has incomplete type" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: the header cycle fails: field 'order' has incomplete type"

# The fix: one side holds a pointer, and a forward declaration replaces the include.
cat > "$work/payment.h" <<'C'
#ifndef PAYMENT_H
#define PAYMENT_H
struct order;                                    /* forward declaration: no include needed */
struct payment { int amount; struct order *order; };
#endif
C
gcc -std=c17 -Wall -Wextra -Werror -c "$work/main.c" -o "$work/main.o"
echo "ok: a forward declaration and a pointer break the cycle"
```

**Lab:** [`concepts/04-best-practices/08-coupling-and-cohesion/labs/c/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/08-coupling-and-cohesion/labs/c) — checked with GCC 16. Fewer includes in headers also means faster builds: every header a header includes is recompiled by everyone who includes it. **include-what-you-use** finds unnecessary ones.

## 7. C++

The same mechanics as C, with classes: `'Order' does not name a type`. The fix is the same — a forward declaration and a pointer or reference — and the [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/in-compiled-languages|pimpl]] pattern takes it further, keeping a class's private members out of its header entirely. Between libraries, CMake's `target_link_libraries` builds an explicit graph; CMake can export it for Graphviz with `cmake --graphviz=deps.dot`.

```sh
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
```

**Lab:** [`concepts/04-best-practices/08-coupling-and-cohesion/labs/cpp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/08-coupling-and-cohesion/labs/cpp) — checked with GCC 16.

## 8. C#

**Project references can't form a cycle**: the build fails with `MSB4006: There is a circular dependency`. Namespaces inside one project can be as tangled as you like, so — as with Rust crates — features in separate projects get cycle detection for free. Inside a project, ArchUnitNET or NetArchTest express the rules as tests.

```sh
#!/bin/sh
# Runs inside the .NET SDK container. Two projects that reference each other can't build.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
for name in Orders Payments; do
  mkdir -p "$work/$name"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>\n' > "$work/$name/$name.csproj"
  echo "namespace $name; public static class Api { }" > "$work/$name/Api.cs"
done
(cd "$work/Orders" && dotnet add reference ../Payments/Payments.csproj >/dev/null)
(cd "$work/Payments" && dotnet add reference ../Orders/Orders.csproj >/dev/null)
if dotnet build "$work/Orders" >"$work/out.txt" 2>&1; then echo "FAIL: the project cycle built"; exit 1; fi
grep -q "error MSB4006: There is a circular dependency" "$work/out.txt" || { cat "$work/out.txt"; exit 1; }
echo "ok: the build refused the Orders <-> Payments project cycle"
```

**Lab:** [`concepts/04-best-practices/08-coupling-and-cohesion/labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/08-coupling-and-cohesion/labs/csharp) — runs in the .NET 10 SDK container.

## Check your understanding

1. In which languages does a cycle between your top-level units fail the build?
2. Why does a Python circular import sometimes work and sometimes fail?
3. Your Java service compiles fine. How would you find out whether its packages form a cycle?
4. Why can't two C structs each contain the other by value, and what's the fix?
5. Why does splitting features into separate Go packages, Rust crates or .NET projects give you cycle detection for free?

<details>
<summary>Answers — after your attempt</summary>

1. Go (packages), Rust (crates), C# (projects). Java only for JPMS modules; Python, TypeScript, C and C++ don't refuse cycles as such.
2. `from x import name` needs `name` to exist when the import runs; in a cycle, `x` may still be half-initialised. `import x` with later access to `x.name` usually works, because by then `x` has finished. Which happens depends on import order — so it appears and disappears as code changes.
3. Run `jdeps -verbose:package` on the compiled classes, or add an ArchUnit `beFreeOfCycles()` test (or Spring Modulith's `verify()`) so CI checks it.
4. Each would need the other's full size to be known first, which is impossible. Hold one side by pointer and forward-declare it instead of including its header.
5. Those are the units the build tool compiles in order, so it has to refuse cycles between them. Inside one unit it doesn't need an order, so it doesn't check.

</details>

## Practice — independent task

**Find out what your language does, on your own project.** Run your language's graph tool from §1 on one real project. If it has a cycle, break it with an event, an interface on the stable side, or a forward declaration. If the language allows cycles, add the test or lint rule that will stop the next one.

**Done when:** you have the graph before and after, no cycles remain, and a check — the build itself, a test, or a lint rule — fails if one is reintroduced.

## Before moving on

You know which cycles your language refuses, how to break one, and which tool shows the graph.

**Recap.** Separately compiled units can't form cycles: Go packages, Rust crates, .NET projects. Java packages, Python modules, TypeScript files and C or C++ headers can — and need a tool or test to stop them. Break a cycle with an event, an interface owned by the stable side, or a forward declaration.

**Next.** Back to the course: [[concepts/04-best-practices/05-solid-principles/index|SOLID]].

## Related
- [[concepts/04-best-practices/08-coupling-and-cohesion/index|Coupling and cohesion]] — the main lesson
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/in-compiled-languages|Organising by feature in compiled languages]] — the boundaries these tools check
