---
id: 403d5a78-f69f-4d5c-865e-d6cc29588155
---

# Database and Production

This lesson covers how a C++ backend talks to a database and what it needs before real users depend on it. C++ has no tool that checks your database code for mistakes while you build it, so you have to be careful by hand. It ends with the checklist for getting a C++ service ready for real traffic.

## Drogon's ORM
<!-- bite: 23e9c87b-948b-49cf-a56a-dbd62f81eacc -->

The most complete database story in C++ web work:

```cpp
auto client = drogon::app().getDbClient();

auto result = co_await client->execSqlCoro(
    "SELECT id, email, created_at FROM users WHERE id = $1", id);

if (result.empty()) { /* 404 */ }
auto email = result[0]["email"].as<std::string>();
```

With generated models (`drogon_ctl create model`):

```cpp
drogon::orm::Mapper<drogon_model::myapp::Users> mapper(client);

auto users = co_await mapper.findBy(
    Criteria(Users::Cols::_active, CompareOperator::EQ, true));

auto user = co_await mapper.findByPrimaryKey(id);
```

`drogon_ctl` reads your live schema and generates a model class per table — typed accessors, and a `Mapper` with a criteria-based query API.

**The checking is weaker than [[backend/frameworks/axum/08-data-with-postgres|Data with PostgreSQL]].** The generated models match the schema *as of generation time*; the raw `execSqlCoro` strings are never checked at all. A typo'd column in a query string is a runtime error. Regenerate models after every migration, or they drift silently.

## The alternatives
<!-- bite: 84280db9-1cc7-4fc7-b580-c6fe1324cd84 -->

| | Character |
|---|---|
| **libpq / MySQL C API** | the C libraries directly — maximum control, manual everything |
| **libpqxx** | the good C++ Postgres wrapper: RAII, exceptions, `std::string` |
| **SOCI** | database-agnostic, stream-like syntax |
| **ODB** | true ORM with a codegen step from annotated C++ classes |
| **sqlpp11** | type-safe SQL as a C++ DSL — the closest to compile-time checking |

```cpp
// libpqxx — clean, RAII, synchronous
pqxx::connection conn{connection_string};
pqxx::work tx{conn};
auto rows = tx.exec_params("SELECT id, email FROM users WHERE id = $1", id);
tx.commit();                            // destructor rolls back if this isn't reached
```

**libpqxx is synchronous**, which is fine in a thread-pool framework like Crow and wrong inside an [[backend/frameworks/boost-beast/02-async-models-and-asio|asio event loop]] — it blocks the thread and stalls every connection on it. Drogon's own async client exists precisely for this reason.

**sqlpp11** is worth knowing about — it builds SQL as typed C++ expressions checked against a schema description, so a column that doesn't exist is a compile error:

```cpp
auto rows = db(select(users.id, users.email).from(users).where(users.id == id));
```

The cost is a heavyweight DSL, a codegen step for the schema headers, and error messages of the kind [[languages/05-cpp/08-templates-and-concepts|templates are famous for]].

## Connection pooling
<!-- bite: 0d666b75-998f-4a27-903e-6e677b1fae8f -->

```cpp
drogon::app().createDbClient(
    "postgresql", "127.0.0.1", 5432, "myapp", "user", "password",
    /*connectionNum=*/ 10);              // per event-loop thread, NOT total
```

> **Drogon's `connectionNum` is per thread.** With 8 event loops and 10 connections each you have opened **80** connections, not 10. Postgres's default `max_connections` is 100 total, so two replicas exhaust it.

That multiplication is the single most common C++ database misconfiguration, and the arithmetic is the same as everywhere: `connections × threads × replicas` under the database limit, with headroom. → [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]]

## Transactions
<!-- bite: d5039766-0063-475d-94c6-e8283f681fcf -->

```cpp
auto tx = co_await client->newTransactionCoro();
co_await tx->execSqlCoro("UPDATE accounts SET balance = balance - $1 WHERE id = $2", amt, from);
co_await tx->execSqlCoro("UPDATE accounts SET balance = balance + $1 WHERE id = $2", amt, to);
// commits when tx is destroyed without rollback() being called
```

RAII again: **an exception or early return destroys the transaction object, which rolls back.** No `defer`, no `finally`. It's the same property as [[languages/03-rust/03-ownership|Rust's]] and it's one of the genuinely pleasant parts of C++ database work.

Drogon's transaction commits on destruction by default (unless you called `rollback()`), which is the opposite of libpqxx and sqlx — **check which convention your library uses**, because getting it backwards means either silently committing failed work or silently discarding good work.

## Configuration and secrets
<!-- bite: 60a50233-d1e1-49aa-a3d6-eca387e37374 -->

```cpp
drogon::app().loadConfigFile("config.json").run();
```

Drogon is config-file driven, which is convenient and pushes you toward committing config files. **Read secrets from the environment**, not the file:

```cpp
const char *url = std::getenv("DATABASE_URL");
if (!url) { LOG_FATAL << "DATABASE_URL not set"; return 1; }
```

**Fail at startup on missing config**, loudly. A service that boots and fails on first request is worse than one that refuses to boot. → [[devops/06-secret-management/index|Secret Management]]

## Logging and metrics
<!-- bite: 3a72de83-dee6-48ef-9299-ac75d15df434 -->

```cpp
LOG_INFO << "user created: " << id;             // Drogon
LOG_ERROR << "db failure: " << e.what();
```

Stream-based, and **not structured** — that's a plain text line, not queryable JSON. For anything you'll need to search during an incident, use **spdlog** with a JSON pattern, or wrap Drogon's logger:

```cpp
spdlog::set_pattern(R"({"ts":"%Y-%m-%dT%H:%M:%S.%e","level":"%l","msg":"%v"})");
spdlog::info(R"("request_id":"{}","path":"{}")", req_id, path);
```

The gap versus [[languages/02-go/index|Go's `slog`]] or Rust's `tracing` is real: neither structured fields nor span context come for free, and there's no `#[instrument]` equivalent. You thread a request ID through manually or put it in a thread-local.

**Metrics:** `prometheus-cpp` exposes a `/metrics` endpoint. Same cardinality rule as everywhere — **label with the route pattern, never the actual path**, or you'll take down your Prometheus.

**Tracing:** the OpenTelemetry C++ SDK exists and is more manual than other languages' — no automatic instrumentation, so you create spans by hand at each boundary. → [[devops/07-observability/index|Observability]]

## Deployment
<!-- bite: fc0a5547-306a-43de-8723-9c84278e1c66 -->

The trap that makes C++ containers annoying:

```dockerfile
FROM gcc:14 AS build
WORKDIR /src
COPY . .
RUN cmake -B build -DCMAKE_BUILD_TYPE=Release -G Ninja && cmake --build build -j

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        libstdc++6 libpq5 libjsoncpp25 libssl3 && rm -rf /var/lib/apt/lists/*
COPY --from=build /src/build/myservice /usr/local/bin/
USER 1000:1000
ENTRYPOINT ["myservice"]
```

**A C++ binary is dynamically linked by default**, so the runtime image needs every shared library — libstdc++, libssl, libpq, libjsoncpp, and their transitive dependencies. That's why C++ images are ~100MB while [[languages/02-go/index|Go's]] are ~10MB on `distroless/static`.

```bash
ldd build/myservice        # find out what you actually need
```

Static linking is possible and awkward:

```bash
-static-libstdc++ -static-libgcc        # partial; still needs glibc
```

Fully static needs musl and a rebuilt toolchain. Most teams accept `debian-slim` or `distroless/cc` and move on.

**Build times are the other cost.** Use `ccache`, `ninja`, and a Docker layer that caches dependency builds — otherwise every image build recompiles everything. → [[languages/05-cpp/15-build-tooling-and-ecosystem|Build Tooling]]

## Graceful shutdown
<!-- bite: f6ccf7c1-3db0-490b-878d-664d7295af33 -->

```cpp
drogon::app().registerBeginningAdvice([] { LOG_INFO << "started"; });

std::signal(SIGTERM, [](int) { drogon::app().quit(); });
```

`quit()` stops the event loops after in-flight requests finish. Without it, a deploy kills requests mid-flight — and under [[devops/10-orchestration/index|Kubernetes]] a pod receives `SIGTERM` while the load balancer may still be sending it traffic.

**And ignore `SIGPIPE`**, or a client disconnecting mid-response terminates your process:

```cpp
std::signal(SIGPIPE, SIG_IGN);
```

Drogon does this for you; Beast-based code often doesn't.

## Sanitizers in CI
<!-- bite: 51bc2128-faca-490c-ac7a-d7b6aba6368c -->

The non-negotiable part, given the language:

```bash
cmake -B build-asan -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer -g"
cmake --build build-asan && ctest --test-dir build-asan

cmake -B build-tsan -DCMAKE_CXX_FLAGS="-fsanitize=thread -g"     # separate — incompatible with ASan
```

`-D_GLIBCXX_DEBUG` as well, for [[languages/05-cpp/09-the-stl-containers|iterator invalidation]] — the C++-specific bug ASan often misses, and one that async handlers holding references across suspension points hit readily.

**Run your test suite under ASan+UBSan and separately under TSan.** In a memory-unsafe language handling untrusted input, this is where the guarantees come from.

## The production checklist
<!-- bite: ae3cfeff-c6cb-4548-9845-3dfb8ce8138f -->

1. **Sanitizers in CI** — ASan+UBSan, plus TSan separately
2. **`SIGPIPE` ignored, `SIGTERM` handled** with graceful shutdown
3. **Connection count computed properly** — per thread × threads × replicas
4. **Structured logging** with a request ID
5. **Request body size capped**, and JSON parse depth limited
6. **Timeouts on everything** — they aren't defaults in asio
7. **Metrics with bounded label cardinality**
8. **`ldd` your binary** and pin the runtime image's libraries
9. **Reverse proxy in front** for TLS and malformed-request rejection
10. **Regenerate ORM models after every migration**

---

## Related
<!-- bite: fd18472a-7947-47e2-9c1f-4d741de57614 -->
- [[backend/frameworks/boost-beast/02-async-models-and-asio|Async Models and asio]] — why sync database drivers stall the loop
- [[backend/frameworks/drogon/04-when-to-choose-cpp|When to Choose C++]] — the decision
- [[languages/05-cpp/15-build-tooling-and-ecosystem|C++: Build Tooling]] — CMake, sanitizers, clang-tidy
- [[backend/04-data-and-persistence/index|Data and Persistence]] · [[devops/07-observability/index|Observability]]
- [[backend/frameworks/drogon/index|Drogon]]

## About this lesson
<!-- bite: 4896b549-024b-4fa7-85da-41443f44646c -->

**Level:** Intermediate → Advanced. **Covers:** Database access without a compile-time-checked ORM, and what a C++ service needs before it faces traffic.
