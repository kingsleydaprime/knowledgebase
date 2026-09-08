# Source Coding and Compression

**[Intermediate]** — Entropy as a hard floor, why Huffman isn't optimal, and how modern compressors actually work.

## Shannon's source coding theorem

> **The average code length of any uniquely decodable code satisfies**
> $$L \geq H(X)$$
> **and codes exist achieving $L < H(X) + 1$.**

**Entropy is the compression limit.** Not an engineering estimate — a proof.

**The consequences:**

**No compressor beats entropy.** Every "compresses any file by 50%" claim is provably false — and the pigeonhole argument from [[foundations/discrete-math/06-combinatorics-and-counting|combinatorics]] says the same thing more crudely: **there are more $n$-bit strings than shorter strings, so any lossless compressor must expand some inputs.**

**Random data doesn't compress.** Maximum entropy, no redundancy, nothing to exploit. **Which is why already-compressed files (JPEG, ZIP, MP4) don't shrink further** — and why a compression ratio near 1.0 on a file is decent evidence it's encrypted or compressed.

**Compression is prediction.** To achieve entropy you need the true distribution. **A better model of the source gives better compression** — and this equivalence turns out to run very deep. → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|Cross-Entropy]]

## Prefix codes

**A code where no codeword is a prefix of another.** Then a stream decodes unambiguously without delimiters.

```
 A → 0        "0110111" decodes uniquely:
 B → 10        0 | 110 | 111  →  A, C, D
 C → 110
 D → 111
```

**Kraft's inequality** characterises when lengths $\ell_i$ are achievable:

$$\sum_i 2^{-\ell_i} \leq 1$$

**Equality means no codeword length is wasted.** It's a budget: short codewords are expensive because they block many longer ones.

**And it tells you the optimal length directly** — combining Kraft with minimising expected length gives:

$$\ell_i = -\log_2 p_i$$

> **The optimal codeword length for a symbol is its self-information.** That's not a coincidence — **it's why entropy is the answer.** A symbol occurring 1 time in 8 deserves 3 bits.

## Huffman coding

**Optimal among codes that assign whole numbers of bits per symbol.**

```
Repeatedly: take the two least-probable nodes,
            merge into a parent with their summed probability.
The tree gives the codes.
```

**A greedy algorithm that is provably optimal** — one of the relatively few cases where greedy is exactly right. → [[foundations/dsa/05-algorithms/10-greedy-algorithms|Greedy Algorithms]]

**The limitation, and it's fundamental:**

> **Huffman must use an integer number of bits per symbol.** If a symbol has probability 0.9, its ideal length is $-\log_2 0.9 = 0.152$ bits. **Huffman must give it at least 1** — nearly 7× too long.
>
> **So for highly skewed distributions Huffman is badly suboptimal.** With a binary source at $p = 0.99$, entropy is 0.08 bits/symbol and Huffman spends 1.0 — **a 12× gap.**

**Blocking symbols together helps** (encode pairs or triples) but the alphabet grows exponentially.

## Arithmetic and range coding

**The fix: don't assign codewords to symbols. Encode the whole message as a single number.**

**Maintain an interval $[low, high)$, initially $[0,1)$. Each symbol narrows it in proportion to its probability. At the end, transmit any number inside the final interval.**

```
 [0 ─────────────────────── 1)
   A: [0, 0.7)   B: [0.7, 0.9)   C: [0.9, 1)

 encode "AB":
 after A →  [0, 0.7)
 after B →  [0.49, 0.63)      transmit e.g. 0.5
```

**The final interval has width $\prod p_i$, so it needs $-\log_2\prod p_i = \sum -\log_2 p_i$ bits.**

> **That's exactly the entropy — with no integer-bit penalty.** Arithmetic coding achieves within 2 bits of the entropy **for the entire message**, not per symbol. **It is essentially optimal**, and it's why it displaced Huffman wherever the extra CPU is affordable.

**Practical details:** implementations use integer arithmetic with renormalisation, and emit bits as the interval narrows rather than waiting. **Range coding** is the same idea with a different renormalisation, historically used to sidestep arithmetic-coding patents (now expired).

**ANS (asymmetric numeral systems)** — Jarosław Duda, 2009 — **achieves arithmetic-coding compression at Huffman-like speed.** It's the reason modern compressors got both better *and* faster: **Zstandard, LZFSE, and JPEG XL all use it.** A genuinely significant recent development in a field that had been stable for decades.

## Modelling beats coding

**The entropy coder is the easy part.** The compression ratio is set by the *model*.

**Order-$n$ context models** — predict the next symbol from the previous $n$. English at order 3 gets to ~2 bits/char; better models approach Shannon's ~1.1.

**Dictionary methods (LZ77/LZ78)** — replace repeated strings with references to earlier occurrences.

**This is what DEFLATE is:** LZ77 to find repeats, then Huffman on the result. **gzip, PNG, and ZIP are all this**, which is why they perform similarly.

**Modern general-purpose compressors:**

| | Approach | Character |
|---|---|---|
| **gzip/DEFLATE** | LZ77 + Huffman | universal, moderate ratio, fast |
| **bzip2** | BWT + move-to-front + Huffman | better ratio, slow |
| **xz/LZMA** | LZ77 + range coding, big window | **high ratio**, slow, memory-hungry |
| **Zstandard** | LZ77 + ANS, tunable | **the modern default** — near-xz ratios at near-gzip speed |
| **Brotli** | LZ77 + context modelling + built-in dictionary | **the web** — ships with a dictionary of common HTML/CSS/JS |

> **Zstandard is the right default for new work.** It spans a wide speed/ratio range with one flag, decompresses several times faster than gzip, and supports trained dictionaries for many small similar payloads — which is a large win for things like JSON API responses.
>
> **Brotli's built-in dictionary is a nice trick:** because it ships with ~120 KB of common web text, it compresses small HTML/CSS files far better than a general compressor that has to learn the patterns from the file itself.

**The Burrows–Wheeler transform** deserves a mention: it reversibly permutes the input so that similar contexts cluster, making the result far more compressible. **Reversible without storing the permutation**, which is the clever part, and it's the basis of bzip2 and of the FM-index used in genomics.

## Lossy compression

**Discard information deliberately. A completely different game** — entropy no longer bounds you, because you're not reproducing the input.

**Rate–distortion theory** is the generalisation: $R(D)$ is the minimum rate needed to achieve distortion at most $D$.

**The universal recipe:**

```
1. TRANSFORM     to a domain where energy concentrates  (DCT, wavelet)
2. QUANTISE      coarsely where perception is insensitive   ← the lossy step
3. ENTROPY-CODE  the result losslessly
```

**Only step 2 loses information.** Steps 1 and 3 are exactly reversible.

**JPEG:** 8×8 DCT, quantise high frequencies aggressively (the eye is less sensitive to fine detail), then Huffman or arithmetic code. **JPEG's blocking artefacts are the 8×8 grid becoming visible** when quantisation is too coarse.

**MP3/AAC:** a psychoacoustic model decides what's inaudible — **frequency masking** (a loud tone hides nearby quiet ones) and **temporal masking** (a loud sound hides what follows it) — and spends no bits there.

**Video** adds the big win: **temporal prediction.** Most frames resemble the previous one, so encode motion vectors plus a residual. **This is why video compresses far better than a sequence of independent images.**

**Neural compression** is the active frontier — learned transforms and entropy models beating hand-designed codecs on rate–distortion, at much higher computational cost.

## Kolmogorov complexity

**The theoretical limit for a single object**, and worth knowing because it clarifies what entropy is not.

$$K(x) = \text{length of the shortest program that outputs } x$$

**Entropy is a property of a source; $K$ is a property of an object.** *"What's the entropy of `"hello"`?"* isn't well-posed. *"What's $K(\text{"hello"})$?"* is.

> **And $K$ is uncomputable.** No algorithm computes it for arbitrary input — the proof is a [[foundations/theory-of-computation/06-decidability|halting-problem reduction]], and it also yields Chaitin's incompleteness theorem.
>
> **So the best possible compressor cannot exist.** Every real compressor is an upper bound on $K$, and there's no way to know how far off you are.

**Practically it explains why compressors are domain-specific:** a compressor is a *model*, and no single model is best for every source. That's the no-free-lunch theorem for compression.

**Normalised compression distance** turns this into a usable similarity metric: $\text{NCD}(x,y)$ based on how much better $xy$ compresses than $x$ and $y$ separately. **Used for plagiarism detection, malware clustering, and phylogenetics** — a genuinely surprising application of `gzip`.

## Practical notes

**Don't compress what's already compressed.** Wasted CPU, and it can grow the file.

**Match the compressor to the workload.** High ratio for cold archives (xz), balanced for transfer (zstd), fast for hot paths (lz4, snappy — often faster end-to-end than no compression, since you move fewer bytes).

**Train a dictionary** for many small similar payloads. **Zstandard's `--train` can transform compression of small JSON documents**, where per-message overhead otherwise dominates.

**Compress before encrypting, never after.** Encrypted data is incompressible by design.

> **And be careful even then: compression combined with encryption leaks information.** **CRIME and BREACH** exploited exactly this — an attacker who can inject text into a compressed-then-encrypted stream learns whether their guess matched a secret **by watching the compressed length change.** The fix was to stop compressing attacker-influenced data alongside secrets. → [[cybersecurity/04-web-security/README|Web Security]]

**Beware decompression bombs.** A 42 KB zip expanding to 4.5 PB is a denial-of-service vector. **Always bound the output size** when decompressing untrusted input.

**Measure on your actual data.** Benchmark ratios are for text corpora and may not resemble your workload at all.

---

## Related
- [[foundations/information-theory/04-cross-entropy-and-kl-divergence|Cross-Entropy and KL Divergence]] — compression as prediction, made precise
- [[foundations/information-theory/01-what-information-is|What Information Is]] — where the entropy floor comes from
- [[foundations/theory-of-computation/06-decidability|Decidability]] — why $K$ is uncomputable
- [[foundations/information-theory/README|Information theory map]]
