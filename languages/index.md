---
subject_group: true
---

# Languages

## What this section is

**Each course here teaches one programming language properly: how it works, what makes it different, and how to use it well.**

All programming languages share the same basic ideas (variables, loops, functions), which [[programming-fundamentals/index|Programming Fundamentals]] teaches. But each language makes its own choices: how it handles memory, how it deals with errors, how it runs several things at once. Those choices are why a bug that's impossible in one language is common in another, and why some languages suit phones, some suit servers and some suit games.

These courses teach the language itself and its core tools. Web frameworks built on a language, such as Spring Boot for Java or FastAPI for Python, are taught in [[backend/frameworks/index|Backend: frameworks]], where they can be compared side by side.

## Which language should I learn?

- **Python:** the easiest start. Used for automation, data and AI, and backends.
- **Java or C#:** large company backends. C# is also the language of the Unity game engine.
- **Go:** simple, fast servers and cloud tools.
- **C:** to understand how computers really work underneath.
- **C++:** games, high-performance software, and anything where speed matters most.
- **Rust:** fast and safe systems software, without C's memory bugs.
- **Swift:** iPhone and Mac apps.
- **Kotlin:** Android apps.
- **Dart:** apps for phones and the web with Flutter.

If you're unsure, start with Python, and learn a second language once you're comfortable. The second one is much faster to learn than the first.

## The courses

Every course goes from beginner to advanced.

1. [[languages/01-java/index|Java]]: the language, then how the Java Virtual Machine runs it, tools, working with databases, and real systems built from two internship projects.
2. [[languages/02-go/index|Go]]: 13 notes. Go's simple type system, handling errors as ordinary values, and running many tasks at once with goroutines and channels.
3. [[languages/03-rust/index|Rust]]: 18 notes. Ownership (Rust's rules for who owns each piece of memory, the hard part), handling errors, traits, and safe concurrency.
4. [[languages/04-c/index|C]]: 13 notes. How C code is compiled, pointers, managing memory by hand, and the mistakes C doesn't protect you from.
5. [[languages/05-cpp/index|C++]]: 15 notes. Automatic clean-up of resources (RAII, the central idea), smart pointers, templates, the standard library, and which parts of modern C++ to actually use.
6. [[languages/06-python/index|Python]]: 14 notes. How Python really stores values (the source of most Python surprises), its built-in collections and their costs, generators, decorators, type hints, and why Python is slow at some things.
7. [[languages/07-csharp/index|C#]]: 13 notes. The .NET platform, LINQ for querying data, async code, and memory. Written because C# is Unity's language.
8. [[languages/08-swift/index|Swift]]: 12 notes. Optionals (values that might be missing), memory management, protocols, and safe concurrency. The language for iOS.
9. [[languages/09-kotlin/index|Kotlin]]: 8 notes. What carries over from Java, safety from missing values, and coroutines. Short, because the Java course covers the shared platform.
10. [[languages/10-dart/index|Dart]]: 6 notes. How hot reload works, safety from missing values, and how Dart runs several things at once. Written for Flutter.

## Practice

- [[languages/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".

## Related

- [[programming-fundamentals/index|Programming Fundamentals]]: the ideas every language shares. Start there if you're new.
- [[backend/frameworks/index|Backend: frameworks]]: the web frameworks built on these languages.
- [[dsa/index|Data Structures and Algorithms]]: the computer science underneath all of them.

---

## About this section

- **Why frameworks live elsewhere:** in August 2026 Java's Spring Boot material moved from here into [[backend/frameworks/spring-boot/index|Backend: Java]], so frameworks in different languages sit side by side. Spring's `@RestController` and Nest's `@Controller` are the same idea in different spelling, which is obvious when they share a folder.
- **Where it came from:** the Java course was checked against the [roadmap.sh Java roadmap](https://roadmap.sh/java), and its applied section comes from two real internship projects (record ID generator and direct debit sandbox). The others were written from reference sources.
- **Not covered yet:** JavaScript and TypeScript (the languages of the web, used throughout [[frontend/index|Frontend]]), and others such as Zig and Elixir.
