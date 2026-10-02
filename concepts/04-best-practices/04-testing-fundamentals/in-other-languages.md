# Testing Fundamentals in Other Languages

> **[Beginner→Intermediate]** · A companion to [[concepts/04-best-practices/04-testing-fundamentals/index|testing fundamentals]], which teaches with Node's built-in test runner. The ideas — test levels, test doubles, an injected clock, order-independence — are the same everywhere. What changes is the tooling, the **culture around mocks**, and whether the **clock you need to inject comes in the standard library**.

## Before you start

You can already:

- Explain unit vs integration tests, the four test doubles, and why the clock is passed in → [[concepts/04-best-practices/04-testing-fundamentals/index|the main lesson]].
- Read code in at least one language below. Read §1 and your languages.

After this lesson you will be able to:

1. Name your language's test runner, mocking tool, injectable clock and integration-testing tools.
2. Write the main lesson's trial-reminder tests — stub, spy, fixed clock — idiomatically in your language.
3. Run your tests in random order, to catch tests that depend on each other.

## The kid version

Every school has exams, but they're run differently. Some schools have an exam hall and printed papers ready (**a built-in test runner and clock**); others make you bring your own desk and pen (**a third-party library for everything**). The questions on the paper — *does it still work?* — are the same in all of them.

**Where the analogy stops working.** A school picks one way of running exams. A language often has several competing test tools, and teams argue about them. The choice matters much less than whether the tests exist and run on every push.

## 1. The tooling, side by side

| Language | Runner | Test doubles | Injectable clock | Integration | Random order |
|---|---|---|---|---|---|
| TypeScript | `node:test`, Vitest, Jest | `mock.fn`, `vi.fn` | pass a clock; `mock.timers` | Supertest, Testcontainers | `--test-randomize` |
| Python | pytest (`unittest` built in) | `unittest.mock` | pass a callable; `freezegun` | FastAPI `TestClient`, Testcontainers | `pytest-randomly` |
| Go | `go test` | hand-written fakes (gomock exists) | `func() time.Time`; `testing/synctest` | `net/http/httptest`, Testcontainers | `go test -shuffle=on` |
| Java | JUnit 5 | Mockito | **`java.time.Clock`** — built in | `@SpringBootTest`, MockMvc, Testcontainers | random `MethodOrderer` |
| Rust | `cargo test` | hand-written fakes, `mockall` | a `Clock` trait | `testcontainers` crate | tests already run in parallel |
| C | none standard: `assert`, Unity, CMocka | function pointers, link seams | a function pointer | CTest | — |
| C++ | GoogleTest, Catch2 | gMock | a clock parameter, `std::chrono` | CTest | `--gtest_shuffle` |
| C# | xUnit, NUnit, MSTest | Moq, NSubstitute | **`TimeProvider`** — built in | `WebApplicationFactory`, Testcontainers | not guaranteed by xUnit |

Two differences change how you write tests, not just what you install:

- **Mock culture.** Java and C# teams reach for Mockito and Moq by default. Go's culture is the opposite: small interfaces and hand-written fakes, because a Go interface with one method is a five-line fake. Rust sits in between. Hand-written fakes are easier to read and harder to over-specify — the main lesson's "stub the questions, spy on the commands" is easier to follow when you write the double yourself.
- **The clock.** Java (`Clock`) and .NET (`TimeProvider`) ship an injectable clock, so "pass the clock in" is the standard pattern rather than a choice. Everywhere else you define a tiny interface or pass a function.

## Terms used in this lesson

1. **Test runner**: This is the tool that finds tests, runs them and reports results — `go test`, pytest, JUnit, `cargo test`.
2. **Mocking library**: This is a library that generates test doubles at runtime, such as Mockito or Moq, instead of you writing a class by hand.
3. **Table-driven test**: This is Go's idiom of one test function looping over a table of named cases, each run as a sub-test.
4. **Link seam**: In C, this is replacing a function with a test version by linking a different object file, without changing the code under test.
5. **`TimeProvider` / `Clock`**: These are the standard-library abstractions over "now" in .NET and Java, designed to be replaced in tests.

## 2. Python

**pytest** is the de facto runner; `unittest` ships with Python. `unittest.mock.Mock` creates stubs and spies in one line — `assert_called_once_with` is the spy assertion. For time, pass a callable, as here, or patch it with `freezegun` when you can't change the code.

```python
"""reminders.py — the trial-reminder emailer; every collaborator is passed in."""
from datetime import date, timedelta


def day_after(today: date) -> date:
    return today + timedelta(days=1)  # date arithmetic rolls months and years over


def ending_tomorrow(users: list[dict], today: date) -> list[dict]:
    target = day_after(today)
    return [u for u in users if u["trial_ends_on"] == target]


def send_trial_reminders(users, mailer, clock) -> int:
    due = ending_tomorrow(users.list_on_trial(), clock())
    for user in due:
        mailer.send(user["email"], "Your trial ends tomorrow")
    return len(due)
```

```python
import unittest
from datetime import date
from unittest.mock import Mock

from reminders import day_after, ending_tomorrow, send_trial_reminders

OCT_31 = date(2026, 10, 31)
USERS = [
    {"email": "ada@x.com", "trial_ends_on": date(2026, 11, 1)},
    {"email": "bayo@x.com", "trial_ends_on": date(2026, 11, 5)},
]


class ReminderTests(unittest.TestCase):
    def test_day_after_rolls_over_boundaries(self):
        self.assertEqual(day_after(OCT_31), date(2026, 11, 1))
        self.assertEqual(day_after(date(2026, 12, 31)), date(2027, 1, 1))
        self.assertEqual(day_after(date(2028, 2, 28)), date(2028, 2, 29))  # leap year

    def test_ending_tomorrow(self):
        self.assertEqual(ending_tomorrow(USERS, OCT_31), [USERS[0]])

    def test_send_with_stub_spy_and_fake_clock(self):
        users = Mock(list_on_trial=Mock(return_value=USERS))  # stub: canned answer
        mailer = Mock()                                       # spy: records calls
        sent = send_trial_reminders(users, mailer, clock=lambda: OCT_31)  # fake clock: a function
        self.assertEqual(sent, 1)
        mailer.send.assert_called_once_with("ada@x.com", "Your trial ends tomorrow")


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`concepts/04-best-practices/04-testing-fundamentals/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/04-testing-fundamentals/labs/python) — checked with Python 3.14.

## 3. Go

`go test` is built in, and tests live beside the code in `_test.go` files. The idioms: **table-driven tests** with `t.Run` sub-tests, and **hand-written doubles** for one-method interfaces. Time is a `func() time.Time`; for code that *sleeps* or uses timers, Go 1.25's `testing/synctest` runs it with a fake clock. For HTTP, `net/http/httptest` gives you a real server or a response recorder with no network.

```go
// Package reminders: the clock is a function value; collaborators are small interfaces.
package reminders

import "time"

type User struct {
	Email       string
	TrialEndsOn time.Time // midnight UTC
}

type UserSource interface{ ListOnTrial() []User }
type Mailer interface{ Send(to, subject string) }

func DayAfter(t time.Time) time.Time {
	y, m, d := t.UTC().Date()
	return time.Date(y, m, d+1, 0, 0, 0, 0, time.UTC) // time.Date normalises day 32
}

func SendTrialReminders(users UserSource, mailer Mailer, now func() time.Time) int {
	target := DayAfter(now())
	sent := 0
	for _, u := range users.ListOnTrial() {
		if u.TrialEndsOn.Equal(target) {
			mailer.Send(u.Email, "Your trial ends tomorrow")
			sent++
		}
	}
	return sent
}
```

```go
package reminders

import (
	"testing"
	"time"
)

func day(y int, m time.Month, d int) time.Time { return time.Date(y, m, d, 0, 0, 0, 0, time.UTC) }

// Table-driven: the idiomatic Go test — one function, many named cases.
func TestDayAfter(t *testing.T) {
	cases := []struct {
		name     string
		in, want time.Time
	}{
		{"month end", day(2026, 10, 31), day(2026, 11, 1)},
		{"year end", day(2026, 12, 31), day(2027, 1, 1)},
		{"leap day", day(2028, 2, 28), day(2028, 2, 29)},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := DayAfter(c.in); !got.Equal(c.want) {
				t.Fatalf("DayAfter(%v) = %v, want %v", c.in, got, c.want)
			}
		})
	}
}

// Hand-written doubles: Go's culture prefers these to mocking libraries.
type stubUsers []User

func (s stubUsers) ListOnTrial() []User { return s }

type spyMailer struct{ sent []string }

func (s *spyMailer) Send(to, subject string) { s.sent = append(s.sent, to+" | "+subject) }

func TestSendTrialReminders(t *testing.T) {
	users := stubUsers{{"ada@x.com", day(2026, 11, 1)}, {"bayo@x.com", day(2026, 11, 5)}}
	mailer := &spyMailer{}
	fakeNow := func() time.Time { return time.Date(2026, 10, 31, 12, 0, 0, 0, time.UTC) }

	if n := SendTrialReminders(users, mailer, fakeNow); n != 1 {
		t.Fatalf("sent %d, want 1", n)
	}
	if len(mailer.sent) != 1 || mailer.sent[0] != "ada@x.com | Your trial ends tomorrow" {
		t.Fatalf("mailer saw %v", mailer.sent)
	}
}
```

**Lab:** [`concepts/04-best-practices/04-testing-fundamentals/labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/04-testing-fundamentals/labs/go) — checked with Go 1.26. Add `-shuffle=on` to `go test` to run tests in random order.

## 4. Java

**JUnit 5** is the runner, **Mockito** the usual double library, and **`java.time.Clock`** the clock — production passes `Clock.systemUTC()`, tests pass `Clock.fixed(...)`. Interfaces with one method are functional interfaces, so a lambda is a complete stub or spy, as below. For Spring, `@SpringBootTest` starts the app and **Testcontainers** starts a real Postgres in Docker.

```java
package reminders;

import java.time.Clock;
import java.time.LocalDate;
import java.util.List;

// java.time.Clock is the standard injectable clock: production passes Clock.systemUTC(),
// tests pass Clock.fixed(...).
public final class Reminders {
    public record User(String email, LocalDate trialEndsOn) {}
    public interface UserSource { List<User> listOnTrial(); }
    public interface Mailer { void send(String to, String subject); }

    public static LocalDate dayAfter(LocalDate day) { return day.plusDays(1); }

    public static int sendTrialReminders(UserSource users, Mailer mailer, Clock clock) {
        LocalDate target = dayAfter(LocalDate.now(clock));
        int sent = 0;
        for (User user : users.listOnTrial()) {
            if (user.trialEndsOn().equals(target)) {
                mailer.send(user.email(), "Your trial ends tomorrow");
                sent++;
            }
        }
        return sent;
    }
}
```

```java
package reminders;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;

// In a Maven or Gradle project this is a JUnit 5 test, and the spy is usually Mockito's mock(Mailer.class).
public final class Check {
    public static void main(String[] args) {
        assert Reminders.dayAfter(LocalDate.of(2026, 10, 31)).equals(LocalDate.of(2026, 11, 1));
        assert Reminders.dayAfter(LocalDate.of(2026, 12, 31)).equals(LocalDate.of(2027, 1, 1));
        assert Reminders.dayAfter(LocalDate.of(2028, 2, 28)).equals(LocalDate.of(2028, 2, 29));

        Reminders.UserSource stub = () -> List.of(
            new Reminders.User("ada@x.com", LocalDate.of(2026, 11, 1)),
            new Reminders.User("bayo@x.com", LocalDate.of(2026, 11, 5)));
        List<String> sent = new ArrayList<>();
        Reminders.Mailer spy = (to, subject) -> sent.add(to + " | " + subject);
        Clock fixed = Clock.fixed(Instant.parse("2026-10-31T12:00:00Z"), ZoneOffset.UTC);

        assert Reminders.sendTrialReminders(stub, spy, fixed) == 1;
        assert sent.equals(List.of("ada@x.com | Your trial ends tomorrow")) : sent;
        System.out.println("ok: stub, spy and Clock.fixed");
    }
}
```

**Lab:** [`concepts/04-best-practices/04-testing-fundamentals/labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/04-testing-fundamentals/labs/java) — checked with Java 21, with plain `javac` (no build tool installed here).

## 5. Rust

`cargo test` is built in. Unit tests sit in a `#[cfg(test)] mod tests` inside the same file, so they can test private functions; integration tests go in `tests/`. Collaborators are **traits**, and doubles are small structs. A spy that records through a shared reference needs `RefCell`, because Rust won't let `&self` mutate otherwise. **Tests run in parallel threads by default**, so shared state between tests shows up fast.

The standard library has **no calendar dates** — only `Duration` and `SystemTime` — so date logic uses the `chrono` (or `time`) crate.

```rust
//! Collaborators are traits; tests pass small structs that implement them.
use chrono::{Days, NaiveDate};

pub struct User {
    pub email: String,
    pub trial_ends_on: NaiveDate,
}

pub trait UserSource {
    fn list_on_trial(&self) -> Vec<User>;
}
pub trait Mailer {
    fn send(&self, to: &str, subject: &str);
}
pub trait Clock {
    fn today(&self) -> NaiveDate;
}

pub fn day_after(day: NaiveDate) -> NaiveDate {
    day.checked_add_days(Days::new(1)).expect("date in range")
}

pub fn send_trial_reminders(
    users: &impl UserSource,
    mailer: &impl Mailer,
    clock: &impl Clock,
) -> usize {
    let target = day_after(clock.today());
    let due: Vec<User> = users
        .list_on_trial()
        .into_iter()
        .filter(|u| u.trial_ends_on == target)
        .collect();
    for user in &due {
        mailer.send(&user.email, "Your trial ends tomorrow");
    }
    due.len()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    fn d(y: i32, m: u32, day: u32) -> NaiveDate {
        NaiveDate::from_ymd_opt(y, m, day).unwrap()
    }

    #[test]
    fn day_after_rolls_over_boundaries() {
        assert_eq!(day_after(d(2026, 10, 31)), d(2026, 11, 1));
        assert_eq!(day_after(d(2026, 12, 31)), d(2027, 1, 1));
        assert_eq!(day_after(d(2028, 2, 28)), d(2028, 2, 29));
    }

    struct StubUsers;
    impl UserSource for StubUsers {
        fn list_on_trial(&self) -> Vec<User> {
            vec![
                User {
                    email: "ada@x.com".into(),
                    trial_ends_on: d(2026, 11, 1),
                },
                User {
                    email: "bayo@x.com".into(),
                    trial_ends_on: d(2026, 11, 5),
                },
            ]
        }
    }

    #[derive(Default)]
    struct SpyMailer(RefCell<Vec<String>>); // RefCell: record calls through a shared reference
    impl Mailer for SpyMailer {
        fn send(&self, to: &str, subject: &str) {
            self.0.borrow_mut().push(format!("{to} | {subject}"));
        }
    }

    struct FixedClock(NaiveDate);
    impl Clock for FixedClock {
        fn today(&self) -> NaiveDate {
            self.0
        }
    }

    #[test]
    fn sends_with_stub_spy_and_fake_clock() {
        let mailer = SpyMailer::default();
        let sent = send_trial_reminders(&StubUsers, &mailer, &FixedClock(d(2026, 10, 31)));
        assert_eq!(sent, 1);
        assert_eq!(*mailer.0.borrow(), ["ada@x.com | Your trial ends tomorrow"]);
    }
}
```

**Lab:** [`concepts/04-best-practices/04-testing-fundamentals/labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/04-testing-fundamentals/labs/rust) — checked with Rust 1.96; Cargo downloads `chrono` on the first run.

## 6. C

There's no standard test framework: plain `assert`, or a small library such as Unity or CMocka, run by CTest or a Makefile. Doubles are **function pointers** passed in, as here, or **link seams** — linking a test version of a function instead of the real one.

One difference from the main lesson's bug: C's `timegm` (and `mktime`) **normalise** out-of-range fields, so adding 1 to `tm_mday` on 31 October and converting gives 1 November. The hand arithmetic is safe here *only* because of that normalising call.

```c
#define _DEFAULT_SOURCE /* timegm: standard in C23, a GNU/BSD extension before that */
#include "reminders.h"

#include <string.h>

void day_after(time_t now, char out[11]) {
    struct tm t;
    gmtime_r(&now, &t);
    t.tm_mday += 1;          /* may produce "October 32nd"... */
    time_t next = timegm(&t); /* ...which timegm normalises to 1 November */
    gmtime_r(&next, &t);
    strftime(out, 11, "%Y-%m-%d", &t);
}

int send_trial_reminders(const user *users, int n, const mailer *m, clock_fn clock) {
    char target[11];
    day_after(clock(), target);
    int sent = 0;
    for (int i = 0; i < n; i++) {
        if (strcmp(users[i].trial_ends_on, target) == 0) {
            m->send(m->self, users[i].email, "Your trial ends tomorrow");
            sent++;
        }
    }
    return sent;
}
```

```c
#define _DEFAULT_SOURCE
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "reminders.h"

static time_t utc(int y, int mo, int d) {
    struct tm t = {.tm_year = y - 1900, .tm_mon = mo - 1, .tm_mday = d, .tm_hour = 12};
    return timegm(&t);
}

static time_t oct31(void) { return utc(2026, 10, 31); }   /* the fake clock */

typedef struct { char last[64]; int calls; } spy;
static void spy_send(void *self, const char *to, const char *subject) {
    spy *s = self;
    snprintf(s->last, sizeof s->last, "%s | %s", to, subject);
    s->calls++;
}

int main(void) {
    char out[11];
    day_after(utc(2026, 10, 31), out); assert(strcmp(out, "2026-11-01") == 0);
    day_after(utc(2026, 12, 31), out); assert(strcmp(out, "2027-01-01") == 0);
    day_after(utc(2028, 2, 28), out);  assert(strcmp(out, "2028-02-29") == 0);

    user users[] = {{"ada@x.com", "2026-11-01"}, {"bayo@x.com", "2026-11-05"}};
    spy s = {0};
    mailer m = {.self = &s, .send = spy_send};
    assert(send_trial_reminders(users, 2, &m, oct31) == 1);
    assert(s.calls == 1 && strcmp(s.last, "ada@x.com | Your trial ends tomorrow") == 0);
    puts("ok: function-pointer clock and spy");
    return 0;
}
```

**Lab:** [`concepts/04-best-practices/04-testing-fundamentals/labs/c/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/04-testing-fundamentals/labs/c) — checked with GCC 16. `timegm` is standard from C23 and a GNU/BSD extension before it, hence `_DEFAULT_SOURCE`.

## 7. C++

**GoogleTest** (with **gMock** for doubles) or **Catch2** are the usual frameworks; the lab uses `assert` to stay dependency-free. C++20's `<chrono>` adds **calendar types** — `2026y / October / 31` is a date literal — and arithmetic goes through `sys_days`, which rolls months and years correctly. Collaborators can be `std::function`, as here, an abstract class, or a template parameter.

```cpp
#pragma once
// C++20's <chrono> has calendar types: year_month_day, sys_days, days.
#include <chrono>
#include <functional>
#include <string>
#include <vector>

namespace reminders {

using namespace std::chrono;

struct User { std::string email; year_month_day trial_ends_on; };

inline year_month_day day_after(year_month_day day) {
    return year_month_day{sys_days{day} + days{1}};   // through sys_days: rolls months and years
}

// Collaborators as std::function — the clock returns "today".
inline int send_trial_reminders(const std::vector<User>& users,
                                const std::function<void(const std::string&, const std::string&)>& send,
                                const std::function<year_month_day()>& today) {
    const auto target = day_after(today());
    int sent = 0;
    for (const auto& user : users) {
        if (user.trial_ends_on == target) {
            send(user.email, "Your trial ends tomorrow");
            ++sent;
        }
    }
    return sent;
}

}  // namespace reminders
```

```cpp
#include <cassert>
#include <iostream>

#include "reminders.hpp"

using namespace std::chrono;

int main() {
    assert(reminders::day_after(2026y / October / 31) == 2026y / November / 1);
    assert(reminders::day_after(2026y / December / 31) == 2027y / January / 1);
    assert(reminders::day_after(2028y / February / 28) == 2028y / February / 29);

    std::vector<reminders::User> users{{"ada@x.com", 2026y / November / 1}, {"bayo@x.com", 2026y / November / 5}};
    std::vector<std::string> sent;
    auto spy = [&](const std::string& to, const std::string& subject) { sent.push_back(to + " | " + subject); };
    auto fixed_today = [] { return 2026y / October / 31; };

    assert(reminders::send_trial_reminders(users, spy, fixed_today) == 1);
    assert(sent == std::vector<std::string>{"ada@x.com | Your trial ends tomorrow"});
    std::cout << "ok: chrono calendar, lambda spy and fixed clock\n";
}
```

**Lab:** [`concepts/04-best-practices/04-testing-fundamentals/labs/cpp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/04-testing-fundamentals/labs/cpp) — checked with GCC 16 and `-std=c++20`.

## 8. C#

**xUnit** (or NUnit, MSTest) is the runner; **Moq** or **NSubstitute** generate doubles. **`TimeProvider`**, built into .NET 8 and later, is the clock: production uses `TimeProvider.System`, and the `Microsoft.Extensions.TimeProvider.Testing` package provides `FakeTimeProvider`, which can also advance timers. For ASP.NET Core, `WebApplicationFactory<Program>` runs the whole app in memory for integration tests.

```csharp
// TimeProvider (.NET 8+) is the standard injectable clock. Production passes TimeProvider.System.
Check(TrialReminders.DayAfter(new DateOnly(2026, 10, 31)) == new DateOnly(2026, 11, 1), "month end");
Check(TrialReminders.DayAfter(new DateOnly(2026, 12, 31)) == new DateOnly(2027, 1, 1), "year end");
Check(TrialReminders.DayAfter(new DateOnly(2028, 2, 28)) == new DateOnly(2028, 2, 29), "leap day");

var stub = new StubUsers([new("ada@x.com", new DateOnly(2026, 11, 1)), new("bayo@x.com", new DateOnly(2026, 11, 5))]);
var spy = new SpyMailer();
var clock = new FixedTime(new DateTimeOffset(2026, 10, 31, 12, 0, 0, TimeSpan.Zero));

Check(TrialReminders.Send(stub, spy, clock) == 1, "one reminder sent");
Check(spy.Sent.SequenceEqual(["ada@x.com | Your trial ends tomorrow"]), "sent to ada");
Console.WriteLine("ok: stub, spy and a fixed TimeProvider");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

record User(string Email, DateOnly TrialEndsOn);
interface IUserSource { IReadOnlyList<User> ListOnTrial(); }
interface IMailer { void Send(string to, string subject); }

static class TrialReminders
{
    public static DateOnly DayAfter(DateOnly day) => day.AddDays(1);

    public static int Send(IUserSource users, IMailer mailer, TimeProvider time)
    {
        var target = DayAfter(DateOnly.FromDateTime(time.GetUtcNow().UtcDateTime));
        var due = users.ListOnTrial().Where(u => u.TrialEndsOn == target).ToList();
        foreach (var user in due) mailer.Send(user.Email, "Your trial ends tomorrow");
        return due.Count;
    }
}

// Hand-written doubles. Moq or NSubstitute generate these in real test projects, and the
// Microsoft.Extensions.TimeProvider.Testing package ships a FakeTimeProvider.
sealed class StubUsers(IReadOnlyList<User> users) : IUserSource { public IReadOnlyList<User> ListOnTrial() => users; }
sealed class SpyMailer : IMailer
{
    public List<string> Sent { get; } = [];
    public void Send(string to, string subject) => Sent.Add($"{to} | {subject}");
}
sealed class FixedTime(DateTimeOffset now) : TimeProvider { public override DateTimeOffset GetUtcNow() => now; }
```

**Lab:** [`concepts/04-best-practices/04-testing-fundamentals/labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/04-testing-fundamentals/labs/csharp) — runs in the .NET 10 SDK container.

## Check your understanding

1. Which two languages ship an injectable clock in their standard library, and what are they called?
2. Why do Go codebases use hand-written fakes more than mocking libraries?
3. Why does the Rust spy need `RefCell`?
4. Why is adding 1 to `tm_mday` safe in the C version but not in the main lesson's TypeScript `tomorrowBuggy`?
5. How do you run tests in random order in Go?

<details>
<summary>Answers — after your attempt</summary>

1. Java's `java.time.Clock` and .NET's `TimeProvider`.
2. Go interfaces are small and satisfied implicitly, so a fake is a few lines of ordinary code — readable, typed, and free of a library's API. The culture favours that over generated mocks.
3. `send` takes `&self`, a shared reference, which can't mutate the struct's fields. `RefCell` moves the borrow check to runtime so the spy can record calls.
4. The C version passes the result through `timegm`, which normalises 32 October into 1 November. The TypeScript version formatted the raw day number into a string, so 32 stayed 32.
5. `go test -shuffle=on`.

</details>

## Practice — independent task

**In your second language:** write the trial-reminder tests from memory — boundary dates, a stub, a spy and a fixed clock — using that language's standard runner, then run them in random order.

**Done when:** all tests pass in random order, the clock is injected (not the real one read inside the function), and you can name your language's runner, double library, clock and integration tool without looking.

## Before moving on

You know your language's testing tools and can write the main lesson's tests idiomatically in it.

**Recap.** Same ideas, different tools. Java and .NET ship injectable clocks; elsewhere, pass a function or a trait. Go prefers hand-written fakes; Java and C# reach for Mockito and Moq. Rust has no standard dates and runs tests in parallel; C has no standard test framework at all. Random order: `--test-randomize`, `-shuffle=on`, `pytest-randomly`, `--gtest_shuffle`.

**Next.** Back to the course: [[concepts/04-best-practices/08-coupling-and-cohesion/index|coupling and cohesion]].

## Related
- [[concepts/04-best-practices/04-testing-fundamentals/index|Testing fundamentals]] — the main lesson
- [[backend/07-practices/02-testing-a-backend|Testing a backend]] — Testcontainers, test data, time
- [[backend/frameworks/go/06-testing-and-production|Go: testing and production]] · [[backend/frameworks/csharp/04-testing-and-production|C#: testing and production]]
