# Joint, Conditional and Mutual Information

**[Intermediate]** — What one variable tells you about another. The toolkit, and the one Venn diagram worth memorising.

## Joint entropy

**The uncertainty in two variables together:**

$$H(X,Y) = -\sum_{x,y}p(x,y)\log_2 p(x,y)$$

**Bounded on both sides:**

$$\max(H(X), H(Y)) \leq H(X,Y) \leq H(X) + H(Y)$$

**The upper bound holds with equality exactly when $X$ and $Y$ are independent.** If knowing one tells you nothing about the other, the uncertainties simply add.

**The lower bound is reached when one determines the other** — $Y = f(X)$ means $Y$ adds nothing.

## Conditional entropy

**The uncertainty remaining in $Y$ once you know $X$:**

$$H(Y|X) = -\sum_{x,y}p(x,y)\log_2 p(y|x) = H(X,Y) - H(X)$$

**The chain rule follows immediately:**

$$H(X,Y) = H(X) + H(Y|X)$$

> **Read it as: total uncertainty = uncertainty in $X$, plus whatever's left in $Y$ once you know $X$.** It's just decomposing the joint uncertainty in stages, and it generalises to any number of variables.

**Two facts worth carrying:**

$$H(Y|X) \leq H(Y) \qquad\text{— conditioning never increases entropy}$$

**On average, information never hurts.** Knowing something can only reduce your uncertainty, or leave it unchanged.

> **But note "on average".** A *particular* observation can increase your uncertainty — $H(Y|X=x)$ can exceed $H(Y)$ for some specific $x$. **It's the expectation over $x$ that's guaranteed to decrease.** This trips people up, and it's the difference between "this measurement surprised me and left me more confused" and "measurements are useless".

$$H(Y|X) = 0 \iff Y \text{ is completely determined by } X$$

## Mutual information

**The central quantity in the subject.**

$$I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)$$

**How much does knowing one reduce your uncertainty about the other?**

**Equivalent forms:**

$$I(X;Y) = H(X) + H(Y) - H(X,Y) = \sum_{x,y}p(x,y)\log_2\frac{p(x,y)}{p(x)p(y)}$$

**The Venn diagram, which is genuinely worth memorising:**

```
   ┌───────────────────────────┐
   │        H(X,Y)             │
   │  ┌──────────┬──────────┐  │
   │  │  H(X|Y)  │ H(Y|X)   │  │
   │  │      ┌───┼───┐      │  │
   │  │      │ I(X;Y)│      │  │
   │  │      └───┼───┘      │  │
   │  └──────────┴──────────┘  │
   │     H(X)        H(Y)      │
   └───────────────────────────┘
```

**Every identity in this note is a statement about that picture**, which is why it's the fastest way to remember them.

**The properties that make it useful:**

**Symmetric.** $I(X;Y) = I(Y;X)$ — **what $X$ tells you about $Y$ equals what $Y$ tells you about $X$.** Not obvious, and it falls straight out of the joint form.

**Non-negative.** $I(X;Y) \geq 0$, with equality **iff $X$ and $Y$ are independent.**

**A general measure of dependence.** Unlike correlation, **it captures nonlinear relationships.**

> **This is mutual information's main practical advantage over correlation.** For $Y = X^2$ with $X$ symmetric about zero, **the correlation is exactly 0 and the mutual information is large.** Correlation measures *linear* association; MI measures *any* association.
>
> The cost: MI is much harder to estimate from finite samples, needs binning or a density estimator for continuous variables, and has no natural sign or scale.

## Where these get used

**Feature selection.** Rank features by $I(\text{feature}; \text{target})$ — `sklearn.feature_selection.mutual_info_classif`. **Catches nonlinear relevance that a correlation filter misses.**

*The known weakness:* it's marginal. Two features individually uninformative can be jointly predictive (XOR is the standard example), and pairwise MI ranking will discard both. **mRMR** (max-relevance, min-redundancy) partially addresses this.

**Decision trees.** **Information gain *is* mutual information** — at each split, choose the feature maximising $I(\text{feature};\text{label})$, i.e. the one that most reduces label entropy. ID3, C4.5, and the `entropy` criterion in scikit-learn. → [[ai-ml/02-ml-engineer/03-classical-ml/README|Classical ML]]

*(Gini impurity is the common alternative and behaves similarly — it's a second-order approximation to entropy, and cheaper because there's no logarithm.)*

**Channel capacity.** $C = \max_{p(x)}I(X;Y)$ — capacity is the mutual information between input and output, maximised over input distributions. → [[foundations/information-theory/05-channel-capacity-and-noise|Channel Capacity]]

**Representation learning.** The **information bottleneck** frames learning as compressing $X$ while preserving information about $Y$: minimise $I(X;Z) - \beta I(Z;Y)$. InfoNCE and contrastive methods maximise a lower bound on mutual information between views. → [[ai-ml/02-ml-engineer/08-other-architectures/01-autoencoders-and-gans|Autoencoders]]

**Image registration.** Mutual information between two images is the standard alignment metric in medical imaging — **it works across modalities** (aligning an MRI to a CT) where pixel intensities aren't comparable at all but are statistically dependent.

**Side-channel analysis.** $I(\text{secret}; \text{timing})$ quantifies exactly how much a timing channel leaks. **Zero mutual information is what constant-time code is trying to achieve**, and this makes "how bad is this leak" a measurable question. → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|Cryptographic Attacks]]

## Conditional mutual information

$$I(X;Y|Z) = H(X|Z) - H(X|Y,Z)$$

**What $Y$ tells you about $X$ that $Z$ didn't already.**

**The key subtlety, and it's a real trap:**

> **$I(X;Y|Z)$ can be *larger* than $I(X;Y)$.** Conditioning can *create* dependence.
>
> **The classic case:** $X$ and $Y$ are independent fair coins, and $Z = X \oplus Y$. Then $I(X;Y) = 0$ — they're independent. But $I(X;Y|Z) = 1$ — **given the XOR, knowing one tells you the other exactly.**

**This is the "explaining away" effect**, and it's why causal inference can't be done by looking at correlations alone. Conditioning on a common effect (a collider) induces dependence between independent causes. → [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|Causal Inference]]

**Practical consequence:** *"controlling for more variables is always more rigorous"* is **false**. Conditioning on a collider introduces bias rather than removing it, and this is a live problem in applied statistics.

## The data processing inequality

**A short result with wide consequences.**

For a Markov chain $X \to Y \to Z$ (where $Z$ depends on $X$ only through $Y$):

$$I(X;Z) \leq I(X;Y)$$

> **Post-processing cannot create information.** Once you've mapped $X$ to $Y$, no further computation on $Y$ recovers anything about $X$ that $Y$ didn't already contain.

**Where this bites:**

**No feature engineering creates information.** It reshapes what's there into a form a model can use more easily — genuinely valuable — but the information ceiling is set by the raw data. **If your features don't contain the signal, no transformation will conjure it.**

**Every layer of a neural network can only lose information about the input.** (Which sounds alarming and isn't — the goal is to *discard* the irrelevant information while preserving what predicts $Y$. That's the information bottleneck view of what training does.)

**Lossy compression is irreversible.** Obviously, but now it's a theorem.

**Anonymisation is one-way**, which is the reassuring version — though the inequality says nothing about how much information *survives*, which is why re-identification attacks work.

## Entropy for continuous variables

**Differential entropy** replaces the sum with an integral:

$$h(X) = -\int p(x)\log p(x)\,dx$$

**And it behaves badly**, in ways worth knowing before you use it:

**It can be negative.** A uniform distribution on $[0, 0.5]$ has $h = -1$ bit. **Not a bug** — differential entropy isn't the limit of discrete entropy, which diverges.

**It's not invariant under change of variables.** Rescaling $X$ changes $h(X)$ by $\log|a|$. **So it has no absolute meaning** — measure in metres versus centimetres and you get a different number.

> **But mutual information *is* well-behaved for continuous variables** — it's a difference of differential entropies, and the scaling terms cancel. **$I(X;Y)$ is invariant under invertible transformations of either variable**, which is exactly what you want from a dependence measure. **So use MI, not differential entropy**, when working with continuous data.

**Two useful facts:**

**The Gaussian maximises entropy for a given variance.** $h = \frac{1}{2}\log(2\pi e\sigma^2)$. **This is the information-theoretic justification for the Gaussian as the "least assumptive" distribution** given a known mean and variance — the maximum-entropy principle.

**For a fixed range, the uniform distribution maximises entropy.** Same principle, different constraint.

## Practical notes

**Estimating entropy from samples is biased downward.** With few samples you systematically underestimate — you haven't seen the rare events. **Miller–Madow and other corrections exist**; the naive plug-in estimator is optimistic.

**Binning choices dominate continuous MI estimates.** Too few bins loses structure; too many makes everything look dependent. **Prefer k-NN estimators (Kraskov) or kernel methods** over naive histograms.

**Units matter.** Bits ($\log_2$) or nats ($\ln$). **ML libraries almost always use nats**; be consistent, since a factor of $\ln 2 \approx 0.693$ silently corrupts comparisons.

**Sanity-check against the bounds.** $0 \leq I(X;Y) \leq \min(H(X), H(Y))$. **A negative MI estimate means your estimator is broken**, since the true value can't be.

---

## Related
- [[foundations/information-theory/04-cross-entropy-and-kl-divergence|Cross-Entropy and KL Divergence]] — the ML-facing measures
- [[foundations/information-theory/05-channel-capacity-and-noise|Channel Capacity]] — mutual information, maximised
- [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|Causal Inference]] — where conditioning-on-colliders bites
- [[foundations/information-theory/README|Information theory map]]
