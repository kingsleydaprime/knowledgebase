# Systems Simulation (SSG 418 and SSG 517) – Study Notes

Nov 23, 2026 · @Kingsley Ihemelandu Chukwudi

These notes now cover both courses. **Part 1 (SSG 418, Systems Simulation 1)** comes first as sections A to G. **Part 2 (SSG 517, Systems Simulation 2)** follows as sections 1 to 10. Where Part 2 builds on Part 1 the text says so, and the queueing, random number and Monte Carlo material that Part 1 touched on is in sections 2 to 4.

## A. Part 1: Systems, models and why we simulate

### What a system is

A system is a collection of different elements that together produce results the elements cannot produce alone. The elements can be people, hardware, software, facilities, policies and documents. The important point is that the value of the whole comes from the relationships between the parts, not from the parts on their own.

### Ways to study a system

The lecture draws this as a tree, and it is a favourite to be asked:

1. Experiment with the **actual system**, or with a **model** of the system.
2. If you use a model, it can be a **physical model** (a prototype, a scale model) or a **mathematical model** (equations, symbols).
3. A mathematical model can be solved by an **analytical solution** (a formula) or by **simulation** (run it and watch what happens).

Simulation is what you fall back on when the formula is too hard or does not exist.

### Why not just experiment on the real thing?

Experimenting is the first way humans learn about their world, but often it is not possible:

1. **Ethics:** it is not acceptable (for example measuring radiation spread after a nuclear accident).
2. **Risk:** too dangerous (testing ways to control a reactor, or an epidemic or a fire evacuation).
3. **Cost:** too expensive (upgrading every switch in a large data network to see what happens).
4. **Time:** too slow (the ecological effect of a hunting season over several years).
5. **Disruption:** it would upset normal life (trying a new one-way street grid downtown).
6. **Irreversible:** you cannot undo it (a fiscal policy change on a country's economy).
7. **Impossible:** you cannot manipulate a star, or experiment on a building that does not exist yet.

### Model and simulation: the definitions

A **model** is a representation of something real (a case study) or made up (a use case), used in place of the real thing to understand it better. To make one you abstract the essentials of the system.

A **simulation** is the imitation of the operation of a real-world process or system over a period of time. Other wordings from the lecture: a method for implementing a model over time; an experiment on a model instead of on the real system; a way of getting information by watching the model as it runs.

### Advantages of simulation

The lecture lists 18. Group them so you can recall them:

- **Cheap, safe testing of decisions:** check a decision artificially without committing resources, the original system is not disturbed, a simulated study costs far less than changing a real system, shorter design cycles.
- **Flexibility:** the same model can be reused, the rules are easy to change, you can try special cases while it runs, it needs fewer simplifications than analytical methods, and you can compress or stretch time.
- **Understanding:** it helps diagnose problems by showing how variables interact, find constraints (is a delay the cause or the effect?), see how the system works rather than just predicting it, and visualise it with animation.
- **Planning and training:** it prepares you for change by answering "what if", helps specify requirements, and gives cheaper, less disruptive training than on-the-job training.

### Disadvantages

1. Building models needs special training.
2. Results are hard to interpret. Outputs are random because inputs are random, so you cannot easily tell whether an observation comes from how the system is connected or just from chance.
3. It can be time consuming and expensive.

### When simulation is not appropriate

When common sense solves the problem; when it can be solved analytically; when direct experiments are cheaper; when the cost of modelling is more than the savings; when you lack resources or time; when the necessary data is missing; when the system is so complex that it cannot be defined.

### Where it is used

The lecture gives examples in manufacturing and semiconductors (dispatching rules, lot sizes, cycle time and utilisation), construction (dam embankment, tunnel construction), military (recruiting, controllers for underwater vehicles), logistics and transport (rail capacity, airport passenger flow, toll plaza design, flight schedules), business processes (gate assignment, workforce planning) and human systems (human performance in complex systems, traffic control). You only need two or three examples per area in an exam.

## B. Part 1: System types and components

### Types of system

- **Discrete system:** variables change instantly at separate points in time (a queue at a bank).
- **Continuous system:** state variables change continuously with time (water level in a dam).

Lecture 1 also classifies systems in other ways: by nature (physical, biological, social, engineering), by boundary (open systems exchange inputs and outputs with their surroundings, closed ones do not), by behaviour (static does not change over time, dynamic does), by structure (linear means output is proportional to input, nonlinear means it is not) and by uncertainty (deterministic means the output is fully predictable from the input, stochastic means it is partly or wholly random).

### The five system components

1. **Entity:** an object of interest in the system.
2. **Attribute:** a property of an entity.
3. **State:** the collection of variables needed to describe the system at one moment, relative to the aim of the study.
4. **Activity:** an action that takes place over a stated length of time and changes the system's state.
5. **Event:** an instantaneous occurrence that may change the state.

| System | Entities | Attributes | Activities | Events | State variables |
| --- | --- | --- | --- | --- | --- |
| Railway | Passengers | Origin, destination | Travelling | Arrival at station, arrival at destination | Number of passengers waiting at each station |
| Production | Machines | Speed, capacity, breakdown rate | Welding, stamping | Breakdown | Status of machines (busy, idle, shutdown) |
| Communications | Messages | Length, destination | Transmitting | Arrival at destination | Number of packets waiting to be transmitted |
| Inventory | Warehouse | Capacity | Withdrawal | Demand | Level of inventory |

Two differences that come up in exams. An **attribute** belongs to one entity (a passenger's flight number); a **state variable** describes the whole system at a moment (how many passengers are waiting). An **activity** lasts for a length of time; an **event** happens at an instant and marks the start or end of an activity.

These are the same ideas as the "components of a simulation model" list in section 1 (entities, attributes, events, states, variables, resources, queues). The 418 version uses "activity" where the 517 notes use "resources and logic".

## C. Part 1: Modelling

### Why modelling is needed

The lecture opens with twelve questions that you cannot answer by direct measurement: the height of a tower without climbing it, the width of a river without crossing it, the mass of the Earth, the temperature at the centre of the sun, Nigeria's population in 2050, the effect of a 30% income tax cut, the average life of a bulb, next year's insurance claims. A model lets you answer them anyway.

### What modelling is

Modelling is the process of abstracting a real system. A model exposes the internal workings of a system in a form useful for science and engineering, and modelling is really the process of organising what you know about the system. The word comes from the Latin for a mould or pattern. When building a model you have to balance two things that pull against each other: **simplicity** and **accuracy (faithfulness)**.

### Model purpose decides the model

The same aircraft can be modelled three ways. As a **particle**, if you only want the flight path to compute fuel use (simple and enough). As a **system of rigid bodies**, if you want flight stability (how it reacts to small disturbances). As a **system of deformable bodies**, for flutter analysis (finding the critical speed of flutter). The analyst chooses the model that fits the question. Inputs to model development in the lecture figure: the system and its boundaries, the purpose, the level of detail, the performance measure and the design alternatives.

### Classifying models

The lecture chart splits models into **physical** (prototypes at reduced scale, real models) and **abstract** (mathematical, descriptive, logical, neural network). Mathematical models are further split into static or dynamic, continuous or discrete, ordinary or partial differential equations (ODE or PDE), linear or nonlinear, and deterministic or stochastic.

How different kinds of model compare:

- **English text:** describes well but is very ambiguous; used for explanations and directions.
- **Drawings and block diagrams:** describe well, not ambiguous, good for design and assembly.
- **Logical flow charts and decision tables:** fair at description, can be turned into computer programs.
- **Curves, tables, nomographs:** fair, used to show simple relations between a few variables.
- **Mathematical models:** poor at describing in words, but not ambiguous and excellent to manipulate; used for problem solution and optimisation.

### Mathematical modelling principles

A mathematical model describes the properties and interactions in a system using mathematical language. The **fundamental axiom** (modelling hypothesis): the model of a component describes its behaviour as an independent entity, and how it is connected to other components. So you can remove a component, literally or in your head, and study it alone.

The lecture also gives "across" and "through" variable pairs for different kinds of system (across: velocity, pressure, voltage; through: force, flow rate, current) and classifies two-terminal components as **dissipaters** (power is lost), **delay types** and **accumulators** (no net power over infinite time, so non-dissipative) and **sources or drivers** (their variable is fixed whatever the operating condition). Learn the idea; the equations are less likely to be asked in a simulation exam.

### Building mathematical models from first principles (from the process control chapter)

This chapter is from a process dynamics course, so treat it as supporting material.

- A model can be built from **first principles** (physical laws) or from **system identification** (measuring the system and fitting a model). Often both are combined: the basic model from physics and the uncertain parameters from measurements.
- Every model has a limited validity range, even physical laws. A model from system identification should not be used outside the range of the experiment.
- First principles use two kinds of relationship. **Conservation laws:** flow balance (accumulation per unit time = inflow − outflow + production) and effort balance (change per unit time = forcing quantity − loading quantity, which is Newton's laws and Kirchhoff's voltage law). **Constitutive relationships:** static relations such as Ohm's law, valve characteristics, Bernoulli's law and the ideal gas law.
- Procedure: (1) write the balance equations, (2) add constitutive relationships to link the variables, (3) check that every added term has the same unit and both sides of each equation have the same unit.
- Example: an RC low-pass filter gives RC·(du\_out/dt) + u\_out = u\_in, a first-order linear differential equation.
- **Linearisation:** real models are often nonlinear. If you work near a known operating point you can replace the nonlinear equation by a linear one using a first-order Taylor series about that point, and use several linear models if the operating range is wide.

## D. Part 1: The 12 steps of a simulation study

The Part 1 lectures use the Banks, Carson, Nelson and Nicol list, grouped in four phases:

**Phase 1: Planning**

1. Problem formulation: state the problem.
2. Setting of objectives and overall design: the questions the simulation must answer.

**Phase 2: Building the model**

- **3. Model conceptualisation:** abstract the essential features, choose the assumptions, start with a simple model and enrich it later.
- **4. Data collection:** start early because it can take a long time.
- **5. Model translation:** programming.
- **6. Verification:** is the computer program working properly?
- **7. Validation:** does the model accurately represent the system?

**Phase 3: Running it**

- **8. Experimental design:** which alternatives to simulate.
- **9. Production runs and analysis:** estimate the performance measures (averages, probabilities, frequencies).
- **10. More runs?** Enough runs are needed for statistical accuracy.

**Phase 4: Reporting**

- **11. Documentation.**
- **12. Implementation.**

How this lines up with the 10 steps in section 1: the 10-step version merges experimental design, production runs and more runs into "model experimentation" and merges documentation and implementation into "documentation and communication". The model-building core (definition, objectives, conceptualisation, data, formulation, translation, verification, validation) is identical.

Lecture 1 also lists the same challenges that appear in Part 2: data availability and quality, model complexity and realism, model uncertainty and sensitivity, scalability and efficiency, and usability and accessibility.

### Simulation software (Part 1 view)

Software can be general purpose (MATLAB, Python, Excel) or specific purpose (Arena, Stella, NetLogo); graphical (Simulink, AnyLogic, Vensim) or textual (R, C++, Java); discrete-event (Arena, SimPy, SimEvents) or continuous (Stella, Simulink, Berkeley Madonna); desktop or web based. Choose by the type of system, the level of detail you need, the purpose, your budget and your experience. Benefits: better understanding, fewer bad decisions, faster development and testing, better communication between stakeholders.

## E. Part 1: Discrete-event simulation and queues (recap)

The 418 discrete-event note covers events, state, the clock, simulation time versus wall-clock time, the event list, queue configurations, queue behaviour (balking, reneging, jockeying), queue discipline (FIFO, LIFO, SIRO, SPT, PR), Kendall notation, Little's law and the table of useful formulas. All of it is already written up in sections 2 and 3, including the formula table. Two extra details from that note: a traffic light is the standard example of a state (which light is on), a state variable (the colour) and events (switch to red, yellow, green); and the event list is kept in increasing time order, the clock jumps to the next event, the event runs and is removed.

## F. Part 1: GPSS/H

GPSS (General Purpose Simulation System) is a general-purpose discrete simulation language. You build a model by describing how things flow through a series of blocks.

### The elements of GPSS/H

- **Transactions:** the moving entities (a shopper, a car on an assembly line, a casting). Most are temporary: they are created, do their job and are destroyed. A few can be permanent. A transaction has attributes (a car's colour, a shopper's number of items), some built in and some user defined.
- **Resources:** static, permanent entities that transactions compete for. There are two types. A **Facility** is a single-unit resource (one cashier). A **Storage** is a group of identical parallel resources (three identical machines as a storage of capacity 3).
- **Blocks:** the statements that describe how a transaction moves; the whole set is the model logic, and drawn as a picture it is a **block diagram**.
- **Control statements:** tell GPSS how to run (for example `START 100` to stop after 100 transactions have left, or a stop after 24 hours of simulated time). They also define entities and give looping and IF logic. They have no picture.
- **Compiler directives:** information needed to compile the model that causes no action when running (for example declaring a variable as an integer).
- **Standard numerical attributes (SNAs):** values that GPSS keeps for each entity, which the model can read in its logic.

Other entity groups: computational entities (variables, functions) and statistical entities (queues, tables). When transactions wait, GPSS serves highest priority first, then first-in first-out.

### The main blocks

| Block | What it does |
| --- | --- |
| GENERATE | Creates transactions; the operands give the inter-arrival time, so `GENERATE 15,4.5` means uniform between 10.5 and 19.5 |
| QUEUE | The transaction joins a named queue, so statistics on waiting are collected |
| SEIZE | The transaction captures a facility, or waits if it is busy |
| DEPART | The transaction leaves the queue |
| ADVANCE | Delays the transaction for the service time, for example `ADVANCE 13.5,3` |
| RELEASE | The transaction gives up the facility |
| TERMINATE | Destroys the transaction; `TERMINATE 1` counts one toward the `START` count |
| ENTER / LEAVE | Take and give back units of a storage (multi-server resource) |
| GATE | Lets a transaction through only if a condition holds, such as a storage not being full |
| TRANSFER | Sends the transaction to another block |
| TABULATE | Adds a value to a table, which builds a histogram |

The order QUEUE, SEIZE, DEPART, ADVANCE, RELEASE is the heart of a one-server queue. The wait is measured between QUEUE and DEPART, and the service between SEIZE and RELEASE.

### Worked model 1: the castings and the drill

Castings arrive at a drill every 15 ± 4.5 minutes (uniform). Drilling takes 13.5 ± 3.0 minutes (uniform). First come first served. Simulate until 100 castings have been drilled.

```
        SIMULATE
        GENERATE   15,4.5       ; castings arrive
        QUEUE      DRILLQUE     ; join the drill queue
        SEIZE      DRILL        ; capture the drill
        DEPART     DRILLQUE     ; leave the queue
        ADVANCE    13.5,3       ; drilling time
        RELEASE    DRILL        ; give up the drill
        TERMINATE  1            ; drilled casting leaves
        START      100          ; run until 100 have left
```

Note: the printed code in your handout says `GENERATE 10.0,2.5`, but that does not match the question (15 ± 4.5) or the report. I used the figures from the question. The report shows an end time of 1534.483 minutes, which is about 15.3 minutes per casting, consistent with 15 ± 4.5.

**Reading the report:** all 7 blocks have an entry count of 100, meaning every casting went through every block. The drill facility had 100 entries, **utilisation 0.879** (the drill was busy 87.9% of the time) and an **average time of 13.491** minutes per casting. Check: expected utilisation is mean service time over mean inter-arrival time, 13.5 / 15 = 0.9, so 0.879 is close, and the small gap is sampling randomness. For the queue, read the maximum content, the average content, the number of entries, the zero entries (castings that did not wait) and the average time in the queue.

### Worked model 2: a simple telephone system

Two external lines. Calls arrive every 100 ± 60 seconds. If both lines are busy, the caller redials after 5 ± 1 minutes. A call lasts 3 ± 1 minutes. We want a table of how long each caller takes to complete a call.

```
Sets    STORAGE   2               ; two external lines
Transit TABLE     M1,.5,1,20      ; histogram of transit times
        GENERATE  1.667,1         ; calls arrive (100 +/- 60 s)
Again   GATE SNF  Sets,Occupied   ; if the lines are full go to Occupied
        ENTER     Sets            ; take a line
        ADVANCE   3,1             ; talk for 3 +/- 1 min
        LEAVE     Sets            ; free the line
        TABULATE  Transit         ; record time in system
        TERMINATE 1               ; call completed
Occupied ADVANCE  5,1             ; wait before redialing
        TRANSFER  ,Again          ; try again
```

How it works: a call that finds a free line goes straight through ENTER, ADVANCE, LEAVE and is tabulated. A call that finds both lines busy is sent by the GATE to the `Occupied` block, waits about 5 minutes, then TRANSFERs back to `Again` and tries again. `M1` is the time a transaction has spent in the simulation, so tabulating it just before TERMINATE gives the total time from first dialling to finishing the call. To find out how long 200 calls take, run the model with `START 200` and read the END TIME in the report. Changing the storage to 3 or 4 lines is a one-line experiment.

## G. Part 1: Practice questions with short answers

**Q1 / Q8. Car assembly line (welding, painting, inspection, with rework).**

- **(a) Why simulation:** the line has several stations with different, random processing times and rework loops. Rework creates feedback that makes closed-form (analytical) models hard or impossible, while a simulation handles it easily, along with random breakdowns.
- **(b) Steps:** problem formulation, objectives and project plan, model conceptualisation, data collection, model translation, verification, validation, experimental design, production runs and analysis, more runs, documentation and reporting, implementation (the 12 steps in section D).
- **(c) Two performance measures:** throughput (cars completed per shift) and work in process (cars between stations). Utilisation of each station or the average time a car spends in the system also work.

**Q2. Bank branch with long queues.**

- **(a)** The arrival process is how customers enter: Poisson arrivals, which means exponentially distributed inter-arrival times. The service process is how long service takes: exponential service times.
- **(b)** Queue discipline is the rule for choosing the next customer. FIFO serves in order of arrival. Priority serves important customers (for example business accounts) first. In a model you implement it as the rule the server uses to pick from the waiting line.
- **(c)** Two KPIs: average number waiting (Lq) and average time spent waiting (Wq). Utilisation also counts.
- **(d)** Two strategies to test: add more tellers at peak hours (increase c), and shorten service time (better technology or training, increase μ).
- **(e)** A simulation run is one random sample, so its output varies from run to run, while the formula gives the long-run average. Real systems also break the formula's assumptions (non-exponential times, finite waiting room, priorities).

**Q3. Traffic intersection with lights.**

- **(a)** Entities: vehicles and pedestrians. Attributes: vehicle type, speed, destination. State variables: number of vehicles waiting, light status (red or green).
- **(b)** Random events (accidents, pedestrian crossings) are added by generating random numbers and mapping them to a probability distribution for how often they happen and how long they last.
- **(c)** Two measures: average waiting time and queue length (average or maximum).
- **(d)** Run the model with different light timings and compare waiting times, so the city sees the effect before changing the real lights.

**Q4. Logistics: delivery time under uncertain weather.**

- **(a)** Monte Carlo simulation uses repeated random sampling to estimate an outcome that depends on uncertain inputs. Here you sample the weather and the delivery time it causes many times and look at the distribution of delivery times (see section 4).
- **(b)** Random variables: weather condition (sunny, rainy, stormy) and the delivery time given that weather.
- **(c)** The output is a distribution, so the company can promise delivery times at a stated confidence (for example 95% of the time), which improves customer satisfaction.

**Q5. Hospital ICU beds.**

- **(a)** Entities: patients. Attributes: severity of illness, type of condition, age, expected length of stay.
- **(b)** Arrivals are usually a Poisson process. If the rate changes during the day, use a nonstationary (nonhomogeneous) Poisson process (see section 6).
- **(c)** Critical events: patient arrival (adds demand) and patient departure (frees a bed).
- **(d)** Measures: bed utilisation and the rate at which patients are turned away or balk.

**Q6. Core concepts.**

- **(a)** An entity is an object of interest that flows through the system (a customer in a bank).
- **(b)** Three attributes of an airport passenger: flight number, check-in status, number of bags.
- **(c)** An attribute belongs to one entity; a state variable describes the whole system at a moment.
- **(d)** Real experiments are often too expensive, disruptive, dangerous, slow, irreversible or unethical (section A).
- **(e)** Two critical events in emergency response: call received and unit arrival.
- **(f)** GPSS blocks are the building blocks (GENERATE, QUEUE, SEIZE and so on) that set out the logic of the model as the path a transaction follows.

**Q7. Theory and practice.**

- **(a)** Discrete-event: state changes at separate points in time (a bank). Continuous: state changes continuously (water level behind a dam).
- **(b)** Random numbers are the basic ingredient for generating the random event times and values that imitate real uncertainty (section 4).
- **(c)** Verification checks that the model is built correctly (debugging and checking against the design). Validation checks that it is the correct model, representing reality (section 7).
- **(d)** Simulation software provides ready-made constructs, input and output analysis tools and visualisation, so engineers can build and run models faster (Arena, Simul8, GPSS).

Q8 repeats Q1 word for word in your paper, so the same answer applies.

## 1. The big picture: where Simulation 2 fits

Simulation is building a model of a real or planned system and running experiments on the model, so you can see how the system behaves and compare ways of running it without touching the real thing. Part 1 gave you the vocabulary. Part 2 teaches you how to actually build a model that can be trusted: where the numbers come from, how randomness is made, and how you prove the model is believable.

### Why simulation is useful (from Part 1)

- **Cost and time:** test a design before spending money on it.
- **Risk reduction:** mistakes happen on the computer, not on the factory floor.
- **Performance prediction:** estimate throughput, waiting time, utilisation of a system that exists or is only planned.
- **Optimisation and decision support:** compare alternatives and pick the best one.
- **What-if scenarios:** change assumptions and parameters and watch the effect.
- **Learning:** building the model forces you to understand the system's structure and interactions.

### Types of simulation model

- **Discrete-event:** the system only changes at specific moments (a customer arrives, a machine breaks). Used for hospitals, queues, assembly lines. This is the main type in Part 2.
- **Continuous:** the system changes smoothly with time and is described by differential equations (fluids, heat, chemical reactions).
- **Agent-based:** many autonomous agents follow their own rules and interact (markets, social systems, epidemics).
- **Monte Carlo:** repeated random sampling to get a numerical answer, usually where time does not matter (risk assessment, estimating an area or a profit).
- **Hybrid:** a mix of the above when one system has both discrete and continuous parts.

### Components of a simulation model

- **System and environment:** what you model, and what sits outside the boundary.
- **Entities and attributes:** the things that move through (customers, parts) and their properties.
- **Resources and queues:** what serves the entities (servers, machines) and where they wait.
- **Activities and events:** work that takes time, and instants that change the state.
- **State and state variables:** a snapshot of the system at one moment, and the variables that describe it.
- **Performance measures:** the numbers you judge the system by (waiting time, utilisation, throughput).
- **Functional relationships and logic:** the rules that say how the parts affect each other and how entities flow.

### Monte Carlo and the link to Part 2

Monte Carlo is the bridge between Part 1 and Part 2. It works by feeding random numbers into a model many times and averaging what comes out. That means everything depends on having good random numbers (section 4) and the right input distributions (section 6). In Arena, the same idea is a CREATE, ASSIGN, RECORD, DISPOSE model with many replications (section 8).

### How the topics connect

1. **Problem and system definition:** what question are we answering and what is inside the boundary?
2. **Model building:** decide inputs, outputs, relationships and rules (section 5).
3. **Data collection and input analysis:** find the distributions that describe the randomness (section 6).
4. **Random numbers:** turn those distributions into numbers the computer can generate (section 4).
5. **Build and run:** a discrete-event model, for example a queue, in Arena (sections 2, 3, 8).
6. **Verify and validate:** is it built right, and is it the right model? (section 7)
7. **Experiment, analyse output, recommend:** run replications, build confidence intervals, compare designs.

If one link in this chain is weak, everything after it is weak. That is the point behind "garbage in, garbage out".

### The 10 steps for developing a simulation model (your class version)

This is the list from your handwritten notes. Section 5 below goes deeper on the lecturer's 8-step version; both say the same thing in different words, so know this one by heart and use section 5 for detail.

1. **Problem definition:** identify the fundamental problem or question the model is meant to answer.
2. **Setting of objectives:** define the objectives or criteria the system must optimise or satisfy.
3. **Model conceptualisation / system analysis:** analyse the system's components, variables, parameters, relationships, outputs and behaviours.
4. **Data collection:** gather and process the data needed to describe and quantify the system.
5. **Model formulation:** build the model that represents the system (structure, logic, assumptions, equations, the modelling approach and the software tool).
6. **Model implementation / translation:** build it in the chosen software; this includes coding, testing and documenting.
7. **Model verification:** check the model is correctly and completely implemented according to the formulation (did we build it right?).
8. **Model validation:** check the model is accurate and credible enough to represent the real system (did we build the right model?).
9. **Model experimentation:** run the model under different scenarios to answer the original problem; this includes model analysis and optimisation.
10. **Model documentation and communication:** present the model and its results to the intended audience.

Steps 1 to 3 are circled together in your notes, which tells you they form the "understand the problem" block. A good memory hook: define, aim, analyse, gather, formulate, build, verify, validate, experiment, communicate.

The same page lists the components of a simulation model (entities, attributes, events, states, variables, performance measures, plus resources, queues, activities and logic, which you marked as new entries) and the types of simulation (discrete-event, continuous, agent-based, Monte Carlo, hybrid).

### Class 1 review (25/11/25 and 01/02/26 notes)

Your first class set four questions, and they are a good map of what the course is about: (1) what is simulation and why is it useful for systems engineering; (2) what are the types and components of simulation models; (3) what are the steps and tools for developing and running simulation models; (4) what are the techniques and challenges of verifying, validating and analysing simulation models.

**Definition:** simulation is the process of creating a model of a real-world or proposed system to study its behaviour under different conditions without physically implementing the system.

**Why it is useful in systems engineering:** (1) cost and time efficiency, (2) risk reduction, (3) performance evaluation, (4) optimisation, (5) decision-making support, (6) iterative development, (7) training and testing, (8) complex system analysis.

**More definite uses (01/02/26):** predict the performance of an existing or planned system and compare alternative solutions for a design problem; optimise performance, reduce risk and uncertainty and visualise results; explore the effects of different scenarios, assumptions and parameters on behaviour and outcomes; test and improve understanding of the system's structure, dynamics and interactions. In the systems engineering lifecycle: define the problem and objectives, identify requirements and constraints, design the architecture and interfaces, implement, integrate and test, evaluate performance and stakeholder satisfaction, and manage the lifecycle and changes.

### Types of simulation models

- **Discrete-event:** changes happen at specific, distinct points in time (a patient moving through hospital departments, a product moving along an assembly line).
- **Continuous:** variables change smoothly and continuously.
- **Agent-based:** the system is a collection of autonomous agents, each with its own behaviour and rules, interacting with each other and the environment; useful for complex systems such as epidemics or social dynamics.
- **Monte Carlo:** a risk assessment model that uses repeated random sampling to get numerical results, often for systems with uncertainty.
- **Hybrid:** combines different approaches for systems with both kinds of behaviour. You marked it "not included most times".

### Components of a simulation model

1. **Entities:** dynamic objects that move through the system.
2. **Attributes:** properties of an entity.
3. **Events:** actions that cause a change in the system's state.
4. **States:** a snapshot of the system at a particular moment.
5. **Variables:** characteristics of the system at large that are not tied to one entity.
6. **Performance measures:** metrics used to evaluate the system's performance.
7. **Resources** (new entry): elements that provide service or capacity to entities and have availability and utilisation.
8. **Queues** (new entry): elements that store entities waiting for service or capacity from resources.
9. **Activities** and **logic / functional relationships:** the rules and logic that define how components interact and control the flow and behaviour of the system.

### Tools for developing and running simulation models

Arena, AnyLogic, Simulink, NetLogo, Python.

### Techniques for verification

1. **Tracing:** following the execution of the model step by step and observing changes in the system state and output data.
2. **Stepping:** pausing the execution of the model at certain points and examining the system state and output data.
3. **Breakpoints:** setting conditions or expressions that stop the model when they are met, so you can inspect the system state and output data.

### Techniques for validation

1. **Face validity:** comparing the model output with real data and expectations using common sense and expert judgement. Sensitivity analysis can also be used to check face validity: the model user is asked whether the model behaves as expected when one or more inputs change.
2. **Sensitivity analysis:** changing the values of the input parameters and observing the effect on the output data.
3. **Statistical tests:** applying statistical methods to compare model output with real data and to test the model's hypotheses and assumptions. Examples: t-test, ANOVA, chi-square test.

### Techniques for analysis (of the output)

1. **Descriptive statistics:** summarising and presenting output data using measures of central tendency (mean, median, mode) and dispersion (range, standard deviation, variance).
2. **Confidence intervals:** estimating the range of values that contains the true value of a parameter with a certain level of confidence, such as 95% or 99%.
3. **Hypothesis testing:** testing the validity of a claim about a parameter using the output data and a significance level such as 0.05 or 0.01.
4. **Optimisation:** finding the values of the decision variables that maximise or minimise an objective function (profit, cost, throughput) subject to constraints (capacity, budget, quality).

### Challenges for verifying, validating and analysing

1. Data availability and quality.
2. Model complexity and scalability.
3. Model uncertainty and variability.
4. Communication and presentation of the results (ticked in your notes, so it was probably stressed).

To link this to section 7: the three-step validation approach (high face validity, validate assumptions, compare input-output transformations) and the structural versus data assumptions are covered there.

## 2. Discrete-event simulation and the queueing system

Discrete-event simulation (DES) is the variation in a model caused by a chronological sequence of events acting on it. Nothing happens between events, so the simulation jumps from one event to the next instead of ticking through every second. This is why a simulation can cover weeks of real operation in a few seconds.

### The building blocks

- **Event:** an instantaneous occurrence that may change the state of the system (arrival, start of service, departure, breakdown, repair).
- **State variable:** one or more variables that completely describe the system at a given moment. The value of the state variable is the state.
- **Clock:** keeps track of simulation time and triggers events. Simulation time is not the same as wall-clock (real) time. A model can run much faster than real time.
- **Event list:** a list of the next times each event will happen, ordered by increasing time. When the clock reaches the first time on the list, that event is executed, the state changes instantly, and the event is removed from the list.

**Example, traffic light:** the state variable is the light colour. The value of that colour at any moment completely describes the state. The events are switch to red, switch to yellow, switch to green.

### The queueing system

A queueing system is any system where a customer asks for service from a resource of limited capacity. It is also called a system of flow. A waiting line forms because arrivals are unpredictable and service time is often longer than the gap between arrivals.

There are three major events: **arrival** of a customer, **servicing** of the customer, **departure** of the customer.

### Configurations

| Configuration | What it looks like | Everyday example |
| --- | --- | --- |
| Single queue, single server | One line feeding one server | BRT queue |
| Single queue, multiple servers | One line feeding several servers | Banks, supermarkets |
| Multiple queues, multiple servers | Each server has its own line | Fuel station, ATMs |

### Characteristics of a queueing system

1. **Calling population:** the pool of potential customers. Finite if the exact number expected is known (a doctor with booked appointments). Infinite if the number who could come is unknown (a fuel station). Finite population means arrivals depend on how many are already in the system.
2. **System capacity:** the limit on how many customers can be in the system or waiting line. It is independent of the calling population and is mostly finite.
3. **Customer arrival:** a random event, described by arrival time and arrival rate. Random events are represented by statistical distributions.
4. **Customer service time:** the time the server needs to attend to one customer. Also random.
5. **Inter-arrival time:** the time between two consecutive arrivals.
6. **Queue behaviour:** what customers do while waiting (below).
7. **Queue discipline:** the logical order in which customers are picked when a server becomes free.

### Queue behaviour

- **Balking:** the customer sees the line is too long and never joins.
- **Reneging:** the customer joins, feels the line is moving too slowly, and leaves.
- **Jockeying:** the customer leaves one line to join another line they think is faster. This only makes sense with multiple queues.

### Queue discipline

The default is **FIFO** (first in, first out), which is the queue data structure. Others are **LIFO** (last in, first out), **SIRO** (service in random order), **SPT** (shortest processing time first) and **PR** (service by priority).

### Connecting it to the rest

The arrival and service times are random, so each one is drawn from a distribution found by input analysis (section 6) and generated from random numbers (section 4). The measures in section 3 then tell you how well the queue is performing. In Arena (section 8) the entity is the customer, the resource is the server and the queue is the waiting line.

## 3. Measuring a queue: notation, formulas and Little's law

Once you have a queue, you need a short way to describe it and a set of numbers to judge it by. Kendall's notation does the describing. The performance measures do the judging.

### Kendall's notation: A/B/c/N/K

| Letter | Meaning |
| --- | --- |
| A | Inter-arrival time distribution |
| B | Service time distribution |
| c | Number of servers |
| N | Queue (system) capacity |
| K | Size of the calling population |

Symbols used for the distributions: **M** = exponential (arrivals form a Poisson process), **D** = deterministic (constant), **G** = general (any distribution), **E\_k** = Erlang. When N and K are infinite you just write A/B/c.

**Example:** M/M/1 means exponential inter-arrival times, exponential service times and one server.

### Performance measures and how to compute them

These are the measures from your class notes. Each customer i has an arrival time, a start-of-service time, a service time and a departure time.

| Quantity | Symbol | Formula |
| --- | --- | --- |
| Inter-arrival time | a\_i | arrival time of i minus arrival time of i-1 |
| Delay (wait in queue) | w\_i | start of service of i minus arrival of i |
| Departure time | dep\_i | start of service of i plus service time of i |
| Residence time (time in system) |  | departure of i minus arrival of i, which equals delay plus service time |
| Mean delay |  | sum of delays divided by n |
| Mean residence time |  | sum of residence times divided by n |
| System busy time | B | sum of all service times |
| Utilisation | ρ | B divided by T, where T is the simulation time |

Utilisation is always between 0 and 1. It is the proportion of time the server is busy. Idle time is the opposite: T minus B.

*Notation warning:* in your handwritten notes the letter d is used both for delay and for departure time. Keep them apart in an exam by using your own symbols, for example w for delay and dep for departure.

### Worked example: four customers, one server (FIFO)

| Customer | Arrival | Service starts | Service time | Departure | Delay | Time in system |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | 2 | 4 | 6 | 0 | 4 |
| 2 | 5 | 6 | 3 | 9 | 1 | 4 |
| 3 | 6 | 9 | 5 | 14 | 3 | 8 |
| 4 | 10 | 14 | 2 | 16 | 4 | 6 |

How to read it: a customer starts service at the later of their own arrival time and the moment the previous customer leaves. Mean delay is (0+1+3+4)/4 = 2. Mean time in system is (4+4+8+6)/4 = 5.5. Busy time is 4+3+5+2 = 14 out of T = 16, so utilisation is 14/16 = 0.875.

### Little's law

The average number of customers in the system equals the arrival rate times the average time a customer spends in the system.

```latex
L = \lambda W
```

The same law works for the queue alone: Lq = λ Wq. It holds whatever the arrival and service distributions are, so it needs no special assumptions. That is why it is so widely used to check a simulation's output.

### M/M/1 formulas (one server, infinite capacity)

Here λ is the arrival rate and μ the service rate, and the queue is stable only if ρ = λ/μ is less than 1.

```latex
\rho = \frac{\lambda}{\mu}, \quad L = \frac{\rho}{1-\rho}, \quad L_q = \frac{\rho^2}{1-\rho}, \quad W = \frac{1}{\mu-\lambda}, \quad W_q = \frac{\rho}{\mu-\lambda}, \quad P_0 = 1-\rho
```

**Check with the Arena pharmacy example:** arrivals 10 per hour gives λ = 1/6 per minute, service mean 3 minutes gives μ = 1/3. So ρ = 0.5, Lq = 0.25/0.5 = 0.5 and Wq = 0.5/(1/6) = 3 minutes. The Arena run gave about 3 minutes wait and about 50 percent utilisation, so simulation and theory agree within sampling error.

### Connecting it to the rest

M/M/1 and M/M/c have exact formulas, so they are the test cases used in validation (section 7): run the simulation and compare. Once the distributions are anything else (for example normal service times, as in the exam bank question), the formulas no longer apply and simulation is the tool. For several servers (M/M/c) the stability condition becomes ρ = λ/(cμ) < 1, and the formulas are in the box just below.

### M/M/c formulas (c identical servers)

These are the standard textbook (Erlang C) results. Your notebook photos were unreadable, so I added these from standard queueing theory; compare them with your own notebook. Let a = λ/μ (the offered load) and ρ = λ/(cμ), which must be less than 1.

- **Probability the system is empty:** P0 = 1 / \[ (sum for n = 0 to c−1 of aⁿ/n!) + (aᶜ / c!) × (1/(1−ρ)) \]
- **Probability an arriving customer has to wait (Erlang C):** P(wait) = (aᶜ / (c!(1−ρ))) × P0
- **Average queue length:** Lq = P(wait) × ρ/(1−ρ)
- **Average wait in queue:** Wq = Lq/λ = P(wait) / (cμ − λ)
- **Average time in system:** W = Wq + 1/μ
- **Average number in system:** L = Lq + a (Little's law again)

Sanity check: with c = 1 these collapse to the M/M/1 formulas above (P(wait) = ρ, Lq = ρ²/(1−ρ)). Worked example: λ = 2 per minute, μ = 1.5 per minute, c = 2. Then a = 1.333, ρ = 0.667, P0 = 1/(1 + 1.333 + 1.778/0.333) = 1/7.667 = 0.130, P(wait) = (1.778/0.333) × 0.130 = 0.696, Lq = 0.696 × 2 = 1.39, Wq = 1.39/2 = 0.70 minutes.

## 4. Random numbers, random number generation and Monte Carlo

Every random thing in a simulation (arrival gaps, service times, breakdowns) starts from a stream of random numbers between 0 and 1. These are then turned into the distribution you need. So the quality of the whole simulation rests on how good these numbers are.

### What a random number is

A sequence R1, R2, ... must have two properties: **uniformity** (each number is equally likely anywhere in \[0,1\]) and **independence** (knowing one number tells you nothing about the next). For a continuous uniform variable on \[0,1\]:

```latex
E(R) = \frac{1}{2}, \qquad V(R) = \frac{1}{3} - \left(\frac{1}{2}\right)^2 = \frac{1}{12}
```

If \[0,1\] is divided into n equal classes, each class should hold N/n of the N observations, and the chance of landing in a class must not depend on the previous values.

### Pseudo-random numbers

Computers cannot make truly random numbers. They use a known formula, so the numbers are called **pseudo-random** ("pseudo" means false). The goal is to make them behave as if they were random and uniform. Possible departures from ideal behaviour are:

- not uniformly distributed, or discrete instead of continuous
- mean or variance too high or too low
- dependence: autocorrelation between numbers, runs above or below the mean, or runs of high and low values

**What a good routine needs:** fast, portable between computers, a long cycle before the sequence repeats, replicable (same seed gives the same numbers, which helps debugging and fair comparison of designs), and numbers that closely match the ideal uniform and independent properties.

### Linear congruential method (LCM)

This is the most widely used method. It produces integers and then scales them.

```latex
X_{i+1} = (aX_i + c) \bmod m, \quad i = 0,1,2,\ldots \qquad\qquad R_i = \frac{X_i}{m}
```

- X0 is the **seed** (starting value)
- a is the **constant multiplier**
- c is the **increment**
- m is the **modulus**

The choice of a, c, m and X0 strongly affects the mean, the variance and the cycle length. If c is not zero it is the **mixed** congruential method. If c = 0 it is the **multiplicative** congruential method.

**Worked example (from your class exercise):** generate the first six numbers with X0 = 37, a = 17, c = 29, m = 100.

| i | Calculation | X\_i | R\_i = X\_i / 100 |
| --- | --- | --- | --- |
| 1 | (17 × 37 + 29) mod 100 | 58 | 0.58 |
| 2 | (17 × 58 + 29) mod 100 | 15 | 0.15 |
| 3 | (17 × 15 + 29) mod 100 | 84 | 0.84 |
| 4 | (17 × 84 + 29) mod 100 | 57 | 0.57 |
| 5 | (17 × 57 + 29) mod 100 | 98 | 0.98 |
| 6 | (17 × 98 + 29) mod 100 | 95 | 0.95 |

Each X feeds the next. The textbook example with X0 = 27, a = 17, c = 43, m = 100 gives X1 = 2, X2 = 77, X3 = 52, so R = 0.02, 0.77, 0.52.

### Getting the longest period

- **Mixed, m = 2^b:** the longest possible period is P = m, reached when c is relatively prime to m and a = 1 + 4k.
- **Multiplicative, m = 2^b:** the longest possible period is P = m/4, reached when the seed is odd and a = 3 + 8k or 5 + 8k.
- **Multiplicative, m prime:** the longest possible period is P = m - 1, reached when a is chosen so that the smallest k making a^k - 1 divisible by m is k = m - 1.
- **Example:** a = 13, m = 64, c = 0 gives P = 64/4 = 16 with seed 1 or 3. Seed 2 gives period 8 and seed 4 gives period 4, so a bad seed shortens the cycle.

A long period matters because once the sequence repeats, your simulation is reusing the same randomness. Also, a large modulus gives a fine spacing between possible values (maximum density), so the numbers cover \[0,1\] smoothly.

### Combined generators and streams

With modern computing a single generator with period around 2 billion is too short for big simulations. Combining two or more multiplicative generators (L'Ecuyer's method) gives periods of order 10^18. A **stream** is simply a separate piece of the sequence, started from its own seed. Giving each source of randomness (arrivals, service, breakdowns) its own stream lets you compare two designs fairly using the same random inputs.

### Testing the numbers

The tests fall in two groups: uniformity and independence. For each one you set up a null hypothesis, compute a statistic and compare it with a critical value at a chosen significance level α (often 0.05).

**Uniformity: H0: R \~ U\[0,1\], H1: R is not.** Failing to reject H0 means no evidence of non-uniformity was found. It does not prove the numbers are perfect. α is the probability of rejecting a good generator (a Type I error).

1. **Kolmogorov-Smirnov test.** Compares the empirical cdf with the uniform cdf. Works for small samples and uses the data without grouping.
   - Sort the numbers smallest to largest: R(1) ≤ ... ≤ R(N).
   - Compute D+ = max of (i/N - R(i)) and D- = max of (R(i) - (i-1)/N). Then D = max(D+, D-).
   - Look up the critical value Dα for N and α. If D is larger than Dα, reject. Otherwise do not reject.
   - *Example:* the five numbers 0.44, 0.81, 0.14, 0.05, 0.93 give D+ = 0.26 and D- = 0.21, so D = 0.26. The critical value for N = 5, α = 0.05 is 0.565. Since 0.26 is smaller, the numbers are not rejected as uniform.
2. **Chi-square test.** Splits \[0,1\] into n equal classes and compares observed counts Oi with expected counts Ei = N/n. Needs a large sample, with each Ei at least 5.

```latex
\chi_0^2 = \sum_{i=1}^{n} \frac{(O_i - E_i)^2}{E_i}, \qquad E_i = \frac{N}{n}
```

Compare with the table value with n - 1 degrees of freedom. *Example:* 100 numbers in 10 classes gave χ² = 3.4, much smaller than the critical value 16.9 (9 degrees of freedom, α = 0.05), so not rejected.

**Independence: H0: the numbers are independent, H1: they are not.**

3. **Autocorrelation test.** Checks whether numbers a fixed distance (the lag m) apart are correlated. Start at the i-th number and look at every m-th number after it.
   - H0: the autocorrelation is 0. H1: it is not 0.
   - M is the largest integer such that i + (M+1)m ≤ N. Compute the estimate, its standard deviation and the statistic Z0 = estimate / standard deviation.
   - Do not reject if Z0 lies between -z(α/2) and +z(α/2). For α = 0.05 that is ±1.96.
   - If the estimate is positive, high numbers tend to be followed by high ones. If negative, high ones tend to be followed by low ones.
   - *Example:* N = 30, i = 3, m = 5 gave Z0 = -1.516, inside ±1.96, so no evidence of autocorrelation.
4. **Runs tests** (up and down, above and below the mean) also check independence. Your textbook names them but the pages you sent focus on the three above.

**Passing is not enough:** a generator tested many times will fail an occasional test purely by chance (at α = 0.05, about 5 in 100 tests). One failure is not proof of a bad generator, so you repeat or add other tests.

### Turning random numbers into other distributions

Once you have uniform R values you transform them into the distribution you need. This is called random-variate generation. For the exponential distribution with rate λ, the inverse-transform method gives X = -(1/λ) ln(1 - R). Packages such as Arena do this for you through functions like EXPO(mean), UNIF(a,b), NORM(mean, sd) and DISC for empirical tables.

### Monte Carlo simulation

Monte Carlo uses random numbers to estimate something that is hard to compute directly. The pattern is always the same: generate random inputs, compute the result, repeat many times, and average. Time plays no role, so it is called a static simulation.

- **Area under a curve:** to estimate the area of f(x) from a to b, draw x = a + (b - a) R, compute f(x), and the area is (b - a) times the average of f(x). The textbook example uses the square root of x from 1 to 4. The true value is 4.66, and 20 replications gave about 4.39, with the gap due to sampling error.
- **News vendor problem:** daily demand drawn from a table, profit computed each day (sales revenue + salvage - ordering cost), averaged over many days.

The link back to this section: if the random numbers are poor, every Monte Carlo and every queue simulation inherits the problem. The link forward: more replications reduce sampling error, which is why Arena reports a 95 percent confidence half-width (section 8).

## 5. Model building: from a messy problem to a working model

Model building is a sequence of eight steps. Each step feeds the next, and you often go back a step when something does not fit.

1. **Problem analysis and information collection.** Study the problem itself: identify the input parameters, the performance measures of interest, the relationships among parameters and variables, and the rules governing how the system's components operate. Then write this down as logic flow diagrams, hierarchy trees, a narrative, or whatever way communicates it best.
2. **Data collection.** You need data to estimate the model's input parameters. The analyst makes assumptions about the distributions of the random variables. This leads to input analysis (section 6).
3. **Model construction.** With the problem understood and the data in hand, build the model and implement it as a computer program (for example in Arena).
4. **Model verification.** Check the model is built correctly: it matches its specification and does what it is supposed to do.
5. **Model validation.** Treat every model as a proposal until it is checked against the real system's measurements.
6. **Designing and running experiments.** Once the model is judged valid, design the runs (length, replications, scenarios) to estimate performance and solve the project problem.
7. **Output analysis.** Analyse the results logically and statistically, for example to pick the best of several competing designs.
8. **Final recommendations.** Turn the output analysis into recommendations for the underlying problem.

Verification and validation get their own section (7) because they are where most credibility is won or lost.

### Step 1 in practice: the questions to ask

Your class notes list this sequence for problem analysis:

- Identify the system of interest and determine the performance measures of interest.
- Generate likely questions and decide which one you want to solve. Then define the problem.
- List all components of the system and generate the assumptions or properties of the system.
- Draw a complete flow chart identifying all the parameters necessary.
- Determine the input parameters, then collect the data.

As an exercise, your lecturer asked for six relevant questions about a job shop (two products A and B, three machines M1, M2, M3, different routing and processing times). A good set starts with What, How, Why, Can, Does and Should, for example: What is the utilisation of each machine? How long does a job spend in the system? Why do jobs queue at M2? Can a different routing reduce delay? Does a breakdown at one machine block the others? Should we add a machine?

### Collecting data well (from your notes)

- Plan ahead and practise with a trial observing session.
- Watch for unusual circumstances and check accuracy. Analyse the data as it is collected, so mistakes are caught early.
- Combine homogeneous data sets: only merge samples that come from the same conditions.
- Check for relationships between variables and for correlation.
- Collect input data, not performance data. You need the raw arrival and service times, not the waiting times they produce, because waiting time is what the model has to predict.

### Worked case: the production control problem

A packaging and warehousing process: product is filled and sealed, units go into boxes with stickers, boxes go to the warehouse to meet customer demand. This is the case your lecturer used, and it is very close in style to the exam's manufacturing question.

| Part of the system | Assumption | Deterministic or stochastic? |
| --- | --- | --- |
| Raw materials | Always enough, the process never starves | Deterministic |
| Batch size | 5 units per batch | Deterministic |
| Processing time | Uniform between 10 and 20 minutes per unit | Stochastic |
| Time between failures | Exponential, mean 200 minutes | Stochastic |
| Repair time | Normal, mean 90, standard deviation 45 minutes | Stochastic |
| Warehouse capacity | Target level R = 500 units | Deterministic |
| Restart level | Reorder point r = 150 units | Deterministic |
| Customer inter-arrival time | Uniform between 3 and 7 hours | Stochastic |
| Demand size | Uniform between 50 and 100 units | Stochastic |

**How the logic works:** production runs until the warehouse reaches 500 units. Then the process is blocked and sits idle until stock falls to 150, when it restarts with a new batch. Idle time is not wasted: the resource can be given to another product that is not part of the model. When a customer arrives, stock is checked at once. If there is enough, the demand is met. If not, either the available part is sold and the rest is lost, or the whole demand is lost, depending on the loss policy.

**Performance questions that follow:**

1. Can we improve the customer service level (percentage of customers whose demand is fully met)?
2. Is the machine under-utilised or over-utilised (machine utilisation)?
3. Is maintenance adequate (downtime probabilities)?
4. What is the trade-off between inventory level and customer service level?

**One thing to notice:** a normal repair time with mean 90 and standard deviation 45 can in theory produce negative values. In a real model you would truncate it at zero. It is a good example of an assumption you should state and defend.

### Connecting it to the rest

Step 2 hands directly to section 6 (which distribution fits the data). Steps 4 and 5 are section 7. Step 3 is done in Arena (section 8). Production rate, inventory level and customer demand in this case are linked: if production is slow or breaks down, inventory falls and customers are lost. If production is fast and demand is slow, stock hits the target level and the process blocks. The variability of each one (failures, demand sizes, arrival gaps) is what makes a simulation worth running instead of using averages.

## 6. Input analysis: choosing the right distributions

Input analysis answers one question: what distribution should I use for each random input, such as inter-arrival times, service times and breakdown times? Your flowcharts can be perfect and your model can run, but if the inputs are wrong, the outputs are wrong. This is **garbage in, garbage out (GIGO)**.

**Examples of how it goes wrong:** if you assume constant gaps between arrivals when they are really exponential, you may never see a line form. If you assume a constant arrival rate across the day when it actually changes, the busy periods disappear. If you get the distribution right but the rate wrong, the whole system is mis-sized.

### The four steps

1. **Collect data** on the real process. Know what type of data you need before you start. Start by understanding the process (arrival, service, departure) and drawing it as a flowchart.
2. **Determine the statistical distribution** that describes the data, for example Normal(30, 8).
3. **Estimate the parameters** of that distribution (mean, standard deviation, minimum, maximum).
4. **Test the suitability** of the fit with a goodness-of-fit test, for example the chi-square test or the Kolmogorov-Smirnov test.

The approach is to choose a reasonable distribution and then test that it is not ridiculous. For example, if you think data is normal, it should fall roughly on a straight line on a normal probability plot and pass a goodness-of-fit test for normality.

### Look at the data first

- **Histogram:** the shape suggests the distribution. With enough observations it converges to the true distribution.
- **Stem-and-leaf diagram:** a sideways histogram that keeps every number. Each value is split into a stem (leading digits, for example the tens) and a leaf (usually the last digit). In your class example the scores 100, 100, 99, 98, ... are listed with stems 10, 9, 8, ... down to 4.
- **Scatter diagram:** shows whether two variables are related, which matters for correlated data.

### Questions to ask when choosing a distribution

- Is the data discrete or continuous?
- Is it univariate (one variable) or multivariate (several that move together)?
- How much data is available?
- Are experts around to ask about the nature of the data?
- If there is very little data, can you still guess a reasonable distribution?

### Common distributions and when to use them

| Type | Distribution | Typical use |
| --- | --- | --- |
| Discrete | Bernoulli(p) | One trial: success or failure |
| Discrete | Binomial(n, p) | Number of successes in n trials |
| Discrete | Geometric(p) | Number of trials until the first success |
| Discrete | Negative binomial | Number of trials until a fixed number of successes |
| Discrete | Poisson(λ) | Count of arrivals in a time interval |
| Discrete | Empirical | Sample distribution from the data itself |
| Continuous | Uniform | Only min and max are known |
| Continuous | Triangular | Min, max and most likely value are known |
| Continuous | Exponential(λ) | Inter-arrival times of a Poisson process |
| Continuous | Normal | Heights, weights, sample means, averages and sums |
| Continuous | Beta | Bounded data |
| Continuous | Gamma, Weibull, Gumbel, lognormal | Reliability data and job or repair times |
| Continuous | Empirical | Sample distribution from the data itself |

The link between two entries matters: if the count of arrivals in an interval is Poisson, then the time between arrivals is exponential. That is why M in Kendall's notation means both.

### Four common challenges

These four are the heart of the exam's input-modelling and data-challenges questions.

**1. No or little data.** This turns up more often than you would expect: there may be no data, or the data is awful (goofy values, not cleaned). There are no great options, but you can:

- Interview experts and ask for minimum, maximum and most likely values, then use a uniform or triangular distribution. Quantiles from the expert are even better.
- Decide discrete or continuous. Success or failure observations suggest Bernoulli, binomial, geometric or negative binomial. Counting arrivals suggests Poisson, and the time between them exponential. Averages or sums suggest normal. Bounded values suggest beta. Reliability or job times suggest gamma, Weibull or lognormal.
- Think about the physical process behind the variable.

**2. Nonstandard or mixture distributions.** Some data looks like two normal curves forced together, and most packages cannot fit it. Options: model it as a mixture of reasonable distributions (piece by piece), or sample directly from the empirical distribution or a smoothed version of it. Sampling from the data is a form of bootstrapping.

**3. Nonstationary data.** Arrival rates change over time (restaurants, highway traffic, call centres, seasonal demand). You must account for this or you get GIGO. The suggestion is a **nonhomogeneous Poisson process**, which needs a properly modelled rate function. A practical way is to use a constant arrival rate within each separate period (for example each hour).

**4. Multivariate or correlated data.** Data need not be independent and identically distributed. Examples: a person's height and weight are correlated; monthly unemployment rates are serially correlated; arrivals to a website jump when something goes viral; a badly damaged part may need longer service at several stations in a row; a tired server gives longer service times. What to do:

- Identify the correlation situation and propose a model: **multivariate normal** for variables like height and weight, **time series models** (ARMA(p, q), EAR(1)) for serial correlation.
- Estimate the parameters. For multivariate normal: the means, variances and covariances.
- Validate that the fitted model is actually good.
- Alternative: bootstrap samples from the empirical distribution if you have enough data.

If you ignore correlation, the model produces too little variability: queues look shorter and delays smaller than in reality, and the decisions built on them are over-optimistic.

### Software for fitting

- **Arena Input Analyzer** (Tools menu): fits distributions from its library (about 11 in your note) and reports the best fit with sample and goodness-of-fit statistics.
- **ExpertFit:** a specialist product with a larger library.
- **Minitab, R, MATLAB:** have fitting functions, though less convenient.

### Connecting it to the rest

This section tells you which distribution to use. Section 4 explains how the computer produces values from it. Section 8 shows the Arena functions that implement it, for example EXPO(6) for an exponential with mean 6 minutes, NORM(4, 1) for a normal, TRIA(0.75, 1.5, 3) for a triangular.

## 7. Verification, validation and calibration: can the model be trusted?

A model is only useful if the people who use its results believe them. Engineers and managers rightly look at a model with some scepticism. Verification and validation are how you earn that trust. The goal is twofold: a model that represents true system behaviour closely enough to stand in for the real system, and a model that users find credible.

### Key definitions

| Term | Meaning in plain English |
| --- | --- |
| Verification | Checking that the model implementation and its data accurately match the developer's conceptual description and specification. Did I build the model right? |
| Validation | Checking how well the model and its data represent the real world for its intended use. Did I build the right model? |
| Calibration | The iterative process of comparing the model to the real system, adjusting the model, comparing again, and repeating until the accuracy is acceptable. |
| Accreditation | Official certification that a model is acceptable for a specific purpose. |
| Conceptual model | The developer's description of what the model will represent, the assumptions that limit it, and the capabilities needed to meet the user's requirements. |

### Verification versus validation

|  | Verification | Validation |
| --- | --- | --- |
| Question | Am I building the model right? | Am I building the right model? |
| Compares | The conceptual model with the computer program | The model and its behaviour with the real system |
| Purpose | Make sure the concept is reflected accurately in the operational model | Make sure the model is an accurate representation of the real system |
| Usually done by | Debugging and checking the logic | Calibration and comparison with real data |

They are different questions but are usually worked on at the same time. The model-building chain is: observe the real system, build a conceptual model (assumptions and structure), then build the computerised model. Verification checks the step from concept to code. Validation checks the model against reality.

### Verification techniques

- Have someone other than the developer check the computerised model.
- Draw a flow diagram of every logically possible action for each event, and trace the model logic against it.
- Examine the output for reasonableness under many different input settings.
- Have the model print its input parameters at the end of the run to be sure they were not changed by accident.
- Make the code as self-documenting as possible.
- If the model is animated, check that the animation imitates the real system.
- Use the interactive run controller (debugger): watch the run progress, focus on a line of logic or an entity, observe the current value of variables, attributes, queues, resources and counters, and pause to reassign values or redirect entities. The ideas of **tracing**, **stepping** and **breakpoints** (stop when a condition is met) come from here.

### Validation methods

| Method | What you do |
| --- | --- |
| Face validity | Ask people who know the system whether the model and its behaviour look reasonable (logic and input-output relationships). |
| Comparison to other models | Compare simple cases with known analytic results (for example M/M/1 formulas) or with another validated simulation. |
| Historical data validation | Use part of the data to build the model and the rest to test whether the model behaves like the system. |
| Sensitivity analysis (parameter variability) | Change input and internal parameters and see whether the output changes in the way the real system would. Sensitive parameters must be made especially accurate. |
| Predictive validation | Use the model to forecast, then compare the forecast with what the system actually does. |
| Statistical tests | t-test (compare two means), ANOVA (more than two means), chi-square (compare observed and expected frequencies) and hypothesis tests on output. |

Except for face validity, all of these are data-driven. Predictive validation is among the most commonly used but needs real effort to gather and analyse data.

### The three-step approach to validation (from your notes)

1. **Build a model with high face validity.** Use all available information: talk to people who know the system, use observations, past studies. Face validity is subjective, but it is where you catch a model that is obviously wrong.
2. **Validate the model assumptions.** Structural assumptions are about how the system works and is simplified (for example one line or several, how customers are served). Data assumptions should rest on reliable data and proper statistical tests of the fitted distributions (section 6).
3. **Validate input-output transformations.** The ultimate test is whether the model can predict the future behaviour of the real system when fed the real inputs. Run the model with real input data and compare its output with the real system's output. A Turing test (ask experts whether they can tell model output from real output) can supplement this.

### Calibration: the iterative loop

Calibration is repeated adjustment. Compare model and system, find the discrepancies, change the model (for example fix a wrong assumption or refine a parameter), compare again, and stop when accuracy is judged acceptable. It never ends on its own; you stop when the model is good enough for its purpose and the cost of improving it is not worth the gain.

### Errors and risks in V&V

When you decide whether to use a model, you can be right or wrong in three ways.

| Error | What happens | Whose risk | How serious |
| --- | --- | --- | --- |
| Type I | A valid model is not used because validation did not convince anyone | Model builder's risk | Less serious: wasted development cost and lost benefits |
| Type II | An invalid model is used because validation was done wrongly but convincingly | Model user's risk | More serious: can lead to disasters, for example a collapsed bridge from faulty load analysis |
| Type III | A model that is valid for something else is used for the wrong application | Model accreditor's risk | More serious: similar consequences to Type II |

Type III errors are common, because a model that has worked well for its original use gains an unjustified reputation for broad validity.

### Bounds of validity and credibility

The goal of V&V is not to declare "the model is valid". It is to find the range of inputs over which the model is accurate enough, called its **bounds of validity**. In the textbook's falling-object example, three models of height against time looked equally good if you only tested a single time or a narrow range. Only testing across the full range of inputs the model would meet in real use separated the best from the rest. So validate over the whole range of intended use, and document the range, otherwise someone may reuse the model outside it.

**Credibility** is how likely the results are to be accepted. V&V and accreditation build it, but it costs money. Utility rises with credibility with diminishing returns, while cost rises faster and faster. The project manager balances the two and stops adding credibility when the extra cost is not worth the extra utility.

### Connecting it to the rest

Verification asks whether the code matches the design from section 5. Validation depends on section 6 (are the distributions right?) and on the random numbers in section 4. In the exam, the logistics-model question (Q2) asks you to distinguish the three terms, explain face validity, and describe iterative calibration, all from this section.

## 8. Arena: building and running the model

Arena is commercial simulation software (Rockwell Automation) that gives you a drag-and-drop flowchart way to build models. Underneath it sits the SIMAN simulation language. You describe the life of an entity as it moves through the system, and Arena handles the clock, the event calendar and the statistics. I am not certain from your upload whether Arena is used in class this semester, but it appears in your 25/26 exam (Q6), your lecturer's notes and your textbook chapter, so it is covered here in full.

### The environment

- **Project bar** with templates: Basic Process, Advanced Process, Advanced Transfer, Flow Process, plus Reports and Navigate panels.
- **Model window:** where you drop and connect flowchart modules.
- **Spreadsheet (data) window:** shows a row-and-column view of the selected module, and is where data modules are filled in.
- **Flowchart modules** are dragged into the model (CREATE, PROCESS, DISPOSE, DECIDE ...). **Data modules** (ENTITY, RESOURCE, QUEUE, VARIABLE) are not dragged; you fill them in the spreadsheet or a dialog.

### The main modules (from your notes and the textbook)

| Module | What it does |
| --- | --- |
| CREATE | Creates and introduces entities into the model according to a pattern. Without it nothing happens. |
| DISPOSE | Removes entities once they have finished their activities in the model. |
| PROCESS | Lets an entity experience an activity, possibly using a resource. |
| DECIDE | Gives alternative paths for an entity, chosen by probability or by a condition. |
| BATCH | Groups entities together (a kit) before they continue. |
| SEPARATE | Copies an incoming entity into several, or splits a batched entity. |
| ASSIGN | Assigns values to variables and attributes. |
| RECORD | Captures and tabulates statistics (tally, count). |
| VARIABLE, RESOURCE, QUEUE, ENTITY | Data modules: define variables, servers with capacity, waiting lines, and entity types and pictures. |

**Useful functions:** EXPO(mean), UNIF(min, max), NORM(mean, sd), TRIA(min, mode, max), DISC(cumulative probability, value, ...) for an empirical table, NQ(queue name) for the number waiting, MN() and MX() for the minimum and maximum.

### How time works inside Arena

- Time moves in jumps from one scheduled event to the next, using an **event calendar** (the same idea as the event list in section 2).
- Processing alternates between the **entity movement phase** (the active entity moves until it hits a delay) and the **clock update phase** (advance the clock to the next event).
- Only one entity moves at a time. Every entity is in one of five states: **active** (moving now), **ready** (can move now), **time-delayed** (waiting for a scheduled time, such as being served), **condition-delayed** (waiting for a condition, such as a free server) and **dormant** (needs special logic to wake it).
- Entities that arrive from a CREATE start time-delayed, and a customer waiting for a busy server is condition-delayed.
- The **run controller** lets you step through, trace entities and inspect variables, which is how you verify the model (section 7).

### Activity diagram (conceptual model before you build)

Draw it first: queues as circles, activities as rectangles, resources as small circles, arrows for flow, dashed arrows for seizing and releasing a resource, and zigzag lines for creating and disposing entities. The pseudo-code for a single-server queue is:

```
CREATE customers with EXPO(mean inter-arrival)
PROCESS customers
    SEIZE 1 server
    DELAY for service time
    RELEASE 1 server
END PROCESS
DISPOSE customer
```

### Building a single-server queue step by step

1. **Drag** CREATE, PROCESS and DISPOSE from the Basic Process panel and connect them in that order.
2. **CREATE:** set the type of time between arrivals (random, exponential) and its mean, set entities per arrival to 1, max arrivals to infinite, and the time units (minutes).
3. **RESOURCE (data module):** add the server with capacity 1.
4. **PROCESS:** set the action to Seize, Delay, Release. Add the resource and the number of units. Choose the delay type Expression and enter the service time distribution, for example NORM(4, 1). Set the units to minutes.
5. **Queue:** Arena makes one automatically for the PROCESS module. The default discipline is first in, first out.
6. **Run, Setup, Replication Parameters:** set the replication length, the number of replications and the base time unit.
7. **Run**, then open the report. Arena reports averages, the 95 percent confidence half-width, and minimum and maximum values.

### Run parameters: how long and how many?

- **Replication length:** how long one run lasts. For a bank that closes, use the real opening hours (a terminating simulation). For long-run behaviour, use a very long run (the textbook pharmacy used 10,000 hours) and consider a warm-up period so the empty start does not bias the averages.
- **Number of replications:** each replication is an independent run, so results across replications form a random sample. More replications give a narrower confidence interval. Ten to thirty is a typical minimum.
- **Base time units** should match the model units so reports come out in minutes.

### Output statistics

Arena collects waiting time in queue, number waiting, time in system and resource utilisation automatically from the PROCESS module. Use RECORD for anything custom. The report shows each average with its 95 percent half-width, which is the plus-or-minus around the average.

### Worked check: the exam's bank queue (Q6)

Inter-arrival times are exponential with mean 5 minutes, service times are normal with mean 4 and standard deviation 1, one teller, first come first served.

- **CREATE:** EXPO(5) minutes. **PROCESS:** seize the teller, delay NORM(4, 1), release. **DISPOSE.**
- Utilisation should come out near 4/5 = 80 percent.
- **My extra sanity check, not from your notes:** for an M/G/1 queue the Pollaczek-Khinchine formula gives Wq = λ E\[S²\] / (2(1 - ρ)), with λ = 0.2, E\[S²\] = variance + mean² = 1 + 16 = 17, ρ = 0.8, so Wq = 0.2 × 17 / (2 × 0.2) = 8.5 minutes. Then Lq = λ Wq = 1.7 customers. If Arena gives roughly these values, your model passes a basic validation. This is the kind of comparison to known analytic results mentioned in section 7.

### Your lecturer's practice problem: airport security

Passengers arrive with exponential inter-arrival times (mean 2 minutes). The ID check takes a triangular time TRIA(0.75, 1.5, 3) minutes, and 93 percent of passengers pass. Draw the Arena flowchart, run 20 days, and find: average time in system, longest time in system, maximum number waiting, and the proportion of time the officer is busy. The flow is CREATE, PROCESS (ID check), DECIDE (93 percent pass, 7 percent denied by chance), then DISPOSE for each path. The proportion of time busy is the utilisation, the average and longest time come from the time-in-system statistic, and the maximum number waiting comes from the queue statistic.

### Other Arena tools

- **Input Analyzer:** fits distributions to data (section 6).
- **Process Analyzer:** runs many scenarios in a batch and compares them.
- **OptQuest:** searches for the best design configuration.
- **DECIDE with NQ():** to model balking, for example customers leave if NQ(queue) is 4 or more, use a condition-based DECIDE before the PROCESS and a second DISPOSE for those who leave.

### Connecting it to the rest

Arena is where the earlier sections come together: input distributions from section 6 go into CREATE and PROCESS, Arena's random numbers come from section 4's idea, the queue and its statistics are section 3, and checking the model against theory is section 7. The Monte Carlo models (CREATE, ASSIGN, RECORD, DISPOSE with many replications) show the same software used with no clock at all.

## 9. Past question patterns and answer outlines

The 2025/26 paper is four questions out of six, 2 hours, 15 marks each, split 5 + 5 + 5. Every question is a short case study, so you are being asked to apply the ideas to a situation, not just define them. The six cases map neatly onto the sections above, which tells you what the lecturer values.

| Question | Case | What it tests | Where in these notes |
| --- | --- | --- | --- |
| Q1 | Manufacturing system | Inputs, performance measures, relationships, conceptual model | Sections 1, 5 |
| Q2 | Logistics model credibility | Verification, validation, calibration, face validity | Section 7 |
| Q3 | Urban traffic input modelling | Input analysis, discrete versus continuous, choosing a distribution | Section 6 |
| Q4 | Hospital data challenges | Little data, nonstationary data, correlated data, mixtures | Section 6 |
| Q5 | Smart microgrid model development | Definitions, development steps, representation techniques | Sections 1, 5 |
| Q6 | Bank queue in Arena | Modules, flow, run setup, output measures | Sections 2, 3, 8 |

Four of the six (Q2, Q3, Q4, Q6) come from content that is Part 2 specific. Random number generation did not appear in this paper but is in your notes and textbook, so it can easily appear in a different year. Learn it anyway.

### How to answer a case question

1. Define the term in one line. 2. Apply it to the case with a concrete example from the scenario. 3. Add the reason or consequence. A definition with no example from the case loses marks.

### Q1: Manufacturing system (batches, breakdowns, stochastic demand, seasonality)

**(a) Four input variables and three performance measures.**

- Stochastic inputs: processing time per batch, time between machine breakdowns, repair time, customer demand size, customer inter-arrival times, seasonal demand level.
- Deterministic inputs: batch size, warehouse capacity, reorder or restart level, number of machines.
- Performance measures: machine utilisation, customer service level (percentage of demand fully met), average inventory level, lost sales, throughput or production rate, average customer waiting or back-order time.

**(b) Relationships.** Production rate feeds inventory, and demand drains it. If production exceeds demand, stock builds until the warehouse is full and production is blocked, so machine utilisation drops. If demand exceeds production, stock falls, stock-outs rise and lost sales rise, so service level drops. Variability makes this worse: a breakdown (random production stop) combined with a demand spike (random demand) causes stock-outs even when average production is enough. Seasonal demand means a fixed production plan is too high in some months and too low in others. So the average is not enough; variability in one of the three spreads into the others.

**(c) Conceptual model.** Describe or draw the flow:

1. Boundary: raw material supply (assumed unlimited) to dispatch to customers. Outside the boundary: suppliers, the market that creates demand.
2. Entities: batches or units. Resources: machines, repair crew, warehouse.
3. Process: raw material, processing in a batch, machine up or down (breakdown, repair), finished goods into the warehouse.
4. **Decision point:** is warehouse stock at the target level? If yes, production blocks. If stock is at or below the reorder point, production restarts.
5. **Decision point:** a customer arrives, is stock enough? If yes, ship in full. If not, ship partly and lose the rest, or lose the whole order.
6. **Feedback loop:** inventory level controls production (reorder logic), and stock-outs or high inventory can influence demand policy and planning.
7. Record: utilisation, service level, inventory.

### Q2: Logistics model credibility

**(a) Three terms.** Verification: confirm the code correctly implements the intended model of the delivery network (for example trace a truck through a depot step by step). Validation: confirm the model outputs resemble real delivery performance (delivery times, delays) well enough for decisions. Calibration: iteratively adjust model parameters, such as travel-time distributions or loading times, until the output matches real data, then compare again.

**(b) Face validity.** Ask dispatchers, depot managers and drivers whether the model's logic and results look reasonable. Important here because stakeholders doubt the outputs, and it is quick, cheap and shows people their knowledge was used, which builds buy-in. Limitation: it is subjective, so it must be backed by data-based tests.

**(c) Iterative calibration.** Compare model output with actual delivery data, identify the discrepancy, adjust inputs (for example distance, speeds, loading times, vehicle capacity), rerun, compare again, and stop when the error is within an agreed tolerance. Keep some data aside to test the final model on data it has not seen. Document the bounds within which the model is valid.

### Q3: Urban traffic input modelling

**(a) Input analysis.** The process of choosing and fitting the distributions for random inputs (arrival times, speeds, trip durations) from collected data. Important because the model output is only as good as its inputs (GIGO), so wrong arrival patterns give wrong congestion estimates.

**(b) Discrete and continuous.** Discrete variables take separate values, described by a probability mass function: number of vehicles arriving per minute (Poisson), number of passengers per vehicle (binomial or empirical). Continuous variables take any value in a range, described by a density function: travel speed (normal or lognormal), trip duration (gamma, Weibull or lognormal), inter-arrival time between vehicles (exponential).

**(c) Three factors that influence the choice.**

- The nature of the data: discrete or continuous, bounded or not, one variable or several.
- The amount and quality of data: with a lot of data you can fit and test, with little you rely on experts and a uniform or triangular guess.
- Shape and goodness-of-fit: histogram shape, probability plot and tests such as chi-square or Kolmogorov-Smirnov.
- Also valid: the physical process behind the variable (for example counts of arrivals suggest Poisson), and whether the data is stationary or correlated.

### Q4: Healthcare data challenges

**(a) Challenges.** Lack of sufficient data means you cannot reliably estimate distributions or test fit, so the model has high uncertainty; use experts for min, max and most likely values and a triangular or uniform distribution, collect more data, and use sensitivity analysis. Nonstationary data: patient arrivals change by hour, day and season. A single constant average rate hides peaks, so queues and waiting times are underestimated at busy times and the model loses accuracy.

**(b) Correlated data.** Arrival rate and service time often move together: a busy period may bring sicker patients needing longer treatment. If you model them as independent, the model underestimates variability and queue length, so decisions on staffing and beds will be over-optimistic.

**(c) Techniques.** Correlated data: multivariate normal for variables that are related, time series models (ARMA, EAR(1)) for serial correlation, or bootstrap from the empirical data. Mixture distributions: model as a mixture of reasonable distributions, or sample from the empirical (or smoothed empirical) distribution. For nonstationary arrivals, use a nonhomogeneous Poisson process with a rate for each period.

### Q5: Smart microgrid model development

**(a) Definitions in context.**

- Input parameters: the values fed in from outside, such as demand profile, solar and wind supply, number and size of generators, battery capacity.
- Performance measures: what you judge the system by, such as energy delivered, unmet demand, losses, efficiency, utilisation of storage and generators.
- System variables: quantities that describe the system and change during the run, such as battery state of charge, load on each line, current generation level.
- Simulation assumptions: statements you accept to simplify, such as demand and renewable supply are independent, no equipment failures, perfect forecasts, constant efficiency.

**(b) Five steps.** Problem definition (what is being optimised, boundaries). Model conceptualisation and information collection (components, relationships, rules). Data collection and input analysis (demand and weather distributions). Model construction in software. Verification and validation, then experiments and analysis. Explain each with one sentence about the microgrid.

**(c) Two representation techniques.** A flow diagram is used when the logic and sequence of decisions matter, for example the dispatch rule: use renewable first, then battery, then grid. A state chart is used when the equipment moves between modes, for example battery charging, discharging or idle, or the grid connected or islanded. An entity-relationship model is used when you need to show how the data and components are related, for example generators, loads, meters and their attributes.

### Q6: Bank queue in Arena

See section 8: modules, the flow, EXPO(5) and NORM(4, 1), resource and queue, replication length and number, output statistics, and the three measures: average waiting time (service quality), utilisation (staff workload and cost) and queue length (space and customer patience). Explain each measure's decision use, for example a waiting time of 8 minutes may lead to adding a second teller.

## 10. One-page revision sheet

### 2024/25 paper: hospital and kiosk data collection (from your handwritten answers)

**Hospital model, data to collect:** arrival data (inter-arrival times by hour), service times at each station, resource data (beds, doctors, nurses, labs), and the routing logic (the path a patient follows; it matters because it catches circular bottlenecks, for example patients stuck waiting for lab results while holding an ER bed).

**Sources:** databases (large samples), time studies (watching the flow and recording service times at stations), and interviews with doctors, nurses and technicians when data is missing.

**Challenges:** no or little data, data quality, observation bias, non-standard or mixture distributions, nonstationary data, correlated data.

**Methods to make the data accurate and representative:**

- **Input analysis:** plot histograms to see the shape, then run goodness-of-fit tests so the chosen distribution represents reality.
- **Data cleaning:** remove outliers that do not represent typical hospital operations.
- **Handling nonstationarity:** use different arrival rates for different times of the day.
- **Validation:** face validity, input-output transformation, and a Turing test (give the administrator a model-generated report and a real one; if they cannot tell them apart, the model is credible).

**Kiosk / queue data collection methods:**

- **Manual observation (time studies):** stopwatch or a mobile app to record when each customer enters the queue. Strength: the most reliable way to capture walk-aways and line-jumpers. Weakness: labour intensive.
- **Automated electronic queue management system:** pulled from kiosks and logs. Strength: a massive cleaned dataset over long periods, good for spotting nonstationary trends. Weakness: only records customers who actually take a ticket.
- **Expert interviews:** experts define system boundaries and typical behaviour; the last resort when no hard data exists.

**Implications of missing or inconsistent data:**

1. **GIGO:** flawed input data means inherently wrong output.
2. **Underestimation of queues:** missing peak-hour data makes the model under-represent system stress.
3. **Inaccurate resource allocation:** inconsistent data can make a highly utilised teller look idle, so management makes poor staffing decisions.
4. **Validation failure:** differences between the real system and the model make it hard to pass checks.

**Techniques to handle it:** expert interviews; data preprocessing and cleaning; homogeneity testing (if data was collected across different days, use statistical tests to see whether it comes from the same parent population); and an empirical distribution (if the data does not fit a normal or exponential curve, sample directly from the empirical distribution).

**Data preprocessing framework:** (i) data cleaning and filtering, (ii) stationarity analysis (partition data for nonstationary cases), (iii) exploratory data analysis (histograms for the general shape; stem-and-leaf diagrams to see whether it is univariate or multivariate), (iv) statistical independence testing (check observations are independent and identically distributed), (v) distribution fitting and parameter estimation (hypothesise a distribution from the physical characteristics of the system).

**Why it matters:** prevents GIGO, builds model credibility, captures real-world variability, avoids wrong conclusions.

### Formulas

| Topic | Formula |
| --- | --- |
| Linear congruential method | X(i+1) = (a X(i) + c) mod m, then R(i) = X(i) / m |
| Uniform random number | Mean 1/2, variance 1/12 |
| Max period, mixed, m = 2^b | P = m, with c relatively prime to m and a = 1 + 4k |
| Max period, multiplicative, m = 2^b | P = m/4, with odd seed and a = 3 + 8k or 5 + 8k |
| Max period, multiplicative, m prime | P = m - 1 |
| Chi-square | Sum of (O - E)² / E, with E = N/n and n - 1 degrees of freedom |
| Kolmogorov-Smirnov | D = max(D+, D-), reject if D is larger than the critical value |
| Inter-arrival time | arrival(i) - arrival(i-1) |
| Delay | service start(i) - arrival(i) |
| Departure | service start(i) + service time(i) |
| Utilisation | busy time / total time, between 0 and 1 |
| Little's law | L = λ W (and Lq = λ Wq) |
| M/M/1 | ρ = λ/μ, L = ρ/(1-ρ), Lq = ρ²/(1-ρ), W = 1/(μ-λ), Wq = ρ/(μ-λ) |
| Exponential from random number | X = -(1/λ) ln(1 - R) |

### One-line definitions

- **Simulation:** experimenting on a model of a real or planned system to understand it and compare strategies.
- **Discrete-event simulation:** the model changes only at events, in chronological order.
- **Event / state / clock / event list:** an instant that changes the state / the description of the system / simulation time / ordered list of future events.
- **Balking, reneging, jockeying:** does not join, joins then leaves, switches line.
- **FIFO, LIFO, SIRO, SPT, PR:** queue disciplines.
- **Kendall A/B/c/N/K:** arrival, service, servers, capacity, population.
- **Pseudo-random numbers:** generated by a formula to look uniform and independent, replicable from a seed.
- **Input analysis:** choosing and fitting distributions to data, then testing the fit. GIGO.
- **Nonhomogeneous Poisson process:** arrival rate changes with time.
- **Verification:** built right (code matches design). **Validation:** right model (matches reality). **Calibration:** iterative adjusting to match. **Accreditation:** official approval for a purpose.
- **Face validity:** experts judge the model looks reasonable.
- **Type I / II / III:** valid model rejected / invalid model used / wrong-application model used.
- **Bounds of validity:** the input range where the model is accurate enough.
- **Replication:** one independent run of the model.

### Lists worth memorising

- **8 model-building steps:** problem analysis, data collection, construction, verification, validation, experiments, output analysis, recommendations.
- **4 input-analysis steps:** collect data, choose distribution, estimate parameters, test goodness of fit.
- **4 data challenges:** little data, mixtures, nonstationary, correlated.
- **3 uniformity or independence tests:** Kolmogorov-Smirnov, chi-square, autocorrelation.
- **Arena basics:** CREATE, PROCESS (seize, delay, release), DISPOSE, DECIDE, ASSIGN, RECORD, BATCH, SEPARATE; data modules ENTITY, RESOURCE, QUEUE, VARIABLE.

### Part 1 (SSG 418) quick revision

- **Ways to study a system:** actual system or model; physical or mathematical model; analytical solution or simulation.
- **Why not experiment:** ethics, risk, cost, time, disruption, irreversible, impossible.
- **Not appropriate when:** common sense or an analytical answer works, direct experiment is cheaper, costs exceed savings, no time, no data, system cannot be defined.
- **Disadvantages:** needs training, hard to interpret random output, costly and slow.
- **Five components:** entity, attribute, state, activity, event. Attribute belongs to one entity; state variable describes the whole system.
- **Model design tension:** simplicity versus accuracy. The purpose decides the model (aircraft as particle, rigid body or deformable body).
- **12 steps (Banks):** problem, objectives, conceptualise, data, translate, verify, validate, experimental design, runs, more runs, document, implement.
- **GPSS core:** GENERATE, QUEUE, SEIZE, DEPART, ADVANCE, RELEASE, TERMINATE. Facility is one server, storage is several. Transactions are the moving entities.
- **GPSS check:** utilisation is roughly mean service time over mean inter-arrival time (13.5 / 15 = 0.9; the run gave 0.879).

### Likely questions beyond the 25/26 paper

1. Generate random numbers with a given a, c, m and seed, then test them (KS or chi-square).
2. Hand-simulate a queue from a table of arrivals and service times, and compute delay, utilisation and time in system.
3. Explain Type I, II and III errors with an example.
4. Describe the Arena model for a given queue, including a DECIDE module and output statistics.
5. Compare simulation output with M/M/1 formulas as a validation exercise.

### What to double-check yourself

A few things in these notes did not come straight from your handwriting, so check them against your own notebook and what your lecturer stressed: the M/M/c formulas (standard theory, added by me), the Pollaczek–Khinchine check in the bank queue example (also mine), and the Kelton textbook, which I only used for chapters matching your topics. Everything else comes from your class notes, the lecture PDFs and past questions.
