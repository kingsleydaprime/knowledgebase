# What a Frontend Actually Is

> **[Beginner]** · The four responsibilities, and the constraint that makes this different from every other kind of software.

**A frontend is a program that runs on hardware you don't own, on a network you don't control, for a user who will not read your error message.**

Every difficulty in this domain follows from that sentence.

## The four responsibilities

**1. Render state as something a human can perceive.** Take data and produce pixels, text, and structure a screen reader can navigate.

**2. Capture intent.** Turn taps, clicks, keystrokes and gestures into meaningful operations.

**3. Talk to the backend.** Fetch, mutate, handle latency and failure, and keep a local view of remote state that is always slightly out of date → [[frontend/04-state-and-data/README|state and data]].

**4. Stay responsive while doing all of it.** A frozen interface is a broken one, regardless of correctness.

## The constraint that defines the domain

**You control the code. You control nothing else.**

| | Backend | Frontend |
|---|---|---|
| Hardware | You chose it | **A five-year-old Android on 3G** |
| Runtime version | You pinned it | **Whatever browser they have** |
| Network | Datacentre-local | **Lossy, high-latency, sometimes absent** |
| Concurrency | You set the limits | **One main thread, shared with rendering** |
| Failure | Retry, log, alert | **A human is watching** |
| Code visibility | Private | **Every byte is readable** |

**Two consequences that beginners consistently underestimate:**

**The client is untrusted, by definition.** Validation in the browser is a *usability* feature — instant feedback — and never a security control. Anyone can open dev tools, edit the request, or skip your UI entirely with `curl`. **Every check that matters must exist on the server** → [[backend/01-foundations/01-what-a-backend-is|never trust the client]].

**Nothing is in your secrets.** An API key in frontend code is public, whatever your bundler did to it. `NEXT_PUBLIC_` and `VITE_` prefixes are warnings, not protections → [[backend/06-cross-cutting/02-configuration-and-secrets|config and secrets]].

## One thread does everything

**The single most important mechanical fact about browsers.**

JavaScript execution, layout, paint and user input all share **one main thread**. A 300 ms synchronous loop doesn't just delay your function — it freezes scrolling, blocks clicks, and stops animation.

**Which is why:**
- Long tasks are the main cause of a page that "feels slow" despite loading fast
- Anything heavy belongs in a **Web Worker** or on the server
- `async` doesn't create parallelism — it yields the thread during waits → [[frontend/interview/02-javascript-and-typescript|the event loop]]

**The 16 ms budget applies here too.** At 60 Hz, everything the browser must do between frames has to fit in ~16 ms — the same constraint as [[game-development/01-what-game-development-actually-is|game development]], with less control over the machine.

## The platform is the framework

**Underneath React, Vue, Svelte and everything else is the same platform**, and the platform is the part that doesn't churn:

- **HTML** — structure and semantics. **Not a formatting language**; the tags carry meaning that accessibility tooling depends on
- **CSS** — presentation, the cascade, layout → [[frontend/05-styling/README|styling]]
- **JavaScript** — behaviour
- **The DOM** — the live tree the browser renders, which your code mutates
- **Browser APIs** — fetch, storage, history, observers, workers, media

**Frameworks are strategies for keeping the DOM in sync with your state.** That's genuinely all they are, and knowing it makes learning the next one much faster → [[frontend/02-rendering/README|rendering]].

**The practical advice: invest in the platform, not the framework.** Frameworks have a half-life of a few years; `fetch`, the cascade, event handling and the DOM do not.

## Where the difficulty actually is

**Not in the syntax.** The hard parts, roughly in order:

**State.** Keeping a local copy of remote data correct while it changes underneath you → [[frontend/04-state-and-data/README|04]].

**Asynchrony.** Everything worth doing is async, and races, out-of-order responses and stale closures follow.

**Layout across unknown viewports.** From a 320 px phone to an ultrawide monitor, with text the user may have scaled to 200%.

**Accessibility.** Which is a correctness requirement, not a nicety, and frequently a legal one → [[frontend/06-cross-cutting/README|06]].

**Performance on hardware you'd never choose.** Your laptop is the least representative device you own.

## Related
- [[frontend/02-rendering/README|rendering]] — how state becomes pixels
- [[frontend/README|the frontend course]]
- [[backend/01-foundations/01-what-a-backend-is|what a backend is]] — the other half
- [[foundations/programming-fundamentals/README|programming fundamentals]] — if this is your first code

*Source: [reference] — written Aug 2026.*
