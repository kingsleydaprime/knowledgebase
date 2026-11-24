# SSG 418 and SSG 517 Question Bank

Every past and practice question from SSG 418 (Systems Simulation 1) and SSG 517 (Systems Simulation 2) that the author collected, in one place. The questions are left unsolved on purpose, and each one points to the lesson that teaches it.

**How to use this:** attempt each question closed-book, on paper, as if in the exam. Then open the linked lesson and compare. The value is in the attempt.

**How to answer a case question:** (1) define the term in one line, (2) apply it to the case with a concrete example from the scenario, (3) add the reason or consequence. A definition with no example from the case loses marks.

---

## SSG 517, 2025/26 paper

**Format:** answer four questions out of six in 2 hours; 15 marks each, split 5 + 5 + 5. Every question is a short case study. The wording below is rebuilt from the answer outlines in the author's notes, so check it against the paper itself.

### Question 1: a manufacturing system

A plant produces in batches, its machines break down at random, customer demand is random, and demand is seasonal.

- **(a)** Identify four input variables and three performance measures for a simulation of the system. → [[systems-simulation/26-model-building-2|26 — Model Building 2]]
- **(b)** Explain the relationships between production rate, inventory level and customer demand, and how variability affects them. → [[systems-simulation/26-model-building-2|26 — Model Building 2]]
- **(c)** Describe a conceptual model of the system, with its boundary, entities, resources, decision points and feedback. → [[systems-simulation/25-model-building-1|25 — Model Building 1]] and [[systems-simulation/06-types-and-components-of-simulation-models|06 — Types and Components of Simulation Models]]

### Question 2: credibility of a logistics model

Stakeholders doubt the outputs of a delivery network simulation.

- **(a)** Distinguish verification, validation and calibration in this context. → [[systems-simulation/31-verification-and-validation-1|31 — Verification and Validation 1]]
- **(b)** Explain face validity and why it matters here. → [[systems-simulation/32-verification-and-validation-2|32 — Verification and Validation 2]]
- **(c)** Describe how you would calibrate the model iteratively. → [[systems-simulation/32-verification-and-validation-2|32 — Verification and Validation 2]]

### Question 3: input modelling for urban traffic

- **(a)** What is input analysis, and why is it important for a traffic model? → [[systems-simulation/27-input-analysis-1|27 — Input Analysis 1]]
- **(b)** Distinguish discrete and continuous input variables, with traffic examples and suitable distributions. → [[systems-simulation/28-input-analysis-2|28 — Input Analysis 2]]
- **(c)** Give three factors that influence the choice of an input distribution. → [[systems-simulation/28-input-analysis-2|28 — Input Analysis 2]]

### Question 4: data challenges in a hospital model

- **(a)** Explain the challenges of insufficient data and of nonstationary data. → [[systems-simulation/29-input-analysis-3|29 — Input Analysis 3]]
- **(b)** Explain how correlated data affects the model if it is ignored. → [[systems-simulation/29-input-analysis-3|29 — Input Analysis 3]]
- **(c)** Describe techniques for handling correlated data and mixture distributions. → [[systems-simulation/29-input-analysis-3|29 — Input Analysis 3]]

### Question 5: developing a smart microgrid model

- **(a)** Define input parameters, performance measures, system variables and simulation assumptions, with examples from the microgrid. → [[systems-simulation/06-types-and-components-of-simulation-models|06 — Types and Components of Simulation Models]] and [[systems-simulation/26-model-building-2|26 — Model Building 2]]
- **(b)** Describe five steps in developing the model, one sentence each about the microgrid. → [[systems-simulation/25-model-building-1|25 — Model Building 1]]
- **(c)** Explain two techniques for representing the model, and when each is used. → [[systems-simulation/25-model-building-1|25 — Model Building 1]] (ways to write the model down)

### Question 6: a bank queue in Arena

Inter-arrival times are exponential with mean 5 minutes, service times are normal with mean 4 and standard deviation 1 minute, one teller, first come first served.

- **(a)** Describe the Arena modules and the flow of the model. → [[systems-simulation/35-arena-1|35 — Arena 1]] and [[systems-simulation/37-arena-3|37 — Arena 3]]
- **(b)** Explain how you would set up the run: replication length, number of replications and time units. → [[systems-simulation/37-arena-3|37 — Arena 3]]
- **(c)** Name three output measures and explain the decision each supports. → [[systems-simulation/37-arena-3|37 — Arena 3]]

---

## SSG 517, 2024/25 paper: data collection

- **(a)** For a hospital simulation, what data would you collect, and from what sources? → [[systems-simulation/30-collecting-and-preparing-data|30 — Collecting and Preparing Data]]
- **(b)** What challenges arise in collecting it, and what methods make it accurate and representative? → [[systems-simulation/30-collecting-and-preparing-data|30 — Collecting and Preparing Data]]
- **(c)** For a kiosk queue, compare three methods of collecting data, with a strength and a weakness of each. → [[systems-simulation/30-collecting-and-preparing-data|30 — Collecting and Preparing Data]]
- **(d)** What are the implications of missing or inconsistent data, and how would you handle them? → [[systems-simulation/30-collecting-and-preparing-data|30 — Collecting and Preparing Data]]
- **(e)** Describe a framework for preprocessing the data. → [[systems-simulation/30-collecting-and-preparing-data|30 — Collecting and Preparing Data]]

---

## SSG 418 practice questions

### Q1 (repeated as Q8): a car assembly line

Welding, painting and inspection stations, with rework of failed cars.

- **(a)** Why is simulation suitable for this system? → [[systems-simulation/02-when-to-simulate|02 — When to Simulate]]
- **(b)** List the steps of the simulation study. → [[systems-simulation/07-the-simulation-study-1|07 — The Simulation Study 1]]
- **(c)** Give two performance measures. → [[systems-simulation/12-measuring-a-queue-1|12 — Measuring a Queue 1]]

### Q2: a bank branch with long queues

- **(a)** Describe the arrival process and the service process. → [[systems-simulation/28-input-analysis-2|28 — Input Analysis 2]]
- **(b)** What is queue discipline? Give two examples and say how you would implement one in a model. → [[systems-simulation/11-queueing-systems-2|11 — Queueing Systems 2]]
- **(c)** Give two key performance indicators. → [[systems-simulation/14-littles-law-and-the-mm1-queue|14 — Little's Law and the M/M/1 Queue]]
- **(d)** Suggest two strategies to test with the model. → [[systems-simulation/15-the-mmc-queue|15 — The M/M/c Queue]]
- **(e)** Why might a simulation's output differ from the queueing formula's answer? → [[systems-simulation/34-output-analysis|34 — Output Analysis]]

### Q3: a traffic intersection with lights

- **(a)** Identify the entities, attributes and state variables. → [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]]
- **(b)** How would you add random events such as accidents to the model? → [[systems-simulation/21-generating-random-variates|21 — Generating Random Variates]]
- **(c)** Give two performance measures. → [[systems-simulation/12-measuring-a-queue-1|12 — Measuring a Queue 1]]
- **(d)** How would the model help the city choose light timings? → [[systems-simulation/34-output-analysis|34 — Output Analysis]]

### Q4: delivery times under uncertain weather

- **(a)** What is Monte Carlo simulation? → [[systems-simulation/22-monte-carlo-simulation|22 — Monte Carlo Simulation]]
- **(b)** Name the random variables. → [[systems-simulation/22-monte-carlo-simulation|22 — Monte Carlo Simulation]]
- **(c)** How does the output help the company's customers? → [[systems-simulation/22-monte-carlo-simulation|22 — Monte Carlo Simulation]]

### Q5: hospital ICU beds

- **(a)** Name the entities and their attributes. → [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]]
- **(b)** How would you model patient arrivals, including a rate that changes during the day? → [[systems-simulation/29-input-analysis-3|29 — Input Analysis 3]]
- **(c)** Name two critical events. → [[systems-simulation/09-discrete-event-simulation|09 — Discrete-Event Simulation]]
- **(d)** Give two performance measures. → [[systems-simulation/12-measuring-a-queue-1|12 — Measuring a Queue 1]]

### Q6: core concepts

- **(a)** What is an entity? → [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]]
- **(b)** Give three attributes of an airport passenger. → [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]]
- **(c)** Distinguish an attribute from a state variable. → [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]]
- **(d)** Why are real experiments often not possible? → [[systems-simulation/02-when-to-simulate|02 — When to Simulate]]
- **(e)** Name two critical events in emergency response. → [[systems-simulation/09-discrete-event-simulation|09 — Discrete-Event Simulation]]
- **(f)** What are GPSS blocks? → [[systems-simulation/23-gpss-1|23 — GPSS/H 1]]

### Q7: theory and practice

- **(a)** Distinguish discrete-event from continuous simulation. → [[systems-simulation/06-types-and-components-of-simulation-models|06 — Types and Components of Simulation Models]]
- **(b)** What role do random numbers play in simulation? → [[systems-simulation/16-random-numbers-1|16 — Random Numbers 1]]
- **(c)** Distinguish verification from validation. → [[systems-simulation/31-verification-and-validation-1|31 — Verification and Validation 1]]
- **(d)** What does simulation software provide? → [[systems-simulation/08-the-simulation-study-2|08 — The Simulation Study 2]]

---

## Likely questions beyond these papers

The author's notes flag these as likely in other years:

1. Generate random numbers with a given a, c, m and seed, then test them with Kolmogorov-Smirnov or chi-square. → [[systems-simulation/17-random-numbers-2|17 — Random Numbers 2]], [[systems-simulation/19-testing-random-numbers-1|19 — Testing Random Numbers 1]] and [[systems-simulation/20-testing-random-numbers-2|20 — Testing Random Numbers 2]]
2. Hand-simulate a queue from a table of arrivals and service times, and compute the delay, utilisation and time in system. → [[systems-simulation/13-measuring-a-queue-2|13 — Measuring a Queue 2]]
3. Explain Type I, II and III errors with an example. → [[systems-simulation/33-verification-and-validation-3|33 — Verification and Validation 3]]
4. Describe the Arena model for a given queue, including a DECIDE module and output statistics. → [[systems-simulation/38-arena-4|38 — Arena 4]]
5. Compare simulation output with the M/M/1 formulas as a validation exercise. → [[systems-simulation/14-littles-law-and-the-mm1-queue|14 — Little's Law and the M/M/1 Queue]]
6. Write a GPSS/H model for a single-server queue and read its report. → [[systems-simulation/24-gpss-2|24 — GPSS/H 2]]

## Related

- [[systems-simulation/index|Systems simulation map]]
