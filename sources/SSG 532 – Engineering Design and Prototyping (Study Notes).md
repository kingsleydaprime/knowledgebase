# SSG 532 – Engineering Design and Prototyping (Study Notes)

Nov 23, 2026 · @Kingsley Ihemelandu Chukwudi

## 1. Introduction to Engineering Design and Prototyping

This course is about how we go from a human need to a working solution. This first lecture gives the two big ideas (design and prototyping) and the steps the rest of the course follows.

### What they are

- **Engineering design** is the process of creating solutions to meet human needs and desires by applying scientific and engineering knowledge, skills and tools.
- **Engineering prototyping** is the process of creating physical or virtual models of the design solution to test its feasibility, functionality and usability.
- According to the pdf, **Systems Engineering** is the discipline of designing, developing and managing complex systems that satisfy the needs of customers and stakeholders. Design and prototyping sit inside it and depend on each other: design creates the solution, prototyping tests it.

### Importance

They enable engineers to:

1. Solve real-world problems that affect people, society and the environment.
2. Innovate new products, services and systems that create value and improve quality of life.
3. Communicate and collaborate with other engineers, customers and stakeholders effectively.
4. Learn from feedback and failures and improve their design solutions continuously.

### Challenges

They are challenging because they involve:

1. Dealing with ill-defined, complex and dynamic problems that have multiple and conflicting objectives, requirements, constraints and criteria for success.
2. Generating and selecting among many possible design concepts that have different trade-offs, risks and uncertainties.
3. Refining and detailing the design concept to meet the specifications and standards of the system.
4. Prototyping and testing the design solution in realistic conditions and evaluating its performance and outcomes.
5. Managing the resources, time and cost of the design and prototyping process.

### Phases of the design process

The design process is a systematic and iterative approach to engineering design and prototyping. Iterative means you can go back to an earlier phase when testing shows a problem. It has seven phases:

| # | Phase | What you do | Methods |
| --- | --- | --- | --- |
| 1 | Problem definition | Identify and analyse the design problem and its context, and define the objectives, requirements, constraints and criteria for success | User research, benchmarking, mind mapping, SCAMPER |
| 2 | Concept generation | Generate multiple design concepts that satisfy the problem definition | Brainstorming, morphological analysis, TRIZ, SCAMPER |
| 3 | Concept selection | Select the best design concept that meets the criteria for success | Pugh matrix, Kano model, decision matrix, AHP |
| 4 | Concept refinement | Refine the selected design concept | Functional decomposition, design structure matrix, QFD |
| 5 | Detailed design | Detail the concept by specifying the dimensions, materials, components, interfaces and functions of the system | Drawings and specifications |
| 6 | Prototyping | Create physical or virtual models of the design solution | 3D printing, CAD, simulation |
| 7 | Testing and evaluation | Test and evaluate the design solution | Experiments, surveys, interviews |

### Creativity, innovation and user needs

- **Creativity** is the ability to generate novel and useful ideas that solve problems or meet needs.
- **Innovation** is the process of implementing creative ideas into practical and valuable solutions.
- **User needs** are the desires, expectations and requirements of the potential users or customers of the design solution.

They all help engineers to:

1. Identify and define the design problem and its context from different perspectives and sources of information.
2. Generate and select among diverse and original design concepts that address the problem and its context effectively and efficiently.
3. Refine and detail the design concept to meet the specifications and standards of the system and the user needs.
4. Prototype and test the design solution to ensure its feasibility, functionality and usability for the intended users and stakeholders.
5. Improve the design solution by incorporating feedback and suggestions from the users and stakeholders.

Creativity makes the ideas, innovation turns them into something real, and user needs keep both pointed at the right target.

### Case studies

When stating a case study, start with (i) the mission of the project, (ii) the capabilities, (iii) the impact, (iv) the future.

| Case | Mission | Capabilities | Impact | Future |
| --- | --- | --- | --- | --- |
| Mars Rover | Explore the Martian surface, search for signs of past or present life, study the planet's geology and climate | Cameras, spectrometers and drills to analyse rocks, weather patterns and the Martian atmosphere | Revealed evidence of ancient water, diverse minerals and potential for supporting microbial life | Paves the way for future robotic and human missions, and gives data for a possible Martian base |
| iPhone | Revolutionise mobile communication | Touchscreen interface, app store, internet, camera and multimedia in one device | Transformed communication, entertainment and business, and shaped online behaviour | New models yearly with better cameras, processing power and features |
| Tesla Model 3 | Make electric vehicles more affordable, powerful and stylish | Strong acceleration, long driving range, advanced driver-assistance | Pushed traditional carmakers to invest heavily in EVs | Charging infrastructure and range anxiety are still hurdles; better batteries and charging networks should help |
| EpiPen | Deliver a precise dose of epinephrine within seconds to treat anaphylactic shock (a severe allergic reaction) | Compact and easy to carry, so people with allergies can manage their condition confidently | Increased awareness of allergies and of carrying an EpiPen | Next-generation EpiPens with improved safety features, possibly treating other conditions |
| Dyson Airblade | Dry hands quickly and hygienically | Uses high-velocity air | Reduces spread of bacteria compared to conventional dryers and uses less energy | Could become the preferred hand dryer in more public and private places as awareness of hygiene and sustainability grows |

## 2. Problem Definition and Concept Generation

These are the first two steps of engineering design: first you understand the problem (problem definition), then you come up with possible answers (concept generation). A solution can only be as good as the problem it was built for, so we start there.

### Problem definition

Problem definition involves four things:

1. **Objectives**: What are you trying to achieve? What are the desired outcomes of the design?
2. **Requirements**: What are the essential features and functions? What are the limitations and constraints?
3. **Constraints**: Factors that limit your design choices. They could be technical, economic, environmental or social.
4. **Criteria for success**: The metrics that will be used to measure success.

Requirements say what the design must do; constraints say what limits how you can do it; criteria for success say how you will know it worked.

#### Methods for problem definition

1. **User research**: Interviewing, observing and surveying potential users to understand their needs, wants and pain points.
2. **Benchmarking**: Studying existing products or solutions that address similar problems, to identify their strengths and weaknesses.
3. **Mind mapping**: A visual brainstorming technique that helps you organise your thoughts and identify key aspects of the problem.
4. **SCAMPER**: A creative problem-solving technique that involves asking questions to stimulate new ideas.

### Concept generation

Here we move from problem definition to potential solutions. It involves brainstorming and exploring various ideas to address the identified needs and constraints.

#### Importance of diverse concepts

- Essential for finding the best possible solution.
- Avoids being limited to conventional solutions or simply improving existing ideas.
- Diversity arises from exploring different functionalities, technologies, materials and design principles.
- Aim for a broad range of concepts, even some that seem unconventional or outlandish at first.

#### Techniques for concept generation

**1. Brainstorming.** Gather individuals (ideally with diverse backgrounds) to freely generate ideas without judgement. Encourage quantity over quality at this stage. Brainwriting and round-robin brainstorming help overcome inhibitions and encourage participation.

**2. Morphological analysis.** Involves identifying the key functional elements of the design and then exploring all possible combinations of their attributes. It ensures a thorough exploration of the design space and can lead to unexpected solutions.

**3. TRIZ (Theory of Inventive Problem Solving).** TRIZ is a Russian acronym. It provides a structured framework for identifying and overcoming design challenges, using a database of 40 inventive principles and contradiction matrices to guide the search for innovative solutions.

The 40 principles of TRIZ, as listed in the lecture:

1. Segmentation: divide the object into independent parts
2. Taking out: take out unnecessary parts or features
3. Local quality: change the local quality of an object
4. Asymmetry: make the object asymmetrical
5. Merging: merge two or more objects
6. Universality: make the object multifunctional
7. Nesting: place one object inside another
8. Counterweight: balance the object
9. Preliminary action: pre-arrange the object to perform a desired function
10. Prior action: perform a prior action to prevent a potential problem
11. Cushioning: cushion objects to reduce impact
12. Composite materials: combine different materials to achieve desired properties
13. Parameter change: change the parameters of an object
14. Parameter variation: vary the parameters of an object
15. Dynamicity: make the object dynamic
16. Partial or excessive action: use partial or excessive action to achieve the desired result
17. Another dimension: move the object into another dimension
18. Mechanical vibration: use vibration to improve or achieve a function
19. Periodic action: make the object perform periodic actions
20. Continuity of useful action: make the object perform useful actions continuously
21. Skipping: skip steps in a process
22. Blessing in disguise: turn a harmful factor into a beneficial one
23. Feedback: use feedback to control the object or process
24. Intermediary: introduce an intermediary object or process
25. Self-service: make the object serve itself
26. Copying: copy useful features from other objects or systems
27. Cheap substitutes: replace expensive parts with cheaper ones
28. Parameter modification: change the parameters of an object or process
29. Mechanical mixture: mix different objects or substances
30. Composite material property change: change the properties of a composite material
31. Porous materials: use porous materials to achieve desired functions
32. Color change: change the color of an object
33. Parameter homogeneity: make the parameters of an object or process uniform
34. Discarding and recovering: discard unnecessary parts and recover them later
35. Parameter change and recovery: change parameters and then recover them
36. Phase change: change the phase of an object or substance
37. Thermal expansion: use thermal expansion to achieve desired functions
38. Strong oxidants: use strong oxidants to achieve desired results
39. Inert atmosphere: use an inert atmosphere to prevent unwanted reactions
40. Composite material substitution: substitute one composite material with another

These principles are only a starting point. The key is to use them creatively and adapt them to your specific problem.

> Two small fixes from your handwritten list: "Taking out" is number 2 (it was written as 6 on that page), and number 20 is "Continuity of useful action" (it was written "Community of useful period"). Also, this list is the lecturer's version. Published TRIZ lists name some principles differently, so for the exam use the lecturer's names.

**4. SCAMPER.** The letters stand for Substitute, Combine, Adapt, Modify (Magnify and Minify), Put to another use, Eliminate, Rearrange/Reverse. It stimulates creative thinking by asking questions about an existing design or concept.

| Letter | What it means | Question to ask | Example |
| --- | --- | --- | --- |
| S: Substitute | Replace parts, materials, people or processes | What can be used instead? | Use a cheaper material than the one now used |
| C: Combine | Merge two or more ideas, objects or functions | What can be combined? | Combine two features of existing products to create something new |
| A: Adapt | Modify an existing idea or object for a new purpose | What can be adapted? | Adapt a technology from one industry to solve a problem in another |
| M: Modify (Magnify and Minify) | Change the size, shape, color or other properties | What can be modified? | Make the product bigger or smaller, change its color or shape |
| P: Put to another use | Find new ways to use existing objects or processes | What else can this be used for? | Use the product in a new and unexpected way |
| E: Eliminate | Remove unnecessary parts, features or processes | What can be eliminated? | Simplify the design by removing unnecessary features |
| R: Rearrange/Reverse | Change the order or arrangement of things | What can be rearranged or reversed? | Change the order of steps in a process, or reverse the direction of something |

**Benefits of SCAMPER:** (i) promotes creative thinking, (ii) easy to use, (iii) encourages collaboration, (iv) improves problem solving.

**Tips for using SCAMPER:** (i) start with a clear problem statement, (ii) don't judge your ideas, (iii) build on other people's ideas, (iv) be persistent.

**5. Biomimicry.** Seeking inspiration from nature's solutions to similar problems.

**6. Design analogy.** Drawing inspiration from existing solutions in other domains and adapting them to your specific problem.

**7. Collective intelligence techniques.** Leverages the power of crowdsourcing and online platforms to gather diverse ideas from a broader community (for example InnoCentive and NineSigma).

### Concept evaluation and refinement (bridge to Lecture 3)

Once concepts are generated, evaluate each one based on the defined criteria. Select the most promising concepts and refine them by identifying potential improvements. This may involve developing sketches, prototypes and so on, to test and validate your concept before finalizing your design.

Factors to consider: (i) feasibility (can it be built with available resources and technology?), (ii) cost (to design, manufacture and maintain), (iii) functionality (does it meet the objectives and requirements?), (iv) safety (for users and the environment), (v) aesthetics.

**Additional tips for concept generation:** (i) focus on the user, (ii) embrace ambiguity, (iii) challenge assumptions, (iv) build on existing knowledge, (v) seek feedback and collaborate. Concept generation is iterative, so be willing to revisit concepts as you get more information and feedback.

## 3. Concept Selection and Concept Refinement

By now concept generation has given us many ideas. Selection (phase 3) picks the best one, and refinement (phase 4) improves the one we picked.

### How to select the best design concept

To select the best design concept, apply and combine these skills:

1. **Evaluation**: the ability to measure and assess the performance and outcomes of the design concepts using various methods and tools.
2. **Comparison**: the ability to identify and analyse the similarities and differences of the design concepts.
3. **Decision-making**: the ability to make a rational and justified choice among the design concepts.
4. **Trade-off analysis**: the ability to balance and optimise the conflicting objectives, requirements and constraints of the design solution.

The four methods below are the tools for doing this.

### Pugh matrix

A method of evaluating and comparing design concepts by using a table that lists the criteria for success and the design concepts, and assigns scores to each design concept based on how well it meets or exceeds the criteria compared to a reference design concept.

**Steps**

1. Define your evaluation criteria (and assign weights to each criterion based on its importance).
2. Identify your design concepts (ideas, basically).
3. Create the matrix: criteria go in the rows, design concepts in the columns. You can add a column for a reference design.
4. Score each concept by comparing it to the reference design for each criterion: +1 is better, 0 is the same, -1 is worse.
5. Analyse the scores.

**Benefits:** (i) ensures you evaluate designs based on what truly matters, (ii) reduces bias and emotional decision-making, (iii) makes the selection process transparent and easy to communicate, (iv) encourages discussion and consensus building.

**Note:** you may need to consider other factors like feasibility, manufacturability and market research to take the final decision.

**Lecture example: a new student backpack** (reference design scores 0 everywhere; weighted total = weight × score added up)

| Criteria | Weight | Minimalist roll-top | Padded backpack | Convertible bag |
| --- | --- | --- | --- | --- |
| Comfort | 2 | +1 | -1 | 0 |
| Capacity | 1 | -1 | +1 | +1 |
| Organisation | 1 | -1 | +1 | +1 |
| Durability | 1 | 0 | +1 | 0 |
| Cost | 0.5 | -1 | +1 | 0 |
| Style | 0.5 | +1 | 0 | +1 |
| **Weighted total** |  | **0** | **1.5** | **2.5** |

The padded backpack and the convertible bag come out ahead of the roll-top. The lecture says you may need more analysis or prototyping before the final decision.

### Kano model

Focuses on understanding user needs and emotions to predict how satisfied they will be with different features or design choices. It classifies user needs into three categories (basic, performance and delight) and plots the design concepts on a graph showing the relationship between user satisfaction and the fulfilment of the user needs.

**Steps**

1. Identify user needs (through research).
2. Categorise the needs into basic, performance and delight:
   - **Basic**: absence causes dissatisfaction, but their presence doesn't necessarily delight users (for a booking app: showing available appointment times).
   - **Performance**: satisfaction increases as their level of fulfilment increases (faster loading times).
   - **Delight**: unexpected features that surprise users, exceed their expectations and create emotional attachment (suggesting appointments from past preferences).
3. Plot the design concepts. The x-axis is the level of fulfilment of each user need, and the y-axis is user satisfaction.
4. Analyse the graph: basic needs give a flat line, performance needs give a rising line, delight needs give a sharp jump.
5. Make informed decisions: choose concepts that fulfil both basic and performance needs while prioritising those with delight features.

**Benefits:** (i) emphasises user emotions, (ii) prioritises features effectively, (iii) identifies opportunities for innovation.

The Kano model is a framework, not a rigid formula. Use it as a guide to understand user preferences.

### Decision matrix

A method of evaluating and comparing design concepts by using a table that lists the criteria for success and the design concepts, and assigns weights to each criterion and scores to each design concept based on how well it meets or exceeds the criterion, and calculates the total score for each design concept by multiplying the weights and the scores.

**Steps**

1. Define criteria and weights (weights indicate relative importance, 5 being most important).
2. List options.
3. Score each option.
4. Calculate total scores (weight × score, added up).
5. Analyse results.

**Benefits:** (i) forces systematic evaluation of multiple factors, (ii) makes the decision-making process clear and understandable, (iii) facilitates discussion and consensus-building among stakeholders, (iv) allows objective comparison of design concepts, (v) acknowledges the importance of different criteria and their relative weights.

**Lecture example: choosing an office location**

| Criteria | Weight | A: Downtown | B: Suburban park | C: Coworking |
| --- | --- | --- | --- | --- |
| Rent cost | 5 | 2 | 4 | 5 |
| Accessibility | 4 | 5 | 3 | 4 |
| Space | 3 | 4 | 5 | 3 |
| Amenities | 2 | 3 | 2 | 5 |
| Neighbourhood | 4 | 4 | 3 | 2 |
| **Total** |  | **64** | **63** | **68** |

> Correction: the lecture gives totals of 58, 55 and 58. Working it out with the lecture's own scores gives A = 10+20+12+6+16 = 64, B = 20+12+15+4+12 = 63 and C = 25+16+9+10+8 = 68. So C (coworking) wins outright, not a tie between A and C.

### Analytical Hierarchy Process (AHP)

A method that uses a hierarchical structure to break the decision problem down into levels of objectives, criteria and alternatives. It assigns priorities to each element using pairwise comparisons and consistency checks, then calculates the overall ranking of the alternatives by combining the priorities. It is best when decisions are complex, with many criteria and perspectives.

**Steps**

1. Define the hierarchy: objective, then criteria, then alternatives.
2. Make pairwise comparisons, i.e. compare each criterion pair within each level, on a 1 to 9 scale (1 = equal importance, 9 = much more important).
3. Check for consistency in your judgements by comparing ratios across different comparisons (a consistency ratio and an eigenvector, by software or by hand).
4. Priority calculation: calculate the relative importance of each element.
5. Perform the overall ranking: combine the priorities of the criteria with the performance score of the alternatives for every criterion, calculate the overall score of each alternative, then choose the alternative with the highest overall score.

**Benefits:** (i) makes complex decisions easier to understand and communicate, (ii) reduces bias and ensures logical decision-making, (iii) provides numerical scores for comparison and ranking, (iv) accommodates multiple stakeholders.

**Lecture example: a fitness tracker.** Objective: the most popular fitness tracker. Criteria: functionality, design, price, brand. Alternatives: minimalist wristband, multi-feature smartwatch, hybrid analog/digital watch. If functionality is 2 times more important than design and the smartwatch is much better on functionality, the smartwatch can come out highest overall even though it costs more, and AHP lets you justify that with evidence.

### How to refine the selected design concept

Basically, improving and optimising the design concept by adding more details and specifications to the system. Apply and combine these skills:

1. **Functional analysis**: identify and describe the functions and subfunctions of the system and their relationships and dependencies.
2. **Structural analysis**: identify and describe the components and subcomponents of the system and their relationships and dependencies.
3. **Integration**: combine and coordinate the functions and components of the system to achieve the desired performance and outcomes.
4. **Optimisation**: maximise or minimise the objectives and criteria of the system.

To refine, use these methods in order:

1. **Functional decomposition**: breaking down the overall function of the design into smaller, more manageable subfunctions. This helps identify key components, interactions and areas for improvement.
2. **Design structure matrix (DSM)**: a visual representation of how different elements of a design interact with each other. It identifies dependencies, potential bottlenecks and chances for modularisation.
3. **Quality Function Deployment (QFD)**: translates customer needs and expectations into specific design requirements, and makes sure design changes align with customer needs and priorities.

**Using them together:** (1) start with functional decomposition, (2) create a DSM, (3) identify potential improvements (simplify, modularise or enhance), (4) apply QFD, (5) iterate and refine.

**Lecture example: a collapsible water bottle**

| Method | What it shows for the bottle |
| --- | --- |
| Functional decomposition | Contain liquid (body, cap, seal); provide drinking access (mouthpiece, lid, valve); collapse for storage (flexible material, folding mechanism); maintain shape (ribs, supports) |
| DSM | Body and cap must fit together; valve and mouthpiece control flow; folding mechanism and structural elements must keep shape while collapsing |
| QFD | Leakproof design (high priority need), easy-to-clean materials (medium), attractive design (low) |

Putting it together: decomposition shows the folding mechanism is complex and prone to failure, the DSM shows it interacts with the structural elements, and QFD shows customers care about durability and ease of use. So redesign the folding mechanism to be simpler and more robust while protecting structural integrity.

## 4. Considerations of Good Design

The earlier sections were about the process. This one is about what a good design must get right, whatever the product is. Design considerations differ from problem to problem, but they fall into three broad groups:

1. Performance and functional issues
2. Total life cycle issues
3. Regulatory and social issues

### A. Performance and functional issues (achievement of performance requirements)

Performance requirements (PR) include seven design considerations: functional performance, behaviour performance, environmental performance, aesthetic performance, human factors engineering (HFE), manufacturing technology, and cost and economy.

**1. Functional performance requirement.** A major and most important design consideration is its function. The functional requirement asks: "Is the system operational for what it was originated for?" It is divided into:

- **Primary functional performance**: the main job the design must do.
- **Complementary functional performance**: the supporting qualities around that job.

Example: a screw jack designed to lift a car of up to 300 kg. The primary function is to lift the required 300 kg load up to a height of 18 inches (so the measures are the load and the height). The complementary performance includes useful life, reliability, robustness in service conditions, less muscle power to lift and less fatigue for the operator.

Functional requirements depend on factors like: (i) form, shape and size, (ii) surface finish, (iii) material and their properties, (iv) manufacturing processes involved, (v) features (specific physical attributes).

**2. Behaviour performance requirements.** How well does it perform under real conditions? For the screw jack: ease of operation, safety while operating, noise level and maintenance.

**3. Environmental performance requirements.** As important as economic considerations. Two aspects:

- **Green design**: how the product will behave with respect to maintaining a safe, clean and healthy environment. It started because of government regulations but over time became standard design practice.
- **Service conditions**: the conditions and real situation under which the product must operate, such as temperature limits, humidity, corrosive conditions, dirt, dust, vibration and noise. They must be predicted and considered in the design.

**4. Aesthetic performance requirements.** The sense of the beautifulness: how the product appears to a customer. It involves shape, colour, surface quality and visual appearance. It is the responsibility of the industrial designer (an applied artist), not the engineering designer, but it should be part of the initial design concept.

**5. Human factors engineering (HFE) requirements.** Ensures that the design can be operated efficiently by humans. It involves: (i) ergonomics and biomechanics, (ii) engineering psychology, (iii) physiological and anthropometric data, (iv) human muscle power and response times.

**6. Manufacturing technology.** Must be considered at the initial level, and closely integrated with product design. Limitations include: (i) the manufacturing processes that can be used, (ii) material availability, (iii) equipment availability within the company.

**7. Cost and economy.** A key design requirement: every design must be economic, and projects can be rejected because of unfavourable initial cost estimates. Total cost may include development cost, initial product cost, life cycle cost, tooling cost, infrastructure cost and return on investment (ROI).

### B. Total life cycle

The total life cycle (TLC) of a component starts with an idea of a need and ends with the retirement or dumping of the product. The phases:

1. Mining, drilling or harvesting of natural material (e.g. mineral, oil, cotton)
2. Extract and refine raw materials (e.g. coal, iron ore, sand, wood)
3. Processing into finished engineering material (e.g. aluminium sheets, alloys, plastics)
4. Designing and manufacturing of the part
5. Performance, service or use of the part
6. Wears out, becomes obsolete (end of life)
7. Recycle or dispose of the part (returns the material to the earth)

Total life cycle design considerations are: material selection, material and energy conservation, durability and recycling.

**Sustainable material life cycle.** A combination of the natural (biological) life cycle and the industrial (product) life cycle. Today the industrial product life cycle is considered bad, while the biological one is good. So the idea is to redesign things so they don't poison the environment, which needs a comprehensive analysis of the material life cycle, including the product's impact on the environment and all living things.

**Limitations of the sustainable material life cycle**

1. Switching from conventional materials to lightweight eco-friendly materials needs a change of the whole set-up and tools.
2. Switching involves huge investment and money.

Even so, for a better future we need design sustainability, because what we use is borrowed from future generations.

**1. Material selection.** A good design requires good material selection. The first step is the assessment of the service conditions. Then selection depends on the properties of the material, the manufacturing process to be used, the service conditions and the service-time performance. Material properties to consider: static yield strength, fatigue, creep, toughness, ductility and corrosion resistance.

**2. Material conservation.** A good design must conform to material and energy conservation along with environmental protection, which also reduces material and energy cost.

**3. Durability.** A good design permits maximum durability at minimum cost. Durability is the amount of useful life before retirement of the product.

**4. Recycling.** A good design allows recycling of waste material, which restarts the total life cycle of the material. Example: aluminium beverage cans used for cold drinks must be recyclable from the early stage of design.

### C. Regulatory and social issues

These are the rules and the society side of design: specifications and standards, codes of ethics, public health and safety, human factor engineering, and behaviour of the end-user.

**1. Specifications and standards.** A good and successful design must conform to the specifications and standards. Societies like ASME, ASTM and IEEE provide design standards. Standards are a voluntary agreement among users (consumers) and producers (industrialists), and they often represent only the minimum. A company can set its own standards if it needs more. A good design must conform to all legal requirements and design codes.

**2. Codes of ethics.** Require the engineer to protect public health and safety.

**3. Public health and safety.** Agencies put direct constraints on the designer in the interests of protecting security, health and safety. Examples: Occupational Safety and Health Administration (OSHA), Environmental Protection Agency (EPA), also the Consumer Product Safety Commission (CPSC) and the Department of Homeland Security (DHS). If these aspects cannot be covered by the functional design, then warnings must always be attached to the product, and user manuals must ensure safe operating procedures and conditions.

**4. Human factor engineering.** A good design must ensure it can be operated efficiently and safely by human beings, using the knowledge of ergonomics, biomechanics and engineering psychology.

**5. Behaviour of the end-user.** Important. Focusing only on materials deals with about 5% of the problem; the other 95% depends on the behaviour of the end-user. Example: for a hair-drier, about 95% of the carbon footprint comes from the electricity the user spends drying hair over the years, and only about 5% from the materials and manufacturing stage.

## 5. Term Paper Worked Example: Student Study Desk

This is the example from your handwritten notes. It walks through the design phases from section 1 on one real problem, so use it as a model whenever an exam question says "illustrate with an engineering example".

**Term paper task:** "Generate any problem and solve it using the engineering design process."

**Problem:** Improving the ergonomics and organisation of a student's study desk.

### Phase 1: Problem definition

- **Objective:** Create a desk accessory that reduces strain while reading and keeps the student's desk organised.
- **Requirements:** (i) must hold the laptop and notes at eye level, (ii) should be able to hold at least 4 textbooks, (iii) should have a dedicated space for stationery.
- **Constraints:** (i) should cost less than ₦20,000 to manufacture, (ii) should be lightweight, (iii) should be eco-friendly.
- **Criteria for success:** (i) should measure a 20% reduction in user-reported neck strain, (ii) should achieve a "high" rating in satisfaction surveys.

### Phase 2: Concept generation

We start by brainstorming. Ideas include: (i) a foldable laptop stand with built-in drawers, (ii) a rotating stand for books, (iii) a standing desk converter.

**Applying the principles of TRIZ**

- **Segmentation:** divide the organiser into modules, one part for the laptop and the other for the stationery, for flexibility.
- **Dynamicity:** make the organiser flexible and adaptable to perform its function. Give the stationery holders magnets or sliding rails so the user can configure the layout depending on whether they are typing, drawing and so on. Make the accessory collapsible so it can fold or retract when not in use.
- **Universality:** make it serve another function as well, for example let it have a cup holder.

**Then SCAMPER**

- **Combine** a desk lamp with a wireless charging pad.
- **Modify** its base to include a hidden storage compartment.

### Phase 3: Concept selection

The aim is finding the most balanced solution. The best method for this is the decision matrix. Here, each score is multiplied by the criterion's weight.

| Criteria | Weight | Concept A | Concept B | Concept C |
| --- | --- | --- | --- | --- |
| Cost | 5 | 3 (15) | 4 (20) | 4 (20) |
| Ergonomics | 4 | 2 (8) | 3 (12) | 2 (8) |
| Sustainability | 3 | 2 (6) | 2 (6) | 3 (9) |
| Size | 2 | 3 (6) | 3 (6) | 2 (4) |
| **Total score** |  | **35** | **44** | **41** |

Concept B has the highest total, so Concept B is chosen. (Your note left the reason after "Concept B due to..." unfinished, so add it in your own words.)

### Phase 4: Concept refinement

**Functional decomposition:** optimise the selected stand using it.

- **Sub-function 1, support laptop:** refine it to include adjustable height notches (the angles written in your notes are hard to read, so check them) to cater to different user heights.
- **Sub-function 2, organise stationery:** add magnetic strips to the side unit to keep paperclips and metal rulers in place.

**Design structure matrix:** we don't need this here, because there are no bottlenecks.

**Quality function deployment:** ensure the foldable feature is prioritised because user research showed that students value portability.

### Phase 5: Detailed design

- **Dimensions:** length 50 cm, width 10 cm, thickness 5 cm; adjustable heights of 10 cm, 15 cm and 25 cm (check these against your page, the handwriting is small).
- **Materials:** 3-ply bamboo, 12 mm thick carbonised bamboo, and a surface finish of water-resistant matte varnish. Your list also has an item that looks like "iron"; confirm it.
- **Components:** (i) hinges: 2 heavy-duty stainless steel friction hinges, (ii) fasteners: M4 steel screws.
- **Interfaces:** safe edges.
- **Functions:** (i) laptop stand, (ii) stationery organiser.

### Phase 6: Prototyping

Build a low-fidelity model using cardboard first, then move to a high-fidelity 3D printed or CNC cut version to test stability.

### Phase 7: Testing and evaluation

Your handwritten notes stop at phase 6 on the last page, so phase 7 is missing. Section 7 of these notes has a testing protocol you can adapt for it, using the success criteria above (20% less neck strain, high satisfaction rating).

## 6. Exam Topics Not Covered in Your Notes

The exam asks about several topics that are not in your handwritten notes or the lecture pdfs: requirements, testing protocols, FMEA, engineering drawings, polymers, DFMA and material choice. I wrote this section from general engineering knowledge in the same plain style, so treat it as a first draft and check it against any slides your lecturer gave on these. Each part links back to the sections above.

### 6.1 Requirements and requirement writing

In section 2, requirements are the essential features and functions a design must have. Writing them down clearly is what turns a vague need into something you can design, build and test against.

**Types of requirements**

| Type | What it states | Example (bicycle) | How it influences design decisions |
| --- | --- | --- | --- |
| Functional | What the system must do | Must carry a rider of up to 100 kg | Decides frame size, material and wall thickness |
| Performance (non-functional) | How well it must do it | Frame mass under 2 kg | Pushes the choice toward light materials |
| User or stakeholder | What users and stakeholders need or expect | Comfortable for 2-hour rides | Decides geometry, saddle and handlebar position |
| Constraints (technical, economic, social, environmental) | Limits on design choices | Retail price under ₦150,000 | Rules out expensive materials and processes |
| Interface | How it connects to other systems or parts | Fits standard wheels and brakes | Fixes dimensions at connection points |
| Safety and regulatory | Laws, codes and standards to meet | Passes frame fatigue standards | Adds safety factors and required tests |
| Environmental or service conditions | Conditions it must survive | Rain, dust, temperature range | Decides coating and corrosion protection |
| Manufacturing | What the factory can actually do | Must use welding available locally | Limits shape and process |

**Why well-defined requirements matter**

- **Design accuracy:** the team designs the right thing, because everyone reads the requirement the same way.
- **Project success:** you can check each requirement at the end, so "done" has a clear meaning.
- **Risk reduction:** gaps and conflicts are found on paper, where they are cheap to fix, instead of during testing, where they are expensive.
- **Stakeholder satisfaction:** the requirements record what stakeholders asked for, so the result matches what they expected and there are fewer arguments later.

A good requirement is clear, measurable, testable, feasible, consistent with the others and traceable to a user need. "The stand should be strong" is weak; "the stand must hold at least 4 textbooks" is good (it is straight from the study desk example).

### 6.2 Why design and prototyping are complex

These are the factors behind the challenges listed in section 1:

1. Problems are ill-defined and change as you learn more.
2. Objectives, requirements and constraints are many and often conflict (for example light but strong, strong but cheap).
3. Many stakeholders want different things.
4. There are many possible concepts, each with trade-offs, risks and uncertainties.
5. The parts of a system depend on each other, so a change in one affects the others (this is what the design structure matrix shows).
6. Several disciplines are involved (mechanical, electrical, software, materials, human factors).
7. Uncertainty about performance in realistic conditions, only found out by prototyping and testing.
8. Limits on resources, time and cost.
9. Rules to follow: standards, regulations, ethics and safety.

### 6.3 The design phases with inputs, outputs and decision criteria

| Phase | Input | Output | Decision-making criteria | Engineering example (study desk stand) |
| --- | --- | --- | --- | --- |
| Problem definition | A need, user research, benchmarking | Objectives, requirements, constraints, criteria for success | Is the problem clear, complete and agreed by stakeholders? | Reduce strain, hold 4 textbooks, cost under ₦20,000 |
| Concept generation | The problem definition | Many diverse concepts | Do the concepts satisfy the problem definition? Is there enough variety? | Foldable stand with drawers, rotating book stand, standing desk converter |
| Concept selection | The concepts and criteria for success | One chosen concept | Weighted score against criteria such as cost, ergonomics, sustainability | Decision matrix picks Concept B (44) |
| Concept refinement | The chosen concept | Improved concept with subfunctions and interactions clear | Does it meet customer needs and have no bottlenecks? | Adjustable height notches, magnetic strips |
| Detailed design | The refined concept | Dimensions, materials, components, interfaces, functions | Meets specifications, standards, cost and manufacturability | Bamboo, hinges, M4 screws, safe edges |
| Prototyping | The detailed design | A physical or virtual model | Is it feasible, functional and usable? | Cardboard model, then 3D printed or CNC cut |
| Testing and evaluation | The prototype | Test data and a decision to release or redesign | Success criteria met? Safe? Users satisfied? | 20% less neck strain, high survey rating |

### 6.4 Applying SCAMPER to improve an existing product: a structured guide

**Systematic steps**

1. Pick the existing product or system and write a clear problem statement (what do you want to improve?).
2. List its parts, functions and users.
3. Go through S, C, A, M, P, E, R one letter at a time and ask the question for each. Write every idea, without judging.
4. Build on each other's ideas (work in a group if you can).
5. Screen the ideas against the criteria for success (cost, feasibility, safety, functionality).
6. Pick the best ideas, sketch or prototype them, test, and repeat if needed.

**Practical tips:** start with a clear problem statement, don't judge ideas early, build on other people's ideas, be persistent, and use the user's complaints as a source of questions.

**Example: improving an ordinary backpack**

| Letter | Question | Idea |
| --- | --- | --- |
| Substitute | What can be used instead? | Recycled fabric instead of virgin nylon |
| Combine | What can be combined? | Add a built-in power bank and charging cable |
| Adapt | What can be adapted? | Use the load-spreading harness of hiking packs |
| Modify | What can be made bigger, smaller or changed? | Slimmer shape, brighter colour for night visibility |
| Put to another use | What else can it be used for? | Converts into a picnic or sitting mat |
| Eliminate | What can be removed? | Remove extra zips and straps to cut weight and cost |
| Rearrange or reverse | What can be rearranged? | Laptop compartment on the back so it is reachable without removing the bag |

### 6.5 Testing protocol (performance and usability)

A test protocol says what is tested, how, what data is recorded and what counts as a pass. Example for the study desk stand from section 5:

| Test | Procedure | Data collected | Success criterion |
| --- | --- | --- | --- |
| Load test | Place 4 textbooks and a laptop on the stand for 24 hours | Deflection, any cracks | No permanent deformation or cracks |
| Stability test | Tilt and push gently at each height setting | Tilt angle at which it tips | Does not tip in normal use |
| Durability (cycle) test | Fold and unfold the hinges many times (for example 1,000 cycles) | Number of cycles before loosening or failure | Hinges still hold position after the test |
| Ergonomic test | Users work for a set time with and without the stand | User-reported neck strain scores | At least 20% reduction in neck strain |
| Usability test | Users set it up and organise stationery without instructions | Time taken, errors, observations | Most users finish without help |
| Safety test | Inspect edges and pinch points | Sharp edges and pinch points found | None found |
| Satisfaction survey | Questionnaire after use | Ratings from 1 to 5 | Average rating "high" (for example 4 or more) |

Record the conditions, the sample of users, the results and any redesign actions.

### 6.6 Failure Mode and Effects Analysis (FMEA)

FMEA is a structured way to ask, for each part of a product: how could it fail, what would happen if it did, and what can we do about it. It is done early in product development, before tooling and production, because fixing problems then is cheap. It links to the risk side of section 6.2.

**Steps:** (1) list the parts and their functions, (2) list the possible failure modes, (3) list the effects of each, (4) rate severity (S), occurrence (O) and detection (D), usually 1 to 10, (5) calculate the risk priority number, RPN = S × O × D, (6) act first on the highest RPN, (7) re-rate after the fix.

**Retractable ballpoint pen: two examples**

| Failure mode | Effect | Action the design team might take |
| --- | --- | --- |
| The spring weakens or breaks | The tip does not retract, the pen leaks into pockets or the user cannot click it | Use a better spring material and wire size, and run click-cycle testing (for example tens of thousands of clicks) |
| The click cam or plunger wears or cracks | The tip will not lock out, or locks out and slips back while writing | Use a harder, wear-resistant plastic, tighten tolerances and test for wear |

### 6.7 Why engineering drawings still matter in the age of 3D CAD

A 3D model shows the shape, but a manufacturer needs to know exactly what to make, how accurately, and how to check it. Drawings are also standardised documents that everyone reads the same way, and often a legal and contractual record between designer and manufacturer. Rapid prototyping can work from a model, but production usually needs a drawing.

Information a drawing conveys that a 3D file alone may not state explicitly:

- Dimensions with **tolerances** and geometric tolerances (GD&T), which say how much variation is allowed.
- **Material** and its grade or specification, and heat treatment.
- **Surface finish** and coatings.
- **Fits** between mating parts.
- Which dimensions are critical to inspect, and inspection or quality requirements.
- Assembly notes, the bill of materials and the standards used.
- Revision and approval information, scale and units.

### 6.8 Thermoplastics and thermosetting polymers

| Property | Thermoplastics | Thermosetting polymers (thermosets) |
| --- | --- | --- |
| What happens with heat | Soften when heated and harden when cooled, and can be reheated and reshaped many times | Cure once (set) permanently and cannot be remelted; they char or burn if overheated |
| Structure | Long chains held by weak forces | Chains linked by strong cross-links, forming a rigid network |
| Typical properties | Flexible to tough, easier to process, recyclable | Hard, rigid, good heat and chemical resistance, dimensionally stable, harder to recycle |
| Typical applications | Packaging, pipes, casings, consumer goods, 3D printing filament | Electrical parts, circuit boards, adhesives, heat-resistant handles, composites |
| Examples | Water bottles (PET); PVC pipes | Circuit boards (epoxy resin); pot handles or electrical sockets (phenolic, also called Bakelite) |

### 6.9 Design for Manufacturing and Assembly (DFMA): four key principles

Sources word these differently, so check which four your lecturer used. A common set:

1. **Minimise the number of parts.** Fewer parts means fewer things to make, store, assemble and fail. Influence: combine parts into one moulded part, or use snap fits instead of screws.
2. **Standardise parts and materials.** Use off-the-shelf components, fasteners and standard sizes. Influence: lower cost and easier supply and repair.
3. **Design for ease of fabrication.** Use simple shapes, processes and generous tolerances the factory can achieve. Influence: avoids deep holes, undercuts and tight tolerances that raise cost.
4. **Design for ease of assembly.** Parts should be easy to handle, self-locating and assembled from one direction, and impossible to assemble wrongly. Influence: faster, cheaper and more reliable assembly.

### 6.10 Material and process for a lightweight, high-strength bicycle frame

A frame needs low mass for its strength and stiffness, resistance to fatigue (the load repeats with every pedal stroke) and corrosion resistance, at a cost that suits the market.

| Option | Properties | Process | Fit |
| --- | --- | --- | --- |
| Aluminium alloy (for example 6061-T6) | Roughly one third the density of steel, good strength after heat treatment, corrosion resistant, easy to work | Extruded or hydroformed tubes, TIG welded, then heat treated | Best balance for medium to high volume and moderate cost |
| Carbon fibre composite | Very high strength and stiffness for its weight, can be shaped and tuned | Layup of prepreg sheets in a mould, then cured | Best performance but high cost and labour, so for low volume or premium bikes |
| Chromoly steel | Tough and fatigue resistant, but heavier | Tube cutting and welding or brazing | Good for repair and low-cost tooling |
| Titanium | Light, strong and corrosion resistant | Welded in inert gas | Very expensive, so a niche market |

**Recommendation:** for a lightweight, high-strength frame produced in medium to high volume at a reasonable cost, choose aluminium alloy with hydroformed tubes and welding followed by heat treatment. If the target is a premium, low-volume racing frame and cost is less important, choose carbon fibre. Justify it with the three factors the question names: material properties (strength-to-weight, fatigue, corrosion), production volume (welding suits volume, hand layup does not) and cost (raw material plus labour).

## 7. Question Bank (2025/2026 First Semester Exam)

The paper is the same one in all three files you sent (the two PQ files and the exam file). Instructions: attempt any four questions, time allowed 2 hours, credit for orderly presentation. The questions are left unsolved, each tagged with the section of these notes that answers it.

| Q | Part | Question | Marks | Notes section |
| --- | --- | --- | --- | --- |
| 1 | a | Effective problem definition is fundamental to successful engineering design. Analyse four (4) established methods used for problem definition. | 6 | 2 |
| 1 | b | Illustrate the SCAMPER technique as a creative problem-solving tool in engineering design. | 5 | 2, 6.4 |
| 1 | c | Evaluate its benefits in enhancing innovation, idea generation and design improvement. Support your answer with practical engineering applications. | 5 | 2, 6.4 |
| 2 | a | Critically examine the importance of engineering design and prototyping in modern engineering practice. Evaluate the major challenges encountered during the design and prototyping stages. | 7 | 1, 6.2 |
| 2 | b | Design a structured guide on how to effectively apply the SCAMPER technique in engineering design and prototyping. Include practical tips, systematic steps and examples demonstrating how SCAMPER can be used to improve an existing product or system. | 8 | 2, 6.4 |
| 3 | a | Engineering design and prototyping are inherently complex activities. Analyse the factors that contribute to this complexity. | 7 | 1, 6.2 |
| 3 | b | Evaluate the importance of requirement writing in engineering design and prototyping. In your answer, explain how well-defined requirements influence design accuracy, project success, risk reduction and stakeholder satisfaction. Illustrate your discussion with relevant engineering examples. | 8 | 6.1 |
| 4 | a | Describe the standard phases of the engineering design process. Illustrate each phase with appropriate engineering examples, highlighting inputs, outputs and decision-making criteria. | 6 | 1, 5, 6.3 |
| 4 | b | Interpret the different types of requirements used in engineering design and prototyping. Provide appropriate examples to demonstrate how each type influences design decisions. | 9 | 6.1 |
| 5 | a | Design a comprehensive testing protocol to evaluate its performance and usability. The protocol should detail the specific tests to be conducted, data collected and the success criteria used. | 5 | 6.5 |
| 5 | b | Justify the purpose and application of Failure Mode and Effects Analysis (FMEA) in the product development cycle. Using a simple product, such as a retractable ballpoint pen, provide two (2) examples of potential failure modes, their effects and the actions a design team might take to mitigate them. | 5 | 6.6 |
| 5 | c | Support why detailed and accurate engineering drawing is still a vital skill in the age of 3D CAD and rapid prototyping. What critical information do these drawings convey that a 3D model file alone may not explicitly communicate for manufacturing? | 5 | 6.7 |
| 6 | a | Compare and contrast the properties and typical applications of thermoplastics and thermosetting polymers in product design. Provide two (2) examples of products for each material type. | 5 | 6.8 |
| 6 | b | Evaluate the four (4) key principles of Design for Manufacturing and Assembly (DFMA). For each principle, describe how its application influences the final design of a product. | 5 | 6.9 |
| 6 | c | In designing a lightweight, high-strength bicycle frame, recommend a suitable material and a corresponding manufacturing process for this application. Justify your choices in detail, considering factors such as material properties, production volume and cost. | 5 | 6.10 |

Two things to note. First, Q5a says "its performance and usability" but doesn't name a product, so choose one (the study desk stand from section 5 works) and say so at the start of your answer. Second, Q1's marks add up to 16 while every other question is 15, which may be a misprint on the paper.
