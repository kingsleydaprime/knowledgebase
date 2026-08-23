# Components and Composition

> **[Intermediate]** · Where to put the boundary, and the prop-drilling trap that sends people to a global store too early.

## What a component is for

**A component is a boundary**: a name, a contract (props), and something you can reason about without reading its insides. **Same move as a function** → [[foundations/programming-fundamentals/08-functions|functions]].

**The test for a good one, borrowed from the same place: can you describe it without using "and"?** A `UserCard` that also fetches the user, tracks analytics and manages a modal is three components.

## Presentational and container

**The most useful split, whatever you call it:**

- **Presentational** — takes props, renders markup, emits events. **No data fetching, no global state.** Trivially testable, trivially reusable, works in Storybook
- **Container** — fetches, holds state, coordinates. Renders presentational components

**Why it pays: the presentational half is the part you'll reuse, and coupling it to a data source is what stops that.** A `<Table>` that fetches its own rows can only ever show those rows.

**This is the same layering argument as [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|controllers, services, repositories]]** — separate the thing that *decides* from the thing that *displays*.

## Prop drilling, and the wrong reflex

```jsx
<Page user={user}>
  <Layout user={user}>
    <Sidebar user={user}>
      <Profile user={user} />      {/* four levels to use it once */}
```

**The reflex is to reach for a global store. That is usually the wrong first move**, and it's how apps end up with everything in Redux.

**Try these first, in order:**

**1. Composition — pass the element, not the data.**
```jsx
<Layout sidebar={<Profile user={user} />} />
```
`Layout` no longer knows a user exists. **This solves prop drilling more often than people expect, and it's the most underused technique in React.**

**2. Move state down.** If only one subtree needs it, it doesn't belong at the top.

**3. Context — for genuinely ambient values.** Theme, locale, the current user, a client instance. **Things that rarely change** → [[frontend/04-state-and-data/README|state and data]].

**4. A store with selectors** — when many components need fine-grained slices and context would re-render everything.

**Only reach for 4 when 1–3 genuinely don't fit.** Reaching for it first is how a to-do app acquires a global store.

## Organise by feature

```
src/
├── features/
│   ├── checkout/  { components/ hooks/ api/ types.ts }
│   └── profile/   { … }
├── ui/            # generic primitives: Button, Input, Modal
└── lib/           # cross-cutting helpers
```

**Not** a top-level `components/` with 200 files.

**Why: change locality.** A checkout change touches one directory. With type-based folders, every feature change touches five directories, and two people on different features collide constantly → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|by layer vs by feature]].

**Keep business logic out of `ui/`.** A `Button` that knows about orders isn't a primitive. The test: could you copy `ui/` into another product unchanged?

**Enforce the boundaries.** Features shouldn't import each other's internals — ESLint rules (`no-restricted-imports`) make that mechanical rather than a code-review argument → [[foundations/systems-engineering/04-architecture-and-interfaces|interfaces]].

## The patterns worth knowing

**Custom hooks** — the primary reuse mechanism in React. Extract *stateful logic*, not markup.
```jsx
function useDebounced(value, ms) { /* … */ }
```

**Compound components** — related parts sharing implicit state:
```jsx
<Tabs><Tabs.List><Tabs.Tab/></Tabs.List><Tabs.Panel/></Tabs>
```
Flexible layout, no prop explosion.

**Render props / slots** — the consumer supplies the markup, the component supplies the behaviour. Largely superseded by hooks in React; still central in Vue and Svelte.

**Headless components** — behaviour and accessibility with **no styling** (Radix, Headless UI, TanStack Table). **The best of these are also the best accessibility you'll get for free** — focus traps, ARIA, keyboard handling done properly by people who specialise in it → [[frontend/06-cross-cutting/README|accessibility]].

## When to extract

**Not on line count.** Extract when:

- It's used in **three** places *(two is a coincidence)* → [[concepts/interview/02-patterns-code-quality-and-review|the rule of three]]
- It has a name that isn't "wrapper" or "container"
- It has a genuinely independent testable behaviour
- The parent has become hard to read

**Premature extraction produces components with nine props and a boolean that switches behaviour** — which is worse than the duplication it replaced. **Duplication is cheaper than the wrong abstraction.**

## Related
- [[frontend/04-state-and-data/README|state and data]] — where state lives
- [[backend/03-structuring-a-backend/README|structuring a backend]] — the same arguments, other end
- [[frontend/frameworks/react/README|React]] — the specifics
- [[concepts/03-design-patterns/README|design patterns]]

*Source: [reference] — written Aug 2026.*
