# ML Engineering — Building With Code

Where Phase 1 was about understanding concepts, this folder is about the actual practice: preparing data, running a real training loop, evaluating honestly, and adapting an existing model rather than starting from zero. Everything here assumes the Phase 1 foundations — especially [[04-optimization|optimization]] — as background.

## Reading order

**Data** (`data/`)
1. [[01-missing-data-and-cleaning|missing-data-and-cleaning]] — **[Beginner]** — handling gaps, duplicates, and inconsistent values before anything else happens
2. [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]] — **[Intermediate]** — reshaping raw columns into a form a model can learn from well
3. [[03-train-val-test-splits|train-val-test-splits]] — **[Beginner]** — the honest-evaluation discipline everything downstream depends on

**Training** (`training/`)
4. [[01-training-loop-in-pytorch|training-loop-in-pytorch]] — **[Intermediate]** — the gradient descent loop from `optimization.md`, in real code
5. [[02-evaluation-metrics|evaluation-metrics]] — **[Intermediate]** — precision/recall/F1, MAE/MSE/R², and picking the right one
6. [[03-overfitting-and-regularization|overfitting-and-regularization]] — **[Intermediate]** — recognizing and fixing the most common practical failure mode

**Adapting existing models**
7. [[03-fine-tuning|fine-tuning]] — **[Advanced]** — specializing a pretrained model on your own data, full fine-tuning vs LoRA

## Related
- [[ai-ml/README|ai-ml curriculum map]] — all phases
- [[ai-ml/04-computer-vision/README|computer-vision]] — the same workflow, specialized for image data
- [[ai-ml/05-building-your-own-models/README|building-your-own-models]] — what comes after this: designing and training an architecture from scratch
