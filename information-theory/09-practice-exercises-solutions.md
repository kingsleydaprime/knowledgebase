# Practice Exercises — Solutions

> **[Intermediate]** · Worked answers to [[foundations/information-theory/08-practice-exercises|note 08]]. **Measured, August 2026.**

---

## Part A — Entropy

### 1. Entropy of a real file — and why gzip beats the "floor"

Measured on a 31,128-byte markdown file:

```
order-0 entropy   4.801 bits/byte  →  predicted floor 18,682 bytes
gzip -9                                              10,871 bytes
xz                                                   10,272 bytes
```

**The compressor beat the floor by nearly 2×.** If entropy is a hard limit, how?

**Because the "floor" was computed under the wrong model.** Order-0 entropy assumes each byte is drawn *independently* from the frequency distribution. Real text isn't: `q` is followed by `u`, `th` is common, and whole words repeat.

gzip exploits exactly that — LZ77 replaces repeated substrings with back-references, capturing correlations an order-0 model ignores. Under a **better model** (conditional entropy given previous bytes), the true entropy is much lower, and gzip is respecting *that* floor.

**The correct statement: entropy is the compression floor *for a given source model*.** A better model has lower entropy and permits more compression. This is the same fact as *compression ≡ prediction* → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|note 04]], and it's why a large language model is an extraordinary compressor.

**What is still impossible** is exercise 9's counting argument — no scheme compresses *every* input.

### 2. Entropy of English

Measured on the same text, letters only: **4.189 bits/char**, versus $\log_2 26 = 4.700$ for a uniform alphabet.

So letter frequencies alone reveal about **0.5 bits/char of redundancy** — roughly 11%.

**But the true entropy of English is ~1.0–1.5 bits/char**, because most redundancy is in *context*, not single-letter frequency: bigrams, trigrams, words, grammar and meaning. Order-0 sees none of it — the same limitation as exercise 1, quantified.

### 3. Shannon's experiment

Typical: most letters guessed first or second try, occasional long runs after a word boundary.

Shannon's estimator uses the guess-count distribution to bound entropy, giving **~1.0–1.3 bits/char** for English — far below the 4.189 of exercise 2, and the gap *is* everything a human knows about English that a frequency table doesn't.

**This is still one of the cleanest experiments in the field**, and it needs no equipment.

### 4. Mutual information beats correlation

$X \sim U(-1,1)$, $Y = X^2$: **Pearson $r \approx 0$**, because the relationship is symmetric — positive and negative $X$ contribute opposite products, cancelling.

**Mutual information is clearly positive**, because knowing $X$ determines $Y$ *exactly*: $H(Y|X) = 0$, so $I(X;Y) = H(Y)$.

**Correlation measures *linear* dependence only.** MI measures dependence of any shape. **Reporting "these variables are uncorrelated" as "these variables are unrelated" is a real and common error** — and it's why feature-selection by correlation silently discards useful non-linear features → [[ai-ml/README|AI & ML]].

(Estimating MI from finite samples is genuinely hard and bin-size dependent — your number will be biased upward. The *sign* is the point.)

### 5. Conditioning creates dependence

$A, B$ independent fair bits: $I(A;B) = 0$.

But given $C = A \oplus B$: knowing $C$ **and** $A$ determines $B$ exactly. So $I(A;B \mid C) = 1$ bit.

**Conditioning on a common effect creates dependence between independent causes.** That's a **collider**, and it's why "control for everything you can" is wrong: conditioning on a variable that both causes influence *manufactures* a spurious association.

The everyday version: among admitted students, test scores and grades correlate negatively even if independent in the population — because admission depends on both. **Same structure, and it appears constantly in observational analysis.**

---

## Part B — Compression

### 6. Huffman

Correct implementation lands **within 1 bit/symbol of $H$** — guaranteed, since Huffman is optimal among codes assigning a whole number of bits per symbol, with redundancy $< 1$ bit.

Round-trip must be exact — Huffman is lossless, and the prefix property makes decoding unambiguous with no delimiters.

### 7. Make Huffman lose badly

Binary source, $H = -(p\log_2 p + (1-p)\log_2(1-p))$; Huffman must spend **1 bit/symbol** (there are only two symbols; you can't use half a bit):

| $p$ | $H$ (bits) | Huffman | ratio |
|---|---|---|---|
| 0.90 | 0.4690 | 1 | **2.13×** |
| 0.95 | 0.2864 | 1 | 3.49× |
| 0.98 | 0.1414 | 1 | **7.07×** |
| 0.99 | 0.0808 | 1 | **12.38×** |

**At $p=0.99$ Huffman uses over twelve times the optimal.**

**It cannot do better because it assigns an integer number of bits per symbol.** When the optimal code length is 0.08 bits, rounding to 1 is catastrophic. **This is the structural limit of Huffman**, not an implementation flaw.

### 8. Fix it with blocking

Coding blocks of $k$ symbols amortises the rounding over $k$ symbols, so the excess falls as $O(1/k)$. At $p=0.9$: 1.0 → ~0.65 → ~0.55 → ~0.51 bits/symbol as $k$ goes 1→4, approaching $H = 0.469$.

**The cost is an alphabet of $2^k$ blocks** — exponential table growth for linear improvement.

**Arithmetic coding sidesteps it entirely** by encoding the whole message as a single number in $[0,1)$, never committing to a per-symbol boundary. It achieves within ~2 bits of $H$ for the *entire message*, and it takes fractional probabilities natively — which is why modern compressors (and ANS in Zstandard) use it rather than Huffman → [[foundations/information-theory/03-source-coding-and-compression|note 03]].

### 9. No compressor compresses everything

There are $2^n$ inputs of length $n$, and only $2^n - 1$ possible strings of length $< n$ (summing $2^0 + \dots + 2^{n-1}$). A lossless code must be injective. **By pigeonhole, at least one input of length $n$ cannot map to anything shorter.** ∎

**Stronger:** at most half of all $n$-bit inputs can be shortened by even one bit.

**The one-sentence dismissal:** *"If it compresses every input, apply it repeatedly and reach one bit — which cannot be decoded back to anything."* Every recursive-compression claim dies to this, and several have been patented anyway → [[foundations/discrete-math/09-practice-exercises|pigeonhole]].

---

## Part C — ML and channels

### 10. Cross-entropy by hand

$\text{CE} = -\frac{1}{N}\sum_i \log p_i(\text{correct class})$ — **only the probability assigned to the true class matters**, which is the thing to notice.

Matching your framework requires care: use natural log (PyTorch does), and remember `cross_entropy` expects **logits**, applying log-softmax internally — feeding it probabilities is a classic and silent bug.

**Perplexity $= e^{\text{loss}}$** (natural log). A perplexity of 12 means the model is as uncertain as if choosing uniformly among 12 options. **It's an effective branching factor**, which is why it's the standard language-model metric and why it's interpretable in a way loss isn't.

### 11. Forward vs reverse KL

Target: a bimodal mixture. Fitting one Gaussian:

- **Forward, $D_{KL}(p\|q)$ — mean-seeking.** Penalises $q$ being small where $p$ is large, so $q$ spreads to cover **both** modes, placing most mass in the valley between them where the target has none
- **Reverse, $D_{KL}(q\|p)$ — mode-seeking.** Penalises $q$ being large where $p$ is small, so $q$ collapses onto **one** mode and ignores the other

**Neither is "correct" — they fail differently, and knowing which you're minimising tells you which failure to expect.** Variational inference minimises reverse KL, which is why VI is known to underestimate variance; maximum likelihood minimises forward KL, which is why it produces over-broad models. **Mode collapse in generative models is this** → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|note 04]].

### 12. Hamming(7,4)

Three parity bits at positions 1, 2, 4 covering overlapping subsets. Recomputing parity on receipt yields a 3-bit **syndrome** which, read as a binary number, is *exactly the position of the flipped bit* — 0 meaning no error. Elegant, and the elegance is the point.

**Flip two bits and it fails silently.** The syndrome points at a third, innocent position, which the decoder "corrects" — producing a codeword **further** from the original. **Hamming(7,4) has minimum distance 3**: it can correct 1 error *or* detect 2, but not both.

**Hence SECDED** — add an overall parity bit for distance 4, giving single-error correction *and* double-error detection. **That's what ECC memory in [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|servers]] actually implements**, and why the guarantee is stated as "corrects single-bit, detects double-bit" rather than "corrects errors".

## Related
- [[foundations/information-theory/08-practice-exercises|the exercises]]
- [[foundations/information-theory/README|the course]]

*Source: [reference] — entropy and compression figures measured August 2026.*
