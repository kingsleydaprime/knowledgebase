---
id: 7b917207-77ea-4a55-b536-5cdb0b9f989a
---

# What Astronomy Is

Astronomy is unusual among sciences in one structural way: **you cannot experiment on your subject.** You cannot heat a star, collide two galaxies, or rerun the Big Bang. **Everything is inference from light that has already arrived.**

That single constraint shapes the whole discipline — its instruments, its statistics, and its characteristic humility about error bars.

## The neighbouring words
<!-- bite: d0845078-4465-42c2-bc3a-69f286b67401 -->

Confused constantly, and worth separating precisely:

| | Is |
|---|---|
| **Astronomy** | Observing and explaining objects and phenomena beyond Earth's atmosphere |
| **Astrophysics** | The physics *of* those objects. In practice the terms are now used interchangeably |
| **Cosmology** | The universe as a whole — its origin, structure and fate |
| **Planetary science** | Planets, moons, asteroids; overlaps geology and atmospheric science |
| **Astrobiology** | Whether life exists elsewhere, and how we'd know |
| **Space science / engineering** | Getting instruments and people *there* → [[astronomy/08-spaceflight-and-exploration\|note 08]] |
| **Astrology** | **Not a science.** Covered honestly in [[astronomy/09-astrology-honestly\|note 09]] |

**The astronomy/astrophysics distinction has effectively dissolved.** Historically astronomy was *where things are* and astrophysics *what they're made of and why they shine*; since spectroscopy that separation stopped making sense.

**Astrology is a separate matter entirely**, and this folder handles it as history and psychology rather than as a working system. [[astronomy/09-astrology-honestly|Note 09]] explains what it is, why it and astronomy share a root, and what the evidence actually says.

## Everything comes from light
<!-- bite: 2436417b-9176-4f50-93d9-7686d7879f2e -->

Almost all astronomical knowledge arrives as **electromagnetic radiation**. From that alone you can extract a remarkable amount:

- **Brightness** → distance, if you know the intrinsic luminosity
- **Colour / spectrum** → **temperature, chemical composition, density, magnetic field**
- **Spectral line shifts** → velocity toward or away from us (Doppler), and **expansion of the universe** (redshift)
- **Variation over time** → orbits, pulsation, explosions, transiting planets
- **Polarisation** → magnetic fields, scattering, dust

**Spectroscopy is the single most important technique in the field** → [[astronomy/03-light-and-instruments|note 03]]. Splitting light into its spectrum turns a point of light into a physics experiment: you learn what a star is made of without going there.

**The four non-light messengers**, and each opened a genuinely new window:

- **Cosmic rays** — charged particles; arrival directions scrambled by magnetic fields
- **Neutrinos** — barely interact, so they escape from places light cannot, like a star's core
- **Gravitational waves** — ripples in spacetime, first detected 2015 → [[astronomy/06-gravity-and-relativity|note 06]]
- **Meteorites and sample return** — the only material we hold in our hands

**"Multi-messenger astronomy"** is observing one event across several of these. In 2017 a neutron-star merger was seen in gravitational waves *and* across the electromagnetic spectrum — which confirmed that such mergers produce heavy elements like gold, and did it in a single night.

## The scales
<!-- bite: 8cb905b5-dcee-4759-947c-505aec3da16a -->

Astronomy's numbers defeat intuition, so it uses its own units:

| Unit | Is | Roughly |
|---|---|---|
| **AU** (astronomical unit) | Earth–Sun distance | 150 million km |
| **Light-year** | Distance light travels in a year | 9.46 × 10¹² km |
| **Parsec** | The professional unit | 3.26 light-years |

**And the ladder:**

- Earth to the Moon — **1.3 light-seconds**
- Earth to the Sun — **8.3 light-minutes**
- The Sun to Neptune — ~4 light-hours
- The nearest star (Proxima Centauri) — **4.2 light-years**
- Across the Milky Way — ~100,000 light-years
- To Andromeda, the nearest large galaxy — 2.5 million light-years
- The observable universe — **~46.5 billion light-years in radius**

**That last number looks wrong and isn't.** The universe is 13.8 billion years old, so how is anything 46 billion light-years away? **Because space itself expanded while the light was in transit** → [[astronomy/07-cosmology|note 07]].

## Looking out is looking back
<!-- bite: a53094c3-1041-4a3d-8ecc-a6c54599a37b -->

**A light-year is a distance, but it's also a delay.** Everything you see is in the past:

- The Sun as it was **8 minutes** ago
- Proxima Centauri **4.2 years** ago
- Andromeda **2.5 million years** ago — before *Homo* existed
- The most distant galaxies JWST sees, **more than 13 billion years** ago

**This is astronomy's greatest methodological advantage.** You cannot rerun the universe — but you can *look further away* to see it younger. **Distance is a time machine**, and it's how the history of galaxy formation is studied at all.

## What astronomers actually do
<!-- bite: 34a75f11-ae2a-45e2-95be-fb456da72758 -->

**Very little of it is looking through eyepieces.**

- **Writing telescope proposals**, and mostly being rejected — big facilities are oversubscribed several times over
- **Reducing data** — calibration, removing instrumental artefacts, subtracting the sky. Often the bulk of the work
- **Writing code.** Modern astronomy is a computational science; Python is effectively its lingua franca → [[languages/06-python/index|Python]]
- **Statistics** — much of the field is extracting weak signals from noisy, incomplete, biased samples
- **Simulation** — you can't experiment on a galaxy, so you simulate one → [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]]

**The field is unusually open.** Most large surveys become public, papers go to **arXiv** before journals, and the core software stack (Astropy, NumPy) is open source. **An amateur with a laptop can do real work on real data**, which is not true of most sciences → [[astronomy/10-getting-started|note 10]].

## Related
<!-- bite: 616f8f74-7e87-4b00-a3b9-655aae588d96 -->
- [[astronomy/02-the-sky-and-how-it-moves|the sky and how it moves]] — start here for observing
- [[astronomy/03-light-and-instruments|light and instruments]] — how everything is measured
- [[astronomy/09-astrology-honestly|astrology, honestly]] — the distinction, properly
- [[astronomy/index|the domain index]]

## About this lesson
<!-- bite: 50556a15-b253-499a-8653-04cd5cc52f46 -->

**Level:** Beginner. **Covers:** The observational science of everything beyond Earth — and how it differs from the fields it gets confused with.

*Source: [reference] — written Aug 2026 from standard texts and current mission documentation.*
