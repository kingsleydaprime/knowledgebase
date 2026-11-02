# 14 — Wheel UI, Wishlist UI & List-vs-Detail Data

*Written 2026-11-02.*

See also: [[projects/nextvibe/learning/frontend/12-rtk-query-and-api-slices|12 — RTK Query & API Slices]],
[[projects/nextvibe/learning/frontend/11-guest-identity-and-conversion|11 — Guest Identity & Conversion]],
backend: [[projects/nextvibe/learning/backend/10-wishlist-and-spin-wheel|10 — Wishlist & Spin the Wheel]]

---

## Part 1 — The postcard carousel bug: list data vs detail data

**Symptom:** postcards with several photos or videos showed one slide. "It used to work."

**Cause:** `postcard-viewer.tsx` built its carousel from the `postcard` **prop**. When the viewer
is opened from the feed, gallery or profile, that prop comes from `GET /postcards`, and the
backend's `findAll` fetches `media: { take: 1 }` because lists only need a thumbnail. The viewer
*also* fetched the full postcard (`useGetPostcardQuery`, polling every 5 s), but only used it for
the author and comments.

**Fix:**
```ts
const media = useMemo(
  () => ((freshData?.media ?? postcard.media ?? []) as PostcardMediaItem[])
          .filter((item) => !!item.mediaUrl),
  [freshData?.media, postcard.media],
);
```
The detail data wins, and the list data is a placeholder until it arrives.

**The general rule:** a list endpoint and a detail endpoint return **different shapes of the same
thing**. Any component that can be opened from both must decide which one it trusts for each
field.

**The trap that made it confusing:** `components/postcard-viewer.tsx` and
`components/postcard-viewer/index.tsx` both exist. An import of `…/postcard-viewer` resolves to
the **file**, not the folder. The folder's `index.tsx` was 1,250 lines of commented-out old
viewer, an easy place to read the wrong code.

---

## Part 2 — Animating to a result the server chose

The wheel must never decide the outcome in the browser. The flow:

1. Tap **Spin**, then `POST /game-rounds/:id/spin`. The response names the slice.
2. Work out a rotation that lands the pointer (at 12 o'clock) on that slice:
   ```ts
   const centre = index * segment + segment / 2;          // degrees clockwise from top
   const jitter = (Math.random() - 0.5) * segment * 0.6;  // cosmetic: not always dead centre
   const target = (360 - centre - jitter + 360) % 360;
   setRotation(cur => cur + FULL_TURNS * 360 + ((target - ((cur % 360) + 360) % 360) + 360) % 360);
   ```
3. A CSS `transition: transform 4500ms cubic-bezier(…)` does the spin, and `onTransitionEnd`
   reveals the result.
4. Only **after** the reveal, refetch the wheel. Refetching earlier would grey out a sold-out slice
   while the wheel is still turning toward it, giving the result away.

`Math.random` is fine here because it only changes *where inside the slice* the wheel stops. The
prize itself was chosen on the server with `crypto.randomInt`.

**Drawing slices in SVG:** each slice is a path `M centre L start-point A r r 0 largeArc 1
end-point Z`, with angles measured clockwise from the top (`rad = (deg − 90)·π/180`). The label
sits in a `<g transform="rotate(mid cx cy)">`, so the text runs along the slice's middle. Font
size steps down as slices narrow (13 → 11 → 9 px).

---

## Part 3 — Resetting a form when its input changes: use `key`, not an effect

The lint rule `react-hooks/set-state-in-effect` flagged this pattern three times:
```ts
useEffect(() => { setName(item.name); setPrice(item.price); }, [item]); // ❌ cascading renders
```
The fix is to **remount** the component with fresh state:
```tsx
<ItemDialog key={editing === null ? "closed" : editing === "new" ? "new" : editing.id} … />
// inside: useState(existing?.name ?? "")  — seeded once per mount
```
I used the same trick for the wishlist settings form, keyed by the server's `updatedAt` so it
re-seeds after a save, and for the contribute dialog, keyed by item id.

---

## Part 4 — Smaller lessons from the wishlist UI

- **Lazy, uncached sensitive fetches.** Bank details use `useLazyGetPaymentDetailsQuery`,
  triggered only when the dialog opens, with `keepUnusedDataFor: 0`, so they don't stay in the
  Redux store.
- **One RTK Query instance, so tags work across features.** A new `"Wishlist"` tag had to be added
  to `baseApi.tagTypes`, because `injectEndpoints` can't add tag types. Toggling the wishlist also
  invalidates the `Event` tag, because the event page shows the tab based on `hasWishlist`.
- **404 as a state, not an error.** The organizer's `GET …/wishlist/manage` returns 404 until the
  wishlist exists, and the dashboard card shows that as the "turn it on" form.
- **Shared helpers go in `shared/`.** Uploading to the CDN was copy-pasted in four places, so the
  fifth went into `shared/api/uploads-api.ts` as `uploadFileToCDN` rather than becoming copy five.
  The others weren't refactored, to stay on task.
- **Don't promise what isn't built.** The thank-you screen said "we'll let you know by email" before
  any email existed. It was removed until the feature is real.

---

## Check yourself

1. Why did the carousel collapse to one slide, and what's the rule that prevents it?
2. Why must the wheel's rotation come from the server's answer, and why refetch only after the reveal?
3. What's wrong with calling `setState` inside `useEffect` to reset a form, and what replaces it?
4. Why are bank details fetched lazily with `keepUnusedDataFor: 0`?
