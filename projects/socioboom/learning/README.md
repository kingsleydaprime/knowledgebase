# SocioBoom — Learning Notes

Moved here from `socioboom/learning/` in the project repo on 2026-08-11, and split from two large
flat files (`backend-learning.md`, `frontend-learning.md`) into domain folders. The originals are
preserved verbatim in `archive/` — nothing was shortened, only reorganized.

SocioBoom is a social-media scheduling and content tool: an Express + Prisma + BullMQ backend
(`socioboom/backend`) and a Next.js 16 App Router frontend (`socioboom/frontend`), publishing to
X/Twitter, LinkedIn, Reddit, Facebook Pages, Instagram and TikTok, with AI-driven review posting
and pain-point discovery.

Note that backend and frontend are **two separate git repositories**; the parent `socioboom/`
folder is not a repo. Architectural decisions live in `socioboom/backend/DECISIONS.md`, not here —
these files teach, that one records why.

## Start here

| File | Covers |
|---|---|
| [00-how-it-fits-together.md](00-how-it-fits-together.md) | The five processes, and one post traced end to end from upload to Instagram |

## Standalone domains

Taught in this project's context. The general-purpose versions of the same material also
live in the main vault (`devops/01-linux/`, `git/`) — these teach, those are
the reference; each file links across.

| File | Covers |
|---|---|
| [01-shell.md](01-shell.md) | `find`/`grep`/`sed`, heredoc quoting, `set -euo pipefail`, verifying a bulk migration, project commands |
| [02-git.md](02-git.md) | Two-repo layout, Conventional Commits, splitting commits (and when you can't), staging flags |

## Backend

| File | Covers |
|---|---|
| [backend/01-foundations.md](backend/01-foundations.md) | Node, Express, TypeScript, bootstrap, tsconfig |
| [backend/02-architecture-and-modules.md](backend/02-architecture-and-modules.md) | The five-file module pattern, middleware chain, full module tour |
| [backend/03-database-prisma.md](backend/03-database-prisma.md) | Prisma 5 schema, relations, migrations |
| [backend/04-auth-and-security.md](backend/04-auth-and-security.md) | Passport JWT, Helmet/CORS/rate limits, secrets, OAuth token refresh |
| [backend/05-queues-and-jobs.md](backend/05-queues-and-jobs.md) | BullMQ + Redis, delayed jobs, retry-without-double-posting |
| [backend/06-ai-and-agents.md](backend/06-ai-and-agents.md) | Provider abstraction, agent loops, structured output, SSRF grounding |
| [backend/07-feature-case-studies.md](backend/07-feature-case-studies.md) | Review Poster, Pain-Point Discovery, Axios patterns |
| [backend/08-devops-and-deployment.md](backend/08-devops-and-deployment.md) | Docker, deployment, production war stories |
| [backend/09-decisions-and-mastery.md](backend/09-decisions-and-mastery.md) | ADRs, rebuild-from-scratch path, expert internals |
| [backend/10-media-and-social-publishing.md](backend/10-media-and-social-publishing.md) | R2 presigned uploads, Facebook Pages tokens, Instagram containers, TikTok's two scopes |
| [backend/11-integration-playbook.md](backend/11-integration-playbook.md) | The ordered process for adding a platform, and the table of every failure and its real cause |

## Frontend

| File | Covers |
|---|---|
| [frontend/01-foundations.md](frontend/01-foundations.md) | TypeScript for React, React fundamentals, JSX |
| [frontend/02-nextjs-app-router.md](frontend/02-nextjs-app-router.md) | App Router, route groups, server vs client, `@/` alias |
| [frontend/03-styling-and-ui.md](frontend/03-styling-and-ui.md) | Tailwind v4, shadcn/ui, dark mode |
| [frontend/04-architecture.md](frontend/04-architecture.md) | `features/` structure, navigation, adding a feature |
| [frontend/05-data-fetching.md](frontend/05-data-fetching.md) | TanStack Query v5, polling background jobs, payload discipline |
| [frontend/06-feature-walkthroughs.md](frontend/06-feature-walkthroughs.md) | Create-Post page, AI features, URL-params wiring |
| [frontend/07-pitfalls-and-honest-ui.md](frontend/07-pitfalls-and-honest-ui.md) | Common pitfalls, only-offer-what-works |
| [frontend/08-rebuild-and-reference.md](frontend/08-rebuild-and-reference.md) | Rebuild path, key file reference, dependency reference |
| [frontend/09-media-uploads.md](frontend/09-media-uploads.md) | Direct-to-R2 uploads, XHR progress, async stale-closure bugs |

## Archive

- [archive/original-flat-backend-learning.md](archive/original-flat-backend-learning.md)
- [archive/original-flat-frontend-learning.md](archive/original-flat-frontend-learning.md)
