# SSG 513 Question Bank

Every question from the SSG 513 (Techniques of Planning and Scheduling) papers the author collected, in one place. The questions are left unsolved on purpose, and each one points to the lesson that teaches it. For calculation questions, the final figures sit in a hidden "Check" block so you can mark your attempt without seeing the working.

**How to use this:** attempt each question closed-book, on paper, as if in the exam. Then open the Check block, and if you're off, go to the linked lesson. The value is in the attempt.

**Paper format:** every paper says **answer Question 1 and any two others**. Question 1 is worth 40 marks, the others 30.

**The most repeated items, so learn these cold:** the PERT A to J table (three papers), the A to D crash table (three papers), the four dependencies (four papers), the three-point estimate with a diagram (three papers), the resource short notes (three papers), the five characteristics (three papers), and the level-of-activity diagram (three papers).

---

## 2019/20 paper

### Question 1 (40 marks): resource-constrained scheduling

- **(a)** Explain the significance of resource-constraining in project scheduling. (4) → [[planning-and-scheduling/26-resources-2|26 — Resources 2]]
- **(b)** Define ACTRES, ROT, scaled SAF, RAF and CAF. (10) → [[planning-and-scheduling/28-priority-rules-1|28 — Priority Rules 1]] and [[planning-and-scheduling/29-priority-rules-2|29 — Priority Rules 2]]
- **(c)** Eight development tasks (A to H, with PERT times and Type 1 and Type 2 staff needs; available 8 and 10; w = 0.6). Compute RAF, SAF, scaled CAF, and schedule with Brooks' algorithm. (26) → [[planning-and-scheduling/29-priority-rules-2|29]] and [[planning-and-scheduling/31-brooks-algorithm-2|31]]

  <details><summary>Check</summary>

  Priority order D and H (100), E, C, B, G, F, A. Brooks' schedule ends at 30.83 weeks, against 13.33 unconstrained.

  </details>

### Question 2 (30 marks)

- **(a)** Short notes: resource allocation, resource loading, resource scheduling. → [[planning-and-scheduling/25-resources-1|25 — Resources 1]]
- **(b)** Explain the four types of dependency. → [[planning-and-scheduling/10-types-of-dependency|10 — Types of Dependency]]
- **(c)** Crash table: A (3 days, crash 1, N4,000 to N14,000), B after A (7 to 3, N1,000 to N11,000), C after A (4 to 2, N4,000 to N18,000), D after C (5 to 2, N2,000 to N13,000). Fixed cost N4,500 per day. Draw the network, find the normal duration, the cost slopes and the normal total cost. (14) → [[planning-and-scheduling/23-crashing-2|23 — Crashing 2]]

  <details><summary>Check</summary>

  Normal 12 days (A-C-D). Slopes A 5,000, B 2,500, C 7,000, D 3,667. Normal total N65,000. Crashing D twice gives the minimum, N63,333 at 10 days.

  </details>

### Question 3 (30 marks)

- **(a)** Explain the work breakdown structure. → [[planning-and-scheduling/06-work-breakdown-structure|06 — The Work Breakdown Structure]]
- **(b)** Laralek project (AON). Draw the network and find ES, EF, LS, LF, the critical path and the duration. Activities (days): A 0; B 10, C 5 and F 2 after A; D 14 and E 10 after F; G 12 after D and E; H 1 after G; I 1 after B; J 5 after C; K 0.5 after I and J; L 2 after B; M 1 after I and L; N 0.5 after H, K and M; O 0.5 after N. → [[planning-and-scheduling/14-critical-path-method-2|14]] and [[planning-and-scheduling/16-critical-path-method-4|16]]

  <details><summary>Check</summary>

  30 days, critical path A-F-D-G-H-N-O. Floats: B 16, C 18.5, E 4, I 17, J 18.5, K 17.5, L 16, M 16.

  </details>

### Question 4 (30 marks)

- **(a)** Outline the ten knowledge areas. (10) → [[planning-and-scheduling/05-pmbok-2|05 — PMBOK 2]]
- **(b)** Explain five characteristics of a project. → [[planning-and-scheduling/01-what-a-project-is|01 — What a Project Is]]
- **(c)** Workload of a team (names and hours given on the paper; note the clash in its wording). → [[planning-and-scheduling/25-resources-1|25 — Resources 1]]
- **(d)** With a diagram, explain the level of activity of the five process groups. → [[planning-and-scheduling/04-pmbok-1|04 — PMBOK 1]]

### Question 5 (30 marks)

- **(a)** Explain the three-point estimate, with a diagram. → [[planning-and-scheduling/17-pert-1|17 — PERT 1]]
- **(b)** PERT network A to J (a, m, b: A 1,2,3; B 1,1,1 after A; C 2,6,10 after A; D 1,4,7 after A; E 2,2,2 after B; F 4,5,6 after C; G 1,3,5 after D; H 2,8,14 after C and G; I 4,6,8 after E; J 3,3,3 after F, I and H). Find the expected time, the critical path, and the probability of finishing in 21 days, in 20% more than expected and in 50% more than expected. → [[planning-and-scheduling/18-pert-2|18 — PERT 2]]

  <details><summary>Check</summary>

  $T_e = 20$ days on A-D-G-H-J; $V_p = 5.556$, $\sigma = 2.357$. $P(21) \approx 0.66$; $P(24) \approx 0.955$; $P(30) \approx 1$.

  </details>

---

## 2020/21 marking scheme

The question paper itself isn't in the author's files, only the marking scheme, so the wording here is rebuilt from it.

### Question 1: CPM and crashing

A network START-P-Q-...-Y-END, crashed to meet a deadline. → [[planning-and-scheduling/23-crashing-2|23 — Crashing 2]]

<details><summary>Check</summary>

Critical path START-P-Q-S-T-W-X-Y-END, 6.4 time units. Crash X by 0.5, P by 0.1, W by 0.1 and T by 0.1, in order of lowest crash ratio, for an extra $17.5 thousand.

</details>

### Question 2: PERT, power plant

Expected times A 15.33, B 9.67, C 11.83, D 10.17, E 29.50, F 12.17, G 37.33, H 48.33, I 12.50, J 6.17, K 6.17 (network on the paper). Find the critical path, its variance, and the probability of finishing in 77 weeks, in 82 weeks, and between the two. → [[planning-and-scheduling/18-pert-2|18 — PERT 2]]

<details><summary>Check</summary>

B-D-H-J-K, $T_e = 80.5$ weeks; variance $1.00 + 6.25 + 2.78 + 0.25 + 0.25 = 10.53$, $\sigma = 3.25$. P(77) = 0.140, P(82) = 0.678, between = 0.538. (The marking scheme's 15.03 and its probabilities are wrong.)

</details>

### Question 3: precedence relationships

A 3; B 1 after A; C 2 after A; D 4 after B; E 1 after C; F 1 after C; G 4 after D and E; H 3 after G and F. Find the duration with plain logic, then with FS(A,B) = 2, SS(A,C) = 4, SS(B,D) = 2, SF(C,E) = 3, FF(C,F) = 5, SS(D,G) = 1, SF(F,H) = 8. → [[planning-and-scheduling/12-precedence-relationships-2|12 — Precedence Relationships 2]]

<details><summary>Check</summary>

15 days plain (A-B-D-G-H); 18 days with the relationships, new critical path A-C-F-H.

</details>

### Question 4: resource-constrained scheduling

Activities P to W, w = 0.4, available Type 1 = 10, Type 2 = 12 (data on the paper). Compute scaled CAF and schedule with Brooks' algorithm. → [[planning-and-scheduling/29-priority-rules-2|29]] and [[planning-and-scheduling/31-brooks-algorithm-2|31]]

<details><summary>Check</summary>

Expected times P 3.67, Q 3.00, R 9.83, S 6.17, T 2.00, U 15.83, V 2.00, W 7.67; 21.17 weeks unconstrained. Scaled CAF: P 89.89, Q 68.09, R 63.46, S 33.07, T 63.61, U 67.53, V 100.00, W 52.77, so the order is V, P, Q, U, T, R, W, S. The scheme's table ends at 31.34 weeks; with the question's own figures it is 29.33 (the scheme gives S a Type 1 need of 7, the question 0).

</details>

---

## 2023/24 paper

### Question 1 (40 marks)

- **(a)** Explain the significance of resource-constraining. (4) → [[planning-and-scheduling/26-resources-2|26 — Resources 2]]
- **(b)** Software project crashing: A 5 (crash 4, 100 to 200); B after A 3 (2, 300 to 350); C after A 2 (1, 200 to 325); D after B and C 2 (1, 250 to 300); E after C 1 (1, 400); F after D 4 (2, 500 to 900); G after E 4 (2, 150 to 350). Costs in N'000, fixed cost N100,000. Find the normal direct cost, normal duration, full-crash duration and cost, and the minimum-cost duration. → [[planning-and-scheduling/24-crashing-3|24 — Crashing 3]]

  <details><summary>Check</summary>

  Normal: N1,900k direct, 14 days (A-B-D-F), total N3,300k. Full crash: 9 days. Minimum total N3,200k at 12 days (or 11), reading the fixed cost as per day.

  </details>

### Question 2 (30 marks)

- **(a)** Resource short notes. → [[planning-and-scheduling/25-resources-1|25]]
- **(b)** The four types of dependency. → [[planning-and-scheduling/10-types-of-dependency|10]]
- **(c)** The A to D crash table (A 4/2, B 8/5, C 5/4, D 5/3; costs as in lesson 23; fixed N3,500 per day). → [[planning-and-scheduling/23-crashing-2|23 — Crashing 2]]

  <details><summary>Check</summary>

  Normal 14 days (A-C-D), slopes A 5,000, B 3,333, C 14,000, D 5,500, normal total N60,000. No critical slope is below N3,500, so crashing never lowers the total.

  </details>

### Question 3 (30 marks)

- **(a)** Explain rolling wave planning. (4) → [[planning-and-scheduling/07-rolling-wave-planning-and-reserves|07]]
- **(b)** Distinguish management reserve from contingency reserve. (3) → [[planning-and-scheduling/07-rolling-wave-planning-and-reserves|07]]
- **(c)** Craneburg AOA network: 1-2 = 0, 1-3 = 11, 1-4 = 6, 2-4 = 5, 3-5 = 7, 3-6 = 5, 4-6 = 9, 4-7 = 10, 4-8 = 12, 5-6 = 2, 6-8 = 8, 6-9 = 12, 7-8 = 4, 8-9 = 8. Find ES, EF, LS, LF, float and the critical path. → [[planning-and-scheduling/15-critical-path-method-3|15 — Critical Path Method 3]]

  <details><summary>Check</summary>

  36 days, critical path 1-3-5-6-8-9.

  </details>

### Question 4 (30 marks)

- **(a)** Level of activity of the five process groups, with a diagram. → [[planning-and-scheduling/04-pmbok-1|04]]
- **(b)** Five characteristics of a project. → [[planning-and-scheduling/01-what-a-project-is|01]]
- **(c)** Large construction AOA network, events 1 to 23 (data on the paper). Treat the durations shown as "-" (11-22, 16-19, 18-19) as dummies. → [[planning-and-scheduling/09-network-diagrams-2|09]] and [[planning-and-scheduling/15-critical-path-method-3|15]]

  <details><summary>Check</summary>

  66 days, critical path 1-2-15-16-17-22-23. Next longest: 1-2-15-18-21-22-23 (56) and 1-2-12-14-22-23 (45). Event 22 is the big merge, where eight arrows meet.

  </details>

### Question 5 (30 marks)

- **(a)** Explain the three-point estimate, with a diagram. → [[planning-and-scheduling/17-pert-1|17]]
- **(b)** Cost PERT: A 80, 100, 150; B 40, 50, 75; C 200, 200, 200; D 50, 60, 60; E 30, 40, 60 (naira). Find the mean and variance of the total cost, and the probability it lies between N450 and N500. → [[planning-and-scheduling/20-pert-4|20 — PERT 4]]

  <details><summary>Check</summary>

  Mean N457.50, variance 197.92, σ = 14.07; P(450 to 500) ≈ 0.70.

  </details>

- **(c)** The PERT A to J network. → [[planning-and-scheduling/18-pert-2|18]] (Check as in 2019/20 Question 5b.)

---

## 2024/25 paper

### Question 1 (40 marks)

- **(a)** Explain the triple constraint. → [[planning-and-scheduling/03-the-triple-constraint|03]]
- **(b)** Compare CPM and PERT. (4) → [[planning-and-scheduling/21-cpm-and-pert-compared|21]]
- **(c)** Dangote refinery maintenance AOA network, in hours: A 1-2 24; B 2-3 16; C 2-6 16; D 2-8 40; E 2-9 24; F 3-4 16; G 3-5 8; H 4-5 dummy; I 5-7 6; J 6-7 dummy; K 6-14 12; L 7-14 36; M 8-14 8; N 9-10 16; O 9-13 4; P 10-11 16; Q 10-12 24; R 11-12 dummy; S 12-13 8; T 13-14 16; U 14-15 8. Find the critical path, duration and every activity's times and float. → [[planning-and-scheduling/15-critical-path-method-3|15]]

  <details><summary>Check</summary>

  120 hours, critical path A-E-N-Q-S-T-U. Next longest: A-E-N-P-R-S-T-U at 112. Floats: B, F, H, I, L 14; C, J 36; D, M 40; G 22; K 60; O 44; P, R 8.

  </details>

- **(d)** Project scoring model, Score = (P(success) + 2 × Payoff) / Cost, for twelve projects (data on the paper). Choose the best three as the project manager. → [[planning-and-scheduling/32-project-scoring-models|32]]

  <details><summary>Check</summary>

  Projects 4 (4.96), 6 (4.22) and 3 (4.13); project 5 (4.10) is a very close fourth.

  </details>

### Question 2 (30 marks)

- **(a)** Characteristics of a project. → [[planning-and-scheduling/01-what-a-project-is|01]]
- **(b)** The five process groups. → [[planning-and-scheduling/04-pmbok-1|04]]
- **(c)** The types of dependency. → [[planning-and-scheduling/10-types-of-dependency|10]]
- **(d)** PERT with a = t² − t, m = t, b = t² + t: find the expected time, standard deviation and the probability of finishing by t² + 2t. → [[planning-and-scheduling/20-pert-4|20]]

  <details><summary>Check</summary>

  $T_e = (t^2 + 2t)/3$, $\sigma = t/3$, probability $\Phi(2(t + 2))$.

  </details>

### Question 3 (30 marks)

- **(a)** Short notes on network terms (activity, event, critical path, WBS). → [[planning-and-scheduling/08-network-diagrams-1|08]], [[planning-and-scheduling/14-critical-path-method-2|14]] and [[planning-and-scheduling/06-work-breakdown-structure|06]]
- **(b)** E-library PERT project, eleven activities A to K (estimates on the paper, columns labelled a, b, C). Find the critical path and the probability that all paths finish by $T_e + 2$. → [[planning-and-scheduling/19-pert-3|19 — PERT 3]]

  <details><summary>Check</summary>

  B-E-G-H-J-K, $T_e = 23$ days, $V_p = 4.0$. All four paths by 25 days: $0.9857 \times 0.8875 \times 0.8413 \times 0.9727 \approx 0.716$.

  </details>

### Question 4 (30 marks)

- **(a)** Explain the three-point estimate. → [[planning-and-scheduling/17-pert-1|17]]
- **(b)** Software development network: A 3, B 5, C 7 (no predecessors); D 8 after A; E 5 after B; F 5 after C; G 4 after E; H 5 after F; I 6 after D; J 4 after G and H (weeks). → [[planning-and-scheduling/16-critical-path-method-4|16]]

  <details><summary>Check</summary>

  21 weeks, critical path C-F-H-J.

  </details>

### Question 5 (30 marks)

- **(a)** Resource short notes. → [[planning-and-scheduling/25-resources-1|25]]
- **(b)** Workload: Josiah 6 days at 8 hours; Oluwatobi and Ginika 2 hours a day less, for 4 and 5 days; Jesuseun half Josiah's hours, for 3 days. → [[planning-and-scheduling/25-resources-1|25]]

  <details><summary>Check</summary>

  114 hours (24 + 12 + 30 + 48).

  </details>

- **(c)** The A to D crash table (as 2023/24 Question 2c). → [[planning-and-scheduling/23-crashing-2|23]]

---

## Class exercises and assignments

- **Class Exercise 2 (fence and gate):** → [[planning-and-scheduling/14-critical-path-method-2|14]]. <details><summary>Check</summary>12 days, A-B-D-F-G-H.</details>
- **Class Exercise 3:** <details><summary>Check</summary>18 days, A-C-E-G-H.</details>
- **Class Exercise 4:** <details><summary>Check</summary>20 days, B-C-D-E-G-I.</details>
- **Assignment 1 Q1 (arrow diagram, events 0 to 6):** → [[planning-and-scheduling/09-network-diagrams-2|09]]. <details><summary>Check</summary>19 days; 0-1-4-6 and 0-1-2-4-6 are both critical, through the dummy 1-2.</details>
- **Assignment 1 Q2:** the Laralek network (2019/20 Question 3b).
- **Assignment 2 (computer installation, columns a, b, m):** → [[planning-and-scheduling/17-pert-1|17]] and [[planning-and-scheduling/18-pert-2|18]]. <details><summary>Check</summary>Expected times A 5.17, B 8.00, C 4.00, D 2.00, E 2.33, F 4.33, G 2.00, H 4.17. Critical path B-D-F-H, $T_e = 18.5$ weeks, $V_p = 1.25$, $P(20 \text{ weeks}) \approx 0.91$.</details>

---

## About this question bank

Rebuilt from the author's SSG 513 study notes, section 9, which collect the four papers, the 2020/21 marking scheme, the class exercises and both assignments. Every figure in the Check blocks was recomputed in code, not copied from a marking scheme; where a scheme disagrees, the bank says so.
