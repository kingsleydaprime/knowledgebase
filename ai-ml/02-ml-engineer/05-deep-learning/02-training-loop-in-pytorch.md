# The Training Loop in PyTorch

[[04-optimization|Optimization]] describes gradient descent conceptually; this note is the same loop, in actual code. PyTorch is the most widely used deep learning framework for exactly this — it handles automatic differentiation (see [[03-chain-rule|chain-rule]]) so you write the forward pass and let the framework work out the gradients.

## The pieces

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

PyTorch **accumulates** gradients by default rather than overwriting them on each `.backward()` call (useful for some advanced techniques, but not what you want in the basic loop). Skipping `zero_grad()` means each batch's gradient gets added on top of the previous batch's, silently corrupting training — a loss that behaves strangely or refuses to improve is a common symptom of this exact mistake.

## Epochs vs batches vs steps

- **Batch** — one chunk of training data processed in a single forward/backward pass (see [[04-optimization|optimization]] for why training uses mini-batches rather than the whole dataset at once).
- **Epoch** — one full pass through the entire training dataset (every batch, once).
- **Step** — one single update to the parameters (one batch processed).

A dataset of 10,000 examples with a batch size of 100 means 100 steps per epoch — these numbers matter for both estimating training time and for setting learning rate schedules that change over the course of training.

## Moving to a GPU

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
batch_inputs, batch_targets = batch_inputs.to(device), batch_targets.to(device)
```

Both the model's parameters and every tensor involved in a computation need to be on the same device (CPU or GPU) — a mismatch here (some tensors on GPU, others still on CPU) is one of the most common early errors when first running training on a GPU.

## Gotchas

- Forgetting `model.eval()` before evaluation and `model.train()` before resuming training changes behavior for certain layers (dropout, batch normalization) that behave differently between training and inference — a model evaluated without switching to `eval()` mode can give misleading validation numbers.
- A loss that becomes `NaN` partway through training is very often a learning-rate-too-high problem (see [[04-optimization|optimization]]) — lowering the learning rate is the first thing to try before suspecting the model architecture or data.
- Not wrapping evaluation code in `torch.no_grad()` wastes memory and time computing gradients that will never be used, since no training happens during evaluation.

## Related
- [[04-optimization|optimization]]
- [[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|evaluation-metrics]]
- [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting-and-regularization]]
