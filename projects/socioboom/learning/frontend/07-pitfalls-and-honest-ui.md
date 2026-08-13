# SocioBoom Frontend — Common Pitfalls & Honest UI

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
`learning/frontend/05-data-fetching.md` (the payload bugs that motivate half of this),
`learning/frontend/01-foundations.md` (the hook rules being violated in several pitfalls), and
`learning/backend/08-devops-and-deployment.md` (the backend equivalent — production war stories).

This file covers: the common React and Next.js pitfalls hit while building SocioBoom and how to
avoid each one, and the "honest UI" principle — only offering the user what the backend can
actually deliver, why a disabled-with-explanation control beats a button that fails, and where the
codebase still violates this.

---

## 16. Common Pitfalls and How to Avoid Them

### 1. Forgetting `"use client"` on Components that Use Hooks

**Symptom**: Error like `useState can only be used in a Client Component`

**Cause**: You created a component with `useState`, `useEffect`, or event handlers but forgot `"use client"` at the top.

**Fix**: Every component that uses React hooks or browser APIs needs `"use client"` as its very first line (before any imports).

### 2. Calling `useSearchParams()` Without Suspense

**Symptom**: Build error: `useSearchParams() should be wrapped in a suspense boundary`

**Fix**: In the `app/(app)/.../page.tsx`, wrap the feature component in `<Suspense>`:

```typescript
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import MyFeaturePage from "@/features/my-feature/pages/my-feature.page";

export default function Page() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full" />}>
      <MyFeaturePage />
    </Suspense>
  );
}
```

### 3. Mutating State Directly

**Symptom**: UI does not update after you change state; or updates are inconsistent.

**Cause**: Direct mutation does not trigger re-renders.

```typescript
// WRONG
selectedPlatforms.push("instagram");  // mutates array, no re-render

// RIGHT
setSelectedPlatforms([...selectedPlatforms, "instagram"]);  // new array, triggers re-render
```

Same for objects:

```typescript
// WRONG
user.name = "Alice";  // mutates object
setUser(user);  // React thinks nothing changed (same reference)

// RIGHT
setUser({ ...user, name: "Alice" });  // new object reference
```

### 4. Missing `key` on Mapped Elements

**Symptom**: React console warning `Each child in a list should have a unique "key" prop`; potentially incorrect updates when list items move.

**Fix**: Add `key` with a stable unique value. Prefer IDs over array indices.

```typescript
// WRONG
{posts.map((post) => <PostCard post={post} />)}

// WRONG (index as key — breaks when list is reordered/filtered)
{posts.map((post, i) => <PostCard key={i} post={post} />)}

// RIGHT
{posts.map((post) => <PostCard key={post.id} post={post} />)}
```

### 5. Stale Closures in `useEffect`

**Symptom**: An effect uses a state variable but always sees the initial value.

**Cause**: The effect closure captured the variable at the time the effect was created, not the current value. This happens when a variable is missing from the dependency array.

```typescript
// WRONG: count will always be 0 inside the effect
useEffect(() => {
  const id = setInterval(() => console.log(count), 1000);
  return () => clearInterval(id);
}, []);  // empty deps: count not tracked

// RIGHT
useEffect(() => {
  const id = setInterval(() => console.log(count), 1000);
  return () => clearInterval(id);
}, [count]);  // effect re-runs when count changes
```

### 6. Using `<a>` Instead of `<Link>` for Internal Navigation

**Symptom**: Page fully reloads on navigation instead of client-side transition; no prefetching; layout re-mounts.

**Fix**: Always use `<Link href="...">` from `next/link` for internal routes. Only use `<a>` for external URLs.

### 7. TailwindCSS v4 Config Gotchas

**Symptom**: Custom colors or utilities not generated; `@apply` not working.

The v4 config is in `globals.css`, not `tailwind.config.js`. Custom tokens must be in `@theme {}`. The import order matters:

```css
/* MUST be first */
@import "tailwindcss";

/* Plugins after */
@plugin "tailwindcss-animate";

/* Then your custom variant */
@custom-variant dark (&:is(.dark *));

/* Then :root variables */
:root { ... }

/* Then @theme — wires CSS vars into Tailwind utilities */
@theme { ... }

/* Then @layer base/components/utilities */
@layer base { ... }
```

### 8. Incorrect `@/` Alias Usage

**Symptom**: TypeScript can find the file but you're confused about which path is correct.

Remember: `@/` resolves to `src/shared/` first, then `src/`. So:
- `@/components/ui/button` → `src/shared/components/ui/button` ✓
- `@/features/posts/...` → `src/features/posts/...` ✓ (shared/ has no `features/` folder)
- `@/shared/components/ui/button` → `src/shared/components/ui/button` ✓ (via `src/*`)

Do not create a `src/shared/features/` folder — it would shadow `src/features/` for `@/features/...` imports.

### 9. `process.env.NEXT_PUBLIC_*` at Build Time

**Symptom**: API URL is `undefined` in production.

Next.js only embeds environment variables that start with `NEXT_PUBLIC_` in client-side code. Variables without that prefix are server-only. The API URL pattern in the feature pages:

```typescript
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001/api/v1";
```

In production, set `NEXT_PUBLIC_API_URL` in your hosting environment. The `??` fallback ensures local development works without a `.env` file.

### 10. `asChild` Without a Single Child

**Symptom**: Runtime error or no rendering.

`asChild` requires exactly one child element. Multiple children will throw.

```typescript
// WRONG
<Button asChild>
  <span>one</span>
  <span>two</span>
</Button>

// RIGHT
<Button asChild>
  <Link href="/somewhere">Text</Link>
</Button>
```

---


## 21. Honest UI: Only Offer What the Backend Can Do

The platform selector offered **Instagram**. The publish worker supported twitter, linkedin, reddit, facebook — Instagram fell through to `default: throw 'Publishing not yet supported'`. So a user could select Instagram, write a post, schedule it, and get a silent failure days later. Meanwhile **Reddit**, which the worker fully supported, wasn't offered at all.

The frontend's option lists are a *promise about backend capability*. When they drift, users experience it as your product lying to them. The fix was mechanical — swap Instagram for Reddit in `PlatformSelector`, `AIGeneratePanel`'s meta map, and the connections card — but the lesson is the audit: for every option you render, find the backend `switch` that handles it.

The Reddit swap also demonstrates **conditional required fields** done properly, on both sides:

```tsx
{selectedPlatforms.includes("reddit") && (
  <div className="space-y-2">
    <Label htmlFor="subreddit">Subreddit</Label>
    <Input
      id="subreddit"
      placeholder="e.g. smallbusiness"
      value={subreddit}
      onChange={(e) => setSubreddit(e.target.value.replace(/^r\//, ""))}  // normalize "r/foo" → "foo"
    />
    <p className="text-xs text-muted-foreground">
      The community your Reddit post will be submitted to. The first line of your post becomes the title.
    </p>
  </div>
)}
```

- The field **appears only when relevant** (Reddit selected) instead of sitting permanently in the form as noise.
- Input is **normalized at the edge** — users will type `r/smallbusiness`; strip the prefix rather than erroring on it.
- Client validates before submit (instant toast) **and** the backend validates again (`400` if reddit ∈ platforms and no subreddit) — client validation is UX, server validation is the actual guarantee. Never rely on the first for the second.
- The helper text explains a non-obvious backend behavior (first line becomes the Reddit title) *at the moment it's relevant*, not in documentation nobody reads.

---


