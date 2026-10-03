# Local & Open Models

> **[Intermediate]** · Running a model on your own machine: when it's worth it, which runtime to use, whether a model will fit, what decides its speed, and how much context an agent framework eats before you type. The worked example is real — a study partner set up on a 16 GB laptop on 2026-10-02, with every number measured.

## Before you start

You can already:

- Explain tokens, the context window and why models are measured in parameters → [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]].
- Call a model over HTTP → [[ai-ml/03-ai-engineer/04-calling-models/index|calling models]].
- Run a command in a terminal and read a JSON response.

After this lesson you will be able to:

1. Decide whether a task justifies a local model instead of a hosted API.
2. Estimate a model's memory from its parameter count and quantisation, and pick one that fits your machine.
3. Read Ollama's timing output, and explain what decides speed on a laptop — including why thinking and partial GPU offload can slow it down.
4. Budget a context window for an agent framework, and scope a local agent's permissions.

**Study route.** The kid version and §1–3 are the background. §4–6 are the hands-on part, built on measurements. Run the worked example; the practice task is measuring your own machine.

## The kid version

A hosted model is like ordering food: someone else's kitchen, fast, and you pay per plate. A local model is cooking at home: free per meal, and private — but your kitchen is small. A big recipe won't fit on your counter, and a slow oven makes everything take longer. Running a model locally is mostly about **choosing a recipe your kitchen can actually handle**.

**Where the analogy stops working.** A kitchen that's too small just refuses the recipe. A computer that's too small doesn't refuse — it starts using the hard disk as overflow memory and becomes dramatically slower, with no error message. You have to do the arithmetic yourself, before you start.

## 1. Why this exists

Kingsley wanted an AI study partner that reads his knowledgebase, runs on his laptop, and costs nothing per question. The laptop already had two models pulled: `gemma4` (9.6 GB) and `qwen3.5` (6.6 GB). Neither was usable — with about 7 GB of RAM free, one didn't fit and the other left no room for anything else. The 4-billion-parameter model that did fit then took **four minutes** to answer "explain a token bucket in two sentences", and the agent built on it failed on the message "hi". Each problem had a measurable cause and a one-line fix. This lesson is those causes.

## Terms used in this lesson

1. **Open-weight model**: This is a model whose trained parameters you can download and run yourself. "Open weights" is not the same as open source, and not automatically free for commercial use.
2. **Parameter**: This is one learned number inside the model. Models are sized in billions — a "4B" model has about 4 billion.
3. **Quantisation**: This is storing each parameter in fewer bits — 4 or 8 instead of 16 — so the model takes less memory and runs faster, at a small cost in quality.
4. **GGUF**: This is the file format llama.cpp and Ollama use for quantised models. Names like `Q4_K_M` describe the quantisation.
5. **Runtime**: This is the program that loads a model and serves it — Ollama, LM Studio or llama.cpp on a laptop; vLLM or TGI on a server.
6. **Inference**: This is running a trained model to produce output, as opposed to training it.
7. **Prompt processing**: This is the model reading your whole prompt. It's fast because it handles many tokens at once. Ollama reports it as **prompt eval rate**.
8. **Generation**: This is the model producing its answer one token at a time. It's the slow part on a CPU. Ollama reports it as **eval rate**, in tokens per second.
9. **Offloading**: This is putting some of a model's layers on the GPU (graphics processor) and the rest on the CPU.
10. **KV cache (key–value cache)**: The letters stand for "key" and "value". It is memory the runtime keeps for every token in the context, so it grows with the context window.
11. **Thinking tokens**: This is also known as **reasoning**. These are tokens a reasoning model generates privately before its visible answer. They cost the same time as visible ones.
12. **Modelfile**: In Ollama, this is a short file that builds a named variant of a model with settings built in.

## 2. Why run a model yourself at all

The default for building is a hosted API — someone else runs the GPUs, you send tokens. Self-hosting an open-weight model ([[ai-ml/03-ai-engineer/03-the-model-landscape|the model landscape]]) is worth the extra effort when one of these dominates:

- **Privacy / data residency** — the data legally or contractually can't leave your infrastructure (health, legal, on-premises enterprise). This is the most common real reason.
- **Cost at high, steady volume** — past a certain sustained throughput, owning the hardware (or renting a fixed GPU) beats per-token pricing.
- **Control & no lock-in** — you pin the exact model version forever (hosted models get retired out from under you), and you can fine-tune it ([[ai-ml/03-ai-engineer/15-fine-tuning-applied|applied fine-tuning]]).
- **Offline / edge** — no network, or a latency requirement a round trip to the cloud can't meet.
- **Free, unlimited personal use** — a study partner you can ask a thousand questions without a bill, as in this lesson.

Against all that: you own the operations, and the best open models still trail the frontier closed models on the hardest tasks. **Prototype on an API; self-host when a concrete reason above forces it.**

## 3. Runtimes and quantisation

### On your own machine — Ollama, LM Studio, llama.cpp

- **Ollama** — the pragmatic default. `ollama run <model>` downloads a quantised model and serves it on `http://localhost:11434`, including an OpenAI-compatible endpoint, so existing SDK code works by changing the base URL.
- **LM Studio** — a desktop app over the same idea, for browsing and trying models without a terminal.
- **llama.cpp** — the C++ engine underneath much of the above. Use it directly for the most control, or to embed inference in an app.

### On a server, at scale — vLLM, TGI

Serving many users needs an **inference server**. **vLLM** manages the KV cache like virtual memory (PagedAttention) and slots new requests into running batches (continuous batching), which keeps a GPU busy. **TGI** is Hugging Face's equivalent. *Ollama is for you; vLLM is for your users.*

### Quantisation — what makes local possible

Full precision stores each parameter in 16 bits, so a 70B model needs about 140 GB. Quantising to 4 bits shrinks that about fourfold, with a small quality cost. **4-bit (`Q4_K_M`) is the usual sweet spot**; below 4 bits, quality drops in task-dependent ways. A well-quantised larger model usually beats a smaller full-precision one at the same memory. GGUF is the format for Ollama and llama.cpp; AWQ and GPTQ are common with vLLM.

## 4. Will it fit? Sizing a model to your machine

The memory for the weights is close to:

> **parameters × bits per weight ÷ 8** — so a 4B model at `Q4_K_M` (about 4.8 bits per weight on average) needs about 2.4 GB.

Then add:

- **The runtime and the KV cache**, which grows with the context window — budget at least a gigabyte or two.
- **Extra components.** Multimodal models carry an image (and sometimes audio) encoder. That's why `qwen3.5:latest` — 9.7B parameters, about 5.8 GB of weights by the formula — downloads at 6.6 GB.

And compare with **free** RAM, not total. On the 16 GB laptop, about 7 GB was free with everyday apps open:

| Model | Size | With ~7 GB free |
|---|---|---|
| `gemma4` (8B, with vision and audio) | 9.6 GB | Doesn't fit — swaps to disk and crawls |
| `qwen3.5:latest` (9.7B) | 6.6 GB | No headroom left |
| **`qwen3.5:4b`** | **3.4 GB** | **Fits, with room to spare** |

A model that "fits" only by pushing other apps into swap will run, slowly, with no error. Check `free -h`: if the **Swap used** column grows while the model runs, it doesn't really fit.

## 5. What decides the speed

`ollama run <model> --verbose` prints timing after each answer. From the laptop, CPU only, thinking off:

```
load duration:        23.0s      ← first message only: loading 3.4 GB from disk into RAM
prompt eval rate:     36.6 tokens/s   ← reading the prompt: many tokens at once
eval count:           83 token(s)
eval rate:            5.09 tokens/s   ← writing the answer: one token at a time
```

Four things moved those numbers:

1. **Generation is the bottleneck.** On a CPU, producing each token means reading the whole model's weights from memory, so speed is mostly limited by memory bandwidth — and is roughly the same whatever the question. Total time ≈ output tokens ÷ eval rate.
2. **Thinking tokens cost real time.** With thinking on, "two sentences" produced **1,087 tokens** at 4.59 per second: **3 minutes 57 seconds**, nearly all of it hidden reasoning. With thinking off, **83 tokens in 17.7 seconds**. Turn thinking on per question, when a question needs it.
3. **A weak GPU can make it slower.** Left to itself, Ollama put 10% of the model on the 2 GB MX130 and ran at **3.91 tokens/s**. Forced onto the CPU alone, **5.09** — about 30% faster. Moving data between CPU and a small GPU every token costs more than the GPU saves. On a GPU big enough to hold the *whole* model, the opposite is true.
4. **Load time is paid once per idle period.** Ollama unloads a model after 5 minutes idle by default; the next question pays the ~23-second load again. `OLLAMA_KEEP_ALIVE=30m` keeps it in memory longer, at the cost of holding that RAM.

Heat can also slow a laptop under sustained load (thermal throttling) — here the CPU stayed at 40–55 °C, so it wasn't a factor.

The fixes become a **Modelfile**: a named variant with the settings built in, used by `ollama run` and by anything calling Ollama's API:

```
FROM qwen3.5:4b
PARAMETER num_gpu 0          # CPU only
PARAMETER num_ctx 32768      # context window (Ollama's default is 4,096)
```

## 6. Context windows, agents, and permissions

**The context window must hold everything at once:** the system prompt, the tool descriptions, any file the model reads, the conversation, and space for the reply. Agent frameworks add a large fixed overhead before you type anything.

Measured from OpenClaw's own log: its prompt was **8,786 tokens with no messages**, and it reserved **8,384 tokens** for the reply. On a 16K window, that left a prompt budget of 16,384 − 8,384 = **8,000 tokens** — less than the overhead alone, so even "hi" overflowed. On 32K, the budget is about 24,000: room for the overhead, one lesson file (a 5,000-word lesson is about 6,500 tokens), and a conversation.

**Two more context traps:**
- **Ollama defaults to a 4,096-token window** unless the request or a Modelfile says otherwise — a long prompt can be cut short without an error.
- **Bigger windows cost memory**, through the KV cache. Size the window to what you'll actually send.

**Giving a local model tools is giving it your permissions.** An agent that can read files can read *every* file your account can, unless it's restricted. The study partner's agent therefore gets **only** the `read` tool — no shell, no web, no writing — and isn't connected to any chat app, because anyone who could message it could ask it to read `~/.ssh`. Small models are also easier to mislead with instructions hidden in content they read (prompt injection), which is why OpenClaw's own guidance for small local models is its most restrictive tool profile. The full setup: [[tools/openclaw-study-partner/index|OpenClaw study partner]].

## 7. Where to get models, and how this plugs into the track

**Hugging Face** is the hub: each open model in several formats and quantisations, with licences that vary and matter — "open weights" is not automatically "free for commercial use". Ollama's library re-packages popular models as ready-to-run tags such as `qwen3.5:4b`.

An OpenAI-compatible local endpoint means **almost nothing else changes**: [[ai-ml/03-ai-engineer/04-calling-models/index|calling models]], [[ai-ml/03-ai-engineer/11-structured-output/index|structured output]], [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|tool calling]], [[ai-ml/03-ai-engineer/06-rag-and-embeddings/index|retrieval]] and [[ai-ml/03-ai-engineer/12-evals/index|evals]] all work the same way, pointed at your own server. An [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|AI gateway]] then makes hosted ↔ local a configuration change, including falling back between them.

## Worked example — sizing and measuring

Two pieces: arithmetic you can do before downloading anything, and a script that measures a real model through Ollama's HTTP API.

```python
"""sizing.py — the arithmetic for running a model on your own machine: will it fit,
how long will it take, and does the prompt fit the context window."""

# Average bits stored per weight for common GGUF quantisations (they mix precisions internally).
BITS_PER_WEIGHT = {"Q8_0": 8.5, "Q6_K": 6.6, "Q5_K_M": 5.7, "Q4_K_M": 4.8, "Q3_K_M": 3.9}


def weights_gb(billions_of_params: float, quant: str) -> float:
    """Memory for the weights alone: parameters × bits per weight ÷ 8 bits per byte."""
    return round(billions_of_params * BITS_PER_WEIGHT[quant] / 8, 1)


def fits(model_gb: float, free_ram_gb: float, headroom_gb: float = 1.5) -> bool:
    """Leave headroom for the context cache and the runtime, or the system starts swapping."""
    return model_gb + headroom_gb <= free_ram_gb


def generation_seconds(output_tokens: int, tokens_per_second: float) -> float:
    """Output is produced one token at a time, so time is tokens ÷ rate."""
    return round(output_tokens / tokens_per_second, 1)


def prompt_budget(context_window: int, reserve_for_reply: int) -> int:
    """What's left for the prompt once the reply's space is set aside."""
    return context_window - reserve_for_reply


def fits_context(fixed_overhead: int, lesson_tokens: int, chat_tokens: int,
                 context_window: int, reserve_for_reply: int) -> bool:
    return fixed_overhead + lesson_tokens + chat_tokens <= prompt_budget(context_window, reserve_for_reply)


def words_to_tokens(words: int) -> int:
    """English averages roughly 1.3 tokens per word; code and markdown run higher."""
    return round(words * 1.3)
```

**Predict before running.** Using only the functions above: does `qwen3.5:latest` (6.6 GB) fit in 7 GB free with 1.5 GB of headroom? At 4.59 tokens/s, how long do 1,087 tokens take? Does an 8,786-token overhead fit a 16K window with 8,384 reserved?

```python
"""Every number here was measured on the laptop the study partner runs on (2026-10-02):
16 GB RAM with about 7 GB free, an i7-8650U, and a 2 GB MX130."""
import unittest

from sizing import (fits, fits_context, generation_seconds, prompt_budget, weights_gb,
                    words_to_tokens)


class SizingTests(unittest.TestCase):
    def test_weights_follow_parameters_times_bits(self):
        self.assertEqual(weights_gb(9.7, "Q4_K_M"), 5.8)   # qwen3.5:latest (9.7B) downloads at 6.6 GB:
        self.assertEqual(weights_gb(4.0, "Q4_K_M"), 2.4)   # the gap is the vision encoder and metadata
        self.assertEqual(weights_gb(4.0, "Q8_0"), 4.2)     # same model, 8-bit: almost twice the memory

    def test_what_fits_in_7_gb_free(self):
        self.assertFalse(fits(9.6, free_ram_gb=7))         # gemma4 8B with its encoders: swaps
        self.assertFalse(fits(6.6, free_ram_gb=7))         # qwen3.5 9.7B: no headroom left
        self.assertTrue(fits(3.4, free_ram_gb=7))          # qwen3.5:4b

    def test_thinking_is_why_two_sentences_took_four_minutes(self):
        self.assertEqual(generation_seconds(1087, 4.59), 236.8)  # measured: 3 min 56.9 s, thinking on
        self.assertEqual(generation_seconds(83, 4.68), 17.7)     # measured: 17.7 s, thinking off

    def test_openclaw_on_a_16k_window_overflows_before_you_type(self):
        overhead = 8786   # OpenClaw's prompt with no messages, from its own log
        reserve = 8384    # what it keeps back for the reply
        self.assertEqual(prompt_budget(16384, reserve), 8000)
        self.assertFalse(fits_context(overhead, 0, 0, 16384, reserve))   # "hi" failed
        lesson = words_to_tokens(5000)                                   # a long lesson, ~6,500 tokens
        self.assertTrue(fits_context(overhead, lesson, 2000, 32768, reserve))


if __name__ == "__main__":
    unittest.main()
```

```python
"""measure.py — time one prompt through Ollama's HTTP API and report what decides the speed.
Needs Ollama running locally. Usage:
    python3 measure.py qwen3.5:4b                 # Ollama decides where layers go
    python3 measure.py qwen3.5:4b --cpu           # force CPU only (num_gpu 0)
    python3 measure.py qwen3.5:4b --think         # let the model think first
"""
import json
import sys
import urllib.request

PROMPT = "Explain a token bucket in two sentences."


def measure(model: str, cpu_only: bool, think: bool) -> dict:
    body = {"model": model, "prompt": PROMPT, "stream": False, "think": think,
            "options": {"num_gpu": 0} if cpu_only else {}}
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        r = json.load(resp)
    ns = 1e9  # Ollama reports durations in nanoseconds
    return {
        "load_s": round(r["load_duration"] / ns, 1),
        "prompt_tokens": r["prompt_eval_count"],
        "prompt_rate": round(r["prompt_eval_count"] / (r["prompt_eval_duration"] / ns), 1),
        "output_tokens": r["eval_count"],
        "output_rate": round(r["eval_count"] / (r["eval_duration"] / ns), 2),
        "total_s": round(r["total_duration"] / ns, 1),
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    print(measure(args[0], cpu_only="--cpu" in args, think="--think" in args))
```

**Lab:** these files are in [`ai-ml/03-ai-engineer/16-local-and-open-models/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/16-local-and-open-models/labs/python). From the vault root, `python3 labs/run.py local-and-open-models/python` runs the sizing tests and checks this page still shows the same code. `measure.py` needs Ollama running, so the runner doesn't call it; run it yourself — `python3 ai-ml/03-ai-engineer/16-local-and-open-models/labs/python/measure.py qwen3.5:4b --cpu` printed `output_rate: 5.06` on the laptop, matching the manual 5.09.

**The answers.** No — 6.6 + 1.5 = 8.1 GB, over the 7 GB free. 236.8 seconds — the measured 3 minutes 56.9 seconds. No — the budget is 8,000 tokens, under the 8,786 overhead; that's the "hi" that failed.

## Common pitfalls

1. **Comparing a model's size with total RAM** instead of free RAM. The swap column is the honest test.
2. **Leaving thinking on for simple questions.** It multiplies answer time; the visible answer doesn't get noticeably better for easy ones.
3. **Assuming the GPU always helps.** Partial offload to a small GPU was 30% slower here. Measure both.
4. **Trusting Ollama's default 4K window** with long prompts, or setting a window smaller than an agent framework's overhead.
5. **Giving a local agent shell or write tools by default**, or connecting it to a chat app, when all it needs is to read.
6. **Weights ≠ served model.** Downloading is step zero; you still need a runtime, enough memory, and for production a real inference server.
7. **Over-quantising.** Below about 4 bits, quality drops in ways benchmarks don't show. Evaluate on *your* task.
8. **Licences bite at ship time.** Check commercial-use terms before building on a model.

## Check your understanding

1. Estimate the weight memory of a 7B model at `Q4_K_M`, and at `Q8_0`.
2. Your laptop has 16 GB RAM and 6 GB free. Which is the better first choice: a 9B model at 4 bits, or a 4B model at 4 bits? Why?
3. A model generates at 5 tokens/s. With thinking on it writes 900 hidden tokens before a 60-token answer. How long does the answer take, and with thinking off?
4. Why can putting part of a model on a small GPU make it *slower*?
5. An agent framework's prompt is 9,000 tokens and it reserves 8,000 for replies. What's the smallest context window that lets you send a 4,000-token lesson and a 1,000-token conversation?

<details>
<summary>Answers — after your attempt</summary>

1. 7 × 4.8 ÷ 8 ≈ 4.2 GB at `Q4_K_M`; 7 × 8.5 ÷ 8 ≈ 7.4 GB at `Q8_0`.
2. The 4B. The 9B's weights are about 5.4 GB, leaving well under the headroom it needs in 6 GB free, so it would push the system into swap. The 4B (~2.4 GB plus extras) fits with room for the cache.
3. With thinking: 960 tokens ÷ 5 = 192 seconds, over three minutes. Without: 60 ÷ 5 = 12 seconds.
4. Every generated token needs data moved between the CPU's memory and the GPU's across the connection between them. With only a slice of the model on a small GPU, that transfer costs more time than the GPU saves.
5. 9,000 + 4,000 + 1,000 + 8,000 = 22,000 tokens — so in practice a 32K window (the next common size).

</details>

## Practice — independent task

**Measure your own machine and choose a model for it.**

1. Note your free RAM with `free -h`, and pick the largest model the sizing rule says fits with headroom.
2. Run `measure.py` on it three ways: default, `--cpu`, and `--think`. Record load time, prompt rate and output rate.
3. Write a Modelfile with the faster placement and a context window sized for what you'll send, and build it with `ollama create`.
4. Watch `free -h` during a long answer: does swap grow?

**Done when:** you have the three measurements in a table, a Modelfile you can justify line by line, and swap that stays flat while it runs.

## Before moving on

You can choose a local model that fits a machine, explain its speed from Ollama's numbers, and budget the context and permissions for an agent built on it.

**Recap.** Self-host for privacy, steady volume, control or free personal use. Memory ≈ parameters × bits ÷ 8, plus the cache and any encoders — compare with *free* RAM. Generation speed is the bottleneck; thinking multiplies it; a small GPU can slow it; the first message pays the load. The context window must hold the framework's overhead, the files, the chat and the reply. A local agent gets your permissions, so give it only what it needs.

**Next.** [[ai-ml/03-ai-engineer/17-voice-and-realtime|Voice and realtime]] in the track; for SWE 102, back to the week you're on.

## Related
- [[tools/openclaw-study-partner/index|OpenClaw study partner]] — the setup this lesson measured
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The model landscape]] — open vs. closed, self-hosted vs. API
- [[ai-ml/03-ai-engineer/15-fine-tuning-applied|Fine-tuning (applied)]] — running your own LoRA on open weights
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|Reliability and plumbing]] — gateways make hosted ↔ local a config change
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|Cost, caching and latency]] — when owning the hardware wins on cost

*Source: §4–6 and the worked example are grounded — measured on the author's own laptop on 2026-10-02, with the study partner in [[tools/openclaw-study-partner/index|tools/openclaw-study-partner]]. §2–3 are [reference].*
