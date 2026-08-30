# munakalati — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from [[projects/munakalati/learning/README|../learning/]]. Munakalati is the Muna Kalati / MunaWorld site — Next.js 16 + Sanity, with **434 blog posts migrated out of Wix**.

**This is the vault's strongest project for content-modelling and data-migration questions**, and its best source of *silent-bug* stories. It is deliberately weak on auth, databases and testing — [[projects/gees-arise/interview/README|gees-arise]] covers the first two, and nothing here covers the third.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = likely to be asked. 🔥🔥 = build your prep around it.

## Files

| File | Covers |
|---|---|
| [[projects/munakalati/interview/01-sanity-and-content-modeling|01-sanity-and-content-modeling]] | Headless CMS trade-offs, schema design, singletons, GROQ, Portable Text, editor experience |
| [[projects/munakalati/interview/02-nextjs-and-rendering|02-nextjs-and-rendering]] | Server Components, ISR and layered caches, fetch waterfalls, route groups, the fallback pattern |
| [[projects/munakalati/interview/03-migration-and-data-integrity|03-migration-and-data-integrity]] ⭐ | Idempotency, deterministic IDs, rich-text conversion, dry runs, verification |
| [[projects/munakalati/interview/04-bugs-and-story|04-bugs-and-story]] ⭐ | The silent bugs, trade-offs defended, what you'd do differently, behavioural |

---

## Before anything else: the 60-second pitch

> Munakalati is the website for Muna Kalati, an organisation building African children's media — a Next.js 16 site on a Sanity CMS. The visible half is a fairly conventional content site: App Router, almost entirely Server Components, ISR, five client components in about ten thousand lines. **The interesting half was the migration.** Their blog was on Wix, 434 posts, and the URLs were already indexed so the slugs had to survive. That meant pulling everything out of an API whose documentation didn't match its responses, converting Wix's rich-text tree into Sanity's Portable Text — two formats that disagree about nesting — and writing the import so it was idempotent, because I ran it about a dozen times. **Almost every bug I hit was silent**: no exception, no failing build, just less data than there should have been, or a page that 404'd for a French title. So the thing I'd actually take from it is that in data work, the defence isn't a debugger — it's asserting things earlier: check the status code, reconcile the count against the source's own total, and never let a fallback render without logging that it fired.

**Why this pitch works.** It states the shape (content site), then immediately redirects to the part with real engineering in it, then lands on a *general* lesson with specifics attached. The last sentence is the one that separates it from "I built a website with a CMS" — it says you noticed a pattern across your own bugs.

**Have ready:** the slug encoding saga (the best story), the 868-post duplication (the crispest lesson), and the one-line `typedRoutes` fix (shows you know what you'd change).

## Related
- [[projects/munakalati/learning/README|../learning/]] — the material these come from
- [[projects/README|all projects]] · [[INTERVIEW|the domain interview banks]]
