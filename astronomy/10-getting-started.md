# Getting Started

> **[Beginner]** · Observing with no equipment, what to buy and when, and how to do real science from a laptop.

**Astronomy is unusually accessible.** The sky is free, the data is public, and amateurs still make genuine contributions — which is true of almost no other science.

## Start with your eyes

**Do not buy a telescope first.** The commonest path to an unused telescope in a cupboard is buying one before knowing the sky.

**Learn these, in order:**
1. **The Moon's phases** — watch for a month. You'll never misremember why they happen again
2. **Find north.** The Plough → Polaris (northern); the Southern Cross (southern)
3. **Three constellations you can find without help.** Orion is the easiest and richest
4. **Follow one planet across weeks.** Jupiter and Venus are unmistakable — brighter than any star and they don't twinkle
5. **Notice the sky rotating.** Same time each night, a fortnight apart → [[astronomy/02-the-sky-and-how-it-moves|note 02]]

**Then binoculars — genuinely, before a telescope.** A pair of 10×50s shows the Moon's craters, Jupiter's four Galilean moons, the Pleiades, the Orion Nebula and the Andromeda Galaxy. **They cost a fraction of a telescope, need no setup, and you may already own some.**

## Light pollution

**The single biggest factor in what you can see**, and it's worth measuring rather than guessing.

The **Bortle scale** runs 1 (pristine) to 9 (inner city). Most people live at 6–8, where a few dozen stars are visible; at Bortle 2–3 you see thousands and the Milky Way is obvious.

**Practical:** check a light-pollution map, drive out if you can, **give your eyes 20–30 minutes to dark-adapt** (and use red light to preserve it), and observe when the Moon is down for faint objects.

**The Moon and planets don't care** — they're bright enough for a city centre.

## Buying a telescope

**When you've used binoculars enough to want more.** Then:

**Aperture beats everything.** Light-gathering scales with the square of the diameter → [[astronomy/03-light-and-instruments|note 03]]. **Any advertised "675× magnification" is a warning sign** — useful magnification is capped by aperture and atmosphere at roughly 2× the aperture in mm.

| Type | Good | Less good |
|---|---|---|
| **Dobsonian reflector** | **Most aperture per pound. The standard recommendation** | Bulky; not for astrophotography |
| Refractor | Low maintenance, sharp, good for planets | Expensive per mm of aperture |
| Catadioptric (SCT/Mak) | Compact, versatile | Pricier; cools slowly |

**A 6–8 inch Dobsonian is the near-universal first-telescope answer**, and it will outperform a more expensive small refractor on almost everything.

**The mount matters as much as the optics.** A wobbly mount makes good optics unusable. **This is where cheap telescope kits fail.**

## Software, all free

- **Stellarium** — planetarium software; shows the sky for any time and place. **Start here**
- **SkySafari** / **Stellarium Mobile** — the same, pointable at the sky
- **Astropy** — the Python ecosystem for real analysis → [[languages/06-python/README|Python]]
- **Aladin**, **TOPCAT** — professional sky atlas and catalogue tools, freely available
- **Clear Outside** — cloud forecasting, which turns out to be the binding constraint most nights

## Doing real science

**This is the part people don't realise is open.**

**Citizen science** — genuinely contributes to published papers:
- **Zooniverse** — Galaxy Zoo (morphology), Planet Hunters (transits in real TESS data). **Human classification still beats automation on some tasks**, and volunteers have found genuinely new objects
- **Variable star observing (AAVSO)** — amateur photometry feeds professional research; long-baseline coverage is something professionals cannot fund
- **Occultation timing** — measuring asteroid shapes and sizes, an area amateurs materially lead

**Public data archives** — anyone can download and analyse:
- **MAST** (Hubble, JWST, TESS, Kepler), **ESA archives** (Gaia), **SDSS**, **NASA Exoplanet Archive**
- **arXiv** — nearly every paper, free, usually before journal publication

**A concrete first project:** download a TESS light curve, plot it, and **find the transit dip yourself**. It's an afternoon with Python and Astropy, it uses real data from a real spacecraft, and it produces a plot you can explain → [[foundations/numerical-methods/README|numerical methods]] for the fitting.

**That project is the reason this domain is worth a folder in a software vault:** modern astronomy is a data-analysis discipline, and the skills transfer both ways.

## Reading and watching

- **Astronomy Picture of the Day (APOD)** — daily, since 1995, with real explanations
- **"Cosmos"** — Sagan's, and Tyson's
- **Carl Sagan, *Pale Blue Dot*** — the best-written thing in the genre
- **Chris Hadfield, *An Astronaut's Guide to Life on Earth*** — spaceflight from inside
- **Kurzgesagt, PBS Space Time** — the latter is unusually rigorous for video
- **Textbooks:** Carroll & Ostlie, *An Introduction to Modern Astrophysics* — the standard, and readable with first-year physics

## Related
- [[astronomy/02-the-sky-and-how-it-moves|the sky and how it moves]] — what you're looking at
- [[astronomy/03-light-and-instruments|light and instruments]] — why aperture wins
- [[astronomy/README|the domain index]]
- [[languages/06-python/README|Python]] — the analysis language

*Source: [reference] — written Aug 2026.*
