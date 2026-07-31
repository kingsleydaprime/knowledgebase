# Reinforcement Learning

**[reference]** — from the roadmap.sh `machine-learning` roadmap. A fundamentally different learning paradigm — and the one behind the RLHF that makes LLMs usable.

## The paradigm: learning from reward

Unlike [[ai-ml/02-ml-engineer/01-foundations-of-ml/01-what-is-ml-and-types|supervised learning]], there's **no dataset of correct answers**. An **agent** interacts with an **environment**: it observes a **state**, takes an **action**, receives a **reward** and a new state, and repeats. Its goal is to learn a **policy** (a mapping from states to actions) that maximizes *cumulative* reward over time.

```
        ┌──────── action ────────►
   Agent                          Environment
        ◄──── state, reward ──────┘
```

The defining challenges that make RL distinct:

- **Delayed reward / credit assignment** — a reward may come many steps after the action that earned it (a chess move that wins 30 moves later). Figuring out which actions deserve credit is the hard part.
- **Exploration vs exploitation** — do you exploit the best-known action, or explore an uncertain one that might be better? Balancing this is central.
- **No supervision** — the agent must discover good behavior by trial and error, guided only by reward.

## The main approaches

- **Value-based (Q-learning)** — learn the *value* of taking each action in each state (the "Q-value" = expected future reward), then act greedily on it. **Deep Q-Networks (DQN)** use a neural network to approximate Q-values, famously learning to play Atari games from pixels.
- **Policy-based (policy gradient)** — directly learn the policy (a network mapping state → action probabilities), adjusting it in the direction of higher reward. Handles continuous action spaces better.
- **Actor-critic** — combine both: an *actor* (policy) chooses actions, a *critic* (value estimate) evaluates them, stabilizing learning. Modern algorithms (PPO) are actor-critic.

## Where RL is used — and its catch

RL shines where you can define a reward and simulate/interact cheaply: **game-playing** (AlphaGo, AlphaStar), **robotics** and control, resource optimization. Its big catch is **sample inefficiency** — RL often needs enormous amounts of interaction to learn, which is fine in a fast simulator but expensive or unsafe in the real world (you can't crash a real robot a million times).

## RLHF — why an AI/ML engineer cares

The most consequential recent application: **RLHF (Reinforcement Learning from Human Feedback)** is a key step in turning a raw pretrained LLM into a helpful, aligned assistant. Humans rank model outputs; a *reward model* is trained to predict those preferences; then RL (typically PPO) fine-tunes the LLM to maximize that reward — nudging it toward helpful, harmless, honest responses rather than merely statistically-likely text. This connects the modeling side directly to the [[ai-ml/03-ai-engineer/02-how-llms-work|instruction-tuning]] that makes the models the AI-engineer track uses behave the way they do. (Newer variants like DPO achieve similar alignment without full RL.)

## Related
- [[ai-ml/02-ml-engineer/01-foundations-of-ml/01-what-is-ml-and-types|Types of Learning]] — where RL sits among the paradigms
- [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]] — RLHF's role in instruction-tuning
- [[ai-ml/00-foundations/03-mathematics/04-optimization|Optimization]] — policy gradients are gradient ascent on reward
