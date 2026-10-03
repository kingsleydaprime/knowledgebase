# 05 — Maps and structured data

Written while putting the two office addresses (Philadelphia and Accra) on the
contact page, with a map for each.

Two halves that turn out to be the same problem. **Maps**: how a web map is
actually built out of square images, and how to render one ahead of time
instead of loading somebody else's JavaScript. **Structured data**: how to
publish the same address in a form a machine can read, without storing it
twice.

See also: [03-frontend.md](03-frontend.md) (the YouTube facade — the same
trade, made earlier), [02-content-modelling.md](02-content-modelling.md)
(Zod as the content boundary).

---

## 1. The embed trade — the facade argument again

A Google Maps `<iframe>` costs roughly **a megabyte of third-party JavaScript
per map** and sets cookies **on load**, before the visitor has agreed to
anything. Two offices on one page means two of those.

This is the same shape as the YouTube facade in `03-frontend.md §4`, but the
conclusion is different, and the difference is worth understanding.

| | YouTube | Map |
|---|---|---|
| What the embed adds | playing the video — irreplaceable | panning and zooming |
| Can a static image substitute? | no, a still is not a video | **yes, almost entirely** |
| Where does the user actually want to end up? | on your page | in their own maps app, getting directions |

So the video gets a *facade* (static until clicked, then the real embed), and
the map gets **no embed at all** — a flat image plus a link out. Once you
notice that "pan the map" is a worse version of "open this in Google Maps",
the interactive map stops earning its megabyte.

The general principle: **an interaction has to buy something the static version
cannot.** Ask what the user is actually trying to do, not what the widget can do.

---

## 2. How a web map is built: tiles

Every slippy map — Google, OSM, Mapbox, all of them — is the same structure:

- The world is drawn at a set of **zoom levels**, `z = 0, 1, 2, …`
- At zoom `z` the world is a grid of `2^z x 2^z` square images, each **256x256 px**
- So zoom 0 is one tile for the whole planet; zoom 1 is 2x2; zoom 17 is
  131072 x 131072 tiles

Each tile has a URL of the form `/{z}/{x}/{y}.png`, where `x` counts east from
the left edge and `y` counts **south** from the top:

```
https://tile.openstreetmap.org/17/38169/49644.png
```

Fetch the few tiles that cover your area, paste them side by side, crop. That
is the whole of "generate a static map".

---

## 3. Web Mercator: lat/lon → pixels

To know *which* tiles, you project the coordinates. Web Mercator (EPSG:3857)
is what every web map uses:

```python
def project(lat, lon, zoom):
    n = 256 * 2**zoom          # width of the whole world, in pixels, at this zoom
    x = (lon + 180.0) / 360.0 * n
    rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(rad) + 1 / math.cos(rad)) / math.pi) / 2.0 * n
    return x, y
```

**Longitude is the easy half.** It is linear: -180° is the left edge, +180° the
right, so you just rescale into `0..n`.

**Latitude is not linear, and the `log(tan(...))` is why.** Mercator is a
*conformal* projection: it preserves angles and local shapes, which is what
makes it usable for navigation — a street corner looks like a street corner
anywhere on the map. The price is that vertical distance has to stretch more
and more as you move away from the equator, exactly in step with how longitude
is already being stretched there. That stretching factor works out to
`1/cos(lat)`, and integrating it gives the `ln(tan φ + sec φ)` you see above.

Two consequences worth knowing:

- **The poles are infinitely far away.** `tan(90°)` diverges, so Web Mercator is
  cut off around ±85.05°, which makes the world a square and the tile grid
  tidy.
- **Greenland looks the size of Africa.** Famously. That is this stretching,
  not a mistake.

Sanity check that the formula is right: at `lat = 0`, `tan(0) + sec(0) = 1`,
`ln(1) = 0`, so `y = n/2` — the equator sits exactly halfway down. Good.

---

## 4. Stitching: the tile window and the crop offset

Given a centre point and a target size, the arithmetic:

```python
cx, cy = project(lat, lon, ZOOM)          # global pixel coords of the centre
left, top = cx - WIDTH / 2, cy - HEIGHT / 2   # top-left of the crop we want

x0, y0 = math.floor(left / TILE), math.floor(top / TILE)      # first tile
x1 = math.floor((left + WIDTH  - 1) / TILE)                   # last tile
y1 = math.floor((top  + HEIGHT - 1) / TILE)
```

Fetch every tile in that rectangle onto one canvas, then crop out the part you
asked for:

```python
ox, oy = int(left - x0 * TILE), int(top - y0 * TILE)   # how far into the first tile
crop = canvas.crop((ox, oy, ox + WIDTH, oy + HEIGHT))
```

The `- 1` in the last-tile calculation is the off-by-one to watch. If the crop
ends exactly on a tile boundary, `left + WIDTH` is already the *next* tile's
first pixel, and without the `- 1` you fetch a whole column you never use.

**Be a good neighbour.** OSM's tile servers are donated infrastructure. Their
usage policy requires a `User-Agent` identifying your application with a way to
contact you, and forbids bulk downloading. A handful of tiles, once, with a
`time.sleep(0.25)` between them, is fine. Generating a thousand map images on
demand is not — that is when you pay for MapTiler or Mapbox.

---

## 5. The density trade-off, and why it has no clean answer

A 2x (retina) screen wants twice as many pixels as CSS pixels. Images normally
solve this by shipping a bigger file. Maps cannot, quite:

- Fetching **`@2x` tiles** (512px covering the same ground) is the correct fix —
  the provider re-renders labels at double size. Not every tile server offers
  them; OSM's standard layer does not.
- **Rendering one zoom level deeper and displaying it at half size** gets you
  the pixel density, but the *labels* are drawn at their normal size and then
  halved. Crisp on a 2x screen, too small on a 1x one.

There is no free version. Pick knowing which you are trading:

| | Sharp on retina | Labels readable at 1x |
|---|---|---|
| `@2x` tiles | yes | yes |
| zoom+1, displayed at half | yes | no |
| 1x at display size | no | yes |

A related trap: **a provider that returns a stub tile looks like a provider
that works.** Carto's CDN answered `200` for every style and coordinate — always
exactly 2049 bytes. Identical sizes across *different* content is the tell. See
`01-shell.md §4` for the general habit of checking what a download actually
contains rather than whether it succeeded.

---

## 6. Keep the pin and the attribution out of the pixels

Two things that could have been drawn into the PNG, and should not be.

**The pin** is an inline SVG positioned over the image:

```tsx
<svg className="absolute left-1/2 top-1/2 h-9 w-auto -translate-x-1/2 -translate-y-full">
```

`-translate-x-1/2` centres it horizontally. `-translate-y-full` — not
`-translate-y-1/2` — pulls it up by its **whole height**, so the *tip* of the
teardrop lands on the centre point. A pin whose middle is on the target is
pointing at the wrong place, by half its own height. This is the single most
common map-marker bug.

Keeping it in the DOM means it stays crisp at any size, uses the brand colour
token, and can be restyled without regenerating the image.

**The attribution** is required by the tile licence — OSM's tiles are
CC-BY-SA, and the data is ODbL. It stays live text:

```tsx
<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>
```

A link in markup is selectable, followable and survives the image being
re-cropped; the same words flattened into a corner of the PNG are a picture of
a credit. Licence conditions are not decoration — if you cannot comply, you
cannot use the tiles.

---

## 7. Store the parts, derive the display

The address had to appear in three places: the contact card, the footer, and
the structured data. The instinct is to store what you want to show:

```jsonc
// Don't
{ "city": "Philadelphia", "lines": ["230 S Broad Street", "17th Floor", "..."] }
```

That fails the moment something needs the *parts*. `schema.org/PostalAddress`
wants `streetAddress`, `addressLocality`, `addressRegion` and `postalCode`
separately — so you would end up storing the parts **as well** as the display
string. Two representations of one fact, and the one nobody remembers to edit
is the one that goes stale.

Store the parts; derive the display:

```ts
export function formatAddress(address: PostalAddress): string[] {
  const locality = [address.locality, address.region].filter(Boolean).join(", ");
  const withPostcode = [locality, address.postalCode].filter(Boolean).join(" ");
  return [...address.street, withPostcode, address.country];
}
```

`filter(Boolean)` is doing real work: Accra has neither a state nor a postcode,
so the line collapses to `"Accra"` instead of `"Accra,  "`. **Write the
formatter against the address that has the fewest fields, not the one you
happen to be looking at.** US-shaped assumptions — there is always a state,
there is always a ZIP — are one of the most reliable sources of wrong output in
international software.

The deeper rule: **one fact, one place.** Everything else is a view of it.

---

## 8. JSON-LD: the address a machine can read

Visible text tells a crawler nothing structured. JSON-LD does:

```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
/>
```

Three things in that snippet are deliberate.

**`dangerouslySetInnerHTML` is unavoidable.** React escapes text by default, so
rendering the JSON as a child would produce `&quot;` everywhere and the crawler
would parse nothing.

**The `<` → `<` replacement is the security control.** Without it, any
string in your data containing `</script>` closes the tag early, and the rest
of the JSON is parsed as HTML — a script-injection hole fed by your own CMS.
`<` is identical to a JSON parser and inert to an HTML one. Next's own
docs call this out; do not skip it because "the data is ours". Today it is.

**A plain `<script>`, not `next/script`.** `next/script` exists to schedule the
*execution* of JavaScript. This is data; there is nothing to schedule.

For two real offices, the shape is `Organization` with a `location` **array**:

```ts
location: site.offices.map((office) => ({
  "@type": "Place",
  address: {
    "@type": "PostalAddress",
    streetAddress: office.address.street.join(", "),
    addressLocality: office.address.locality,
    ...(office.address.region ? { addressRegion: office.address.region } : {}),
    addressCountry: office.address.countryCode,   // "US", not "United States"
  },
  geo: { "@type": "GeoCoordinates", latitude: ..., longitude: ... },
}))
```

- **Spread-an-empty-object** (`...(x ? { k: x } : {})`) omits a key rather than
  sending `""`. An empty string is a claim that the field applies and the value
  is blank; absence is the truth.
- **`addressCountry` takes the ISO 3166-1 alpha-2 code.** The display name is
  for humans, the code is for the consumer. Storing both is why the content
  model has `country` *and* `countryCode`.
- **Never flatten two offices into one address.** Whichever one loses becomes a
  published falsehood.

Validate with Google's [Rich Results Test](https://search.google.com/test/rich-results)
or the [Schema Markup Validator](https://validator.schema.org/).

---

## 9. NAP consistency — why the footer matters

"NAP" is the local-SEO term for **Name, Address, Phone**. Search engines decide
whether two mentions of a business are the same business partly by whether
these strings match *exactly* across the web.

"230 S Broad St" and "230 South Broad Street, 17th Fl" can read as two
different listings, splitting the ranking signal between them. This is the
business reason behind §7's engineering reason: deriving every rendering from
one stored record makes inconsistency structurally impossible, rather than
something somebody has to remember.

---

## 10. Small things worth keeping

- **`new URL(path, origin).toString()`** turns `/images/logo.jpeg` into an
  absolute URL. Crawlers have no page context to resolve a relative path
  against, so structured data and OG tags both need absolute URLs.
- **`metadataBase`** in Next's root `generateMetadata` is the same problem for
  Open Graph images. Unset, Next resolves them against `http://localhost:3000`
  and every share card points at a machine nobody can reach. It warns at build
  time — read the warnings.
- **`<address>` is italic by default** in every browser, which reads as emphasis
  nobody intended. `not-italic` puts it back. Use the element for the
  semantics, then fix the styling; do not reach for a `<div>` to dodge a font.
- **Two identical "Get directions" links on one page** are useless to a screen
  reader. Give each an accessible name that says *which*: a visible
  `aria-hidden` label plus an `sr-only` span carrying the full phrase.
- **Quantizing map PNGs** to 256 colours is visually lossless and cuts the file
  by roughly two thirds — map art is flat fills and thin lines. Turn dithering
  **off**; it adds noise that defeats the compression it is supposed to help.

---

## Outstanding — promote to the general vault

- Web Mercator and the tile scheme (§2–§4) is general cartography/geo
  knowledge, not project-specific. Candidate: a `geo/` folder in the vault.
- The JSON-LD XSS escape (§8) belongs with general web-security notes —
  it is the same class as any "inject data into a script tag" problem.
- NAP consistency (§9) belongs in a general SEO folder if one is started.
