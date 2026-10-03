# Monolith / Microservices / Serverless in Other Languages

> **[Intermediate]** · A companion to [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|monolith, microservices, serverless]], which puts numbers on coordination, shared releases, the network tax of extracting a module, serverless cost and cold starts, and builds a checker for a modular monolith's boundaries. This page does the same in Python, Go, Java, Rust and C#, with the same numbers in every language. The arithmetic translates line for line. What really differs is what each language does for you: some refuse boundary violations and cycles at compile time, so the checker is half built in. And the language you write a function in decides much of its cold start.

## Before you start

You can already:

- Explain the network tax of a chatty module, serverless break-even, cold-start chances and the two boundary rules → [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|the main lesson]].
- Read code in at least one of the languages here.

After this lesson you will be able to:

1. Say how your language enforces a module's boundary: by the compiler, by a build tool, or only by convention and a linter.
2. Say whether your language allows dependency cycles between modules, and where it stops them.
3. Rank the languages by typical cold start, and name each slow runtime's fix.

## The kid version

Five houses each have a rule about bedrooms. In one, bedroom doors lock, so nobody can wander into your room. In another, there's a sign saying "please knock" and nothing else. In a third, there's no lock, but a grown-up checks every evening who went where. The rooms are the same; how firmly the rule is kept is not. And on a cold morning, some houses heat up in seconds and some take half an hour, and that matters most if you only go in for a minute.

**Where the analogy stops working.** A lock can be picked. A compiler's boundary can't be talked round: code that imports another package's `internal` folder in Go simply doesn't build. The strongest rules are the ones that make the wrong code fail to compile.

## 1. The tools, by ecosystem

| Language | Hide a module's insides | Cycles between modules | Check boundaries | Faster cold starts |
|---|---|---|---|---|
| TypeScript | `exports` in `package.json`; convention | allowed | dependency-cruiser, ESLint boundary rules | small bundles |
| Python | a leading `_` (convention only) | allowed (and fragile at import time) | **import-linter** | trim dependencies; load lazily |
| Go | **`internal/` directories**, enforced by the compiler | **refused** between packages | the compiler, plus `go vet` | already fast: one static binary |
| Java | **JPMS** `module-info.java` `exports`; package-private | refused between JPMS modules | **ArchUnit**, Spring Modulith | Lambda SnapStart, GraalVM native image |
| Rust | **`pub` / `pub(crate)`**, enforced by the compiler | **refused** between crates | the compiler | already fast: one native binary |
| C# | **`internal`** with one project per module | **refused** between projects | NetArchTest, ArchUnitNET | Native AOT |

A modular monolith in Go, Rust, Java (with JPMS) or C# (with one project per module) gets both of the main lesson's rules from the compiler or build tool. Python and TypeScript need a linter in CI. C and C++ have static functions and separate libraries, but they're rarely where these architecture choices are made, so they have no lab here.

## 2. What changes between languages

### Where the boundary is enforced

The lab's `boundaryViolations` treats `catalog/internal/prices` as private to `catalog`. In **Go**, that's not a convention: a package under `catalog/internal/` can only be imported by code inside `catalog/`, and anything else fails to compile. **Rust** makes items private unless marked `pub`, and `pub(crate)` keeps them inside one crate, so a module split into crates in a workspace can't be reached into. **C#**'s `internal` hides a type outside its assembly, so one project per module enforces the boundary. **Java**'s JPMS exports only the packages listed in `module-info.java`. **Python** has only the leading-underscore convention; nothing stops `from catalog._prices import x`. That's why import-linter exists, and why the main lesson says to run the check in CI.

### Where cycles are stopped

`findCycle` finds `orders → billing → customers → orders`. Go refuses an import cycle between packages ("import cycle not allowed"). Cargo refuses a cycle between crates in a workspace, and .NET refuses one between project references. So in those languages, splitting modules into packages, crates or projects turns the cycle check into a build error. Inside one package, crate or project, nothing stops a cycle, and the lab's check is still useful. Python allows import cycles and sometimes fails at run time ("partially initialised module"), depending on which file was imported first.

### What the arithmetic needs

The formulas are the same everywhere. Small differences in the labs:

- Java's `Math.round` returns a `long`, so the break-even rounds with `Math.round(x / 1e5) / 10.0`. Without the `.0`, the division would be an integer one.
- Rust uses `powi` for whole-number powers.
- C# rounds with `MidpointRounding.AwayFromZero` to match JavaScript.
- The cold-start simulation ports mulberry32 with each language's 32-bit wrap-around, as in [[architecture/01-system-design-fundamentals/02-scalability-and-performance/in-other-languages|week 1's companion]].

### Cold starts depend on the runtime

The main lesson's $e^{-\lambda W}$ says how *often* a request is cold. How *long* a cold start takes depends mostly on the language. Go and Rust start a single native binary, typically in tens of milliseconds. Node and Python start an interpreter and load modules, so they're slower, and grow with the dependencies imported at start-up. The JVM and .NET runtimes have the slowest default starts, often reaching seconds for framework-heavy services. Each has a fix: Lambda SnapStart restores a snapshot of a started JVM, GraalVM native image compiles Java ahead of time, and .NET Native AOT does the same for C#. A quiet function written in Java without SnapStart pays the most, on the most requests.

### Frameworks built for services

When you do extract a service, the usual starting points are:

- **Go:** the standard library's `net/http`, or grpc-go.
- **Java:** Spring Boot, or Quarkus and Micronaut, which were designed for fast start and small memory.
- **C#:** ASP.NET Core minimal APIs.
- **Python:** FastAPI.
- **Rust:** axum.
- **TypeScript:** Fastify or NestJS.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| coordination links for 4, 8, 50 people | 6, 28, 1,225 |
| a release with 40 changes, 5 changes (1% each) | 33.1%, 4.9% |
| 40 calls of 1 ms at 99.99%; one coarse call | 40 ms and 99.60%; 1 ms and 99.99% |
| invoices at 200 ms, 512 MB | $1.87 a month for a million, $93.33 for fifty million; break-even 16.1 million against $30 |
| cold share with a 5-minute window, at 10, 1, 0.1 a minute | 0.00%, 0.67%, 60.65%; simulation within 0.5 points |
| the shop's modules | one violation (`orders → catalog/internal/prices`); then the cycle orders, billing, customers, orders |

## Terms used in this lesson

1. **Assembly**: In .NET, this is one compiled unit of code, usually one project's output. `internal` types are visible only inside it.
2. **JPMS (Java Platform Module System)**: The letters stand for those words. It's Java's built-in module system, in which `module-info.java` lists which packages a module exports and which modules it requires.
3. **Crate**: In Rust, this is one unit of compilation: a library or a program. A workspace holds several crates.
4. **Ahead-of-time compilation**: This is compiling code to native machine code before it runs, instead of starting a runtime that compiles it while running. It's what makes GraalVM native image and Native AOT start fast.
5. **Snapshot restore**: This means starting a function from a saved image of an already started runtime, instead of starting it from scratch. Lambda SnapStart does this for Java.

## 4. Python

`Module` is a dataclass, and `boundary_violations` is one comprehension, using the walrus operator `:=` to name the target inside it. `find_cycle` uses a nested function with the path in the enclosing scope. The cold-start simulation masks every step of mulberry32 to 32 bits.

```python
"""The arithmetic behind choosing a monolith, microservices or serverless, and a modular-monolith boundary
checker. The same numbers as the TypeScript lab."""
import math
from dataclasses import dataclass, field

MASK = 0xFFFFFFFF


def coordination_links(people: int) -> int:
    return people * (people - 1) // 2


def release_breaks(changes: int, p: float) -> float:
    return 1 - (1 - p) ** changes


def extract(calls_per_request: int, network_ms: float, call_availability: float) -> tuple[float, float]:
    """(added ms, chance every call succeeds) when a module moves behind the network."""
    return calls_per_request * network_ms, call_availability ** calls_per_request


@dataclass(frozen=True)
class Pricing:
    per_million_requests: float
    per_gb_second: float


def serverless_monthly(requests: float, ms: float, memory_gb: float, price: Pricing) -> float:
    return requests / 1e6 * price.per_million_requests + requests * (ms / 1000) * memory_gb * price.per_gb_second


def break_even_requests(server_monthly: float, ms: float, memory_gb: float, price: Pricing) -> float:
    return server_monthly / (price.per_million_requests / 1e6 + (ms / 1000) * memory_gb * price.per_gb_second)


def cold_share(per_minute: float, warm_minutes: float) -> float:
    return math.exp(-per_minute * warm_minutes)


def simulate_cold_share(per_minute: float, warm_minutes: float, requests: int, seed: int) -> float:
    a = seed & MASK

    def random() -> float:  # mulberry32, as in week 1's lab
        nonlocal a
        a = (a + 0x6D2B79F5) & MASK
        t = ((a ^ (a >> 15)) * (a | 1)) & MASK
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & MASK)) & MASK
        return (t ^ (t >> 14)) / 4294967296

    cold = sum(-math.log(1 - random()) / per_minute > warm_minutes for _ in range(requests))
    return cold / requests


@dataclass
class Module:
    name: str
    imports: list[str] = field(default_factory=list)


def boundary_violations(modules: list[Module]) -> list[str]:
    """Imports that reach inside another module instead of going through its public face."""
    names = {m.name for m in modules}
    return [f"{m.name} → {imp}" for m in modules for imp in m.imports
            if (target := imp.split("/")[0]) != m.name and target in names and "/" in imp]


def find_cycle(modules: list[Module]) -> list[str] | None:
    deps = {m.name: [d for d in dict.fromkeys(i.split("/")[0] for i in m.imports) if d != m.name] for m in modules}
    state: dict[str, str] = {}
    path: list[str] = []

    def visit(name: str) -> list[str] | None:
        if state.get(name) == "done":
            return None
        if state.get(name) == "visiting":
            return path[path.index(name):] + [name]  # back to a module on the path
        state[name] = "visiting"
        path.append(name)
        for d in deps.get(name, []):
            if cycle := visit(d):
                return cycle
        path.pop()
        state[name] = "done"
        return None

    for m in modules:
        if cycle := visit(m.name):
            return cycle
    return None
```

```python
import unittest

from architecture import (Module, Pricing, boundary_violations, break_even_requests, cold_share, coordination_links,
                          extract, find_cycle, release_breaks, serverless_monthly, simulate_cold_share)

PRICE = Pricing(per_million_requests=0.2, per_gb_second=0.0000166667)


class Architecture(unittest.TestCase):
    def test_coordination_grows_with_the_square(self):
        self.assertEqual([coordination_links(n) for n in [4, 8, 50]], [6, 28, 1_225])

    def test_a_shared_release_breaks_more_often(self):
        self.assertEqual(f"{release_breaks(40, 0.01) * 100:.1f}", "33.1")
        self.assertEqual(f"{release_breaks(5, 0.01) * 100:.1f}", "4.9")

    def test_chatty_versus_coarse(self):
        ms, availability = extract(40, 1, 0.9999)
        self.assertEqual((ms, f"{availability * 100:.2f}"), (40, "99.60"))
        ms, availability = extract(1, 1, 0.9999)
        self.assertEqual((ms, f"{availability * 100:.2f}"), (1, "99.99"))

    def test_serverless_until_traffic_is_steady(self):
        self.assertEqual(f"{serverless_monthly(1_000_000, 200, 0.5, PRICE):.2f}", "1.87")
        self.assertEqual(f"{serverless_monthly(50_000_000, 200, 0.5, PRICE):.2f}", "93.33")
        self.assertEqual(round(break_even_requests(30, 200, 0.5, PRICE) / 1e5) / 10, 16.1)

    def test_cold_starts_hit_quiet_functions(self):
        self.assertEqual([f"{cold_share(r, 5) * 100:.2f}" for r in [10, 1, 0.1]], ["0.00", "0.67", "60.65"])
        for rate in [1, 0.1]:
            self.assertLess(abs(simulate_cold_share(rate, 5, 100_000, 7) - cold_share(rate, 5)), 0.005)

    def test_boundaries_and_cycles(self):
        shop = [Module("orders", ["billing", "catalog/internal/prices"]), Module("billing", ["customers"]),
                Module("catalog", ["catalog/internal/prices"]), Module("customers")]
        self.assertEqual(boundary_violations(shop), ["orders → catalog/internal/prices"])
        self.assertIsNone(find_cycle(shop))
        shop[3].imports.append("orders")
        self.assertEqual(find_cycle(shop), ["orders", "billing", "customers", "orders"])


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/01-monolith-microservices-serverless/labs/python). `python3 labs/run.py monolith-microservices-serverless/python`.

## 5. Go

`strings.Cut` splits an import into module and inside. `FindCycle` declares `visit` with `var` first so the closure can call itself. The comments note where Go's own compiler already enforces both rules: `internal/` directories and refused import cycles.

```go
// Package architecture: the arithmetic behind choosing a monolith, microservices or serverless, and a
// modular-monolith boundary checker. The same numbers as the TypeScript lab.
package architecture

import (
	"math"
	"slices"
	"strings"
)

func CoordinationLinks(people int) int { return people * (people - 1) / 2 }

func ReleaseBreaks(changes int, p float64) float64 { return 1 - math.Pow(1-p, float64(changes)) }

// Extract returns the time added to a request, and the chance all its calls succeed, when a module moves behind the network.
func Extract(callsPerRequest int, networkMs, callAvailability float64) (addedMs, availability float64) {
	return float64(callsPerRequest) * networkMs, math.Pow(callAvailability, float64(callsPerRequest))
}

type Pricing struct{ PerMillionRequests, PerGBSecond float64 }

func ServerlessMonthly(requests, ms, memoryGB float64, p Pricing) float64 {
	return requests/1e6*p.PerMillionRequests + requests*(ms/1000)*memoryGB*p.PerGBSecond
}

func BreakEvenRequests(serverMonthly, ms, memoryGB float64, p Pricing) float64 {
	return serverMonthly / (p.PerMillionRequests/1e6 + (ms/1000)*memoryGB*p.PerGBSecond)
}

func ColdShare(perMinute, warmMinutes float64) float64 { return math.Exp(-perMinute * warmMinutes) }

func SimulateColdShare(perMinute, warmMinutes float64, requests int, seed uint32) float64 {
	a := seed
	random := func() float64 { // mulberry32, as in week 1's lab
		a += 0x6d2b79f5
		t := (a ^ a>>15) * (a | 1)
		t ^= t + (t^t>>7)*(t|61)
		return float64(t^t>>14) / 4294967296
	}
	cold := 0
	for range requests {
		if -math.Log(1-random())/perMinute > warmMinutes {
			cold++
		}
	}
	return float64(cold) / float64(requests)
}

type Module struct {
	Name    string
	Imports []string
}

// BoundaryViolations lists imports that reach inside another module. In real Go code, putting a module's insides
// in an internal/ directory makes the compiler refuse such imports, so this check comes for free.
func BoundaryViolations(modules []Module) []string {
	names := map[string]bool{}
	for _, m := range modules {
		names[m.Name] = true
	}
	var out []string
	for _, m := range modules {
		for _, imp := range m.Imports {
			target, _, inside := strings.Cut(imp, "/")
			if target != m.Name && names[target] && inside {
				out = append(out, m.Name+" → "+imp)
			}
		}
	}
	return out
}

// FindCycle returns a dependency cycle as a path that starts and ends at the same module, or nil. (Go refuses
// import cycles between packages at compile time; between modules of one package, nothing does.)
func FindCycle(modules []Module) []string {
	deps := map[string][]string{}
	for _, m := range modules {
		for _, imp := range m.Imports {
			d, _, _ := strings.Cut(imp, "/")
			if d != m.Name && !slices.Contains(deps[m.Name], d) {
				deps[m.Name] = append(deps[m.Name], d)
			}
		}
	}
	state := map[string]string{}
	var path []string
	var visit func(string) []string
	visit = func(name string) []string {
		switch state[name] {
		case "done":
			return nil
		case "visiting":
			return append(slices.Clone(path[slices.Index(path, name):]), name)
		}
		state[name] = "visiting"
		path = append(path, name)
		for _, d := range deps[name] {
			if cycle := visit(d); cycle != nil {
				return cycle
			}
		}
		path = path[:len(path)-1]
		state[name] = "done"
		return nil
	}
	for _, m := range modules {
		if cycle := visit(m.Name); cycle != nil {
			return cycle
		}
	}
	return nil
}
```

```go
package architecture

import (
	"fmt"
	"math"
	"slices"
	"testing"
)

var price = Pricing{PerMillionRequests: 0.2, PerGBSecond: 0.0000166667}

func TestCoordinationGrowsWithTheSquare(t *testing.T) {
	if got := []int{CoordinationLinks(4), CoordinationLinks(8), CoordinationLinks(50)}; !slices.Equal(got, []int{6, 28, 1_225}) {
		t.Fatal(got)
	}
}

func TestASharedReleaseBreaksMoreOften(t *testing.T) {
	if a, b := fmt.Sprintf("%.1f", ReleaseBreaks(40, 0.01)*100), fmt.Sprintf("%.1f", ReleaseBreaks(5, 0.01)*100); a != "33.1" || b != "4.9" {
		t.Fatal(a, b)
	}
}

func TestChattyVersusCoarse(t *testing.T) {
	ms, availability := Extract(40, 1, 0.9999)
	coarseMs, coarse := Extract(1, 1, 0.9999)
	if ms != 40 || fmt.Sprintf("%.2f", availability*100) != "99.60" || coarseMs != 1 || fmt.Sprintf("%.2f", coarse*100) != "99.99" {
		t.Fatal(ms, availability, coarseMs, coarse)
	}
}

func TestServerlessUntilTrafficIsSteady(t *testing.T) {
	one, fifty := ServerlessMonthly(1_000_000, 200, 0.5, price), ServerlessMonthly(50_000_000, 200, 0.5, price)
	breakEven := math.Round(BreakEvenRequests(30, 200, 0.5, price)/1e5) / 10
	if fmt.Sprintf("%.2f %.2f", one, fifty) != "1.87 93.33" || breakEven != 16.1 {
		t.Fatal(one, fifty, breakEven)
	}
}

func TestColdStartsHitQuietFunctions(t *testing.T) {
	var got []string
	for _, rate := range []float64{10, 1, 0.1} {
		got = append(got, fmt.Sprintf("%.2f", ColdShare(rate, 5)*100))
	}
	if !slices.Equal(got, []string{"0.00", "0.67", "60.65"}) {
		t.Fatal(got)
	}
	for _, rate := range []float64{1, 0.1} {
		if sim := SimulateColdShare(rate, 5, 100_000, 7); math.Abs(sim-ColdShare(rate, 5)) >= 0.005 {
			t.Fatal(rate, sim)
		}
	}
}

func TestBoundariesAndCycles(t *testing.T) {
	shop := []Module{
		{"orders", []string{"billing", "catalog/internal/prices"}},
		{"billing", []string{"customers"}},
		{"catalog", []string{"catalog/internal/prices"}},
		{"customers", nil},
	}
	if got := BoundaryViolations(shop); !slices.Equal(got, []string{"orders → catalog/internal/prices"}) || FindCycle(shop) != nil {
		t.Fatal(got, FindCycle(shop))
	}
	shop[3].Imports = append(shop[3].Imports, "orders")
	if got := FindCycle(shop); !slices.Equal(got, []string{"orders", "billing", "customers", "orders"}) {
		t.Fatal(got)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/01-monolith-microservices-serverless/labs/go). `python3 labs/run.py monolith-microservices-serverless/go`.

## 6. Java

`Module` is a record. `findCycle` returns `Optional<List<String>>`, and `visit` is a private static method with its state passed in, since Java has no nested functions. `LinkedHashSet` keeps each module's dependencies in the order they were declared, so the cycle is found in the same order as in the other languages.

```java
package architecture;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

/** The arithmetic behind choosing a monolith, microservices or serverless, and a boundary checker. */
public final class Architecture {
    private Architecture() {}

    public static long coordinationLinks(long people) {
        return people * (people - 1) / 2;
    }

    public static double releaseBreaks(int changes, double p) {
        return 1 - Math.pow(1 - p, changes);
    }

    public record Extracted(double addedMs, double availability) {}

    public static Extracted extract(int callsPerRequest, double networkMs, double callAvailability) {
        return new Extracted(callsPerRequest * networkMs, Math.pow(callAvailability, callsPerRequest));
    }

    public record Pricing(double perMillionRequests, double perGbSecond) {}

    public static double serverlessMonthly(double requests, double ms, double memoryGb, Pricing p) {
        return requests / 1e6 * p.perMillionRequests() + requests * (ms / 1000) * memoryGb * p.perGbSecond();
    }

    public static double breakEvenRequests(double serverMonthly, double ms, double memoryGb, Pricing p) {
        return serverMonthly / (p.perMillionRequests() / 1e6 + (ms / 1000) * memoryGb * p.perGbSecond());
    }

    public static double coldShare(double perMinute, double warmMinutes) {
        return Math.exp(-perMinute * warmMinutes);
    }

    public static double simulateColdShare(double perMinute, double warmMinutes, int requests, int seed) {
        int a = seed;
        int cold = 0;
        for (int i = 0; i < requests; i++) {
            a += 0x6d2b79f5; // mulberry32, as in week 1's lab
            int t = (a ^ (a >>> 15)) * (a | 1);
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            double random = Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
            if (-Math.log(1 - random) / perMinute > warmMinutes) cold++;
        }
        return (double) cold / requests;
    }

    public record Module(String name, List<String> imports) {}

    /** Imports that reach inside another module. JPMS modules, ArchUnit or Spring Modulith enforce this in real code. */
    public static List<String> boundaryViolations(List<Module> modules) {
        Set<String> names = modules.stream().map(Module::name).collect(Collectors.toSet());
        List<String> out = new ArrayList<>();
        for (Module m : modules) {
            for (String imp : m.imports()) {
                String target = imp.split("/")[0];
                if (!target.equals(m.name()) && names.contains(target) && imp.contains("/")) out.add(m.name() + " → " + imp);
            }
        }
        return out;
    }

    public static Optional<List<String>> findCycle(List<Module> modules) {
        Map<String, Set<String>> deps = new LinkedHashMap<>();
        for (Module m : modules) {
            Set<String> ds = new LinkedHashSet<>();
            for (String imp : m.imports()) {
                String d = imp.split("/")[0];
                if (!d.equals(m.name())) ds.add(d);
            }
            deps.put(m.name(), ds);
        }
        Map<String, String> state = new HashMap<>();
        List<String> path = new ArrayList<>();
        for (Module m : modules) {
            var cycle = visit(m.name(), deps, state, path);
            if (cycle.isPresent()) return cycle;
        }
        return Optional.empty();
    }

    private static Optional<List<String>> visit(String name, Map<String, Set<String>> deps, Map<String, String> state, List<String> path) {
        if ("done".equals(state.get(name))) return Optional.empty();
        if ("visiting".equals(state.get(name))) {
            List<String> cycle = new ArrayList<>(path.subList(path.indexOf(name), path.size()));
            cycle.add(name); // back to a module on the path
            return Optional.of(cycle);
        }
        state.put(name, "visiting");
        path.add(name);
        for (String d : deps.getOrDefault(name, Set.of())) {
            var cycle = visit(d, deps, state, path);
            if (cycle.isPresent()) return cycle;
        }
        path.removeLast();
        state.put(name, "done");
        return Optional.empty();
    }
}
```

```java
package architecture;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class ArchitectureCheck {
    private ArchitectureCheck() {}

    private static String fixed(double x, int places) {
        return String.format(Locale.ROOT, "%." + places + "f", x);
    }

    public static void main(String[] args) {
        assert Architecture.coordinationLinks(4) == 6 && Architecture.coordinationLinks(8) == 28 && Architecture.coordinationLinks(50) == 1_225;
        assert fixed(Architecture.releaseBreaks(40, 0.01) * 100, 1).equals("33.1") && fixed(Architecture.releaseBreaks(5, 0.01) * 100, 1).equals("4.9");

        var chatty = Architecture.extract(40, 1, 0.9999);
        var coarse = Architecture.extract(1, 1, 0.9999);
        assert chatty.addedMs() == 40 && fixed(chatty.availability() * 100, 2).equals("99.60") : chatty;
        assert coarse.addedMs() == 1 && fixed(coarse.availability() * 100, 2).equals("99.99") : coarse;

        var price = new Architecture.Pricing(0.2, 0.0000166667);
        assert fixed(Architecture.serverlessMonthly(1_000_000, 200, 0.5, price), 2).equals("1.87");
        assert fixed(Architecture.serverlessMonthly(50_000_000, 200, 0.5, price), 2).equals("93.33");
        assert Math.round(Architecture.breakEvenRequests(30, 200, 0.5, price) / 1e5) / 10.0 == 16.1;

        List<String> cold = new ArrayList<>();
        for (double rate : new double[] {10, 1, 0.1}) cold.add(fixed(Architecture.coldShare(rate, 5) * 100, 2));
        assert cold.equals(List.of("0.00", "0.67", "60.65")) : cold;
        for (double rate : new double[] {1, 0.1}) {
            double sim = Architecture.simulateColdShare(rate, 5, 100_000, 7);
            assert Math.abs(sim - Architecture.coldShare(rate, 5)) < 0.005 : sim;
        }

        var customers = new ArrayList<String>();
        var shop = List.of(new Architecture.Module("orders", List.of("billing", "catalog/internal/prices")),
                new Architecture.Module("billing", List.of("customers")),
                new Architecture.Module("catalog", List.of("catalog/internal/prices")),
                new Architecture.Module("customers", customers));
        assert Architecture.boundaryViolations(shop).equals(List.of("orders → catalog/internal/prices"));
        assert Architecture.findCycle(shop).isEmpty();
        customers.add("orders");
        assert Architecture.findCycle(shop).orElseThrow().equals(List.of("orders", "billing", "customers", "orders"));
        System.out.println("all architecture checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/01-monolith-microservices-serverless/labs/java). `python3 labs/run.py monolith-microservices-serverless/java`.

## 7. Rust

Module names are `&'static str`, so the cycle can be returned without copying strings. `visit` is a nested `fn`, which can't capture its surroundings, so the state and path are passed in as `&mut`. `split_once` separates the module from the inside path. The cold-start simulation's generator is a `move` closure that owns its state.

```rust
//! The arithmetic behind choosing a monolith, microservices or serverless, and a modular-monolith boundary
//! checker. The same numbers as the TypeScript lab.
use std::collections::{HashMap, HashSet};

pub fn coordination_links(people: u64) -> u64 {
    people * (people - 1) / 2
}

pub fn release_breaks(changes: i32, p: f64) -> f64 {
    1.0 - (1.0 - p).powi(changes)
}

/// (ms added, chance all calls succeed) when a module moves behind the network.
pub fn extract(calls_per_request: i32, network_ms: f64, call_availability: f64) -> (f64, f64) {
    (
        f64::from(calls_per_request) * network_ms,
        call_availability.powi(calls_per_request),
    )
}

pub struct Pricing {
    pub per_million_requests: f64,
    pub per_gb_second: f64,
}

pub fn serverless_monthly(requests: f64, ms: f64, memory_gb: f64, p: &Pricing) -> f64 {
    requests / 1e6 * p.per_million_requests + requests * (ms / 1000.0) * memory_gb * p.per_gb_second
}

pub fn break_even_requests(server_monthly: f64, ms: f64, memory_gb: f64, p: &Pricing) -> f64 {
    server_monthly / (p.per_million_requests / 1e6 + (ms / 1000.0) * memory_gb * p.per_gb_second)
}

pub fn cold_share(per_minute: f64, warm_minutes: f64) -> f64 {
    (-per_minute * warm_minutes).exp()
}

pub fn simulate_cold_share(per_minute: f64, warm_minutes: f64, requests: u32, seed: u32) -> f64 {
    let mut a = seed;
    let mut random = move || {
        // mulberry32, as in week 1's lab
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = (a ^ (a >> 15)).wrapping_mul(a | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4_294_967_296.0
    };
    let cold = (0..requests)
        .filter(|_| -(1.0 - random()).ln() / per_minute > warm_minutes)
        .count();
    cold as f64 / f64::from(requests)
}

pub struct Module {
    pub name: &'static str,
    pub imports: Vec<&'static str>,
}

/// Imports that reach inside another module. In a Rust workspace, items not marked `pub` can't be reached at all.
pub fn boundary_violations(modules: &[Module]) -> Vec<String> {
    let names: HashSet<&str> = modules.iter().map(|m| m.name).collect();
    let mut out = Vec::new();
    for m in modules {
        for imp in &m.imports {
            let (target, inside) = imp
                .split_once('/')
                .map_or((*imp, false), |(t, _)| (t, true));
            if target != m.name && names.contains(target) && inside {
                out.push(format!("{} → {imp}", m.name));
            }
        }
    }
    out
}

/// A dependency cycle as a path that starts and ends at the same module. (Cargo refuses cycles between crates.)
pub fn find_cycle(modules: &[Module]) -> Option<Vec<&'static str>> {
    let mut deps: HashMap<&str, Vec<&'static str>> = HashMap::new();
    for m in modules {
        let entry = deps.entry(m.name).or_default();
        for imp in &m.imports {
            let d = imp.split('/').next().unwrap_or(imp);
            if d != m.name && !entry.contains(&d) {
                entry.push(d);
            }
        }
    }
    fn visit(
        name: &'static str,
        deps: &HashMap<&str, Vec<&'static str>>,
        state: &mut HashMap<&'static str, bool>,
        path: &mut Vec<&'static str>,
    ) -> Option<Vec<&'static str>> {
        match state.get(name) {
            Some(true) => return None, // done
            Some(false) => {
                // still being visited: we've come back round
                let start = path.iter().position(|&p| p == name)?;
                return Some([&path[start..], &[name]].concat());
            }
            None => {}
        }
        state.insert(name, false);
        path.push(name);
        for &d in deps.get(name).into_iter().flatten() {
            if let Some(cycle) = visit(d, deps, state, path) {
                return Some(cycle);
            }
        }
        path.pop();
        state.insert(name, true);
        None
    }
    let (mut state, mut path) = (HashMap::new(), Vec::new());
    modules
        .iter()
        .find_map(|m| visit(m.name, &deps, &mut state, &mut path))
}

#[cfg(test)]
mod tests {
    use super::*;

    const PRICE: Pricing = Pricing {
        per_million_requests: 0.2,
        per_gb_second: 0.0000166667,
    };

    #[test]
    fn coordination_grows_with_the_square() {
        assert_eq!([4, 8, 50].map(coordination_links), [6, 28, 1_225]);
    }

    #[test]
    fn a_shared_release_breaks_more_often() {
        assert_eq!(
            format!(
                "{:.1} {:.1}",
                release_breaks(40, 0.01) * 100.0,
                release_breaks(5, 0.01) * 100.0
            ),
            "33.1 4.9"
        );
    }

    #[test]
    fn chatty_versus_coarse() {
        let ((ms, a), (cms, ca)) = (extract(40, 1.0, 0.9999), extract(1, 1.0, 0.9999));
        assert_eq!(
            format!("{ms} {:.2} {cms} {:.2}", a * 100.0, ca * 100.0),
            "40 99.60 1 99.99"
        );
    }

    #[test]
    fn serverless_until_traffic_is_steady() {
        assert_eq!(
            format!("{:.2}", serverless_monthly(1_000_000.0, 200.0, 0.5, &PRICE)),
            "1.87"
        );
        assert_eq!(
            format!(
                "{:.2}",
                serverless_monthly(50_000_000.0, 200.0, 0.5, &PRICE)
            ),
            "93.33"
        );
        assert_eq!(
            (break_even_requests(30.0, 200.0, 0.5, &PRICE) / 1e5).round() / 10.0,
            16.1
        );
    }

    #[test]
    fn cold_starts_hit_quiet_functions() {
        assert_eq!(
            [10.0, 1.0, 0.1].map(|r| format!("{:.2}", cold_share(r, 5.0) * 100.0)),
            ["0.00", "0.67", "60.65"]
        );
        for rate in [1.0, 0.1] {
            assert!(
                (simulate_cold_share(rate, 5.0, 100_000, 7) - cold_share(rate, 5.0)).abs() < 0.005
            );
        }
    }

    #[test]
    fn boundaries_and_cycles() {
        let mut shop = vec![
            Module {
                name: "orders",
                imports: vec!["billing", "catalog/internal/prices"],
            },
            Module {
                name: "billing",
                imports: vec!["customers"],
            },
            Module {
                name: "catalog",
                imports: vec!["catalog/internal/prices"],
            },
            Module {
                name: "customers",
                imports: vec![],
            },
        ];
        assert_eq!(
            boundary_violations(&shop),
            ["orders → catalog/internal/prices"]
        );
        assert_eq!(find_cycle(&shop), None);
        shop[3].imports.push("orders");
        assert_eq!(
            find_cycle(&shop),
            Some(vec!["orders", "billing", "customers", "orders"])
        );
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/01-monolith-microservices-serverless/labs/rust). `python3 labs/run.py monolith-microservices-serverless/rust`.

## 8. C#

`BoundaryViolations` is a LINQ query expression. `FindCycle` uses a local function, `Visit`, which captures `state` and `path`, with a range `path[start..]` for the cycle. It runs in the .NET SDK container.

```csharp
// The arithmetic behind choosing a monolith, microservices or serverless, and a modular-monolith boundary
// checker. The same numbers as the TypeScript lab.

public record Pricing(double PerMillionRequests, double PerGbSecond);

public record Module(string Name, List<string> Imports);

public static class Architecture
{
    public static long CoordinationLinks(long people) => people * (people - 1) / 2;

    public static double ReleaseBreaks(int changes, double p) => 1 - Math.Pow(1 - p, changes);

    /// <summary>(ms added, chance all calls succeed) when a module moves behind the network.</summary>
    public static (double AddedMs, double Availability) Extract(int callsPerRequest, double networkMs, double callAvailability) =>
        (callsPerRequest * networkMs, Math.Pow(callAvailability, callsPerRequest));

    public static double ServerlessMonthly(double requests, double ms, double memoryGb, Pricing p) =>
        requests / 1e6 * p.PerMillionRequests + requests * (ms / 1000) * memoryGb * p.PerGbSecond;

    public static double BreakEvenRequests(double serverMonthly, double ms, double memoryGb, Pricing p) =>
        serverMonthly / (p.PerMillionRequests / 1e6 + (ms / 1000) * memoryGb * p.PerGbSecond);

    public static double ColdShare(double perMinute, double warmMinutes) => Math.Exp(-perMinute * warmMinutes);

    public static double SimulateColdShare(double perMinute, double warmMinutes, int requests, uint seed)
    {
        var a = seed;
        var cold = 0;
        for (var i = 0; i < requests; i++)
        {
            a += 0x6d2b79f5; // mulberry32, as in week 1's lab
            var t = (a ^ (a >> 15)) * (a | 1);
            t ^= t + (t ^ (t >> 7)) * (t | 61);
            var random = (t ^ (t >> 14)) / 4294967296.0;
            if (-Math.Log(1 - random) / perMinute > warmMinutes) cold++;
        }
        return (double)cold / requests;
    }

    /// <summary>Imports that reach inside another module. In .NET, `internal` plus one project per module enforces this.</summary>
    public static List<string> BoundaryViolations(IReadOnlyList<Module> modules)
    {
        var names = modules.Select(m => m.Name).ToHashSet();
        return [.. from m in modules
                   from imp in m.Imports
                   let target = imp.Split('/')[0]
                   where target != m.Name && names.Contains(target) && imp.Contains('/')
                   select $"{m.Name} → {imp}"];
    }

    /// <summary>A dependency cycle as a path that starts and ends at the same module, or null.</summary>
    public static List<string>? FindCycle(IReadOnlyList<Module> modules)
    {
        var deps = modules.ToDictionary(m => m.Name, m => m.Imports.Select(i => i.Split('/')[0]).Where(d => d != m.Name).Distinct().ToList());
        var state = new Dictionary<string, bool>(); // false while visiting, true when done
        var path = new List<string>();
        List<string>? Visit(string name)
        {
            if (state.TryGetValue(name, out var done)) return done ? null : [.. path[path.IndexOf(name)..], name];
            state[name] = false;
            path.Add(name);
            foreach (var d in deps.GetValueOrDefault(name) ?? [])
                if (Visit(d) is { } cycle) return cycle;
            path.RemoveAt(path.Count - 1);
            state[name] = true;
            return null;
        }
        return modules.Select(m => Visit(m.Name)).FirstOrDefault(c => c is not null);
    }
}
```

```csharp
// Checks: the same numbers as every other language.
using System.Globalization;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static string Fixed(double x, int places) => x.ToString("F" + places, CultureInfo.InvariantCulture);

Check(new long[] { 4, 8, 50 }.Select(Architecture.CoordinationLinks).SequenceEqual([6L, 28, 1_225]), "links");
Check(Fixed(Architecture.ReleaseBreaks(40, 0.01) * 100, 1) == "33.1" && Fixed(Architecture.ReleaseBreaks(5, 0.01) * 100, 1) == "4.9", "release");

var chatty = Architecture.Extract(40, 1, 0.9999);
var coarse = Architecture.Extract(1, 1, 0.9999);
Check(chatty.AddedMs == 40 && Fixed(chatty.Availability * 100, 2) == "99.60", chatty);
Check(coarse.AddedMs == 1 && Fixed(coarse.Availability * 100, 2) == "99.99", coarse);

var price = new Pricing(0.2, 0.0000166667);
Check(Fixed(Architecture.ServerlessMonthly(1_000_000, 200, 0.5, price), 2) == "1.87", "a million");
Check(Fixed(Architecture.ServerlessMonthly(50_000_000, 200, 0.5, price), 2) == "93.33", "fifty million");
Check(Math.Round(Architecture.BreakEvenRequests(30, 200, 0.5, price) / 1e5, MidpointRounding.AwayFromZero) / 10 == 16.1, "break-even");

Check(new[] { 10, 1, 0.1 }.Select(r => Fixed(Architecture.ColdShare(r, 5) * 100, 2)).SequenceEqual(["0.00", "0.67", "60.65"]), "cold");
foreach (var rate in new[] { 1, 0.1 })
    Check(Math.Abs(Architecture.SimulateColdShare(rate, 5, 100_000, 7) - Architecture.ColdShare(rate, 5)) < 0.005, rate);

var shop = new List<Module>
{
    new("orders", ["billing", "catalog/internal/prices"]),
    new("billing", ["customers"]),
    new("catalog", ["catalog/internal/prices"]),
    new("customers", []),
};
Check(Architecture.BoundaryViolations(shop).SequenceEqual(["orders → catalog/internal/prices"]), "violations");
Check(Architecture.FindCycle(shop) is null, "no cycle yet");
shop[3].Imports.Add("orders");
Check(Architecture.FindCycle(shop)?.SequenceEqual(["orders", "billing", "customers", "orders"]) == true, string.Join(",", Architecture.FindCycle(shop) ?? []));
Console.WriteLine("all architecture checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/01-monolith-microservices-serverless/labs/csharp). `python3 labs/run.py monolith-microservices-serverless/csharp`.

## Common pitfalls

1. **Relying on a convention the language doesn't enforce.** A Python `_private` module or a TypeScript `internal` folder is imported the day someone's in a hurry. Add import-linter or dependency-cruiser to CI.
2. **One Go package for the whole monolith.** Everything in one package can see everything else, and cycles inside a package aren't refused. Use a package per module, and `internal/` for its insides.
3. **One .NET project for the whole monolith.** `internal` then hides nothing between modules. Use a project per module.
4. **A Java function on Lambda without SnapStart or native image.** Cold starts reach seconds, and quiet functions hit them often.
5. **Integer division in Java and C#.** `Math.round(x) / 10` divides two whole numbers. Write `/ 10.0`.

## Check your understanding

1. In which of the six languages does code that reaches into another module's private folder fail to compile, with no extra tooling?
2. Why does splitting a Go modular monolith into packages turn `findCycle` into a compile error?
3. A Python team wants the main lesson's boundary rules enforced. What do they add, and where does it run?
4. A Java function gets 1 request every 10 minutes. Using the main lesson, roughly what share of requests are cold, and what two fixes would you consider?
5. Why does the Rust `find_cycle` pass `state` and `path` into `visit` rather than capturing them?

<details>
<summary>Answers — after your attempt</summary>

1. Go, with `internal/` directories. Rust, Java with JPMS, and C# also do, once each module is its own crate, JPMS module or project. Python and TypeScript don't.
2. Each module becomes a package, and module imports become package imports. The Go compiler refuses import cycles between packages, so the cycle no longer builds.
3. Python's import-linter, with a contract listing the modules and what each may import (and forbidding imports of private parts), run in CI on every pull request.
4. With a 5-minute window, $e^{-0.1 \times 5}$ ≈ 61% are cold. For Java, each cold start is slow, so consider SnapStart, a GraalVM native image, or provisioned concurrency to keep an instance warm. Or ask whether this function needs to be on a latency-critical path at all.
5. A nested `fn` in Rust can't capture variables from the function around it; only closures can. A recursive closure is awkward in Rust, so the nested function takes its state as `&mut` parameters instead.

</details>

## Practice — independent task

**Make the compiler enforce a boundary.**

1. In Go (or Rust, or C#), make a tiny module layout: `catalog` with a private `prices` part, and `orders` that uses `catalog`'s public function.
2. Make `orders` import the private part directly, and record the exact compiler error.
3. Make `catalog` depend on `orders` as well as the other way round, and record the error.
4. In Python or TypeScript, set up import-linter or dependency-cruiser for the same layout, and show it failing on the same two mistakes.

**Done when:** you have both compiler errors and both linter failures written down, and one sentence on which you'd rather rely on in a team, and why.

## Before moving on

You can say how your language enforces a module boundary and refuses cycles, and how its runtime affects cold starts and the fixes for them.

**Recap.** The numbers behind the architecture choice are the same in every language. Enforcement isn't. Go's `internal/`, Rust's `pub`, C#'s `internal` across projects and Java's JPMS make the compiler keep a modular monolith modular, and Go, Cargo and .NET refuse cycles between packages, crates and projects. Python and TypeScript rely on convention plus a linter in CI. For serverless, Go and Rust start fastest; the JVM and .NET start slowest by default, with SnapStart, GraalVM native image and Native AOT as fixes.

## Related

- [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|Monolith, microservices, serverless]]: the main lesson
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/in-compiled-languages|Organising by feature in compiled languages]]: module boundaries in the same languages
- [[architecture/03-architectural-patterns/05-transactional-outbox/in-other-languages|Transactional outbox in other languages]]: this week's other companion
