# Fine-Tuning

[[05-open-source-models|Open-source-models]] introduced fine-tuning as a reason to prefer open weights; this note is the practical side — what actually happens when you fine-tune, and the decisions involved. Fine-tuning means taking an already-trained model and continuing training on a smaller, specific dataset, so it specializes toward a particular task or domain without starting from random weights.

## Why fine-tuning works so much faster than training from scratch

A pretrained model already encodes a huge amount of general structure — grammar and world knowledge for an LLM, edge/shape/texture detectors for a vision model (see [[03-transfer-learning|transfer-learning]] for the vision-specific version of this same idea). Fine-tuning only has to adjust that existing structure toward a narrower task, rather than learning everything from zero — which is why it needs far less data and far less compute than training from scratch (see [[02-training-from-scratch-vs-fine-tuning|training-from-scratch-vs-fine-tuning]] for when full training is still the right call).

## Full fine-tuning vs parameter-efficient fine-tuning

**Full fine-tuning** updates every parameter in the model — most accurate in principle, but requires enough memory to store gradients for the entire model (often far more memory than just running inference needs), making it impractical for very large models on modest hardware.

**LoRA (Low-Rank Adaptation)** and similar parameter-efficient methods freeze the original model's weights entirely and train a small number of additional parameters injected alongside them, which get combined with the frozen weights at inference time. Training a few million additional parameters instead of billions makes fine-tuning feasible on a single consumer GPU, at a small cost in flexibility versus full fine-tuning.

```python
# conceptual shape of a LoRA setup, not a specific library's exact API
base_model = load_pretrained_model()
for param in base_model.parameters():
    param.requires_grad = False          # freeze everything

lora_layers = attach_lora_adapters(base_model, rank=8)   # small additional trainable parameters
train(lora_layers, custom_dataset)                        # only these get updated
```

## Preparing data for fine-tuning

Fine-tuning data is typically much smaller than pretraining data but needs to be higher quality and closely shaped like the target task — for an LLM, this usually means (prompt, ideal response) pairs formatted consistently. The same data hygiene from [[01-missing-data-and-cleaning|missing-data-and-cleaning]] and [[03-train-val-test-splits|train-val-test-splits]] still applies: clean examples, a held-out validation set to check the fine-tuned model isn't overfitting to the small fine-tuning set specifically.

## When fine-tuning is (and isn't) the right call

Fine-tune when: the base model is broadly capable but needs to consistently follow a specific format, tone, or domain vocabulary that prompting alone doesn't reliably achieve, and you have at least a few hundred to a few thousand good-quality examples of the target behavior.

Don't reach for fine-tuning when: the actual problem is that the model lacks specific factual/current knowledge — that's a retrieval/grounding problem (see [[08-ai-tools-landscape|ai-tools-landscape]]), not a fine-tuning problem, since fine-tuning changes *behavior/style* far more reliably than it reliably injects new, precise factual knowledge. Also skip it when better prompting (see [[07-prompting|prompting]]) already solves the problem — fine-tuning is more expensive and less flexible than a well-crafted prompt, and isn't worth it if the cheaper option already works.

## Gotchas

- **Catastrophic forgetting** — fine-tuning too aggressively (too high a learning rate, too many epochs on a narrow dataset) can degrade the model's original general capabilities while it specializes, the same underlying failure mode as [[03-overfitting-and-regularization|overfitting]], just showing up as lost general ability rather than lost test-set accuracy.
- A small, unrepresentative fine-tuning dataset can teach a model bad habits just as easily as good ones — data quality matters more than data quantity here, unlike large-scale pretraining where quantity is often the bigger lever.

## Related
- [[05-open-source-models|open-source-models]]
- [[03-transfer-learning|transfer-learning]]
- [[02-training-from-scratch-vs-fine-tuning|training-from-scratch-vs-fine-tuning]]
