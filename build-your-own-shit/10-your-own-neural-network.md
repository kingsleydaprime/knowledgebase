# Build Your Own Neural Network

> **[Intermediate]** · Backpropagation from scratch, no framework. **The vault's largest domain had no build guide — this is it.**

## What you're building

**A working neural network in raw arrays, trained by gradient descent you wrote**, classifying MNIST digits to >95% accuracy.

**And what you're deliberately not:** competing with PyTorch, using a GPU, or implementing modern architectures. **The goal is that `loss.backward()` stops being magic.**

**Why this one matters here:** [[ai-ml/README|ai-ml/]] is ~98 notes — the largest domain in this vault — and every one of them assumes autodiff works. **This is the guide that converts that reading into having built it.**

## What you need first

- **Arrays and loops** → [[foundations/programming-fundamentals/README|programming fundamentals]]
- **The chain rule.** Genuinely all the calculus required
- **Matrix multiplication** — what shape times what shape gives what shape
- **Cross-entropy**, and why it's the loss → [[foundations/information-theory/04-cross-entropy-and-kl-divergence|information theory 04]]
- Helpful, not required: [[foundations/numerical-methods/10-numerical-optimisation|numerical optimisation]] · [[ai-ml/README|ai-ml]]

**Python + NumPy is the natural choice** (NumPy for the matrix multiply, nothing else). Any language with arrays works — the pure-Python version is instructive and slow.

## The build order

**1. Forward pass, one neuron.**
Inputs, weights, bias, weighted sum, activation. Hand-compute the output for a 2-input neuron and check your code matches.
*Works when:* your code agrees with your arithmetic on paper.

**2. A layer, then a network.**
A layer is a matrix multiply plus a bias vector. Stack two. **Get the shapes right and print them at every step** — shape errors are ~80% of the bugs in this project.
*Works when:* a random network turns a 784-vector into 10 numbers without a shape error.

**3. Loss.**
Softmax over the outputs, then cross-entropy against the true label.
*Works when:* an untrained network gives loss ≈ ln(10) ≈ 2.303. **If it doesn't, something is wrong before you've trained anything** — this is the single best early sanity check in the project.

**4. Backprop for one layer.**
The chain rule, applied backwards. Derive $\partial L/\partial W$ and $\partial L/\partial b$ on paper *first*, then code them.
*Works when:* **gradient checking passes** — see below. Do not skip this.

**5. Backprop through the whole network.**
Propagate the gradient backwards layer by layer, each layer receiving $\partial L/\partial(\text{its output})$ and producing $\partial L/\partial(\text{its input})$.
*Works when:* gradient checking passes for every parameter in a small network.

**6. Gradient descent.**
`W -= learning_rate * dW`. Train on 100 examples.
*Works when:* **loss on those 100 examples goes to nearly zero.** Overfitting a tiny set is the standard proof that learning works at all.

**7. Mini-batches and the full dataset.**
Batch 32–128 examples. Shuffle each epoch.
*Works when:* MNIST test accuracy > 90%.

**8. Make it better.**
ReLU instead of sigmoid, better initialisation (He/Xavier), momentum, then Adam.
*Works when:* > 95% test accuracy, and **you can say which change bought what**.

**9. Optional: a tiny autodiff engine.**
Rewrite so gradients are computed by a `Value`/`Tensor` class recording operations, rather than hand-derived per layer.
*Works when:* you can add a new operation and get its gradient without touching the training loop. **This is the step where PyTorch stops being mysterious.**

## Gradient checking — the technique that saves the project

**Your analytic gradient will be wrong, and the symptom is a network that trains badly rather than an error.** So verify it numerically:

$$\frac{\partial L}{\partial w} \approx \frac{L(w + \varepsilon) - L(w - \varepsilon)}{2\varepsilon}$$

Compare against your backprop gradient; relative error should be < 10⁻⁷.

**Use $\varepsilon \approx 10^{-5}$**, and know why: too large and truncation error dominates, too small and floating-point cancellation destroys it. **That's the U-curve from [[foundations/numerical-methods/11-practice-exercises|numerical methods exercise 1]]**, and this is the same problem in a different costume.

**Check a few parameters, not all of them** — it's O(n) forward passes per parameter.

## The parts that will bite you

**Shape errors, constantly.** Print `.shape` at every step. Decide early whether a batch is rows or columns and never waver.

**Forgetting to zero gradients** between batches — they accumulate, and the network diverges.

**Softmax overflow.** `exp(1000)` is `inf`. **Subtract the max before exponentiating** — mathematically identical, numerically essential. This is the single most common numerical bug in the project → [[foundations/numerical-methods/02-floating-point-and-error|floating point]].

**Log of zero** in cross-entropy → `-inf`. Clip, or use a fused log-softmax.

**All weights initialised to zero** — every neuron computes the same thing and stays identical forever. **Symmetry must be broken.** Initialise randomly, scaled by fan-in.

**Learning rate.** Too high diverges (loss → NaN); too low appears to do nothing. Try 0.001, 0.01, 0.1 and watch.

**Sigmoid saturation.** Large inputs give gradients near zero and learning stalls — the vanishing gradient problem, and the reason ReLU won.

## How to know it works

1. **Untrained loss ≈ ln(number of classes)**
2. **Gradient check passes**
3. **You can overfit 100 examples to ~zero loss.** If you can't, there's a bug — don't proceed to the full dataset
4. **Training loss decreases smoothly**
5. **> 95% MNIST test accuracy**
6. **Compare against PyTorch** — same architecture, same data. You should land within a couple of percent

## Where to stop

**Stop at MNIST.** The next steps — convolutions, GPUs, batch norm, transformers — teach far less per hour, because the *core* insight is already yours.

**You will have learned:** that backprop is the chain rule applied systematically, that a framework is bookkeeping around it, why initialisation and learning rate matter, and why loss curves look the way they do.

**The natural follow-on** is Karpathy's *Zero to Hero* series (micrograd → makemore → GPT), which starts roughly where step 9 ends.

## Related
- [[ai-ml/README|AI & ML]] — the 98 notes this makes concrete
- [[foundations/information-theory/04-cross-entropy-and-kl-divergence|cross-entropy]] — why that loss
- [[foundations/numerical-methods/10-numerical-optimisation|numerical optimisation]] — gradient descent properly
- [[foundations/gpu-and-parallel-computing/README|GPU]] — why the real ones run elsewhere

*Source: [reference] — build guide, Aug 2026.*
