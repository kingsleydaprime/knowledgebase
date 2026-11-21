---
id: ff03d8c1-395b-4532-b0fa-443fc36792ab
---

# Ulfius

Ulfius is a C framework for building REST APIs. It sits on top of libmicrohttpd and adds the parts that library leaves out: routing with path parameters, JSON, and a chain of callbacks that works like middleware.

## An Ulfius endpoint
<!-- bite: a26d2929-2354-4bbf-9728-32629751e42a -->

REST-shaped, with JSON handled:

```c
int callback_get_user(const struct _u_request *req, struct _u_response *resp, void *data) {
    const char *id = u_map_get(req->map_url, "id");
    json_t *json = json_pack("{s:s, s:s}", "id", id, "name", "Kingsley");
    ulfius_set_json_body_response(resp, 200, json);
    json_decref(json);
    return U_CALLBACK_CONTINUE;
}

ulfius_add_endpoint_by_val(&instance, "GET", "/users", "/:id", 0,
                           &callback_get_user, NULL);
```

Built on libmicrohttpd, adds routing with parameters, Jansson for JSON, and a `U_CALLBACK_CONTINUE` chain that works like middleware. The closest thing to a conventional REST framework in C.

---

## Related
<!-- bite: 7c0fc775-9d7a-4a5c-9fad-5595edda328d -->
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side, and the honest question of whether to use C at all
- [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]] — what Ulfius is built on
- [[backend/frameworks/ulfius/index|Ulfius]]

## About this lesson
<!-- bite: 6424eee4-cbf1-4d49-96fd-2ffb4825885b -->

**Level:** Intermediate. **Covers:** An Ulfius endpoint, and what it adds over plain libmicrohttpd.
