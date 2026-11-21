---
subject: false
---

# NestJS (TypeScript Backends)

## What NestJS is

**NestJS is a TypeScript framework for building backends on Node.js, and it decides a lot for you.** It comes with modules, decorators and a container that wires your classes together. The controller, service and repository layers that Express leaves to you are built in as convention.

## Lessons so far

1. [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## What to know
- **It's Angular's architecture for the backend** — modules, providers, decorator-based DI.
- **The request pipeline is explicit**: middleware → guards → interceptors → pipes → handler → interceptors → exception filters. That maps almost exactly onto [[backend/01-foundations/03-the-request-lifecycle/index|the request lifecycle]].
- **Validation decorators are inert without a `ValidationPipe`** — the classic "my validation isn't running" bug. Set `whitelist: true` so clients can't smuggle extra fields.
- **`forwardRef()` is a smell**, not a fix — a circular dependency is a design problem. → [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|DI]]
- It still runs on Express (or Fastify) underneath, so the [[backend/frameworks/node/index|Node runtime]] rules all still apply.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the NestJS way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What NestJS is and a first app**: the CLI, `main.ts`, modules, and why it looks like Angular — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
2. **Controllers and routing**: decorators, params, DTOs in and responses out — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
3. **The request pipeline**: middleware → guards → interceptors → pipes → handler → exception filters — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
4. **Modules and structure**: feature modules, what to export, `@Global()`, monorepos — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
5. **Providers and DI**: `@Injectable`, scopes, custom providers, why `forwardRef()` is a smell — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
6. **Validation**: DTOs, class-validator, `ValidationPipe` with `whitelist: true` — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
7. **Errors**: built-in HTTP exceptions, exception filters, Prisma errors to status codes — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
8. **Data**: a Prisma module and service, transactions, database design patterns — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
9. **Auth**: Passport strategies, `AuthGuard`, roles with `Reflector` and custom decorators — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
10. **Security and cross-cutting**: CORS, Helmet, the throttler, versioning, Redis caching, BullMQ queues — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
11. **Testing**: `Test.createTestingModule`, unit, integration and e2e tests — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
12. **Production**: config validation, Swagger, health checks, scaling, microservices — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/node/index|Node.js]] · [[backend/frameworks/express/index|Express]] — what Nest sits on
- [[backend/frameworks/spring-boot/index|Spring Boot]] — the same container-and-opinions trade in Java
- [[projects/arete/learning/backend/01-fundamentals-and-nestjs|arete: NestJS in a real project]] · [[projects/nextvibe/learning/backend/01-core|nextvibe]]

## About this subject

The one lesson so far is a 6,600-word personal reference that covers every stop on the plan. Writing this subject means cutting it into the twelve lessons. Until November 2026 NestJS shared a subject with Node.js and Express.
