# Linear Algebra for AI/ML

Linear algebra is the language ML is written in because data and model parameters are almost always represented as vectors and matrices, and "run the model" almost always reduces to matrix multiplication. You don't need a full linear algebra course to get productive — you need to be fluent in the four notes below, and more importantly, *what each operation represents*, not just how to compute it.

## Reading order
1. [[01-vectors|vectors]] — **[Beginner]** — a list of numbers representing a data point, an embedding, or a direction
2. [[02-matrices|matrices]] — **[Beginner]** — a table of data, or a transformation — both readings matter
3. [[03-dot-product|dot-product]] — **[Intermediate]** — the operation that measures how aligned two vectors are; the basis of similarity/search
4. [[04-matrix-multiplication|matrix-multiplication]] — **[Intermediate]** — dot products, batched — what a neural network's forward pass actually is

## What you don't need to memorize upfront

Eigenvalues, singular value decomposition, and most of a formal linear algebra course are used *inside* specific algorithms (PCA for dimensionality reduction, for instance) but aren't needed to understand how a neural network works day-to-day. The four notes above cover the vast majority of what shows up when reading about how models work; treat anything beyond them as "look it up when a specific technique needs it," not a prerequisite to start.

## Related
- [[ai-ml/00-foundations/03-mathematics/02-calculus/README|calculus]] — the other half of how training actually works
- [[ai-ml/00-foundations/02-what-is-a-model|what-is-a-model]]
- [[ai-ml/03-ai-engineer/02-how-llms-work|llms]] — embeddings and attention are built directly on these operations
