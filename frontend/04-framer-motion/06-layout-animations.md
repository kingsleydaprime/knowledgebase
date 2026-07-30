# Layout Animations: the `layout` prop

Some layout changes can't be expressed as an `animate` prop at all — a flex/grid item changing size and pushing its siblings, an element reparenting, or a list item being removed and its neighbors sliding up to fill the gap. These are consequences of layout recalculation, not a value you can hand to `animate` directly. The `layout` prop tells Framer Motion to detect layout changes between renders and animate the transition automatically.

## Basic usage

```jsx
<motion.div layout className={isExpanded ? "expanded" : "collapsed"} />
```

When the `expanded`/`collapsed` class changes the element's actual box size (via CSS, not inline styles), adding `layout` makes Framer Motion animate smoothly between the old and new size/position instead of an instant jump — without you writing any explicit `animate` values for width/height at all.

## How it works (FLIP, automatically)

This is the same First-Last-Invert-Play technique as GSAP's [[../03-gsap/05-other-plugins|Flip plugin]], but performed automatically on every render instead of manually wrapped around a state change: Framer Motion measures the element's layout before the render (First), measures it again after (Last), computes the transform delta, applies it inverted so nothing visually moves yet (Invert), then animates that transform back to identity (Play) — meaning the *actual* CSS layout property never gets animated frame-by-frame, only a `transform`, which is why this stays performant even for expensive-to-animate properties like `width`/`height`/`flex`.

## `layoutId`: shared element transitions

The more striking use case — animate an element morphing into a *visually different* element elsewhere in the tree (or even a different component), by giving both the same `layoutId`:

```jsx
{items.map((item) => (
  <motion.div key={item.id} layoutId={selectedId === item.id ? "selected-card" : undefined}>
    {item.thumbnail}
  </motion.div>
))}

{selectedId && (
  <motion.div layoutId="selected-card" className="fullscreen-detail">
    {/* full detail view */}
  </motion.div>
)}
```

When the small thumbnail unmounts and the fullscreen detail view mounts with the *same* `layoutId`, Framer Motion treats them as one continuous element and animates the size/position delta between them — the classic "card expands into a fullscreen modal" effect, without any manual measurement code.

## `layout="position"` vs `layout="size"`

By default `layout` animates both position and size changes. Restricting to one axis avoids visual distortion in cases where only one actually matters:

- `layout="position"` — animate position changes only, skip size (useful when an element's content reflows internally and you don't want that internal reflow to stretch/squish visually)
- `layout="size"` — animate size only

## Gotcha: layout animations and non-uniform scaling

Because layout animation works by scaling a transform rather than literally animating `width`/`height`, child elements with non-percentage-based content (text, borders, box-shadows) can visually distort mid-animation as the parent scales. Framer Motion auto-corrects this for most children automatically, but nested `motion` components with their own independent layout animations occasionally need `<LayoutGroup>` to coordinate correctly — worth knowing the name if a nested layout animation looks subtly wrong, rather than assuming the library is broken.

## Related
- [[05-animate-presence|AnimatePresence]] — combining `layout` with add/remove for reflowing lists
- [[../03-gsap/05-other-plugins|GSAP: Flip]] — the manual, imperative version of the same underlying technique
