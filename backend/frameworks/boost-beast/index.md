# Boost.Beast (C++ Backends)

## What Boost.Beast is

**Boost.Beast is a C++ library that reads and writes HTTP and WebSocket messages on top of asio. It is a toolkit, not a framework.** It has no routing, middleware or JSON, so you build those yourself. What you get is a correct, well-tested parser and asio's async model, which is why other frameworks and proxies are built on it.

## Lessons so far

1. [[backend/frameworks/boost-beast/01-boost-beast|Boost.Beast]]
2. [[backend/frameworks/boost-beast/02-async-models-and-asio|Async Models and asio]]

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Boost.Beast way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Boost.Beast is**: HTTP primitives on asio, and when to build on them — written in part: [[backend/frameworks/boost-beast/01-boost-beast|Boost.Beast]]
2. **asio and the async models**: callbacks, futures and coroutines, completion tokens, timeouts — written in part: [[backend/frameworks/boost-beast/02-async-models-and-asio|Async Models and asio]]
3. **A routing layer of your own**: a map from method and target to handler
4. **Middleware**: functions that wrap handlers
5. **Sessions and lifetime**: `shared_from_this`, strands
6. **Bodies and parsing**: body types, body limits, JSON with Boost.JSON
7. **Errors**: `beast::error_code`, timeouts with `tcp_stream`
8. **Data**: calling a database without blocking the `io_context`
9. **Auth and TLS**: reading auth headers, `ssl_stream`
10. **WebSockets**: `websocket::stream`
11. **Testing**: `beast::test::stream`
12. **Production**: a thread pool on one `io_context`, graceful shutdown, fuzzing

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/drogon/index|Drogon]] — what a full framework gives you instead
- [[backend/frameworks/c-sockets/index|Sockets and epoll]] — the layer below asio
- [[languages/05-cpp/index|The C++ course]]

## About this subject

`[reference]`. Until November 2026 this was one section inside the C++ subject, which is now [[backend/frameworks/drogon/index|Drogon]]. The asio lesson used to be lesson 02 of that subject.
