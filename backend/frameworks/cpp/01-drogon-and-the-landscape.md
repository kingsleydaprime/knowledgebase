# Drogon and the Landscape

**[Intermediate → Advanced]** — The C++ web framework options, and what a modern one actually looks like now that coroutines exist.

**Source:** `[reference]`. Assumes [[languages/05-cpp/README|the C++ course]].

## The landscape

| | Character | Model | Use when |
|---|---|---|---|
| **Drogon** | the most complete — HTTP/1.1+2, WebSockets, ORM, templates, **coroutines** | event loop per thread | a real C++ web application |
| **Crow** | header-only, Flask-like routing | thread pool | embedding something small |
| **oat++** | zero-dependency, API-docs-first | own async or threads | microservices, embedded |
| **Pistache** | modern C++ REST, Linux-only | event loop | Linux REST APIs |
| **Boost.Beast** | **not a framework** — HTTP/WebSocket primitives on asio | you choose | you want control, or building your own |
| **cpp-httplib** | single header, blocking | thread per connection | test servers, tools, quick embedding |

**Drogon is the default recommendation** for anything substantial. It's the only one with a full stack — routing, ORM, sessions, templates, coroutine support — and it consistently tops the TechEmpower benchmarks, which matters less than the completeness does.

## Drogon

```cpp
#include <drogon/drogon.h>

int main() {
    drogon::app()
        .addListener("0.0.0.0", 8080)
        .setThreadNum(0)                      // 0 = one event loop per CPU core
        .run();
}
```

Handlers are registered by macro on a controller class:

```cpp
class UserController : public drogon::HttpController<UserController> {
public:
    METHOD_LIST_BEGIN
        ADD_METHOD_TO(UserController::getUser, "/users/{id}", drogon::Get);
        ADD_METHOD_TO(UserController::createUser, "/users", drogon::Post);
    METHOD_LIST_END

    void getUser(const HttpRequestPtr &req,
                 std::function<void(const HttpResponsePtr &)> &&callback,
                 int64_t id);

    void createUser(const HttpRequestPtr &req,
                    std::function<void(const HttpResponsePtr &)> &&callback);
};
```

The path parameter arrives as a **typed argument** — `int64_t id`, parsed and converted before your code runs. That's the same idea as [[backend/frameworks/rust/02-extractors-and-responses|Axum's extractors]], done with template machinery instead of traits.

**The callback-passing signature is the async model.** You don't return a response; you invoke `callback` when you have one — possibly much later, from a different thread. That's what lets the event loop move on.

```cpp
void UserController::getUser(const HttpRequestPtr &req,
                             std::function<void(const HttpResponsePtr &)> &&callback,
                             int64_t id)
{
    auto client = drogon::app().getDbClient();
    client->execSqlAsync(
        "SELECT id, email FROM users WHERE id = $1",
        [callback = std::move(callback)](const drogon::orm::Result &r) {
            if (r.empty()) {
                auto resp = HttpResponse::newHttpResponse();
                resp->setStatusCode(k404NotFound);
                callback(resp);
                return;
            }
            Json::Value json;
            json["id"]    = r[0]["id"].as<int64_t>();
            json["email"] = r[0]["email"].as<std::string>();
            callback(HttpResponse::newHttpJsonResponse(json));
        },
        [callback](const drogon::orm::DrogonDbException &e) {       // error callback
            auto resp = HttpResponse::newHttpResponse();
            resp->setStatusCode(k500InternalServerError);
            callback(resp);
        },
        id);
}
```

Two callbacks — success and error — per async operation. Chain three database calls and you have three levels of nesting with error handling duplicated at each. **This is callback hell, and it's why the next section matters.**

## Coroutines change everything

C++20 coroutines turn that into linear code:

```cpp
drogon::Task<> UserController::getUser(HttpRequestPtr req,
                                       std::function<void(const HttpResponsePtr &)> callback,
                                       int64_t id)
{
    auto client = drogon::app().getDbClient();
    try {
        auto result = co_await client->execSqlCoro(
            "SELECT id, email FROM users WHERE id = $1", id);

        if (result.empty()) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setStatusCode(k404NotFound);
            callback(resp);
            co_return;
        }

        Json::Value json;
        json["id"]    = result[0]["id"].as<int64_t>();
        json["email"] = result[0]["email"].as<std::string>();
        callback(HttpResponse::newHttpJsonResponse(json));

    } catch (const drogon::orm::DrogonDbException &e) {
        LOG_ERROR << "db error: " << e.base().what();
        auto resp = HttpResponse::newHttpResponse();
        resp->setStatusCode(k500InternalServerError);
        callback(resp);
    }
}
```

Sequential reads, `try/catch` handles errors once, and no nesting. Three chained queries stay three lines instead of three nested lambdas.

> **If you're writing Drogon today, use the coroutine API.** It's the difference between C++ web development feeling archaic and feeling current. The callback API remains for pre-C++20 toolchains and for interop.

The catch, from [[languages/05-cpp/13-concurrency|Concurrency]]: C++20 coroutines are a *language mechanism*, not a library. The standard provides `co_await` and nothing to await on — so `drogon::Task` is Drogon's own coroutine type, and it doesn't interoperate with cppcoro's or asio's. Unlike Rust, where everything is a `Future`, C++ has no shared async vocabulary.

## Lifetime across the async boundary

The hard part, and the place C++ bites hardest.

```cpp
void handler(const HttpRequestPtr &req, Callback &&callback) {
    std::string user_id = req->getParameter("id");     // local

    db->execSqlAsync(sql,
        [&user_id, &callback](const Result &r) {        // ☠ CAPTURED BY REFERENCE
            callback(makeResponse(user_id));            // both are DEAD by now
        },
        errorCb);
}                                                        // handler returns immediately
```

The handler returns as soon as the query is *submitted*. Its stack frame is gone. When the callback fires, `user_id` and `callback` are dangling references — a use-after-free with no compiler warning.

**Capture by value or by move:**

```cpp
db->execSqlAsync(sql,
    [user_id, callback = std::move(callback)](const Result &r) mutable {
        callback(makeResponse(user_id));
    },
    errorCb);
```

For member functions on a heap object, keep the object alive with `shared_from_this`:

```cpp
class Session : public std::enable_shared_from_this<Session> {
    void start() {
        auto self = shared_from_this();                  // keeps `this` alive
        socket_.async_read_some(buffer_,
            [self](std::error_code ec, size_t n) { self->on_read(ec, n); });
    }
};
```

That pattern is ubiquitous in asio and Beast code, and it's the C++ equivalent of Rust's `'static` bound on a spawned task — except Rust makes you prove it and C++ makes you remember it. → [[languages/05-cpp/05-smart-pointers-and-ownership|Smart Pointers]]

**Coroutines don't fully remove the problem**: a coroutine's frame is heap-allocated and lives across suspension, so locals are safe — but a reference *parameter* to a coroutine dangles if the caller's argument dies. Hence `HttpRequestPtr req` by value in the coroutine signature above, rather than `const HttpRequestPtr &`.

## Crow

The lightweight option — header-only and immediately readable:

```cpp
#include "crow.h"

int main() {
    crow::SimpleApp app;

    CROW_ROUTE(app, "/users/<int>")
    ([](int id) {
        crow::json::wvalue json;
        json["id"] = id;
        return json;
    });

    CROW_ROUTE(app, "/users").methods("POST"_method)
    ([](const crow::request &req) {
        auto body = crow::json::load(req.body);
        if (!body) return crow::response(400);
        return crow::response(201);
    });

    app.port(8080).multithreaded().run();
}
```

Flask-shaped, no build integration beyond dropping in a header, and a thread-pool model rather than an event loop. Good for embedding a small API into an existing application; not what you'd build a large service on.

## Boost.Beast

Not a framework — HTTP and WebSocket **primitives** on asio:

```cpp
http::request<http::string_body> req;
http::read(socket, buffer, req);

http::response<http::string_body> res{http::status::ok, req.version()};
res.set(http::field::content_type, "application/json");
res.body() = R"({"status":"ok"})";
res.prepare_payload();
http::write(socket, res);
```

There's no routing, no middleware, no JSON — you build those. What you get is a correct, well-tested HTTP message parser and serialiser, plus asio's async model.

Use it when you're **building a framework**, implementing a proxy, or need protocol-level control. It's also the most portable option, since asio is the de facto standard C++ networking library and the basis of the long-proposed `std::net`.

## Choosing

**Drogon** for a real application — it's the only complete option, and with coroutines it's genuinely pleasant.

**Crow or cpp-httplib** for embedding something small in an existing program.

**Beast** for protocol-level work or when you're building the abstraction yourself.

**oat++** if API documentation generation matters to you, or for very constrained targets.

And the framing worth keeping from [[backend/frameworks/c/04-when-not-to-use-c|the C decision]]: **C++ on the server is defensible far more often than C**, because RAII and containers remove the easy memory bugs while keeping the performance. Whether it beats [[backend/frameworks/rust/README|Rust]] or [[languages/02-go/README|Go]] for a *new* service is the question note 05 takes up.

---

## Related
- [[backend/frameworks/cpp/02-async-models-and-asio|Async Models and asio]] — the layer underneath all of these
- [[backend/frameworks/cpp/03-json-and-serialisation|JSON and Serialisation]] — the gap C++ feels most
- [[languages/05-cpp/13-concurrency|C++: Concurrency]] — coroutines in context
- [[backend/frameworks/cpp/README|C++ backends]]
