---
id: f46eb353-9800-4c4b-9e31-6b3968a7e38b
---

# What is a Model

A model is a function whose numbers were learned from examples.

## What a model is
<!-- bite: 8d3b43ff-1741-41fb-9b5d-b2bffceb2d89 -->

A model is a function with a huge number of adjustable numbers ("parameters" or "weights") whose values were set by feeding it examples, rather than hand-written by a programmer. That's it, mechanically — everything else (LLMs, image classifiers, recommendation engines) is a variation on "a big adjustable function plus a way of adjusting it."

The next bites take the parts one at a time: parameters, training vs inference, architecture, size, and generalization.

## Parameters / weights
<!-- bite: 29289151-d544-4cc0-b1e8-194cb9d67435 -->

Every parameter is just a number the model multiplies or adds somewhere internally while turning an input into an output. A model with "7 billion parameters" has 7 billion of these numbers. Before training, they're random noise; training's entire job is nudging them toward values that make the model's outputs match reality (see [[04-optimization|optimization]] for the mechanism). Nothing about a parameter is inherently meaningful on its own — the meaning is distributed across all of them together, which is exactly why individual weights inside a trained model are notoriously hard to interpret.

## Training vs inference — two completely different phases
<!-- bite: 5c821790-a19b-485b-91d1-ab13df58e2cb -->

- **Training**: showing the model many (input, correct-output) examples, computing how wrong its guess is, and adjusting parameters to reduce that error. Expensive — can take days to months of GPU time for large models — and happens once (or occasionally, to update the model).
- **Inference**: using an already-trained model to produce output for a new input. Cheap and fast relative to training, no parameter updates happen — this is what's running every time you chat with an LLM or run an image classifier on a new photo.

Confusing these two is a common source of misunderstanding — "training a model" and "using a model" (inference) are different operations with wildly different cost profiles, and a deployed product almost never trains live on your input (though some products do collect your input to potentially retrain a *future* version).

## Architecture — the shape of the function
<!-- bite: 04b9c3c6-dc26-4fa1-a59b-31ab015e6f88 -->

"Architecture" describes how the parameters are organized and connected — not their values, but the structure they sit in. A linear regression's architecture is a single weighted sum. A neural network's architecture is layers of weighted sums each followed by a nonlinear function, stacked on top of each other. A transformer (what LLMs are built from) is a specific architecture built around an "attention" mechanism that lets the model weigh how much every part of the input should influence every other part — enough of its own topic to warrant its own note in [[ai-engineering/02-how-llms-work/index|llms]] rather than covered fully here.

## Why "bigger model" isn't automatically "better model"
<!-- bite: 0f009e20-8b25-4b4c-a7d7-90be7dc0ebf5 -->

More parameters mean more capacity to represent complex patterns, but also:
- More data needed to set all those parameters meaningfully (an under-trained large model can underperform a smaller, well-trained one).
- More compute for both training and inference.
- More risk of **overfitting** — memorizing the training examples' quirks instead of learning the general pattern, which shows up as great performance on training data and poor performance on new data.

## Generalization — the actual goal
<!-- bite: 658c3463-d851-4471-86bf-ff9d9f337092 -->

The entire point of training isn't to get the right answer on the training examples (that's almost trivial to achieve by memorizing them) — it's to produce a model that performs well on inputs it has **never seen**. This is called generalization, and it's evaluated by holding back a chunk of data (the "test set") that the model never trains on, then checking performance there. Any time you hear "accuracy" or "loss" quoted for a model, the honest version of that number is measured on held-out data, not training data.

## Gotchas
<!-- bite: 393bd10b-cf38-4347-b3fc-e1a4ed668ab8 -->

- "The model has learned X" usually means "the model's parameters, after training, produce outputs correlated with X across the examples it saw" — not that it has an explicit, inspectable rule for X anywhere inside it.
- A model performing perfectly on its training data and poorly on new data is the textbook overfitting signature — not a sign of a "smart" model, the opposite.
- Inference isn't free of quirks either — the same trained model can give different-feeling answers depending on decoding settings (temperature, sampling strategy — see [[ai-engineering/02-how-llms-work/index|llms]]), which is a separate axis from anything learned during training.

## Check your understanding
<!-- bite: 2ccb2a32-fdeb-4aae-b114-b4c2f78f50fa -->

Try each one before you open the answer.

1. <!-- q: mcq id="54419df8" -->
   Mechanically, what is a model?

   - [ ] A set of if/else rules written by a programmer
   - [x] A function with many adjustable numbers whose values were set by learning from examples
   - [ ] A database of all the training examples
   - [ ] A program that searches the internet for answers

   <details><summary>Answer</summary>

   A function with many adjustable numbers (parameters or weights) whose values were learned from examples. Everything else, from LLMs to image classifiers, is a variation on that.

   </details>

2. <!-- q: mcq id="b66c3912" -->
   You chat with an LLM and it answers you. Which phase is that?

   - [ ] Training
   - [x] Inference

   <details><summary>Answer</summary>

   Inference: using an already-trained model on a new input. No parameters change. Training is the expensive phase where the parameters are adjusted, and it happens before you ever use the model.

   </details>

3. <!-- q: gap id="9a42c298" answers="overfitting|overfit" -->
   Fill in the gap. A model scores perfectly on its training data but badly on new data. It has memorized the quirks instead of the pattern. This is called ___.

   <details><summary>Answer</summary>

   Overfitting. It is not a sign of a smart model; it is the opposite.

   </details>

4. <!-- q: mcq id="e67353c2" -->
   Which of these are real costs of a bigger model? Choose all that apply.

   - [x] It needs more data to set all its parameters well
   - [x] It needs more compute for training and inference
   - [x] It has more risk of overfitting
   - [ ] It can no longer be used for inference

   <details><summary>Answer</summary>

   The first three. More parameters mean more capacity, but also more data, more compute and more risk of overfitting. A big model can still run inference; it just costs more.

   </details>

5. <!-- q: open id="d01d23ed" -->
   What is generalization, and why should a model's accuracy be measured on held-out data rather than on the training data?

   <details><summary>Answer</summary>

   Generalization is performing well on inputs the model has never seen, which is the real goal of training. Getting the training examples right is almost free, because the model can memorize them. So the honest number comes from a test set the model never trained on.

   </details>

## Related
<!-- bite: d3fd6674-fe3b-4bd4-b382-eaa90b3ff12f -->
- [[04-optimization|optimization]]
- [[ai-engineering/02-how-llms-work/index|llms]]
- [[ai-engineering/03-the-model-landscape|other-model-types]]
