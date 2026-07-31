# Overfitting & Regularization

Overfitting is when a model learns the training data's specific quirks and noise instead of the general pattern underneath it — it performs great on data it's already seen and poorly on new data. It's the single most common practical failure mode in applied ML, and most of what's called "regularization" exists specifically to fight it.

## Recognizing it

The textbook signature: training loss keeps dropping while validation loss flattens out or starts rising.

```
loss
 |  \                              training loss keeps falling
 |   \___________________________
 |
 |  \___
 |      \________/‾‾‾‾‾‾‾‾‾‾‾‾‾    validation loss bottoms out, then rises
 +------------------------------------> training progress
              ^
        overfitting starts around here
```

That growing gap between training and validation performance (see [[03-train-val-test-splits|train-val-test-splits]] and [[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|evaluation-metrics]]) is overfitting in numeric form — the model is still improving at fitting training data, but that improvement has stopped transferring to unseen data.

## The opposite failure — underfitting

A model that performs poorly on *both* training and validation data isn't overfitting — it's **underfitting**: too simple, or not trained long enough, to capture the real pattern in the data at all. The fix for underfitting (bigger model, more training, better features) is often the opposite of the fix for overfitting, so correctly diagnosing which one is happening matters before reaching for a fix.

## Regularization techniques

**L2 regularization (weight decay)** — add a penalty to the loss proportional to the size of the model's weights, discouraging any single weight from growing very large. Large weights tend to make a model extremely sensitive to small input changes — exactly the kind of fragile, memorization-prone behavior overfitting produces.

```python
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)  # PyTorch's built-in L2 penalty
```

**Dropout** — during training, randomly zero out a fraction of a layer's neurons on each forward pass, forcing the network to not rely too heavily on any single neuron or narrow path through the network. Disabled automatically at inference time (this is part of why `model.eval()` matters, see [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|training-loop-in-pytorch]]).

```python
nn.Dropout(p=0.5)   # zero out 50% of activations during training
```

**Early stopping** — track validation loss during training and stop (or restore the best-seen checkpoint) once it stops improving, rather than training for a fixed number of epochs regardless of what validation performance is doing. Directly targets the exact symptom shown in the loss-curve picture above.

**Data augmentation** — artificially expand the effective size/diversity of the training set (rotating/cropping images, paraphrasing text) so the model sees more variation and has a harder time simply memorizing exact training examples (covered concretely for images in [[02-image-data-and-augmentation|image-data-and-augmentation]]).

**More data** — often the single most effective fix, when available: a model has a much harder time memorizing noise in a dataset large enough that noise doesn't repeat in exploitable patterns.

## The bias-variance tradeoff, briefly

Underfitting is "high bias" (the model's assumptions are too simple to capture the pattern); overfitting is "high variance" (the model is too sensitive to the specific noise in this particular training set). Model complexity, training time, and regularization strength all trade off between these two failure modes — pushing too hard against one risks sliding into the other, which is why regularization strength is itself a setting to tune, not something to maximize blindly.

## Gotchas

- Adding regularization doesn't fix underfitting — if a model is already too simple or undertrained, more dropout or weight decay makes it worse, not better. Diagnose which failure mode is actually happening before choosing a fix.
- A model that looks great on the validation set after many rounds of tuning against that same validation set can still be subtly overfit *to the validation set* (see the gotcha in [[03-train-val-test-splits|train-val-test-splits]]) — the untouched test set is the real check.

## Related
- [[03-train-val-test-splits|train-val-test-splits]]
- [[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|evaluation-metrics]]
- [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|training-loop-in-pytorch]]
