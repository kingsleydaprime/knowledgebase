---
id: 356e2642-01ba-4366-961d-15a69cd0cf12
---

# Variants: Named States and Orchestration

Passing animation objects inline (`animate={{ opacity: 1 }}`) works for a single element, but breaks down once multiple related elements need to animate together, or the same animation state needs reusing across renders. **Variants** solve this by naming states instead of describing them inline.

## Basic variants
<!-- bite: 301cd698-1c89-40a8-a0b7-d05a3696ff78 -->

```jsx
const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

<motion.div
  variants={cardVariants}
  initial="hidden"
  animate="visible"
/>
```

Same visual result as passing the object directly, but now `cardVariants` is a single named source of truth that can be reused across every element that needs the same "hidden/visible" states — a list of cards, a set of modals, etc.

## Propagation to children
<!-- bite: 76382bc7-2e4b-4dcc-b561-4e273c74dae0 -->

This is the actual reason variants exist, not just naming: if a parent `motion` component has a variant, and its children *also* have `variants` with matching state names but no explicit `animate` prop of their own, the children automatically inherit and animate to whichever state the parent is in:

```jsx
const listVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

<motion.ul variants={listVariants} initial="hidden" animate="visible">
  {items.map((item) => (
    <motion.li key={item.id} variants={itemVariants}>
      {item.label}
    </motion.li>
  ))}
</motion.ul>
```

Only the parent `<motion.ul>` needs `initial`/`animate` set explicitly — every `<motion.li>` picks it up automatically by matching variant key names. This is the declarative equivalent of GSAP's [[frontend/frameworks/gsap/02-tweens-and-easing|stagger]], expressed as parent/child state propagation instead of an explicit selector + stagger config.

## Orchestration props
<!-- bite: 5a4229b3-1f80-42cf-bcc7-a3f15203db0f -->

Set on the *parent's* variant transition, these control how children's animations relate to each other and to the parent's own animation:

```js
transition: {
  staggerChildren: 0.1,   // delay between each child's start
  delayChildren: 0.2,      // wait before the first child starts
  when: "beforeChildren",   // parent finishes before children start (or "afterChildren")
}
```

## Dynamic variants (functions)
<!-- bite: 57b2c579-f692-4154-8d61-9078767f2a2a -->

A variant value can be a function that receives a custom prop, letting per-instance data drive the animation without inline objects:

```jsx
const itemVariants = {
  hidden: { opacity: 0 },
  visible: (i) => ({ opacity: 1, transition: { delay: i * 0.1 } }),
};

{items.map((item, i) => (
  <motion.li key={item.id} custom={i} variants={itemVariants} initial="hidden" animate="visible" />
))}
```

## Related
<!-- bite: ff8c4841-766b-4aa7-aa14-28fe9977976a -->
- [[02-animate-props|animate props]] — the underlying `initial`/`animate` mechanics variants build on
- [[03-gestures|gestures]] — `whileHover="hover"` etc. reference variant names the same way
- [[05-animate-presence|AnimatePresence]] — variants commonly define the `exit` state too
