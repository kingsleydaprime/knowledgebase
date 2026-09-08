# Error-Correcting Codes

**[Advanced]** — Adding structured redundancy so errors can be detected and fixed. The fifty-year gap between Shannon's promise and codes that delivered.

## Detection vs correction

**Detection** — know that something is wrong. Cheap. **Ask for a retransmission** (ARQ).

**Correction** — fix it without asking. More redundancy. **Necessary when there's no back channel** (a disk, a deep-space probe, a broadcast) or when a round trip costs too much.

**Hybrid ARQ** combines them — correct what you can, request retransmission otherwise. **What LTE and 5G actually do.**

## Hamming distance

**The number of positions in which two codewords differ.**

**A code's minimum distance $d$ determines its power:**

$$\text{detect } d-1 \text{ errors} \qquad \text{correct } \left\lfloor\frac{d-1}{2}\right\rfloor \text{ errors}$$

> **The geometric picture: codewords are points in a space, and each is surrounded by a ball of radius $\lfloor(d-1)/2\rfloor$.** A received word inside a ball is decoded to its centre. **Correction needs the balls to be disjoint; detection only needs the received word not to land on another codeword.** That's why detection is cheaper by a factor of two.

**A parity bit gives $d = 2$** — detects one error, corrects none.

**Notation:** an $(n,k,d)$ code has $n$-bit codewords carrying $k$ data bits with minimum distance $d$. **Rate $R = k/n$**, and the whole game is pushing $R$ toward capacity while keeping $d$ useful.

## Hamming codes

**The first error-correcting code (1950), and still the clearest.**

**The (7,4) Hamming code:** 4 data bits, 3 parity bits, $d = 3$ — **corrects any single error.**

**The construction is elegant:** put parity bits at positions 1, 2, 4 (the powers of two). Parity bit $2^i$ checks every position whose binary representation has bit $i$ set.

> **Then the syndrome — the pattern of failed checks, read as a binary number — is the *position of the error*, directly.** Syndrome 5 means bit 5 flipped. **No search, no table.**
>
> Hamming invented this out of frustration: his weekend batch jobs kept failing on parity errors, and the machine could detect the problem but not fix it. **"If it can detect the error, why can't it correct it?"**

**Extended Hamming (SECDED)** adds an overall parity bit, giving $d = 4$: **single error correction, double error detection.** This is what ECC memory uses — and it's why servers with ECC RAM survive the cosmic-ray bit flips that silently corrupt data on consumer machines. → [[foundations/computer-architecture/README|Computer Architecture]]

## Reed–Solomon

**The workhorse of the pre-2000s, and still everywhere.**

**Operates on symbols (bytes) rather than bits, over a finite field $GF(2^m)$.** → [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|Modular arithmetic and finite fields]]

**The idea:** treat the $k$ data symbols as coefficients of a polynomial, and **evaluate it at $n$ points.** Any $k$ of those $n$ values reconstruct the polynomial — **it's polynomial interpolation as error correction.** → [[foundations/numerical-methods/06-interpolation-and-approximation|Interpolation]]

**RS$(n,k)$ corrects $\lfloor(n-k)/2\rfloor$ symbol errors**, or $n-k$ erasures.

> **Its defining strength is burst errors.** Because it works on symbols, **a burst corrupting 8 consecutive bits damages one symbol, not eight.** That's exactly the error pattern you get from a scratch on a disc, a dust particle, or a fading radio burst — which is why RS dominated storage and broadcast.

**Where you'll find it:** CDs and DVDs (a CD survives a 2.5 mm scratch), QR codes (up to 30% of the code can be destroyed — which is why you can put a logo in the middle), RAID 6, DSL, digital TV, and **Voyager**, still transmitting from interstellar space.

**Interleaving** is the companion trick: **scramble symbol order before transmission** so a burst in the channel becomes scattered single errors across many codewords. **Cheap, and it multiplies burst tolerance** — CDs use cross-interleaved RS (CIRC) for exactly this.

## Convolutional codes and Viterbi

**Instead of blocks, a sliding window: output bits depend on the current input and the last $K-1$ inputs.**

**Decoded with the Viterbi algorithm** — dynamic programming over the trellis of encoder states, finding the maximum-likelihood path. → [[foundations/dsa/06-patterns/15-dynamic-programming|Dynamic Programming]]

**Optimal decoding in polynomial time**, which is why it was so widely deployed: GSM, 802.11, satellite links, and Voyager's inner code.

**Viterbi appears far beyond coding** — it's the standard decoder for hidden Markov models, used in speech recognition, part-of-speech tagging and gene finding. **Same algorithm, different trellis.**

## Turbo and LDPC — reaching capacity

**The 1990s breakthrough that closed Shannon's fifty-year gap.**

**Turbo codes (1993)** — two convolutional codes with an interleaver between them, decoded **iteratively**: each decoder passes soft probability estimates to the other, which refines and passes back.

> **The result was met with disbelief.** Berrou and Glavieux reported performance within **0.5 dB of the Shannon limit** — after decades in which the best codes were several dB away. **Reviewers initially assumed a simulation error.**

**LDPC codes** — Gallager's 1963 thesis, **ignored for thirty years because the decoding was computationally infeasible at the time**, and rediscovered in 1996 when it wasn't.

**A sparse parity-check matrix, decoded by belief propagation** on the Tanner graph — messages passed between variable and check nodes until they agree.

**LDPC now beats turbo codes** in most applications and is easier to parallelise.

**Where they are:** LDPC in 5G data channels, WiFi 6, DVB-S2, and **every modern SSD** — where cell-level error rates are so high that the drive is unusable without it. Turbo codes in 3G/4G and deep space.

**Polar codes (Arıkan, 2008)** — the first construction **provably achieving capacity** with explicit low-complexity encoding and decoding. **Used for 5G control channels.** A genuinely major theoretical result, and unusually recent.

> **The common thread in all three: soft-decision iterative decoding.** Instead of deciding each bit is 0 or 1 and then correcting, **keep the probability** ("this bit is 70% likely to be 1") and let the decoder refine it. **Soft decisions are worth about 2 dB over hard decisions** — a large fraction of the gap to capacity, from throwing away less information at the demodulator.

## Erasure codes

**When you know *which* pieces are missing** — a dropped packet, a failed disk — the problem is much easier.

**An $(n,k)$ erasure code recovers from any $n-k$ erasures.** No need to *find* the errors; you're told where they are.

**Reed–Solomon works as an erasure code**, and this is how distributed storage achieves durability cheaply:

| Scheme | Storage overhead | Survives |
|---|---|---|
| 3× replication | **200%** | 2 failures |
| RS(9,6) | **50%** | 3 failures |
| RS(14,10) | 40% | 4 failures |

> **Erasure coding gives better durability at a fraction of the storage cost**, which is why every large object store uses it — S3, Ceph, HDFS, Backblaze.
>
> **The trade is reconstruction cost.** Replacing a replica means copying one disk; **reconstructing an erasure-coded block means reading $k$ blocks from $k$ machines and computing.** That's a lot of network traffic, and it's why hot data is often replicated while cold data is erasure-coded. → [[architecture/04-distributed-systems/05-replication|Replication]]

**Fountain codes (LT, Raptor)** are rateless — generate **unlimited** encoded symbols, and the receiver reconstructs once it has slightly more than $k$ of *any* of them. **Ideal for broadcast to receivers with different loss rates**, since nobody needs to tell the sender what they missed.

## Checksums and hashes — a distinction

**Not error-correcting codes, and used for different threats.**

**Checksums (CRC)** detect *accidental* errors. **CRC-32 catches all burst errors up to 32 bits** and is cheap in hardware. **Ethernet, ZIP, PNG.** → [[foundations/networking/02-the-link-layer|The Link Layer]]

**Cryptographic hashes** (SHA-256) detect *deliberate* tampering. **Much more expensive, and CRC is trivially forgeable** — an attacker can adjust the payload to keep the CRC unchanged.

> **Using CRC where you need a MAC is a real vulnerability**, and it's how WEP was broken. **CRC for accidents, HMAC for adversaries.** → [[cybersecurity/05-cryptography/03-hashing-and-integrity|Hashing and Integrity]]

## Practical notes

**Use a library.** Finite-field arithmetic and belief propagation are easy to get subtly wrong. `zfec`, `liberasurecode`, `reedsolo`; hardware LDPC in modern radios.

**Match the code to the error pattern.** Random bit errors → LDPC/convolutional. Bursts → Reed–Solomon plus interleaving. Erasures → an erasure code.

**Use soft information if you have it.** Passing the demodulator's confidence to the decoder rather than a hard 0/1 is worth ~2 dB and costs nothing in transmit power.

**Watch the error floor.** Turbo and LDPC codes have a region where the error rate stops falling steeply — **fine for streaming video, unacceptable for storage.** Concatenating an outer code (often RS or BCH) cleans up the residual errors.

**Enable ECC memory** on anything where silent corruption matters. Cosmic-ray bit flips are real and measurable at scale — **Google's 2009 DRAM study found error rates far higher than manufacturers claimed.**

**Erasure-code cold data, replicate hot data.** Storage saving versus reconstruction cost.

**Test the recovery path.** **An erasure-coded system whose reconstruction has never been exercised is not known to work** — the same argument as untested backups. → [[databases/10-durability-and-recovery|Backups]]

---

## Related
- [[foundations/information-theory/05-channel-capacity-and-noise|Channel Capacity]] — the limit these approach
- [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|Number Theory]] — the finite fields Reed–Solomon needs
- [[architecture/04-distributed-systems/05-replication|Replication]] — erasure coding in storage
- [[foundations/information-theory/README|Information theory map]]
