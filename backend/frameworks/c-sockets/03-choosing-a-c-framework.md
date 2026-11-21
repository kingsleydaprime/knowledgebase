---
id: 5baf4234-3a5a-47eb-bcdb-ab8d5287ce8d
---

# Choosing a C Framework

A C web framework is a library that handles the work of running a web server so you can write your backend in the C language. This lesson puts the main ones side by side (libmicrohttpd, Kore, Ulfius and civetweb, each of which has its own subject) and asks honestly when any of them is the right choice.

## The options
<!-- bite: faab7037-6361-4891-acc2-97ddb870f430 -->

| | Character | Model | Use when |
|---|---|---|---|
| **[[backend/frameworks/libmicrohttpd/index\|libmicrohttpd]]** | GNU, small, embeddable, LGPL | pluggable: threads, thread pool, or external event loop | adding HTTP to an existing C program |
| **[[backend/frameworks/civetweb/index\|civetweb]]** | tiny, MIT, embeddable | thread pool | firmware, desktop apps, game engines |
| **mongoose** | similar; dual-licensed (GPL/commercial) | event loop | embedded, with commercial support |
| **[[backend/frameworks/kore/index\|Kore]]** | a full framework, security-focused | multi-process, privilege separation | a real C web application |
| **[[backend/frameworks/ulfius/index\|Ulfius]]** | REST-oriented, JSON built in | thread pool (on libmicrohttpd) | REST APIs in C |
| **libevent / libuv** | not HTTP frameworks — event-loop libraries with basic HTTP | event loop | you want the loop, not the framework |

## What none of them give you
<!-- bite: 62a88765-a5b7-4708-8545-c016aacf2ea3 -->

Compared with every other stack in [[backend/frameworks/index|frameworks/]]:

- **No dependency injection.** Globals or a context pointer threaded manually
- **No ORM.** libpq or the MySQL C API directly, and you write every mapping
- **No serialisation from types.** Jansson or cJSON, field by field. There is no `serde`, no `encoding/json`, no Jackson — because C has no reflection and no derive macros
- **No middleware ecosystem.** The `http.Handler` interoperability that makes [[backend/frameworks/net-http/index|Go]] compose has no equivalent
- **No standard testing framework.** Unity or greatest, and you wire it up

The JSON gap is the one that bites hardest. Turning a struct into JSON is ~5 lines per field, by hand, forever — and each of those lines is a place to leak memory or overflow a buffer.

## The honest question
<!-- bite: 1184709d-85b0-4155-aa36-461307000620 -->

**When is C actually the right answer for HTTP?**

**Yes:**
- **An existing C or C++ program needs an HTTP surface** — a device's config page, a game engine's debug server, an instrument's control API. Spawning a Go sidecar to talk to your C program over IPC is often the worse trade
- **The target has no other toolchain** — small embedded, no Rust or Go support
- **Learning.** Writing one from `socket()` up teaches you more about HTTP and about every runtime you use than any framework will → [[BUILD-PLAN|build-your-own-shit]]

**No:**
- **A new web service.** You're taking [[languages/04-c/07-memory-management|manual memory management]] onto the most attacker-exposed surface you own, for performance [[languages/02-go/index|Go]] or [[backend/frameworks/axum/index|Rust]] would also give you
- **Anything with a rich domain model.** No generics, no collections, no serialisation — you'll write thousands of lines the other stacks generate
- **A team.** C web code requires discipline that doesn't survive a deadline

> The pattern worth noticing: **C's remaining niche here is embedding, not serving.** When the process is already C for a good reason, adding HTTP to it beats adding a second process. When you're choosing from scratch, essentially nothing recommends it.
>
> And if the reason is "an existing C++ codebase", look at [[backend/frameworks/drogon/index|C++ frameworks]] first — Drogon gives you RAII, a real JSON layer, and coroutines, which removes most of this note's difficulty.

## If you do ship it
<!-- bite: a69e16b3-c797-4156-865d-357d125ef14b -->

1. **Use a real HTTP parser** — llhttp or picohttpparser
2. **Bound every buffer, cap every limit** → [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]]
3. **Compile hardened**: `-D_FORTIFY_SOURCE=2 -fstack-protector-strong -fPIE -pie -Wl,-z,relro,-z,now`
4. **Fuzz the parser** with libFuzzer or AFL++
5. **Run the test suite under ASan and UBSan**, in CI
6. **Drop privileges** after `bind()`; `chroot` and `seccomp` if you can
7. **Put a reverse proxy in front** — let nginx terminate TLS and reject malformed requests before they reach you
8. **Consider Kore** specifically for its privilege separation

That last one is worth emphasising: **a hardened reverse proxy in front of your C service is the highest-value single mitigation available.** It handles TLS, absorbs malformed requests, and enforces limits, so your parser sees a much narrower range of input.

---

## Related
<!-- bite: 64218fb5-151d-4e69-8d8f-00d1c46c034f -->
- [[backend/frameworks/c-sockets/01-the-accept-loop-and-event-loops|The Accept Loop and Event Loops]] — what these wrap
- [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] — the part they solve for you
- [[backend/frameworks/c-sockets/04-when-not-to-use-c|When Not to Use C]] — the decision, in full
- [[backend/frameworks/drogon/index|Drogon]] — usually the better answer for an existing native codebase
- [[backend/frameworks/c-sockets/index|Sockets and epoll]]

## About this lesson
<!-- bite: 6d47149a-d69e-436c-ac4d-10e25b49652b -->

**Level:** Intermediate. **Covers:** The C framework options side by side, what none of them give you, and the honest question of when any of them is the right answer.
