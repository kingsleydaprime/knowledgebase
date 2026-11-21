---
subject: false
---

# Crow (C++ Backends)

## What Crow is

**Crow is a small C++ web framework that you add by including one header file.** Its routes look like Python's Flask, and it runs handlers on a thread pool. It is good for putting a small API inside an existing C++ program, not for building a large service.

## Lessons so far

1. [[backend/frameworks/crow/01-crow|Crow]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Crow way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Crow is and a first app**: the single header, `CROW_ROUTE`, and where it fits — written in part: [[backend/frameworks/crow/01-crow|Crow]]
2. **Routing**: typed params, methods, blueprints
3. **Middleware**: Crow middleware structs, `before_handle` and `after_handle`
4. **Structure**: a blueprint per feature
5. **Wiring**: app context, and passing dependencies into lambdas
6. **Validation and JSON**: `crow::json`, checking every field
7. **Errors**: `crow::response` codes and exception handling
8. **Data**: bringing your own database library, such as libpqxx, and pooling
9. **Auth**: a middleware that checks a token
10. **Security and cross-cutting**: CORS middleware, multipart, limits
11. **Testing**: `app.handle` without a socket
12. **Production**: multithreading, logging, embedding Crow in an existing program

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/drogon/index|Drogon]] — the full-stack C++ option
- [[languages/05-cpp/index|The C++ course]]

## About this subject

`[reference]`. Until November 2026 this was one section inside the C++ subject, which is now [[backend/frameworks/drogon/index|Drogon]].
