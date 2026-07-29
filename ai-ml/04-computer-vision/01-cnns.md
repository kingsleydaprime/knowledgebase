# Convolutional Neural Networks (CNNs)

A CNN is a neural network architecture built around scanning small local patches of an image with a shared, learned filter, rather than treating every pixel as an independent input the way a plain fully-connected layer would. That single design choice — reusing the same small filter across the whole image — is what makes CNNs practical for images at all, and it's built directly on the [[04-matrix-multiplication|matrix multiplication]] covered in the maths notes.

## Why not just use a plain fully-connected layer on raw pixels?

A modest 224×224 color image has over 150,000 individual pixel values. A fully-connected layer connecting every pixel to even a modest number of neurons would need an enormous number of parameters — and worse, it would treat a cat in the top-left corner of an image as a completely different pattern from the same cat shifted to the bottom-right, since a plain layer has no built-in notion that "the same pattern can appear anywhere in the image." Convolution solves both problems: far fewer parameters (one small filter, reused everywhere) and a filter that recognizes a pattern regardless of where in the image it appears.

## The convolution operation

A filter (a small grid of numbers, say 3×3) slides across the image, and at each position, computes a [[03-dot-product|dot product]] between the filter and the patch of image underneath it, producing one output value per position.

```
image patch:      filter:          dot product:
1 2 0             1 0 -1
3 1 2      x      1 0 -1     ->    (1*1+2*0+0*-1) + (3*1+1*0+2*-1) + (0*1+1*0+2*-1)
0 1 2             1 0 -1           = 1 + 1 + (-2) = 0
```

Different filters detect different patterns — one might respond strongly to vertical edges, another to a particular texture. Early in training these filters are random; training (via [[03-chain-rule|backpropagation]], same as any other layer) shapes them into detectors for whatever patterns are actually useful for the task.

## Layers get more abstract with depth

Early convolutional layers tend to learn simple, general patterns — edges, corners, color blobs. Layers deeper in the network combine those into increasingly complex, task-specific patterns — textures, then parts (an eye, a wheel), then whole objects. This progressive abstraction is exactly what makes [[03-transfer-learning|transfer learning]] work: the early layers' edge/texture detectors are useful for almost any image task, so they don't need to be relearned from scratch for a new problem.

## Pooling — shrinking the representation

Between convolutional layers, a pooling operation (commonly max pooling: take the largest value in each small region) reduces the spatial size of the representation, cutting computation for later layers and adding a degree of tolerance to small shifts/distortions in exactly where a pattern appears.

```python
import torch.nn as nn

model = nn.Sequential(
    nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(kernel_size=2),      # halves the spatial dimensions
    nn.Conv2d(16, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(kernel_size=2),
    nn.Flatten(),
    nn.Linear(32 * 56 * 56, 10),       # final classification layer, exact size depends on input dimensions
)
```

## Vision Transformers — the newer alternative

More recent vision models increasingly use the same attention mechanism LLMs use (see [[03-llms|llms]]) instead of, or alongside, convolution — splitting an image into fixed-size patches, treating each patch like a "token," and applying self-attention across them. CNNs remain common, well-understood, and often more data-efficient for smaller datasets; Vision Transformers tend to need more training data to reach their full potential but can outperform CNNs at scale.

## Gotchas

- Input images need consistent sizing before batching (resize/crop to a fixed resolution) — a CNN's later fully-connected layers are usually tied to a specific expected input size, so mismatched dimensions are a common early error.
- Very deep CNNs face the same vanishing-gradient risk as any very deep network (see [[03-chain-rule|chain-rule]]) — modern architectures address this with residual/skip connections, worth recognizing by name even without implementing one from scratch immediately.

## Related
- [[02-image-data-and-augmentation|image-data-and-augmentation]]
- [[03-transfer-learning|transfer-learning]]
- [[04-matrix-multiplication|matrix-multiplication]]
