# Layers in Other Languages

> **[Beginner→Intermediate]** · A companion to [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers — controllers, services, repositories]], which teaches the idea in TypeScript. The three jobs are the same in every language. What changes is the vocabulary, and above all **how a domain error travels from the service to the HTTP response**.

## Before you start

You can already:

- Say what the controller, service and repository each know about, and why services throw domain errors rather than HTTP errors → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|the main lesson]].
- Read code in at least one language below. Read §1, §2 and your languages.

After this lesson you will be able to:

1. Name the three layers in your framework's own vocabulary.
2. Represent a domain error idiomatically in your language — an exception, an error value, a `Result`, a return code or `std::expected`.
3. Map those errors to status codes in one place, the way your framework expects.

## The kid version

Every restaurant has a waiter, a chef and a pantry, whatever language the staff speak. What differs is how the chef says "we're out of steak". In one kitchen the chef shouts it and the waiter catches it (**exceptions**). In another the chef hands back a slip that says either "here's your dish" or "out of steak" (**a result value**), and the waiter has to read it. In the oldest kitchens there's just a number on the slip — 0 for fine, 2 for "out of stock" (**return codes**).

**Where the analogy stops working.** A waiter can ignore a slip; a shout is hard to miss. In code it's the reverse of what you'd expect: an exception nobody catches crashes the request far from where it started, while some languages *won't compile* until you've handled every kind of slip. §2 compares them.

## 1. The same three layers, different names

| Language / framework | Controller | Service | Repository |
|---|---|---|---|
| TypeScript — NestJS | `@Controller` | `@Injectable` service | repository / Prisma client |
| Python — Django | view (`views.py`) | `services.py` (by convention) | model manager / queryset |
| Python — FastAPI | path operation in an `APIRouter` | service class, injected with `Depends` | repository class |
| Go | handler — a method on a struct | service struct | store struct |
| Java — Spring | `@RestController` | `@Service` | `@Repository` / Spring Data interface |
| Rust — Axum | handler function with extractors | service struct in `State` | repository struct |
| C# — ASP.NET Core | controller or minimal-API endpoint | service class | repository or `DbContext` |
| C++ — Drogon | `HttpController` | plain class | `DbClient` wrapper |
| C | the request-handling function | plain functions | functions over a storage handle |

## 2. Where languages genuinely differ: the domain error

The main lesson's rule — *the service throws a domain error; one place maps it to a status* — holds everywhere. How the error is represented decides how hard it is to forget one:

| Language | Domain error is… | Forgetting to handle one… |
|---|---|---|
| TypeScript, Python, Java, C# | an exception | compiles, and becomes a 500 at runtime |
| Go | an error value: a sentinel (`ErrEmptyOrder`) or a type (`*OutOfStockError`) | compiles; linters like `errcheck` catch an *ignored* error |
| Rust | a variant of an error `enum`, inside `Result` | **doesn't compile** — `match` must cover every variant |
| C | an `enum` return code | compiles; `-Wswitch` warns if a `switch` misses a code |
| C++ | an exception, or a `std::expected<T, E>` (C++23) | with `std::variant` errors and `std::visit`, doesn't compile |

## Terms used in this lesson

1. **Exception**: This is an error that jumps up the call stack until something catches it. Uncaught, it ends the request.
2. **Error value**: This is an error returned as an ordinary value, alongside or instead of the result. Go's `(int, error)` is the standard example.
3. **Sentinel error**: This is a single, named error value compared by identity — `if errors.Is(err, ErrEmptyOrder)`.
4. **`Result`**: In Rust, this is a type holding either `Ok(value)` or `Err(error)`. You can't reach the value without deciding what happens to the error.
5. **`std::expected`**: In C++23, this is the same idea as Rust's `Result`: a value or an error, without throwing.
6. **Exhaustive match**: This is a `match`, `switch` or `visit` the compiler checks covers every possible case.

## 3. Python

Exceptions, like TypeScript. In **FastAPI**, register one handler per domain exception with `@app.exception_handler(OutOfStockError)` and routes stay free of `try`; in **Django REST Framework**, a custom `EXCEPTION_HANDLER` does the same job.

```python
"""orders.py — three layers; domain errors are exceptions, mapped to HTTP in one place."""
from dataclasses import dataclass


class EmptyOrderError(Exception):
    pass


class OutOfStockError(Exception):
    def __init__(self, sku: str):
        super().__init__(f"out of stock: {sku}")
        self.sku = sku


@dataclass
class Item:
    sku: str
    quantity: int


class Repository:
    """The only code that knows how stock and orders are stored."""

    def __init__(self, stock: dict[str, int]):
        self.stock = stock
        self.orders: list[list[Item]] = []

    def stock_of(self, sku: str) -> int:
        return self.stock.get(sku, 0)

    def reserve(self, sku: str, quantity: int) -> None:
        self.stock[sku] -= quantity

    def create(self, items: list[Item]) -> int:
        self.orders.append(items)
        return len(self.orders)


class Service:
    """Business rules. Knows nothing about HTTP."""

    def __init__(self, repo: Repository):
        self.repo = repo

    def place(self, items: list[Item]) -> int:
        if not items:
            raise EmptyOrderError("an order needs at least one item")
        for item in items:
            if self.repo.stock_of(item.sku) < item.quantity:
                raise OutOfStockError(item.sku)
        for item in items:
            self.repo.reserve(item.sku, item.quantity)
        return self.repo.create(items)


def create_order(service: Service, body: dict) -> tuple[int, dict]:
    """The controller: HTTP in, HTTP out. In FastAPI this mapping would be an exception handler."""
    items = [Item(i["sku"], i["quantity"]) for i in body.get("items", [])]
    try:
        return 201, {"id": service.place(items)}
    except EmptyOrderError as e:
        return 400, {"error": str(e)}
    except OutOfStockError as e:
        return 409, {"error": str(e), "sku": e.sku}
```

```python
import unittest

from orders import Item, OutOfStockError, Repository, Service, create_order


class LayerTests(unittest.TestCase):
    def test_service_rule_without_http(self):
        service = Service(Repository({"mug": 1}))
        with self.assertRaises(OutOfStockError):
            service.place([Item("mug", 2)])

    def test_controller_maps_domain_errors_to_status_codes(self):
        stock = {"mug": 1}
        service = Service(Repository(stock))
        self.assertEqual(create_order(service, {"items": []})[0], 400)
        self.assertEqual(create_order(service, {"items": [{"sku": "mug", "quantity": 5}]}),
                         (409, {"error": "out of stock: mug", "sku": "mug"}))
        self.assertEqual(create_order(service, {"items": [{"sku": "mug", "quantity": 1}]}), (201, {"id": 1}))
        self.assertEqual(stock["mug"], 0)


if __name__ == "__main__":
    unittest.main()
```

**Lab:** `labs/layers/typescript/python/` — checked with Python 3.14.

## 4. Go

Errors are **values**, returned next to the result: `(int, error)`. A fixed condition is a sentinel, compared with `errors.Is`; a condition carrying data is a type, extracted with `errors.As`. Both work even when the error has been **wrapped** with context on its way up (`fmt.Errorf("placing order: %w", err)`), which is why you use them instead of `==`.

```go
// Package orders: three layers. Domain errors are values; the handler maps them to HTTP.
package orders

import (
	"errors"
	"fmt"
	"net/http"
)

type Item struct {
	SKU      string
	Quantity int
}

// A sentinel error for a fixed condition, and a type for one that carries data.
var ErrEmptyOrder = errors.New("an order needs at least one item")

type OutOfStockError struct{ SKU string }

func (e *OutOfStockError) Error() string { return fmt.Sprintf("out of stock: %s", e.SKU) }

// Repository: the only code that knows how data is stored.
type Repository struct {
	Stock  map[string]int
	orders [][]Item
}

func (r *Repository) create(items []Item) int {
	r.orders = append(r.orders, items)
	return len(r.orders)
}

// Service: business rules. It returns errors; it never chooses a status code.
type Service struct{ Repo *Repository }

func (s *Service) Place(items []Item) (int, error) {
	if len(items) == 0 {
		return 0, ErrEmptyOrder
	}
	for _, it := range items {
		if s.Repo.Stock[it.SKU] < it.Quantity {
			return 0, &OutOfStockError{SKU: it.SKU}
		}
	}
	for _, it := range items {
		s.Repo.Stock[it.SKU] -= it.Quantity
	}
	return s.Repo.create(items), nil
}

// StatusFor is the one place domain errors become HTTP statuses.
func StatusFor(err error) int {
	var oos *OutOfStockError
	switch {
	case err == nil:
		return http.StatusCreated
	case errors.Is(err, ErrEmptyOrder):
		return http.StatusBadRequest
	case errors.As(err, &oos):
		return http.StatusConflict
	default:
		return http.StatusInternalServerError
	}
}
```

```go
package orders

import (
	"errors"
	"fmt"
	"testing"
)

func TestServiceReturnsTypedErrors(t *testing.T) {
	svc := &Service{Repo: &Repository{Stock: map[string]int{"mug": 1}}}
	_, err := svc.Place([]Item{{"mug", 2}})
	var oos *OutOfStockError
	if !errors.As(err, &oos) || oos.SKU != "mug" {
		t.Fatalf("err = %v", err)
	}
}

func TestStatusMappingSurvivesWrapping(t *testing.T) {
	stock := map[string]int{"mug": 1}
	svc := &Service{Repo: &Repository{Stock: stock}}
	_, err := svc.Place(nil)
	if StatusFor(err) != 400 {
		t.Fatal("empty order should be 400")
	}
	_, err = svc.Place([]Item{{"mug", 5}})
	if StatusFor(fmt.Errorf("placing order: %w", err)) != 409 { // a wrapped error still maps
		t.Fatal("out of stock should be 409")
	}
	id, err := svc.Place([]Item{{"mug", 1}})
	if StatusFor(err) != 201 || id != 1 || stock["mug"] != 0 {
		t.Fatalf("id=%d err=%v stock=%d", id, err, stock["mug"])
	}
}
```

**Lab:** `labs/layers/typescript/go/` — checked with Go 1.26. In a real handler, `StatusFor(err)` sets the status and the error's message becomes the body; unknown errors become a logged 500, as in [[backend/07-practices/01-backend-best-practices|backend best practices]].

## 5. Java (and Spring)

Unchecked exceptions named in the domain's language. In **Spring**, the catch blocks below move into one class, so controllers contain no error handling at all — fragment:

```java
@RestControllerAdvice
class DomainErrors {
    @ExceptionHandler(OutOfStockException.class)
    ProblemDetail outOfStock(OutOfStockException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, e.getMessage());
    }
}
```

```java
package orders;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class Orders {
    public record Item(String sku, int quantity) {}

    // Domain errors: unchecked exceptions named in the business's language.
    public static final class EmptyOrderException extends RuntimeException {
        public EmptyOrderException() { super("an order needs at least one item"); }
    }
    public static final class OutOfStockException extends RuntimeException {
        public final String sku;
        public OutOfStockException(String sku) { super("out of stock: " + sku); this.sku = sku; }
    }

    // Repository: the only code that knows how data is stored.
    public static final class Repository {
        final Map<String, Integer> stock;
        private final List<List<Item>> orders = new ArrayList<>();
        public Repository(Map<String, Integer> stock) { this.stock = stock; }
        int create(List<Item> items) { orders.add(items); return orders.size(); }
    }

    // Service: business rules, no HTTP.
    public static final class Service {
        private final Repository repo;
        public Service(Repository repo) { this.repo = repo; }

        public int place(List<Item> items) {
            if (items.isEmpty()) throw new EmptyOrderException();
            for (Item it : items) {
                if (repo.stock.getOrDefault(it.sku(), 0) < it.quantity()) throw new OutOfStockException(it.sku());
            }
            for (Item it : items) repo.stock.merge(it.sku(), -it.quantity(), Integer::sum);
            return repo.create(items);
        }
    }

    public record Response(int status, String body) {}

    // Controller: in Spring, the catch blocks become one @RestControllerAdvice class.
    public static Response createOrder(Service service, List<Item> items) {
        try {
            return new Response(201, "{\"id\":" + service.place(items) + "}");
        } catch (EmptyOrderException e) {
            return new Response(400, e.getMessage());
        } catch (OutOfStockException e) {
            return new Response(409, e.getMessage());
        }
    }
}
```

**Lab:** `labs/layers/typescript/java/` — checked with Java 21. Prefer unchecked exceptions for domain errors: Java's checked exceptions would force every layer in between to declare them.

## 6. Rust

The error is an **`enum`**, and the service returns `Result<T, PlaceError>`. Mapping with `match` is exhaustive: add a `PlaceError::PaymentDeclined` variant and every `match` that doesn't handle it stops compiling, so a new error can't silently become a 500. In **Axum**, `impl IntoResponse for PlaceError` holds the `match`, and handlers just return `Result<Json<Order>, PlaceError>`.

```rust
//! Three layers. Domain errors are an enum; `match` maps every case to a status,
//! and the compiler complains if a new variant isn't handled.
use std::collections::HashMap;

pub struct Item {
    pub sku: &'static str,
    pub quantity: u32,
}

#[derive(Debug, PartialEq)]
pub enum PlaceError {
    EmptyOrder,
    OutOfStock { sku: String },
}

/// The only code that knows how data is stored.
pub struct Repository {
    pub stock: HashMap<String, u32>,
    orders: usize,
}

impl Repository {
    pub fn new(stock: HashMap<String, u32>) -> Self {
        Repository { stock, orders: 0 }
    }
}

/// Business rules. Returns `Result`; never a status code.
pub fn place(repo: &mut Repository, items: &[Item]) -> Result<usize, PlaceError> {
    if items.is_empty() {
        return Err(PlaceError::EmptyOrder);
    }
    for item in items {
        if repo.stock.get(item.sku).copied().unwrap_or(0) < item.quantity {
            return Err(PlaceError::OutOfStock {
                sku: item.sku.into(),
            });
        }
    }
    for item in items {
        *repo.stock.get_mut(item.sku).unwrap() -= item.quantity;
    }
    repo.orders += 1;
    Ok(repo.orders)
}

/// The controller's mapping. In Axum this is `impl IntoResponse for PlaceError`.
pub fn status_for(result: &Result<usize, PlaceError>) -> u16 {
    match result {
        Ok(_) => 201,
        Err(PlaceError::EmptyOrder) => 400,
        Err(PlaceError::OutOfStock { .. }) => 409,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn errors_map_to_statuses() {
        let mut repo = Repository::new(HashMap::from([("mug".to_string(), 1)]));
        assert_eq!(status_for(&place(&mut repo, &[])), 400);
        let out = place(
            &mut repo,
            &[Item {
                sku: "mug",
                quantity: 5,
            }],
        );
        assert_eq!(out, Err(PlaceError::OutOfStock { sku: "mug".into() }));
        assert_eq!(status_for(&out), 409);
        let ok = place(
            &mut repo,
            &[Item {
                sku: "mug",
                quantity: 1,
            }],
        );
        assert_eq!((status_for(&ok), ok), (201, Ok(1)));
        assert_eq!(repo.stock["mug"], 0);
    }
}
```

**Lab:** `labs/layers/typescript/rust/` — checked with Rust 1.96.

## 7. C

A domain error is an **`enum` return code**; the real result comes back through a pointer argument. Compile with `-Wall`, which includes `-Wswitch`: a `switch` over the enum that misses a code is a warning, and with `-Werror` an error.

```c
/* orders.h — in C, a domain error is a return code; the result travels through a pointer. */
#ifndef ORDERS_H
#define ORDERS_H

typedef enum { PLACE_OK, PLACE_EMPTY_ORDER, PLACE_OUT_OF_STOCK } place_result;

typedef struct { const char *sku; int quantity; } item;

typedef struct {            /* the repository: the only code that knows how stock is stored */
    const char *skus[8];
    int stock[8];
    int count;
    int orders;
} repository;

/* The service. On success *order_id is set; on PLACE_OUT_OF_STOCK, *failed_sku is. */
place_result orders_place(repository *repo, const item *items, int n, int *order_id, const char **failed_sku);

/* The controller's mapping, in one place. */
int status_for(place_result r);

#endif
```

```c
#include "orders.h"

#include <string.h>

static int *stock_slot(repository *repo, const char *sku) {
    for (int i = 0; i < repo->count; i++) {
        if (strcmp(repo->skus[i], sku) == 0) return &repo->stock[i];
    }
    return NULL;
}

place_result orders_place(repository *repo, const item *items, int n, int *order_id, const char **failed_sku) {
    if (n == 0) return PLACE_EMPTY_ORDER;
    for (int i = 0; i < n; i++) {
        int *slot = stock_slot(repo, items[i].sku);
        if (!slot || *slot < items[i].quantity) {
            *failed_sku = items[i].sku;
            return PLACE_OUT_OF_STOCK;
        }
    }
    for (int i = 0; i < n; i++) *stock_slot(repo, items[i].sku) -= items[i].quantity;
    *order_id = ++repo->orders;
    return PLACE_OK;
}

int status_for(place_result r) {
    switch (r) {
        case PLACE_OK: return 201;
        case PLACE_EMPTY_ORDER: return 400;
        case PLACE_OUT_OF_STOCK: return 409;
    }
    return 500; /* unreachable for valid values; -Wswitch warns if a new code is unhandled */
}
```

**Lab:** `labs/layers/typescript/c/` — checked with GCC 16.

## 8. C++

C++ has exceptions, but **C++23's `std::expected`** brings the Rust approach: the service returns a value or an error, and nothing is thrown. With the errors as a `std::variant` and the mapping as a `std::visit`, leaving out an error type is a compile error.

```cpp
#pragma once
// C++23: std::expected<T, E> holds either a value or an error — no exception thrown.
#include <expected>
#include <map>
#include <span>
#include <string>
#include <variant>

namespace orders {

struct Item { std::string sku; int quantity; };

struct EmptyOrder {};
struct OutOfStock { std::string sku; };
using PlaceError = std::variant<EmptyOrder, OutOfStock>;

class Repository {  // the only code that knows how stock is stored
public:
    explicit Repository(std::map<std::string, int> stock) : stock(std::move(stock)) {}
    std::map<std::string, int> stock;
    int create() { return ++orders_; }
private:
    int orders_ = 0;
};

// The service: business rules, returning a value or a domain error.
inline std::expected<int, PlaceError> place(Repository& repo, std::span<const Item> items) {
    if (items.empty()) return std::unexpected(EmptyOrder{});
    for (const auto& item : items) {
        if (repo.stock[item.sku] < item.quantity) return std::unexpected(OutOfStock{item.sku});
    }
    for (const auto& item : items) repo.stock[item.sku] -= item.quantity;
    return repo.create();
}

// The controller's mapping. std::visit with one overload per error type.
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

inline int status_for(const std::expected<int, PlaceError>& result) {
    if (result) return 201;
    return std::visit(overloaded{
        [](const EmptyOrder&) { return 400; },
        [](const OutOfStock&) { return 409; },
    }, result.error());
}

}  // namespace orders
```

**Lab:** `labs/layers/typescript/cpp/` — checked with GCC 16 and `-std=c++23`.

## 9. C#

Exceptions, like Java. The idiomatic mapping is a **`switch` expression** on the exception type. In **ASP.NET Core**, implement `IExceptionHandler`, register it with `AddExceptionHandler`, and return `ProblemDetails`, so controllers and minimal-API endpoints never catch domain errors themselves.

```csharp
// Three layers. Domain errors are exceptions; one switch expression maps them to statuses.
var stock = new Dictionary<string, int> { ["mug"] = 1 };
var service = new OrdersService(new OrdersRepository(stock));

Check(Controller.Create(service, []).Status == 400, "empty order is 400");
Check(Controller.Create(service, [new Item("mug", 5)]) == new Response(409, "out of stock: mug"), "out of stock is 409");
Check(Controller.Create(service, [new Item("mug", 1)]) == new Response(201, "{\"id\":1}"), "success is 201");
Check(stock["mug"] == 0, "stock was reserved");
Console.WriteLine("ok: domain errors mapped to 400, 409 and 201");

static void Check(bool condition, string what)
{
    if (!condition) throw new Exception($"FAIL: {what}");
}

record Item(string Sku, int Quantity);
record Response(int Status, string Body);

sealed class EmptyOrderException() : Exception("an order needs at least one item");
sealed class OutOfStockException(string sku) : Exception($"out of stock: {sku}")
{
    public string Sku { get; } = sku;
}

// Repository: the only code that knows how data is stored.
sealed class OrdersRepository(Dictionary<string, int> stock)
{
    private int _orders;
    public int StockOf(string sku) => stock.GetValueOrDefault(sku);
    public void Reserve(string sku, int quantity) => stock[sku] -= quantity;
    public int Create() => ++_orders;
}

// Service: business rules, no HTTP.
sealed class OrdersService(OrdersRepository repo)
{
    public int Place(IReadOnlyList<Item> items)
    {
        if (items.Count == 0) throw new EmptyOrderException();
        foreach (var item in items)
            if (repo.StockOf(item.Sku) < item.Quantity) throw new OutOfStockException(item.Sku);
        foreach (var item in items) repo.Reserve(item.Sku, item.Quantity);
        return repo.Create();
    }
}

// Controller. In ASP.NET Core the mapping becomes an IExceptionHandler returning ProblemDetails.
static class Controller
{
    public static Response Create(OrdersService service, IReadOnlyList<Item> items)
    {
        try
        {
            return new Response(201, $"{{\"id\":{service.Place(items)}}}");
        }
        catch (Exception e) when (e is EmptyOrderException or OutOfStockException)
        {
            return new Response(e switch
            {
                EmptyOrderException => 400,
                OutOfStockException => 409,
                _ => 500,
            }, e.Message);
        }
    }
}
```

**Lab:** `labs/layers/typescript/csharp/` — runs in the .NET 10 SDK container.

## Check your understanding

1. What's Spring's name for each layer? And ASP.NET Core's?
2. In Go, why use `errors.Is` and `errors.As` instead of `err == ErrEmptyOrder` or a type assertion?
3. You add a `PaymentDeclined` error. In which languages does the compiler make you handle it in the status mapping?
4. Why are unchecked exceptions usually preferred for domain errors in Java?
5. What does `std::expected` give C++ that exceptions don't?

<details>
<summary>Answers — after your attempt</summary>

1. Spring: `@RestController`, `@Service`, `@Repository`. ASP.NET Core: a controller or minimal-API endpoint, a service class, and a repository or `DbContext`.
2. Errors are often wrapped with context on the way up. `errors.Is` and `errors.As` look through the wrapping; `==` and a plain type assertion only see the outermost error.
3. Rust (exhaustive `match`) and C++ when the errors are a `std::variant` handled with `std::visit`. C warns with `-Wswitch` (an error with `-Werror`). Go, Java, C#, Python and TypeScript compile and produce a 500 at runtime.
4. Checked exceptions would have to be declared by every method between the service and the handler, coupling every layer to every domain error.
5. The error is part of the function's return type, so callers can see it and must deal with it, and nothing unwinds the stack — useful where exceptions are disabled or too costly, and it makes the failure path explicit.

</details>

## Practice — independent task

**In the language you'd most like to use after TypeScript:** rebuild the orders example from memory — repository, service, controller mapping — then add a third error, `PaymentDeclined`, mapped to `402`. Note what the compiler did or didn't tell you when you added it.

**Done when:** the three original outcomes and the new one are tested, and you can say whether your language would have caught a missing mapping before runtime.

## Before moving on

You can name the layers in your framework's vocabulary and represent and map domain errors idiomatically in your language.

**Recap.** Same three jobs, different names. Exceptions (TypeScript, Python, Java, C#) are mapped by one handler per framework; Go's error values are matched with `errors.Is` and `errors.As`; Rust's `Result` enums and C++23's `std::expected` with a variant make an unhandled error a compile error; C uses return codes and `-Wswitch`.

**Next.** Back to the course: [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|organising by layer vs by feature]].

## Related
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — the main lesson
- [[backend/07-practices/01-backend-best-practices|Backend best practices]] — the error contract and the central handler
- [[programming-fundamentals/10-errors-and-debugging|Errors and debugging]]
