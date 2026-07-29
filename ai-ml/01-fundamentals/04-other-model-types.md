# Other Model Types (Beyond LLMs)

"AI" in current conversation is dominated by LLMs, but they're one branch of a much wider tree. This is a map of the other major branches — enough to recognize what a given model is for and roughly how it works, without going deep into any one of them yet.

## Classic ML (non-deep-learning)

Models that don't use neural networks at all — often the right choice for structured/tabular data (spreadsheets of numbers, not raw text/images):

- **Linear/logistic regression** — fit a straight line (or its probability-flavored version) through the data. Fast, interpretable, a reasonable first thing to try.
- **Decision trees / random forests / gradient-boosted trees (XGBoost, LightGBM)** — learn a sequence of if/else splits on the features. Consistently strong on tabular data, often beating deep learning there while training in a fraction of the time.
- **k-means, clustering** — unsupervised grouping of data points by similarity, no labels needed.

These matter to know about specifically because deep learning isn't automatically the better tool — for structured business data with a moderate number of rows, a gradient-boosted tree model is often faster to build, cheaper to run, and more accurate than a neural network.

## Computer vision models

Models built to process images/video, historically dominated by **convolutional neural networks (CNNs)** — architectures built around scanning small local patches of an image (edges, textures) and building up to recognizing larger structures (shapes, objects) in deeper layers. Newer vision models increasingly use transformer-style attention (Vision Transformers / ViT) instead of or alongside convolutions. Common tasks: classification ("what's in this image"), object detection ("where are the objects, with bounding boxes"), segmentation ("which exact pixels belong to which object").

## Diffusion models

The dominant approach behind current image/video/audio generation (Stable Diffusion, Midjourney's underlying tech, Sora-style video models). The core idea: train a model to reverse a process of gradually adding random noise to an image until it's pure static — once it can reliably remove a little noise at a time, starting from *pure* noise and repeatedly denoising produces a coherent generated image. Conceptually very different from an LLM's next-token prediction, even though both get called "generative AI."

## Embedding models

Models whose entire output is a vector (see [[01-vectors|vectors]]) representing the *meaning* of an input — a sentence, an image, a product description — such that similar inputs produce similar vectors. This isn't for generating anything; it's for **comparison and search**. Semantic search, recommendation systems, and RAG (retrieval-augmented generation for LLMs) all depend on embeddings: convert a query and a database of documents into vectors, then find the closest ones by dot product / cosine similarity (see [[03-llms|llms]] for how this plugs into working around context window limits).

## Speech models

- **Speech-to-text (ASR)** — audio in, transcribed text out (Whisper is the well-known open example).
- **Text-to-speech (TTS)** — text in, synthesized audio out.
Both have converged toward transformer-based architectures too, following the same trend as vision.

## Recommendation systems

Models that predict which items a user is likely to want, typically by learning embeddings for both users and items such that a user's embedding is close (by dot product) to items they'd like — collaborative filtering (using patterns across many users) is the classic approach, often blended with content-based signals (features of the item itself).

## Reinforcement learning (RL)

A fundamentally different training paradigm from everything above: instead of learning from a fixed dataset of correct answers, an RL agent learns by taking actions in an environment and receiving a reward signal, adjusting its behavior to maximize cumulative reward over time. Used for game-playing agents (AlphaGo), robotics, and — notably — as part of how LLMs are instruction-tuned (RLHF: reinforcement learning from human feedback, mentioned in [[03-llms|llms]]).

## Why this map matters

The practical skill isn't memorizing every architecture — it's recognizing **what kind of input/output a problem has**, which immediately narrows the field: structured numeric data → classic ML; images → CNN/ViT-based; generate new images/audio → diffusion; search/compare meaning → embeddings; sequential decision-making with a reward signal → RL; anything language-shaped → an LLM. See [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]] for turning this into an actual decision process.

## Related
- [[03-llms|llms]]
- [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]
- [[02-what-is-a-model|what-is-a-model]]
