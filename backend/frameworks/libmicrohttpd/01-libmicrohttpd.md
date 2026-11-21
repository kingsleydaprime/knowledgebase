---
id: 13fedf4c-cec7-4006-a552-3a88435df785
---

# libmicrohttpd

libmicrohttpd is a small GNU library that adds an HTTP server to a C program. It is the usual choice when an existing C program needs to answer web requests, because it can run inside an event loop you already have.

## A libmicrohttpd server
<!-- bite: a174a523-d614-4d9b-bece-f059d8f9595a -->

The most common choice for embedding:

```c
#include <microhttpd.h>

static enum MHD_Result handler(void *cls, struct MHD_Connection *conn,
                               const char *url, const char *method,
                               const char *version, const char *upload_data,
                               size_t *upload_data_size, void **con_cls)
{
    const char *page = "{\"status\":\"ok\"}";
    struct MHD_Response *response = MHD_create_response_from_buffer(
        strlen(page), (void *)page, MHD_RESPMEM_PERSISTENT);
    MHD_add_response_header(response, "Content-Type", "application/json");

    enum MHD_Result ret = MHD_queue_response(conn, MHD_HTTP_OK, response);
    MHD_destroy_response(response);
    return ret;
}

int main(void) {
    struct MHD_Daemon *d = MHD_start_daemon(
        MHD_USE_INTERNAL_POLLING_THREAD | MHD_USE_EPOLL,
        8080, NULL, NULL, &handler, NULL,
        MHD_OPTION_CONNECTION_LIMIT, 1000,
        MHD_OPTION_CONNECTION_TIMEOUT, 30,
        MHD_OPTION_END);
    if (!d) return 1;
    getchar();
    MHD_stop_daemon(d);
}
```

**One callback for everything.** There's no routing — you `strcmp` the URL yourself, which is the main thing you'll notice coming from any other framework.

The threading model is chosen by flags: `MHD_USE_THREAD_PER_CONNECTION`, an internal thread pool, or `MHD_USE_NO_LISTEN_SOCKET` to drive it from your own [[backend/frameworks/c-sockets/01-the-accept-loop-and-event-loops|event loop]]. That last one is why it embeds well — it can live inside a loop you already have.

**The `con_cls` parameter is the state machine.** The callback is invoked **multiple times per request** — once for headers, then repeatedly as the body streams in. `*con_cls` is your per-connection pointer, and mishandling it is the standard libmicrohttpd bug:

```c
if (*con_cls == NULL) {
    *con_cls = calloc(1, sizeof(request_state_t));   // FIRST call: allocate
    return MHD_YES;                                   // and return, without responding
}
```

You also need a request-completed callback to free it, or you leak per request.

`MHD_RESPMEM_PERSISTENT` says "this buffer outlives the response, don't copy". Use `MHD_RESPMEM_MUST_COPY` for anything on the stack, and `MHD_RESPMEM_MUST_FREE` to hand over ownership. Getting this wrong is a use-after-free on the response path.

---

## Related
<!-- bite: c56a09f9-b676-49a5-9314-5f8afa21cd45 -->
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side, and the honest question of whether to use C at all
- [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] — the part it solves for you
- [[backend/frameworks/ulfius/01-ulfius|Ulfius]] — routing and JSON built on top of libmicrohttpd
- [[backend/frameworks/libmicrohttpd/index|libmicrohttpd]]

## About this lesson
<!-- bite: e3126fb0-22d9-44f1-a81e-5383c915b7eb -->

**Level:** Intermediate. **Covers:** The one-callback model, the `con_cls` state machine, and the response-memory flags that decide who frees what.
