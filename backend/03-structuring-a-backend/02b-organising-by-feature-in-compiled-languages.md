# Organising by Feature in Go, Java, Rust, C, C++ and C#

> **[Intermediate]** · A companion to [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|organising by layer vs by feature]]. In JavaScript and Python, feature boundaries need a lint rule. **In these six languages the compiler or the build system enforces them** — as long as you pick the layout that lets it.

## Before you start

You can already:

- Explain the case for organising by feature, the composition root, and boundary enforcement → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|the main lesson]], §1–5.
- Read code in at least one of these languages. You don't need all six — read the sections for the languages you use, plus §1.

After this lesson you will be able to:

1. Name the mechanism each language uses to hide a feature's internals: `internal/` packages, package-private, private modules, opaque types and `static`, `PRIVATE` include directories, and `internal` assemblies.
2. Explain why a by-layer layout switches that mechanism off in each of them.
3. Prove a boundary holds by making a forbidden access fail to compile.

**Study route.** §1 for everyone, then only your languages. The worked examples are the labs; run one, and make its prediction first.

## The kid version

In the main lesson, the "keep out of other features' boxes" rule was a sign on the box — a lint rule that complains if you reach in. In these languages, the box has a **lock built into it**. Put a feature's private parts inside, and the compiler simply can't open it from outside.

**Where the analogy stops working.** The lock only works if things are *inside the same box*. Organise by layer and a feature's parts end up in different boxes — so to let them reach each other, you have to leave every box unlocked. That's §1.

## 1. Why the language changes the argument

Every language here hides things at the level of a **package, module, file, target or assembly**. In the by-feature layout, a feature's controller, service and repository live in the same one of those, so the repository can stay hidden while the service is public.

In the by-layer layout, the service lives in `services/` and the repository in `repositories/` — different packages. For the service to reach the repository, the repository must be public. **And public means public to every feature.** So by-layer doesn't just make files harder to find in these languages; it removes a check the compiler would otherwise do for free.

## Terms used in this lesson

1. **Package**: In Go and Java, this is a named group of source files compiled together — in Go one folder, in Java one namespace like `shop.orders`.
2. **Module**: In Rust, this is a named scope of items (`mod orders`), private to its parent unless marked `pub`.
3. **Translation unit**: In C and C++, this is one `.c` or `.cpp` file after its headers are included — the unit the compiler sees at once.
4. **Target**: In CMake, this is one thing the build produces — a library or an executable — with its own sources, include directories and dependencies.
5. **Assembly**: In .NET, this is the compiled output of one project — a `.dll` or `.exe`. C#'s `internal` means "visible within this assembly".
6. **Opaque type**: This is a type declared in a header but defined only in one source file, so other code can hold a pointer to it but not see inside.

## 2. Go

Go code is organised by **package**, one per folder, and a package exports only names that start with a capital letter. Two consequences decide the layout question.

### By layer — fighting the language

```
shop/
├── cmd/server/main.go
├── handlers/      orders.go  users.go      package handlers
├── services/      orders.go  users.go      package services
└── repositories/  orders.go  users.go      package repositories
```

Every handler has to call into `services`, so every service method must be exported — and so must every repository method, because services live in another package. **Nothing can be private between features**, because the features share packages. The names also stutter: `services.OrdersService`, `repositories.OrdersRepository`. Go's style guide pushes the other way.

### By feature — the Go way, with `internal/` (verified, Go 1.26)

```
shop/
├── go.mod                          module shop
├── cmd/server/
│   ├── main.go                     composition root
│   └── main_test.go
└── internal/
    ├── users/users.go              package users
    └── orders/
        ├── orders.go               package orders — Routes() is its public API
        └── internal/store/store.go private to orders
```

**`internal/` is enforced by the Go compiler.** A package whose path contains `internal/` can only be imported by code rooted at the folder that contains that `internal/`. So `shop/internal/orders/internal/store` is importable from `shop/internal/orders/...` and from nowhere else — not from `users`, not from `main`. The outer `shop/internal/` does the same for the whole module: other Go modules can't import any of it.

```go
// Package store is private to orders: Go only lets code under internal/orders import it.
package store

type Order struct {
	ID     int    `json:"id"`
	UserID string `json:"userId"`
	Kobo   int    `json:"totalKobo"`
}

type Memory struct{ orders []Order }

func (m *Memory) Insert(userID string, kobo int) Order {
	o := Order{ID: len(m.orders) + 1, UserID: userID, Kobo: kobo}
	m.orders = append(m.orders, o)
	return o
}
```

```go
// Package orders is a feature: handler, service and storage together.
package orders

import (
	"encoding/json"
	"errors"
	"net/http"

	"shop/internal/orders/internal/store"
)

// UserChecker is what orders needs from users — declared here, where it's used.
type UserChecker interface{ Exists(id string) bool }

var errUnknownUser = errors.New("unknown user")

type service struct {
	users UserChecker
	store *store.Memory
}

func (s *service) place(userID string, kobo int) (store.Order, error) {
	if !s.users.Exists(userID) {
		return store.Order{}, errUnknownUser
	}
	return s.store.Insert(userID, kobo), nil
}

// Routes is the feature's public API: the composition root mounts it.
func Routes(users UserChecker) http.Handler {
	svc := &service{users: users, store: &store.Memory{}}
	mux := http.NewServeMux()
	mux.HandleFunc("POST /orders", func(w http.ResponseWriter, r *http.Request) {
		var body struct {
			UserID string `json:"userId"`
			Kobo   int    `json:"totalKobo"`
		}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			http.Error(w, "invalid JSON", http.StatusBadRequest)
			return
		}
		order, err := svc.place(body.UserID, body.Kobo)
		if errors.Is(err, errUnknownUser) {
			http.Error(w, err.Error(), http.StatusUnprocessableEntity)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(order)
	})
	return mux
}
```

Notice that `orders` declares the small interface it needs from users, `UserChecker`, in its **own** file. That's idiomatic Go — "accept interfaces, return structs" — and it means `orders` doesn't import `users` at all; the composition root connects them:

```go
// The composition root: the only place that knows every feature.
package main

import (
	"log"
	"net/http"

	"shop/internal/orders"
	"shop/internal/users"
)

func newMux() http.Handler {
	mux := http.NewServeMux()
	mux.Handle("/orders", orders.Routes(users.NewService()))
	return mux
}

func main() {
	log.Fatal(http.ListenAndServe(":8080", newMux()))
}
```

**Proving the boundary.** The lab's check copies the project, adds a file to `users` that imports orders' private store, and expects the build to fail:

```sh
#!/bin/sh
# Prove the boundary is real: copy the project, add a forbidden import, and expect the build to fail.
set -eu
export LC_ALL=C  # plain ASCII compiler messages, whatever the locale
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r . "$work"
cat > "$work/internal/users/sneak.go" <<'GO'
package users

import "shop/internal/orders/internal/store"

var _ = store.Memory{}
GO
if (cd "$work" && go build ./... 2>"$work/err.txt"); then
  echo "FAIL: users imported orders' private store and the build still passed"; exit 1
fi
grep -q "use of internal package shop/internal/orders/internal/store not allowed" "$work/err.txt"
echo "ok: the compiler refused the cross-feature import"
```

It does, with `use of internal package shop/internal/orders/internal/store not allowed`. No lint rule, no configuration — the boundary is part of the language. More on wiring Go services: [[backend/frameworks/go/04-structuring-a-go-service|structuring a Go service]].

---

## 3. Java (and Spring Boot)

Java's unit of organisation is the **package**, and it has a visibility level that most Java developers forget exists: **package-private** — no modifier at all — meaning visible only inside the same package.

### By layer — everything must be public

```
src/main/java/com/shop/
├── controller/   OrdersController.java  UsersController.java
├── service/      OrdersService.java     UsersService.java
├── repository/   OrdersRepository.java  UsersRepository.java
└── ShopApplication.java
```

`OrdersController` in `controller` calls `OrdersService` in `service`, which calls `OrdersRepository` in `repository` — three packages, so all three must be `public`. **And once `OrdersRepository` is public, `UsersService` can use it too.** The by-layer layout throws away the language's own boundary.

### By feature — package-private does the work (verified with plain `javac`, Java 21)

```
src/shop/
├── App.java                     composition root
├── users/UsersService.java      public: the users API
└── orders/
    ├── Order.java               public record
    ├── OrdersService.java       public: the orders API
    └── OrdersRepository.java    package-private: invisible outside shop.orders
```

```java
package shop.orders;

import java.util.ArrayList;
import java.util.List;

// No "public": only code in shop.orders can see this class. That's the boundary.
final class OrdersRepository {
    private final List<Order> orders = new ArrayList<>();

    Order insert(String userId, long totalKobo) {
        Order order = new Order(orders.size() + 1, userId, totalKobo);
        orders.add(order);
        return order;
    }
}
```

```java
package shop.orders;

import shop.users.UsersService;

// Public: the orders feature's API. Its repository stays package-private.
public final class OrdersService {
    private final UsersService users;
    private final OrdersRepository repository = new OrdersRepository();

    public OrdersService(UsersService users) {
        this.users = users;
    }

    public Order place(String userId, long totalKobo) {
        if (!users.exists(userId)) {
            throw new IllegalArgumentException("unknown user: " + userId);
        }
        return repository.insert(userId, totalKobo);
    }
}
```

```java
package shop;

import shop.orders.Order;
import shop.orders.OrdersService;
import shop.users.UsersService;

// The composition root: builds each feature and connects them.
public final class App {
    public static OrdersService wire() {
        return new OrdersService(new UsersService());
    }

    public static void main(String[] args) {
        OrdersService orders = wire();
        Order order = orders.place("u1", 500_000);
        System.out.println(order);
        try {
            orders.place("nobody", 1);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
    }
}
```

**Proving the boundary.** The lab's `check.sh` compiles and runs the app, then adds a class to `shop.users` that tries `new shop.orders.OrdersRepository()`:

```sh
#!/bin/sh
# Compile, run, and prove another feature can't reach orders' package-private repository.
set -eu
export LC_ALL=C  # plain ASCII compiler messages, whatever the locale
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
javac -d "$work/out" $(find src -name '*.java')
output=$(java -cp "$work/out" shop.App) || { echo "the app failed to run"; exit 1; }
expected='Order[id=1, userId=u1, totalKobo=500000]
rejected: unknown user: nobody'
[ "$output" = "$expected" ] || { echo "unexpected output:"; echo "$output"; exit 1; }
echo "ok: the app runs"

cp -r src "$work/src"
cat > "$work/src/shop/users/Sneak.java" <<'JAVA'
package shop.users;

class Sneak {
    Object reach() { return new shop.orders.OrdersRepository(); }
}
JAVA
if javac -d "$work/bad" $(find "$work/src" -name '*.java') 2>"$work/err.txt"; then
  echo "FAIL: users reached orders' repository and it compiled"; exit 1
fi
grep -q "OrdersRepository is not public in shop.orders; cannot be accessed from outside package" "$work/err.txt"
echo "ok: the compiler refused the cross-feature access"
```

`javac` refuses: `OrdersRepository is not public in shop.orders; cannot be accessed from outside package`.

### In Spring Boot

Spring's component scanning finds `@Service` and `@Repository` classes whether they're public or not, so **the same layout works**: one package per feature directly under the application's package, controllers, services and repositories inside it, and only the API marked `public`.

```
src/main/java/com/shop/
├── ShopApplication.java        @SpringBootApplication — scans everything below
├── orders/
│   ├── OrdersController.java   @RestController (package-private is fine)
│   ├── OrdersService.java      public — the API other features may use
│   └── OrdersRepository.java   package-private
└── users/
```

For checks beyond one package — a feature split across sub-packages — **Spring Modulith** treats each direct sub-package of the application package as a module and verifies the dependencies in a test (fragment, not run here):

```java
@Test
void modulesRespectTheirBoundaries() {
    ApplicationModules.of(ShopApplication.class).verify(); // fails on cycles and on access to another module's internals
}
```

Java's module system (`module-info.java`, with `exports` listing the packages others may use) is the strictest option, but it's rarely used in Spring applications. Spring itself: [[backend/frameworks/java/01-spring-boot|Spring Boot]].

---

## 4. Rust

Rust's modules are **private by default**: an item is visible to its own module and its children, and nothing else, unless marked `pub`. So the by-feature boundary costs nothing — it's what happens if you don't type `pub`.

### By layer

```
src/
├── main.rs
├── handlers/      mod.rs  orders.rs  users.rs
├── services/      mod.rs  orders.rs  users.rs
└── repositories/  mod.rs  orders.rs  users.rs
```

`handlers::orders` needs `services::orders`, which needs `repositories::orders`, so all of it ends up `pub` or `pub(crate)` — visible to the whole crate, including every other feature.

### By feature (verified, Rust 1.96, edition 2024)

```
src/
├── lib.rs                 pub mod orders; pub mod users;
├── main.rs                composition root
├── users.rs
└── orders/
    ├── mod.rs             the orders API; declares `mod repository;` without pub
    └── repository.rs      private to orders
```

```rust
// lib.rs — one module per feature. What each one marks `pub` is its public API.
pub mod orders;
pub mod users;
```

```rust
// The orders feature. `repository` is declared without `pub`, so nothing outside
// `orders` can name it — the compiler enforces the boundary.
mod repository;

use crate::users::Users;
pub use repository::Order;
use repository::Repository;

#[derive(Debug, PartialEq)]
pub enum PlaceError {
    UnknownUser,
}

pub struct Orders<'a> {
    users: &'a Users,
    repository: Repository,
}

impl<'a> Orders<'a> {
    pub fn new(users: &'a Users) -> Self {
        Orders {
            users,
            repository: Repository::default(),
        }
    }

    pub fn place(&mut self, user_id: &str, total_kobo: u64) -> Result<Order, PlaceError> {
        if !self.users.exists(user_id) {
            return Err(PlaceError::UnknownUser);
        }
        Ok(self.repository.insert(user_id, total_kobo))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn places_an_order_for_a_known_user() {
        let users = Users::new();
        let mut orders = Orders::new(&users);
        let order = orders.place("u1", 500_000).unwrap();
        assert_eq!(
            order,
            Order {
                id: 1,
                user_id: "u1".into(),
                total_kobo: 500_000
            }
        );
    }

    #[test]
    fn rejects_an_unknown_user() {
        let users = Users::new();
        let mut orders = Orders::new(&users);
        assert_eq!(orders.place("nobody", 1), Err(PlaceError::UnknownUser));
    }
}
```

```rust
// Private to the orders module.
#[derive(Debug, Clone, PartialEq)]
pub struct Order {
    pub id: u32,
    pub user_id: String,
    pub total_kobo: u64,
}

#[derive(Default)]
pub(super) struct Repository {
    orders: Vec<Order>,
}

impl Repository {
    pub(super) fn insert(&mut self, user_id: &str, total_kobo: u64) -> Order {
        let order = Order {
            id: self.orders.len() as u32 + 1,
            user_id: user_id.into(),
            total_kobo,
        };
        self.orders.push(order.clone());
        order
    }
}
```

`pub(super)` means "visible to the parent module" — here, `orders` and nothing above it. `pub use repository::Order` re-exports the one type callers need, so the module stays private while its result type is public.

**Proving the boundary:**

```sh
#!/bin/sh
# Prove the boundary is real: users tries to use orders' private repository module.
set -eu
export LC_ALL=C  # plain ASCII compiler messages, whatever the locale
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
cat >> "$work/src/users.rs" <<'RS'

pub fn sneak() {
    let _ = crate::orders::repository::Order { id: 0, user_id: String::new(), total_kobo: 0 };
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then
  echo "FAIL: users reached orders' private module and it compiled"; exit 1
fi
grep -q "error\[E0603\]: module \`repository\` is private" "$work/err.txt"
echo "ok: the compiler refused the cross-feature access"
```

The build fails with ``error[E0603]: module `repository` is private`` — even though `Order` itself is public, the *path* through the private module isn't.

### With Axum, and with a workspace

Each feature exposes a `Router`, and `main` nests them — fragment:

```rust
let app = Router::new()
    .nest("/orders", orders::router(state.clone()))
    .nest("/users", users::router(state));
```

For a hard boundary between teams, make each feature its own **crate** in a Cargo workspace (`crates/orders`, `crates/users`). A crate can only use another crate listed in its `Cargo.toml`, so the dependency graph is written down and checked by Cargo. More: [[backend/frameworks/rust/01-axum-and-the-tower-stack|Axum and the Tower stack]].

---

## 5. C

C has no modules and no packages. Its tools are older and blunter, and they're enough: **a header per feature as its public API, `static` for file-private functions, and opaque structs**. Large C codebases have always been organised by feature — the Linux kernel is `net/`, `fs/`, `mm/`, `drivers/`, not `functions/` and `structs/`.

```
src/
├── main.c               composition root
├── users/   users.h  users.c
└── orders/  orders.h  orders.c
tests/test_orders.c
```

```c
/* orders.h — the orders feature's public API.
 * `struct orders` is declared but not defined here: callers hold a pointer
 * and can't see or touch its fields. That's an opaque type. */
#ifndef ORDERS_H
#define ORDERS_H

#include <stdbool.h>

typedef struct orders orders;
typedef bool (*user_exists_fn)(const char *user_id); /* what orders needs from users */

orders *orders_new(user_exists_fn user_exists);
void orders_free(orders *o);
/* Returns the new order's id, or 0 if the user is unknown. */
int orders_place(orders *o, const char *user_id, long total_kobo);
long orders_total_kobo(const orders *o);

#endif
```

```c
#include "orders.h"

#include <stdlib.h>

/* The definition lives only here, so only this file can read the fields. */
struct orders {
    user_exists_fn user_exists;
    int count;
    long total_kobo;
};

/* static: a private helper — other files can't call it, even if they declare it. */
static int next_id(orders *o) { return ++o->count; }

orders *orders_new(user_exists_fn user_exists) {
    orders *o = calloc(1, sizeof *o);
    if (o) o->user_exists = user_exists;
    return o;
}

void orders_free(orders *o) { free(o); }

int orders_place(orders *o, const char *user_id, long total_kobo) {
    if (!o->user_exists(user_id)) return 0;
    o->total_kobo += total_kobo;
    return next_id(o);
}

long orders_total_kobo(const orders *o) { return o->total_kobo; }
```

```c
/* main.c — the composition root: it hands orders the users check. */
#include <stdio.h>

#include "orders/orders.h"
#include "users/users.h"

int main(void) {
    orders *o = orders_new(users_exists);
    printf("order %d\n", orders_place(o, "u1", 500000));
    printf("order %d\n", orders_place(o, "nobody", 1));
    orders_free(o);
    return 0;
}
```

Two boundaries, proven by the lab (verified with GCC 16):

```sh
#!/bin/sh
# Build and test, then prove the two C boundaries hold: opaque types and static functions.
set -eu
export LC_ALL=C  # plain ASCII quotes in compiler messages, whatever the locale
CC="${CC:-gcc}"
FLAGS="-std=c17 -Wall -Wextra -Werror -Isrc"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

$CC $FLAGS -o "$work/test" tests/test_orders.c src/orders/orders.c
"$work/test"
$CC $FLAGS -o "$work/shop" src/main.c src/orders/orders.c src/users/users.c
output=$("$work/shop")
[ "$output" = "order 1
order 0" ] || { echo "unexpected output: $output"; exit 1; }
echo "ok: the app runs"

# 1. Another feature reads a field of the opaque struct.
cat > "$work/peek.c" <<'C'
#include "orders/orders.h"
long peek(orders *o) { return o->total_kobo; }
C
if $CC $FLAGS -c "$work/peek.c" -o "$work/peek.o" 2>"$work/err1.txt"; then
  echo "FAIL: read a private field"; exit 1
fi
grep -q "invalid use of incomplete typedef 'orders'" "$work/err1.txt"
echo "ok: the compiler refused to read a private field"

# 2. Another feature calls orders' static helper by declaring it itself.
cat > "$work/sneak.c" <<'C'
#include "orders/orders.h"
int next_id(orders *o);
int sneak(orders *o) { return next_id(o); }
int main(void) { return 0; }
C
if $CC $FLAGS -o "$work/sneak" "$work/sneak.c" src/orders/orders.c 2>"$work/err2.txt"; then
  echo "FAIL: called a static function"; exit 1
fi
grep -q "undefined reference to .next_id." "$work/err2.txt"
echo "ok: the linker refused to call a private function"
```

1. **An opaque type.** Reading `o->total_kobo` outside `orders.c` fails to compile: `invalid use of incomplete typedef 'orders'`. Callers can hold the pointer, and nothing else.
2. **A `static` function.** Declaring `next_id` yourself and calling it gets past the compiler but fails at the **link** step: `undefined reference to 'next_id'`, because `static` gives the function no external name.

Note how `orders` gets "does this user exist?" as a **function pointer** from `main` rather than including `users.h` — the C version of the composition root passing in a dependency. More on C backends: [[backend/frameworks/c/index|C]].

---

## 6. C++

C++ has `namespace`s, which organise names but enforce nothing, and anonymous namespaces, which work like C's `static`. **The real boundary is in the build**: with CMake, each feature is a library target, and a target's include directories are either `PUBLIC` — given to whoever links it — or `PRIVATE` — kept to itself.

```
CMakeLists.txt
app/main.cpp                          composition root
users/include/users/users.hpp         public header
users/src/users.cpp
orders/include/orders/orders.hpp      public header
orders/src/orders.cpp
orders/src/repository.hpp             private header: a PRIVATE include directory
tests/test_orders.cpp
```

```cmake
cmake_minimum_required(VERSION 3.25)
project(shop LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -Werror)

# One library target per feature. PUBLIC include dirs are its API; PRIVATE ones stay inside.
add_library(users users/src/users.cpp)
target_include_directories(users PUBLIC users/include)

add_library(orders orders/src/orders.cpp)
target_include_directories(orders PUBLIC orders/include PRIVATE orders/src)
target_link_libraries(orders PUBLIC users)

# The composition root.
add_executable(shop app/main.cpp)
target_link_libraries(shop PRIVATE orders)

enable_testing()
add_executable(test_orders tests/test_orders.cpp)
target_link_libraries(test_orders PRIVATE orders)
add_test(NAME orders COMMAND test_orders)
```

```cpp
#pragma once
#include <memory>
#include <optional>
#include <string>

#include "users/users.hpp"

namespace shop::orders {

struct Order {
    int id;
    std::string user_id;
    long total_kobo;
};

class Repository;  // defined in a private header; callers never see it

// The orders feature's public API.
class Orders {
public:
    explicit Orders(const users::Users& users);
    ~Orders();
    std::optional<Order> place(const std::string& user_id, long total_kobo);

private:
    const users::Users& users_;
    std::unique_ptr<Repository> repository_;
};

}  // namespace shop::orders
```

```cpp
#include "orders/orders.hpp"

#include "repository.hpp"

namespace shop::orders {

Orders::Orders(const users::Users& users) : users_(users), repository_(std::make_unique<Repository>()) {}
Orders::~Orders() = default;

std::optional<Order> Orders::place(const std::string& user_id, long total_kobo) {
    if (!users_.exists(user_id)) return std::nullopt;
    return repository_->insert(user_id, total_kobo);
}

}  // namespace shop::orders
```

The public header only forward-declares `Repository` and holds it through a `std::unique_ptr` — the **pimpl** idea — so callers never need the private header to compile. That's also why `~Orders()` is defined in the `.cpp`, where `Repository` is a complete type.

**Proving the boundary** (verified with GCC 16 and CMake 4.3):

```sh
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
```

The `sneak` target links `orders` but only receives its `PUBLIC` include directory, so `#include "repository.hpp"` fails: `repository.hpp: No such file or directory`. The build file *is* the dependency rule. More on C++ backends: [[backend/frameworks/cpp/index|C++]].

---

## 7. C# (and ASP.NET Core)

C#'s `internal` keyword means **visible inside this assembly** — the `.dll` one project compiles to. That makes the boundary a project-level decision.

### By layer — the template default

```
Shop.Api/
├── Controllers/   OrdersController.cs  UsersController.cs
├── Services/      OrdersService.cs     UsersService.cs
├── Repositories/  OrdersRepository.cs  UsersRepository.cs
└── Program.cs
```

All in one project, so all in one assembly: `internal` is the same as `public` between features, and nothing stops `UsersService` from using `OrdersRepository`.

### By feature — one project per feature (verified, .NET 10)

```
src/
├── Shop.App/       Program.cs — composition root; references the features
├── Shop.Users/     UsersService.cs (public)
└── Shop.Orders/    OrdersService.cs (public) · OrdersRepository.cs (internal)
```

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Shop.Users/Shop.Users.csproj" />
  </ItemGroup>
</Project>
```

```csharp
namespace Shop.Orders;

public sealed record Order(int Id, string UserId, long TotalKobo);

// internal: visible inside the Shop.Orders assembly only. That's the boundary.
internal sealed class OrdersRepository
{
    private readonly List<Order> _orders = [];

    public Order Insert(string userId, long totalKobo)
    {
        var order = new Order(_orders.Count + 1, userId, totalKobo);
        _orders.Add(order);
        return order;
    }
}
```

```csharp
using Shop.Users;

namespace Shop.Orders;

// public: the orders feature's API. Its repository stays internal.
public sealed class OrdersService(UsersService users)
{
    private readonly OrdersRepository _repository = new();

    public Order? Place(string userId, long totalKobo) =>
        users.Exists(userId) ? _repository.Insert(userId, totalKobo) : null;
}
```

```csharp
// The composition root: builds each feature and connects them.
using Shop.Orders;
using Shop.Users;

var orders = new OrdersService(new UsersService());
Console.WriteLine(orders.Place("u1", 500_000));
Console.WriteLine(orders.Place("nobody", 1)?.ToString() ?? "rejected");
```

The `ProjectReference` is also a dependency rule: `Shop.Users` doesn't reference `Shop.Orders`, so it can't use even orders' *public* types, and a reference cycle between projects is a build error.

**Proving the boundary.** The lab runs inside the .NET SDK container, so you don't need .NET installed — only Podman or Docker:

```sh
#!/bin/sh
# Runs inside the .NET SDK container. Build and run, then prove the app can't reach
# orders' internal repository from another assembly.
set -eu
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r src "$work/src"

output=$(dotnet run --project "$work/src/Shop.App" 2>&1) || { echo "build or run failed:"; echo "$output"; exit 1; }
expected='Order { Id = 1, UserId = u1, TotalKobo = 500000 }
rejected'
[ "$output" = "$expected" ] || { echo "unexpected output:"; echo "$output"; exit 1; }
echo "ok: the app runs"

cat > "$work/src/Shop.App/Sneak.cs" <<'CS'
static class Sneak
{
    public static object Reach() => new Shop.Orders.OrdersRepository();
}
CS
if dotnet build "$work/src/Shop.App" >"$work/err.txt" 2>&1; then
  echo "FAIL: the app reached orders' internal repository and it compiled"; exit 1
fi
grep -q "error CS0122: 'OrdersRepository' is inaccessible due to its protection level" "$work/err.txt"
echo "ok: the compiler refused the cross-feature access"
```

The compiler refuses: `error CS0122: 'OrdersRepository' is inaccessible due to its protection level`.

**Tests that need internals** add `<InternalsVisibleTo Include="Shop.Orders.Tests" />` to the feature's project file — a deliberate, named exception rather than making things public. In ASP.NET Core, each feature project can expose a `MapOrdersEndpoints(this IEndpointRouteBuilder app)` extension method and an `AddOrders(this IServiceCollection services)` registration, and `Program.cs` calls one of each per feature — the composition root. If one project per feature is too heavy, a single project with **feature folders** plus an architecture-test library (NetArchTest or ArchUnitNET) gets the checks back as tests. More: [[backend/frameworks/csharp/index|C#]].


## Check your understanding

1. In Go, which packages may import `shop/internal/orders/internal/store`?
2. A Spring developer says "package-private doesn't work with Spring". Is that right?
3. In Rust, `Order` is `pub`, but `crate::orders::repository::Order` still fails from `users`. Why?
4. In C, which boundary is checked by the compiler, and which by the linker?
5. Why does a CMake `PRIVATE` include directory stop another target including a header, even though that target links the library?
6. In a single .NET project, does `internal` separate one feature from another? What does?

<details>
<summary>Answers — after your attempt</summary>

1. Only packages rooted at `shop/internal/orders` — the folder containing that `internal/`. Not `users`, not `main`.
2. No. Spring's component scanning finds package-private `@Service`, `@Repository` and `@RestController` classes. Only the classes other features genuinely use need to be `public`.
3. Privacy applies to the *path*. The module `repository` is private to `orders`, so no path through it is valid outside `orders`, even to a public item. `orders` re-exports `Order` so there's a public path to it.
4. The compiler checks the opaque type — reading a field of an incomplete type fails at compile time. The linker checks `static` — the call compiles, but there's no external symbol to link to.
5. `PRIVATE` usage requirements apply only to the target itself; only `PUBLIC` (and `INTERFACE`) ones are passed on to targets that link it. The other target never gets that directory on its include path.
6. No — `internal` is per assembly, and one project is one assembly. One project per feature makes `internal` a feature boundary; inside one project you'd need an architecture test library instead.

</details>

## Practice — independent task

**Prove a boundary in your own language.** Pick the language you'd most like to use professionally after TypeScript.

1. Rebuild the shop from that language's lab — users, orders, a composition root — from memory, without opening the lab.
2. Add a third feature, `payments`, that orders calls through its public API.
3. Write a check script, like the labs', that adds a forbidden access from `payments` into orders' internals and expects the build to fail with a specific message.

**Done when:** the app runs, the check script passes, and you can explain — without notes — which language mechanism enforces the boundary and why a by-layer layout would have disabled it.

## Before moving on

You can name each language's hiding mechanism, explain why by-layer switches it off, and prove a boundary by making a forbidden access fail to build.

**Recap.** Go: `internal/`. Java: package-private, and Spring Modulith for checks across sub-packages. Rust: private modules, and workspace crates for hard boundaries. C: opaque types and `static`. C++: one CMake target per feature with `PRIVATE` include directories. C#: `internal` with one project per feature. In all six, by feature keeps the boundary; by layer forces everything public.

**Next.** Back to the course: [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|dependency injection and wiring]].

## Related
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|Organising by layer vs by feature]] — the main lesson
- [[backend/frameworks/go/04-structuring-a-go-service|Structuring a Go service]] · [[backend/frameworks/java/01-spring-boot|Spring Boot]] · [[backend/frameworks/rust/01-axum-and-the-tower-stack|Axum]] · [[backend/frameworks/c/index|C]] · [[backend/frameworks/cpp/index|C++]] · [[backend/frameworks/csharp/index|C#]]
