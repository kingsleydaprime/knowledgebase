---
id: fffe6653-4a59-4fd2-918d-4b778b18eeeb
---

# Simulated Annealing

Simulated annealing is hill climbing that sometimes accepts a worse move, less and less often as a "temperature" cools.

## Before you start
<!-- bite: cd8e544f-5ac0-4484-99f0-8bc7ce207be0 -->

Read [[artificial-intelligence/03-heuristic-search/07-hill-climbing|Hill Climbing]] first. You need the landscape and the local maximum at state 2. You should be comfortable using $e^x$ on a calculator.

After this lesson you will be able to:

1. explain the idea behind simulated annealing and where its name comes from;
2. compute the probability of accepting a worse move, $e^{\Delta E / T}$, for given values;
3. explain why the temperature starts high and is lowered over time;
4. compare simulated annealing with hill climbing.

## What simulated annealing is
<!-- bite: ab006cdc-fade-4bdf-bbd8-5389b5c094d5 -->

Hill climbing got stuck on the small hill at state 2, value 6. Every step from there goes down, so it stopped, even though the highest point, 11, is just a few steps further on. To get there, it would have to go *down* first.

Simulated annealing does exactly that, but carefully. Your slides put it in one sentence: it sometimes accepts a worse move, with a probability that falls as the "temperature" cools. This helps it escape local maxima.

Early on, it's adventurous and takes plenty of downhill steps, exploring widely. As time goes on, it gets more and more careful, until at the end it behaves just like hill climbing and settles on a peak.

## The kid version
<!-- bite: d95943fc-b638-42f7-8624-914bfe16f68d -->

You're shaking a tray of sand with a marble on it, trying to get the marble into the deepest dip. If you only tilt gently, the marble rolls into the nearest dip and stays there, even if a deeper one is next door. So you start by shaking hard, so the marble bounces out of shallow dips. Then you shake more and more gently. By the end, the marble is resting in a deep dip, and gentle shakes can no longer knock it out.

**Where the analogy stops working.** Shaking moves the marble randomly. Simulated annealing is less random than that: it always accepts an *improvement*, and only rolls the dice for moves that make things worse.

## Where the name comes from
<!-- bite: b4742fce-21a7-4935-892e-f6f1eba2034d -->

**Annealing** is a process in metalwork. A blacksmith heats a metal until it's very hot, then lets it cool slowly. At high temperature the atoms move about freely; as the metal cools, they settle into a strong, orderly arrangement. Cool it too fast, and the atoms freeze in a messy, brittle arrangement.

Simulated annealing copies this. The **temperature** $T$ controls how freely the search moves. High $T$: it accepts bad moves often, like hot atoms. Low $T$: it hardly ever accepts them, like cold atoms settling into place. Lowering $T$ slowly gives the search time to find a deep, good state before it freezes.

## The algorithm
<!-- bite: e77c3edc-cb1c-4c6d-81d3-fa1678932436 -->

At each step:

1. Pick a **random** neighbour of the current state. (Not the best one, as in hill climbing: a random one.)
2. Work out the change in value, $\Delta E$ = value of the neighbour minus value of the current state.
3. If $\Delta E > 0$ (the neighbour is better), **always move** to it.
4. If $\Delta E \le 0$ (the neighbour is worse or equal), **move to it with probability** $e^{\Delta E / T}$.
5. Lower the temperature $T$ a little, following a fixed **cooling schedule**, and repeat.

The search stops when $T$ is close to zero, or after a set number of steps.

## The acceptance probability
<!-- bite: 8ccb9a6b-df43-40e2-a826-f82cf607bd62 -->

The rule for a worse move, stated in words first: the worse the move, and the cooler the temperature, the less likely it is to be accepted. The formula is:

$$P(\text{accept}) = e^{\Delta E / T}$$

Since $\Delta E$ is negative for a worse move, $\Delta E / T$ is negative, and $e$ to a negative power is between 0 and 1. A probability, as it should be.

Let's use it on our landscape. The search is stuck at state 2 (value 6), and picks neighbour 3 (value 5). So $\Delta E = 5 - 6 = -1$.

1. **Hot, $T = 10$:** $e^{-1/10} = e^{-0.1} \approx 0.905$. A 90% chance of taking the downhill step.
2. **Warm, $T = 1$:** $e^{-1} \approx 0.368$. About a 37% chance.
3. **Cold, $T = 0.1$:** $e^{-10} \approx 0.000045$. Almost no chance.

## Big drops versus small drops
<!-- bite: b8cf08cc-2e70-4bdc-b6b5-0a967b9b8afd -->

Now compare a bigger drop. Say a move loses 3 instead of 1, so $\Delta E = -3$:

1. **$T = 10$:** $e^{-0.3} \approx 0.741$.
2. **$T = 1$:** $e^{-3} \approx 0.050$.

Put the two side by side. At $T = 1$, a small drop of 1 is accepted 37% of the time, but a big drop of 3 only 5% of the time. So even when it does go downhill, simulated annealing prefers small steps down to big ones. And at $T = 10$, both are accepted most of the time: when hot, it barely cares.

That's why it works. Early, while hot, the search wanders freely across the landscape, out of the hill at state 2, across the plateau, toward the big hill. Later, as it cools, it stops accepting downhill steps and climbs whatever hill it's on. If it found the big hill while it was hot, it ends at the top, at 11.

## How good is simulated annealing?
<!-- bite: 78367f90-b9d6-409f-82c3-7ae22c4bb023 -->

1. **Complete and optimal?** Not in a single run with a practical schedule. But there's a strong theoretical result: if the temperature is lowered *slowly enough*, the probability of ending at the global maximum approaches 1.
2. **Time:** set by the cooling schedule. Slow cooling is more reliable but takes longer.
3. **Space:** tiny, just the current state, like hill climbing.

In practice, it's a robust method for large optimisation problems such as chip layout, timetabling and scheduling, where hill climbing keeps getting stuck.

## Hill climbing and simulated annealing compared
<!-- bite: 0e1d9d2a-4add-4c12-8ede-a09fbe37bb37 -->

| | Hill climbing | Simulated annealing |
|---|---|---|
| Which neighbour? | The best one | A random one |
| Worse moves? | Never | Sometimes, with probability $e^{\Delta E/T}$ |
| Escapes local maxima? | No | Yes, while the temperature is high |
| Memory | One state | One state |

## Terms used in this lesson
<!-- bite: 924e08d6-94c3-4a04-b29a-1fe8af83989e -->

1. **Simulated annealing**: This is local search that moves to a random neighbour, always accepting improvements and accepting worse moves with a probability that falls as a temperature is lowered.
2. **Annealing**: This is the metalworking process of heating a metal and cooling it slowly so its atoms settle into a strong, orderly arrangement.
3. **Temperature ($T$)**: This is the control number in simulated annealing. High $T$ means worse moves are often accepted; low $T$ means they're rarely accepted.
4. **$\Delta E$**: This is the change in value from the current state to the neighbour. It's negative for a worse move.
5. **Cooling schedule**: This is the rule for lowering $T$ over time, such as multiplying it by 0.95 after each step.

## Common pitfalls and traps
<!-- bite: cd43f8ab-d928-4ebb-bf58-23346a205bb8 -->

- **Thinking simulated annealing always takes the worse move.** It only *may* take it, with probability $e^{\Delta E/T}$. Better moves are always taken.
- **Getting the sign wrong.** For a worse move, $\Delta E$ is negative, so $e^{\Delta E/T}$ is less than 1. If you get a probability above 1, check the sign.
- **Cooling too fast.** Then it behaves like plain hill climbing and gets stuck, like quenched metal going brittle.

## Check your understanding
<!-- bite: 4c7d9162-502b-4cee-b963-f008ed181ba8 -->

Try each one before you open the answer.

1. <!-- q: exact id="e3be427f" answer="0.606531" sigfigs="2" -->
   Simulated annealing is at a state of value 20 and picks a neighbour of value 18. The temperature is $T = 4$. What is the probability that it accepts the move?

   <details><summary>Answer</summary>

   $\Delta E = 18 - 20 = -2$, so $P = e^{-2/4} = e^{-0.5} \approx 0.61$.

   </details>

2. <!-- q: exact id="8f60dec7" answer="0.135335" sigfigs="2" -->
   Same move, $\Delta E = -2$, but the temperature has cooled to $T = 1$. What is the probability of accepting it now?

   <details><summary>Answer</summary>

   $P = e^{-2/1} = e^{-2} \approx 0.14$. Cooling from 4 to 1 cut the chance from about 61% to about 14%.

   </details>

3. <!-- q: mcq id="fb7d0802" -->
   Simulated annealing picks a neighbour whose value is *higher* than the current state's. What does it do?

   - [x] Always moves to it
   - [ ] Moves to it with probability $e^{\Delta E/T}$
   - [ ] Moves to it only if the temperature is high
   - [ ] Never moves to it

   <details><summary>Answer</summary>

   It always moves to a better neighbour. The probability rule only applies to worse (or equal) moves.

   </details>

4. <!-- q: mcq id="b40d3151" -->
   At the same temperature, which worse move is more likely to be accepted?

   - [x] One that loses 1 point
   - [ ] One that loses 5 points
   - [ ] Both equally likely
   - [ ] Neither is ever accepted

   <details><summary>Answer</summary>

   The one that loses 1. A smaller drop gives a $\Delta E$ closer to 0, so $e^{\Delta E/T}$ is closer to 1.

   </details>

5. <!-- q: open id="ab5ec265" -->
   Explain why simulated annealing starts with a high temperature and lowers it slowly, using the landscape where hill climbing got stuck at state 2.

   <details><summary>Answer</summary>

   At a high temperature, worse moves are accepted often, so the search can walk down off the small hill at state 2, across the plateau, and reach the big hill where the global maximum (11) is. As the temperature falls, worse moves are accepted less and less, so the search stops wandering and climbs to the top of whichever hill it's on. Lowering it slowly gives the search enough time to find the big hill before it settles; cooling too fast would trap it at state 2, as plain hill climbing is.

   </details>

## Before moving on
<!-- bite: 4a807720-2753-450f-9214-1f2e1b2aa1b3 -->

You're done when you can explain the annealing idea, compute $e^{\Delta E/T}$ for a worse move, say how temperature and the size of the drop change it, and compare the method with hill climbing.

Recap: simulated annealing picks a random neighbour, always accepts better moves, and accepts worse ones with probability $e^{\Delta E / T}$. A high temperature lets it explore and escape local maxima; cooling slowly makes it settle. Small drops are accepted more readily than big ones. With slow enough cooling, it finds the global maximum with probability approaching 1.

Next, [[artificial-intelligence/03-heuristic-search/10-genetic-algorithms|Genetic Algorithms]] takes a different idea from nature: instead of one state cooling down, a whole population evolves.

## Related
<!-- bite: 3dcd6e72-ea8d-47c3-bd81-b6c406b3b7be -->

- [[artificial-intelligence/03-heuristic-search/07-hill-climbing|Hill Climbing]]: the method simulated annealing improves on.

## About this lesson
<!-- bite: bfac8764-4291-4767-9add-35f787e8545d -->

**Level:** intermediate. Lesson 9 of section 03 (heuristic search). It covers the annealing idea, the algorithm, the acceptance probability with worked numbers, cooling schedules, and a comparison with hill climbing.

**Source:** University of Lagos SSG 518 *Introduction to Search* slides (*Local Search and Optimisation*: "simulated annealing sometimes accepts a worse move, with a probability that falls as the temperature cools"). The acceptance formula follows Russell and Norvig. Every probability is computed and asserted by `scripts/diagrams/ai_heuristic.py`.
