# Next.js

**Scaffold + a routed index.** `[reference]`.

The React framework: routing, rendering strategies, server components, and the build/deploy layer React deliberately doesn't provide.

## The shape

**App Router** (the current model) over the older Pages Router:

```
app/
├── layout.tsx           # shared shell, persists across navigation
├── page.tsx             # the route
├── loading.tsx          # Suspense fallback, automatically
├── error.tsx            # error boundary, automatically
└── products/[id]/page.tsx
```

**File-system routing**, with **Server Components by default** → [[frontend/02-rendering/02-hydration-and-the-server-boundary|the server boundary]].

## The things worth knowing

**Server Components are the default; `"use client"` opts out.** That directive marks a *boundary* — everything imported below it becomes client code, so **one misplaced directive near the root ships your whole tree** → [[frontend/02-rendering/02-hydration-and-the-server-boundary|note 02]].

**Rendering is per route, not per app.** Static, dynamic, or revalidating — and mixing them deliberately is the whole point → [[frontend/02-rendering/01-rendering-strategies|rendering strategies]].

**Server Actions** let a form call a server function directly, with no API route. Convenient, and **they are public HTTP endpoints** — authorise inside them exactly as you would a route handler → [[backend/06-cross-cutting/01-validation-and-dtos|validation]].

**Caching is the hard part.** Next has had several caching layers with defaults that changed across versions, and "why is my data stale" is the most common complaint. **Read your version's caching docs specifically** — this is the area where an out-of-date tutorial will hurt you most.

**`next/image` and `next/font`** solve two real Core Web Vitals problems — layout shift from unsized images, and font-swap flash → [[frontend/07-practices/02-performance|performance]].

## Where the material actually is

**~6,600 words on the App Router and routing model** live in the project notes, against real code:

- [[projects/nextvibe/learning/frontend/01-routing|nextvibe — routing]]
- [[projects/socioboom/learning/frontend/02-nextjs-app-router|socioboom — App Router]]
- [[projects/munakalati/learning/04-frontend/README|munakalati — App Router, ISR and a CMS]] — **Next 16 specifically**: async `params`/`searchParams`, private folders, `typedRoutes` as the fix for untyped `href`

Plus everything in [[frontend/frameworks/react/README|React]]'s index.

## Related
- [[frontend/frameworks/react/README|React]] · [[frontend/frameworks/README|frameworks/]]
- [[frontend/02-rendering/README|rendering]] — the concepts this implements
- [[backend/frameworks/javascript/README|Node backends]] — what runs on the server side
