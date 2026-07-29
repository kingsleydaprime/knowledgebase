# Computer Vision

Applying the general ML engineering workflow (`ml-engineering/`) specifically to image data — a CNN is just a neural network architecture (see [[04-matrix-multiplication|matrix-multiplication]]) shaped around how images are structured, and everything else (data splits, evaluation, overfitting) still applies underneath it.

## Reading order
1. [[01-cnns|cnns]] — **[Intermediate]** — the convolution operation, why it beats a plain fully-connected layer on images, Vision Transformers as the newer alternative
2. [[02-image-data-and-augmentation|image-data-and-augmentation]] — **[Intermediate]** — loading, normalizing, and augmenting image datasets
3. [[03-transfer-learning|transfer-learning]] — **[Advanced]** — starting from a pretrained model instead of training from scratch, feature extraction vs fine-tuning

## Related
- [[ai-ml/03-ml-engineering/README|ml-engineering]] — the general workflow this specializes
- [[ai-ml/05-building-your-own-models/README|building-your-own-models]] — designing a new architecture rather than reusing an existing one
