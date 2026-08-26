# Testing and Tooling

> **[Intermediate]** · xUnit, the analyzer story, and the tooling that comes free with the SDK.

## xUnit

The de-facto standard for new projects.

```csharp
public class DiscountCalculatorTests
{
    [Fact]
    public void NoDiscount_ForSmallOrders()
    {
        var result = new DiscountCalculator().For(100m);
        Assert.Equal(0m, result);
    }

    [Theory]
    [InlineData(100, 0)]
    [InlineData(500, 0)]
    [InlineData(501, 50.1)]
    [InlineData(1000, 100)]
    public void AppliesTieredDiscount(decimal total, decimal expected)
        => Assert.Equal(expected, new DiscountCalculator().For(total));
}
```

**`[Theory]` + `[InlineData]` is the highest-return feature** — the same argument as pytest's `parametrize` → [[languages/06-python/13-testing-and-tooling|Python]]. Each case is reported separately, so covering edge cases is cheap enough that you actually do it.

**xUnit's design choices are opinionated and mostly right:** a **new instance of the test class per test** (so state cannot leak between tests), constructor for setup and `IDisposable` for teardown, no `[SetUp]` attributes.

**NUnit** and **MSTest** are the alternatives; NUnit has richer assertions, MSTest is Microsoft's. **All three are fine** — xUnit is the default for new work.

## The rest of the kit

**FluentAssertions** — readable assertions and much better failure messages:
```csharp
result.Should().Be(50.1m);
orders.Should().HaveCount(3).And.OnlyContain(o => o.IsPaid);
```
*(Note its licence changed to paid for commercial use in v8 — check before adopting. Alternatives: `Shouldly`, or plain xUnit assertions.)*

**Moq / NSubstitute** — mocking:
```csharp
var repo = Substitute.For<IOrderRepository>();
repo.GetAsync(1).Returns(new Order { Total = 100m });
```
**Mock sparingly.** Each mock encodes an assumption about a collaborator; a suite full of them passes while the system is broken → [[concepts/interview/02-patterns-code-quality-and-review|testing theatre]]. Mock the true boundaries — network, time, randomness, paid APIs.

**Testcontainers** — spin up a real Postgres/Redis in Docker for integration tests. **This largely replaced in-memory database fakes**, which historically passed tests that failed against real SQL.

**`WebApplicationFactory<T>`** — spins up your whole ASP.NET Core app in-process for end-to-end API tests without a network. Genuinely one of the nicest testing stories in any ecosystem.

**Verify** — snapshot testing, for output too tedious to assert field by field.

## The analyzer story

**This is where C# tooling is strongest, and it's mostly free.**

**Roslyn analyzers** run as part of compilation, so warnings appear as you type, not in a separate lint step:

```xml
<PropertyGroup>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <AnalysisLevel>latest-recommended</AnalysisLevel>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
</PropertyGroup>
```

**`.editorconfig` drives formatting and style**, enforced by `dotnet format` and in the IDE.

**Worth adding:** `Microsoft.CodeAnalysis.NetAnalyzers` (in the SDK), **`SonarAnalyzer.CSharp`**, and **`Roslynator`**. Security-focused: **`SecurityCodeScan`** → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]].

**The nullable analyzer is the highest-value one you already have** — turn it on and treat its warnings as errors → [[languages/07-csharp/02-the-type-system|note 02]].

## Coverage and benchmarks

```bash
dotnet test --collect:"XPlat Code Coverage"    # coverlet, then ReportGenerator
```

**Coverage measures what ran, not what was checked** — the same caveat as everywhere → [[languages/06-python/13-testing-and-tooling|Python note 13]]. Use it to find untested regions, never as a target.

**BenchmarkDotNet** is the standout tool in this ecosystem:

```csharp
[MemoryDiagnoser]
public class Benchmarks
{
    [Benchmark] public string Concat() => string.Join(",", _items);
    [Benchmark] public string Builder() { … }
}
```

**It handles warmup, JIT tiering, statistical significance and outlier detection for you** — all the things that make hand-rolled `Stopwatch` benchmarks wrong. **`[MemoryDiagnoser]` reports allocations per operation**, which is often the number you actually care about → [[languages/07-csharp/08-memory-gc-and-spans|note 08]].

## CI

```yaml
- run: dotnet restore
- run: dotnet build --no-restore -c Release
- run: dotnet test --no-build -c Release --collect:"XPlat Code Coverage"
```

Add `dotnet format --verify-no-changes` to fail on unformatted code, and **`dotnet list package --vulnerable`** to catch known CVEs in dependencies → [[devops/06-ci-cd/README|CI/CD]].

## Related
- [[languages/07-csharp/11-the-standard-library-and-ecosystem|the ecosystem]]
- [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]]
- [[languages/07-csharp/13-performance-and-the-runtime|performance]] — BenchmarkDotNet in anger

*Source: [reference] — from the .NET testing documentation, Aug 2026.*
