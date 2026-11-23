---
id: eeb6f2c1-d58c-4182-877a-0de059063c1d
---

# Reinforcement Learning

Reinforcement learning is training by trial and error, with rewards.

## What reinforcement learning is
<!-- bite: 257f0e8f-ed20-41d7-b02a-da870aefa163 -->

Reinforcement learning is a way of training a computer by trial and error, where it gets rewards for good actions and learns to collect as many rewards as it can. There is no list of correct answers, only feedback after each try. It is how computers learned to beat people at games like chess and Go, and it is also used to make chatbots more helpful.

Next: learning from reward in more detail, then the main approaches.

## The paradigm: learning from reward
<!-- bite: d6e3a0b2-9e83-48bb-8d53-68258ebc7e21 -->

Unlike [[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|supervised learning]], there's **no dataset of correct answers**. An **agent** interacts with an **environment**: it observes a **state**, takes an **action**, receives a **reward** and a new state, and repeats. Its goal is to learn a **policy** (a mapping from states to actions) that maximizes *cumulative* reward over time.

```text
        ┌──────── action ────────►
   Agent                          Environment
        ◄──── state, reward ──────┘
```

The defining challenges that make RL distinct:

- **Delayed reward / credit assignment** — a reward may come many steps after the action that earned it (a chess move that wins 30 moves later). Figuring out which actions deserve credit is the hard part.
- **Exploration vs exploitation** — do you exploit the best-known action, or explore an uncertain one that might be better? Balancing this is central.
- **No supervision** — the agent must discover good behavior by trial and error, guided only by reward.

## The main approaches
<!-- bite: c60373ce-fda5-46f9-83b5-fc5aff4734bb -->

- **Value-based (Q-learning)** — learn the *value* of taking each action in each state (the "Q-value" = expected future reward), then act greedily on it. **Deep Q-Networks (DQN)** use a neural network to approximate Q-values, famously learning to play Atari games from pixels.
- **Policy-based (policy gradient)** — directly learn the policy (a network mapping state → action probabilities), adjusting it in the direction of higher reward. Handles continuous action spaces better.
- **Actor-critic** — combine both: an *actor* (policy) chooses actions, a *critic* (value estimate) evaluates them, stabilizing learning. Modern algorithms (PPO) are actor-critic.

## Where RL is used — and its catch
<!-- bite: c0968575-1f90-4323-abc6-9ade18da3798 -->

RL shines where you can define a reward and simulate/interact cheaply: **game-playing** (AlphaGo, AlphaStar), **robotics** and control, resource optimization. Its big catch is **sample inefficiency** — RL often needs enormous amounts of interaction to learn, which is fine in a fast simulator but expensive or unsafe in the real world (you can't crash a real robot a million times).

## RLHF — why an AI/ML engineer cares
<!-- bite: b1a6afa7-7778-41d3-ab55-6b58850c3c5c -->

The most consequential recent application: **RLHF (Reinforcement Learning from Human Feedback)** is a key step in turning a raw pretrained LLM into a helpful, aligned assistant. Humans rank model outputs; a *reward model* is trained to predict those preferences; then RL (typically PPO) fine-tunes the LLM to maximize that reward — nudging it toward helpful, harmless, honest responses rather than merely statistically-likely text. This connects the modeling side directly to the [[ai-engineering/02-how-llms-work/index|instruction-tuning]] that makes the models the AI-engineer track uses behave the way they do. (Newer variants like DPO achieve similar alignment without full RL.)

## Check your understanding
<!-- bite: bcc12cd0-98b8-4aa4-abe7-82800c3b7338 -->

Try each one before you open the answer.

1. <!-- q: gap id="e71a5123" answers="policy" -->
   Fill in the gap. An RL agent's goal is to learn a ___, a mapping from states to actions that maximizes cumulative reward.

   <details><summary>Answer</summary>

   A policy.

   </details>

2. <!-- q: mcq id="c16546fe" -->
   A chess move wins the game 30 moves later. Which RL challenge is figuring out that it deserves credit?

   - [x] Delayed reward / credit assignment
   - [ ] Exploration vs exploitation
   - [ ] Overfitting

   <details><summary>Answer</summary>

   Credit assignment. The reward comes long after the action that earned it.

   </details>

3. <!-- q: mcq id="7e85a533" -->
   PPO uses an actor and a critic. What does each do?

   - [x] The actor chooses actions, the critic evaluates them
   - [ ] The actor evaluates actions, the critic chooses them
   - [ ] Both choose actions and vote

   <details><summary>Answer</summary>

   The actor (the policy) chooses, and the critic (a value estimate) evaluates, which stabilizes learning.

   </details>

4. <!-- q: mcq id="fb86ecc2" -->
   What is RL's big catch for real-world robots?

   - [ ] It can't handle continuous actions
   - [x] Sample inefficiency: it needs huge amounts of trial and error
   - [ ] It needs labelled data

   <details><summary>Answer</summary>

   Sample inefficiency. That is fine in a fast simulator, but you can't crash a real robot a million times.

   </details>

5. <!-- q: open id="fe063c3f" -->
   Describe the three steps of RLHF.

   <details><summary>Answer</summary>

   Humans rank the model's outputs. A reward model is trained to predict those preferences. Then RL (usually PPO) fine-tunes the LLM to maximize that reward, nudging it toward helpful, harmless and honest answers.

   </details>

## Related
<!-- bite: 948d0f92-c99a-42ab-8a40-19263508de5e -->
- [[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|Types of Learning]] — where RL sits among the paradigms
- [[ai-engineering/02-how-llms-work/index|How LLMs Work]] — RLHF's role in instruction-tuning
- [[machine-learning/00-foundations/03-mathematics/04-optimization|Optimization]] — policy gradients are gradient ascent on reward

## About this lesson
<!-- bite: 4b053945-2b78-4fa3-b8a8-5e8f43547aa3 -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. A fundamentally different learning paradigm — and the one behind the RLHF that makes LLMs usable.
