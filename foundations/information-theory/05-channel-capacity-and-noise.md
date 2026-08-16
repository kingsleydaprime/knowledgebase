# Channel Capacity and Noise

**[Intermediate → Advanced]** — Shannon's noisy channel theorem, the result that founded modern communications, and why your WiFi has the speed it does.

## The channel

**A channel takes an input $X$ and produces an output $Y$, corrupted by noise.**

```
   X ──►│  p(y|x)  │──► Y
         noisy channel
```

**The binary symmetric channel (BSC)** is the standard model: each bit flips with probability $p$.

**The binary erasure channel (BEC)** instead loses bits with probability $p$ — **and you know which ones were lost.** That knowledge makes it a fundamentally easier channel, which is why packet networks (where a checksum tells you a packet is bad) behave better than bit-level noise.

## Capacity

$$C = \max_{p(x)} I(X;Y)$$

**The maximum mutual information between input and output, over all input distributions.** → [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|Mutual Information]]

**For the binary symmetric channel:**

$$C = 1 - H(p)$$

with $H(p)$ the binary entropy function.

| Flip probability $p$ | Capacity |
|---|---|
| 0 | **1 bit/use** — perfect |
| 0.01 | 0.919 |
| 0.1 | 0.531 |
| **0.5** | **0** — useless |
| 0.9 | 0.531 |
| 1 | **1** — perfectly inverted |

> **Two things worth noticing.**
>
> **$p = 0.5$ gives zero capacity** — the output is independent of the input, so nothing gets through.
>
> **$p = 1$ gives full capacity.** A channel that inverts *every* bit is perfectly reliable — just flip them back. **A completely predictable channel is not noisy**, however wrong it looks. Noise is unpredictability, not error.

## The noisy channel coding theorem

**Shannon, 1948. Arguably the most consequential result in engineering of the last century.**

> **For any rate $R < C$, there exist codes achieving arbitrarily small error probability.**
>
> **For $R > C$, error probability is bounded away from zero.**

**Read that carefully, because it was genuinely shocking at the time.**

**Before Shannon**, the assumption was that reliable communication over a noisy channel required either slowing down or accepting errors — that you'd trade rate against reliability continuously, and perfect reliability meant zero rate.

**Shannon proved there's a sharp threshold.** Below capacity, you can have **essentially zero errors at a nonzero rate.** Above it, you cannot do better than a fixed error floor no matter what you do.

```
 error
 prob   │
        │─────────────────╮
        │                 │      ← sharp threshold at C
        │                 │
      0 ┤_________________╯
        └──────────────────────► rate R
                          C
```

**The proof is non-constructive**, and famously so: Shannon showed that a **randomly chosen** code works, on average, with high probability. **He proved good codes exist without exhibiting one.**

> **That gap defined the next fifty years of coding theory.** Shannon said the limit was reachable in 1948; **codes that actually approach it — turbo codes (1993) and rediscovered LDPC codes (1996) — took until the 1990s.** → [[foundations/information-theory/06-error-correcting-codes|Error-Correcting Codes]]

## Shannon–Hartley

**The continuous version, for a bandwidth-limited channel with Gaussian noise:**

$$C = B\log_2\left(1 + \frac{S}{N}\right) \quad\text{bits/second}$$

**$B$ is bandwidth in Hz; $S/N$ is the signal-to-noise power ratio.**

**This single formula governs every radio link, cable and fibre in existence.**

**What it says:**

**Capacity is linear in bandwidth.** Double the bandwidth, double the capacity. **This is why WiFi moved from 20 MHz to 40, 80 and 160 MHz channels**, and why 6 GHz spectrum mattered — it's the cheapest way to go faster.

**Capacity is only logarithmic in SNR.** **Doubling transmit power buys you one extra bit per symbol at high SNR.** Diminishing returns, and it's why "just turn up the power" stops working quickly.

**Worked example:** 20 MHz at 30 dB SNR gives $20\times10^6 \times \log_2(1001) \approx 200$ Mbps. **Which is about what a good single-stream 802.11n link achieves** — real systems get within a factor of ~2 of Shannon.

**Two more consequences worth carrying:**

**MIMO beats the formula by cheating.** Multiple antennas create multiple spatial streams, so capacity scales with $\min(N_t, N_r)$ — **you multiply the whole expression rather than fighting the logarithm.** This is the single biggest reason WiFi throughput grew: 802.11n added MIMO. → [[hardware/06-radio-frequency|Radio Frequency]]

**There is a minimum energy per bit.** Taking $B\to\infty$ gives the Shannon limit: $E_b/N_0 \geq \ln 2 = -1.59$ dB. **Below that, reliable communication is impossible at any rate.** Deep-space missions design against this number directly.

## What noise actually is

**Thermal noise** — $N = kTB$. Unavoidable, set by temperature and bandwidth. **The reason radio telescopes and low-noise amplifiers are cryogenically cooled.**

**Shot noise** — the discreteness of charge carriers or photons. Dominant in optical links.

**Interference** — other transmitters. **The dominant impairment in real WiFi**, not thermal noise, which is why congested 2.4 GHz performs so badly.

**Multipath fading** — signals arriving via multiple paths and cancelling. **OFDM's whole purpose is to handle this** by splitting into many narrow subcarriers, each seeing flat rather than frequency-selective fading. It's why WiFi, LTE, 5G and DSL all use it.

## Where capacity thinking applies

**The concept generalises well beyond radio.**

**Networking.** Bandwidth-delay product, and why TCP needs window scaling to fill a fast long link. **Note that "bandwidth" in networking means bits/second (capacity), while in signal processing it means Hz** — a genuinely confusing overload. → [[foundations/networking/15-network-performance|Network Performance]]

**Storage.** A hard drive or SSD is a channel — write, wait, read, with noise. **Modern SSDs are so noisy at the cell level that they're unusable without LDPC codes**, and read latency rises as cells wear and decoding gets harder.

**Side channels.** A timing or power leak is a communication channel from a secret to an attacker, **and its capacity is measurable.** "How many bits per query does this leak" is the right question, and it tells you how many queries an attack needs. → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|Cryptographic Attacks]]

**Neuroscience and biology.** Capacity of a neuron's spike train; the channel capacity of DNA replication with its error-correction machinery.

**Any pipeline.** A rate-limited stage is a capacity constraint, and Little's law plays a similar role in queueing. → [[architecture/01-system-design-fundamentals/README|System Design]]

## The separation theorem

**A structural result that explains how communication systems are built.**

> **Source coding and channel coding can be designed independently without loss of optimality.**
>
> **Compress to remove redundancy, then add structured redundancy for error correction.**

**Which sounds absurd** — you strip redundancy out, then put different redundancy back in — **and is provably right** for a single point-to-point link with unlimited block length.

**This is why the layering exists:** compress (JPEG, H.264), then encrypt, then error-correct (LDPC), then modulate. **Each layer designed separately**, which is a large part of why the whole stack is tractable.

**Where separation fails**, and it matters in practice:

**Finite block lengths** — real systems have latency budgets and can't use asymptotically long codes.

**Multi-user channels** — broadcast and multiple-access channels don't obey it.

**Non-ergodic channels** — fading links where the channel state varies.

**Which is why joint source-channel coding exists** for video over wireless, and why **unequal error protection** (guarding a video stream's header bits far more heavily than its detail coefficients) beats treating all bits alike.

## Practical notes

**Capacity is an upper bound, not a throughput estimate.** Real links include protocol overhead, retransmissions, contention and imperfect coding. **Getting within 2× of Shannon is excellent.**

**Improve SNR before bandwidth if SNR is poor**, because you're on the steep part of the logarithm. **Once SNR is high, bandwidth is the only lever that scales.**

**Check the SNR before diagnosing anything else** on a wireless problem. Most WiFi complaints are interference or range, not configuration.

**Error rate and capacity are different questions.** A link can have adequate capacity and unacceptable latency or jitter. **Capacity says nothing about delay.**

**Watch the dB.** 3 dB is 2×, 10 dB is 10×, 30 dB is 1000×. **These are power ratios, and mixing up power and amplitude dB (factor of 2 in the exponent) is a common error.** → [[hardware/06-radio-frequency|Radio Frequency]]

---

## Related
- [[foundations/information-theory/06-error-correcting-codes|Error-Correcting Codes]] — how capacity is actually approached
- [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|Mutual Information]] — what capacity maximises
- [[hardware/06-radio-frequency|Radio Frequency]] — the physical layer
- [[foundations/information-theory/README|Information theory map]]
