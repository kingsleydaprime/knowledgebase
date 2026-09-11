# Build Your Own LLM

> **[Advanced]** · Tokeniser → attention → a transformer → training → sampling. **A few hundred lines, and the thing writes text. The sequel to guide 10.**

## What you're building

**A small transformer language model, trained from scratch**, that generates text one token at a time. Roughly 10 million parameters, trained in under an hour on one GPU, or overnight on a CPU. The architecture is the same one behind every model you have used — only the scale differs, and **scale is the least interesting difference.**

**And what you're deliberately not:** competing with anything, training at scale, doing reinforcement learning from human feedback, or building a chat assistant. **Your model will produce fluent nonsense.** That is the correct outcome: the grammar is learned, the knowledge is not, and seeing exactly which of the two falls out of the architecture is the lesson.

[[build-your-own-shit/10-your-own-neural-network|Guide 10]] stopped at a multilayer perceptron with hand-written backpropagation, which is where `ai-ml/`'s ~98 notes needed a build guide most. **This is where that guide was always heading.**

## What you need first

- **Backpropagation, written by hand at least once** — do [[build-your-own-shit/10-your-own-neural-network|guide 10]] first. This guide uses a framework's autodiff, and that is only safe if you have already written your own
- **The training loop in PyTorch** → [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|training loop]]
- **What a transformer is, and what attention computes** → [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|transformers and attention]]
- **How LLMs work at the level of the application** → [[ai-ml/03-ai-engineer/02-how-llms-work|how LLMs work]]
- **Matrix multiplication, and being able to track shapes** → [[mathematics/04-linear-algebra/01-matrices-and-determinants/01-matrices-and-determinants|matrices]]
- **Cross-entropy, which is the loss function and is not a coincidence** → [[information-theory/04-cross-entropy-and-kl-divergence|cross-entropy and KL divergence]]

**PyTorch is the right choice**, and using it here is not cheating — you wrote the autodiff in guide 10, and the subject of *this* guide is the architecture. JAX works. Writing it in raw NumPy is possible and mostly teaches you what you already learned in guide 10.

**Andrej Karpathy's *Let's build GPT* and `nanoGPT` are the references.** Two hours of video and about 300 lines of code, both free.

## The build order

**1. A tokeniser, and start at the character level.**
Map each distinct character to an integer. Shakespeare gives you a vocabulary of 65. It is trivially simple, it lets you skip straight to the model, and it works.

**Then implement byte-pair encoding properly**, because it explains a whole category of behaviour you have seen: start from bytes, repeatedly find the most frequent adjacent pair and merge it into a new token. **Tokenisation is why models are bad at arithmetic, bad at spelling, and bad at counting the letters in a word** — the model never sees letters, it sees chunks. This is a two-hour detour that permanently changes how you read model failures.
*Works when:* encode-then-decode is the identity for arbitrary text, and you can print the token boundaries of a sentence and be surprised by them.

**2. A bigram baseline — the whole training loop, with no model.**
A lookup table from token to next-token logits. Train it with cross-entropy and sample from it. It generates garbage.

**But it establishes everything else:** batching, the loss, the optimiser, the sampling loop and the evaluation. **And it gives you a number to beat.**
*Works when:* the loss falls from about 4.17 to about 2.5 on character-level Shakespeare, and the output is plausible-looking gibberish. (4.17 is $\ln 65$ — the loss of a uniform guess over 65 characters, and the value you should see at initialisation.)

**3. Self-attention, built up in four stages.**
Do not implement it in one go. Each stage should run:

1. **Average the previous tokens.** Each position takes the mean of every position before it. Crude, but it is communication between positions.
2. **Make the average a matrix multiply** with a lower-triangular matrix of weights. Same result, and now it is differentiable in a useful shape.
3. **Make the weights data-dependent.** Each token emits a **query** ("what am I looking for") and a **key** ("what do I contain"); their dot product is the affinity, softmaxed into weights, applied to **values**. This is attention.
4. **Scale by $1/\sqrt{d_k}$** before the softmax, or the dot products grow with dimension, the softmax saturates, and gradients vanish.

The causal mask — setting future positions to $-\infty$ before the softmax — is what makes it a language model rather than an encoder.
*Works when:* the loss beats the bigram baseline, and your attention weight matrix is visibly lower-triangular when you print it.

**4. Multiple heads.**
Run several attention operations in parallel with smaller dimensions, concatenate, project. **Different heads learn different relationships** — one tracks syntax, another matches quotes to their openers — and you can visualise this.
*Works when:* four heads beat one head at the same total parameter count.

**5. The block: attention, then a feed-forward layer.**
Attention moves information *between* tokens; the feed-forward network (an expansion to 4× the width and back) does the thinking *within* each token. Alternate them.

**Add residual connections and layer normalisation, and put the norm before each sub-layer, not after.** Then delete the residuals and watch a six-layer model fail to train at all. **That five-minute experiment is worth more than any explanation of why they exist.**
*Works when:* stacking six blocks improves the loss rather than making it worse.

**6. Positional embeddings.**
Attention is a weighted sum, so it is **permutation-invariant** — without positional information, "dog bites man" and "man bites dog" are literally the same input. Add a learned embedding per position.
*Works when:* removing them makes the loss noticeably worse. Do run that experiment; it is the clearest demonstration in the project.

**7. Scale it up and train properly.**
Six layers, six heads, 384 embedding dimensions, a context of 256 tokens, dropout at 0.2. Hold out a validation split. Warm up the learning rate, then decay it.
*Works when:* validation loss reaches about 1.48 on character-level Shakespeare and the samples have line breaks, speaker names and vaguely Elizabethan cadence. **It is meaningless text with perfect structure**, and that is exactly the point.

**8. Sampling, and the knobs you have used from the other side.**
Greedy decoding, then temperature, then top-k, then nucleus (top-p) sampling. **Generate from the same model at temperature 0.1 and at 1.5.** Every complaint you have ever had about a model being either boring or unhinged is visible in those two outputs, from a model whose weights did not change → [[ai-ml/03-ai-engineer/05-prompt-engineering|prompt engineering]].
*Works when:* you can predict which setting produced which sample.

**9. A KV cache.**
Naive generation re-runs the whole prefix for every new token, so producing $n$ tokens costs $O(n^2)$ forward passes' worth of work. Cache the keys and values per layer and each new token is $O(n)$.
*Works when:* generating 500 tokens is several times faster and the output is **identical** to the uncached version. That equality is the test.

**10. Optional: fine-tune it.**
Take your pretrained model and train it further on instruction-formatted pairs. **The base model completes text; the fine-tuned one answers.** Watching that change happen to a model you trained explains the difference between a base and an instruct model better than any diagram → [[ai-ml/02-ml-engineer/09-building-and-fine-tuning/02-training-from-scratch-vs-fine-tuning|training from scratch vs fine-tuning]].

**11. Optional: measure a scaling law.**
Train four models of increasing size on the same data and plot final loss against parameter count on log axes. **You will get a straight line.** Producing that line yourself is a different kind of knowing than reading that it exists.

## The parts that will bite you

**A loss that is suspiciously good means the mask leaks.** If the model can see even one future token, it will learn to copy it, and your loss will plummet while your samples stay terrible. **Test the mask directly:** change a token late in the sequence and confirm that the predictions at earlier positions do not move at all.

**Check the initial loss before training.** It should be $\ln(\text{vocabulary size})$ — about 4.17 for 65 characters, about 10.8 for a 50,000-token vocabulary. **Wrong initial loss means a bug in initialisation or in the loss itself**, and finding it now saves an hour of watching a run go nowhere.

**Overfit a single batch first.** Take one batch, turn off dropout, and train until the loss is near zero. If it cannot memorise ten examples it will never learn ten million, and this test takes thirty seconds. **It is the highest-value diagnostic in all of deep learning.**

**Shape confusion between batch, time and channel.** Almost every bug in this project is a transposed dimension that broadcasts silently instead of erroring. Write the expected shape as a comment on every line and check them.

**A small corpus overfits fast.** Train and validation loss diverging after a few thousand steps is expected, not a bug — but you must be watching both to see it.

**The model knows nothing.** It has grammar and cadence and no facts, because it never saw enough text to have any. **This is the most useful thing the project teaches**, and it should change how you think about what a much larger model is doing when it sounds confident.

## How to know it works

1. **Initial loss equals $\ln(\text{vocab size})$**
2. **It overfits a single batch to near-zero loss**
3. **It beats the bigram baseline**, comfortably
4. **Validation loss around 1.48** on character-level Shakespeare at the config above
5. **Ablations behave as predicted** — removing positional embeddings hurts, removing residuals breaks training entirely, one head is worse than four
6. **The KV cache produces byte-identical output** to the uncached path
7. **Samples have structure without meaning** — the signature of a model this size

## Where to stop

**Stop after sampling and the ablations.** You have then built the architecture and, more importantly, measured what each piece contributes.

**Not worth it here:** distributed training, mixed precision, FlashAttention, mixture of experts, or reinforcement learning from human feedback. Each is real and each is about *scaling* a thing you now understand rather than understanding it.

**You will have learned** what attention actually computes, why context length is quadratic and therefore expensive, why tokenisation causes the failures it causes, what temperature is a temperature *of*, and where the boundary sits between what the architecture gives you and what the data gives you. **Every article about LLMs becomes readable**, including the ones being vague on purpose — and [[ai-ml/03-ai-engineer/index|the AI engineer track]] stops being a set of APIs and becomes a set of consequences.

## Related

- [[build-your-own-shit/10-your-own-neural-network|Your Own Neural Network]] — the prerequisite, and where the backpropagation lives
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers and attention]] — the reference note for this guide
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG and embeddings]] — the natural next project, and the one `ai-ml/projects` names first
- [[information-theory/04-cross-entropy-and-kl-divergence|Cross-entropy]] — why the loss function is the one it is
- [[build-your-own-shit/index|Build Your Own Shit index]]

*Source: [reference] — build guide, Sep 2026.*
