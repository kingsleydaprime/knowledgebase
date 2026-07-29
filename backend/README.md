# Backend

**Scaffold — folder structure and planned reading order only, most of the actual notes don't exist yet.** Framework-agnostic concepts already live in [[concepts/01-backend/README|concepts/backend/]] — read that first. This folder is the framework-specific layer on top: shared Node.js fundamentals, then pick a track.

## Structure

1. [[backend/01-nodejs/README|01-nodejs/]] — **[Beginner → Intermediate]** — plain Node.js, framework-agnostic: currently [[01-nodejs/01-node-env-validation|node-env-validation]], [[01-nodejs/02-nodejs-errorhandler|nodejs-errorhandler]]. Planned: the event loop in practice, streams, testing a Node service.
2. [[backend/02-express/README|02-express/]] — **[Intermediate]** — currently [[02-express/01-extending-express-types|extending-express-types]]. Planned: routing/middleware in practice, error-handling middleware, request validation, testing an Express app.
3. [[backend/03-nest/README|03-nest/]] — **[Intermediate → Advanced]** — currently [[03-nest/01-nestjs-reference|nestjs-reference]]. Planned: modules/providers/DI in depth, guards/interceptors/pipes, testing a Nest app.

Other frameworks/languages (Django, Spring, Go, etc.) would slot in as further numbered tracks alongside express/ and nest/ if/when notes get written for them.

## Related
- [[concepts/01-backend/README|backend concepts]] — the framework-agnostic ideas these tracks implement
- [[concepts/03-design-patterns/README|design patterns]]
