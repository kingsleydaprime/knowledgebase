# Distributed and Multi-GPU

**[Advanced]** — Scaling past one device. The parallelism strategies, collective operations, and why interconnect topology decides your architecture.

## Why one GPU isn't enough

**Two separate reasons, and they call for different strategies:**

**The model doesn't fit.** A 70B-parameter model at BF16 is 140 GB of weights alone — and training needs gradients, optimizer states and activations on top, typically **4–6× the parameter memory.** An 80 GB H100 can't hold it.

**Training takes too long.** The model fits, but a single device would take months.

> **These have different answers.** *Doesn't fit* → **model/tensor/pipeline parallelism.** *Too slow* → **data parallelism.** **Large training runs use several at once**, and the combination is called 3D parallelism.

## Data parallelism

**Replicate the model on every device; split the batch.**

```
 GPU 0: model copy, batch chunk 0 ──┐
 GPU 1: model copy, batch chunk 1 ──┤ ALL-REDUCE gradients
 GPU 2: model copy, batch chunk 2 ──┤ then each applies the same update
 GPU 3: model copy, batch chunk 3 ──┘
```

**Each device computes gradients on its shard; an all-reduce averages them; every device applies the identical update.**

**The simplest strategy and the first to reach for.** `torch.nn.parallel.DistributedDataParallel`.

**The costs:**

**The whole model must fit on each device.** Doesn't solve the memory problem at all.

**Gradient communication each step.** For a 1B-parameter model in FP16, that's **2 GB all-reduced every iteration.**

**Effective batch size grows with device count**, which changes the optimisation problem — you need learning-rate scaling and warmup, and past a point large batches generalise worse.

**Key optimisation: overlap communication with backward computation.** Gradients for the last layer are ready before the first layer's are computed, **so start reducing them immediately.** DDP does this via gradient bucketing, and it hides most of the communication cost.

### ZeRO / FSDP

**The refinement that made data parallelism memory-efficient.**

**Standard data parallelism replicates optimizer states, gradients and parameters on every device — enormously redundant.** Adam keeps two moments per parameter in FP32, so **optimizer state alone is ~12 bytes per parameter.**

**ZeRO shards them:**

| Stage | Shards | Memory saving |
|---|---|---|
| **ZeRO-1** | optimizer states | ~4× |
| **ZeRO-2** | + gradients | ~8× |
| **ZeRO-3 / FSDP** | **+ parameters** | **linear in device count** |

**ZeRO-3 gathers each layer's parameters just before use and frees them after** — so no device ever holds the whole model. **The cost is extra communication**, traded against memory.

> **FSDP (PyTorch) and DeepSpeed ZeRO are the standard tools for training models that don't fit.** **ZeRO-3 makes data parallelism work for arbitrarily large models**, at the price of more collective traffic per step. It's the default starting point now, ahead of manual model parallelism.

## Model and tensor parallelism

**Split the model itself across devices.**

**Tensor parallelism** — split individual operations. A matrix multiply $XW$ splits $W$ by columns; each device computes part of the output, then an all-gather combines.

**Used within a node**, because it needs an all-reduce **per layer** — very high communication, only viable over NVLink.

**Megatron-LM's approach**, and it's standard for large transformer training.

**Pipeline parallelism** — split by *layers*. Device 0 gets layers 1–8, device 1 gets 9–16, and activations pass along.

**The problem is the bubble** — devices idle while waiting:

```
 naive:      GPU0: [F1]......[B1]
             GPU1: ....[F1]...[B1]....      ← mostly idle

 microbatched: GPU0: [F1][F2][F3][B1][B2][B3]
               GPU1:   [F1][F2][F3][B1][B2][B3]
```

**Splitting the batch into microbatches keeps the pipeline full.** GPipe, PipeDream, and interleaved schedules reduce the bubble further. **Bubble fraction ≈ $(P-1)/M$** for $P$ stages and $M$ microbatches — so you want many microbatches.

**Expert parallelism (MoE)** — different experts on different devices, with a router sending each token to a few. **Scales parameters without scaling per-token compute**, and the difficulty is load balancing across experts.

**The standard combination for very large models — 3D parallelism:**

```
 tensor parallel   WITHIN a node   (NVLink, highest bandwidth)
 pipeline parallel ACROSS nodes    (fewer, larger messages)
 data parallel     ACROSS replicas (gradient all-reduce)
```

> **The mapping to hardware is the design.** Tensor parallelism demands the fastest link, so it goes inside a node. Pipeline parallelism sends less data, so it tolerates slower interconnect. **Getting this wrong — tensor parallelism across an Ethernet boundary — can cost you most of your throughput.**

## Collective operations

**The primitives, and they're the same set MPI standardised decades ago.**

| Operation | Effect |
|---|---|
| **Broadcast** | one → all |
| **Reduce** | all → one, combined |
| **All-reduce** | all → all, combined. **The one that matters for training** |
| Scatter | one splits to all |
| Gather / All-gather | all → one / all → all |
| **Reduce-scatter** | reduce, then each keeps a shard |

**All-reduce = reduce-scatter + all-gather**, which is how it's implemented.

**Ring all-reduce** is the standard algorithm:

**Each device sends to its neighbour in a ring, $2(N-1)$ steps.** Each device sends $\frac{N-1}{N}\times$ the data.

> **The important property: bandwidth cost is independent of $N$.** Adding devices doesn't increase per-device traffic — **which is what makes data-parallel training scale to thousands of GPUs.** It's why Baidu's 2017 ring all-reduce paper mattered so much, and NCCL implements this plus tree algorithms for small messages.

**NCCL** is NVIDIA's implementation, topology-aware, using NVLink where available and InfiniBand between nodes. **RCCL is the AMD equivalent; MPI the HPC standard.**

## Interconnect

**The hardware that determines what's feasible.**

| Link | Bandwidth | Scope |
|---|---|---|
| **NVLink 4** | 900 GB/s | GPU↔GPU in a node |
| **NVSwitch** | all-to-all NVLink | within a node/pod |
| PCIe 5.0 x16 | ~50 GB/s | GPU↔CPU |
| **InfiniBand NDR** | ~50 GB/s | node↔node |
| 100 GbE | ~12 GB/s | node↔node |

> **NVLink is ~20× PCIe.** That single ratio is why an 8-GPU NVLink node is a fundamentally different machine from 8 GPUs on PCIe, and why tensor parallelism is confined inside a node.

**GPUDirect RDMA** lets the network card write straight into GPU memory, **bypassing the CPU and host memory entirely** — essential for multi-node training.

**Topology matters.** Check `nvidia-smi topo -m` — it shows which GPU pairs share NVLink versus routing through PCIe or across sockets. **Placing communicating ranks on poorly-connected pairs is a real and easily-avoided loss.**

## Inference at scale

**Different constraints from training** — latency matters, batches are dynamic, and the model is fixed.

**Quantisation** — INT8, FP8, or 4-bit weights. **Weights dominate memory in inference, and 4-bit quantisation makes a 70B model fit on one 48 GB card.** GPTQ, AWQ, bitsandbytes.

**KV cache management** is the central problem for LLM serving. **The cache grows with sequence length and batch size, and naive allocation fragments badly.** **PagedAttention (vLLM)** applies [[foundations/os/04-virtual-memory|virtual-memory paging]] to the KV cache — non-contiguous blocks with a page table — and dramatically improves throughput. **A genuinely elegant borrowing from OS design.**

**Continuous batching** — add and remove sequences from a batch as they arrive and finish, rather than waiting for a whole batch. **Large throughput win** for serving, and standard in vLLM and TGI.

**Speculative decoding** — a small draft model proposes several tokens, the large model verifies them in one forward pass. **2–3× on latency with identical output distribution.**

**Tensor parallelism for inference** when the model doesn't fit, accepting the per-layer communication cost.

→ [[ai-ml/03-ai-engineer/16-local-and-open-models|Local and Open Models]]

## Failure and scale

**At hundreds of GPUs for weeks, hardware failure is a certainty, not a risk.**

**Checkpointing** — save state regularly. **Sharded checkpoints** so each rank writes its own portion, and asynchronous writes so training doesn't stall.

**Elastic training** — continue with fewer workers after a failure rather than crashing. `torchrun` supports it.

**Straggler detection.** One slow GPU (thermal throttling, a bad link) **slows every collective**, because all-reduce waits for the slowest participant. **Monitor per-rank step times.**

**Determinism is hard.** Different device counts change reduction order, and floating-point addition isn't associative. **Bit-exact reproducibility across cluster sizes is generally not achievable** — and this is the same non-associativity from [[foundations/numerical-methods/02-floating-point-and-error|note 02]], at scale.

> **Large training runs are distributed systems**, with all that implies: partial failure, stragglers, coordination overhead, and the need for observability. → [[architecture/04-distributed-systems/README|Distributed Systems]]

## Practical notes

**Scale up before scaling out.** One 8-GPU NVLink node beats eight single-GPU nodes for almost anything, because the interconnect is 20× better.

**Start with DDP, move to FSDP when memory forces it.** Don't reach for model parallelism until data parallelism genuinely can't work.

**Profile the communication.** Nsight Systems shows NCCL operations on the timeline — **if you're spending 40% of the step in all-reduce, that's the problem**, not your kernels.

**Overlap communication with computation.** Usually automatic in DDP/FSDP; verify it's happening.

**Check `nvidia-smi topo -m`** before assuming your GPUs are well connected.

**Use gradient accumulation** to get a large effective batch without the memory — several forward/backward passes before one optimizer step.

**Watch for stragglers** and for thermal throttling.

**Test checkpoint *restore*, not just save.** Same argument as [[databases/10-durability-and-recovery|backups]] — an untested restore path is not known to work, and finding out three weeks into a training run is expensive.

---

## Related
- [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|Performance and the Roofline]] — single-device optimisation first
- [[architecture/04-distributed-systems/README|Distributed Systems]] — the general theory
- [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]] — running training at scale
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel map]]
