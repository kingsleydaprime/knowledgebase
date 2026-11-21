---
id: aad7aa93-b0fb-42c7-9489-6299d7996719
---

# Why C#, and the Toolchain

C# is a **statically typed, garbage-collected, multi-paradigm language** that began as Microsoft's answer to Java and has since overtaken it on language design while trailing it on ecosystem breadth.

**Where it wins:** enterprise backends, Windows desktop, **Unity game development**, and increasingly cross-platform services. It has the best async story of any mainstream language — `async`/`await` originated here in 2012 and was copied by JavaScript, Python, Rust and Swift → [[languages/07-csharp/07-async-await-and-tasks|note 07]].

**Where it doesn't:** systems programming without a runtime, scripting and data science (Python owns it), and anything where a GC pause is unacceptable → [[languages/07-csharp/08-memory-gc-and-spans|note 08]].

**The fair summary: C# is what Java would look like if it had shipped its good ideas faster.** Records, pattern matching, nullable reference types, value types, LINQ and async all arrived years earlier → [[languages/01-java/index|Java]].

## The naming, untangled
<!-- bite: 12900ab2-a191-4136-90b8-7b00bb04f96b -->

This confuses everyone and the history is short:

| Name | What it is |
|---|---|
| **C#** | The language |
| **.NET Framework** | The old, **Windows-only** runtime. 4.8 is the end of the line. Legacy |
| **.NET Core** | The rewrite: cross-platform, open source. Versions 1–3 |
| **.NET 5+** | **Core, renamed.** "Framework" was dropped to end the confusion. This is the one |
| **Mono** | An older independent implementation — **and what Unity used for years** |
| **CLR** | The runtime: JIT, GC, type system |
| **IL / CIL** | The bytecode C# compiles to |

**In 2026, "use .NET" means .NET 8 or 10 (the LTS releases).** Anything called ".NET Framework" is maintenance work.

## The toolchain
<!-- bite: 44f24d4a-e165-42c5-b247-44ebc13118d8 -->

```bash
dotnet new console -o MyApp     # scaffold
dotnet run                      # build and run
dotnet add package Serilog      # add a dependency (NuGet)
dotnet test                     # run tests
dotnet publish -c Release       # produce a deployable
dotnet format                   # format
```

**One CLI does everything**, which is a genuine advantage over the JVM's fragmented tooling.

**The project file is small and readable** — a real improvement over the XML of a decade ago:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>          <!-- turn this on -->
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Serilog" Version="4.0.0" />
  </ItemGroup>
</Project>
```

**`<Nullable>enable</Nullable>` is the single most valuable line in that file** → [[languages/07-csharp/02-the-type-system|note 02]].

**Editors:** Visual Studio (Windows, heavyweight, excellent), **VS Code + the C# Dev Kit** (cross-platform, the common choice), **Rider** (JetBrains, paid, widely considered the best).

## The Unity footnote — read this if that's why you're here
<!-- bite: 3673a5cb-5ebd-480f-93ea-3acee02cd5cd -->

**Unity does not use current C#.** Historically it was pinned to old Mono runtimes and old language versions, and even recent Unity trails the .NET releases by years.

**Practical consequences:**
- Some syntax in this course won't compile in your Unity project. **Check your Unity version's supported C# level** before assuming a feature exists
- Unity's GC has historically been non-generational Boehm, which makes allocation avoidance matter *more* than in .NET → [[languages/07-csharp/08-memory-gc-and-spans|note 08]]
- Unity compiles to IL then optionally to C++ via **IL2CPP** for AOT platforms (iOS, consoles, WebGL)

**None of this makes the language knowledge wrong** — it makes a subset unavailable. Learn the language properly; adjust at the boundary → [[game-development/engines/unity|Unity]].

## The version cadence
<!-- bite: b6e9e561-1158-49ab-a5b1-3b24c88f76dd -->

Annual releases, even-numbered ones are LTS (3 years' support). Notable additions, because the language has changed a lot:

| Version | Brought |
|---|---|
| 6.0 | `async`/`await` — **the one everyone copied** |
| 8.0 | **Nullable reference types**, switch expressions, `IAsyncEnumerable` |
| 9.0 | **Records**, top-level statements, init-only setters |
| 10–12 | File-scoped namespaces, global usings, **primary constructors**, collection expressions |

**Target the newest LTS you can** and know which features your runtime supports.

## Hello, modern C#
<!-- bite: ef81fc0b-7211-4a27-8b7a-aaf049193414 -->

```csharp
// Program.cs — top-level statements: no class, no Main
Console.WriteLine("Hello");

var user = new User("Ada", 36);            // a record
Console.WriteLine(user with { Age = 37 }); // non-destructive mutation

record User(string Name, int Age);
```

**That's the whole program.** The ceremony people remember from 2010 C# — a class, a static `Main`, a namespace block — is optional now.

## Related
<!-- bite: d54cee4c-b49b-4407-b04c-c04a90459e82 -->
- [[languages/07-csharp/02-the-type-system|the type system]] — value vs reference, and nullability
- [[languages/07-csharp/index|the course]]
- [[languages/01-java/index|Java]] — the closest neighbour
- [[game-development/engines/unity|Unity]] — the reason many people arrive here

## About this lesson
<!-- bite: 81598bd2-23b5-4173-af09-f8050cb94488 -->

**Level:** Beginner. **Covers:** What C# is for, the .NET naming mess untangled, and the one version footnote that matters if you're here for Unity.

*Source: [reference] — from the .NET and C# language documentation, Aug 2026.*
