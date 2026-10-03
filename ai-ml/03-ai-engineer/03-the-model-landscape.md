# The model landscape

> **[Beginner]** · A map of the models an AI engineer chooses between: the kinds of model, the companies that sell language models through APIs, gateways that put many of them behind one key, open-weight models you run yourself, and the tradeoff between hosted and self-run. The worked example decides where the ticket classifier should run, using real prices and a speed measured on a 16 GB laptop. The point is to choose well, so it teaches the questions that outlast any list of model names.

## Before you start

You can already:

- Take a feature through the four-step decision in [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|the AI engineer role]].
- Explain what a token is → [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]] (or read this first and come back to the costs).

After this lesson you will be able to:

1. Name the kinds of model and say which kind a problem needs.
2. Explain closed and open-weight models, what a gateway is for, and what quantisation trades away.
3. Decide between a hosted API and a model you run yourself, with numbers for cost and throughput.
4. Read a model's licence before shipping it.

**Study route.** Read §1–4, do the prediction in the worked example before reading its answer, then the practice task.

## The kid version

Think of models like vehicles. A bicycle, a van, a bus and a lorry each suit different jobs, and you'd pick by the job, not by which is newest. You can also rent or own. Renting a van (a hosted model) means someone else maintains it and you pay per trip, and you get the newest model. Owning one (running a model yourself) costs more up front, it's slower to get the newest, but each trip is nearly free and nobody else sees what you carry.

**Where the analogy stops working.** A rented van doesn't change between trips. A hosted model can be updated by its provider under the same name, so the evals that passed last month need running again.

## 1. Why this exists

Every AI feature makes the same choices: which kind of model, which provider, how large, and whether to call an API or run it yourself. Making them by habit means overpaying for capability you don't need, sending data somewhere it shouldn't go, or building on a model that can't handle your traffic. The names change every few months; the questions don't.

## Terms used in this lesson

1. **Closed model**: This is a model available only through its provider's API. You never see its weights.
2. **Open-weight model**: This is a model whose trained weights are published, so you can download and run it yourself. "Open-weight" isn't the same as "open source": the licence may restrict how you use it.
3. **Gateway**: This is also called an **aggregator**. It is a service that puts many providers' models behind one API and one key, so you can switch or compare models by changing a string.
4. **Quantisation**: This means storing a model's weights with fewer bits, such as 4 instead of 16, so it needs less memory and runs faster, at some cost in quality.
5. **Inference server**: This is software that runs a model and answers requests for it, such as Ollama on a laptop or vLLM on a GPU server.
6. **Throughput**: This is how many requests a system can answer in a given time, such as tickets per hour.
7. **Model card**: This is the page published with a model that describes its size, training data, intended use, limitations and licence.

## 2. Kinds of model

Language models dominate the conversation, but they're one kind among several, and the first filter is picking the right kind:

- **Language models**: text in, text out. The AI engineer's main tool.
- **Embedding models**: an input in, a vector out, with similar meanings giving nearby vectors. They don't generate; they make **comparison and search** possible ([[ai-ml/03-ai-engineer/06-rag-and-embeddings/index|RAG and embeddings]]).
- **Image, video and audio generation models**: text in, new media out. They work by gradually removing noise, a different architecture from language models ([[ai-ml/03-ai-engineer/09-multimodal/index|multimodal]]).
- **Speech models**: speech to text (such as Whisper) and text to speech ([[ai-ml/03-ai-engineer/17-voice-and-realtime|voice and realtime]]).
- **Vision models**: images in, labels, boxes or descriptions out. Many language models now take images too.
- **Classic machine learning**: regression, decision trees, clustering. On rows of structured data, a gradient-boosted tree is often more accurate, faster and far cheaper than a language model ([[ai-ml/02-ml-engineer/index|ML engineer]]).

## 3. Who sells language models, and how to reach them

**Closed models through APIs.** The main providers are Anthropic (Claude), OpenAI (GPT and its reasoning models), Google (Gemini), and others including Mistral, Cohere, DeepSeek and xAI. Each sells several sizes at different prices; on Anthropic's list on 2026-10-02, the largest model cost four times the smallest per token ([[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|cost, caching and latency]]). Closed models give the best capability with no infrastructure, which makes them the usual default. You give up control of the model and of where your data goes.

**Gateways.** Instead of integrating each provider, a gateway such as **OpenRouter** or the **Vercel AI Gateway** puts hundreds of models behind one API, with one bill, and can fall back to another provider when one fails ([[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]]). They add a small hop and sometimes a margin, and make comparing models on your golden set a matter of changing a string.

**Open-weight models.** Llama, Mistral, Qwen, Gemma and Whisper publish their weights, mostly on **Hugging Face**, the main hub for models, datasets and model cards. To run one:

- **On a laptop:** **Ollama** is the easiest start (it downloads, quantises and serves the model behind an API); **llama.cpp** is the engine underneath many local tools; **LM Studio** is a desktop app.
- **On a server, for many users:** **vLLM** is the usual inference server. It handles concurrent requests far better than laptop tools, and speaks the OpenAI API format, so application code barely changes.

**Quantisation** is why a 4-billion-parameter model fits in a few gigabytes: names like `Q4_K_M` mean about 4 bits per weight. It's not free: check quality at the level you choose, on your evals. **Fine-tuning** an open model on your own data is possible because the weights are yours; methods such as LoRA train a small number of extra parameters instead of the whole model ([[ai-ml/03-ai-engineer/15-fine-tuning-applied|fine-tuning applied]]).

## 4. Hosted or self-run

| | A model you run | A hosted API |
|---|---|---|
| Cost | hardware up front; each request nearly free | per token; no hardware |
| Data | never leaves your machines | sent to the provider, under their terms |
| Capability | usually behind the best closed models | the best available |
| Throughput | limited by your hardware | the provider scales it, within your rate limits |
| Operations | you run, update and monitor it | the provider does |
| Control | complete: fine-tune it, run it offline | what the API offers |

**Use a hosted API unless** the data mustn't leave, you must work offline, your volume makes per-token pricing the biggest cost, or you need to fine-tune on private data.

**Read the licence.** Open-weight licences differ. Some are permissive, such as Apache 2.0. Others restrict use: Meta's Llama licences, for example, require a separate licence for products with more than 700 million monthly active users and have their own acceptable-use terms. Check the model card before you ship.

## Worked example — where should the classifier run?

The ticket classifier gets **1,000 tickets an hour**. Each request is about 300 input tokens (the instructions plus a ticket) and a one-word answer.

**Option A: a small hosted model.** On the 2026-10-02 price list, Claude Haiku 4.5 costs $1 per million input tokens and $5 per million output tokens. 1,000 × 300 input tokens is 300,000 tokens, which is $0.30; the one-word outputs add about a cent. **About $0.31 an hour**, roughly $225 a month running all day, every day, and the provider handles the throughput.

**Option B: a local model on the course laptop.** `qwen3.5:4b` on the 16 GB laptop took about **12 seconds per classification** when the machine was otherwise quiet ([[ai-ml/03-ai-engineer/12-evals/index|evals]]), and generates about 5 tokens a second ([[ai-ml/03-ai-engineer/16-local-and-open-models/index|local and open models]]). Each request is free.

**Predict before reading on.** Which option would you choose, and what single number decides it?

**Throughput decides it.** At 12 seconds each, the laptop answers at most 3,600 ÷ 12 = **300 tickets an hour**, less than a third of the traffic, so the queue grows by 700 an hour. Option B isn't cheaper; it doesn't work at this volume. To serve 1,000 an hour locally you'd need a GPU server running something like vLLM, which costs money and someone's time to run.

So the decision is Option A, **unless the tickets contain data that mustn't leave**. Then the answer is a self-run model on hardware sized for the traffic, and the cost of that hardware is the price of keeping the data in. The laptop remains exactly right for development, for evals, and for the study partner it already runs.

## Common pitfalls

1. **Choosing by hype or habit.** Choose by the job, measured on your golden set.
2. **Assuming self-run is cheaper.** It's cheaper per request, not per hour of throughput you need. Do the arithmetic.
3. **Treating "open-weight" as "open source".** Read the licence.
4. **Assuming quantisation is free.** Measure quality at the level you'll run.
5. **Locking into one provider's SDK.** A port ([[ai-ml/03-ai-engineer/04-calling-models/index|calling models]]) or a gateway keeps switching cheap.
6. **Forgetting that hosted models change.** Re-run your evals when a provider updates the model behind a name.

## Check your understanding

1. A feature predicts delivery times from order data in a table. Which kind of model, and why not a language model?
2. What does a gateway give you, and what does it cost?
3. Why doesn't "each request is free" make the laptop the right choice for 1,000 tickets an hour?
4. What does `Q4_K_M` in a model's file name tell you, and what should you check before relying on it?
5. Give two situations where you'd run a model yourself despite the cost.

<details>
<summary>Answers — after your attempt</summary>

1. Classic machine learning, such as a gradient-boosted tree: the input is structured rows and the output is a number. A language model would be slower, costlier, and usually less accurate on tabular data.
2. One API and one key for many providers, easy comparison and fallback between models, and one bill. It costs a small extra network hop, sometimes a margin, and one more service in the path.
3. Throughput: at 12 seconds a request, the laptop handles at most 300 an hour, so it can't keep up, whatever each request costs.
4. That the weights are quantised to about 4 bits each, so the model is smaller and faster than full precision. Check its quality on your own evals at that level.
5. Any two of: the data mustn't leave your control; it must work offline; your volume makes per-token pricing the biggest cost; you need to fine-tune on private data.

</details>

## Practice — independent task

**Price your flagship's AI feature both ways.**

1. Estimate requests per hour at your expected peak, and input and output tokens per request.
2. Work out the hourly and monthly cost on one small and one large hosted model, using current prices from the provider's page, with the date.
3. Measure how long one request takes on a local model on your machine, and work out its maximum requests per hour.
4. Write down which you'd choose, and what would change your mind.

**Done when:** you have both costs, the local throughput with the date you measured it, and a decision with its reason. It belongs in week 6's write-up.

## Before moving on

You can name the kinds of model, explain closed and open-weight models, gateways and quantisation, decide between hosted and self-run with numbers, and check a licence.

**Recap.** Pick the kind of model first: language, embedding, generation, speech, vision or classic machine learning. Closed models through APIs are the default, with the best capability and no infrastructure; gateways make switching cheap. Open-weight models run on Ollama on a laptop or vLLM on a server, quantised to fit, and can be fine-tuned. Self-run when data, offline use, volume or fine-tuning demand it, and work out the throughput, not just the per-request price. Read the licence.

**Next.** [[ai-ml/03-ai-engineer/04-calling-models/index|Calling models]] — the code that reaches any of these, behind one port.

## Related
- [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|The AI engineer role]] — the decision this landscape feeds
- [[ai-ml/03-ai-engineer/16-local-and-open-models/index|Local and open models]] — running one, measured on the laptop
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|Cost, caching and latency]] — prices and how to cut them
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings/index|RAG and embeddings]] — where embedding models earn their place

*Source: folds three old notes (other model types, open-source models, the AI-tools landscape) and the roadmap.sh AI-engineer provider map; prices from Anthropic's list on 2026-10-02.*
