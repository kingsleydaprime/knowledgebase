---
id: fe672927-b46b-4dc8-8d59-f548c4cc104e
---

# Systems and Their Components

Every system can be sorted into types and described with the same five components: entities, attributes, state, activities and events.

## Before you start
<!-- bite: 32fa1ffb-9e6a-4731-a95e-1875d0ee10ba -->

You should have read [[systems-simulation/02-when-to-simulate|02 — When to Simulate]].

After this lesson you will be able to:

1. tell a discrete system from a continuous one, and classify a system in five other ways;
2. name the five components of a system and give an example of each;
3. explain the difference between an attribute and a state variable, and between an activity and an event.

## What describing a system involves
<!-- bite: f2fe8329-8d70-4a57-9433-e393cf541b75 -->

Before you can model a system, you need a way to describe it. This lesson gives you two tools. The first is a set of labels for the *type* of system, which tells you what kind of model it needs. The second is a checklist of five *components*, which you fill in for any system, whether it is a railway, a factory or a hospital. The same checklist comes back in every case question in the exam.

## Discrete and continuous systems
<!-- bite: 620558da-f22d-437f-9e69-c93ed7dda86b -->

The most important split, because it decides the kind of simulation you build:

1. **Discrete system:** variables change instantly, at separate points in time. The number of people in a bank queue jumps from 3 to 4 the moment someone walks in; it is never 3.5.
2. **Continuous system:** variables change smoothly with time. The water level behind a dam rises a little every second while it rains.

Discrete systems are simulated by jumping from one change to the next (lesson 09). Continuous systems are simulated with equations that describe the rate of change (lesson 05).

## Five more ways to classify a system
<!-- bite: dde68323-f012-4e9d-83b1-7e52bc933aec -->

1. **By nature:** physical, biological, social or engineering.
2. **By boundary:** an **open** system exchanges inputs and outputs with its surroundings; a **closed** system doesn't.
3. **By behaviour:** a **static** system doesn't change over time; a **dynamic** one does.
4. **By structure:** in a **linear** system the output is proportional to the input; in a **nonlinear** one it isn't.
5. **By uncertainty:** a **deterministic** system's output is fully predictable from its input; a **stochastic** system is partly or wholly random.

A bank is a social, open, dynamic, nonlinear, stochastic and discrete system. Customers come and go (open), the queue changes (dynamic), doubling arrivals more than doubles the wait (nonlinear), and arrival times are random (stochastic).

## The five components
<!-- bite: 26390d85-ec3f-4065-babf-0125ec6c3bf5 -->

Any system is described with the same five components.

1. **Entity:** This is an object of interest in the system, such as a customer in a bank.
2. **Attribute:** This is a property of one entity, such as the customer's account type.
3. **State:** This is the collection of variables needed to describe the whole system at one moment, for the purpose of the study, such as the number of customers waiting and whether each teller is busy.
4. **Activity:** This is an action that lasts a stated length of time and changes the state, such as a teller serving a customer.
5. **Event:** This is an instant that may change the state, such as a customer arriving or leaving.

## Four systems, described
<!-- bite: c0b39d69-6d4e-47da-ade0-07109580a58c -->

Here the five components are filled in for four systems. The table is worth learning, because exam questions give you a new system and ask you to fill in exactly these columns.

| System | Entities | Attributes | Activities | Events | State variables |
| --- | --- | --- | --- | --- | --- |
| Railway | Passengers | Origin, destination | Travelling | Arrival at station, arrival at destination | Number waiting at each station |
| Production | Machines | Speed, capacity, breakdown rate | Welding, stamping | Breakdown | Each machine busy, idle or shut down |
| Communications | Messages | Length, destination | Transmitting | Arrival at destination | Number of packets waiting to send |
| Inventory | Warehouse | Capacity | Withdrawal | Demand | Level of inventory |

## The two differences exams ask about
<!-- bite: bc3a7db2-4c9a-4e40-9218-ba5fd9a006a6 -->

Two pairs are easy to confuse.

1. **Attribute versus state variable.** An attribute belongs to *one* entity: this passenger's flight number. A state variable describes the *whole system* at a moment: how many passengers are waiting.
2. **Activity versus event.** An activity *lasts* for a length of time: serving a customer for 4 minutes. An event happens at an *instant*, and marks the start or end of an activity: service starts, service ends.

So in a bank, "serving" is an activity, while "service starts" and "service ends" are its two events.

## Common pitfalls
<!-- bite: a1d92fb9-455a-43c4-bd73-930801d824c9 -->

1. **Calling a state variable an attribute.** "Number of customers waiting" belongs to the system, not to any one customer.
2. **Calling an activity an event.** If it takes time, it is an activity. If it happens in an instant, it is an event.
3. **Leaving out the purpose.** The state is "the variables needed for the aim of the study". A queue study doesn't need the temperature in the bank.

We can now describe a system. Next lesson looks at modelling itself: why we need models, and how the purpose of a study decides what the model looks like.

## Check your understanding
<!-- bite: 94652e99-5ca2-463c-9539-20afc1a3976c -->

Try each one before you open the answer.

1. <!-- q: mcq id="6aba2534" -->
   Which of these is a continuous system?

   - [ ] The number of cars waiting at a traffic light
   - [ ] The number of patients in a clinic
   - [x] The temperature of water in a heating tank
   - [ ] The number of parts in a warehouse

   <details><summary>Answer</summary>

   The water temperature, which changes smoothly with time. The others are counts that jump from one whole number to the next.

   </details>

2. <!-- q: open id="a9817bac" -->
   For a petrol station, name the entities, one attribute, one activity, two events and one state variable.

   <details><summary>Answer</summary>

   Entities: cars. Attribute: fuel type, or litres wanted. Activity: refuelling. Events: a car arrives, a car leaves (or refuelling starts and ends). State variable: number of cars waiting, or how many pumps are busy.

   </details>

3. <!-- q: mcq id="96aa4b46" -->
   In a hospital model, which of these is a state variable rather than an attribute?

   - [ ] A patient's age
   - [ ] A patient's illness
   - [x] The number of beds occupied
   - [ ] A patient's expected length of stay

   <details><summary>Answer</summary>

   The number of beds occupied describes the whole system at a moment. The others belong to one patient, so they are attributes.

   </details>

4. <!-- q: mcq id="b8e63966" -->
   A machine drills a part for 6 minutes. Which of these is an event?

   - [ ] Drilling the part
   - [x] The drilling finishes
   - [ ] The 6 minutes of work
   - [ ] The machine's speed

   <details><summary>Answer</summary>

   "The drilling finishes" happens at an instant, so it is an event. Drilling for 6 minutes is the activity, and the machine's speed is an attribute.

   </details>

5. <!-- q: gap id="29ac85ec" answers="deterministic;stochastic" -->
   A ___ system's output is fully predictable from its input. A ___ system is partly or wholly random.

   <details><summary>Answer</summary>

   Deterministic, then stochastic. Most systems worth simulating are stochastic, because randomness is what makes formulas hard.

   </details>

## Before moving on
<!-- bite: a6c6ff67-0727-42b0-9094-7bae3c65d60b -->

You can classify a system and describe it with the five components. **Next:** [[systems-simulation/04-modelling-1|04 — Modelling 1]]: why we need models, and how the purpose decides the model.

## Related
<!-- bite: e6efe21f-5396-4cc5-9dcc-18d9f04246d1 -->

- [[systems-simulation/index|Systems simulation map]]
- [[systems-engineering/index|Systems Engineering]]: managing big systems through their whole life.

## About this lesson
<!-- bite: 121eb65f-a7e3-4174-b1bd-a8d7a8c881fb -->

**Level:** Beginner. **Covers:** discrete and continuous systems, five other ways to classify a system, the five components, the four-system table, and the attribute/state and activity/event differences.

**Where it sits:** lesson 03 of 38, in part 1 (systems and models).

**Source:** the author's own SSG 418 and SSG 517 study notes, section B.
