# What Information Is

**[Intermediate]** — Shannon's definition, why surprise is the right measure, and where the bit comes from.

**Source:** `[reference]` — see [[foundations/information-theory/README|the domain note]].

## The question

**1948. Claude Shannon, at Bell Labs, asks: how much information is in a message?**

**The answer had to be independent of meaning.** A telephone company doesn't care whether you're proposing marriage or reading a shopping list — it needs to know how many bits it must carry.

> **Shannon's move was to define information as *surprise*.**
>
> A message that tells you something you already knew carries no information. A message that tells you something wildly unexpected carries a lot. **"The sun rose today" is worth nothing; "it snowed in Lagos" is worth a great deal.**

**So information is a property of the *probability distribution*, not of the content.**

## Self-information

**How surprised should you be by an event of probability $p$?**

$$I(x) = -\log_2 p(x) \quad\text{bits}$$

**Three requirements force this form, and it's worth seeing that it's not arbitrary:**

**1. Certain events carry no information.** $p=1 \Rightarrow I = 0$. ✓

**2. Rarer means more informative.** $I$ decreases as $p$ increases. ✓

**3. Independent events add.** If $x$ and $y$ are independent, learning both should give you $I(x) + I(y)$. Since $p(x,y) = p(x)p(y)$, **you need a function turning multiplication into addition — a logarithm.** ✓

**That third requirement is the one that pins it down.** Additivity over independent events is what makes information behave like a physical quantity you can measure and budget.

**The base sets the unit:**

| Base | Unit |
|---|---|
| 2 | **bits** (or shannons) |
| $e$ | **nats** — natural in maths and ML |
| 10 | hartleys / dits |

**A fair coin flip is $-\log_2(1/2) = 1$ bit.** That's the definition of the bit, and it's why the unit exists.

**A fair die roll is $\log_2 6 \approx 2.585$ bits** — note it's not an integer, which is the first sign that "bits" here means something more precise than "storage cells".

## Entropy

**The average information content of a distribution:**

$$H(X) = -\sum_x p(x)\log_2 p(x) = \mathbb{E}[-\log_2 p(X)]$$

**Entropy is the expected surprise.** Equivalently — and this is the operational meaning that matters:

> **$H(X)$ is the average number of bits needed to encode a value drawn from $X$, using the best possible code.**
>
> **Not "could be" — the minimum, provably.** That's Shannon's source coding theorem. → [[foundations/information-theory/03-source-coding-and-compression|Source Coding]]

**The properties:**

$$0 \leq H(X) \leq \log_2 n \quad\text{for } n \text{ outcomes}$$

**$H = 0$** when one outcome is certain — no uncertainty, no information.

**$H = \log_2 n$** when all outcomes are equally likely — **maximum uncertainty.** A uniform distribution is the most surprising one, which matches intuition.

**Worked examples worth carrying:**

| Distribution | Entropy |
|---|---|
| Fair coin | **1 bit** |
| Biased coin, $p = 0.9$ | **0.469 bits** |
| Biased coin, $p = 0.99$ | 0.081 bits |
| Fair die | 2.585 bits |
| English letters (frequency only) | ~4.1 bits |
| **English text** (with context) | **~1.1 bits/char** |

> **That last pair is the whole subject in one comparison.** Treating letters as independent gives 4.1 bits each. **Accounting for the fact that `q` is followed by `u`, that `th` is common, and that words are real, drops it to ~1.1.**
>
> **Shannon measured this experimentally in 1951** by having people guess the next letter of a text. **The redundancy is why English compresses ~4:1**, why you can read text with vowels removed, and why autocomplete works.

## The binary entropy function

**For a two-outcome distribution:**

$$H(p) = -p\log_2 p - (1-p)\log_2(1-p)$$

```
 H(p)
  1 ┤        ╭───╮
    │      ╱       ╲
0.5 ┤    ╱           ╲
    │  ╱               ╲
  0 ┼─────────┬─────────────
    0        0.5          1  p
```

**Maximum at $p = 0.5$, zero at both extremes, and symmetric.** A coin biased 90/10 and one biased 10/90 are equally uncertain — which they obviously should be, and the formula gets it right.

**The curve is flat near the top.** $p = 0.4$ still gives $H = 0.971$ — **a 40/60 split is nearly as uncertain as 50/50.** This is why moderate class imbalance in ML barely reduces the information content, while extreme imbalance ($p = 0.001$, $H = 0.011$) removes almost all of it.

## Why "entropy"

**The name is borrowed from thermodynamics, and the connection is real rather than metaphorical.**

**Boltzmann:** $S = k_B\ln W$, with $W$ the number of microstates consistent with the observed macrostate.

**Shannon:** $H = -\sum p\log p$.

**For a uniform distribution over $W$ states, $H = \log W$.** Same formula, different constant.

> **The story goes that von Neumann suggested the name to Shannon, on the grounds that the function already had one in statistical mechanics — and that "nobody knows what entropy really is, so in a debate you will always have the advantage."** Probably embellished, and the underlying point stands: **both measure uncertainty about a system's exact state given partial knowledge.**

**Landauer's principle makes it physical:** erasing one bit of information dissipates at least $k_BT\ln 2$ joules of heat. **Information has a thermodynamic cost, and it's been measured experimentally.** It's also the resolution of Maxwell's demon — the demon must erase its measurements, and that erasure pays back the entropy it seemed to remove.

## What entropy is not

**Three clarifications that prevent real confusion:**

**Not "amount of data".** A 1 GB file of zeros has almost zero entropy. **Entropy is about the distribution, not the length.**

**Not "meaning" or "value".** A random string has maximum entropy and no meaning. **Shannon deliberately excluded semantics** — and said so explicitly in the 1948 paper, noting that the semantic aspects are "irrelevant to the engineering problem".

**Not a property of a single message.** **Entropy is a property of the *source*** — the distribution messages are drawn from. Asking for the entropy of the string `"hello"` is not well-posed without saying what distribution produced it. (Kolmogorov complexity is the per-object alternative, and it's uncomputable.)

## Where this goes

**The rest of the track builds on this one definition:**

**Multiple variables** — joint, conditional and mutual information → [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|note 02]]

**Compression** — entropy is the hard floor → [[foundations/information-theory/03-source-coding-and-compression|note 03]]

**Machine learning** — cross-entropy loss and KL divergence are this, directly → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|note 04]]

**Communication** — how much can a noisy channel carry → [[foundations/information-theory/05-channel-capacity-and-noise|note 05]]

**Reliability** — error-correcting codes → [[foundations/information-theory/06-error-correcting-codes|note 06]]

**Prerequisites:** [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|probability]] — distributions, expectation, independence, conditional probability. Logarithms. **Nothing else.**

---

## Related
- [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|Joint, Conditional and Mutual Information]] — the toolkit
- [[foundations/information-theory/04-cross-entropy-and-kl-divergence|Cross-Entropy and KL Divergence]] — the note the ML material needs
- [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability and Statistics]] — the prerequisite
- [[foundations/information-theory/README|Information theory map]]
