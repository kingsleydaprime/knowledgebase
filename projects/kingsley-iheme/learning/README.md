# kingsley-iheme — Learning Log

Portfolio/marketing site for Kingsley Iheme (ghostwriter, author, pastor, relationship & marriage counselor). Built solo, mid-2026. Repo lives at `~/code/spectroniq/projects/kingsley-iheme`; these notes live here so study material doesn't ship inside a client-facing deliverable.

**Stack:** Next.js 16 (App Router) · React 19 · Tailwind CSS v4 · Sanity v6 (embedded Studio) · Resend · Cal.com embed · bun · Vercel.

**What makes it worth writing up.** On paper it's "a brochure site" — the kind of project that looks like it teaches nothing. It actually carries four things the vault had thin or no coverage of:

1. **Next.js 16 specifically** — not Next 13/14 from memory. `params` is a Promise, route groups shape the layout tree, and the file-convention metadata API (`sitemap.ts`, `robots.ts`, `opengraph-image.tsx`) does work that used to need libraries.
2. **Sanity** — a *second* instance, alongside [[projects/munakalati/learning/03-sanity/README|munakalati's five-note Sanity course]]. The general folder `frontend/frameworks/sanity/` is still an empty stub, so both instances live only in `projects/`. This one is smaller and differently shaped: a discriminated-union content model, conditional validation, and a graceful-degradation fetch wrapper. Where the two agree independently — API version as a date, `required()` being a form check rather than a constraint, `defined()` in queries — treat that as confirmation, not duplication.
3. **Graceful degradation as an architectural stance** — every third-party integration (CMS, booking, email) is env-gated so the site renders correctly with *nothing* connected. That's a handover requirement, not a nicety, and it changes how you write every data-fetching function.
4. **Tailwind v4's CSS-first config** — no `tailwind.config.js` at all. `@theme` in CSS replaces it, and almost every Tailwind tutorial predates this.

## Read in this order

| # | File | Covers |
|---|---|---|
| 01 | [[projects/kingsley-iheme/learning/01-frontend\|Frontend]] | Next 16 App Router, route groups, the RSC boundary, Tailwind v4 `@theme`, `next/font`, the metadata API, `ImageResponse`, motion, client-side list filtering |
| 02 | [[projects/kingsley-iheme/learning/02-sanity\|Sanity]] | Schema design, the native/external discriminated union, conditional validation, GROQ, Portable Text, image URL builder, embedded Studio, ISR |
| 03 | [[projects/kingsley-iheme/learning/03-backend-api\|Backend / API]] | The `/api/contact` route handler, hand-rolled validation, Resend, `replyTo` as a routing trick, status-code design as a client contract |
| 04 | [[projects/kingsley-iheme/learning/04-devops\|DevOps / Deploy]] | Env var strategy, `NEXT_PUBLIC_` semantics and its security edge, the `.gitignore` bug found here, bun, `ignoreScripts`/`trustedDependencies`, Vercel |

## Bugs and smells found while writing these notes

Kept here rather than buried, because postmortems are the part worth rereading. Each is explained in full in the file named.

| Finding | Severity | Where |
|---|---|---|
| `.env.local.example` is gitignored and untracked, but the README tells you to copy it — a fresh clone can't follow its own setup instructions | **Real bug** | [[projects/kingsley-iheme/learning/04-devops\|04-devops]] |
| `styled-components` is a dependency, imported nowhere — dead weight in the bundle graph and the lockfile | Smell | [[projects/kingsley-iheme/learning/04-devops\|04-devops]] |
| Two near-identical env example files (`.env.example`, `.env.local.example`) that disagree on one value | Smell | [[projects/kingsley-iheme/learning/04-devops\|04-devops]] |
| `sanityFetch` swallows every error with a bare `catch {}` — a CMS outage is indistinguishable from an empty CMS | Trade-off, deliberate | [[projects/kingsley-iheme/learning/02-sanity\|02-sanity]] |
| `POST_BY_SLUG_QUERY` doesn't filter to `postType == "native"`, so `/blog/<external-slug>` renders a bodiless page instead of 404ing | Minor bug | [[projects/kingsley-iheme/learning/02-sanity\|02-sanity]] |
| Copy bugs in `cal-sessions.ts` — "Basic Invidiual Session", and a description copy-pasted from the intro call | Copy | [[projects/kingsley-iheme/learning/01-frontend\|01-frontend]] |

## Related in the vault

- [[frontend/frameworks/next/README|frontend/frameworks/next]] · [[frontend/frameworks/react/README|react]] — the general course this project's frontend note instantiates
- [[frontend/README|frontend]] — Tailwind lives here; this project is the vault's Tailwind **v4** instance
- [[projects/munakalati/learning/03-sanity/README|munakalati — Sanity]] — the deeper Sanity course (11k words); read it alongside [[projects/kingsley-iheme/learning/02-sanity|02]]
- [[backend/02-api-design/README|backend/api-design]] — the status-code contract in 03 is that material, applied
- [[devops/09-secret-management/README|devops/secret-management]] — the env-var half of 04
- [[cybersecurity/04-web-security/README|web security]] — `NEXT_PUBLIC_` and what it means to ship a variable to the browser
