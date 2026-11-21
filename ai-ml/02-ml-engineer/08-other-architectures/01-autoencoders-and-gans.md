---
id: 0e9f66cc-3aa4-4bb3-a07e-6e69a9d82164
---

# Autoencoders & GANs

## Autoencoders — learning compressed representations
<!-- bite: 26c0f949-3936-403b-b358-06671ce7ffd8 -->

An autoencoder is a network trained to **reconstruct its own input**, forced through a narrow middle layer (the *bottleneck*). It has two halves:

- **Encoder** — compresses the input into a small latent vector.
- **Decoder** — reconstructs the original from that vector.

```
input → [encoder] → latent (small) → [decoder] → reconstruction
                (loss = difference between input and reconstruction)
```

Because the bottleneck can't hold everything, the network is forced to learn a compressed, meaningful representation — the *neural, non-linear* counterpart to [[ai-ml/02-ml-engineer/03-classical-ml/04-unsupervised-clustering-and-pca|PCA]]. It's [[ai-ml/02-ml-engineer/01-foundations-of-ml/01-what-is-ml-and-types|unsupervised]] (the label is the input itself, a form of self-supervision). Uses:

- **Dimensionality reduction** and feature learning.
- **Anomaly detection** — train on normal data; anything that reconstructs *badly* is anomalous (fraud, defects).
- **Denoising** — train to reconstruct clean data from corrupted input.
- **Variational autoencoders (VAEs)** — a probabilistic variant whose latent space is smooth enough to *generate* new samples, an early generative model.

## GANs — generation by competition
<!-- bite: 364d641c-f69c-4a79-beb4-f4f48cf15393 -->

A **Generative Adversarial Network** pits two networks against each other:

- **Generator** — tries to produce fake data (e.g. images) that look real.
- **Discriminator** — tries to tell real data from the generator's fakes.

They train together in a contest: the generator gets better at fooling, the discriminator gets better at catching, and at equilibrium the generator produces convincingly realistic output.

```
random noise → [Generator] → fake image ─┐
                                          ├→ [Discriminator] → "real or fake?"
                real image ───────────────┘
```

GANs produced a leap in realistic image generation (faces, art, super-resolution, style transfer). The catch: they're **notoriously hard to train** — unstable, prone to "mode collapse" (generating only a few varieties), and sensitive to hyperparameters.

## Where these sit now
<!-- bite: aab0ca88-e6e1-4708-98e0-bd9ea6572c7e -->

Both matter to recognize, but the generative frontier has largely moved to **diffusion models** ([[ai-ml/03-ai-engineer/09-multimodal/index|multimodal]]), which are more stable to train and produce higher-quality, more diverse images — they power today's image generators. Autoencoders remain widely useful for representation learning, anomaly detection, and as components (the VAE in some diffusion pipelines); GANs remain relevant for specific generation and super-resolution tasks. The through-line — encoder/decoder and adversarial training — recurs across modern architectures.

## Related
<!-- bite: 1378fcc1-66e9-474a-8830-cf63a29bc178 -->
- [[ai-ml/02-ml-engineer/03-classical-ml/04-unsupervised-clustering-and-pca|Clustering & PCA]] — the linear version of dimensionality reduction
- [[ai-ml/03-ai-engineer/09-multimodal/index|Multimodal AI]] — diffusion models, the current generative frontier
- [[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|Neural Network Fundamentals]] — the building blocks

## About this lesson
<!-- bite: 3ff20df3-aadf-4d10-b9d2-54daf3d2a3fb -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. Two generative/representation architectures worth recognizing.
