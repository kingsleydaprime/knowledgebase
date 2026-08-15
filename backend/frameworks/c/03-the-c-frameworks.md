# The C Frameworks

**[Intermediate]** — libmicrohttpd, Kore, Ulfius, civetweb: what each is for, and the honest question of when any of them is the right answer.

## The options

| | Character | Model | Use when |
|---|---|---|---|
| **libmicrohttpd** | GNU, small, embeddable, LGPL | pluggable: threads, thread pool, or external event loop | adding HTTP to an existing C program |
| **civetweb** | tiny, MIT, embeddable | thread pool | firmware, desktop apps, game engines |
| **mongoose** | similar; dual-licensed (GPL/commercial) | event loop | embedded, with commercial support |
| **Kore** | a full framework, security-focused | multi-process, privilege separation | a real C web application |
| **Ulfius** | REST-oriented, JSON built in | thread pool (on libmicrohttpd) | REST APIs in C |
| **libevent / libuv** | not HTTP frameworks — event-loop libraries with basic HTTP | event loop | you want the loop, not the framework |

## libmicrohttpd

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

The threading model is chosen by flags: `MHD_USE_THREAD_PER_CONNECTION`, an internal thread pool, or `MHD_USE_NO_LISTEN_SOCKET` to drive it from your own [[backend/frameworks/c/01-the-accept-loop-and-event-loops|event loop]]. That last one is why it embeds well — it can live inside a loop you already have.

**The `con_cls` parameter is the state machine.** The callback is invoked **multiple times per request** — once for headers, then repeatedly as the body streams in. `*con_cls` is your per-connection pointer, and mishandling it is the standard libmicrohttpd bug:

```c
if (*con_cls == NULL) {
    *con_cls = calloc(1, sizeof(request_state_t));   // FIRST call: allocate
    return MHD_YES;                                   // and return, without responding
}
```

You also need a request-completed callback to free it, or you leak per request.

`MHD_RESPMEM_PERSISTENT` says "this buffer outlives the response, don't copy". Use `MHD_RESPMEM_MUST_COPY` for anything on the stack, and `MHD_RESPMEM_MUST_FREE` to hand over ownership. Getting this wrong is a use-after-free on the response path.

## Kore

The one that's a genuine framework:

```c
#include <kore/kore.h>
#include <kore/http.h>

int page(struct http_request *req) {
    http_response(req, 200, "hello", 5);
    return KORE_RESULT_OK;
}
```

```
# conf/app.conf
server tls { bind 0.0.0.0 8888 }
domain * {
    attach tls
    certfile cert/server.pem
    certkey  cert/key.pem
    route / { handler page }
    route /users/[0-9]+ { handler get_user methods get }
}
```

Kore gives you routing with regex parameters, TLS by default, WebSockets, background tasks, pgsql integration, and a build tool (`kodev`).

Its distinguishing feature is **privilege separation**: worker processes run as an unprivileged user in a `chroot`, with `seccomp` filters restricting syscalls. If a worker is compromised, the blast radius is deliberately small. That's a serious answer to [[backend/frameworks/c/02-parsing-http-safely|the security problem]] — not preventing the bug, but containing it.

The single-binary-with-config model is opinionated and doesn't embed into an existing program.

## civetweb

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

## Ulfius

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

## What none of them give you

Compared with every other stack in [[backend/frameworks/README|frameworks/]]:

- **No dependency injection.** Globals or a context pointer threaded manually
- **No ORM.** libpq or the MySQL C API directly, and you write every mapping
- **No serialisation from types.** Jansson or cJSON, field by field. There is no `serde`, no `encoding/json`, no Jackson — because C has no reflection and no derive macros
- **No middleware ecosystem.** The `http.Handler` interoperability that makes [[backend/frameworks/go/README|Go]] compose has no equivalent
- **No standard testing framework.** Unity or greatest, and you wire it up

The JSON gap is the one that bites hardest. Turning a struct into JSON is ~5 lines per field, by hand, forever — and each of those lines is a place to leak memory or overflow a buffer.

## The honest question

**When is C actually the right answer for HTTP?**

**Yes:**
- **An existing C or C++ program needs an HTTP surface** — a device's config page, a game engine's debug server, an instrument's control API. Spawning a Go sidecar to talk to your C program over IPC is often the worse trade
- **The target has no other toolchain** — small embedded, no Rust or Go support
- **Learning.** Writing one from `socket()` up teaches you more about HTTP and about every runtime you use than any framework will → [[BUILD-PLAN|build-your-own-x]]

**No:**
- **A new web service.** You're taking [[languages/04-c/07-memory-management|manual memory management]] onto the most attacker-exposed surface you own, for performance [[languages/02-go/README|Go]] or [[backend/frameworks/rust/README|Rust]] would also give you
- **Anything with a rich domain model.** No generics, no collections, no serialisation — you'll write thousands of lines the other stacks generate
- **A team.** C web code requires discipline that doesn't survive a deadline

> The pattern worth noticing: **C's remaining niche here is embedding, not serving.** When the process is already C for a good reason, adding HTTP to it beats adding a second process. When you're choosing from scratch, essentially nothing recommends it.
>
> And if the reason is "an existing C++ codebase", look at [[backend/frameworks/cpp/README|C++ frameworks]] first — Drogon gives you RAII, a real JSON layer, and coroutines, which removes most of this note's difficulty.

## If you do ship it

1. **Use a real HTTP parser** — llhttp or picohttpparser
2. **Bound every buffer, cap every limit** → [[backend/frameworks/c/02-parsing-http-safely|Parsing HTTP Safely]]
3. **Compile hardened**: `-D_FORTIFY_SOURCE=2 -fstack-protector-strong -fPIE -pie -Wl,-z,relro,-z,now`
4. **Fuzz the parser** with libFuzzer or AFL++
5. **Run the test suite under ASan and UBSan**, in CI
6. **Drop privileges** after `bind()`; `chroot` and `seccomp` if you can
7. **Put a reverse proxy in front** — let nginx terminate TLS and reject malformed requests before they reach you
8. **Consider Kore** specifically for its privilege separation

That last one is worth emphasising: **a hardened reverse proxy in front of your C service is the highest-value single mitigation available.** It handles TLS, absorbs malformed requests, and enforces limits, so your parser sees a much narrower range of input.

---

## Related
- [[backend/frameworks/c/01-the-accept-loop-and-event-loops|The Accept Loop and Event Loops]] — what these wrap
- [[backend/frameworks/c/02-parsing-http-safely|Parsing HTTP Safely]] — the part they solve for you
- [[backend/frameworks/c/04-when-not-to-use-c|When Not to Use C]] — the decision, in full
- [[backend/frameworks/cpp/README|C++ backends]] — usually the better answer for an existing native codebase
- [[backend/frameworks/c/README|C backends]]
