# SOLID in Other Languages

> **[Intermediate]** · A companion to [[concepts/04-best-practices/05-solid-principles/index|SOLID principles]], which teaches them in JavaScript. The principles were written for languages with classes and inheritance. Here: what happens to them in languages **without inheritance** (Go, Rust, C), where **interfaces are implicit** (Go), and where the compiler offers a rival to open/closed — the **exhaustive match**.

## Before you start

You can already:

- State the five principles and show the smell each fixes → [[concepts/04-best-practices/05-solid-principles/index|the main lesson]].
- Read code in at least one language below. Read §1–2, then your languages.

After this lesson you will be able to:

1. Say which principles your language makes automatic, which it makes impossible to violate, and which still need discipline.
2. Write the main lesson's fee rules two ways in your language — open (a strategy per method) and closed (an enum and an exhaustive match) — and choose between them.
3. Show whether your compiler catches a forgotten case.

## The kid version

A toy box with a lid that only fits certain shapes is **closed**: when a new shape of toy arrives, the box won't take it until you redesign the lid — but you'll never lose a toy you forgot about. An open basket takes anything — easy to add new toys, but nothing tells you when a new toy needs special care.

**Where the analogy stops working.** You can't have both a lid and an open basket in one toy box. In code you choose per decision: open where new *kinds* keep arriving, closed where the kinds are fixed and new *operations* keep arriving.

## 1. What the language decides for you

| Language | Class inheritance? | Interfaces | Exhaustive match? |
|---|---|---|---|
| TypeScript | yes | structural (shape matches) | with a `never` check |
| Python | yes | duck typing; `Protocol` for type checkers | with `assert_never` and mypy |
| Go | **no** — embedding is composition | **implicit**, usually one or two methods | **no** |
| Java | yes | declared | **yes** — sealed interfaces + `switch` (Java 21) |
| Rust | **no** | traits | **yes** — `enum` + `match` |
| C | **no** | function-pointer structs | warning: `-Wswitch-enum` |
| C++ | yes (multiple) | abstract classes; concepts for templates | **yes** — `std::variant` + `std::visit` |
| C# | yes | declared | warning **CS8509** for enums |

Three consequences:

- **Liskov substitution via subclassing can't go wrong in Go, Rust or C** — there are no subclasses. The principle still applies to *interface implementations*: an `io.Reader` that returns data and an error in a way callers don't expect breaks every caller, just as `Square` did.
- **Interface segregation is Go's default culture.** `io.Reader` has one method, `io.Writer` one, and big interfaces are rare because any type with the right methods satisfies them without declaring it. Rust traits tend the same way.
- **Composition over inheritance isn't advice in Go and Rust — it's the only option.**

## 2. Open/closed has a rival: the exhaustive match

The main lesson's fee example is **open for extension**: each payment method is a separate rule, so adding USSD adds a rule and edits nothing. The alternative is **closed**: an enum of methods and one `match` — in languages that check exhaustiveness, adding `Ussd` to the enum makes **every** unhandled `match` a compile error.

That's a real trade-off, sometimes called the **expression problem**:

- **Open** (interfaces, maps of strategies): easy to add a new *kind* — a payment method. Hard to add a new *operation* — "refund fee" means editing every kind.
- **Closed** (enums, sealed types, variants): easy to add a new *operation* — another `match`. Adding a new *kind* means editing every `match` — but the compiler lists every one.

**Choose by which change actually arrives.** New payment methods every month: open. A fixed set of order states that keep gaining behaviour: closed. The labs below write the fee rules both ways and check whether each language catches a forgotten case.

## Terms used in this lesson

1. **Exhaustive match**: This is a `match`, `switch` or `visit` that the compiler checks handles every possible case.
2. **Sealed type**: This is a type whose list of subtypes is fixed and known to the compiler — Java's `sealed interface … permits`, Rust's `enum`, C++'s `std::variant`.
3. **Embedding**: In Go, this is placing one type inside another so its methods are promoted — composition, with no subtype relationship.
4. **Expression problem**: This is the trade-off between making it easy to add new kinds of data and making it easy to add new operations on them.

## 3. Python

Duck typing means any object with the right method fits — interfaces are informal unless you declare a `Protocol` for a type checker. Python itself never checks a `match` for completeness; **mypy with `assert_never`** does, at type-check time.

```python
"""fees.py — open (a dict of functions) and closed (an Enum with an exhaustive match)."""
from enum import Enum
from typing import Callable, assert_never

# Open for extension: a new method is a new entry; no existing rule is edited.
OPEN_RULES: dict[str, Callable[[int], int]] = {
    "card": lambda amount_kobo: amount_kobo * 29 // 1000,
    "transfer": lambda _: 50,
}


class Method(Enum):
    CARD = "card"
    TRANSFER = "transfer"


def fee(method: Method, amount_kobo: int) -> int:
    match method:
        case Method.CARD:
            return amount_kobo * 29 // 1000
        case Method.TRANSFER:
            return 50
        case _:
            assert_never(method)  # a type checker errors here if a member is unhandled
```

```sh
#!/bin/sh
# Python itself won't notice a new member until it runs. mypy, with assert_never, does.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
uv run -q --no-project --with mypy mypy --strict fees.py >/dev/null
echo "ok: mypy is happy with the complete match"
sed 's/^    TRANSFER = "transfer"$/    TRANSFER = "transfer"\n    USSD = "ussd"/' fees.py > "$work/fees.py"
if uv run -q --no-project --with mypy mypy --strict "$work/fees.py" >"$work/err.txt" 2>&1; then echo "FAIL: mypy missed USSD"; exit 1; fi
grep -q 'Argument 1 to "assert_never" has incompatible type "Literal\[Method.USSD\]"' "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: mypy refused the unhandled USSD member"
```

**Lab:** [`concepts/04-best-practices/05-solid-principles/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/05-solid-principles/labs/python) — mypy reports `Argument 1 to "assert_never" has incompatible type "Literal[Method.USSD]"`. Run mypy in CI and this is as good as a compiler check.

## 4. Go

No inheritance, implicit interfaces, and **no enums or exhaustive switch**. Named constants of a custom type are the convention, and a forgotten case compiles, falling into `default`. So Go leans hard toward the **open** design — a map of functions or a small interface. (The `exhaustive` linter adds the check, if you want it.)

```go
// Package fees: Go favours the open design — a map of functions, or small interfaces.
package fees

// Open for extension: a new method is a new entry.
var OpenRules = map[string]func(amountKobo int64) int64{
	"card":     func(a int64) int64 { return a * 29 / 1000 },
	"transfer": func(int64) int64 { return 50 },
}

// Closed: Go has no enums or exhaustive switch — constants of a named type are the convention,
// and a forgotten case compiles. The default branch is the only safety net.
type Method int

const (
	Card Method = iota
	Transfer
)

func Fee(m Method, amountKobo int64) (int64, bool) {
	switch m {
	case Card:
		return amountKobo * 29 / 1000, true
	case Transfer:
		return 50, true
	default:
		return 0, false
	}
}
```

```go
package fees

import "testing"

func TestBothDesignsAgree(t *testing.T) {
	if OpenRules["card"](10_000) != 290 {
		t.Fatal("open card fee")
	}
	if fee, ok := Fee(Card, 10_000); !ok || fee != 290 {
		t.Fatal("closed card fee")
	}
}

// A new constant compiles without touching Fee — it falls into default.
func TestForgottenCaseIsOnlyCaughtAtRuntime(t *testing.T) {
	const Ussd Method = Transfer + 1
	if _, ok := Fee(Ussd, 10_000); ok {
		t.Fatal("expected the unknown method to be rejected at runtime")
	}
}
```

**Lab:** [`concepts/04-best-practices/05-solid-principles/labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/05-solid-principles/labs/go) — checked with Go 1.26. The second test shows the gap: a new constant reaches `default` at runtime, and nothing warned at compile time.

## 5. Java

Classes, inheritance and declared interfaces — SOLID's home language. Java 21 adds the closed option: a **sealed interface** with record implementations, and a `switch` over it that the compiler checks is complete. Both styles are idiomatic now.

```java
package fees;

import java.util.Map;
import java.util.function.LongUnaryOperator;

public final class Fees {
    // Open for extension: a map from method name to rule. A new method is a new entry.
    public static final Map<String, LongUnaryOperator> OPEN_RULES = Map.of(
        "card", amount -> amount * 29 / 1000,
        "transfer", amount -> 50);

    // Closed: a sealed interface and an exhaustive switch (Java 21). A new record that
    // implements Method makes every such switch fail to compile until it handles it.
    public sealed interface Method permits Card, Transfer {}
    public record Card() implements Method {}
    public record Transfer() implements Method {}

    public static long fee(Method method, long amountKobo) {
        return switch (method) {
            case Card c -> amountKobo * 29 / 1000;
            case Transfer t -> 50;
        };
    }

    public static void main(String[] args) {
        assert OPEN_RULES.get("card").applyAsLong(10_000) == 290;
        assert fee(new Card(), 10_000) == 290;
        assert fee(new Transfer(), 10_000) == 50;
        System.out.println("ok: open map and sealed switch agree");
    }
}
```

**Lab:** [`concepts/04-best-practices/05-solid-principles/labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/05-solid-principles/labs/java) — adding a `Ussd` record fails with `the switch expression does not cover all possible input values`. Checked with Java 21.

## 6. Rust

No inheritance; behaviour comes from **traits**, and the closed option is the **`enum`**, Rust's most-used tool. A `match` that misses a variant is error E0004. Open designs use trait objects (`Box<dyn FeeRule>`) — useful when the set of kinds belongs to other crates or plugins.

```rust
//! The same fee rules two ways. Open: a trait, so new methods are new types.
//! Closed: an enum, so a new method is a new variant the compiler makes you handle everywhere.
use std::collections::HashMap;

// ---- Open for extension: a trait object per payment method ----
pub trait FeeRule {
    fn fee(&self, amount_kobo: u64) -> u64;
}
pub struct Card;
impl FeeRule for Card {
    fn fee(&self, amount_kobo: u64) -> u64 {
        amount_kobo * 29 / 1000
    }
}
pub struct Transfer;
impl FeeRule for Transfer {
    fn fee(&self, _: u64) -> u64 {
        50
    }
}

pub fn open_rules() -> HashMap<&'static str, Box<dyn FeeRule>> {
    HashMap::from([
        ("card", Box::new(Card) as Box<dyn FeeRule>),
        ("transfer", Box::new(Transfer)),
    ])
}

// ---- Closed: an enum and one exhaustive match ----
pub enum Method {
    Card,
    Transfer,
}

pub fn fee(method: &Method, amount_kobo: u64) -> u64 {
    match method {
        Method::Card => amount_kobo * 29 / 1000,
        Method::Transfer => 50,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn both_designs_agree() {
        let rules = open_rules();
        assert_eq!(rules["card"].fee(10_000), 290);
        assert_eq!(rules["transfer"].fee(10_000), 50);
        assert_eq!(fee(&Method::Card, 10_000), 290);
        assert_eq!(fee(&Method::Transfer, 10_000), 50);
    }
}
```

```sh
#!/bin/sh
# Add a USSD variant to the closed enum but not to the match: the build must fail.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
sed -i 's/^    Transfer,$/    Transfer,\n    Ussd,/' "$work/src/lib.rs"
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: the missing case compiled"; exit 1; fi
grep -q "error\[E0004\]: non-exhaustive patterns: \`&Method::Ussd\` not covered" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: rustc refused the unhandled Ussd variant (E0004)"
```

**Lab:** [`concepts/04-best-practices/05-solid-principles/labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/05-solid-principles/labs/rust) — `error[E0004]: non-exhaustive patterns`. Checked with Rust 1.96.

## 7. C

No inheritance and no interfaces: the open design is a **table of function pointers**, exactly how C codebases implement plugins and drivers. The closed design is an `enum` and a `switch`; `-Wswitch-enum` (with `-Werror`) makes a missing case a build failure.

```c
/* fees.c — open: a table of function pointers. Closed: an enum and a switch that
 * -Wswitch-enum checks for completeness. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef long (*fee_fn)(long amount_kobo);
static long card_fee(long a) { return a * 29 / 1000; }
static long transfer_fee(long a) { (void)a; return 50; }

/* Open for extension: a new method is a new row. */
static const struct { const char *name; fee_fn fee; } open_rules[] = {
    {"card", card_fee},
    {"transfer", transfer_fee},
};

static long open_fee(const char *name, long amount) {
    for (size_t i = 0; i < sizeof open_rules / sizeof open_rules[0]; i++)
        if (strcmp(open_rules[i].name, name) == 0) return open_rules[i].fee(amount);
    return -1;
}

/* Closed: an enum and one switch. */
typedef enum { METHOD_CARD, METHOD_TRANSFER } method;

static long closed_fee(method m, long amount) {
    switch (m) {
        case METHOD_CARD: return amount * 29 / 1000;
        case METHOD_TRANSFER: return 50;
    }
    return -1;
}

int main(void) {
    assert(open_fee("card", 10000) == 290 && open_fee("transfer", 10000) == 50);
    assert(closed_fee(METHOD_CARD, 10000) == 290 && closed_fee(METHOD_TRANSFER, 10000) == 50);
    puts("ok: function-pointer table and enum switch agree");
    return 0;
}
```

**Lab:** [`concepts/04-best-practices/05-solid-principles/labs/c/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/05-solid-principles/labs/c) — `enumeration value 'METHOD_USSD' not handled in switch`. Checked with GCC 16.

## 8. C++

Both styles are first-class. Open: an abstract base class with `virtual` functions — where Liskov substitution applies exactly as in the main lesson, plus C++'s own trap, **slicing** (copying a derived object into a base-class value loses the derived part). Closed: **`std::variant` with `std::visit`**, where a missing overload doesn't compile.

```cpp
// fees.cpp — open: virtual functions behind an interface. Closed: std::variant + std::visit,
// where a missing overload is a compile error.
#include <cassert>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <variant>

struct FeeRule { virtual ~FeeRule() = default; virtual long fee(long amount) const = 0; };
struct CardRule : FeeRule { long fee(long a) const override { return a * 29 / 1000; } };
struct TransferRule : FeeRule { long fee(long) const override { return 50; } };

struct Card {};
struct Transfer {};
using Method = std::variant<Card, Transfer>;

template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

long fee(const Method& m, long amount) {
    return std::visit(overloaded{
        [&](Card) { return amount * 29 / 1000; },
        [](Transfer) { return 50L; },
    }, m);
}

int main() {
    std::map<std::string, std::unique_ptr<FeeRule>> open;   // open for extension: add an entry
    open["card"] = std::make_unique<CardRule>();
    open["transfer"] = std::make_unique<TransferRule>();
    assert(open["card"]->fee(10000) == 290 && open["transfer"]->fee(10000) == 50);
    assert(fee(Card{}, 10000) == 290 && fee(Transfer{}, 10000) == 50);
    std::cout << "ok: virtual rules and variant visit agree\n";
}
```

**Lab:** [`concepts/04-best-practices/05-solid-principles/labs/cpp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/05-solid-principles/labs/cpp) — the error is long, as template errors are; its key line is `no type named 'type' in 'struct std::invoke_result<…, const Ussd&>'`. Checked with GCC 16.

## 9. C#

Classes, interfaces and inheritance, like Java. The closed option is an `enum` with a **switch expression**: a missing value gives warning **CS8509**, which `TreatWarningsAsErrors` makes an error. C# has no sealed class *hierarchies* that the compiler treats as closed, so for type-based switches it can't check completeness — enums and records with an explicit discard are the practical options.

```csharp
// Open: a dictionary of delegates. Closed: an enum and a switch expression, where the compiler
// warns (CS8509) about an unhandled value — an error here, because warnings are errors.
var openRules = new Dictionary<string, Func<long, long>>
{
    ["card"] = amount => amount * 29 / 1000,
    ["transfer"] = _ => 50,
};

if (openRules["card"](10_000) != 290 || Fee(Method.Card, 10_000) != 290 || Fee(Method.Transfer, 10_000) != 50)
    throw new Exception("FAIL: designs disagree");
Console.WriteLine("ok: delegate dictionary and enum switch agree");

// CS8524 is about integers cast to Method that aren't named values — not what this lab checks.
#pragma warning disable CS8524
static long Fee(Method method, long amountKobo) => method switch
{
    Method.Card => amountKobo * 29 / 1000,
    Method.Transfer => 50,
};
#pragma warning restore CS8524

enum Method { Card, Transfer }
```

**Lab:** [`concepts/04-best-practices/05-solid-principles/labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/05-solid-principles/labs/csharp) — runs in the .NET 10 SDK container; adding `Ussd` gives `error CS8509`.

## Check your understanding

1. Why can't the square/rectangle Liskov violation happen in Go or Rust, and where does Liskov substitution still apply?
2. Why is interface segregation close to automatic in Go?
3. In which languages does adding a variant to a closed set break the build until every match handles it?
4. Your payment provider adds a new method every month. Open or closed? And a fixed set of order statuses that keeps gaining new reports?
5. What is slicing in C++, and which principle does it relate to?

<details>
<summary>Answers — after your attempt</summary>

1. Neither has subclass inheritance, so there's no subclass to override a parent's behaviour. It still applies to interface and trait implementations: any implementation must keep the contract callers rely on.
2. Interfaces are satisfied implicitly, so consumers declare exactly the one or two methods they need, and the standard library models it — `io.Reader`, `io.Writer`.
3. Rust, Java (sealed + switch), C++ (variant + visit), and C and C# when warnings are errors (`-Wswitch-enum`, CS8509). Python with mypy and `assert_never`. Not Go without a linter.
4. New methods monthly: open — adding a kind shouldn't touch existing code. Fixed statuses gaining reports: closed — new operations are easy, and the compiler guards completeness.
5. Copying a derived object into a base-class *value* keeps only the base part, silently dropping the derived behaviour. It's a substitution failure: the object no longer behaves like the one you had. Pass by reference or pointer.

</details>

## Practice — independent task

**In your second language:** take the order lifecycle from [[concepts/03-design-patterns/03-behavioral-patterns/index|behavioural patterns]] — pending, paid, shipped, delivered, cancelled — and write it **closed**: an enum of statuses and an exhaustive match for "which actions are allowed". Then add a `refunded` status and record what the compiler (or type checker) told you.

**Done when:** the lifecycle tests pass, and you can say in one sentence whether your language would have let you ship the new status with a case unhandled.

## Before moving on

You know which SOLID principles your language enforces, which it removes, and when to choose a closed, compiler-checked design over an open one.

**Recap.** Go, Rust and C have no inheritance — composition is the only option, and Liskov applies to interface implementations. Go's tiny implicit interfaces make segregation the default. Open designs make new kinds easy; closed designs make new operations easy and let the compiler find every unhandled case — Rust, Java, C++, and C and C# with warnings as errors.

**Next.** Back to the course: [[concepts/03-design-patterns/03-behavioral-patterns/index|behavioural patterns]] (week 4).

## Related
- [[concepts/04-best-practices/05-solid-principles/index|SOLID principles]] — the main lesson
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/in-other-languages|Layers in other languages]] — exhaustive matching for errors
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/in-other-languages|Dependency injection in other languages]] — the D in SOLID, per language
