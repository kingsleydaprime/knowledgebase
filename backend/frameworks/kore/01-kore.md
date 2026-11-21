---
id: bd1c1b73-f686-488a-8de6-8dac602d2ff4
---

# Kore

Kore is a full web framework for C, with routing, TLS and WebSockets built in. It is designed around security: its worker processes run with as little power as possible, so a bug in one does limited damage.

## A Kore application
<!-- bite: e6a82400-8af6-477b-b349-aa65be8026de -->

The one that's a genuine framework:

```c
#include <kore/kore.h>
#include <kore/http.h>

int page(struct http_request *req) {
    http_response(req, 200, "hello", 5);
    return KORE_RESULT_OK;
}
```

```text
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

Its distinguishing feature is **privilege separation**: worker processes run as an unprivileged user in a `chroot`, with `seccomp` filters restricting syscalls. If a worker is compromised, the blast radius is deliberately small. That's a serious answer to [[backend/frameworks/c-sockets/02-parsing-http-safely|the security problem]] — not preventing the bug, but containing it.

The single-binary-with-config model is opinionated and doesn't embed into an existing program.

---

## Related
<!-- bite: 9834672d-3a49-451e-88f7-2b0cdf727de4 -->
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side, and the honest question of whether to use C at all
- [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] — the problem privilege separation contains
- [[backend/frameworks/kore/index|Kore]]

## About this lesson
<!-- bite: 7b45ef64-2252-4b8d-a434-2a436faa42a7 -->

**Level:** Intermediate. **Covers:** A Kore handler and config, what the framework gives you, and why privilege separation matters.
