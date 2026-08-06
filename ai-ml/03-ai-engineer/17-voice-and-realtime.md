# Voice & Realtime

**Source:** Part II of the AI-engineer track. [[ai-ml/03-ai-engineer/09-multimodal|Multimodal AI]] covered speech-to-text and text-to-speech as *building blocks*; this note is what you assemble from them — a conversational **voice agent** — and the realtime constraints that make it a distinct engineering problem. Code is illustrative shape.

## Two ways to build a voice agent

### The pipeline (cascaded) approach
Chain the components you already know:

```
mic audio → [STT] → text → [LLM] → text → [TTS] → speaker audio
```

- **STT (speech-to-text)** transcribes the user's speech ([[ai-ml/03-ai-engineer/09-multimodal|multimodal]]).
- **The LLM** does the thinking — and everything else in this track still applies: [[ai-ml/03-ai-engineer/05-prompt-engineering|prompting]], [[ai-ml/03-ai-engineer/07-tools-and-mcp|tools]], [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]], [[ai-ml/03-ai-engineer/08-agents|the agent loop]].
- **TTS (text-to-speech)** voices the reply.

**Pros:** you control and swap each stage independently, reuse your existing text-LLM stack (a voice agent is your chatbot with ears and a mouth), and can inspect the transcript at every hop. **Con:** latency stacks up across three sequential models, and you lose the *non-text* information in speech — tone, emotion, interruptions.

### The realtime / speech-native approach
A single **speech-to-speech** model takes audio in and emits audio out directly, without a text bottleneck in the middle. **Pros:** far lower latency, and it preserves prosody — tone, laughter, emphasis — because it never flattens the conversation to text. **Cons:** less transparent (harder to log/inspect/guardrail the intermediate), newer, and often more expensive. Use it when *natural, low-latency conversation* is the product; use the pipeline when *control and reuse of your text stack* matter more.

## Latency is the whole game

In text, a second of delay is fine. In voice, **humans expect a reply in well under a second** — the natural gap between conversational turns is short, and a two-second pause feels broken, like the system froze. This single constraint reshapes every choice:

- **Stream everything.** Don't wait for the full transcript, then the full LLM answer, then the full audio. **Stream STT** (transcribe as they speak), **stream the LLM** (start generating on partial input, emit tokens as they come — [[ai-ml/03-ai-engineer/04-calling-models|calling models]]), and **stream TTS** (start voicing the first sentence while the model is still writing the rest). Overlapping the stages is what gets you under the latency budget; running them sequentially never will.
- **Time-to-first-word** is the number users feel, not total response time. Optimize the *start* of the reply.
- **Favor faster models** for the LLM step ([[ai-ml/03-ai-engineer/14-cost-caching-and-latency|cost, caching & latency]]) — a voice turn can't afford a slow frontier model unless the task truly needs it. A cascade (fast model for simple turns, escalate for hard ones) fits voice especially well.

## The hard parts unique to voice

Beyond latency, conversation has mechanics that text doesn't:
- **Turn-taking / endpointing** — knowing when the user has *finished* speaking versus just paused mid-sentence. Cut them off too early and you interrupt; wait too long and the agent feels sluggish. This "voice activity detection + endpointing" is a genuinely hard sub-problem and a common source of a bad feel.
- **Barge-in (interruption)** — a real conversation lets you interrupt. The agent must detect the user starting to talk *while it's speaking*, **stop its own audio immediately**, and listen. Without barge-in, the agent talks over people and feels robotic.
- **Backchannel and pacing** — natural conversation has "mm-hm"s, brief acknowledgments, and pauses. Getting the rhythm right is much of what makes a voice agent feel human rather than like a menu.

## Everything else still applies — plus voice-specific safety

A voice agent is still an LLM app, so the whole track carries over: it needs [[ai-ml/03-ai-engineer/07-tools-and-mcp|tools]] to *do* things, [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]] to know your data, [[ai-ml/03-ai-engineer/12-evals|evals]] to measure quality, and [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|reliability plumbing]] underneath. Safety ([[ai-ml/03-ai-engineer/10-safety-and-production|safety & production]]) gains extra edges in voice:
- **[[ai-ml/03-ai-engineer/10-safety-and-production|Prompt injection]] via spoken input** — the same attack surface as text, now arriving as transcribed speech; treat the transcript as untrusted.
- **Higher stakes on errors** — voice interactions often *do* things (place orders, change bookings) and there's no "re-read the message" — a wrong action executes on a mishearing. Confirm before consequential, hard-to-reverse actions, and keep a [[ai-ml/03-ai-engineer/08-agents|human in the loop]] for the risky ones.
- **STT errors compound** — a misheard word propagates through the whole pipeline; the LLM should tolerate imperfect transcripts and ask for clarification rather than confidently acting on a mishearing.

## Gotchas

- **Sequential (non-streaming) stages blow the latency budget.** STT-then-LLM-then-TTS run end-to-end is always too slow. Overlap them by streaming, or the agent feels broken.
- **No barge-in = talks over the user.** Interruption handling isn't a nice-to-have; without it the thing is unusable in real conversation.
- **Endpointing too eager or too patient.** Cutting users off mid-thought, or leaving dead air, both wreck the feel — tune it, and expect it to be hard.
- **Frontier-model latency.** The most capable text model may simply be too slow for a voice turn. Right-size, and cascade.
- **Transcription errors acted on blindly.** Confirm consequential actions; a homophone shouldn't cancel someone's flight.

## Key insight

**A voice agent is your text LLM stack wrapped in speech-in/speech-out — either as a streamed STT→LLM→TTS pipeline (control, reuse) or a speech-native realtime model (natural, low-latency) — and the defining constraint is sub-second latency, which forces you to stream and overlap every stage.** The genuinely voice-specific engineering is the conversation mechanics: turn-taking, barge-in, and pacing. Everything else you learned in this track (tools, RAG, evals, safety, reliability) still holds — it just now has to happen fast enough to feel like talking.

## Related
- [[ai-ml/03-ai-engineer/09-multimodal|Multimodal AI]] — STT and TTS as the building blocks
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|Cost, Caching & Latency]] — streaming and right-sizing for the latency budget
- [[ai-ml/03-ai-engineer/08-agents|Agents]] — a voice agent is an agent that listens and speaks
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — the raised stakes of voice actions
