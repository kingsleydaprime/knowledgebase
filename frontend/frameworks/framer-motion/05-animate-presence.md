---
id: 690d96a0-8e43-4d5c-b34b-956fd47d6561
---

# AnimatePresence: Exit Animations

React unmounts a removed component synchronously — the DOM node is gone before any exit animation could visibly play. `AnimatePresence` solves this by intercepting the unmount: it keeps the outgoing component mounted in the DOM just long enough to run its `exit` animation, then removes it for real once that animation finishes.

## Basic usage
<!-- bite: 2aeee4ab-d877-4bce-9e6f-331581c5fc12 -->

```jsx
import { AnimatePresence, motion } from "framer-motion";

function Modal({ isOpen }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
        />
      )}
    </AnimatePresence>
  );
}
```

**Why `exit` is inert without this wrapper**: `exit` (from [[02-animate-props|animate props]]) is just a prop on `motion.div` — it needs something watching the React tree for removals and delaying the actual unmount. `AnimatePresence` is that watcher; it inspects its direct children on every render and detects when one has been removed from the list, rather than the removed component detecting its own removal (which is impossible — it's already gone).

## Requirement: a stable `key`
<!-- bite: 7a03d305-ddba-4fe6-9322-8c16ac026a17 -->

`AnimatePresence` identifies "this specific child was removed" (as opposed to "this child's content changed") via React's `key` prop — this matters most when swapping between multiple children, not just a single conditional one:

```jsx
<AnimatePresence mode="wait">
  <motion.div key={currentTab} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    {tabContent[currentTab]}
  </motion.div>
</AnimatePresence>
```

Without a distinct `key` per tab, React would treat this as "the same element, content updated" rather than "old element removed, new element added" — and no exit/enter transition would fire at all.

## `mode` prop
<!-- bite: b2d138f7-c28f-4088-8057-41fc04f6bee6 -->

- `"sync"` (default) — exiting and entering elements animate simultaneously (both `exit` and the new element's `initial`→`animate` run at once)
- `"wait"` — the exiting element fully finishes its `exit` animation before the new element starts entering (used above for tab content, where overlapping would look like double content)
- `"popLayout"` — removes the exiting element from document flow immediately (via `position: absolute`) so sibling elements can animate into its space right away, while the exiting element still plays its own exit animation on top — used for animated list removal where remaining items should slide up immediately rather than waiting

## List example (add/remove with exit)
<!-- bite: bab5fb78-fd3b-4492-ab79-4d919429a2e6 -->

```jsx
<AnimatePresence>
  {items.map((item) => (
    <motion.li
      key={item.id}
      layout
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
    >
      {item.label}
    </motion.li>
  ))}
</AnimatePresence>
```

The `layout` prop here is what makes the *remaining* items smoothly slide up to fill the gap when one is removed — that's a separate mechanism covered in [[06-layout-animations|layout animations]].

## Related
<!-- bite: 0fbf5dad-caf1-4207-ba97-c0819dd8817b -->
- [[02-animate-props|animate props]] — what `exit` actually is
- [[04-variants|variants]] — variants commonly carry the `exit` state as well as `hidden`/`visible`
- [[06-layout-animations|layout animations]] — `layout` prop for animating position changes among siblings
