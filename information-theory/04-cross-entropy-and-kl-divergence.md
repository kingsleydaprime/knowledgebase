# Cross-Entropy and KL Divergence

**[Intermediate]** — The two quantities used on every page of the ML notes and explained on none of them. What your loss function actually measures.

> **This is the note the rest of the vault was missing.** `ai-ml/` is 98 notes; cross-entropy loss appears throughout and KL divergence underlies VAEs, RLHF and distillation. **Here's what they are.**

## Cross-entropy

**Entropy assumes you know the true distribution $p$. What if you use a model $q$ instead?**

$$H(p,q) = -\sum_x p(x)\log q(x) = \mathbb{E}_{x\sim p}[-\log q(x)]$$

> **Cross-entropy is the average number of bits needed to encode data from $p$ using a code optimised for $q$.**
>
> **You pay for the mismatch.** Code as though the distribution were $q$, but reality draws from $p$, and your messages are longer than they had to be.

**The key inequality:**

$$H(p,q) \geq H(p), \qquad\text{with equality iff } p = q$$

**Your model can never beat the true distribution.** The best possible model is the truth, and cross-entropy is minimised exactly there.

> **Which is why cross-entropy is a loss function.** Minimising $H(p,q)$ over $q$ drives $q$ toward $p$. **It has a unique minimum at the truth**, and that's precisely what you want a loss to do.

## KL divergence

**The excess — how many bits you waste using $q$ instead of $p$:**

$$D_{KL}(p\|q) = H(p,q) - H(p) = \sum_x p(x)\log\frac{p(x)}{q(x)}$$

$$\boxed{H(p,q) = H(p) + D_{KL}(p\|q)}$$

**Cross-entropy = the irreducible entropy of the data + the penalty for your model being wrong.**

**Properties:**

**$D_{KL} \geq 0$**, zero iff $p = q$ (Gibbs' inequality).

**Not symmetric.** $D_{KL}(p\|q) \neq D_{KL}(q\|p)$ — **so it is not a distance**, despite constant informal use as one.

**Not a metric** — no triangle inequality either.

### The asymmetry matters

**This is the part that has real consequences, and it's frequently glossed over.**

**Forward KL, $D_{KL}(p\|q)$ — "mean-seeking" / mass-covering.**

The term $p(x)\log\frac{p(x)}{q(x)}$ blows up wherever $p$ is large and $q$ is near zero. **So $q$ is heavily penalised for putting no mass where $p$ has some** — it must cover everything, even if that means spreading over regions $p$ doesn't occupy.

**Reverse KL, $D_{KL}(q\|p)$ — "mode-seeking" / zero-forcing.**

Now the expectation is over $q$. Wherever $q$ is near zero, that region contributes nothing regardless of $p$. **So $q$ can safely ignore parts of $p$** — it will lock onto one mode and stay there.

```
 True p is bimodal:      ╱╲      ╱╲
                        ╱  ╲    ╱  ╲

 Forward KL fit:      ╱‾‾‾‾‾‾‾‾‾‾‾‾╲     covers both, mass in between
 Reverse KL fit:        ╱╲                picks one mode, ignores the other
                       ╱  ╲
```

**Where each shows up:**

**Forward KL** — maximum likelihood, which is what standard supervised training does. **You want to cover the data.**

**Reverse KL** — variational inference (the VAE's ELBO), and **RLHF's KL penalty**, where you want the policy to stay near the reference model without being forced to cover its whole distribution.

> **Mode collapse in generative models is partly this.** A reverse-KL objective is *content* to model one mode well. Understanding which direction you're minimising tells you what failure to expect. → [[ai-ml/02-ml-engineer/08-other-architectures/01-autoencoders-and-gans|Autoencoders and GANs]]

**Jensen–Shannon divergence** symmetrises it — $\frac{1}{2}D_{KL}(p\|m) + \frac{1}{2}D_{KL}(q\|m)$ with $m$ the average. **Bounded, symmetric, and its square root is a true metric.** The original GAN objective minimises JS divergence, and **its vanishing gradients when distributions don't overlap is why Wasserstein GANs were proposed.**

## Why your loss function is cross-entropy

**The connection that makes this note load-bearing.**

**For classification with one-hot labels**, $p$ puts probability 1 on the true class $y$ and 0 elsewhere. Cross-entropy collapses to:

$$H(p,q) = -\log q(y)$$

**Just the negative log-probability your model assigned to the correct answer.**

**Averaged over a dataset:**

$$\mathcal{L} = -\frac{1}{N}\sum_{i=1}^N \log q(y_i \mid x_i)$$

> **That is exactly the negative log-likelihood.**
>
> $$\boxed{\text{minimising cross-entropy} \equiv \text{maximising likelihood} \equiv \text{minimising } D_{KL}(p_{\text{data}}\|p_{\text{model}})}$$
>
> **All three are the same objective.** Whichever framing you started from — information theory, statistics, or "make the model assign high probability to the data" — **you arrive at the same loss.** That convergence is why cross-entropy is *the* classification loss rather than one option among many.

**Note $H(p)$ is a constant** with respect to your parameters (it's a property of the data), **so minimising cross-entropy and minimising KL are identical optimisation problems.** People say "cross-entropy loss" and "minimising KL to the data distribution" interchangeably for this reason.

**Binary cross-entropy** is the two-class case:

$$\mathcal{L} = -[y\log\hat{y} + (1-y)\log(1-\hat{y})]$$

## Perplexity

**The language-modelling metric, and it's just exponentiated cross-entropy:**

$$\text{PPL} = 2^{H(p,q)} = e^{\mathcal{L}} \quad\text{(nats)}$$

> **Interpretation: the effective number of equally-likely choices the model is deciding among at each step.**
>
> **Perplexity 1** — perfect prediction. **Perplexity 50,000** — no better than uniform over the vocabulary.

**Why report perplexity instead of loss:** it's on a meaningful scale. Going from loss 4.0 to 3.0 sounds modest; **going from perplexity 55 to 20 is obviously a large improvement.**

**The caveat that makes cross-model comparison treacherous: perplexity depends on the tokeniser.** A model with a larger vocabulary predicts fewer, larger tokens, and its perplexity isn't comparable to one with a smaller vocabulary. **Bits-per-character normalises this** and is the honest comparison. → [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]]

## Compression is prediction

**The equivalence that ties this track together.**

**A language model outputs $q(\text{next token} \mid \text{context})$. Feed that to an [[foundations/information-theory/03-source-coding-and-compression|arithmetic coder]] and you have a compressor** achieving $H(p,q)$ bits per token.

$$\text{better model} \iff \text{lower cross-entropy} \iff \text{better compression}$$

> **They are the same quantity.** Training a language model *is* training a compressor, and the loss curve is a compression-ratio curve in different units.

**This isn't a cute analogy — it's exploited directly:**

**The Hutter Prize** pays for compressing 1 GB of Wikipedia, explicitly on the premise that compression is equivalent to intelligence.

**Large language models are excellent general-purpose compressors** — DeepMind's 2023 result showed Chinchilla compressing ImageNet patches better than PNG and audio better than FLAC, **despite being trained only on text.** The model learned enough structure to predict, and prediction is compression.

**And it's the strongest argument for what the pretraining objective does:** to predict the next token well, a model must learn syntax, facts, arithmetic, and reasoning patterns — **because those are what make text predictable.** Compression forces modelling.

## Practical notes

**Never implement cross-entropy naively.**

```python
loss = -np.log(softmax(logits)[y])      # ✗ overflows / underflows
loss = F.cross_entropy(logits, y)       # ✓ fused, numerically stable
```

**`softmax` then `log` overflows for large logits and underflows for small probabilities.** The fused implementation uses the log-sum-exp trick:

$$\log\sum e^{x_i} = m + \log\sum e^{x_i - m}, \qquad m = \max_i x_i$$

**PyTorch's `cross_entropy` takes raw logits** and does this internally. **Passing it post-softmax probabilities is a common and silent bug** — you apply softmax twice, gradients shrink, and training just underperforms without erroring. → [[foundations/numerical-methods/02-floating-point-and-error|Numerical stability]]

**Zero probabilities give infinite loss.** $\log 0 = -\infty$. Clamp, or use label smoothing.

**Label smoothing** replaces one-hot targets with $(1-\epsilon)$ on the true class and $\epsilon/(K-1)$ elsewhere. **Prevents the model driving logits to infinity chasing certainty**, improves calibration, and usually generalises slightly better.

**Watch your units.** ML libraries use **nats** ($\ln$); information theory conventionally uses **bits** ($\log_2$). Factor of $\ln 2 \approx 0.693$.

**KL in VAEs has a closed form** for Gaussians — no sampling needed:

$$D_{KL}(\mathcal{N}(\mu,\sigma^2)\|\mathcal{N}(0,1)) = \tfrac{1}{2}\left(\mu^2 + \sigma^2 - \log\sigma^2 - 1\right)$$

**Estimating KL from samples is high-variance.** For the reverse direction, use the low-variance estimator $\mathbb{E}_q[(r - 1) - \log r]$ with $r = p/q$, rather than the naive $\mathbb{E}[\log r]$ — **this is what modern RLHF implementations use** and it materially reduces gradient noise.

**Cross-entropy is not calibration.** A model can have low cross-entropy and still be overconfident. **Check reliability diagrams and expected calibration error separately.** → [[ai-ml/02-ml-engineer/04-model-evaluation/README|Model Evaluation]]

---

## Related
- [[foundations/information-theory/03-source-coding-and-compression|Source Coding]] — the compression half of the equivalence
- [[ai-ml/02-ml-engineer/05-deep-learning/README|Deep Learning]] — where this loss is used
- [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]] — perplexity and next-token prediction
- [[foundations/information-theory/README|Information theory map]]
