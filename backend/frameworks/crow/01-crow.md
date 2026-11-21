---
id: 21ff8c34-5b2e-40e1-811f-0a9112ea7e32
---

# Crow

Crow is a small C++ web framework that comes as a single header file. Its routing looks like Python's Flask, which makes it easy to read and easy to drop into an existing C++ program.

## A Crow server
<!-- bite: b257c99c-f2ff-48cc-8add-8b2c4ebdb4b4 -->

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

---

## Related
<!-- bite: 5e07e1c4-2e74-4c9d-ae10-dc132666ce16 -->
- [[backend/frameworks/drogon/01-drogon|Drogon]] — the full-stack C++ option, and the landscape of all of them
- [[backend/frameworks/drogon/02-json-and-serialisation|JSON and Serialisation]] — the gap Crow feels too
- [[backend/frameworks/flask/01-flask|Flask]] — the Python framework Crow is modelled on
- [[backend/frameworks/crow/index|Crow]]

## About this lesson
<!-- bite: f6f04225-9aef-4bfa-86c0-aea32f6451fe -->

**Level:** Intermediate. **Covers:** What a Crow server looks like, and when a small header-only framework is the right call.
