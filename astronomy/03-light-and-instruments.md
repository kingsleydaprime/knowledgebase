# Light and Instruments

> **[Beginner → Intermediate]** · The electromagnetic spectrum, what telescopes actually do, and why spectroscopy is the most important technique in the field.

## The spectrum

Visible light is a sliver. **Each band shows you different physics, and each needed its own instrument to open:**

| Band | Reveals | Observed from |
|---|---|---|
| **Radio** | Cold hydrogen, pulsars, the CMB, jets | Ground |
| **Microwave** | **The cosmic microwave background** | Space (mostly) |
| **Infrared** | Dust-obscured regions, cool stars, **early galaxies** | Space + high dry sites |
| **Visible** | Stars, galaxies — what our eyes evolved for | Ground |
| **Ultraviolet** | Hot young stars, accretion | **Space only** |
| **X-ray** | Black hole accretion, hot gas, supernova remnants | **Space only** |
| **Gamma** | The most energetic events in the universe | **Space only** |

**The atmosphere is opaque to most of it.** Only radio and visible pass through well, with some infrared windows. **That is why space telescopes exist** — not to be closer, but to be *above* the air. Hubble is only ~540 km up; the point is the vacuum.

**Why JWST is infrared and Hubble mostly isn't:** the most distant galaxies are **redshifted** so far that their ultraviolet and visible light has stretched into the infrared. To see the early universe you must look in the infrared — and to do that you must be cold, which is why JWST sits at L2 behind a tennis-court-sized sunshield at ~40 K.

## What a telescope actually does

**Two jobs, and the first is the important one:**

**1. Collect light.** Light-gathering power scales with **aperture area** — the square of the diameter. A 200 mm mirror gathers 4× a 100 mm. **This is why aperture dominates every other specification**, and why "magnification" on a box is marketing.

**2. Resolve detail.** The diffraction limit: $\theta \approx 1.22\lambda/D$ — bigger aperture, finer detail.

**Ground-based telescopes rarely reach their diffraction limit**, because the atmosphere blurs everything — "seeing", typically 1–2 arcseconds. Two answers:

- **Adaptive optics** — measure the distortion with a guide star (sometimes a laser-created artificial one) and deform a mirror hundreds of times a second to cancel it. **Ground telescopes can now beat Hubble's resolution in the infrared**
- **Go to space**

**Interferometry** — combine several telescopes so resolution depends on their *separation* rather than their size. The **Event Horizon Telescope** did this across the whole Earth to image a black hole's shadow. Standard in radio; increasingly used in the optical.

## Detectors

**Photographic plates → CCDs** was the field's quiet revolution. A photographic emulsion captures ~2% of incoming photons; a CCD captures **>90%**. **Overnight, every telescope became roughly 40× more powerful**, and photometry became precise rather than approximate.

**CMOS sensors** — the technology in your phone — now compete with and often beat CCDs, and they made serious amateur astrophotography affordable.

## Spectroscopy — the technique that matters most

**Split light into its spectrum and a point of light becomes a physics experiment.**

**Three spectrum types** (Kirchhoff's laws):
- **Continuous** — a hot dense object; a smooth rainbow
- **Emission lines** — a hot thin gas; bright lines at specific wavelengths
- **Absorption lines** — a continuous source seen *through* cooler gas; dark lines

**Each element produces a unique set of lines** — a fingerprint. So from a spectrum you read:

- **Composition** — which elements, and how much
- **Temperature** — from the continuum shape and which lines appear
- **Density and pressure** — from line widths
- **Magnetic field** — from Zeeman splitting
- **Motion** — from Doppler shift

**Helium was discovered in the Sun's spectrum in 1868, 27 years before it was found on Earth.** That single fact is the best argument for spectroscopy's power: an element identified in an object nobody could ever visit.

## Redshift

**A Doppler shift of the whole spectrum toward longer wavelengths.** Because the line *pattern* is known, you can measure the shift precisely even for objects too faint to see detail in.

**Three distinct causes, and conflating them is a common error:**
- **Doppler** — genuine motion away from us
- **Cosmological** — **the expansion of space itself** stretching light in transit. Not motion through space → [[astronomy/07-cosmology|note 07]]
- **Gravitational** — light climbing out of a gravity well → [[astronomy/06-gravity-and-relativity|note 06]]

**Cosmological redshift, denoted $z$, is astronomy's clock.** It's how "distance" and "lookback time" are actually quoted for anything far away.

## The modern reality: surveys and pipelines

**Astronomy is now a data science.** The **Vera Rubin Observatory** will image the entire southern sky every few nights, producing ~20 TB nightly and millions of alerts — transients, variables, moving objects.

**Nobody looks at those images by eye.** The work is pipelines, classification, and increasingly machine learning → [[ai-ml/README|AI & ML]]. **Gaia** measured positions and motions for ~2 billion stars; that catalogue alone has generated thousands of papers.

**And the data is largely public**, usually after a short proprietary period. **Anyone can download and analyse it** → [[astronomy/10-getting-started|note 10]].

## Related
- [[astronomy/04-stars|stars]] — what the spectra are telling you about
- [[astronomy/07-cosmology|cosmology]] — redshift as a distance measure
- [[foundations/information-theory/README|information theory]] — extracting signal from noise
- [[foundations/computer-graphics/README|computer graphics]] — the imaging maths

*Source: [reference] — written Aug 2026.*
