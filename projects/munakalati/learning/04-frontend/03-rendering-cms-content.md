# Rendering CMS Content — The Fallback Pattern

**Split from:** the munakalati frontend domain. **See also:** [[projects/munakalati/learning/04-frontend/02-data-fetching-and-caching|02 — data fetching]] · [[projects/munakalati/learning/03-sanity/02-schema-design|sanity/02 — schema design]]

**The defining pattern of this codebase**, and the one most worth understanding, because it's the answer to a problem every CMS-backed rebuild hits: *you have to build the pages before anyone has entered the content.*

---

## The problem

The Muna site was designed and built as static pages first — real copy, real testimonials, real partner logos, all hardcoded in JSX. Sanity came second. That ordering is normal and usually correct: you cannot design a content model for content that doesn't exist yet, and stakeholders approve a *page*, not a schema.

But it leaves a gap. The day the schema ships, the dataset is empty. If the components read only from Sanity, the site is blank until someone types everything into the Studio — and that person is usually not you, and usually not available this week.

## The pattern

Every CMS-backed section carries a hardcoded copy of the content and uses it when Sanity has nothing:

```tsx
// src/components/home/cms/Testimonials.tsx
type TestimonialRender = {
  key: string; quote: string; name: string; role: string;
  photoSrc?: string; countryCode?: string; countryName?: string;
};

const FALLBACK: TestimonialRender[] = [
  { key: "mimi-kalinda",
    quote: "We deserve a future where every African child can see themselves in the stories they read…",
    name: "Mimi Kalinda",
    role: "Group CEO & Co-Founder, Africa Communications Media Group",
    photoSrc: "/images/testimonials/mimi-kalinda.jpg",
    countryCode: "cd", countryName: "DR Congo" },
  // …three more
];

function toRender(sanity: Testimonial[]): TestimonialRender[] {
  return sanity.map((t) => ({
    key: t._id,
    quote: t.quote,
    name: t.name,
    role: t.role,
    photoSrc: t.photo?.asset ? urlFor(t.photo).width(80).height(80).url() : undefined,
    countryCode: t.countryCode,
    countryName: t.countryName,
  }));
}

export default async function Testimonials() {
  const sanity = await client.fetch<Testimonial[]>(testimonialsQuery);
  const testimonials = sanity.length > 0 ? toRender(sanity) : FALLBACK;
  // …render `testimonials`, which is one shape regardless of source
}
```

**Three moving parts, and the middle one is the load-bearing idea:**

1. **A `FALLBACK` constant** — the original hardcoded content, kept.
2. **A render type (`TestimonialRender`) that is neither the Sanity type nor raw JSX props** — a *view model*. The key move: `photoSrc` is a plain string, not a Sanity image object. Fallbacks reference `/images/...` in `public/`; CMS entries go through `urlFor()`. **By the time the JSX sees it, the difference is gone.**
3. **A `toRender()` adapter** — the one place that knows how to turn a Sanity document into the view model.

The result: **the JSX below is written once and knows nothing about where the data came from.** No `{cmsData ? … : hardcoded}` branching scattered through the markup, no two parallel render paths to keep in sync.

The singleton version is the same shape, simpler:

```tsx
// cms/Hero.tsx
const FALLBACK: HeroContent = { badge: "Africa's Children's Media Ecosystem", headlineStart: "Stories that", /* … */ };

const [content, banners] = await Promise.all([
  client.fetch<HeroContent | null>(heroContentQuery),
  client.fetch<HeroBanner[]>(heroBannersQuery),
]);

const c = content ?? FALLBACK;                                    // one object or the other
const panels = banners.length > 0 ? banners.map(/* … */) : FALLBACK_PANELS;
```

**`?? FALLBACK` for a singleton, `.length > 0 ? … : FALLBACK` for a list.** Note the list check is `.length > 0`, not a null check — `client.fetch` on a list query returns `[]`, never `null`, and `[] ?? FALLBACK` gives you `[]`. **An empty array is truthy in JavaScript**, so `banners || FALLBACK_PANELS` would also silently render nothing. That's a real, easy mistake and this code avoids it consistently.

## Why this is the right pattern here

**It decouples two teams.** Frontend work and content entry proceed in parallel, neither blocking the other. For an agency-style build with a client who will populate the CMS later, that's often the difference between shipping and not.

**Every page is always renderable.** No blank sections, no `Cannot read property 'title' of undefined`. If Sanity is down, misconfigured, or pointed at an empty dataset, the site still serves a complete page. That's a genuine resilience property — this site would survive a Sanity outage looking exactly the same as usual.

**Migration is incremental and reversible.** A section moves to the CMS when its content is entered, one at a time, and reverts by deleting the documents.

**It's the demo story.** A fresh clone with no `.env` still renders the whole site. Onboarding a developer doesn't start with "get CMS credentials".

## Why it's also a liability

**Content lives in two places, and only one is obviously authoritative.** An editor updates a testimonial in the Studio; the JSX still contains the old version. Nothing flags the divergence. Six months on, nobody knows whether `FALLBACK` is a safety net or the live content — and the only way to find out is to check whether the dataset has documents of that type.

**The failure mode is silent and specifically bad.** If a GROQ query breaks — a renamed field, a wrong `_type`, a typo — the fetch returns `[]` and the page renders the fallback. **Perfectly, with no error.** You lose the CMS integration and the site looks fine. That's worse than a crash: a crash gets noticed and fixed the same day. This is the pattern's real cost, and it's worth stating baldly — *the safety net hides the fall.*

**It bloats components.** `Testimonials.tsx` is 133 lines and roughly half is `FALLBACK` data. The About page is 590 lines, largely hardcoded team members and board bios.

**It duplicates the content model.** `TestimonialRender` must be kept in step with both the Sanity schema and the JSX. Add a field and there are three places to update, and TypeScript only catches two of them.

## What would make it safer

Two small changes, neither large:

**Log when the fallback fires.**

```tsx
const testimonials = sanity.length > 0 ? toRender(sanity) : (
  console.warn("[cms] testimonials: no documents, using FALLBACK"), FALLBACK
);
```

Server-side, so it lands in the platform logs. **This alone converts the silent failure into a visible one** — the section still renders, and someone watching logs learns the query returned nothing. It's the highest-value line in this note.

**Make it explicit per environment.** A `CMS_STRICT=true` in production that throws instead of falling back, while development keeps the fallback. Then a broken query fails the build rather than shipping stale hardcoded content to users.

And structurally: **move the `FALLBACK` constants into a separate `fallbacks/` module.** Same behaviour, but the duplication becomes visible in the file tree instead of hiding at the top of each component — and a periodic "are these still needed?" pass becomes possible.

## The `cms/` directory, and the duplication it left

```
src/components/home/
├── Hero.tsx              ← original, hardcoded, "use client"
├── Testimonials.tsx      ← original, hardcoded
├── Partners.tsx          ← original, hardcoded, "use client"
├── …
└── cms/
    ├── Hero.tsx          ← CMS version, Server Component, with fallback
    ├── Testimonials.tsx  ← CMS version
    ├── Partners.tsx      ← CMS version
    └── …
```

**Nine components exist twice.** The homepage imports the `cms/` ones:

```tsx
import Hero from "@/components/home/cms/Hero";
import Testimonials from "@/components/home/cms/Testimonials";
import BlogPreview from "@/components/home/BlogPreview";   // never had a cms/ twin
```

This is a **migration scaffold that outlived its migration.** Keeping the original alongside the new one is a sensible way to do a risky conversion — you can diff them, and revert by changing an import. But once the CMS versions are the ones in use, the originals are dead code that:

- **Look live.** Nothing in `home/Hero.tsx` says "superseded". A developer opening it and editing the headline changes nothing on the site, and that's a genuinely confusing half-hour.
- **Get half-maintained.** Some fixes landed in both, some in one. Commit `3442c85` fixed `/donate` → `/engage/donate` in `home/DonateCTA.tsx` — which is fine, since `DonateCTA` has no CMS twin — but the same class of link fix in a duplicated component would need doing twice.
- **Rot silently.** They still compile, so nothing complains.

**The cleanup is: delete the originals whose `cms/` twin is in use, and drop the `cms/` prefix** — the distinction stopped being meaningful once every section came from the CMS. Deferred by the handover, and worth flagging as the first thing to do if anyone picks the project up.

**The general lesson** — one that generalises well past this repo: *a scaffold needs a demolition date.* "Keep the old one around during the migration" is right; "during" has to end. If you can't delete it the day the switch flips, put the deletion in the tracker with the migration itself.

## Related
- [[projects/munakalati/learning/04-frontend/01-app-router-structure|01 — App Router structure]]
- [[projects/munakalati/learning/03-sanity/02-schema-design|sanity/02 — the schemas behind these]]
- [[frontend/03-structuring-a-frontend/01-components-and-composition|components and composition]]
- [[concepts/04-best-practices/01-clean-code|clean code]] — dead code that still compiles
