# Information Theory

Shannon's measure of surprise, and the surprising number of things it turns out to govern. **Connective tissue for material already in this vault, not a new silo.**

**~11,700 words across 9 notes** (including practice + solutions). Built August 2026. `[reference]`.

> **The one idea:** information is **surprise**, measured as $-\log p$. That single definition gives you the compression limit, the channel capacity, the loss function every classifier is trained on, the strength of a password, and the energy cost of erasing a bit.

## Why this exists

**Two things in the vault were leaning on it without saying so:**

**Cross-entropy loss and KL divergence appear throughout `ai-ml/` — 98 notes — and were never explained.** [[foundations/information-theory/04-cross-entropy-and-kl-divergence|Note 04]] is that explanation, and it's the load-bearing one.

**Key entropy is referenced in [[foundations/discrete-math/06-combinatorics-and-counting|discrete-math 06]]**, Shannon capacity belongs under [[foundations/networking/README|networking]], and error-correcting codes sit on [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|finite fields]]. **All of it existed in pieces.**

## Reading order

**01–02 are the definitions and build in order. 03–06 are the four classical applications** — compression, ML, communication, reliability — and can be read independently. **07 is the payoff.**

1. [[foundations/information-theory/01-what-information-is|What Information Is]] — **[Intermediate]** — surprise, the bit, entropy, and **why English is only ~1.1 bits per character**
2. [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|Joint, Conditional and Mutual Information]] — **[Intermediate]** — the toolkit, the Venn diagram worth memorising, **why mutual information beats correlation**, and the data processing inequality
3. [[foundations/information-theory/03-source-coding-and-compression|Source Coding and Compression]] — **[Intermediate]** — entropy as a hard floor, **why Huffman isn't optimal**, arithmetic coding and ANS, and Kolmogorov complexity
4. [[foundations/information-theory/04-cross-entropy-and-kl-divergence|Cross-Entropy and KL Divergence]] — **[Intermediate]** — **the note the ML material needed.** Why your loss is cross-entropy, forward vs reverse KL, perplexity, and compression ≡ prediction
5. [[foundations/information-theory/05-channel-capacity-and-noise|Channel Capacity and Noise]] — **[Intermediate → Advanced]** — the noisy channel coding theorem, Shannon–Hartley, and **why WiFi is as fast as it is**
6. [[foundations/information-theory/06-error-correcting-codes|Error-Correcting Codes]] — **[Advanced]** — Hamming, Reed–Solomon, turbo and LDPC, erasure coding, and **the fifty-year gap between Shannon's promise and codes that delivered**
7. [[foundations/information-theory/07-where-information-theory-shows-up|Where It Shows Up]] — **[Intermediate]** — nine domains, one measure

## The things worth carrying

1. **Information is surprise.** $-\log p$, and the logarithm is forced by requiring independent events to add → [[foundations/information-theory/01-what-information-is|01]]
2. **Entropy is a property of the *source*, not of a message.** "The entropy of this string" isn't well-posed → [[foundations/information-theory/01-what-information-is|01]]
3. **Mutual information captures nonlinear dependence where correlation sees nothing.** $Y = X^2$ has zero correlation and high MI → [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|02]]
4. **Conditioning can *create* dependence.** Which is why "control for more variables" is not automatically more rigorous — colliders → [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|02]]
5. **Post-processing cannot create information.** No feature engineering adds signal that isn't in the raw data → [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|02]]
6. **Entropy is the compression floor** — a theorem, so every "compresses anything" claim is provably false → [[foundations/information-theory/03-source-coding-and-compression|03]]
7. **Minimising cross-entropy = maximising likelihood = minimising KL to the data.** Three framings, one objective → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|04]]
8. **Forward KL covers all modes; reverse KL picks one.** Knowing which direction you're minimising tells you which failure to expect → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|04]]
9. **Compression and prediction are the same quantity.** Training a language model *is* training a compressor → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|04]]
10. **Below capacity, essentially zero errors at nonzero rate. Above it, never.** A sharp threshold, not a gradual trade → [[foundations/information-theory/05-channel-capacity-and-noise|05]]
11. **Capacity is linear in bandwidth, logarithmic in power.** Which is why MIMO and wider channels beat turning up the transmitter → [[foundations/information-theory/05-channel-capacity-and-noise|05]]
12. **Entropy is a property of the generation process, not the output string.** `Tr0ub4dor&3` looks random and isn't → [[foundations/information-theory/07-where-information-theory-shows-up|07]]

## Where this connects

| | |
|---|---|
| [[ai-ml/02-ml-engineer/05-deep-learning/README\|deep learning]] | **The biggest consumer.** Cross-entropy, KL, perplexity |
| [[cybersecurity/05-cryptography/README\|cryptography]] | Key entropy, perfect secrecy, side-channel capacity |
| [[foundations/networking/README\|networking]] | Shannon–Hartley, CRC, the coding in every physical layer |
| [[databases/03-storage-and-page-layout\|databases]] | Column-store compression, Bloom filters, erasure coding |
| [[foundations/discrete-math/08-number-theory-and-modular-arithmetic\|number theory]] | The finite fields Reed–Solomon needs |
| [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README\|probability]] | **The prerequisite** |

## The honest note

**`[reference]`, and unusually cheap to make concrete** — every idea here is a short script over real data.

**What would close the gap:**

1. **Measure the entropy of a real file** — character frequencies, compute $H$, then compare against what `gzip` and `zstd` actually achieve. **The gap between the two is the redundancy your model isn't capturing**
2. **Reproduce Shannon's 1951 experiment.** Have someone guess the next letter of a sentence, record how many guesses each took, and estimate the entropy of English. **A genuinely fun hour**
3. **Implement Huffman, then arithmetic coding.** Compare on a skewed distribution and watch Huffman lose — **measured: 2.1× at $p=0.9$, 7.1× at $p=0.98$, 12.4× at $p=0.99$** → [[foundations/information-theory/03-source-coding-and-compression|03]] · [[foundations/information-theory/09-practice-exercises-solutions|exercise 7]]
4. **Compute the cross-entropy loss of a model by hand** for a few examples and confirm it matches what PyTorch reports. **Then compute the perplexity and check it's $e^{\text{loss}}$**
5. **Fit forward vs reverse KL to a bimodal distribution** and watch one cover both modes and the other pick one. **Twenty lines, and note 04's central point becomes visual**
6. **Try `gzip` + k-NN as a text classifier.** It works better than it has any right to
7. **The books:** Cover & Thomas, *Elements of Information Theory* (the standard, and readable); **MacKay's *Information Theory, Inference and Learning Algorithms*** — free online, idiosyncratic, and outstanding on the ML connection; Shannon's original 1948 paper, which is short and remarkably clear

**What's missing:** ~~exercises~~ — **closed by notes 8–9 (Aug 2026)**; rate–distortion theory properly, network information theory (multi-user channels), algorithmic information theory beyond a mention, quantum information, and the estimation problem in depth (getting MI from finite samples is genuinely hard and gets one paragraph).

→ [[PRIMETECHIE|Reading is not a rank.]]

## Practice

- [[foundations/information-theory/08-practice-exercises|Practice Exercises]] — twelve exercises over real data — **including why gzip beats your entropy 'floor'**
- [[foundations/information-theory/09-practice-exercises-solutions|Solutions]] — worked answers, **after you've tried**

## Related
- [[ai-ml/README|AI & ML]] — the domain that needed note 04
- [[foundations/discrete-math/README|Discrete Mathematics]] — probability and counting underneath
- [[cybersecurity/05-cryptography/README|Cryptography]] — entropy as security
- [[BUILD-PLAN|Build Plan]]
