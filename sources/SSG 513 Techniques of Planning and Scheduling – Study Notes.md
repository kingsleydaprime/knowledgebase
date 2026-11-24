# SSG 513 Techniques of Planning and Scheduling – Study Notes

Nov 24, 2026 · @Kingsley Ihemelandu Chukwudi

The whole course is one chain: define the project, break it into activities (WBS), draw the network, find the critical path, add uncertainty (PERT), buy time with money (crashing), then fit the plan to the resources you really have. Each section below builds on the one before it, and section 9 solves the past questions using the earlier sections.

## 1. Projects and project management

A project is a temporary effort to create something unique. PMBOK 7th edition defines it as a temporary endeavour undertaken to create a unique product, service or result. Other bodies say the same thing in their own words:

| Source | Their angle |
| --- | --- |
| PMBOK (PMI) | Temporary, creates a unique product, service or result |
| IPMA | Time and cost constrained, delivers a set of defined deliverables to quality standards |
| ISO | A unique set of coordinated, controlled activities with start and end dates |
| APM | Unique, transient endeavour to achieve planned objectives (outputs, outcomes or benefits) |
| PRINCE2 | A temporary organisation created to deliver business products to an agreed Business Case |

Operations are the opposite: they carry on and repeat. A project ends when its deliverables are handed over.

### Characteristics of a project

Exams ask for any five (2023, 2024, 2019 papers). Learn all nine so you can pick:

1. **Objectives**: it has a mission to achieve.
2. **Lifecycle**: it moves through phases from start to close.
3. **Definite time frame**: it has a start and a finish.
4. **Uniqueness**: no two projects are the same.
5. **Teamwork**: success needs coordination between team members.
6. **Complexity**: it is made of many linked activities.
7. **Risk and uncertainty**: the future is not fully known.
8. **Change**: scope, plans and conditions shift as it runs.
9. **Response to environment**: it reacts to its surroundings.

### What surrounds a project

The environment can help, hurt or do nothing. Slides split it in two:

- **Internal** (inside the organisation): process assets (tools, templates, methods), governance documents, knowledge assets, security and safety, culture and structure, where people and facilities are located, infrastructure, scheduling software, resource availability, and the skills of employees.
- **External** (outside it): market conditions, social and cultural issues, regulations, commercial databases, academic research, industry standards, financial factors (exchange rates, interest, inflation, taxes) and the physical environment (weather, working conditions).

### Words that are easy to mix up

- **Product**: something produced that you can count, either an end item or a component.
- **Outcome**: the end result and the benefit it delivers; wider than an output.
- **Project**: one unique effort. **Program**: related projects managed together to get benefits you would not get one by one. **Portfolio**: projects, programs and operations managed as a group for strategic goals.
- **Project management**: applying knowledge, skills, tools and techniques to meet project requirements.
- **Project manager**: the person the performing organisation assigns to lead the team and hit the objectives.

The tools and techniques you meet in this course sit inside that definition. Tools: WBS, Gantt chart, MS Project, Primavera. Techniques: decomposition, AON, estimating, rolling wave planning, earned value, resource levelling.

### The triple constraint

Scope, time and cost are the three biggest limits on any project, and they are linked. Change one and at least one of the others must move. If scope grows, the project probably takes longer or costs more. If the deadline moves earlier, you must either pay more or do less. This idea returns in section 6, where we spend money to save time.

### PMBOK in one view

- **Editions**: 1996, 2000, 2004 (3rd), 2008 (4th), 2013 (5th), 2017 (6th), 2021 (7th).
- **Up to the 6th edition**: 5 process groups, 47 processes and 10 knowledge areas.
- **7th edition**: 8 performance domains instead: Stakeholder, Team, Development Approach and Life Cycle, Planning, Project Work, Delivery, Measurement, Uncertainty.

**Five process groups**: Initiating, Planning, Executing, Monitoring and Controlling, Closing.

**Ten knowledge areas** (asked as "outline" for 10 marks in 2019/20). One line each, written from general project-management knowledge because your slides only list the names, so check against Assignment 1:

| Knowledge area | What it manages |
| --- | --- |
| Integration | Holding all the other areas together; change control; the project plan |
| Scope | Exactly what is and is not in the project (WBS lives here) |
| Time (Schedule) | Activity sequencing, duration estimates, the schedule (this course) |
| Cost | Estimating, budgeting and controlling money |
| Quality | Meeting standards and requirements |
| Human Resources | Getting and developing the team |
| Communications | Who gets what information and when |
| Risk | Identifying, analysing and responding to uncertainty |
| Procurement | Buying goods and services from outside |
| Stakeholder | Identifying and engaging the people affected |

**Level of activity across the five process groups** (asked 2019/20, 2023/24, 2024/25; 7 to 9 marks with a diagram). In words, left to right across the project life: Initiating is a short burst at the start. Planning rises fast just after and is heavy early. Executing builds up and is the largest block in the middle. Monitoring and Controlling runs alongside from planning until the end and rises and falls with executing. Closing is a short burst at the end. Draw time on the horizontal axis, level of activity on the vertical, and one hump per group.

### Methodologies and certifications

Methodologies: PMBOK-based predictive (waterfall), Agile (Scrum and Kanban), hybrid, and Lean Six Sigma. Certifications named in class: PMP and CAPM (PMI), PRINCE2 Foundation and Practitioner (PeopleCert/Axelos), CSM (Scrum Alliance), PSM I (Scrum.org), CompTIA Project+, Google Project Management Certificate, and IPMA Level D. Exam fees on the slide change, so check them before quoting.

## 2. Work Breakdown Structure (WBS)

You cannot schedule what you have not listed. The WBS is how you list it. A major cause of project failure is wrong estimates of time and cost, and the WBS is the best tool to fix that. The idea is simple: keep splitting a big, complicated task into smaller tasks until you reach a level that cannot be split any further. Those lowest-level pieces are the activities that go into the network in section 3.

- **WBS dictionary**: if the names in the WBS are vague, the dictionary explains each element. It describes milestones, deliverables, activities and scope, and sometimes dates, resources, cost and quality. PMI calls it a document giving detailed deliverable, activity and scheduling information about each WBS component.
- **Why it matters for scheduling**: every activity you later draw, estimate and crash starts life as a WBS box. Estimating at the lowest level is what makes durations and costs believable.

### Rolling wave planning (asked 2023/24, 4 marks)

Plan the near future in detail and the far future roughly, then add detail as you get closer. Work that is a few weeks away is broken down into full activities; work months away stays at a high-level work package until more is known. The plan "rolls" forward as the project moves. It is a form of progressive planning, and it suits projects where the later stages cannot yet be defined. (Written from general project-management knowledge; your slides only name the technique.)

### Management reserve vs contingency reserve (asked 2023/24, 3 marks)

Both are extra money or time set aside for surprises, but they differ in what surprise they cover and who controls them. From general project-management knowledge, since the slides do not define them:

|  | Contingency reserve | Management reserve |
| --- | --- | --- |
| Covers | Risks you have identified ("known unknowns") | Work or events nobody foresaw ("unknown unknowns") |
| Part of the baseline? | Yes, inside the cost and schedule baseline | No, held outside the baseline |
| Who releases it | The project manager | Senior management approval, then added to the baseline |

## 3. Network diagrams

A network diagram draws the activities from the WBS in a logical order and shows how they depend on each other. Some terms you need first:

- **Activity**: a piece of work that takes time.
- **Event**: a specific instant that marks the start or end of an activity (it takes no time).
- **Path**: a sequence of activities from start to finish.
- **Critical path**: the longest path. Its length is the project duration.

There are two ways to draw the same thing.

|  | Activity on Arrow (AOA) | Activity on Node (AON), also PDM |
| --- | --- | --- |
| Activity is drawn as | An arrow | A box (node) |
| Events or links | Circles are events; the number pair on the arrow is (start event - end event), e.g. 2-5 | Arrows only show dependencies |
| Dummy activity | Often needed: a dashed arrow of zero duration to keep the logic right or give each activity a unique event pair | Never needed |
| Relationships | Finish-to-start only | All four types (below) |

AON is also called the Precedence Diagramming Method (PDM). Both methods give the same critical path when the logic is the same. Exams use both: AOA in 2023 and 2024, AON in 2019/20.

### Types of dependency

These describe *why* one activity must wait for another. All four are decided by the project team during activity sequencing.

| Type | Also called | Meaning | Example |
| --- | --- | --- | --- |
| Mandatory | Hard logic | Required by contract or by the nature of the work, often physical | You cannot build the ceiling before the walls |
| Discretionary | Preferred or soft logic | The team's chosen order; document it, because it limits later options | Choosing to paint rooms in a set order |
| External |  | Link between a project activity and something outside the team's control | Waiting for a delivery or a government permit |
| Internal |  | Precedence between two activities inside the project | Test the software after coding it |

### The four precedence relationships (PDM)

Asked in 2019/20, 2020/21, 2023/24 and 2024/25. Call the first activity A and the one that follows it B.

| Relationship | Rule | Remember it as |
| --- | --- | --- |
| Finish to Start (FS) | B cannot start until A finishes. The most common; this is what plain CPM assumes. | A ends, then B begins |
| Start to Start (SS) | B cannot start until A has started | They begin together or with a gap |
| Finish to Finish (FF) | B cannot finish until A finishes | They end together or with a gap |
| Start to Finish (SF) | B cannot finish until A has started. The rarest. | A starting releases B's finish |

A **lag** is a delay added to a relationship ("start 2 days after"). A **lead** is an overlap ("start 2 days before"). In ordinary CPM every relationship is FS with zero lag. Using lead and lag is more realistic because real work has compulsory gaps and overlaps, such as waiting for concrete to cure.

### Worked example: precedence relationships change the answer

From the 2020/21 paper. Activities and durations (days): A3, B1 (after A), C2 (after A), D4 (after B), E1 (after C), F1 (after C), G4 (after D, E), H3 (after G, F).

**Step 1, plain FS logic.** The longest path is A-B-D-G-H = 3+1+4+4+3 = **15 days**.

**Step 2, add the given relationships.** FS(A,B)=2, SS(A,C)=4, SS(B,D)=2, SF(C,E)=3, FF(C,F)=5, SS(D,G)=1, SF(F,H)=8. Forward pass:

| Activity | Rule that fixes it | Start | Finish |
| --- | --- | --- | --- |
| A | start of project | 0 | 3 |
| B | FS 2 after A finishes (3 + 2) | 5 | 6 |
| C | SS 4 after A starts | 4 | 6 |
| D | SS 2 after B starts (5 + 2) | 7 | 11 |
| E | SF 3: E cannot finish before C starts + 3 = 7 | 6 | 7 |
| F | FF 5: F cannot finish before C finishes + 5 = 11 | 10 | 11 |
| G | SS 1 after D starts (7 + 1 = 8) | 8 | 12 |
| H | SF 8: H cannot finish before F starts + 8 = 18 | 15 | 18 |

New duration **18 days**. The new critical path is **A-C-F-H**, driven by SS from A to C, FF from C to F and SF from F to H. The 3-day increase is the net effect of all the relationships together: some shorten the project, others stretch it.

## 4. Critical Path Method (CPM)

CPM answers: how long does the project take, and which activities can slip without hurting it? It uses one fixed duration per activity (deterministic). It was developed by Du Pont in 1957 for plant construction and shutdown work, and it also includes a method for trading time against cost (section 6).

### The four times and the float

- **ES** (earliest start): the soonest an activity can begin. ES = the largest EF of its predecessors (0 if none).
- **EF** (earliest finish): EF = ES + duration.
- **LF** (latest finish): the latest it can finish without delaying the project. LF = the smallest LS of its successors (the project duration if it is last).
- **LS** (latest start): LS = LF - duration.
- **Float (slack)** = LS - ES, which is the same as LF - EF.

The forward pass (left to right) gives ES and EF. The backward pass (right to left) gives LF and LS.

```latex
ES = \max(EF_{\text{predecessors}}),\quad EF = ES + t,\quad LF = \min(LS_{\text{successors}}),\quad LS = LF - t
```

In an AOA diagram the same ideas apply to events. The earliest time of an event is the largest of (earliest time of the tail event + duration) over all arrows coming in. The latest time is the smallest of (latest time of the head event - duration) over all arrows going out.

### Critical path

Activities with zero float make the critical path, which is the longest path and gives the project duration. A delay on any critical activity delays the whole project, so these are the activities to watch. Non-critical activities have float you can use, for example to level resources (section 7). There can be more than one critical path.

Note: your marking scheme calls LS - ES "slack or free float". Strictly, LS - ES is *total float*. Free float is the delay an activity can take without pushing back its successor's earliest start. Use the lecturer's wording in the exam, but know the difference.

### Worked example (Class Exercise 2: fence and gate)

| Activity | Duration | After | ES | EF | LS | LF | Float |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A Dig holes | 3 | - | 0 | 3 | 0 | 3 | 0 |
| B Buy wood | 2 | A | 3 | 5 | 3 | 5 | 0 |
| C Buy gate | 1 | A | 3 | 4 | 6 | 7 | 3 |
| D Erect fence | 3 | B | 5 | 8 | 5 | 8 | 0 |
| E Buy paint | 1 | C | 4 | 5 | 7 | 8 | 3 |
| F Erect gate | 1 | D, E | 8 | 9 | 8 | 9 | 0 |
| G Paint fence | 2 | F | 9 | 11 | 9 | 11 | 0 |
| H Paint gate | 1 | G | 11 | 12 | 11 | 12 | 0 |

Critical path **A-B-D-F-G-H**, duration **12 days**. The other path A-C-E-F-G-H is only 9 days, so C and E each have 3 days of float.

### Answers to the other class exercises and assignment

| Exercise | Critical path | Duration |
| --- | --- | --- |
| Class Exercise 3 | A-C-E-G-H | 18 days |
| Class Exercise 4 | B-C-D-E-G-I | 20 days |
| Assignment 1 Q1 (arrow diagram, events 0 to 6) | 0-1-4-6 and 0-1-2-4-6 (the dummy 1-2 has zero duration, so both are critical) | 19 days |
| Assignment 1 Q2 / 2019/20 Q3 (AON, activities A to O) | A-F-D-G-H-N-O | 30 days (full table in section 9) |

Exercise 1 gives no durations, so it is only a drawing exercise.

## 5. PERT: when durations are uncertain

CPM gives one number per activity. Real durations are uncertain, so PERT (Program Evaluation and Review Technique) gives three, and then answers a question CPM cannot: *what is the chance we finish by a given date?* It was built by the US Navy in 1958 for the Polaris missile programme.

### The three-point estimate (asked every year, 5 to 8 marks, "include diagram")

For each activity, estimate:

- **Optimistic time (a)**: how long it takes if things go well.
- **Most likely time (m)**: the best single estimate.
- **Pessimistic time (b)**: how long it takes if things go badly.

PERT assumes the duration follows a **beta distribution**. For the diagram, draw a bell-shaped curve on a time axis with a on the far left, b on the far right and m under the peak. The curve is usually skewed because b is further from m than a is, so the mean sits slightly to the right of m.

```latex
t_e = \frac{a + 4m + b}{6},\qquad \sigma = \frac{b - a}{6},\qquad V = \sigma^2 = \left(\frac{b-a}{6}\right)^2
```

The mean is a weighted average: m gets weight 4, a and b get weight 1 each, and the total weight is 6. The range b - a is treated as six standard deviations. A bigger variance means the mean time is less reliable.

**Label warning.** Some papers write the three columns as a, m, b, others as o, m, p, and the 2024/25 e-library question labels them a, b, C. In every case the smallest value is optimistic, the middle one is most likely and the largest is pessimistic. Sort them by size if the headings confuse you.

### Steps for a PERT problem

1. Compute t\_e and variance for every activity.
2. Use the t\_e values as durations and run the CPM forward and backward pass. This gives the expected project time T\_e and the critical path.
3. Add the variances of the **critical-path activities only**: V\_p = sum of V. Standard deviation = square root of V\_p.
4. Convert a target time T to a Z score and read the probability from the normal table.

```latex
T_e = \sum t_e\ (\text{critical path}),\quad V_p = \sum V\ (\text{critical path}),\quad Z = \frac{T - T_e}{\sqrt{V_p}},\quad P(\text{finish by } T) = \Phi(Z)
```

Common normal table values to have ready: Z = 0.5 gives 0.6915, 1.0 gives 0.8413, 1.28 gives 0.8997, 1.64 gives 0.9495, 1.96 gives 0.9750. For a negative Z, use 1 minus the value for the positive Z.

### Worked example (the question that appears in 2019/20, 2023/24 and your slides)

| Activity | A | B | C | D | E | F | G | H | I | J |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Predecessors | - | A | A | A | B | C | D | C, G | E | F, I, H |
| a | 1 | 1 | 2 | 1 | 2 | 4 | 1 | 2 | 4 | 3 |
| m | 2 | 1 | 6 | 4 | 2 | 5 | 3 | 8 | 6 | 3 |
| b | 3 | 1 | 10 | 7 | 2 | 6 | 5 | 14 | 8 | 3 |
| t\_e | 2 | 1 | 6 | 4 | 2 | 5 | 3 | 8 | 6 | 3 |
| Variance | 0.111 | 0 | 1.778 | 1.0 | 0 | 0.111 | 0.444 | 4.0 | 0.444 | 0 |

Paths: A-B-E-I-J = 14, A-C-F-J = 16, A-C-H-J = 19, A-D-G-H-J = 20. The critical path is **A-D-G-H-J**, so T\_e = **20 days**.

V\_p = 0.111 + 1.0 + 0.444 + 4.0 + 0 = **5.556**, so the standard deviation is 2.357 days.

- **Finish in 21 days:** Z = (21 - 20) / 2.357 = 0.42, so P = **0.66** (about 66%).
- **20% later than expected:** 1.2 x 20 = 24 days. Z = (24 - 20) / 2.357 = 1.70, so P = **0.955** (about 95.5%).
- **50% later than expected:** 1.5 x 20 = 30 days. Z = 4.24, so P is **about 1** (practically certain).

### Other PERT questions you can be asked

**All paths finish in time.** A project is only done when every path is done. If the paths are treated as independent, work out the probability for each path separately (use that path's own mean and variance) and **multiply** them. A near-critical path with a large variance can matter as much as the critical one. The worked example for this is the 2024/25 e-library question in section 9.

**Time for a given confidence.** Reverse the formula: T = T\_e + Z x sigma. For 95% confidence use Z = 1.64.

**PERT on costs (2023/24).** The same three-point idea works for cost. Cost mean = (Co + 4Cm + Cp) / 6 and cost variance = ((Cp - Co) / 6) squared. Add the means for the total cost and add the variances for the total variance (all activities, since each one costs money). Worked in section 9.

**Three estimates as expressions of a parameter (2024/25 Q2d).** Say a = t^2 - t, m = t, b = t^2 + t. Then T\_e = (a + 4m + b) / 6 = (t^2 + 2t) / 3 and sigma = (b - a) / 6 = 2t / 6 = t / 3. For a target time T = t^2 + 2t: Z = (T - T\_e) / sigma = ((2/3)(t^2 + 2t)) / (t/3) = 2(t + 2), so the probability is Phi(2(t + 2)). The 2020/21 version gives variance t^2 / 9 and standard deviation t / 3.

### CPM and PERT side by side (asked 2024/25, 4 marks)

|  | CPM | PERT |
| --- | --- | --- |
| Duration estimate | One fixed time (deterministic) | Three times on a beta distribution (probabilistic) |
| Best for | Repetitive, well-known work such as construction | New or uncertain work such as research and development |
| Main question | How can I trade time and cost? | What is the chance of finishing by a date? |
| Origin | Du Pont, 1957 | US Navy, 1958 (Polaris) |
| Extra advantage | Time-cost crashing | Handles uncertainty and gives probabilities |

**Limits of both (from the SIMS slides):** every predecessor must finish before an activity starts, activities cannot repeat or loop back, the critical path is always the longest path, and there is only one end event. GERT is a rarely used extension that allows branching and probabilistic logic.

## 6. Time and cost trade-off: crashing

Sometimes the CPM duration is too long and the client wants the project sooner. You can shorten an activity by throwing more money at it (extra workers, overtime, better equipment). That is **crashing**. It is the link between the triple constraint's time and cost.

### Terms

- **Normal time (Tn) and normal cost (Cn)**: what the activity takes under ordinary working conditions.
- **Crash time (Tc) and crash cost (Cc)**: the shortest possible time and what it costs.
- **Cost slope** (crash cost per day): the extra cost of saving one day on that activity.
- **Direct cost**: the cost of doing the activities. It rises when you crash.
- **Indirect (fixed) cost**: overheads such as supervision and site costs. It is charged per day, so it falls when the project is shorter.

```latex
\text{Cost slope} = \frac{C_c - C_n}{T_n - T_c}
```

Because direct cost rises and indirect cost falls as you shorten the project, total cost forms a U shape. The cheapest duration is at the bottom of the U, and it is usually *not* the fastest possible one. Keep crashing only while the cost slope is less than the indirect saving per day.

### The crashing algorithm

1. Draw the network and find the normal critical path and duration.
2. Compute the cost slope of every activity that can still be crashed (an activity with Tn = Tc cannot).
3. Among the **critical** activities, pick the one with the **lowest** cost slope and crash it by one day (or as many days as is allowed before another path becomes critical).
4. Recompute all path lengths. If two or more paths are now critical, crash an activity on each of them (or one common activity if it lies on all).
5. Stop when crashing no longer pays (cost slope is more than the indirect saving) or when no critical activity can be crashed any more.
6. Total cost = direct cost + (indirect cost per day x duration). Compare it at each duration to find the minimum.

Only crash activities on the critical path. Crashing anything else spends money and shortens nothing.

### Worked example 1 (the table that appears in 2019/20, 2023/24 and 2024/25)

| Activity | After | Normal days | Crash days | Normal cost (N) | Crash cost (N) | Cost slope (N/day) |
| --- | --- | --- | --- | --- | --- | --- |
| A | - | 4 | 2 | 4,000 | 14,000 | 5,000 |
| B | A | 8 | 5 | 1,000 | 11,000 | 3,333 |
| C | A | 5 | 4 | 4,000 | 18,000 | 14,000 |
| D | C | 5 | 3 | 2,000 | 13,000 | 5,500 |

Paths: A-B = 12 days, A-C-D = 14 days. The normal duration is **14 days** (critical path A-C-D). Normal direct cost = 4,000 + 1,000 + 4,000 + 2,000 = N11,000. With fixed cost of N3,500 per day, the normal total cost is 11,000 + 3,500 x 14 = **N60,000**.

The 2019/20 paper uses different numbers for the same table (A 3 to 1, B 7 to 3, C 4 to 2, D 5 to 2, fixed N4,500 per day). Its normal duration is 12 days (A-C-D), the slopes are A 5,000, B 2,500, C 7,000, D 3,667, and its normal total cost is 11,000 + 4,500 x 12 = **N65,000**.

### Worked example 2 (2023/24 Question 1)

Software project, costs in N'000, fixed cost taken as N100 thousand **per day** (see the assumption note below).

| Activity | After | Normal days | Crash days | Normal cost | Crash cost | Cost slope per day |
| --- | --- | --- | --- | --- | --- | --- |
| A | - | 5 | 4 | 100 | 200 | 100 |
| B | A | 3 | 2 | 300 | 350 | 50 |
| C | A | 2 | 1 | 200 | 325 | 125 |
| D | B, C | 2 | 1 | 250 | 300 | 50 |
| E | C | 1 | 1 | 400 | 400 | cannot crash |
| F | D | 4 | 2 | 500 | 900 | 200 |
| G | E | 4 | 2 | 150 | 350 | 100 |

- **Normal direct cost:** 100 + 300 + 200 + 250 + 400 + 500 + 150 = **N1,900k**.
- **Paths:** A-B-D-F = 14, A-C-D-F = 13, A-C-E-G = 12. Critical path **A-B-D-F**, normal duration **14 days**.
- **Full crash** (every activity at its crash time): A-B-D-F = 9, A-C-D-F = 8, A-C-E-G = 8. Duration **9 days**, critical path still A-B-D-F. All activities crashed cost N2,825k, but C does not need crashing to reach 9 days, so the cheapest way to get 9 days costs N2,700k.
- **Crashing step by step:**
  1. Crash B by 1 day (slope 50, cheapest critical). Now A-B-D-F = 13 and A-C-D-F = 13, two critical paths.
  2. Crash D by 1 day (slope 50, lies on both). Now A-B-D-F = 12, A-C-D-F = 12 and A-C-E-G = 12, three critical paths.
  3. Going further means crashing A (slope 100, on all three), which only just breaks even against N100 saved per day. Beyond that, F (200) and G (100) must be crashed together and cost more than they save.

| Duration (days) | Direct cost (N'000) | Indirect at 100/day | Total (N'000) |
| --- | --- | --- | --- |
| 14 (normal) | 1,900 | 1,400 | 3,300 |
| 13 | 1,950 | 1,300 | 3,250 |
| **12** | 2,000 | 1,200 | **3,200** |
| **11** (A crashed too) | 2,100 | 1,100 | **3,200** |
| 10 | 2,400 | 1,000 | 3,400 |
| 9 (full crash) | 2,700 | 900 | 3,600 |

The minimum total cost is **N3,200k at 12 days** (11 days costs the same). Full crash costs N3,600k, which is N400k more than the minimum, and N300k more than normal. So the fastest plan is not the cheapest plan.

**Assumption to confirm.** The paper says "fixed cost of N100,000" without "per day". If it is a one-off lump sum, normal total cost is just 1,900 + 100 = N2,000k and crashing never pays, which would make part (iv) pointless. I treated it as per day. Ask your lecturer if you can.

## 7. Resources: loading, levelling and resource-constrained scheduling

Everything so far assumed resources are always there. A network with times is **not yet a schedule** until resources are assigned. This section is where the plan meets reality, and it carries the longest question in the 2019/20 and 2020/21 papers.

### Short notes asked every year (2 marks each)

The slides give the first three; the workload definition follows from the exam question itself.

- **Resource allocation**: assigning the required resources to each activity, in the right amount and at the right time.
- **Resource loading**: the amount of a resource the project needs, activity by activity and period by period. It changes through the project, and plotting it gives a resource profile (histogram).
- **Resource scheduling**: fixing start and finish times of activities so the resource limits are respected (or so demand is even).
- **Workload**: the total work a resource does, taken as time worked multiplied by hours per day (person-hours).

**Worked workload question (2024/25 Q5b).** Josiah worked 6 days at 8 hours. Oluwatobi and Ginika worked 2 hours less, so 6 hours a day, for 4 and 5 days. Jesuseun worked half of Josiah's hours, so 4 hours a day, for 3 days.

| Person | Days | Hours per day | Workload (hours) |
| --- | --- | --- | --- |
| Oluwatobi | 4 | 6 | 24 |
| Jesuseun | 3 | 4 | 12 |
| Ginika | 5 | 6 | 30 |
| Josiah | 6 | 8 | 48 |
| **Total** |  |  | **114** |

The 2019/20 version of this question uses different names and says "Stephen works for half the time Mohammed worked", which clashes with "Abdulkabir and Stephen worked 2 hours less". Read your paper carefully and state your reading.

### Kinds of resources and which need levelling

Resources are **labour** (salaried staff, hourly workers), **equipment** and **materials**. Equipment and materials are either *construction* items that are used and removed (cranes, scaffolding, formwork) or *installed* items that stay (generators, concrete, rebar). Not all resources need levelling. Hired or rented labour and major equipment do, because uneven demand wastes money (hire, mobilisation, set-up, demobilisation). Materials generally do not, because delivery can be lumpy (100 cubic yards of concrete one day, none the next week).

### Why resources constrain the schedule (asked 2019/20 and 2023/24, 4 marks)

Virtually every real project needs resources that are not always available in the right amount, and availability decides when an activity can really start. CPM ignores this, so a CPM schedule can be impossible to carry out. **Resource-constrained scheduling** takes availability into account. The usual result is a *longer* project, because activities that compete for the same resource must wait for each other. Resource limits may also come from technical logic, physical limits or equipment.

|  | Time-constrained project | Resource-constrained project |
| --- | --- | --- |
| Fixed | The end date | The amount of resources |
| Flexible | Resources (add more to hit the date) | Time (shortage delays the project) |
| Typical tool | Resource smoothing (levelling) using float | Priority rules (heuristics) |

### Smoothing and levelling

Your sources use these two words slightly differently, so check which one your lecturer uses.

- **Resource smoothing** (SIMS and Makwana slides): the project end date must not move. Shift non-critical activities within their float to flatten the peaks in demand.
- **Resource levelling**: demand is limited by what is available. If demand exceeds supply, delay the activity with the **most float** first; the project may finish later. If activities tie, choose the one with the shortest duration to reschedule. Lecture 10 and the MGMT 4135 slides use "levelling" more loosely for any attempt to make daily use of a resource as even as possible.

**Example (MGMT 4135, botanical garden).** One resource, backhoes, peaked at 4 in periods 4 to 10. Only two activities had float: Irrigation, and Fence and Walls. The manager delayed Fence and Walls (the least risky one to delay) from period 4 to period 10, and the peak fell from 4 backhoes to 3, a 25% saving, with no change in finish date.

**Sharing across projects.** When several projects share staff or equipment you get overall slippage, uneven demand and bottlenecks. Ways to manage it: a project office, first come first served, treating all projects as one "megaproject", or outsourcing. Lecture 10 shows a sharing engineer is cheaper than two engineers only while travel time and mileage stay below the second salary.

### Priority rules (heuristics) for resource-constrained scheduling

When several activities are ready and there are not enough resources for all of them, a rule decides who goes first. The rules are all from the 2019/20 and 2020/21 papers. Here t is activity time, x\_ij is how much of resource j activity i needs, y\_j is the maximum available of resource j, and s is the standard deviation of the activity.

| Rule | Formula | In words |
| --- | --- | --- |
| ACTRES | t x (resources required) | Duration times resource need |
| ROT (Resource Over Time) | (resources required) / t | Resource need divided by duration |
| TIMRES | 0.5 x (activity time) + 0.5 x ACTRES | Equal mix of time and ACTRES |
| GENRES | w x (activity time) + (1 - w) x ACTRES | General form; TIMRES is GENRES with w = 0.5 |
| RAF (Resource Allocation Factor) | (1 / t) x sum over resources of (x\_ij / y\_j) | Share of the available resources the activity uses, per unit time |
| SAF (Stochastic Allocation Factor) | t + s / t | Duration plus a measure of how uncertain it is |
| Scaled RAF | RAF / (largest RAF) x 100 | RAF rescaled so the biggest is 100 |
| Scaled SAF | (t / largest t) x 50 + ((s/t) / largest (s/t)) x 50 | Both parts rescaled to a total out of 100 |
| CAF (Composite Allocation Factor) | w x (Scaled RAF) + (1 - w) x (Scaled SAF) | Blend of the two, w chosen by the planner |
| Scaled CAF | CAF / (largest CAF) x 100 | The final priority score |

Scaling matters because RAF is a small decimal while SAF is a number of weeks; without scaling one would swamp the other. A higher scaled CAF means higher priority.

### Brooks' algorithm (serial priority scheduling)

1. Compute the priority (scaled CAF) of every activity and rank them.
2. Start at time zero. List the activities whose predecessors are all finished.
3. Go down that list in priority order. Schedule an activity now if there is enough of **every** resource left; otherwise hold it back.
4. Move the clock to the next moment an activity finishes. That releases its resources. Repeat steps 2 and 3.
5. Stop when every activity is scheduled. The finish time of the last one is the project time.

In the exam tables the columns are Duration, Scaled CAF, Immediate precedence, Resources required, TEARL (earliest start from logic), TSCHED (time actually scheduled), TFIN (finish), TNOW (clock time), Resources available, Activities allowed, Iteration number.

### Worked example (2019/20 Question 1c)

Development tasks with PERT times in weeks and human resources needed (Type 1 technical, Type 2 supportive). Maximum available: Type 1 = 8, Type 2 = 10. Weight w = 0.6 on RAF.

| Task | After | a, m, b | t = (a+4m+b)/6 | s = (b-a)/6 | Type 1 | Type 2 |
| --- | --- | --- | --- | --- | --- | --- |
| A Hardware selection | - | 4, 6, 7 | 5.83 | 0.50 | 4 | 5 |
| B Software design | - | 3, 4, 7 | 4.33 | 0.67 | 6 | 3 |
| C Install hardware | A | 2, 3, 4 | 3.00 | 0.33 | 4 | 5 |
| D Code and test software | B | 1, 2, 4 | 2.17 | 0.50 | 5 | 4 |
| E File take-on | B | 1, 3, 4 | 2.83 | 0.50 | 3 | 5 |
| F Write user manual | - | 8, 10, 14 | 10.33 | 1.00 | 6 | 6 |
| G User training | E, F | 3, 3, 3 | 3.00 | 0.00 | 5 | 4 |
| H Install and test system | C, D | 1, 2, 4 | 2.17 | 0.50 | 5 | 4 |

**(i) RAF and scaled RAF.** For task A: RAF = (1/5.83) x (4/8 + 5/10) = 0.171. The largest RAF is 0.473 (tasks D and H), so scaled RAF for A = 0.171 / 0.473 x 100 = 36.2.

**(ii) SAF.** For task A: scaled t = 5.83 / 10.33 x 50 = 28.2; s/t = 0.50 / 5.83 = 0.086. The largest s/t is 0.231 (tasks D and H), so the second part is 0.086 / 0.231 x 50 = 18.6. The two parts add to 28.2 + 18.6 = 46.8.

**(iii) Scaled CAF** = 0.6 x (scaled RAF) + 0.4 x (scaled SAF), then divided by the largest CAF and multiplied by 100.

| Task | RAF | Scaled RAF | Scaled SAF | CAF | Scaled CAF |
| --- | --- | --- | --- | --- | --- |
| A | 0.171 | 36.2 | 46.8 | 40.5 | 48.1 |
| B | 0.242 | 51.2 | 54.3 | 52.5 | 62.3 |
| C | 0.333 | 70.5 | 38.6 | 57.7 | 68.6 |
| D | 0.473 | 100.0 | 60.5 | 84.2 | 100.0 |
| E | 0.309 | 65.3 | 51.9 | 60.0 | 71.2 |
| F | 0.131 | 27.6 | 71.0 | 45.0 | 53.4 |
| G | 0.342 | 72.2 | 14.5 | 49.1 | 58.4 |
| H | 0.473 | 100.0 | 60.5 | 84.2 | 100.0 |

Priority order: D and H (tied at 100), E, C, B, G, F, A. The tie does not change the schedule, because H cannot start until C and D are both finished.

**(iv) Brooks' algorithm.** At time 0 only A, B and F are ready. B has the highest priority and fits (6 of 8 Type 1, 3 of 10 Type 2). F would need 6 more of Type 1 and A another 4, so both wait. The resulting schedule:

| Task | Start | Finish |
| --- | --- | --- |
| B | 0 | 4.33 |
| D | 4.33 | 6.50 |
| E | 4.33 | 7.17 |
| A | 6.50 | 12.33 |
| C | 12.33 | 15.33 |
| H | 15.33 | 17.50 |
| F | 17.50 | 27.83 |
| G | 27.83 | 30.83 |

Project time with limited resources: **30.83 weeks**. Without resource limits the same network needs only 13.33 weeks (the longest path is F-G = 10.33 + 3). The gap of about 17.5 weeks is the price of the resource limit. The long, hungry task F (6 + 6 units) cannot run alongside anything big, so it sits at the end and drags the finish out.

## 8. Other scheduling tools and the rest of the course outline

### Project scoring model (2024/25 Question 1d)

When you must choose between projects, a scoring model turns cost, chance of success and payoff into one number you can rank. The paper gives: Score = (P(success) + 2 x Payoff) / Cost.

| Rank | Project | Score |
| --- | --- | --- |
| 1 | 4 | 4.96 |
| 2 | 6 | 4.22 |
| 3 | 3 | 4.13 |
| 4 | 5 | 4.10 |
| 5 | 8 | 3.43 |
| 6 | 1 | 3.43 |

The three best are **projects 4, 6 and 3**. Project 5 is a very close fourth (4.10 against 4.13), so as the project manager say that the call between 3 and 5 is nearly a tie and could be settled by something outside the score such as risk or strategic fit. The remaining projects score lower (10: 3.35, 9: 2.78, 2: 2.57, 7: 2.55, 11: 2.45, 12: 2.40). Note that several P(success) values are above 1, which a real probability cannot be, so treat them as scores out of a larger scale.

### Bar charts, line of balance and time-location charts

Your course outline lists these, but your slides and past papers do not cover them, so this is general knowledge. Check against class notes.

- **Bar chart (Gantt chart)**: each activity is a horizontal bar on a time axis. Easy to read and good for progress reporting, but it shows dependencies poorly. Float is shown as a thin line after the bar.
- **Line of balance**: for repetitive work such as many identical houses. It plots units completed against time so you can see whether each trade is keeping pace with the target.
- **Time-location (time-chainage) chart**: for linear projects such as roads and pipelines. Position along the route is one axis and time is the other, so each activity is a sloping line and clashes between crews are visible.

### Schedules that come out of the master schedule

Once the project schedule exists, you can derive a construction schedule, material schedule, labour schedule, equipment schedule, financial schedule and invoice schedule. Steps to prepare it: study the scope, decide the method, break the scope into work packages and activities, build the CPM or PERT network, derive a week-by-week or month-by-month schedule, add a master schedule if there are sub-projects, and revise it regularly because real progress always differs from plan.

### Time and cost control (general knowledge, not in your slides)

The outline lists time and cost control and progress monitoring, and your slides name earned value analysis (EVA) as a technique. The standard measures are below. If your lecturer covered EVA, expect this to be tested.

| Measure | Formula | Reading |
| --- | --- | --- |
| Planned value (PV) | Budgeted cost of work scheduled | What you planned to have done |
| Earned value (EV) | Budgeted cost of work done | What you actually achieved, valued at budget |
| Actual cost (AC) | What you actually spent |  |
| Schedule variance | SV = EV - PV | Negative means behind schedule |
| Cost variance | CV = EV - AC | Negative means over budget |
| SPI and CPI | EV / PV and EV / AC | Below 1 is bad |

Software named in class: MS Project and Primavera. They run the CPM calculations, produce Gantt charts and let you assign and level resources.

## 9. Past questions and how to answer them

Every paper has the same shape: **answer Question 1 and any two others**. The same ideas come back year after year, so this section first maps each question to the section that answers it, then solves the calculation questions in full. All numbers below were recomputed in code, not copied from the marking scheme.

### 9.1 Where each question is answered

| Paper | Question | Topic | Marks | Answered in |
| --- | --- | --- | --- | --- |
| 2019/20 | 1a | Significance of resource-constraining | 4 | Section 7 |
| 2019/20 | 1b | ACTRES, ROT, Scaled SAF, RAF, CAF definitions | 10 | Section 7 (rules table) |
| 2019/20 | 1c | RAF, SAF, CAF and Brooks' algorithm | 26 | Section 7 (worked) |
| 2019/20 | 2a, 2b | Resource short notes; four dependencies | 16 | Sections 7 and 3 |
| 2019/20 | 2c | Crash table (A 3/1, B 7/3, C 4/2, D 5/2), fixed N4,500/day | 14 | Section 6 |
| 2019/20 | 3a, 3b | WBS; Laralek AON diagram, critical path, ES/EF/LS/LF | 30 | Sections 2 and 9.2 |
| 2019/20 | 4 | 10 knowledge areas; 5 characteristics; workload; level of activity | 30 | Sections 1 and 7 |
| 2019/20 | 5 | Three-point estimate; PERT network and probabilities | 30 | Section 5 |
| 2023/24 | 1a, 1b | Resource-constraining; crashing with fixed cost | 40 | Sections 7 and 6 |
| 2023/24 | 2 | Resource notes; four dependencies; crash table (A 4/2 ...) | 30 | Sections 7, 3, 6 |
| 2023/24 | 3 | Rolling wave; reserves; AOA network ES/EF/LS/LF | 30 | Sections 2 and 9.2 |
| 2023/24 | 4 | Level of activity; 5 characteristics; large network | 30 | Sections 1 and 9.2 |
| 2023/24 | 5 | Three-point estimate; cost PERT; PERT network | 30 | Sections 5 and 9.3 |
| 2024/25 | 1 | Triple constraint; CPM vs PERT; Dangote network; scoring model | 40 | Sections 1, 5, 9.2, 8 |
| 2024/25 | 2 | Characteristics; 5 process groups; dependencies; PERT with parameter t | 30 | Sections 1, 3, 5 |
| 2024/25 | 3 | Short notes; e-library PERT, all-paths probability | 30 | Sections 3, 4, 2, 9.3 |
| 2024/25 | 4 | Three-point estimate; software AOA network | 30 | Sections 5 and 9.2 |
| 2024/25 | 5 | Resource notes; workload; crash table (A 4/2 ...) | 30 | Sections 7 and 6 |
| 2020/21 | 1 to 4 | CPM and crashing; PERT; PDM; resource-constrained (marking scheme only; your files do not include the paper) | 40 each | Sections 4 to 7, 9.3, 9.4 |

The most repeated items, so learn these cold: the PERT A to J table (three papers), the A to D crash table (three papers), the four dependencies (four papers), three-point estimate with diagram (three papers), resource short notes (three papers), five characteristics (three papers), level of activity diagram (three papers).

### 9.2 Network questions: full forward and backward pass

In every table, ES = earliest start, EF = earliest finish, LS = latest start, LF = latest finish, Float = LS - ES. Critical activities have zero float.

**2019/20 Q3b: Laralek AON network.** Project duration **30 days**. Critical path **A-F-D-G-H-N-O** (A has zero duration).

| Activity | Duration | After | ES | EF | LS | LF | Float |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 0 | - | 0 | 0 | 0 | 0 | 0 |
| B | 10 | A | 0 | 10 | 16 | 26 | 16 |
| C | 5 | A | 0 | 5 | 18.5 | 23.5 | 18.5 |
| F | 2 | A | 0 | 2 | 0 | 2 | 0 |
| D | 14 | F | 2 | 16 | 2 | 16 | 0 |
| E | 10 | F | 2 | 12 | 6 | 16 | 4 |
| G | 12 | D, E | 16 | 28 | 16 | 28 | 0 |
| H | 1 | G | 28 | 29 | 28 | 29 | 0 |
| I | 1 | B | 10 | 11 | 27 | 28 | 17 |
| J | 5 | C | 5 | 10 | 23.5 | 28.5 | 18.5 |
| K | 0.5 | I, J | 11 | 11.5 | 28.5 | 29 | 17.5 |
| L | 2 | B | 10 | 12 | 26 | 28 | 16 |
| M | 1 | I, L | 12 | 13 | 28 | 29 | 16 |
| N | 0.5 | H, K, M | 29 | 29.5 | 29 | 29.5 | 0 |
| O | 0.5 | N | 29.5 | 30 | 29.5 | 30 | 0 |

**2023/24 Q3c: Craneburg AOA network.** Project duration **36 days**. Critical path **1-3-5-6-8-9** (11 + 7 + 2 + 8 + 8).

| Activity | Duration | ES | EF | LS | LF | Float |
| --- | --- | --- | --- | --- | --- | --- |
| 1-2 | 0 | 0 | 0 | 6 | 6 | 6 |
| 1-3 | 11 | 0 | 11 | 0 | 11 | 0 |
| 1-4 | 6 | 0 | 6 | 5 | 11 | 5 |
| 2-4 | 5 | 0 | 5 | 6 | 11 | 6 |
| 3-5 | 7 | 11 | 18 | 11 | 18 | 0 |
| 3-6 | 5 | 11 | 16 | 15 | 20 | 4 |
| 4-6 | 9 | 6 | 15 | 11 | 20 | 5 |
| 4-7 | 10 | 6 | 16 | 14 | 24 | 8 |
| 4-8 | 12 | 6 | 18 | 16 | 28 | 10 |
| 5-6 | 2 | 18 | 20 | 18 | 20 | 0 |
| 6-8 | 8 | 20 | 28 | 20 | 28 | 0 |
| 6-9 | 12 | 20 | 32 | 24 | 36 | 4 |
| 7-8 | 4 | 16 | 20 | 24 | 28 | 8 |
| 8-9 | 8 | 28 | 36 | 28 | 36 | 0 |

**2024/25 Q1c: Dangote refinery maintenance (hours).** Project duration **120 hours**. All paths:

| Path | Length (hours) |
| --- | --- |
| A-E-N-Q-S-T-U (critical) | **120** |
| A-E-N-P-R-S-T-U | 112 |
| A-B-F-H-I-L-U | 106 |
| A-B-G-I-L-U | 98 |
| A-C-J-L-U | 84 |
| A-D-M-U | 80 |
| A-E-O-T-U | 76 |
| A-C-K-U | 60 |

| Activity | Event pair | Duration | ES | EF | LS | LF | Float |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 1-2 | 24 | 0 | 24 | 0 | 24 | 0 |
| B | 2-3 | 16 | 24 | 40 | 38 | 54 | 14 |
| C | 2-6 | 16 | 24 | 40 | 60 | 76 | 36 |
| D | 2-8 | 40 | 24 | 64 | 64 | 104 | 40 |
| E | 2-9 | 24 | 24 | 48 | 24 | 48 | 0 |
| F | 3-4 | 16 | 40 | 56 | 54 | 70 | 14 |
| G | 3-5 | 8 | 40 | 48 | 62 | 70 | 22 |
| H (dummy) | 4-5 | 0 | 56 | 56 | 70 | 70 | 14 |
| I | 5-7 | 6 | 56 | 62 | 70 | 76 | 14 |
| J (dummy) | 6-7 | 0 | 40 | 40 | 76 | 76 | 36 |
| K | 6-14 | 12 | 40 | 52 | 100 | 112 | 60 |
| L | 7-14 | 36 | 62 | 98 | 76 | 112 | 14 |
| M | 8-14 | 8 | 64 | 72 | 104 | 112 | 40 |
| N | 9-10 | 16 | 48 | 64 | 48 | 64 | 0 |
| O | 9-13 | 4 | 48 | 52 | 92 | 96 | 44 |
| P | 10-11 | 16 | 64 | 80 | 72 | 88 | 8 |
| Q | 10-12 | 24 | 64 | 88 | 64 | 88 | 0 |
| R (dummy) | 11-12 | 0 | 80 | 80 | 88 | 88 | 8 |
| S | 12-13 | 8 | 88 | 96 | 88 | 96 | 0 |
| T | 13-14 | 16 | 96 | 112 | 96 | 112 | 0 |
| U | 14-15 | 8 | 112 | 120 | 112 | 120 | 0 |

**2024/25 Q4b: software development (weeks).** Paths: A-D-I = 17, B-E-G-J = 18, C-F-H-J = **21**. Critical path **C-F-H-J**, duration **21 weeks**.

| Task | Duration | After | ES | EF | LS | LF | Float |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 3 | - | 0 | 3 | 4 | 7 | 4 |
| B | 5 | - | 0 | 5 | 3 | 8 | 3 |
| C | 7 | - | 0 | 7 | 0 | 7 | 0 |
| D | 8 | A | 3 | 11 | 7 | 15 | 4 |
| E | 5 | B | 5 | 10 | 8 | 13 | 3 |
| F | 5 | C | 7 | 12 | 7 | 12 | 0 |
| G | 4 | E | 10 | 14 | 13 | 17 | 3 |
| H | 5 | F | 12 | 17 | 12 | 17 | 0 |
| I | 6 | D | 11 | 17 | 15 | 21 | 4 |
| J | 4 | G, H | 17 | 21 | 17 | 21 | 0 |

**2023/24 Q4c: large construction network.** Treat the three durations shown as "-" (11-22, 16-19, 18-19) as dummy activities of zero duration. Project duration **66 days**. Critical path **1-2-15-16-17-22-23** (1 + 3 + 1 + 24 + 36 + 1). The next longest paths are 1-2-15-18-21-22-23 (56 days) and 1-2-12-14-22-23 (45 days). Draw it carefully: node 22 is the big merge point where eight arrows meet.

### 9.3 PERT and cost questions

**2024/25 Q3b: e-library project.** The table's three rows are labelled a, b, C, but by size they are optimistic, most likely and pessimistic (see the label warning in section 5).

| Activity | After | t\_e | Variance |
| --- | --- | --- | --- |
| A | - | 5 | 1.778 |
| B | - | 6 | 0.111 |
| C | A | 3 | 0.111 |
| D | A | 5 | 1.000 |
| E | B | 4 | 1.000 |
| F | C, D | 2 | 0.111 |
| G | E | 1 | 0 |
| H | G | 4 | 0.111 |
| I | F, G | 3 | 0.444 |
| J | H | 1 | 0 |
| K | I, J | 7 | 2.778 |

Critical path **B-E-G-H-J-K**, T\_e = **23 days**, V\_p = 4.0.

**(ii) All paths done by T\_e + 2 = 25 days**, treating the paths as independent:

| Path | Mean | Variance | Z | Probability |
| --- | --- | --- | --- | --- |
| A-C-F-I-K | 20 | 5.222 | 2.19 | 0.9857 |
| A-D-F-I-K | 22 | 6.111 | 1.21 | 0.8875 |
| B-E-G-H-J-K | 23 | 4.000 | 1.00 | 0.8413 |
| B-E-G-I-K | 21 | 4.333 | 1.92 | 0.9727 |
| **All four together** |  |  |  | **0.716** (about 71.6%) |

The critical path alone has only an 84% chance, and the combined chance is lower because every path must come in on time.

**2023/24 Q5b: cost PERT.** Three cost estimates per activity (N). Mean = (Co + 4Cm + Cp)/6, variance = ((Cp - Co)/6) squared.

| Activity | Co | Cm | Cp | Mean cost | Variance |
| --- | --- | --- | --- | --- | --- |
| A | 80 | 100 | 150 | 105.00 | 136.11 |
| B | 40 | 50 | 75 | 52.50 | 34.03 |
| C | 200 | 200 | 200 | 200.00 | 0 |
| D | 50 | 60 | 60 | 58.33 | 2.78 |
| E | 30 | 40 | 60 | 41.67 | 25.00 |
| **Total** |  |  |  | **457.50** | **197.92** |

Standard deviation = square root of 197.92 = 14.07. For the probability that total cost is between N450 and N500: Z1 = (450 - 457.5) / 14.07 = -0.53, so P = 0.297. Z2 = (500 - 457.5) / 14.07 = 3.02, so P = 0.999. The answer is 0.999 - 0.297 = **0.70** (about 70%).

**2023/24 Q5c and 2019/20 Q5b.** These are the A to J example in section 5: T\_e = 20 days, V\_p = 5.556, P(21 days) about 0.66, P(24 days) about 0.955, P(30 days) about 1.

**2024/25 Q2d.** Worked in section 5: T\_e = (t^2 + 2t)/3, sigma = t/3, probability = Phi(2(t + 2)).

**2020/21 Q2: power plant (corrected).** Expected times t\_e: A 15.33, B 9.67, C 11.83, D 10.17, E 29.50, F 12.17, G 37.33, H 48.33, I 12.50, J 6.17, K 6.17. Critical path **B-D-H-J-K**, T\_e = **80.5 weeks**. Its variance is 1.00 + 6.25 + 2.78 + 0.25 + 0.25 = **10.53**, so sigma = 3.25.

| Target | Z | Probability |
| --- | --- | --- |
| 77 weeks | -1.08 | 0.140 |
| 82 weeks | 0.46 | 0.678 |
| Between 77 and 82 |  | 0.678 - 0.140 = **0.538** |

Your marking scheme gives 15.03 for the variance and 0.1767, 0.6506 and 0.4739 for the probabilities. That sum is wrong (the same five numbers add to 10.53), and its Z values do not match each other. See section 10.

**Assignment 2 (computer installation).** The three columns are a, b, m in the order given, so A is a = 4, m = 5, b = 7. Expected times: A 5.17, B 8.00, C 4.00, D 2.00, E 2.33, F 4.33, G 2.00, H 4.17. Critical path **B-D-F-H**, T\_e = **18.5 weeks**, V\_p = 1.25. P(finish in 20 weeks) = Phi((20 - 18.5) / 1.118) = Phi(1.34) = **0.91**.

### 9.4 Crashing, precedence and resource questions

- **Crash tables (2019/20 Q2c, 2023/24 Q2c, 2024/25 Q5c).** Plot the arrow diagram A to (B and C to D), normal duration, cost slope per activity, normal total cost: all worked in section 6, worked example 1. Two versions: N60,000 for the 2023/24 and 2024/25 numbers, N65,000 for the 2019/20 numbers.
- **2023/24 Q1b: software project crashing.** Worked in section 6, worked example 2. Normal direct cost N1,900k, normal duration 14 days, full crash 9 days, minimum total cost N3,200k at 12 days (or 11).
- **2020/21 Q1: CPM and crashing.** The marking scheme finds a critical path START-P-Q-S-T-W-X-Y-END of 6.4 time units, and crashes X by 0.5, P by 0.1, W by 0.1 and T by 0.1, for an extra cost of $17.5 thousand. It crashes in order of lowest crash ratio (20, 20, 20, 35 per unit). That is the same algorithm as section 6.
- **2020/21 Q3: precedence relationships.** Worked in section 3: 15 days without relationships, 18 days with them, new critical path A-C-F-H.
- **2020/21 Q4: resource-constrained scheduling (w = 0.4, available Type 1 = 10, Type 2 = 12).** Expected times: P 3.67, Q 3.00, R 9.83, S 6.17, T 2.00, U 15.83, V 2.00, W 7.67. Without resource limits the project takes 21.17 weeks. Scaled CAF values:

| Activity | P | Q | R | S | T | U | V | W |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Scaled CAF | 89.89 | 68.09 | 63.46 | 33.07 | 63.61 | 67.53 | 100.00 | 52.77 |

Priority order: **V, P, Q, U, T, R, W, S**. The marking scheme's Brooks' table ends at 31.34 weeks. My run of the algorithm with the same priority order and the resource figures printed in the question gives 29.33 weeks. The scheme's table lists a Type 1 need of 7 for activity S where the question says 0, which probably explains the gap. Use the lecturer's layout and say so if you get a different figure. Either way the conclusion the scheme wants is the same: limiting resources does not shorten a project; it usually lengthens it, because activities have to wait for each other.

## 10. Corrections and things to confirm

These are the places where your sources disagree with each other or with a recalculation. Check them against your class notes.

1. **2020/21 PERT marking scheme (power plant).** Critical-path variance is given as 15.03, but 1.00 + 6.25 + 2.78 + 0.25 + 0.25 = 10.53. The scheme's Z values (0.3869 for 77 weeks, -0.9028 for 82 weeks) also do not match 80.5 as the mean. I used the recalculated figures in section 9.3.
2. **2020/21 Brooks' algorithm.** The scheme's 31.34 weeks does not match my run (29.33 weeks). The scheme's S row uses Type 1 = 7 where the question says 0.
3. **"Slack or free float" = LS - ES.** That is total float. Free float is different. I used the lecturer's term but flagged it in section 4.
4. **2024/25 Q3b column labels.** The rows are labelled a, b, C; I read them as optimistic, most likely, pessimistic. If your lecturer meant the labels literally, the answers change.
5. **2023/24 Q1b fixed cost.** "Fixed cost of N100,000" has no "per day". I read it as N100 thousand per day so the time-cost question makes sense. Confirm.
6. **2024/25 Q1d scoring model.** Several P(success) values are above 1. I scored them as given.
7. **Workload question.** The 2019/20 wording ("Stephen works for half the time Mohammed worked") contradicts the line before it. I used the 2024/25 wording.
8. **Not in your slides.** The 10 knowledge-area descriptions, rolling wave planning, management vs contingency reserve, bar chart, line of balance, time-location charts and earned value are written from general project-management knowledge. Verify them against your lecture notes.
9. **Not read.** The 2020/21 question paper itself is not in your files (only the marking scheme), and two parts of its marking scheme (the precedence-time algebra in Q3a(iv) and the Q1(iv) deadline part) are images with no readable question text. The scanned PERT chapter was read for its worked examples (all checked above); I did not use its examples for other topics.
