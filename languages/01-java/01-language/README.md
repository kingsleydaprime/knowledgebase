# 01 — Language

The Java language itself, beginner to fluent — before any framework or the JVM internals underneath. Part of the [[languages/01-java/README|Java course]].

Read in order; later files lean on earlier ones without re-explaining them.

1. [[languages/01-java/01-language/01-fundamentals|Fundamentals]] — the ground floor: static typing, syntax, primitives vs objects, strings, arrays, control flow, packages, access modifiers, `static`/`final`, pass-by-value semantics, `null`, `BigDecimal` for money
2. [[languages/01-java/01-language/02-oop|OOP]] — classes and objects, the four pillars (encapsulation, inheritance, polymorphism, abstraction), interfaces vs abstract classes, overloading vs overriding, static vs dynamic binding, nested classes, the `equals`/`hashCode` contract
3. [[languages/01-java/01-language/03-generics|Generics]] — type parameters, bounded types, wildcards (`? extends` / `? super`), and type erasure (what generics *don't* give you at runtime)
4. [[languages/01-java/01-language/04-collections|Collections]] — the `List`/`Set`/`Map`/`Queue`/`Deque` hierarchy, choosing an implementation by Big-O, `Iterator`, `Comparable`/`Comparator`
5. [[languages/01-java/01-language/05-functional-programming|Functional Programming]] — functional interfaces, lambdas, method references, the Stream API, higher-order functions, `Optional`
6. [[languages/01-java/01-language/06-exceptions|Exceptions]] — checked vs unchecked, the exception hierarchy, custom exceptions, try-with-resources, `finally` semantics
7. [[languages/01-java/01-language/07-modern-java|Modern Java]] — records, sealed classes, pattern matching for `switch`/`instanceof`, `var`, text blocks, switch expressions
8. [[languages/01-java/01-language/08-core-apis|Core APIs]] — date/time, regex, IO/NIO, files, networking, modules, annotations, cryptography

## Related
- [[languages/01-java/02-jvm-and-concurrency/README|JVM & Concurrency]] — what runs the code above
- [[languages/01-java/README|Java course index]]
