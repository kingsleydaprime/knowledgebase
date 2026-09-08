# Textures and Sampling

**[Intermediate]** — UV mapping, filtering, mipmaps, and why aliasing is a signal-processing problem rather than a graphics one.

## Texture mapping

**A texture is an image sampled across a surface**, indexed by **UV coordinates** stored per vertex and interpolated across the triangle.

**UV unwrapping** — flattening a 3D surface into 2D — is genuinely hard, because **you cannot flatten a sphere without distortion** (that's Gauss's *Theorema Egregium*, and it's why every world map lies). Real unwrapping cuts the mesh into charts and packs them, minimising stretch and seams.

**Wrap modes** at the edges: repeat, clamp, mirror, border. **Repeat plus a non-tiling texture gives visible seams**, which is why tileable textures are authored deliberately.

**Textures carry far more than colour now:** albedo, normal, roughness, metallic, ambient occlusion, height, emissive. **A "texture" is any per-surface data lookup.**

## Sampling and aliasing

> **The central problem: a pixel covers an *area* of texture, not a point.** Sampling one texel per pixel is point-sampling a continuous signal, and that aliases.

**This is exactly the Nyquist problem.** → [[foundations/information-theory/01-what-information-is|Information Theory]]

**The two failure directions:**

**Magnification** — the texture is smaller than the screen area. **Blocky texels.** Fixed by interpolation.

**Minification** — the texture is *larger*, so one pixel covers many texels. **Shimmering, moiré, crawling patterns as the camera moves.** This is the harder and more objectionable one.

**Filtering options:**

**Nearest** — pick the closest texel. Blocky, and correct for pixel art and for data textures where interpolation would be meaningless (index maps, IDs).

**Bilinear** — weighted average of the 4 surrounding texels. **The default for magnification.**

**Trilinear** — bilinear on two mip levels, blended. **Removes visible mip transitions.**

**Anisotropic** — multiple samples along the direction of compression.

## Mipmaps

**The solution to minification, and one of the most effective ideas in graphics.**

**Precompute a pyramid of downsampled versions** — each level half the resolution.

```
 level 0:  512×512
 level 1:  256×256
 level 2:  128×128     ... down to 1×1
```

**At render time, pick the level where one texel ≈ one pixel**, chosen from the screen-space derivatives of the UV coordinates (which is why fragments are shaded in 2×2 quads — you need neighbours to compute the derivative). → [[foundations/computer-graphics/03-rasterisation|Quads]]

> **Mipmapping is pre-filtering.** Instead of averaging many texels per pixel at runtime, you average them once, offline. **A band-limited version of the signal, ready at every scale.**
>
> **Cost: 33% more memory** ($1 + 1/4 + 1/16 + \cdots = 4/3$). **Benefit: no shimmering, and *better* cache behaviour** — distant surfaces read a small texture that fits in cache. **Mipmapping frequently makes rendering faster as well as better-looking**, which is unusual for a quality feature.

**Generate them with a proper filter.** A box filter is standard; a Kaiser or Lanczos filter is better. **And generate mipmaps in the correct colour space** — averaging sRGB values directly is wrong, and produces mips that are too dark.

### Anisotropic filtering

**Mipmaps assume the pixel footprint is square. It usually isn't.**

**A floor stretching to the horizon is compressed heavily in one direction and barely in the other.** Trilinear picks a mip level based on the *worst* axis — **so the texture is blurred along the axis that didn't need it.**

**Anisotropic filtering takes several samples along the long axis** at a sharper mip level.

> **This is why "16× anisotropic filtering" makes ground textures look dramatically better in games**, at very little cost on modern hardware. **It's usually the highest quality-per-performance setting available**, and it should essentially always be on.

## Compression

**Textures dominate memory in real applications.**

**Block compression** (BC/DXT, ETC, ASTC) — fixed-ratio, **decompressed in hardware at sample time.** 4:1 to 8:1.

**The key property: fixed block size means random access.** You can sample any texel without decompressing the whole image — **which is why JPEG is unusable as a GPU texture format** despite compressing better. JPEG is for storage; BC is for sampling.

| Format | Ratio | For |
|---|---|---|
| **BC1/DXT1** | 8:1 | opaque colour |
| BC3/DXT5 | 4:1 | colour + alpha |
| **BC5** | 4:1 | **normal maps** (two channels) |
| BC7 | 4:1 | high-quality colour |
| **BC6H** | 6:1 | **HDR** |
| ASTC | variable | mobile, flexible block sizes |

**Use BC5 for normal maps specifically** — it stores two channels well and you reconstruct $z$ from $x$ and $y$ knowing the vector is unit length. **Compressing a normal map as BC1 produces visible lighting artefacts**, and it's a common mistake.

**Supercompression** (Basis Universal, KTX2) compresses further for *transmission*, then transcodes to the target's native block format at load. **Standard for the web and cross-platform assets.**

## Texture memory and streaming

**A modern game has far more texture data than VRAM.**

**Streaming** — load mip levels on demand based on what's visible. **Distant objects need only small mips.** The characteristic artefact is a texture visibly "popping" to higher resolution as you approach.

**Virtual texturing / sparse textures** — treat texture memory like [[foundations/os/04-virtual-memory|virtual memory]], with page tables and on-demand residency. **The same idea as OS paging, applied to textures**, and it's what allows enormous unique-textured worlds.

**Texture atlases and arrays** — pack many textures together to reduce state changes and draw calls. **Atlases have bleeding problems at mip boundaries** (neighbouring textures blur into each other), which is why texture *arrays* are usually better where available.

**Bindless textures** — index into a large table rather than binding slots. **Removes a major source of draw-call overhead**, and it's how modern GPU-driven renderers work.

## Procedural texturing

**Generate rather than store.**

**Noise functions** — Perlin, simplex, Worley/cellular. **The basis of terrain, clouds, marble, wood, fire.**

**Fractal Brownian motion** — sum octaves of noise at increasing frequency and decreasing amplitude:

$$\text{fBm}(x) = \sum_{i} \frac{1}{2^i}\,\text{noise}(2^i x)$$

**This single construction produces convincing terrain, clouds and turbulence**, and it's why it's ubiquitous.

**Advantages:** no memory, infinite detail, no UV unwrapping, no seams.

**Disadvantages:** expensive at runtime, hard to art-direct, **and difficult to antialias** — a procedural texture has detail at every scale, so there's no mip pyramid. **You have to band-limit analytically, which is genuinely hard.**

**Signed distance fields** deserve a mention: store distance-to-surface instead of coverage. **Scales to any size with sharp edges** — which is why they're the standard for text rendering in games (Valve's 2007 paper), and they enable cheap outlines and glows.

## Sampling beyond textures

**The same theory applies throughout rendering**, which is the reason this note connects outward:

**Antialiasing** — sampling geometry coverage. → [[foundations/computer-graphics/03-rasterisation|MSAA and TAA]]

**Shadow maps** — sampling a depth texture, with PCF as the filter.

**Monte Carlo integration** in path tracing — sampling the light integral. → [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|Path Tracing]]

**Temporal sampling** — motion blur is sampling over time; TAA accumulates samples across frames.

> **Blue-noise sampling is worth knowing across all of these.** Randomly-placed samples clump; regularly-placed samples alias. **Blue noise is random but evenly spread** — no clumps, no structure. **The error it produces is high-frequency, which the eye and any subsequent blur handle far better.**
>
> **Substituting blue noise for white noise in a dither pattern or a sampling sequence is often a free quality improvement** — the same total error, distributed where it's less visible.

## Practical notes

**Always generate mipmaps** unless the texture is a data lookup or UI element.

**Turn on anisotropic filtering.** Best quality per cost available.

**Use the right compression format per texture type** — BC5 for normals, BC6H for HDR.

**Mark colour textures as sRGB, and data textures as linear.** Normal, roughness and metallic maps are **data** — sRGB-decoding them is a real and subtle bug. → [[foundations/computer-graphics/04-shading-and-lighting|Colour space]]

**Watch for texture bleeding** in atlases — pad each entry by the mip chain's worth of border.

**Power-of-two dimensions** are no longer required but still help with mip chains and some compression formats.

**Profile texture memory.** It's usually the largest single consumer, and streaming problems show up as stutter rather than low frame rate.

---

## Related
- [[foundations/computer-graphics/04-shading-and-lighting|Shading and Lighting]] — what the textures feed
- [[foundations/computer-graphics/03-rasterisation|Rasterisation]] — antialiasing, the same sampling problem
- [[foundations/information-theory/01-what-information-is|Information Theory]] — sampling and band-limiting
- [[foundations/computer-graphics/README|Computer graphics map]]
