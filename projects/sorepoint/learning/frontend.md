# Frontend — Sorepoint

The Next.js dashboard: how the app is scaffolded, and the honest-coverage UI as
it gets built. Teaching *why*, newest topics appended as they come up.

Stack as scaffolded (2026-07-31): **Next.js 16.2.12 (App Router) · React 19.2.4 ·
TypeScript 5 · Tailwind CSS v4**, code under `src/`.

---

## 1. Scaffolding the app — `create-next-app`

We generated the app with:

```bash
npx create-next-app@latest . --ts --app --tailwind --eslint \
  --src-dir --turbopack --import-alias "@/*" --use-npm --disable-git --agents-md
```

Two choices worth remembering:

- **Every option passed as a flag → zero prompts.** `create-next-app` is
  interactive by default. Specifying `--ts --app --tailwind …` for *every*
  question it would ask makes the run fully non-interactive and reproducible —
  the command itself documents exactly what was chosen.
- **`--disable-git`** — the generator normally runs `git init` and makes a first
  commit. We disable that because git is owned by hand on this project; the
  scaffold should produce files, not history.
- **`--src-dir`** puts app code under `src/`, keeping the repo root for config,
  `docs/`, and (later) `supabase/`.

### `@/*` import alias

`--import-alias "@/*"` wires a path alias in `tsconfig.json`:

```jsonc
"paths": { "@/*": ["./src/*"] }
```

So `import { db } from "@/lib/db"` resolves to `src/lib/db` from anywhere, with
no `../../../` climbing. `moduleResolution: "bundler"` (also in the generated
tsconfig) is the modern setting that lets TS resolve imports the way bundlers
actually do.

---

## 2. "This is NOT the Next.js you know" — read the bundled docs first

`--agents-md` generated an `AGENTS.md` at the repo root (and a one-line
`CLAUDE.md` that just does `@AGENTS.md` to include it). Its whole content is a
warning:

> This version has breaking changes — APIs, conventions, and file structure may
> all differ from your training data. Read the relevant guide in
> `node_modules/next/dist/docs/` before writing any code.

That folder really exists and is the **version-exact** documentation for the
Next.js actually installed:

```
node_modules/next/dist/docs/
  01-app/   02-pages/   03-architecture/   04-community/   index.md
```

Why this matters: Next.js ships breaking changes often (e.g. the App Router
itself, the `proxy.ts` rename in 16). Reading `01-app/` from the installed copy
beats reading a blog post or trusting memory — it can't be stale, because it's
literally the code you're running. This is the same "verify against primary
sources" habit, made trivially local.

---

## 3. Tailwind v4 is CSS-first — there is no `tailwind.config.js`

Tailwind v3 configured everything in a JS file (`tailwind.config.js` with a
`content` array, `theme.extend`, etc.). **v4 moved configuration into CSS.** The
generated setup is:

**`postcss.config.mjs`** — Tailwind runs as a PostCSS plugin:

```js
const config = { plugins: { "@tailwindcss/postcss": {} } };
export default config;
```

**`src/app/globals.css`** — one import pulls in all of Tailwind, and a `@theme`
block *is* the config:

```css
@import "tailwindcss";

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: var(--font-geist-sans);
}
```

- `@import "tailwindcss";` replaces the old `@tailwind base; @tailwind
  components; @tailwind utilities;` trio.
- **`@theme`** defines design tokens as CSS custom properties, and Tailwind
  generates matching utilities from them — e.g. `--color-background` makes
  `bg-background` real. So theme customisation happens in CSS next to the tokens,
  not in a separate JS file.
- Content detection (which files to scan for class names) is now **automatic** in
  v4 — no `content: [...]` array to maintain.

Practical upshot for our dashboard: to add a colour for, say, the "flagged"
light, we'll define `--color-flagged` in `@theme` and then use `bg-flagged`
directly, rather than editing a JS config.

---

## See also

- `shell.md` — the move-aside trick used to scaffold into the non-empty repo
- app repo `~/code/spectroniq/sorepoint/DECISIONS.md` — why Next + Supabase, worker-not-route
