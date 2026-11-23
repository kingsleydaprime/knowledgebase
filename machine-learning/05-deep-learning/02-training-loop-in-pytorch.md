---
id: 97b942fd-5ea6-4b09-9c04-d0f45e2c5c88
---

# The Training Loop in PyTorch

The training loop is gradient descent written as real PyTorch code.

## What the training loop is
<!-- bite: 2a66b26e-fa0e-4bb2-a252-451330d4ac95 -->

[[04-optimization|Optimization]] describes gradient descent conceptually; this note is the same loop, in actual code. PyTorch is the most widely used deep learning framework for exactly this — it handles automatic differentiation (see [[03-chain-rule|chain-rule]]) so you write the forward pass and let the framework work out the gradients.

Next: the pieces of the loop, then the loop itself.

## The pieces
<!-- bite: 89880219-98cb-439d-a6f1-1324e87b5ff9 -->

```python
import torch
import torch.nn as nn

# 1. the model — a stack of layers (matrix multiplications + nonlinearities, see matrix-multiplication.md)
model = nn.Sequential(
    nn.Linear(10, 32),
    nn.ReLU(),
    nn.Linear(32, 1),
)

# 2. the loss function — what "wrong" means (see probability-and-statistics for why cross-entropy looks the way it does)
loss_fn = nn.MSELoss()

# 3. the optimizer — the update rule applied to the gradient (see optimization.md's "optimizer variants")
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
```

## The loop itself
<!-- bite: fc8bbd08-b6ae-4fc4-bf7a-79e394d99281 -->

```python
for epoch in range(num_epochs):
    for batch_inputs, batch_targets in dataloader:
        optimizer.zero_grad()                  # clear gradients from the previous step
        predictions = model(batch_inputs)       # forward pass
        loss = loss_fn(predictions, batch_targets)
        loss.backward()                          # backward pass — autodiff computes all gradients
        optimizer.step()                         # apply the update: params -= lr * gradient (Adam's version of this)
```

Each of these four lines inside the batch loop maps directly onto a step of gradient descent from [[04-optimization|optimization]]: compute predictions, measure the loss, compute gradients, apply the update. Nothing here is conceptually new — this is that exact loop, expressed in a framework that handles the derivative computation for you.

## Why `optimizer.zero_grad()` is easy to forget and breaks everything
<!-- bite: b35e5b1e-e05b-4343-8cf0-b93e2ba399f1 -->

PyTorch **accumulates** gradients by default rather than overwriting them on each `.backward()` call (useful for some advanced techniques, but not what you want in the basic loop). Skipping `zero_grad()` means each batch's gradient gets added on top of the previous batch's, silently corrupting training — a loss that behaves strangely or refuses to improve is a common symptom of this exact mistake.

## Epochs vs batches vs steps
<!-- bite: 2776849d-a200-4eb6-900f-7f32c147d11d -->

- **Batch** — one chunk of training data processed in a single forward/backward pass (see [[04-optimization|optimization]] for why training uses mini-batches rather than the whole dataset at once).
- **Epoch** — one full pass through the entire training dataset (every batch, once).
- **Step** — one single update to the parameters (one batch processed).

A dataset of 10,000 examples with a batch size of 100 means 100 steps per epoch — these numbers matter for both estimating training time and for setting learning rate schedules that change over the course of training.

## Moving to a GPU
<!-- bite: f1b004f7-5eda-48b0-9904-78071b8e77db -->

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
batch_inputs, batch_targets = batch_inputs.to(device), batch_targets.to(device)
```

Both the model's parameters and every tensor involved in a computation need to be on the same device (CPU or GPU) — a mismatch here (some tensors on GPU, others still on CPU) is one of the most common early errors when first running training on a GPU.

## Gotchas
<!-- bite: 752009a7-39ff-4f1d-a0e4-136c73a4b8da -->

- Forgetting `model.eval()` before evaluation and `model.train()` before resuming training changes behavior for certain layers (dropout, batch normalization) that behave differently between training and inference — a model evaluated without switching to `eval()` mode can give misleading validation numbers.
- A loss that becomes `NaN` partway through training is very often a learning-rate-too-high problem (see [[04-optimization|optimization]]) — lowering the learning rate is the first thing to try before suspecting the model architecture or data.
- Not wrapping evaluation code in `torch.no_grad()` wastes memory and time computing gradients that will never be used, since no training happens during evaluation.

## Check your understanding
<!-- bite: c6f81314-3d59-48f6-8883-59f901fef099 -->

Try each one before you open the answer.

1. <!-- q: exact id="0bc68005" answer="100" accept="one hundred" -->
   A dataset has 10,000 examples and the batch size is 100. How many steps are in one epoch?

   <details><summary>Answer</summary>

   100. 10,000 ÷ 100 = 100 batches, and each batch is one step.

   </details>

2. <!-- q: mcq id="0c7ac88d" -->
   What happens if you leave out `optimizer.zero_grad()`?

   - [ ] Nothing, PyTorch clears the gradients itself
   - [x] Each batch's gradient is added on top of the last, which silently corrupts training
   - [ ] The program crashes straight away

   <details><summary>Answer</summary>

   PyTorch accumulates gradients by default, so they pile up across batches. A loss that behaves strangely or refuses to improve is a common symptom.

   </details>

3. <!-- q: gap id="eb3d4994" answers="backward;step" -->
   Fill in the gaps. Inside the loop, `loss.___()` computes all the gradients, and `optimizer.___()` applies the update to the parameters.

   <details><summary>Answer</summary>

   `backward`, then `step`. The full order is: zero_grad, forward pass, loss, backward, step.

   </details>

4. <!-- q: mcq id="792c6c34" -->
   Before evaluating, what should you do? Choose all that apply.

   - [x] Call `model.eval()`
   - [x] Wrap the evaluation in `torch.no_grad()`
   - [ ] Call `loss.backward()`

   <details><summary>Answer</summary>

   `model.eval()` switches dropout and batch norm to inference behaviour, and `torch.no_grad()` stops PyTorch wasting memory on gradients you won't use.

   </details>

5. <!-- q: open id="18f66c75" -->
   You move the model to the GPU but get an error on the first batch. What is a likely cause?

   <details><summary>Answer</summary>

   The batch tensors are still on the CPU. The model's parameters and every tensor in the computation must be on the same device, so move the inputs and targets with `.to(device)` too.

   </details>

## Related
<!-- bite: 0511624b-6482-4fe0-86b3-a06a6834f1c7 -->
- [[04-optimization|optimization]]
- [[machine-learning/04-model-evaluation/01-evaluation-metrics-1|evaluation-metrics]]
- [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|overfitting-and-regularization]]
