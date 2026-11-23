---
id: c533c578-58a4-4bff-b6bd-eaee64155392
---

# Image Data & Augmentation

Image data needs a few extra preparation steps before training.

## What preparing image data involves
<!-- bite: 0e899540-a791-435a-b1a5-b2df7cdeca9f -->

Preparing image data for training follows the same principles as [[03-train-val-test-splits|any other data]] — clean it, split it honestly — plus image-specific steps: consistent sizing, pixel value scaling, and augmentation to make limited data go further.

Next: loading and preprocessing images, then augmentation.

## Loading and preprocessing images
<!-- bite: 75231846-969c-4ad7-8b56-9af610ca6b11 -->

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
<!-- bite: 3b225583-281d-4a16-85d7-decdc83537b4 -->

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

This directly attacks [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|overfitting]]: a model trained on the same exact 1,000 images repeatedly can memorize their specific quirks, but a model that sees a different random variation of those images every epoch has a much harder time doing so, since the "noise" it might otherwise memorize keeps changing.

## Why augmentation choices should match the real-world task
<!-- bite: 579eb950-9625-4424-999d-65eb59644f45 -->

Augmentation should only apply transformations that preserve the label in ways that reflect how the images will actually vary in the real deployment scenario. Flipping a photo of a handwritten digit horizontally can turn one valid digit into a completely different (or invalid) one — an augmentation that makes sense for photos of cats can be actively harmful for a different kind of image task. The choice of augmentations is a modeling decision, not a purely mechanical default.

## Class imbalance in image datasets
<!-- bite: affccdbe-0e3e-4a72-9d88-75b7691b46ed -->

If some classes have far more training images than others (a medical dataset with 10,000 "healthy" scans and 50 "disease" scans), a model can achieve high accuracy by mostly ignoring the rare class entirely — the same imbalance problem covered generally in [[machine-learning/04-model-evaluation/01-evaluation-metrics-1|evaluation-metrics]]. Common fixes: oversampling the rare class, undersampling the common class, or weighting the loss function to penalize mistakes on the rare class more heavily.

## Gotchas
<!-- bite: d374fa13-4d3a-49de-87ec-060b2a8a499c -->

- Computing normalization statistics (mean/std) from the training set only, then applying them unchanged to validation/test data — the same data-leakage discipline as [[01-missing-data-and-cleaning|missing-data-and-cleaning]], applies to images too.
- Augmentation should be applied to the **training set only** — validation and test data should reflect the real, unaltered distribution the model will actually be evaluated and deployed against.
- Overly aggressive augmentation can create unrealistic images that don't represent real deployment conditions, actively hurting rather than helping generalization.

## Check your understanding
<!-- bite: 55e76fce-6b00-4b67-9758-a4d681407e21 -->

Try each one before you open the answer.

1. <!-- q: mcq id="ef4aea96" -->
   Which sets should augmentation be applied to?

   - [x] The training set only
   - [ ] Training and validation
   - [ ] All three sets

   <details><summary>Answer</summary>

   Training only. Validation and test data should reflect the real, unaltered images the model will face.

   </details>

2. <!-- q: mcq id="a1b559b7" -->
   You are training a handwritten digit classifier. Which augmentation is risky?

   - [ ] A small rotation
   - [x] A horizontal flip
   - [ ] A small brightness change

   <details><summary>Answer</summary>

   The horizontal flip. Flipping a digit can turn it into a different or invalid digit, so it doesn't preserve the label. Augmentations must match how real images vary.

   </details>

3. <!-- q: gap id="64cbf1df" answers="0;1" -->
   Fill in the gap. `transforms.ToTensor()` turns pixel values from the range 0–255 into the range ___ to ___.

   <details><summary>Answer</summary>

   0 to 1. Then `Normalize` standardizes each colour channel.

   </details>

4. <!-- q: mcq id="37389bb2" -->
   A dataset has 10,000 healthy scans and 50 disease scans. Which are common fixes? Choose all that apply.

   - [x] Oversample the rare class
   - [x] Undersample the common class
   - [x] Weight the loss to punish mistakes on the rare class more
   - [ ] Report accuracy only

   <details><summary>Answer</summary>

   The first three. Accuracy alone hides the problem: a model can score very high by ignoring the rare class.

   </details>

5. <!-- q: open id="160f6e36" -->
   How does augmentation fight over-fitting?

   <details><summary>Answer</summary>

   The model sees a different random variation of each image every epoch, so the quirks it might memorize keep changing. It is much harder to memorize the exact training images, so it has to learn the general pattern.

   </details>

## Related
<!-- bite: b4bc067c-b06e-42e8-a955-4ab5d53a79ef -->
- [[01-cnns|cnns]]
- [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]]
- [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|overfitting-and-regularization]]
