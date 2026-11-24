---
id: 8d4b2274-8c7e-400a-a763-b30362a9b782
---

# Requirements and Requirement Writing

A requirement is an essential feature or function a design must have, and requirement writing is putting it down clearly enough to design, build and test against.

## Before you start
<!-- bite: 70b15a45-1074-43f6-95dd-ab287e767707 -->

You should know the four parts of a problem definition ([[engineering-design-and-prototyping/04-problem-definition|lesson 04]]).

After this lesson you will be able to:

1. name eight types of requirements and say how each one influences design decisions;
2. explain how well-defined requirements affect design accuracy, project success, risk reduction and stakeholder satisfaction;
3. tell a good requirement from a weak one.

## What requirement writing is
<!-- bite: 410f3dc1-ee74-438a-87dd-bef24a4b6f9c -->

In lesson 04, requirements were the essential features and functions a design must have. Writing them down clearly is what turns a vague need into something you can design, build and test against.

Think about it like this. "Make me a nice bicycle" can mean a hundred things. "The frame must carry a rider of up to 100 kg" means one thing, and you can test it.

There isn't just one kind of requirement. Some say what the design must do, some say how well, some say what it must survive. Let's go through the types, all on one example: a bicycle.

## Types of requirements: what it does and for whom
<!-- bite: 543e932a-5eb7-4803-8cb5-c0aedefdcbde -->

| Type | What it states | Example (bicycle) | How it influences design decisions |
| --- | --- | --- | --- |
| Functional | What the system must do | Must carry a rider of up to 100 kg | Decides frame size, material and wall thickness |
| Performance (non-functional) | How well it must do it | Frame mass under 2 kg | Pushes the choice toward light materials |
| User or stakeholder | What users and stakeholders need or expect | Comfortable for 2-hour rides | Decides geometry, saddle and handlebar position |
| Constraints (technical, economic, social, environmental) | Limits on design choices | Retail price under ₦150,000 | Rules out expensive materials and processes |

## Types of requirements: what it must fit and survive
<!-- bite: b581ecad-cdff-417f-b193-a3169d77b3f8 -->

| Type | What it states | Example (bicycle) | How it influences design decisions |
| --- | --- | --- | --- |
| Interface | How it connects to other systems or parts | Fits standard wheels and brakes | Fixes dimensions at connection points |
| Safety and regulatory | Laws, codes and standards to meet | Passes frame fatigue standards | Adds safety factors and required tests |
| Environmental or service conditions | Conditions it must survive | Rain, dust, temperature range | Decides coating and corrosion protection |
| Manufacturing | What the factory can actually do | Must use welding available locally | Limits shape and process |

See how every type pushes a decision? That's the point of the last column, and it's what an exam wants when it says "show how each type influences design decisions".

## Why well-defined requirements matter
<!-- bite: 4b2b5dbc-21a7-45b4-a02c-adc396f4f0a5 -->

Now we know the types, why does writing them well matter so much?

- **Design accuracy:** the team designs the right thing, because everyone reads the requirement the same way.
- **Project success:** you can check each requirement at the end, so "done" has a clear meaning.
- **Risk reduction:** gaps and conflicts are found on paper, where they are cheap to fix, instead of during testing, where they are expensive.
- **Stakeholder satisfaction:** the requirements record what stakeholders asked for, so the result matches what they expected and there are fewer arguments later.

Imagine the bicycle requirement just said "light". The frame team makes it 3 kg and calls it light; the customer wanted under 2 kg. Nobody finds out until the bike is built. That is all four points failing at once.

## What makes a good requirement
<!-- bite: 3180ff6f-5646-4dfb-8dab-046e559067ee -->

A good requirement is:

1. **Clear**: only one way to read it.
2. **Measurable**: it has a number or a yes/no you can check.
3. **Testable**: you can design a test that passes or fails it.
4. **Feasible**: it can actually be done with the money, time and technology you have.
5. **Consistent** with the other requirements: it doesn't contradict them.
6. **Traceable** to a user need: you can say which need it came from.

"The stand should be strong" is weak; "the stand must hold at least 4 textbooks" is good (it comes from the study desk example in lesson 34).

Writing one requirement well is the first skill. A real product has hundreds, so the next lesson covers the whole process of finding, checking and tracking them.

## Common pitfalls
<!-- bite: f490ab78-a2fa-460f-9788-a2f0619fe7eb -->

1. **Mixing up functional and performance requirements.** Functional is *what* it does (carries a rider). Performance is *how well* (under 2 kg, in under 5 seconds).
2. **Vague words.** "Strong", "light", "user-friendly" and "fast" are weak until they get a number.
3. **Writing a solution as a requirement.** "Must use carbon fibre" picks the answer before concept generation. Write the need ("frame mass under 2 kg") and let the design choose.

## Check your understanding
<!-- bite: e363adef-2ac6-4b4c-a582-da7ea4c01702 -->

Try each one before you open the answer.

1. <!-- q: mcq id="1a7c93e0" -->
   A kettle requirement says: "Must boil 1 litre of water in under 4 minutes." What type of requirement is this?

   - [ ] Functional
   - [x] Performance
   - [ ] Interface

   <details><summary>Answer</summary>

   Performance: it says how well the kettle does its job. "Must boil water" alone would be functional.

   </details>

2. <!-- q: mcq id="e08b4f16" -->
   A phone charger requirement says: "Must plug into a standard USB-C port." What type is this?

   - [ ] Safety and regulatory
   - [x] Interface
   - [ ] Manufacturing

   <details><summary>Answer</summary>

   Interface: it says how the product connects to another system.

   </details>

3. <!-- q: mcq id="7f25d8c1" -->
   Which of these requirements are well written? Choose all that apply.

   - [ ] The chair should be comfortable
   - [x] The chair must support a load of 150 kg without permanent deformation
   - [x] The chair seat must be 450 mm above the floor
   - [ ] The chair should be modern-looking and strong

   <details><summary>Answer</summary>

   The second and third. They are clear, measurable and testable. "Comfortable", "modern-looking" and "strong" have no number and can be read many ways.

   </details>

4. <!-- q: open id="3c96a05b" -->
   Explain how well-defined requirements reduce risk in a project. Use an engineering example.

   <details><summary>Answer</summary>

   Clear requirements let gaps and conflicts be found on paper, where they are cheap to fix, instead of during testing or after release, where they are expensive. For example, if a water pump's requirement says "must deliver 20 litres per minute at a 10 m head", the team can check the motor choice on paper. A vague "must be powerful" would only be found to be wrong when the built pump fails to reach the tank.

   </details>

5. <!-- q: open id="b4d2e87a" -->
   Rewrite this weak requirement so it is good: "The school bag should be light."

   <details><summary>Answer</summary>

   For example: "The empty school bag must weigh no more than 800 g." Any version works if it is clear, measurable and testable.

   </details>

## Before moving on
<!-- bite: db0468fb-1644-4f82-80c5-6e39acbcef9b -->

You can name eight types of requirements, show how each influences a design decision, and explain why well-defined requirements matter. **Next:** [[engineering-design-and-prototyping/07-requirements-engineering|07 — Requirements Engineering]]: the whole process of finding, agreeing, checking and tracking requirements.

## Related
<!-- bite: c79720ca-9b65-4266-9c1a-2e686ec33ce0 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-engineering/02-requirements|Requirements (Systems Engineering)]]: tracing each requirement through a large system.

## About this lesson
<!-- bite: add99c35-db58-46e0-a301-acc33a2d5679 -->

**Level:** Beginner. **Covers:** the types of requirements with a bicycle example, why well-defined requirements matter (design accuracy, project success, risk reduction, stakeholder satisfaction), and what makes a requirement good.

**Where it sits:** lesson 06 of 36, in part 2 (defining the problem).

**Source:** written for the SSG 532 exam from general engineering knowledge. It is not in the lecture notes, so check it against any slides the lecturer gave.
