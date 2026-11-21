---
id: 3ad2c7e1-92a6-4381-acf2-ab683f8d77a0
---

# civetweb

civetweb is a tiny web server for C that comes as one header and one source file. It is what you reach for when a device or desktop app needs a small web page or API, and it is common in firmware.

## A civetweb server
<!-- bite: 5c95ea45-8a7d-4db7-9dcc-8c107a300a78 -->

The embedding option:

```c
struct mg_callbacks callbacks = {0};
const char *options[] = {
    "listening_ports", "8080",
    "num_threads", "10",
    "document_root", "./www",
    NULL
};
struct mg_context *ctx = mg_start(&callbacks, NULL, options);
mg_set_request_handler(ctx, "/api/users", user_handler, NULL);
```

One header, one source file, MIT-licensed, drops into any build. Thread pool model. It's what you use when a device or a desktop application needs a config UI, and it's in a lot of firmware.

---

## Related
<!-- bite: 5caddc8e-16d9-4286-9f53-2520b7ef0ae0 -->
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side, and the honest question of whether to use C at all
- [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]] — the other embedding option
- [[backend/frameworks/civetweb/index|civetweb]]

## About this lesson
<!-- bite: f2d7cb63-85c3-4758-9c65-dae8641220b4 -->

**Level:** Intermediate. **Covers:** Starting civetweb, registering a handler, and where it fits.
