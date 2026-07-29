# HTTP Servers — Request Lifecycle, Routing, Middleware

Every backend framework — Express, NestJS, Django, Spring — is ultimately doing the same thing underneath its own syntax: accepting an HTTP connection, parsing a request, running it through some chain of handlers, and producing a response. Understanding that shared shape is what makes a new framework's docs read as "the same thing, different syntax" instead of a wall of unfamiliar concepts.

## The request lifecycle

```
1. TCP connection accepted
2. Raw bytes parsed into an HTTP request (method, path, headers, body)
3. Routing: match the path + method to a registered handler
4. Middleware chain runs, in order, before the handler
5. Handler executes, produces a response
6. Middleware chain can also run *after* (response-side), in reverse
7. Response serialized back to bytes, sent over the same connection
```

Every framework-specific concept — Express's `app.use()`, NestJS's guards/interceptors, Django's middleware classes — is a variation on step 4: injecting logic into this chain without the handler itself needing to know it's happening.

## Routing — matching a request to code

A router maps `(HTTP method, path pattern)` pairs to handler functions.

```javascript
// framework-agnostic shape — this is what every router does underneath its syntax
router.get("/users/:id", (req, res) => { /* req.params.id is extracted from the path */ });
router.post("/users", (req, res) => { /* handle creation */ });
```

Path parameters (`:id`), query parameters (`?sort=name`), and the request body are three distinct sources of input a handler reads from — conflating them (expecting a value in the body that was actually sent as a query parameter) is a common early mistake when working with a new framework's request object.

## Middleware — the chain, not just a single step

Middleware is a function that runs *before* (or, in response-side middleware, after) the actual handler, with the ability to modify the request/response, short-circuit the chain entirely (returning an error response without ever reaching the handler), or pass control forward.

```javascript
function authMiddleware(req, res, next) {
  const token = req.headers.authorization;
  if (!isValid(token)) {
    return res.status(401).json({ error: "Unauthorized" });   // chain stops here
  }
  req.user = decodeToken(token);
  next();   // pass control to the next middleware / the actual handler
}
```

This is the mechanism behind cross-cutting concerns that shouldn't be duplicated in every handler: authentication (see [[05-authentication-flows|authentication-flows]]), logging, CORS handling (see [[04-security-headers-and-same-origin-policy|security-headers-and-same-origin-policy]]), body parsing, rate limiting. Middleware order matters — auth middleware needs to run before a handler that assumes `req.user` already exists, and get that order wrong and you get confusing bugs where a value "isn't there yet."

## Synchronous handling vs the event loop (Node specifically)

Node.js handles many concurrent requests on a single thread via an event loop — a handler that blocks (a long synchronous computation) stalls every other in-flight request on that same process, not just its own. This is why Node backend code leans so heavily on async/await and non-blocking I/O — a slow database query awaited asynchronously lets the event loop serve other requests while waiting, where a blocking equivalent would freeze the whole process. Frameworks in other languages (Django/Python with WSGI workers, Spring/Java with a thread pool) solve the same concurrency problem with a different underlying model — multiple OS threads/processes instead of one event loop — which is worth knowing exists as a real architectural difference, not just a syntax one, when comparing "how many requests can this framework handle at once."

## Gotchas

- Forgetting to call `next()` in a middleware function (or forgetting to send a response) leaves a request hanging indefinitely — a common, confusing bug for anyone new to a middleware-based framework.
- Middleware registered in the wrong order silently produces bugs that look unrelated to ordering (e.g. a body-parsing middleware registered *after* a middleware that already needs to read the body) — check registration order first when a request handler receives unexpectedly empty/malformed data.
- See `backend/express/`, `backend/nest/`, and `backend/nodejs/` in this vault for framework-specific implementations of these same ideas.

## Related
- [[05-authentication-flows|authentication-flows]]
- [[03-apis|apis]]
- [[02-backend-best-practices|backend-best-practices]]
