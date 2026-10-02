# Structural Patterns in Other Languages

> **[Intermediate]** · A companion to [[concepts/03-design-patterns/02-structural-patterns|structural patterns]], which teaches adapter, decorator, proxy and facade in TypeScript with a retry–cache–log stack. Here: the same stack in seven languages — and the features that make these patterns a one-liner (Python's `@decorator`, Java's dynamic proxies) or **required** (Rust's orphan rule forces an adapter).

## Before you start

You can already:

- Explain composition over inheritance, the four structural patterns, and why wrapper order changes behaviour → [[concepts/03-design-patterns/02-structural-patterns|the main lesson]].
- Read code in at least one language below. Read §1 and your languages.

After this lesson you will be able to:

1. Build the retry–cache–log stack idiomatically in your language.
2. Say which structural patterns your language has as syntax or standard-library features.
3. Explain why Rust sometimes *requires* an adapter.

## The kid version

Wrapping a present is the same idea everywhere — paper, then a ribbon, then a card. But some shops have a wrapping counter that does it in one go (**language features** like Python's `@` or Java's proxies), and in others you do every fold yourself (**hand-written wrapper classes**). Same present, same layers.

**Where the analogy stops working.** A wrapped present doesn't care about the order you add the ribbon and the card. A stack of code wrappers does — the main lesson's cache-outside-retry and retry-outside-cache behave differently in every language here.

## 1. What each language gives you

| Language | Decorator | Proxy | Adapter |
|---|---|---|---|
| TypeScript | wrapper classes; TS decorators (`@`) for classes and methods | `Proxy` object | wrapper class |
| Python | **`@decorator` syntax** — functions wrapping functions | `__getattr__` forwarding; `functools.cache` is a caching proxy | wrapper class |
| Go | **middleware**: `func(RateSource) RateSource`, as in `net/http` | wrapper struct | often unnecessary — interfaces are implicit |
| Java | wrapper classes or records | **`java.lang.reflect.Proxy`** — built in; Spring AOP uses it | wrapper class |
| Rust | generic wrapper structs, as in Tower's `Layer` | wrapper; `Deref` for transparent access | **newtype — required by the orphan rule** |
| C | a struct with a function pointer and a pointer to the inner one | the same | the same |
| C++ | class templates, constrained by concepts | smart pointers are proxies | wrapper class |
| C# | wrapper classes; DI containers can register decorators | `DispatchProxy` | wrapper class |

**Two things that aren't what they look like:** Java annotations (`@Cacheable`) and C# attributes are not decorators — they're metadata, and a framework *uses* them to build a proxy. And TypeScript's `@` decorators are closer to Python's: they really do wrap.

## Terms used in this lesson

1. **Middleware**: This is a decorator whose type is "takes a handler, returns a handler" — Go's `net/http`, Express and ASP.NET Core all build request pipelines from it.
2. **Dynamic proxy**: This is a class generated at runtime that implements an interface and sends every method call through one handler function.
3. **Orphan rule**: In Rust, this is the rule that you may only implement a trait for a type if your crate defines the trait or the type.
4. **Newtype**: In Rust, this is a struct with a single field (`struct FxAdapter(FxClient)`), used to give an existing type a new identity — often so you can implement a trait for it.
5. **Concept**: In C++20, this is a named requirement on a template parameter, such as "has a `rate` method returning `long`".

## 2. Python

Python's **decorator syntax** is the decorator pattern for functions: `@retrying(3)` above a function replaces it with a wrapped version. Stacking decorators stacks wrappers, read bottom-up — the one nearest the function wraps first. And the standard library's `functools.cache` is a ready-made caching proxy.

```python
"""rates.py — decorators as Python decorators: functions that wrap functions."""
import functools


class FlakyApi:
    """Stands in for a slow, flaky HTTP API: fails its first `failures` calls."""

    def __init__(self, failures: int):
        self.calls = 0
        self.failures = failures

    def rate(self, base: str, quote: str) -> int:
        self.calls += 1
        if self.calls <= self.failures:
            raise ConnectionError("503 from rates API")
        return 2000 if (base, quote) == ("GBP", "NGN") else 1


def retrying(attempts: int):
    """A decorator factory: @retrying(3) adds retries to any function."""
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args):
            for attempt in range(attempts):
                try:
                    return fn(*args)
                except ConnectionError:
                    if attempt == attempts - 1:
                        raise
        return wrapper
    return decorate


def logged(log: list):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args):
            value = fn(*args)
            log.append(f"{'->'.join(args)} = {value}")
            return value
        return wrapper
    return decorate


def build(api: FlakyApi, log: list):
    """Stack them: log(cache(retry(api))). functools.cache is a ready-made caching proxy."""
    @logged(log)
    @functools.cache
    @retrying(3)
    def rate(base: str, quote: str) -> int:
        return api.rate(base, quote)
    return rate
```

**Lab:** `labs/structural-patterns/typescript/python/` — the API is called three times (two failures, one success) and the second call comes from the cache. Checked with Python 3.14. `functools.wraps` keeps the original function's name and docstring on the wrapper — leave it out and debugging gets confusing.

## 3. Go

Go's idiom is **middleware**: a function that takes the interface and returns the interface, exactly how `net/http` handlers are wrapped. `RateFunc` is an adapter from a plain function to the interface — the same trick as `http.HandlerFunc`. `Chain` applies them outermost-first, so the stack reads top to bottom.

```go
// Package rates: decorators as middleware — a function from RateSource to RateSource,
// the same shape as net/http middleware.
package rates

import (
	"errors"
	"fmt"
	"sync"
)

type RateSource interface {
	Rate(base, quote string) (int, error)
}

// RateFunc adapts a plain function to the interface, like http.HandlerFunc.
type RateFunc func(base, quote string) (int, error)

func (f RateFunc) Rate(base, quote string) (int, error) { return f(base, quote) }

type Middleware func(RateSource) RateSource

type FlakyAPI struct{ Calls, Failures int }

func (a *FlakyAPI) Rate(base, quote string) (int, error) {
	a.Calls++
	if a.Calls <= a.Failures {
		return 0, errors.New("503 from rates API")
	}
	if base == "GBP" && quote == "NGN" {
		return 2000, nil
	}
	return 1, nil
}

func Retrying(attempts int) Middleware {
	return func(next RateSource) RateSource {
		return RateFunc(func(base, quote string) (int, error) {
			var err error
			for range attempts {
				var v int
				if v, err = next.Rate(base, quote); err == nil {
					return v, nil
				}
			}
			return 0, err
		})
	}
}

func Caching() Middleware {
	return func(next RateSource) RateSource {
		var mu sync.Mutex
		cache := map[string]int{}
		return RateFunc(func(base, quote string) (int, error) {
			key := base + "->" + quote
			mu.Lock()
			v, ok := cache[key]
			mu.Unlock()
			if ok {
				return v, nil
			}
			v, err := next.Rate(base, quote)
			if err == nil {
				mu.Lock()
				cache[key] = v
				mu.Unlock()
			}
			return v, err
		})
	}
}

func Logging(log *[]string) Middleware {
	return func(next RateSource) RateSource {
		return RateFunc(func(base, quote string) (int, error) {
			v, err := next.Rate(base, quote)
			*log = append(*log, fmt.Sprintf("%s->%s = %d", base, quote, v))
			return v, err
		})
	}
}

// Chain applies middleware outermost-first: Chain(src, a, b) is a(b(src)).
func Chain(src RateSource, mws ...Middleware) RateSource {
	for i := len(mws) - 1; i >= 0; i-- {
		src = mws[i](src)
	}
	return src
}
```

**Lab:** `labs/structural-patterns/typescript/go/` — checked with Go 1.26. Go needs fewer adapters than most languages: a third-party type that already has a method `Rate(string, string) (int, error)` satisfies `RateSource` with no wrapper at all.

## 4. Java

Decorators are classes (here, records) implementing the interface. Java adds a **dynamic proxy** in the standard library: `Proxy.newProxyInstance` builds an implementation of any interface at runtime and routes every call through one handler — the logging wrapper below works for any interface, not just this one. That's how Spring makes `@Transactional` and `@Cacheable` work on your beans.

```java
package rates;

import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public final class Rates {
    public interface RateSource { long rate(String base, String quote); }

    public static final class FlakyApi implements RateSource {
        public int calls;
        private final int failures;
        public FlakyApi(int failures) { this.failures = failures; }
        public long rate(String base, String quote) {
            calls++;
            if (calls <= failures) throw new IllegalStateException("503 from rates API");
            return base.equals("GBP") && quote.equals("NGN") ? 2000 : 1;
        }
    }

    // Decorators: classes that implement the interface and wrap another implementation.
    public record Retrying(RateSource inner, int attempts) implements RateSource {
        public long rate(String base, String quote) {
            RuntimeException last = null;
            for (int i = 0; i < attempts; i++) {
                try { return inner.rate(base, quote); } catch (RuntimeException e) { last = e; }
            }
            throw last;
        }
    }

    public record Caching(RateSource inner, Map<String, Long> cache) implements RateSource {
        public Caching(RateSource inner) { this(inner, new HashMap<>()); }
        public long rate(String base, String quote) {
            return cache.computeIfAbsent(base + "->" + quote, k -> inner.rate(base, quote));
        }
    }

    // A dynamic proxy: the JDK builds a class implementing any interface at runtime and sends
    // every call through one handler. Spring AOP's @Transactional and @Cacheable work this way.
    public static RateSource logging(RateSource inner, List<String> log) {
        return (RateSource) Proxy.newProxyInstance(
            RateSource.class.getClassLoader(),
            new Class<?>[] {RateSource.class},
            (proxy, method, args) -> {
                Object result = method.invoke(inner, args);
                log.add(args[0] + "->" + args[1] + " = " + result);
                return result;
            });
    }
}
```

**Lab:** `labs/structural-patterns/typescript/java/` — checked with Java 21. One consequence of proxy-based AOP worth knowing: a bean calling *its own* `@Transactional` method bypasses the proxy, so the annotation does nothing.

## 5. Rust

Decorators are **generic wrapper structs**: `Caching<Retrying<FlakyApi>>` is a single concrete type, so the compiler can inline the whole stack — wrappers cost nothing at runtime. This is the model behind Tower, which Axum uses for middleware → [[backend/frameworks/rust/01-axum-and-the-tower-stack|Axum and Tower]].

**Rust also makes adapters compulsory in one situation.** The orphan rule forbids implementing a trait you didn't define for a type you didn't define, so two crates can't both supply conflicting implementations. To make a third-party client implement your trait, you wrap it in a **newtype** — which is the adapter pattern.

```rust
//! Decorators as generic wrapper structs: `Caching<Retrying<FlakyApi>>` is one concrete type,
//! so the compiler can inline the whole stack.
use std::cell::{Cell, RefCell};
use std::collections::HashMap;

pub trait RateSource {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String>;
}

pub struct FlakyApi {
    pub calls: Cell<u32>,
    pub failures: u32,
}
impl RateSource for FlakyApi {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        self.calls.set(self.calls.get() + 1);
        if self.calls.get() <= self.failures {
            return Err("503 from rates API".into());
        }
        Ok(if (base, quote) == ("GBP", "NGN") {
            2000
        } else {
            1
        })
    }
}

pub struct Retrying<S> {
    pub inner: S,
    pub attempts: u32,
}
impl<S: RateSource> RateSource for Retrying<S> {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        let mut last = Err("no attempts".to_string());
        for _ in 0..self.attempts {
            last = self.inner.rate(base, quote);
            if last.is_ok() {
                break;
            }
        }
        last
    }
}

pub struct Caching<S> {
    pub inner: S,
    cache: RefCell<HashMap<String, u64>>,
}
impl<S> Caching<S> {
    pub fn new(inner: S) -> Self {
        Caching {
            inner,
            cache: RefCell::default(),
        }
    }
}
impl<S: RateSource> RateSource for Caching<S> {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        let key = format!("{base}->{quote}");
        if let Some(v) = self.cache.borrow().get(&key) {
            return Ok(*v);
        }
        let v = self.inner.rate(base, quote)?;
        self.cache.borrow_mut().insert(key, v);
        Ok(v)
    }
}

// Adapter, forced by the orphan rule: you may not implement a trait you didn't define for a
// type you didn't define. To make a third-party client a RateSource, wrap it in your own type.
pub mod third_party {
    pub struct FxClient;
    impl FxClient {
        pub fn quote(&self, pair: (&str, &str)) -> f64 {
            if pair.0 == "USD" { 1500.0 } else { 1.0 }
        }
    }
}
pub struct FxAdapter(pub third_party::FxClient); // a "newtype"
impl RateSource for FxAdapter {
    fn rate(&self, base: &str, quote: &str) -> Result<u64, String> {
        Ok(self.0.quote((base, quote)) as u64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn retry_inside_cache() {
        let stack = Caching::new(Retrying {
            inner: FlakyApi {
                calls: Cell::new(0),
                failures: 2,
            },
            attempts: 3,
        });
        assert_eq!(stack.rate("GBP", "NGN"), Ok(2000));
        assert_eq!(stack.rate("GBP", "NGN"), Ok(2000));
        assert_eq!(stack.inner.inner.calls.get(), 3);
    }

    #[test]
    fn adapter_fits_the_same_stack() {
        assert_eq!(
            Caching::new(FxAdapter(third_party::FxClient)).rate("USD", "NGN"),
            Ok(1500)
        );
    }
}
```

```sh
#!/bin/sh
# The orphan rule: implementing a foreign trait (std's Display) for a foreign type (Vec) is refused.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
cat >> "$work/src/lib.rs" <<'RS'

impl std::fmt::Display for Vec<u64> {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result { write!(f, "{}", self.len()) }
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: compiled"; exit 1; fi
grep -q "error\[E0117\]: only traits defined in the current crate can be implemented for types defined outside of the crate" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: rustc applied the orphan rule (E0117) — wrap the type in a newtype instead"
```

**Lab:** `labs/structural-patterns/typescript/rust/` — `error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate`. Checked with Rust 1.96. Note `Cell` and `RefCell`: the API counts calls and the cache stores results through `&self`, so they need interior mutability.

## 6. C

The decorator is a struct holding a function pointer, a pointer to the source it wraps, and its own state. Every wrapper has the same signature, so they stack — this is how C libraries layer I/O streams and how many drivers are built.

```c
/* rates.c — decorators in C: a struct holding a function pointer and a pointer to the
 * thing it wraps, all sharing one signature. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct rate_source rate_source;
struct rate_source {
    int (*rate)(const rate_source *self, const char *base, const char *quote, long *out); /* 0 = ok */
    const rate_source *inner;   /* what this one wraps, if anything */
    void *state;
};

/* The flaky API: fails its first `failures` calls. */
typedef struct { int calls, failures; } flaky_state;
static int flaky_rate(const rate_source *self, const char *base, const char *quote, long *out) {
    flaky_state *s = self->state;
    if (++s->calls <= s->failures) return -1;
    *out = (strcmp(base, "GBP") == 0 && strcmp(quote, "NGN") == 0) ? 2000 : 1;
    return 0;
}

/* Decorator: retries. */
static int retry_rate(const rate_source *self, const char *base, const char *quote, long *out) {
    int attempts = *(const int *)self->state;
    for (int i = 0; i < attempts; i++)
        if (self->inner->rate(self->inner, base, quote, out) == 0) return 0;
    return -1;
}

/* Proxy: a one-entry cache. */
typedef struct { int filled; char key[16]; long value; } cache_state;
static int cache_rate(const rate_source *self, const char *base, const char *quote, long *out) {
    cache_state *c = self->state;
    char key[16];
    snprintf(key, sizeof key, "%s%s", base, quote);
    if (c->filled && strcmp(c->key, key) == 0) { *out = c->value; return 0; }
    if (self->inner->rate(self->inner, base, quote, out) != 0) return -1;
    c->filled = 1; snprintf(c->key, sizeof c->key, "%s", key); c->value = *out;
    return 0;
}

int main(void) {
    flaky_state fs = {.failures = 2};
    int attempts = 3;
    cache_state cs = {0};
    rate_source api = {flaky_rate, NULL, &fs};
    rate_source retry = {retry_rate, &api, &attempts};
    rate_source cached = {cache_rate, &retry, &cs};   /* cache(retry(api)) */

    long v = 0;
    assert(cached.rate(&cached, "GBP", "NGN", &v) == 0 && v == 2000);
    assert(cached.rate(&cached, "GBP", "NGN", &v) == 0 && v == 2000);
    assert(fs.calls == 3);
    puts("ok: function-pointer decorators: two failures, then cached");
    return 0;
}
```

**Lab:** `labs/structural-patterns/typescript/c/` — checked with GCC 16.

## 7. C++

Class templates make each wrapper generic over what it wraps, and a C++20 **concept** states the requirement — "has a `rate` taking two strings and returning `long`" — so a wrong type gives a readable error instead of a page of template noise. Like Rust's version, the stack is one concrete type with no runtime indirection. (For runtime choice of wrappers, use an abstract base class instead.)

```cpp
// rates.cpp — decorators as class templates over any type with a matching rate() (a C++20
// concept), so the whole stack is one concrete type the compiler can inline.
#include <cassert>
#include <concepts>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>

template <class T>
concept RateSource = requires(T& t, const std::string& s) { { t.rate(s, s) } -> std::same_as<long>; };

struct FlakyApi {
    int calls = 0, failures = 0;
    long rate(const std::string& base, const std::string& quote) {
        if (++calls <= failures) throw std::runtime_error("503 from rates API");
        return base == "GBP" && quote == "NGN" ? 2000 : 1;
    }
};

template <RateSource Inner>
struct Retrying {
    Inner& inner;
    int attempts;
    long rate(const std::string& base, const std::string& quote) {
        for (int i = 1;; ++i) {
            try { return inner.rate(base, quote); }
            catch (const std::runtime_error&) { if (i == attempts) throw; }
        }
    }
};

template <RateSource Inner>
struct Caching {
    Inner& inner;
    std::map<std::string, long> cache;
    long rate(const std::string& base, const std::string& quote) {
        auto key = base + "->" + quote;
        if (auto hit = cache.find(key); hit != cache.end()) return hit->second;
        return cache[key] = inner.rate(base, quote);
    }
};

int main() {
    FlakyApi api{.failures = 2};
    Retrying<FlakyApi> retry{api, 3};
    Caching<Retrying<FlakyApi>> cached{retry, {}};
    assert(cached.rate("GBP", "NGN") == 2000);
    assert(cached.rate("GBP", "NGN") == 2000);
    assert(api.calls == 3);

    FlakyApi worse{.failures = 5};
    Retrying<FlakyApi> gives_up{worse, 3};
    bool threw = false;
    try { gives_up.rate("GBP", "NGN"); } catch (const std::runtime_error&) { threw = true; }
    assert(threw);
    std::cout << "ok: template decorators constrained by a concept\n";
}
```

**Lab:** `labs/structural-patterns/typescript/cpp/` — checked with GCC 16 and `-std=c++20`. `std::unique_ptr` and `std::shared_ptr` are the C++ proxies you use every day: they control access to the object they own.

## 8. C#

Decorators are classes implementing the interface, composed by hand as below — or by the DI container, where the Scrutor package's `services.Decorate<IRateSource, Caching>()` wraps whatever is registered. `DispatchProxy` is .NET's version of Java's dynamic proxy, and ASP.NET Core's request pipeline (`app.Use(...)`) is middleware, like Go's.

```csharp
// Decorators as classes implementing the same interface, composed by hand — or by the DI
// container (the Scrutor package's services.Decorate<IRateSource, Caching>() does this).
var api = new FlakyApi(failures: 2);
var log = new List<string>();
IRateSource rates = new Logging(new Caching(new Retrying(api, attempts: 3)), log);

Check(rates.Rate("GBP", "NGN") == 2000 && rates.Rate("GBP", "NGN") == 2000, "rates");
Check(api.Calls == 3, "two failures, one success, then cached");
Check(log.SequenceEqual(["GBP->NGN = 2000", "GBP->NGN = 2000"]), "logging is outermost");
Console.WriteLine("ok: interface decorators");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

interface IRateSource { long Rate(string baseCurrency, string quote); }

sealed class FlakyApi(int failures) : IRateSource
{
    public int Calls { get; private set; }
    public long Rate(string baseCurrency, string quote)
    {
        if (++Calls <= failures) throw new HttpRequestException("503 from rates API");
        return (baseCurrency, quote) == ("GBP", "NGN") ? 2000 : 1;
    }
}

sealed class Retrying(IRateSource inner, int attempts) : IRateSource
{
    public long Rate(string b, string q)
    {
        for (var i = 1; ; i++)
        {
            try { return inner.Rate(b, q); }
            catch (HttpRequestException) when (i < attempts) { }
        }
    }
}

sealed class Caching(IRateSource inner) : IRateSource
{
    private readonly Dictionary<string, long> _cache = [];
    public long Rate(string b, string q) =>
        _cache.TryGetValue($"{b}->{q}", out var v) ? v : _cache[$"{b}->{q}"] = inner.Rate(b, q);
}

sealed class Logging(IRateSource inner, List<string> log) : IRateSource
{
    public long Rate(string b, string q)
    {
        var v = inner.Rate(b, q);
        log.Add($"{b}->{q} = {v}");
        return v;
    }
}
```

**Lab:** `labs/structural-patterns/typescript/csharp/` — runs in the .NET 10 SDK container.

## Check your understanding

1. In Python, with `@logged` above `@cache` above `@retrying(3)`, which wrapper runs first when the function is called?
2. What does Go's `RateFunc` adapt, and which standard-library type uses the same trick?
3. How does Spring make `@Cacheable` work, and why does a bean calling its own annotated method skip it?
4. What does Rust's orphan rule forbid, and why does that make the adapter pattern compulsory?
5. Why do the Rust and C++ stacks cost nothing at runtime, while the Java and C# ones involve a virtual call per layer?

<details>
<summary>Answers — after your attempt</summary>

1. `logged` — the outermost decorator. Decorators apply bottom-up when defined, so the top one is the outer wrapper and runs first on each call.
2. A plain function to the `RateSource` interface. `http.HandlerFunc` adapts a function to `http.Handler` the same way.
3. It wraps the bean in a proxy, and the proxy checks the cache before calling the real method. A call from inside the bean to itself goes straight to `this`, not through the proxy.
4. Implementing a trait you didn't define for a type you didn't define. To make a foreign type implement a foreign trait — or your trait for a type with conflicting rules — you wrap it in your own newtype and implement it there.
5. They're generic: each wrapper's type includes the type it wraps, so the compiler knows the exact method at every layer and can inline it. Interface-based wrappers call through a vtable, decided at runtime.

</details>

## Practice — independent task

**In your second language:** add a timeout wrapper to the lab's stack, then show — with a test — that putting it inside the retry (each attempt times out) behaves differently from putting it outside (the whole retry loop times out).

**Done when:** both orderings are tested, and you can explain the difference in one sentence.

## Before moving on

You can build the wrapper stack idiomatically in your language and say which structural patterns it gives you for free.

**Recap.** Python has `@decorator` and `functools.cache`; Go uses middleware functions; Java and C# have runtime proxies behind their frameworks' annotations; Rust's generic wrappers and C++'s templates cost nothing at runtime; Rust's orphan rule makes adapters compulsory; C builds it all from function pointers.

**Next.** Back to the course: [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal architecture]] (week 5).

## Related
- [[concepts/03-design-patterns/02-structural-patterns|Structural patterns]] — the main lesson
- [[backend/frameworks/go/02-middleware-as-composition|Go middleware as composition]]
- [[backend/frameworks/rust/01-axum-and-the-tower-stack|Axum and the Tower stack]]
