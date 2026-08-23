# Practice Exercises

> **[Intermediate]** · Twelve exercises. **Every idea in this course is a short script over real data.**

This course's own note says it's *"unusually cheap to make concrete"* — and it is. Pure Python; no libraries needed except where marked.

Solutions with measured results in [[foundations/information-theory/09-practice-exercises-solutions|note 09]].

---

## Part A — Entropy (notes 01–02)

**1. Measure the entropy of a real file.**
Count byte frequencies in a file you own, compute $H = -\sum p_i \log_2 p_i$ in bits per byte, and multiply by the file size for a predicted floor. **Then compress it with `gzip -9` and `xz` and compare.**
**Done when:** you have three numbers — and **if the compressor beat your "floor", you have the most important result in this course.** Explain it → [[foundations/information-theory/01-what-information-is|note 01]].

**2. Entropy of English.**
Compute the order-0 entropy of letters in a large English text, and compare against $\log_2 26$ for a uniform alphabet.
**Done when:** you can say how many bits of redundancy per letter the *letter frequencies alone* reveal, and why the true figure for English is far lower still.

**3. Reproduce Shannon's 1951 experiment.**
Have someone guess the next letter of a sentence they haven't seen, one letter at a time, recording how many guesses each took. 100 letters is enough.
**Done when:** you have a guess-count distribution and an entropy estimate. **A genuinely fun hour**, and it produces a number nothing else gets you.

**4. Mutual information beats correlation.**
Generate $X \sim \text{Uniform}(-1,1)$ and $Y = X^2$. Compute Pearson correlation, then estimate $I(X;Y)$ by binning.
**Done when:** correlation is ~0 and mutual information is clearly positive. **Two variables where one *determines* the other, and correlation sees nothing** → [[foundations/information-theory/02-entropy-joint-conditional-and-mutual|note 02]].

**5. Conditioning creates dependence.**
Let $A$ and $B$ be independent fair coins and $C = A \oplus B$. Verify $I(A;B) = 0$ but $I(A;B \mid C) = 1$ bit.
**Done when:** you can state why *"control for more variables"* is not automatically more rigorous. This is a **collider**, and it's the mechanism behind a large class of bad statistical practice.

---

## Part B — Compression (note 03)

**6. Implement Huffman.**
Build the tree, encode, decode, and verify round-trip. Compare bits used against the entropy floor from exercise 1.
**Done when:** your output is within 1 bit/symbol of $H$ → [[foundations/information-theory/03-source-coding-and-compression|note 03]].

**7. Make Huffman lose badly.**
Encode a binary source with $p = 0.9$, then $0.98$, then $0.99$. Compare bits/symbol against $H$.
**Done when:** you can state how much worse Huffman is at each, and **why it cannot do better** without a change of approach.

**8. Fix it with blocking.**
Group the $p=0.9$ source into blocks of 2, 3, 4 symbols and Huffman-code the blocks.
**Done when:** bits/symbol approaches $H$ as block size grows, and you can explain what arithmetic coding does that makes blocking unnecessary.

**9. Prove no compressor compresses everything.**
Argue by counting that no lossless scheme can shorten every input of length $n$.
**Done when:** the argument is airtight in three lines — **and you can use it to dismiss any "compresses any file by 50%" claim in one sentence**.

---

## Part C — The ML connection and channels (notes 04–06)

**10. Cross-entropy by hand.**
Take a 4-class problem, five examples, hand-written predicted probabilities. Compute the cross-entropy loss manually, then confirm it matches your framework's `cross_entropy`. Then compute perplexity.
**Done when:** your hand figure matches to several decimals, and you can state the relationship between loss and perplexity → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|note 04]].

**11. Forward vs reverse KL.**
Fit a single Gaussian to a bimodal target by minimising $D_{KL}(p\|q)$ and then $D_{KL}(q\|p)$. Plot both.
**Done when:** one covers both modes and one picks a single mode, and you can say which failure each direction produces.

**12. Hamming code by hand.**
Implement Hamming(7,4). Encode a nibble, flip one bit, and correct it. Then flip two bits.
**Done when:** single errors are corrected and **you can show a double error is silently mis-corrected** — which is why real systems use SECDED → [[foundations/information-theory/06-error-correcting-codes|note 06]] · [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|ECC memory]].

## Related
- [[foundations/information-theory/09-practice-exercises-solutions|Solutions]]
- [[foundations/information-theory/README|the course]]

*Source: [reference] — built from this course's own gap-closing list. Results measured Aug 2026.*
