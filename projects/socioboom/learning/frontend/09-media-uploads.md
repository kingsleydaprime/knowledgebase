# SocioBoom Frontend — Direct-to-Storage Uploads & Progress UI

Written 2026-08-11 alongside the R2 media pipeline. See also
`learning/backend/10-media-and-social-publishing.md` (the server side and why storage had to
come first), `learning/frontend/05-data-fetching.md` (the "send what you collect" lesson this
is a direct sequel to), and `learning/frontend/07-pitfalls-and-honest-ui.md` (the principle
applied at the end of this file).

This file covers: why `URL.createObjectURL` is a preview tool and not an upload, the
three-step direct upload, why `XMLHttpRequest` beats `fetch` here, the stale-closure bug that
async uploads invite, and slot accounting for in-flight files.

---

## 1. `URL.createObjectURL` Is Not an Upload

The uploader looked complete. It accepted files, showed thumbnails, enforced a per-platform
limit, and produced a `mediaItems` array that got POSTed with the rest of the form.

```ts
const newUrls = toAdd.map((f) => URL.createObjectURL(f));
setMediaItems([...mediaItems, ...newUrls]);
```

`URL.createObjectURL` returns something like `blob:http://localhost:3000/a1b2c3-...`. That
string is **a handle into this tab's memory**. It is not a network resource. It:

- means nothing to any other browser, device, or server
- stops working the moment the tab closes
- cannot be fetched by Instagram's servers, which is the entire point of the feature

So the UI was honest-looking and completely inert. The backend received these strings and
dropped them, because `PostInput` had no media field.

This is the same failure as the "send what you collect" lesson in
`learning/frontend/05-data-fetching.md`, one level worse: there, a collected field wasn't
sent; here, it was sent, but what was collected was never real.

**The tell:** if a value that is supposed to leave the browser was produced *by* the browser
without a network call, it hasn't left the browser.

`createObjectURL` still has a legitimate job here — the instant local thumbnail shown while
the real upload runs. Just remember to `revokeObjectURL` when done, or the file stays pinned
in memory.

---

## 2. The Three-Step Upload

```ts
// 1. Ask our API for permission
const { data: presign } = await axios.post(`${API}/media/presign`, {
  fileName: file.name, mimeType: file.type, sizeBytes: file.size,
});

// 2. Send the bytes to R2 — our server is not in this request at all
xhr.open("PUT", presign.uploadUrl);
xhr.setRequestHeader("Content-Type", file.type);
xhr.send(file);

// 3. Tell our API to verify it landed
const { data: item } = await axios.post(`${API}/media/confirm`, { key: presign.key });
```

The `Content-Type` header in step 2 must match what was declared in step 1 — the backend
baked it into the signature, so a mismatch fails the upload. That's deliberate: it's what
stops a client from declaring a 2MB JPEG and uploading a 2GB video.

Step 3 returns the canonical `MediaItem` (key, public URL, type, size) — that object, not
the local preview, is what goes into the post payload.

---

## 3. `XMLHttpRequest`, in 2026

`fetch` is better than XHR in essentially every respect except one: **it cannot report
upload progress.** `fetch` gives you a promise that settles when the response arrives;
there's no event stream for bytes sent. (`ReadableStream` request bodies exist but aren't
usable for this across browsers.)

For a 300MB video on a phone connection, a spinner with no percentage is a bad experience.
So XHR:

```ts
xhr.upload.onprogress = (e) => {
  if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
};
```

Note `xhr.upload.onprogress`, not `xhr.onprogress` — the latter tracks the *response*
download, which for an upload is a few bytes and always jumps straight to 100%.

Wrapping the XHR in a promise keeps the calling code `async`/`await`-shaped despite the
event-based API — a useful pattern any time you have to fall back to an older browser API.

---

## 4. The Stale Closure That Async Uploads Invite

Uploads resolve one at a time. The obvious code is wrong:

```ts
// ❌ drops results
for (const file of files) {
  const item = await uploadFile(file);
  setMediaItems([...mediaItems, item]);
}
```

`mediaItems` is captured from the render that started the loop. It never updates during
the loop. So after three uploads the array contains only the third — each iteration built
its new array from the same stale snapshot.

```ts
// ✅
setMediaItems((current) => [...current, item]);
```

The functional form receives React's *current* state rather than the closed-over value.

This had a knock-on effect on the component's props. `PostContent` originally took
`setMediaItems: (items: MediaItem[]) => void` — a plain value callback, which can't express
the functional form. The prop type had to widen:

```ts
setMediaItems: React.Dispatch<React.SetStateAction<MediaItem[]>>;
```

Worth noticing generally: **the "simpler" prop type `(v: T) => void` silently forbids
functional updates.** Fine for synchronous handlers, a bug factory for async ones.

### Sequential, not parallel

`Promise.all` over the uploads would be the reflex. It's worse here: several concurrent
video uploads on one connection just split the same bandwidth, so every progress bar crawls
and the total time is unchanged. Sequential means the first file finishes fast and the user
sees real movement.

---

## 5. Slot Accounting With Files In Flight

Platform media limits (Twitter 4, Instagram 10, Reddit 1) have to count files that are
*uploading*, not just uploaded:

```ts
const usedSlots = mediaItems.length + uploading.length;
```

With `mediaItems.length` alone, a user clicking twice quickly during a slow upload queues
more files than the platform allows, and the excess fails at publish time — long after the
mistake, with a confusing error.

Failed uploads stay visible with a Dismiss action rather than vanishing. A file that
silently disappears reads as a bug; a file marked "Failed" reads as information.

---

## 6. Honest UI, Applied Again

The backend now publishes media to Facebook, Instagram, and TikTok. Twitter, LinkedIn, and
Reddit still publish text only — each needs its own chunked upload API, which wasn't in
scope.

The tempting move is to say nothing and let those posts go out without the image. The
principle from `learning/frontend/07-pitfalls-and-honest-ui.md` says otherwise:

```tsx
{mediaItems.length > 0 && droppingMedia.length > 0 && (
  <p>Media isn't supported yet for {droppingMedia.join(", ")} — those posts will publish as text only.</p>
)}
```

Shown at compose time, while the user can still act on it, rather than as a failure
afterwards. Same reasoning drives the requirement notices in `PlatformSelector` ("Needs a
video" under TikTok) and the `no_pages` / `no_instagram_account` OAuth error messages, which
translate an opaque redirect code into the actual thing the user has to go fix.
