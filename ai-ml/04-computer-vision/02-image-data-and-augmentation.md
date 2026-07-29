# Image Data & Augmentation

Preparing image data for training follows the same principles as [[03-train-val-test-splits|any other data]] — clean it, split it honestly — plus image-specific steps: consistent sizing, pixel value scaling, and augmentation to make limited data go further.

## Loading and preprocessing images

```python
from torchvision import transforms, datasets

transform = transforms.Compose([
    transforms.Resize((224, 224)),          # CNNs typically expect a fixed input size
    transforms.ToTensor(),                    # converts pixel values (0-255) to a tensor scaled to 0-1
    transforms.Normalize(                     # standardize per color channel — see feature-engineering-and-scaling
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

dataset = datasets.ImageFolder("data/train", transform=transform)
```

The normalization step here is exactly the standardization technique from [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]], applied per color channel instead of per tabular column — the underlying reason (putting values on a comparable scale for gradient-based training) is identical.

## Data augmentation — synthetically expanding a limited dataset

Rather than only ever seeing each training image exactly once per epoch in its original form, augmentation applies random, label-preserving transformations each time an image is loaded — a photo of a cat is still a cat whether it's flipped horizontally, slightly rotated, or has its brightness adjusted.

```python
augment = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])
```

This directly attacks [[03-overfitting-and-regularization|overfitting]]: a model trained on the same exact 1,000 images repeatedly can memorize their specific quirks, but a model that sees a different random variation of those images every epoch has a much harder time doing so, since the "noise" it might otherwise memorize keeps changing.

## Why augmentation choices should match the real-world task

Augmentation should only apply transformations that preserve the label in ways that reflect how the images will actually vary in the real deployment scenario. Flipping a photo of a handwritten digit horizontally can turn one valid digit into a completely different (or invalid) one — an augmentation that makes sense for photos of cats can be actively harmful for a different kind of image task. The choice of augmentations is a modeling decision, not a purely mechanical default.

## Class imbalance in image datasets

If some classes have far more training images than others (a medical dataset with 10,000 "healthy" scans and 50 "disease" scans), a model can achieve high accuracy by mostly ignoring the rare class entirely — the same imbalance problem covered generally in [[02-evaluation-metrics|evaluation-metrics]]. Common fixes: oversampling the rare class, undersampling the common class, or weighting the loss function to penalize mistakes on the rare class more heavily.

## Gotchas

- Computing normalization statistics (mean/std) from the training set only, then applying them unchanged to validation/test data — the same data-leakage discipline as [[01-missing-data-and-cleaning|missing-data-and-cleaning]], applies to images too.
- Augmentation should be applied to the **training set only** — validation and test data should reflect the real, unaltered distribution the model will actually be evaluated and deployed against.
- Overly aggressive augmentation can create unrealistic images that don't represent real deployment conditions, actively hurting rather than helping generalization.

## Related
- [[01-cnns|cnns]]
- [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]]
- [[03-overfitting-and-regularization|overfitting-and-regularization]]
