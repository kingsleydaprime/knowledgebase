# Neural Network Fundamentals

**[reference]** — from the roadmap.sh `machine-learning` roadmap. The theory under the [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|PyTorch training loop]] — what a network is and how it learns.

## The perceptron — one neuron

The building block: a neuron takes inputs, multiplies each by a weight, sums them, adds a bias, and passes the result through an **activation function**:

```
output = activation( w₁x₁ + w₂x₂ + … + b )
```

That weighted sum is a [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot product]] — the same operation everywhere in ML. A single perceptron is just a linear classifier (it can only draw a straight boundary); its famous limitation is that it can't learn XOR. The fix is stacking neurons into layers.

## The multi-layer perceptron (MLP)

Stack neurons into **layers** — an input layer, one or more **hidden layers**, and an output layer — with every neuron in one layer connected to every neuron in the next. This is a **fully-connected** (dense) network, and with enough hidden units it's a *universal approximator*: it can represent essentially any function. "Deep" learning just means many layers, letting the network learn increasingly abstract features (early layers: edges/simple patterns; later layers: complex concepts).

## Activation functions — where non-linearity comes from

Without a non-linear activation between layers, stacking layers is pointless — a chain of linear operations collapses into a single linear one. Activations are what let networks learn non-linear patterns:

| Function | Shape | Use |
|---|---|---|
| **ReLU** (`max(0, x)`) | 0 for negatives, linear for positives | the default hidden-layer activation — cheap, avoids vanishing gradients |
| **Sigmoid** | squashes to (0, 1) | binary output as a probability; avoid in hidden layers (vanishing gradients) |
| **Softmax** | vector → probability distribution | multi-class output layer |
| **Tanh** | squashes to (−1, 1) | sometimes in RNNs |

ReLU's dominance in hidden layers is a big part of why deep networks became trainable — it doesn't saturate for positive values, so gradients flow.

## Forward propagation

**Forward pass**: feed the input through the layers — each layer computes its weighted sums and activations — until the output layer produces a prediction. Then a **loss function** measures how wrong that prediction is versus the true answer:

| Loss | For |
|---|---|
| **Cross-entropy** | classification (pairs with softmax/sigmoid) |
| **MSE** | regression |

## Backpropagation — how it learns

The core algorithm of deep learning. After the forward pass computes the loss, **backpropagation** works *backward* through the network computing the gradient of the loss with respect to every weight — how much each weight contributed to the error — by applying the [[ai-ml/00-foundations/03-mathematics/02-calculus/03-chain-rule|chain rule]] of calculus layer by layer. Then an **optimizer** (gradient descent and its variants — [[ai-ml/00-foundations/03-mathematics/04-optimization|optimization]]) nudges each weight in the direction that reduces the loss.

```
forward pass → compute loss → backpropagate (chain rule → gradients) → optimizer updates weights → repeat
```

That loop, run over many batches for many epochs, *is* training. Everything fancier — CNNs, transformers — is this same forward/backward/update loop with different layer types. Seeing it as real code is the whole point of the [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|PyTorch training loop]] note.

## Key training concepts

- **Epoch** — one full pass over the training data; **batch** — the subset processed before each weight update ([[ai-ml/00-foundations/03-mathematics/04-optimization|batches]]).
- **Learning rate** — how big each update step is; the single most important hyperparameter. Too high diverges, too low crawls.
- **Vanishing/exploding gradients** — in deep networks, gradients can shrink to nothing or blow up as they propagate back; ReLU, careful initialization, batch normalization, and residual connections are the fixes that made very deep networks trainable.
- **Regularization for nets** — dropout (randomly zeroing neurons during training) and weight decay (L2) fight [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting]], the same battle as everywhere.

## When to reach for deep learning

Neural nets earn their cost on **unstructured data** — images ([[ai-ml/02-ml-engineer/06-computer-vision/README|CNNs]]), text/sequences ([[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/README|transformers]]), audio — and huge datasets. On structured/tabular data, [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|gradient boosting]] usually wins for less cost. Match the tool to the data shape.

## Related
- [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|Training Loop in PyTorch]] — this as runnable code
- [[ai-ml/00-foundations/03-mathematics/02-calculus/03-chain-rule|Chain Rule]] — the calculus backprop is built on
- [[ai-ml/00-foundations/03-mathematics/04-optimization|Optimization]] — the gradient descent that updates weights
