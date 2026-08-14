# 02 — Express

Minimal and unopinionated: a router, a middleware chain, and nothing else. You supply the [[backend/03-structuring-a-backend/README|structure]] — which is freedom if you know what you're building and a mess if you don't.

1. [[backend/frameworks/javascript/02-express/01-extending-express-types|Extending Express Types]] — typing `req.user` and friends in TypeScript

## What to know
- **Middleware is the whole model** — `(req, res, next)`, order matters, and the error handler takes four arguments (`err, req, res, next`) or it silently isn't one.
- **Async errors are not caught automatically** in Express 4 — an async handler that rejects hangs the request unless you wrap it or use Express 5.
- **It gives you no structure.** Impose [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|feature folders]] and [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|a composition root]] yourself, early.

## Related
- [[backend/frameworks/javascript/README|JavaScript backends]] · [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]]
