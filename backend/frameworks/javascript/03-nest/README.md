# 03 — Nest

Opinionated TypeScript framework: a DI container, modules, decorators, and the [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|controller/service/repository]] layering built in as convention rather than left to you.

1. [[backend/frameworks/javascript/03-nest/01-nestjs-reference|NestJS Reference]] — the comprehensive lookup (6.6k words)

## What to know
- **It's Angular's architecture for the backend** — modules, providers, decorator-based DI.
- **The request pipeline is explicit**: middleware → guards → interceptors → pipes → handler → interceptors → exception filters. That maps almost exactly onto [[backend/01-foundations/03-the-request-lifecycle|the request lifecycle]].
- **Validation decorators are inert without a `ValidationPipe`** — the classic "my validation isn't running" bug. Set `whitelist: true` so clients can't smuggle extra fields.
- **`forwardRef()` is a smell**, not a fix — a circular dependency is a design problem. → [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|DI]]
- It still runs on Express (or Fastify) underneath, so the [[backend/frameworks/javascript/01-node-runtime/README|runtime]] rules all still apply.

## Related
- [[backend/frameworks/javascript/README|JavaScript backends]] · [[projects/arete/learning/backend/01-fundamentals-and-nestjs|arete: NestJS in a real project]] · [[projects/nextvibe/learning/backend/01-core|nextvibe]]
