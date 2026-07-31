# Transfer Learning

Training a CNN from scratch on a modest dataset (a few thousand images) rarely works well — there's not enough data to learn good general-purpose filters from zero. Transfer learning sidesteps this: start from a model already trained on a huge, general dataset, and adapt it to a new, smaller, more specific task instead of starting from random weights. This is the computer-vision-specific version of the same idea covered generally in [[03-fine-tuning|fine-tuning]].

## Why it works — early layers are generic, later layers are specific

As covered in [[01-cnns|cnns]], a CNN's early layers learn broadly useful features (edges, textures, colors) regardless of the specific task, while later layers combine those into increasingly task-specific patterns. A model trained on a huge, diverse image dataset (commonly ImageNet, with over a million images across a thousand categories) has already learned excellent early-layer filters that are useful for almost any image task — reusing them means a new, smaller task only has to adapt the later, more specific layers.

## Two common strategies

**Feature extraction** — freeze the entire pretrained model, remove its final classification layer, and train only a new, small classifier on top of the frozen model's output features.

```python
import torchvision.models as models
import torch.nn as nn

model = models.resnet18(pretrained=True)
for param in model.parameters():
    param.requires_grad = False              # freeze everything

model.fc = nn.Linear(model.fc.in_features, num_new_classes)   # replace and train only the final layer
```

**Fine-tuning** (in the CNN-specific sense) — unfreeze some or all of the pretrained layers and continue training the whole thing (or the later portion of it) at a low learning rate, allowing the model to adapt its features more deeply to the new task, not just its final decision layer.

```python
for param in model.layer4.parameters():   # unfreeze just the last block, for instance
    param.requires_grad = True

optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-5)
```

## Choosing between the two

- **Feature extraction** — fastest, needs the least data, lowest overfitting risk; best when the new task is fairly similar to what the pretrained model originally learned from (e.g. classifying a new set of everyday object photos).
- **Fine-tuning (unfreezing layers)** — more flexible, can adapt more deeply to a task quite different from the original training data (e.g. medical imaging, satellite photos), but needs more data and a lower learning rate to avoid destroying the useful pretrained features (the same catastrophic-forgetting risk noted in [[03-fine-tuning|fine-tuning]]).

## Why a low learning rate specifically for unfrozen pretrained layers

The pretrained weights already encode a lot of useful structure — a large learning rate applied to them risks quickly wrecking that structure before the new task's signal has a chance to guide it constructively (see [[04-optimization|optimization]] for why learning rate size controls how disruptive each update step is). A common pattern is using a much smaller learning rate for unfrozen pretrained layers than for the newly added, randomly initialized layers.

## Gotchas

- Forgetting `for param in model.parameters(): param.requires_grad = False` before training the new final layer means the "frozen" base model actually still updates — usually not catastrophic with a small enough learning rate, but defeats the intended point of feature extraction and can overfit a small new dataset badly.
- Input preprocessing (resizing, normalization values — see [[02-image-data-and-augmentation|image-data-and-augmentation]]) must match what the pretrained model originally expects, not just whatever's convenient for the new dataset — mismatched preprocessing silently degrades the pretrained features' usefulness.

## Related
- [[01-cnns|cnns]]
- [[03-fine-tuning|fine-tuning]]
- [[02-training-from-scratch-vs-fine-tuning|training-from-scratch-vs-fine-tuning]]
