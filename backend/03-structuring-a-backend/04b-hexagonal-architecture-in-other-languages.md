# Hexagonal Architecture in Other Languages

> **[Intermediate→Advanced]** · A companion to [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal and clean architecture]], which builds a checkout with ports and adapters in TypeScript and checks the dependency rule with `grep`. In most languages here, **the build can enforce the dependency rule itself** — because a domain that imports an adapter creates a cycle, or can't see the adapter's files at all.

## Before you start

You can already:

- Explain ports, driving and driven adapters, and the dependency rule — every import points inward → [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|the main lesson]].
- Read code in at least one language below. Read §1 and your languages.

After this lesson you will be able to:

1. Lay out a domain, its ports and an adapter in your language.
2. Make your build fail when the domain imports an adapter.
3. Say what your language uses as a port: an interface, a `Protocol`, a trait, an abstract class, or a struct of function pointers.

## The kid version

The main lesson's wall socket only works if the house is wired so appliances plug into the wall, never the wall into an appliance. In some houses an electrician checked the wiring when it was built — it's **impossible** to wire it backwards (the build refuses). In others nobody checked, and a backwards wire works until someone notices (**you need an inspector** — a lint rule or a test).

**Where the analogy stops working.** A backwards wire in a house is dangerous at once. A backwards import usually works fine for months — the cost is that the domain can no longer be tested or reused without the adapter. That's why you want the build to catch it, not a person.

## 1. What enforces the rule

The adapter imports the domain to implement its ports. So if the domain imports the adapter as well, the two depend on each other:

| Language | Domain → adapter is… | Port |
|---|---|---|
| TypeScript | allowed — catch with ESLint `no-restricted-paths` | `interface` |
| Python | allowed — catch with import-linter's `layers` contract | `Protocol` |
| Go | **a compile error**: `import cycle not allowed` | `interface`, declared in the domain |
| Java | allowed — catch with ArchUnit; `jdeps` shows it | `interface` |
| Rust | **a build error** between crates: `cyclic package dependency` | `trait` |
| C | **a build error** if the domain's include path excludes adapters | struct of function pointers |
| C++ | **a build error**: the domain target doesn't link adapters | abstract class |
| C# | **a build error** between projects: `MSB4006` | `interface` |

**The structural trick:** put the domain in its own unit of compilation — Go package, Rust crate, .NET project, CMake target — and make adapters depend on it. Then the dependency rule isn't a convention; it's how the code builds.

## Terms used in this lesson

1. **Port**: This is an interface the domain owns, describing something it needs — "save an order", "charge a customer".
2. **Adapter**: This is code that implements a port with a real technology, or with an in-memory fake for tests.
3. **Dependency rule**: This is the rule that imports point only inward, toward the domain.
4. **Layers contract**: In import-linter, this is a rule listing packages from outer to inner; an inner package importing an outer one breaks it.
5. **Workspace**: In Rust's Cargo, this is a group of crates built together, each with its own declared dependencies.

## 2. Python

Ports are `Protocol`s: any class with matching methods satisfies them, no inheritance needed, and a type checker verifies it. Python won't stop a reversed import, so the rule lives in an **import-linter `layers` contract**, run in CI.

```python
"""shop/domain — rules and ports. Imports nothing from shop.adapters."""
from dataclasses import dataclass
from typing import Protocol


class InvalidTotal(Exception):
    pass


class PaymentDeclined(Exception):
    pass


@dataclass
class Order:
    id: str
    total_kobo: int
    paid: bool = False


# Ports: Protocols say what the domain needs; any class with these methods fits.
class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...


class PaymentGateway(Protocol):
    def charge(self, customer_id: str, kobo: int) -> bool: ...


def place_order(orders: OrderRepository, payments: PaymentGateway, order_id: str, customer_id: str, kobo: int) -> Order:
    if kobo <= 0:
        raise InvalidTotal(kobo)
    if not payments.charge(customer_id, kobo):
        raise PaymentDeclined(order_id)
    order = Order(order_id, kobo, paid=True)
    orders.save(order)
    return order
```

```toml
[tool.importlinter]
root_package = "shop"

[[tool.importlinter.contracts]]
name = "The dependency rule: adapters may import the domain, never the reverse"
type = "layers"
layers = ["shop.adapters", "shop.domain"]
```

**Lab:** `labs/hexagonal-architecture/python/` — adding `from shop.adapters import memory` to the domain makes `lint-imports` fail with `shop.domain -> shop.adapters.memory`. Checked with Python 3.14.

## 3. Go

Go's habit of declaring interfaces **where they're used** puts ports in the domain package naturally. The adapter package imports the domain to use its types — so a domain that imports the adapter is an import cycle, and **Go refuses to compile it**.

```go
// Package domain holds the rules and the ports. It imports nothing from this module.
package domain

import "errors"

var ErrInvalidTotal = errors.New("total must be positive")
var ErrDeclined = errors.New("payment declined")

type Order struct {
	ID        string
	TotalKobo int64
	Paid      bool
}

// Ports: what the domain needs, declared here, where it's used.
type OrderRepository interface{ Save(Order) error }
type PaymentGateway interface {
	Charge(customerID string, kobo int64) (ok bool, err error)
}

// PlaceOrder is the use case. It depends only on the ports.
func PlaceOrder(orders OrderRepository, payments PaymentGateway, id, customerID string, kobo int64) (Order, error) {
	if kobo <= 0 {
		return Order{}, ErrInvalidTotal
	}
	ok, err := payments.Charge(customerID, kobo)
	if err != nil {
		return Order{}, err
	}
	if !ok {
		return Order{}, ErrDeclined
	}
	order := Order{ID: id, TotalKobo: kobo, Paid: true}
	return order, orders.Save(order)
}
```

```go
// Package memory holds driven adapters. It imports the domain — never the other way round.
package memory

import "shop/domain"

type Orders struct{ Saved []domain.Order }

func (o *Orders) Save(order domain.Order) error {
	o.Saved = append(o.Saved, order)
	return nil
}

type Payments struct{ DeclineAbove int64 }

func (p Payments) Charge(_ string, kobo int64) (bool, error) { return kobo <= p.DeclineAbove, nil }
```

```sh
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
```

**Lab:** `labs/hexagonal-architecture/go/` — checked with Go 1.26.

## 4. Java

Ports are interfaces; adapters implement them, often as lambdas when a port has one method. **Java compiles a reversed dependency without complaint**, so enforce it with an **ArchUnit** test — `layeredArchitecture().layer("Domain").definedBy("..domain..").mayNotAccessAnyLayer()`-style rules — or Spring Modulith. `jdeps` shows it after the fact.

```java
package shop.domain;

// The domain: rules and the ports it owns. Nothing here imports shop.adapters.
public final class Ports {
    public record Order(String id, long totalKobo, boolean paid) {}
    public interface OrderRepository { void save(Order order); }
    public interface PaymentGateway { boolean charge(String customerId, long kobo); }

    public static Order placeOrder(OrderRepository orders, PaymentGateway payments, String id, String customerId, long kobo) {
        if (kobo <= 0) throw new IllegalArgumentException("total must be positive");
        if (!payments.charge(customerId, kobo)) throw new IllegalStateException("payment declined");
        var order = new Order(id, kobo, true);
        orders.save(order);
        return order;
    }
}
```

**Lab:** `labs/hexagonal-architecture/java/` — the check shows javac compiling `shop.domain -> shop.adapters` and jdeps reporting it. Checked with Java 21.

## 5. Rust

Put the domain in **its own crate** with no dependencies, and the adapters in another crate that depends on it. Ports are traits. Reversing the dependency is a crate cycle, which Cargo refuses — and the domain's `Cargo.toml` documents, in one empty `[dependencies]` section, that it depends on nothing.

```toml
[package]
name = "adapters"
version = "0.1.0"
edition = "2024"

[dependencies]
domain = { path = "../domain" }   # adapters depend on the domain, not the reverse
```

```rust
//! Rules and ports. This crate has no dependencies.
#[derive(Debug, Clone, PartialEq)]
pub struct Order {
    pub id: String,
    pub total_kobo: u64,
    pub paid: bool,
}

#[derive(Debug, PartialEq)]
pub enum PlaceError {
    InvalidTotal,
    Declined,
}

// Ports: traits the domain defines and adapters implement.
pub trait OrderRepository {
    fn save(&mut self, order: Order);
}
pub trait PaymentGateway {
    fn charge(&self, customer_id: &str, kobo: u64) -> bool;
}

pub fn place_order(
    orders: &mut impl OrderRepository,
    payments: &impl PaymentGateway,
    id: &str,
    customer_id: &str,
    kobo: u64,
) -> Result<Order, PlaceError> {
    if kobo == 0 {
        return Err(PlaceError::InvalidTotal);
    }
    if !payments.charge(customer_id, kobo) {
        return Err(PlaceError::Declined);
    }
    let order = Order {
        id: id.into(),
        total_kobo: kobo,
        paid: true,
    };
    orders.save(order.clone());
    Ok(order)
}
```

**Lab:** `labs/hexagonal-architecture/rust/` — making the domain depend on adapters gives `cyclic package dependency`. Checked with Rust 1.96.

## 6. C

Ports are structs of function pointers. The rule is enforced by **include paths**: compile the domain with only its own folder on the path, and it can't include an adapter header.

```c
/* domain.h — rules and ports. Includes nothing from adapters/. */
#ifndef DOMAIN_H
#define DOMAIN_H

#include <stdbool.h>

typedef struct { char id[16]; long total_kobo; bool paid; } order;

/* Ports: structs of function pointers the adapters fill in. */
typedef struct { void *self; void (*save)(void *self, const order *o); } order_repository;
typedef struct { void *self; bool (*charge)(void *self, const char *customer, long kobo); } payment_gateway;

typedef enum { PLACE_OK, PLACE_INVALID_TOTAL, PLACE_DECLINED } place_result;

place_result place_order(const order_repository *orders, const payment_gateway *payments,
                         const char *id, const char *customer, long kobo, order *out);

#endif
```

```sh
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
```

**Lab:** `labs/hexagonal-architecture/c/` — checked with GCC 16. **A trap found while building this lab:** the adapter header was first called `memory.h` — and the reversed include *compiled*, because glibc ships a `/usr/include/memory.h`. The compiler silently used the system file. Prefix project headers with their folder (`#include "adapters/in_memory.h"`) or give them unmistakable names.

## 7. C++

The domain is a **CMake target that links nothing**. Adapters are a target that links the domain. The domain's include path never contains the adapters' folder, so the reversed include fails to build.

```cmake
cmake_minimum_required(VERSION 3.25)
project(shop LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -Werror)

# The domain links nothing: it only ever sees its own headers.
add_library(domain domain/src/domain.cpp)
target_include_directories(domain PUBLIC domain/include)

# Adapters depend on the domain.
add_library(adapters INTERFACE)
target_include_directories(adapters INTERFACE adapters/include)
target_link_libraries(adapters INTERFACE domain)

enable_testing()
add_executable(test_place_order tests/test_place_order.cpp)
target_link_libraries(test_place_order PRIVATE adapters)
add_test(NAME place_order COMMAND test_place_order)
```

```cpp
#pragma once
#include <string>

namespace domain {

struct Order { std::string id; long total_kobo; bool paid; };

// Ports: abstract classes the domain owns.
struct OrderRepository { virtual ~OrderRepository() = default; virtual void save(const Order&) = 0; };
struct PaymentGateway { virtual ~PaymentGateway() = default; virtual bool charge(const std::string&, long) = 0; };

enum class PlaceResult { Ok, InvalidTotal, Declined };

PlaceResult place_order(OrderRepository& orders, PaymentGateway& payments,
                        const std::string& id, const std::string& customer, long kobo);

}  // namespace domain
```

**Lab:** `labs/hexagonal-architecture/cpp/` — `adapters/memory.hpp: No such file or directory` when the domain tries. Checked with GCC 16 and CMake 4.3.

## 8. C#

The domain is **a project with no references**; adapters reference it. Making the domain reference the adapters is a project cycle, and the build stops with `MSB4006`. This is how .NET "clean architecture" templates are laid out: `Domain`, `Application`, `Infrastructure`, `Api`, each a project.

```csharp
namespace Shop.Domain;

public sealed record Order(string Id, long TotalKobo, bool Paid);

// Ports: interfaces the domain owns.
public interface IOrderRepository { void Save(Order order); }
public interface IPaymentGateway { bool Charge(string customerId, long kobo); }

public sealed class PaymentDeclinedException(string orderId) : Exception($"payment declined for {orderId}");

public static class Ordering
{
    public static Order PlaceOrder(IOrderRepository orders, IPaymentGateway payments, string id, string customerId, long kobo)
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(kobo);
        if (!payments.Charge(customerId, kobo)) throw new PaymentDeclinedException(id);
        var order = new Order(id, kobo, Paid: true);
        orders.Save(order);
        return order;
    }
}
```

**Lab:** `labs/hexagonal-architecture/csharp/` — runs in the .NET 10 SDK container.

## Check your understanding

1. Why does a domain that imports an adapter create a cycle?
2. In which languages does the build refuse it by itself, and what do Python and Java need instead?
3. What's a port in Rust, in C, and in Python?
4. Why did the C lab's reversed include compile at first, and what's the general lesson?
5. Why does putting the domain in its own Go package, crate, project or CMake target matter more than how its files are named?

<details>
<summary>Answers — after your attempt</summary>

1. The adapter already imports the domain to implement its ports. Adding domain → adapter makes each depend on the other.
2. Go (package cycle), Rust (crate cycle), C# (project cycle), C and C++ (include paths, if the build gives the domain only its own). Python needs an import-linter contract; Java needs ArchUnit or Spring Modulith.
3. Rust: a trait. C: a struct of function pointers plus a context pointer. Python: a `Protocol` (or just duck typing).
4. Its adapter header was named `memory.h`, the same as a glibc system header, so the include resolved to `/usr/include/memory.h`. Give project headers folder-prefixed or unique names.
5. Those are the units the build compiles separately, with declared dependencies — so the build itself checks the direction. Naming conventions are only enforced by people.

</details>

## Practice — independent task

**In your second language:** add a driving adapter — an HTTP handler, or a CLI command — that calls `place_order`, plus a second driven adapter for the payment port. Then deliberately reverse one import and confirm your build or check fails.

**Done when:** the use case is untouched, both adapters have tests, and you've seen your toolchain reject the reversed import.

## Before moving on

You can lay out ports and adapters in your language and make the build enforce the dependency rule.

**Recap.** Adapters import the domain, so the reverse is a cycle. Go, Rust, C# and CMake-built C and C++ refuse it when the domain is its own unit of compilation; Python needs import-linter and Java needs ArchUnit. Ports are interfaces, `Protocol`s, traits, abstract classes, or function-pointer structs.

**Next.** Back to the course: [[backend/03-structuring-a-backend/05-modular-monolith-to-services|modular monolith to services]].

## Related
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal and clean architecture]] — the main lesson
- [[concepts/04-best-practices/08b-coupling-and-cohesion-in-other-languages|Coupling and cohesion in other languages]] — which cycles each toolchain refuses
- [[backend/03-structuring-a-backend/02b-organising-by-feature-in-compiled-languages|Organising by feature in compiled languages]]
