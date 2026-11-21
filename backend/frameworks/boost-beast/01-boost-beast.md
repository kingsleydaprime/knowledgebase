---
id: 6a81943f-b9f4-4811-ba49-9bd90177a300
---

# Boost.Beast

Boost.Beast is a C++ library for reading and writing HTTP and WebSocket messages, built on asio. It is not a framework: there is no routing, middleware or JSON, so you build those yourself on top of it.

## Reading and writing a message
<!-- bite: 65e02107-de34-4d61-ab59-cdf7240c2b39 -->

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

---

## Related
<!-- bite: bb2424ba-0a41-4bca-9961-ecfdc5c18063 -->
- [[backend/frameworks/boost-beast/02-async-models-and-asio|Async Models and asio]] — the library Beast is built on
- [[backend/frameworks/drogon/01-drogon|Drogon]] — what a full framework gives you instead, and the `shared_from_this` lifetime pattern
- [[backend/frameworks/c-sockets/01-the-accept-loop-and-event-loops|The Accept Loop and Event Loops]] — the layer below
- [[backend/frameworks/boost-beast/index|Boost.Beast]]

## About this lesson
<!-- bite: 13bde811-9461-4407-b19c-ba26b18aca62 -->

**Level:** Intermediate → Advanced. **Covers:** What Beast gives you (a correct HTTP parser and serialiser on asio) and when you'd build on it.
