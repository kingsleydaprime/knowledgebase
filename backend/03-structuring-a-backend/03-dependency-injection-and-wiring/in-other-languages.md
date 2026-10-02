# Dependency Injection in Other Languages

> **[Intermediate]** · A companion to [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|dependency injection and wiring]], which teaches the idea in TypeScript. Here: the same rule — *be handed your dependencies, don't make them* — in Python, Go, Java, Rust, C, C++ and C#, and what each language does with the main lesson's scope bug.

## Before you start

You can already:

- Explain constructor injection, the composition root, and the scope bug — per-request data stored on a shared instance → [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|the main lesson]].
- Read code in at least one of the languages below. Read §1 and your languages; skip the rest.

After this lesson you will be able to:

1. Wire dependencies idiomatically in your language: by hand, through a framework container, or with function pointers.
2. Say which languages have a standard DI container, and which deliberately don't.
3. Say what each language does about the scope bug — nothing, a runtime detector, a startup check, or a compile error.

## The kid version

Every kitchen hands the chef an oven instead of making them build one. But kitchens differ. In some, a manager hands out all the equipment at the start of the shift (a **DI container**). In others, the head chef sets every station up by hand (a **composition root in `main`**). And some kitchens have a rule written on the wall that stops two cooks grabbing the same pan at once (a **compiler that refuses unsafe sharing**).

**Where the analogy stops working.** The rule on the wall stops two cooks *grabbing* the pan together — it doesn't stop one cook putting down the wrong order on it. Rust's compiler is like that: it prevents two threads writing at once, but not a correct, well-locked program that still records the wrong user. §5 shows exactly this.

## 1. What changes between languages

The rule doesn't change. Three things do:

1. **Whether there's a standard container.** Java (Spring) and C# (the built-in .NET container) have one, and most projects use it. Python, Go, Rust, C and C++ mostly wire by hand, in `main`.
2. **What an "interface" is.** A TypeScript or Go interface is structural — anything with the right methods fits. Java and C# interfaces are declared. Rust uses traits. C++ uses abstract classes or templates. C uses a struct of function pointers. Python uses duck typing, or a `Protocol` if you want the type checker involved.
3. **What happens to the scope bug** — per-request data on a shared instance:

| Language | What catches it |
|---|---|
| TypeScript, Python | Nothing — it silently records the wrong user |
| Java, C++ | Nothing by default; a race detector (ThreadSanitizer for C++) if it's a data race |
| Go | `go test -race`, at runtime, during tests |
| C# | The container, **at startup**, with scope validation on |
| Rust | **The compiler** refuses unsynchronised sharing — but a correctly locked version can still record the wrong user |

## Terms used in this lesson

1. **DI container**: This is also known as an **IoC container** or **service provider**. It is a library that builds objects and their dependencies for you from registrations.
2. **Lifetime**: This is also known as **scope**. It is how long a container keeps one instance: **singleton** (one for the app), **scoped** (one per request), or **transient** (new every time).
3. **Captive dependency**: This is a shorter-lived service captured inside a longer-lived one — a per-request service inside a singleton. It's the container's name for the scope bug.
4. **Data race**: This is two threads accessing the same memory at the same time, at least one of them writing, with no synchronisation. It's undefined behaviour in C and C++, and a bug everywhere.
5. **Trait**: In Rust, this is a named set of methods a type can implement — Rust's version of an interface.
6. **Context variable**: This is a value attached to the current task or request rather than to an object — `ContextVar` in Python, `context.Context` in Go, `ThreadLocal` in Java, `AsyncLocal` in C#.

## 2. Python

Python has no standard container; **wire by hand in a composition-root function**, and pass dependencies to `__init__`. Frameworks have their own mechanism — FastAPI's `Depends` builds a dependency per request, which suits request-scoped things like a database session:

```python
# FastAPI — fragment
def get_audit(log: AuditLog = Depends(get_log)) -> AuditService:
    return AuditService(log)

@app.get("/invoices/{id}")
async def view_invoice(id: int, user: User = Depends(current_user), audit: AuditService = Depends(get_audit)):
    await audit.record(user.name, "viewed invoice")
```

**The scope bug happens exactly as in TypeScript**: asyncio interleaves tasks at every `await`, and nothing warns you. The context-variable fix is `contextvars.ContextVar` — each asyncio task gets its own copy.

```python
"""audit.py — constructor injection, a composition root, and the scope bug in Python."""
import asyncio
from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass
class AuditLog:
    entries: list[str] = field(default_factory=list)


class AuditServiceWithUserField:
    """BUG: built once at startup, but stores per-request data on itself."""

    def __init__(self, log: AuditLog):
        self.log = log
        self.current_user = "nobody"

    async def record(self, action: str) -> None:
        await asyncio.sleep(0.005)  # any await lets another request run in between
        self.log.entries.append(f"{self.current_user}: {action}")


class AuditService:
    """FIX 1: request data is an argument."""

    def __init__(self, log: AuditLog):
        self.log = log

    async def record(self, user: str, action: str) -> None:
        await asyncio.sleep(0.005)
        self.log.entries.append(f"{user}: {action}")


# FIX 2: a context variable — each asyncio task sees its own value (Python's AsyncLocalStorage).
current_user: ContextVar[str] = ContextVar("current_user", default="nobody")


class ContextAuditService:
    def __init__(self, log: AuditLog):
        self.log = log

    async def record(self, action: str) -> None:
        await asyncio.sleep(0.005)
        self.log.entries.append(f"{current_user.get()}: {action}")


def compose():
    """The composition root: the only place that knows the concrete classes."""
    log = AuditLog()
    return log, AuditServiceWithUserField(log), AuditService(log), ContextAuditService(log)
```

```python
import asyncio
import unittest

from audit import compose, current_user


class ScopeBugTests(unittest.IsolatedAsyncioTestCase):
    async def test_bug_a_per_request_field_records_the_wrong_user(self):
        log, buggy, _, _ = compose()

        async def handle(user):
            buggy.current_user = user
            await buggy.record("viewed invoice")

        await asyncio.gather(handle("ada"), handle("bayo"))
        self.assertEqual(log.entries, ["bayo: viewed invoice", "bayo: viewed invoice"])

    async def test_fix_1_pass_it_as_an_argument(self):
        log, _, audit, _ = compose()
        await asyncio.gather(audit.record("ada", "viewed invoice"), audit.record("bayo", "viewed invoice"))
        self.assertEqual(sorted(log.entries), ["ada: viewed invoice", "bayo: viewed invoice"])

    async def test_fix_2_a_context_variable_per_task(self):
        log, _, _, context_audit = compose()

        async def handle(user):
            current_user.set(user)  # gather runs each coroutine in its own task, with its own context
            await context_audit.record("viewed invoice")

        await asyncio.gather(handle("ada"), handle("bayo"))
        self.assertEqual(sorted(log.entries), ["ada: viewed invoice", "bayo: viewed invoice"])


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/python) — run `python3 labs/run.py dependency-injection-and-wiring/python` from the vault root. Checked with Python 3.14; all three tests pass, the first by asserting the wrong result.

## 3. Go

Go has no container, by design and by culture. **Dependencies are struct fields, set in `main`** — see [[backend/frameworks/go/04-structuring-a-go-service|structuring a Go service]]. Interfaces are declared by the package that *uses* them, and any type with the right methods satisfies them without saying so.

Per-request data travels in a **`context.Context`**, passed as the first argument of every call in the request path. That makes request scope explicit in every signature — verbose, and the reason Go code rarely has this bug.

**What Go adds:** the race detector. Run tests with `-race` and two goroutines writing the same field without a lock fail the test, with the stack of both writes.

```go
// Package audit: dependencies are struct fields, set once, in main. No container.
package audit

import (
	"context"
	"fmt"
	"sync"
)

// Log is a dependency. Real code might write to a database; tests use this.
type Log struct {
	mu      sync.Mutex
	Entries []string
}

func (l *Log) Add(entry string) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.Entries = append(l.Entries, entry)
}

// BuggyService stores per-request data on a value shared by every request.
type BuggyService struct {
	Log         *Log
	CurrentUser string // BUG: one field, many concurrent requests
}

func (s *BuggyService) Record(action string) {
	s.Log.Add(fmt.Sprintf("%s: %s", s.CurrentUser, action))
}

// Service takes request data as an argument — the fix.
type Service struct{ Log *Log }

func (s *Service) Record(user, action string) {
	s.Log.Add(fmt.Sprintf("%s: %s", user, action))
}

// For data every layer needs, Go passes a context.Context down every call.
type userKey struct{}

func WithUser(ctx context.Context, user string) context.Context {
	return context.WithValue(ctx, userKey{}, user)
}

func (s *Service) RecordFromContext(ctx context.Context, action string) {
	user, _ := ctx.Value(userKey{}).(string)
	s.Record(user, action)
}
```

```go
package audit

import (
	"context"
	"slices"
	"sync"
	"testing"
)

// Run under -race, this test fails: two goroutines write CurrentUser with no synchronisation.
func TestBuggyServiceRaces(t *testing.T) {
	svc := &BuggyService{Log: &Log{}}
	var wg sync.WaitGroup
	for _, user := range []string{"ada", "bayo"} {
		wg.Add(1)
		go func() {
			defer wg.Done()
			svc.CurrentUser = user
			svc.Record("viewed invoice")
		}()
	}
	wg.Wait()
}

func TestServiceTakesTheUserAsAnArgument(t *testing.T) {
	log := &Log{}
	svc := &Service{Log: log}
	var wg sync.WaitGroup
	for _, user := range []string{"ada", "bayo"} {
		wg.Add(1)
		go func() {
			defer wg.Done()
			svc.RecordFromContext(WithUser(context.Background(), user), "viewed invoice")
		}()
	}
	wg.Wait()
	slices.Sort(log.Entries)
	if !slices.Equal(log.Entries, []string{"ada: viewed invoice", "bayo: viewed invoice"}) {
		t.Fatalf("entries = %v", log.Entries)
	}
}
```

```sh
#!/bin/sh
# The fixed service is race-free; the buggy one must be caught by the race detector.
set -eu
export LC_ALL=C
out=$(mktemp)
trap 'rm -f "$out"' EXIT
go test -race -run TestServiceTakesTheUserAsAnArgument -count=1 . >/dev/null
echo "ok: the fixed service passes under -race"
if go test -race -run TestBuggyServiceRaces -count=1 . >"$out" 2>&1; then
  echo "FAIL: the race detector missed the shared CurrentUser field"; exit 1
fi
grep -q "WARNING: DATA RACE" "$out" || { echo "failed, but not with a data race:"; cat "$out"; exit 1; }
echo "ok: the race detector caught the per-request field on a shared service"
```

**Lab:** [`backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/go) — the check prints `ok: the race detector caught the per-request field on a shared service`. Checked with Go 1.26. **Run `go test -race ./...` in CI** for any Go service; it catches this whole class of bug for the cost of slower tests.

## 4. Java (and Spring)

Plain Java wires by hand, like the lab below. Almost every real project uses **Spring**, where you declare components and the container builds them — with **constructor injection**, which needs no annotation when a class has one constructor:

```java
// Spring — fragment
@Service
class AuditService {
    private final AuditLog log;
    AuditService(AuditLog log) { this.log = log; }   // Spring passes the AuditLog bean
}
```

Spring beans are **singletons by default** — so the scope bug is the classic Spring mistake. A `@RequestScope` bean injected into a singleton works only because Spring injects a *proxy* that looks up the current request's instance on each call. The safer habit is the same as everywhere: pass request data as an argument. Spring itself: [[backend/frameworks/java/01-spring-boot|Spring Boot]].

The lab forces the bad interleaving with two latches, so it happens every run instead of occasionally:

```java
package audit;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public final class Audit {
    // A dependency, handed in through constructors.
    public static final class Log {
        public final List<String> entries = new CopyOnWriteArrayList<>();
        void add(String entry) { entries.add(entry); }
        public List<String> sorted() { var copy = new java.util.ArrayList<>(entries); Collections.sort(copy); return copy; }
    }

    // BUG: one instance serves every request, but holds per-request data.
    public static final class BuggyService {
        private final Log log;
        private volatile String currentUser = "nobody";
        public BuggyService(Log log) { this.log = log; }
        public void setUser(String user) { currentUser = user; }
        public void record(String action) { log.add(currentUser + ": " + action); }
    }

    // FIX 1: request data is an argument.
    public static final class Service {
        private final Log log;
        public Service(Log log) { this.log = log; }
        public void record(String user, String action) { log.add(user + ": " + action); }
    }

    // FIX 2: per-thread context — the classic servlet-era answer. Always clear it when the request ends.
    public static final ThreadLocal<String> CURRENT_USER = ThreadLocal.withInitial(() -> "nobody");

    public static final class ContextService {
        private final Log log;
        public ContextService(Log log) { this.log = log; }
        public void record(String action) { log.add(CURRENT_USER.get() + ": " + action); }
    }
}
```

```java
package audit;

import java.util.List;
import java.util.concurrent.CountDownLatch;

// Plain-Java checks, run with assertions enabled (java -ea).
public final class Check {
    public static void main(String[] args) throws Exception {
        // The composition root for the test: build the graph by hand.
        var log = new Audit.Log();
        var buggy = new Audit.BuggyService(log);

        // Force the bad interleaving: ada sets her name, then bayo sets his, then ada records.
        var adaHasSetUser = new CountDownLatch(1);
        var bayoHasSetUser = new CountDownLatch(1);
        var ada = new Thread(() -> {
            buggy.setUser("ada");
            adaHasSetUser.countDown();
            await(bayoHasSetUser);
            buggy.record("viewed invoice");
        });
        var bayo = new Thread(() -> {
            await(adaHasSetUser);
            buggy.setUser("bayo");
            bayoHasSetUser.countDown();
            buggy.record("viewed invoice");
        });
        ada.start(); bayo.start(); ada.join(); bayo.join();
        assert log.entries.equals(List.of("bayo: viewed invoice", "bayo: viewed invoice")) : log.entries;
        System.out.println("bug reproduced: " + log.entries);

        var fixedLog = new Audit.Log();
        var service = new Audit.Service(fixedLog);
        var t1 = new Thread(() -> service.record("ada", "viewed invoice"));
        var t2 = new Thread(() -> service.record("bayo", "viewed invoice"));
        t1.start(); t2.start(); t1.join(); t2.join();
        assert fixedLog.sorted().equals(List.of("ada: viewed invoice", "bayo: viewed invoice")) : fixedLog.entries;

        var contextLog = new Audit.Log();
        var contextService = new Audit.ContextService(contextLog);
        Runnable request1 = () -> withUser("ada", () -> contextService.record("viewed invoice"));
        Runnable request2 = () -> withUser("bayo", () -> contextService.record("viewed invoice"));
        var t3 = new Thread(request1); var t4 = new Thread(request2);
        t3.start(); t4.start(); t3.join(); t4.join();
        assert contextLog.sorted().equals(List.of("ada: viewed invoice", "bayo: viewed invoice")) : contextLog.entries;
        System.out.println("both fixes record the right users");
    }

    static void withUser(String user, Runnable work) {
        Audit.CURRENT_USER.set(user);
        try { work.run(); } finally { Audit.CURRENT_USER.remove(); } // thread pools reuse threads
    }

    static void await(CountDownLatch latch) {
        try { latch.await(); } catch (InterruptedException e) { throw new RuntimeException(e); }
    }
}
```

**Lab:** [`backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/java) — prints `bug reproduced: [bayo: viewed invoice, bayo: viewed invoice]`, then `both fixes record the right users`. Checked with Java 21. Note the `finally` that clears the `ThreadLocal`: servers reuse threads, so a value left behind leaks into the next request. Java 25's `ScopedValue` removes that risk by design.

## 5. Rust

Rust wires by hand. Dependencies are fields; an interface is a **trait**, used either as `&dyn Trait` (one compiled function, chosen at runtime) or as a generic `T: Trait` (a copy compiled per type, no runtime cost). Shared, app-wide dependencies are usually an `Arc<…>` in the web framework's state → [[backend/frameworks/rust/03-state-and-shared-data|state and shared data]].

**What Rust adds is the most interesting part.** The scope bug, written naively, **doesn't compile**:

```sh
#!/bin/sh
# Without the Mutex, the shared field can't be written from two threads at all: rustc refuses.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/src"
cp Cargo.toml "$work/"
cat > "$work/src/lib.rs" <<'RS'
pub struct BuggyService {
    pub current_user: String,
}

pub fn handle_two_requests(service: &BuggyService) {
    std::thread::scope(|s| {
        s.spawn(|| service.current_user = "ada".to_string());
        s.spawn(|| service.current_user = "bayo".to_string());
    });
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then
  echo "FAIL: a shared field was written from two threads without a lock, and it compiled"; exit 1
fi
grep -q "error\[E0524\]: two closures require unique access to \`\*service\` at the same time" "$work/err.txt" \
  || { echo "failed, but not with E0524:"; cat "$work/err.txt"; exit 1; }
echo "ok: rustc refused the unsynchronised shared write"
```

rustc refuses with `error[E0524]: two closures require unique access to *service at the same time` — two threads may not both hold a mutable reference. To make it compile you must add a lock. And then:

```rust
//! Dependencies are fields set by the caller. A trait is the "interface"; tests pass a fake.
use std::sync::Mutex;

pub trait AuditLog: Send + Sync {
    fn add(&self, entry: String);
}

/// An in-memory log for tests. `Mutex` because many threads may write at once.
#[derive(Default)]
pub struct MemoryLog(pub Mutex<Vec<String>>);

impl AuditLog for MemoryLog {
    fn add(&self, entry: String) {
        self.0.lock().unwrap().push(entry);
    }
}

/// Compiles — the Mutex makes it free of *data* races — but it's still the scope bug:
/// one shared value holding per-request data.
pub struct BuggyService<'a> {
    pub log: &'a dyn AuditLog,
    pub current_user: Mutex<String>,
}

impl BuggyService<'_> {
    pub fn set_user(&self, user: &str) {
        *self.current_user.lock().unwrap() = user.to_string();
    }
    pub fn record(&self, action: &str) {
        let user = self.current_user.lock().unwrap().clone();
        self.log.add(format!("{user}: {action}"));
    }
}

/// The fix: request data is an argument.
pub struct Service<'a> {
    pub log: &'a dyn AuditLog,
}

impl Service<'_> {
    pub fn record(&self, user: &str, action: &str) {
        self.log.add(format!("{user}: {action}"));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::mpsc;
    use std::thread;

    #[test]
    fn a_mutex_stops_data_races_not_the_wrong_user() {
        let log = MemoryLog::default();
        let buggy = BuggyService {
            log: &log,
            current_user: Mutex::new("nobody".into()),
        };
        let (ada_set, ada_set_rx) = mpsc::channel();
        let (bayo_set, bayo_set_rx) = mpsc::channel();

        let buggy = &buggy; // share a reference; move the channel ends into their threads
        thread::scope(|s| {
            s.spawn(move || {
                buggy.set_user("ada");
                ada_set.send(()).unwrap();
                bayo_set_rx.recv().unwrap(); // wait until bayo has overwritten it
                buggy.record("viewed invoice");
            });
            s.spawn(move || {
                ada_set_rx.recv().unwrap();
                buggy.set_user("bayo");
                bayo_set.send(()).unwrap();
                buggy.record("viewed invoice");
            });
        });

        let entries = log.0.lock().unwrap();
        assert_eq!(*entries, ["bayo: viewed invoice", "bayo: viewed invoice"]);
    }

    #[test]
    fn passing_the_user_records_each_request_correctly() {
        let log = MemoryLog::default();
        let service = Service { log: &log };
        thread::scope(|s| {
            s.spawn(|| service.record("ada", "viewed invoice"));
            s.spawn(|| service.record("bayo", "viewed invoice"));
        });
        let mut entries = log.0.lock().unwrap().clone();
        entries.sort();
        assert_eq!(entries, ["ada: viewed invoice", "bayo: viewed invoice"]);
    }
}
```

The first test passes by asserting **`bayo` twice**. The `Mutex` makes every access safe — no data race, no undefined behaviour — and the program is still wrong, because one shared value holds per-request data. **Rust prevents data races, not logic errors.** The fix is the same as in every other language.

**Lab:** [`backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/rust) — checked with Rust 1.96.

## 6. C

C has no classes and no containers. An interface is a **struct of function pointers** plus a pointer to the implementation's own state — the same idea C++ compiles virtual functions into. Injection is passing that struct in.

```c
/* audit.h — dependency injection in C: a struct of function pointers is the interface,
 * and the caller passes it in. */
#ifndef AUDIT_H
#define AUDIT_H

#include <stddef.h>

typedef struct {
    void *self;                                    /* the implementation's own state */
    void (*add)(void *self, const char *entry);    /* the one operation the audit needs */
} audit_log;

/* The fix for the scope bug is the same as everywhere: the user is an argument. */
void audit_record(const audit_log *log, const char *user, const char *action);

#endif
```

```c
/* A fake log that remembers entries — the test's stand-in for a database. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "audit.h"

typedef struct {
    char entries[4][128];
    int count;
} memory_log;

static void memory_add(void *self, const char *entry) {
    memory_log *m = self;
    snprintf(m->entries[m->count++], sizeof m->entries[0], "%s", entry);
}

int main(void) {
    memory_log memory = {0};
    audit_log log = {.self = &memory, .add = memory_add};   /* the composition root, for the test */

    audit_record(&log, "ada", "viewed invoice");
    audit_record(&log, "bayo", "viewed invoice");

    assert(memory.count == 2);
    assert(strcmp(memory.entries[0], "ada: viewed invoice") == 0);
    assert(strcmp(memory.entries[1], "bayo: viewed invoice") == 0);
    puts("ok: audit records through an injected log");
    return 0;
}
```

**Lab:** [`backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/c/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/c) — checked with GCC 16. The scope bug in C is a global or `static` variable holding "the current user"; with threads, writing it unsynchronised is a data race and undefined behaviour. The fix is the argument; a `_Thread_local` variable is the C equivalent of a context variable.

## 7. C++

C++ wires by hand. The interface is an **abstract class** with virtual functions, and the service holds a reference (or `std::shared_ptr`) to whatever implementation it was given. For zero runtime cost, use a template parameter instead — the C++ version of Rust's generics.

```cpp
#pragma once
#include <string>
#include <string_view>

namespace audit {

// The interface: an abstract class. Implementations override `add`.
class Log {
public:
    virtual ~Log() = default;
    virtual void add(std::string entry) = 0;
};

// Constructor injection: the service holds a reference to whatever Log it was given.
class Service {
public:
    explicit Service(Log& log) : log_(log) {}
    void record(std::string_view user, std::string_view action) {
        log_.add(std::string(user) + ": " + std::string(action));
    }

private:
    Log& log_;
};

}  // namespace audit
```

```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

#include "audit.hpp"

// A fake Log for the test, safe to call from several threads.
class MemoryLog final : public audit::Log {
public:
    void add(std::string entry) override {
        std::lock_guard lock(mutex_);
        entries.push_back(std::move(entry));
    }
    std::vector<std::string> entries;

private:
    std::mutex mutex_;
};

int main() {
    MemoryLog log;
    audit::Service service(log);  // the composition root, for the test

    std::jthread ada([&] { service.record("ada", "viewed invoice"); });
    std::jthread bayo([&] { service.record("bayo", "viewed invoice"); });
    ada.join();
    bayo.join();

    std::ranges::sort(log.entries);
    assert((log.entries == std::vector<std::string>{"ada: viewed invoice", "bayo: viewed invoice"}));
    std::cout << "ok: each request recorded with its own user\n";
}
```

**Lab:** [`backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/cpp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/cpp) — checked with GCC 16. A per-request field on a shared service is a data race, which is undefined behaviour; **ThreadSanitizer** (`-fsanitize=thread`) catches it at runtime, like Go's race detector. It isn't used in the lab because its runtime library isn't installed on the machine this was checked on — install `libtsan` and add the flag.

## 8. C#

.NET has a **built-in container** (`Microsoft.Extensions.DependencyInjection`), used by every ASP.NET Core app. You register each service with a lifetime — `AddSingleton`, `AddScoped` (one per HTTP request), `AddTransient` — and constructors receive what they declare.

**What C# adds:** the container knows lifetimes, so it can detect the scope bug. With `ValidateScopes` on — ASP.NET Core turns it on automatically in the Development environment — a scoped service inside a singleton fails **at startup**, before any request is served:

```csharp
using Microsoft.Extensions.DependencyInjection;

// 1. The bug, caught at startup: a singleton that captures a per-request (scoped) service.
var captive = new ServiceCollection();
captive.AddSingleton<AuditLog>();
captive.AddScoped<RequestContext>();      // one per request
captive.AddSingleton<CaptiveAuditService>(); // one for the whole app — holding a RequestContext
try
{
    captive.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });
    throw new Exception("FAIL: the container accepted a scoped service inside a singleton");
}
catch (AggregateException e) when (e.InnerException is InvalidOperationException inner)
{
    Console.WriteLine($"caught at startup: {inner.Message}");
}

// 2. The fix: the service that needs request data is scoped too.
var services = new ServiceCollection();
services.AddSingleton<AuditLog>();
services.AddScoped<RequestContext>();
services.AddScoped<AuditService>();
using var provider = services.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });

async Task HandleRequest(string user)
{
    using var scope = provider.CreateScope();            // ASP.NET Core does this per HTTP request
    scope.ServiceProvider.GetRequiredService<RequestContext>().User = user;
    await scope.ServiceProvider.GetRequiredService<AuditService>().Record("viewed invoice");
}
await Task.WhenAll(HandleRequest("ada"), HandleRequest("bayo"));

var entries = provider.GetRequiredService<AuditLog>().Entries.Order().ToList();
if (!entries.SequenceEqual(["ada: viewed invoice", "bayo: viewed invoice"]))
    throw new Exception($"FAIL: {string.Join(", ", entries)}");
Console.WriteLine($"scoped: {string.Join(", ", entries)}");

sealed class AuditLog
{
    private readonly List<string> _entries = [];
    public void Add(string entry) { lock (_entries) _entries.Add(entry); }
    public IReadOnlyList<string> Entries { get { lock (_entries) return [.. _entries]; } }
}

sealed class RequestContext { public string User { get; set; } = "nobody"; }

sealed class CaptiveAuditService(AuditLog log, RequestContext context)
{
    public void Record(string action) => log.Add($"{context.User}: {action}");
}

sealed class AuditService(AuditLog log, RequestContext context)
{
    public async Task Record(string action)
    {
        await Task.Delay(5); // other requests run here; each still sees its own RequestContext
        log.Add($"{context.User}: {action}");
    }
}
```

**Lab:** [`backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/03-dependency-injection-and-wiring/labs/csharp) — runs in the .NET 10 SDK container and prints:

```
caught at startup: … Cannot consume scoped service 'RequestContext' from singleton 'CaptiveAuditService'.
scoped: ada: viewed invoice, bayo: viewed invoice
```

The context-variable equivalent is `AsyncLocal<T>`; ASP.NET Core's `IHttpContextAccessor` is built on it. C# itself: [[backend/frameworks/csharp/index|C#]].

## Check your understanding

1. Which of these languages have a standard DI container, and which wire by hand in `main`?
2. What does Go's race detector catch, and when — at compile time or while tests run?
3. Why does the Rust version with a `Mutex` still record the wrong user?
4. What is a captive dependency, and how does .NET catch it?
5. Why must a Java `ThreadLocal` be cleared in a `finally` block?

<details>
<summary>Answers — after your attempt</summary>

1. Containers: Java (Spring) and C# (built into .NET). By hand: Python (apart from framework helpers like FastAPI's `Depends`), Go, Rust, C, C++.
2. Unsynchronised concurrent access to the same memory, at least one a write — detected at runtime, while code runs with `-race`, usually in tests.
3. The lock makes each access safe, but there's still one shared value holding per-request data. Whichever request wrote last wins. That's a logic error, which no compiler can see.
4. A shorter-lived service held by a longer-lived one — a per-request service inside a singleton. With `ValidateScopes` on, the container refuses to build it and throws at startup.
5. Servers reuse threads from a pool. A value left on a thread is still there for the next request that runs on it.

</details>

## Practice — independent task

**In the language you'd most like to use professionally after TypeScript:**

1. Rebuild the audit example from memory: an interface for the log, a service that receives it, a composition root, and a fake in the test.
2. Reproduce the scope bug deterministically — force the bad interleaving the way the Java and Rust labs do, with a latch or a channel.
3. Fix it twice: with an argument, and with that language's context mechanism.
4. If the language has a detector — Go's `-race`, C++'s ThreadSanitizer, .NET's `ValidateScopes` — show it catching the bug.

**Done when:** the bug reproduces every run, both fixes pass, and you can explain without notes what your language does and doesn't protect you from.

## Before moving on

You can wire dependencies idiomatically in your language and say what it does about the scope bug.

**Recap.** Same rule everywhere: be handed your dependencies. Java and C# use containers; the rest wire by hand in `main`. Interfaces are structural in TypeScript and Go, declared in Java and C#, traits in Rust, abstract classes in C++, function-pointer structs in C. The scope bug is silent in TypeScript and Python, caught by `-race` in Go, by `ValidateScopes` in .NET, and half-prevented by Rust's compiler — which stops data races but not wrong answers.

**Next.** Back to the course: [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index|hexagonal architecture]].

## Related
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|Dependency injection and wiring]] — the main lesson
- [[languages/01-java/03-tooling/02-dependency-injection|Dependency injection in Java]] — Spring's implementation in depth
- [[backend/frameworks/go/04-structuring-a-go-service|Structuring a Go service]] · [[backend/frameworks/rust/03-state-and-shared-data|Rust: state and shared data]] · [[backend/frameworks/csharp/index|C#]]
