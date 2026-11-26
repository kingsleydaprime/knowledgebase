---
id: 9c7f2d52-eadd-43a4-8920-2d2d631d2d56
---

# Methodology and Experiment Design

Methodology is the exact plan for how you'll collect your data, designed so that the result can only be explained by the thing you're testing.

## Before you start
<!-- bite: 1e85b9cc-4655-4568-9aa8-e98c41b98bf6 -->

Read [[research/04-research-questions-and-hypotheses|Research Questions and Hypotheses]] first, and have your dated `plan.md` from its steps: your question, metrics, variables, confounds and hypothesis. This lesson turns that plan into a procedure you can follow every day without thinking.

After this lesson you will be able to:

1. design a fair comparison, where the only thing that differs is what you're testing;
2. choose baselines, including the simple guesses your result must beat;
3. give every option you compare the same effort;
4. name the four kinds of validity and write down the threats to your own study;
5. set up your instruments and a data sheet, and run a short pilot before the real study.

## What methodology is
<!-- bite: e374a59b-5839-4d3e-b8a3-deb631abf0cf -->

A good question can still die here. If the way you collect data is unfair or sloppy, the result means nothing, however carefully you analyse it, and a reviewer will spot it in one read. This is where most weak papers are weak.

**Methodology** is the answer to "how exactly did you get these numbers?": what you measured, with what, when, how often, and against what. Written well, it lets a stranger repeat your study and get the same answer.

## Where we stopped
<!-- bite: 66ba361d-2d3a-4759-9c66-2c87b94edab5 -->

Your `plan.md` says what to measure: for the weather study, each app's rain hit rate and average temperature error, over four weeks, with the hypothesis that each app beats "tomorrow will be like today". Now you'll decide exactly *how* to measure it, try it for three days, and start collecting for real.

## The kid version
<!-- bite: 1108c4be-f3a7-4332-8c9c-f7d42ea7f746 -->

You made a new paper plane and think it flies farther than your old one. Here's how *not* to test it: throw the new one hard, indoors, and the old one gently, outside, into the wind. If the new one wins, you've learned nothing: was it the design, or the throw, or the wind?

The fair way: throw **both planes the same way, from the same spot, on the same day, many times each**, and compare the averages. Now the design is the only thing that's different, so if the new plane wins, the design did it.

**Where the analogy stops working.** You can throw a plane fifty times in an afternoon. Some studies only get one chance a day, like the weather study, so every day of data is precious and a mistake in the method costs you days.

## A fair comparison
<!-- bite: 2f8175a1-75d4-4b83-bff5-95258bff4b91 -->

The rule is: **change only what you're testing, and keep everything else the same.** In the weather study, that decides the schedule:

![Two ways to schedule the weather study over four weeks. Top, unfair: app A is read in week 1, app B in week 2 and app C in week 3, so each app faces different weather and a stormy week can make one app look bad. Bottom, fair: all three apps are read every evening for all four weeks, in a shuffled order, so every app faces exactly the same weather and the only difference left is the app](images/rs-same-days.svg)

Read all three apps every evening, so they all face the same weather. Some things you can't hold perfectly still: if you always read app A first, app C is always read a minute or two later. So **shuffle the order** each evening (roll a die, or draw names from a cup). Shuffling is called **randomising**, and it stops a small difference from always favouring the same side.

## Baselines: something to beat
<!-- bite: 48796724-9fa4-45b8-b126-96583230c962 -->

"App B was right 79% of the time." Is that good? You can't tell. If it rains nearly every day, an app that always says "rain" might score 79% too. A number means something only next to a **baseline**: something to compare it with.

There are two kinds:

1. **Simple baselines** are the cheapest guesses that could work: always give the most common answer, guess at random, or say tomorrow will be like today. Your result must beat these, or it's worthless.
2. **Prior-work baselines** are the best results already published, which your literature review found. Beating these is what makes a result new.

Reviewers reject papers for missing or weak baselines more than for almost anything else.

## The weather study's baselines
<!-- bite: 19a2b34b-0d5a-43f9-9594-fea912eef2fb -->

The weather study has two simple baselines, and both come free from data you're already collecting: **always say "rain"**, and **"tomorrow will be like today"**. Here's an *example* of what four weeks might look like (made-up numbers, not real results):

![An example of four weeks of results, 28 days, compared with two simple baselines. Always saying rain is right on the 16 rainy days, 57 percent. Guessing tomorrow will be like today is right on 17 days, 61 percent. App A is right on 18 days, 64 percent, barely above the guesses. App B is right on 22 days, 79 percent, clearly better. App C is right on 15 days, 54 percent, worse than simply always saying rain. A dashed line marks the best simple guess, 61 percent](images/rs-baselines.svg)

Without the baselines, 64% for app A sounds fine. With them, you can see it barely beats a guess anyone could make, and app C loses to "always rain". That's the finding, and only the baselines reveal it.

## Equal effort for everything
<!-- bite: 2612affb-3793-46dc-8065-b967ace9c767 -->

The most common way studies mislead isn't fraud. It's **unequal effort**: you look after the option you like and leave the others at their defaults. In software, it's tuning your own method's settings for days and running the competitor out of the box. Of course yours wins.

The weather study has its own versions. Reading app B's detailed hourly forecast but only app A's one-line summary. Setting your favourite app to your street and the others to "Lagos". Fixing a missed reading for one app but not the others.

The fix: **give every option the same treatment, and write down how you treated each one**, so a reader can check.

## Ablations: does each part earn its place?
<!-- bite: e3342b85-1bfb-4798-a2be-3e001969161d -->

If your study *builds* something with several parts, there's one more test. Say you build a phone-cooling case with a fan and a gel pad, and phones run 6 °C cooler. Which part did it? Test the case with the fan only, then with the gel pad only. Removing one part at a time and measuring again is called an **ablation**.

If removing the fan changes almost nothing, the fan wasn't doing the work, and it's much better to find that out yourself than from a reviewer. The weather study compares apps rather than building one, so it doesn't need ablations.

## Measuring well
<!-- bite: 0baf71b7-d98d-4ef4-8964-bfe5bf9468a9 -->

Your instruments decide what your numbers really mean. For the weather study:

1. **Rain gauge.** A clean tin or jar with straight sides, in the open, away from roofs and trees. Measure the water's depth with a ruler, in millimetres, every morning at 7 am, then empty it.
2. **Thermometer.** A cheap min/max thermometer, which remembers the day's highest reading. Put it in the shade about 1.5 m off the ground: in the sun it reads several degrees too hot. Read and reset it at 7 am too.
3. **Times.** Apps at 8 pm, instruments at 7 am, every day, the same way.

If you can get daily readings from a weather station near you, use them as well. Two sources that agree give you more confidence than one.

## Four ways a study can be wrong
<!-- bite: 8ea98459-be45-488f-8758-6e414601ea4d -->

**Validity** means your result is what you say it is. There are four kinds, and each is a question to ask of your design:

![The four kinds of validity, each with its question and a threat from the weather study. Internal: is the difference down to the app? Guarded by reading all apps on the same days at the same time. Construct: are you measuring what you mean? Reading the gauge at 7 am means 7 hours of the next day spill into each reading. External: does the result hold beyond your setup? Only one season and one area of Lagos were tested. Statistical: is the difference bigger than luck? Over 28 days, a gap of 2 days may be chance](images/rs-validity.svg)

1. **Internal validity**: is the difference really down to what you changed, or a confound? This is the most important one.
2. **Construct validity**: does your metric measure the thing you care about?
3. **External validity**: does the result hold beyond your exact setup?
4. **Statistical validity**: is the difference bigger than luck?

## Naming your own threats
<!-- bite: aeee5151-b345-4fd9-a654-b4293502481b -->

No study is perfect, so good papers include a short section called **threats to validity** that names the ways their own study could be wrong. It reads as strength, not weakness: it shows you looked.

The weather study's construct threat is a good example. Your 7 am gauge reading holds rain from 7 am yesterday to 7 am today, but the app forecast midnight to midnight. So up to 7 hours of each reading belong to the wrong day. You can't fix it with one tin, but you can name it, and say whether it could favour any app. (It can't: every app is scored against the same readings.)

## Fix your rules before you look
<!-- bite: 6b128f16-78e1-4cd4-99f4-9f873a42a283 -->

Once data starts coming in, it's tempting to adjust: "50% made app B look bad; maybe 40% is a fairer line". Don't. Changing your rules after seeing the data lets you tune the result to what you hoped, often without meaning to. Your thresholds and metrics are in `plan.md`, dated; stick to them, and if you try another rule later, report it as exploratory.

In machine learning the same idea is the **test set**: data you check only once, at the end, and never use to make choices. Letting it influence any choice is called **data leakage**. See [[machine-learning/02-working-with-data/03-train-val-test-splits|train, validation and test splits]].

## How much data is enough?
<!-- bite: 4244049c-b77f-4754-a21f-b470d8d78f35 -->

One week can't tell you much. In the week from the last lesson, an app with a true hit rate of 70% could easily get 4, 5 or 6 days right out of 7 by luck alone. More days shrink the luck. Four weeks is a sensible minimum for one person; two months would be stronger.

The general rule: **repeat your measurement enough times that luck can't explain the difference you're looking for**, and decide how many before you start. Bigger differences need fewer repeats; small ones need many. [[research/06-analyzing-and-interpreting-results|Analysing results]] shows how to check whether your gap is bigger than luck.

## Could a stranger repeat it?
<!-- bite: aaca4a0c-d241-45b3-ab04-4e3c75dbb307 -->

A result nobody can repeat is a story, not a finding. Many published results in psychology, medicine and machine learning failed when others tried to repeat them; this is called the **replication crisis**, and it made **reproducibility** a first-class duty.

For the weather study that means writing down: the three apps and their versions, the location set in each, the exact times, how the gauge and thermometer were made and placed, and the rules for "said rain", "rained" and the error. Keep every raw reading, never only the totals. In software, it means releasing code, data, settings and versions.

Keep asking: *could a careful stranger repeat this from what I've written?*

## In other fields
<!-- bite: c5c542e0-3f6d-4c2d-a5e4-bd97cd7c7ffd -->

The same ideas take different forms:

1. **Machine learning**: several datasets, proper splits, several runs with different random seeds, ablations, released code.
2. **Systems benchmarks**: throw away the warm-up runs, report percentiles such as p95 as well as the average, repeat runs, and state the hardware exactly.
3. **Robotics and hardware**: calibrate your instruments, run many physical trials, and say clearly what was simulated and what was built and measured.

## Step 1: choose your baselines
<!-- bite: ae21b595-a189-4023-aa50-d0ee93ce949c -->

In `plan.md`, add a heading **Method**, and under it **Baselines**. Write at least two simple baselines your result must beat, and how you'll compute each from your data. Add one prior-work baseline from your literature review if there is one (a published figure for forecast accuracy somewhere similar), with its reference.

## Step 2: set up your instruments and data sheet
<!-- bite: abe37736-c811-4eed-a464-5e114554812c -->

Build or get your instruments, and write under **Method** exactly how each is made, placed and read. Then create `data.csv`, one row per app per day, with these columns:

```text
date,app,rain_chance,forecast_high,rain_mm,actual_high,read_at,notes
```

Put `rain_mm` and `actual_high` on the row for the day they describe, even though you read them the next morning. Use `notes` for anything odd: a missed reading, an app update, a storm that knocked the gauge over.

## Step 3: write the procedure
<!-- bite: d9c95db2-ec42-4929-b6e6-69102b8e1bca -->

Under **Method**, write the daily procedure as numbered steps someone else could follow: when you read the apps, how you shuffle the order, what you copy down, when you read the instruments, and what you do about a missed day. Then add **Threats to validity**: at least one threat for each of the four kinds, and what you did about it.

## Step 4: run a three-day pilot
<!-- bite: e9b95cc2-effe-41da-b5df-ed05ccab89d3 -->

Follow your procedure for three days, filling `data.csv` as if it were real. This is a **pilot**: a small trial run to find problems while they're cheap. Expect to find some: an app that changes its forecast after 8 pm, a gauge that overflows, a column you forgot.

Fix every problem in `plan.md`, add a dated line saying what you changed and why, and commit. Then clear the pilot rows (keep a copy) and **start the four weeks**.

## Your project so far
<!-- bite: eb6f35f4-8838-40b0-9816-1dd152f313e0 -->

```text
my-study/
├── journal.md
├── reading-log.md
├── lit-review.md
├── plan.md          ← + Method: baselines, instruments, daily procedure, threats to validity, pilot changes
├── data.csv         ← one row per app per day, filling up
└── pilot-data.csv   ← the three pilot days, kept
```

**Done when** `plan.md` has a Method section a stranger could follow, with two or more baselines and a threat for each kind of validity; the three-day pilot is done and its fixes are written down and dated; and the real four weeks have started. Read [[research/06-analyzing-and-interpreting-results|the next lesson]] while you collect, and do its steps once your data is in.

## Terms used in this lesson
<!-- bite: 3bc8ee04-4726-4d59-a34f-3486d5ea7425 -->

1. **Methodology** is the exact plan for how data is collected: what, with what, when, how often, and against what.
2. **Randomising** means letting chance decide something you can't hold still, like reading order.
3. A **baseline** is something to compare a result against, either a cheap guess or the best published result.
4. An **ablation** removes one part of something you built and measures again, to see if that part mattered.
5. **Validity** means a result is what it claims to be: down to what you changed (internal), measuring what you meant (construct), holding elsewhere (external), and bigger than luck (statistical). A paper's **threats to validity** section names how its study could be wrong.
6. **Reproducibility** means a stranger can repeat the study from what you wrote and get the same answer.
7. A **pilot** is a small trial run of a study, done to find problems before the real thing.

## Common pitfalls and traps
<!-- bite: e6cdcf6f-c2b7-418b-9b8c-47594d9a3cc5 -->

1. **No baseline.** A number on its own can't show anything is good.
2. **Comparing under different conditions.** Different days, places or times for each option, and the comparison is broken.
3. **Unequal effort.** Care for your favourite, defaults for the rest.
4. **Moving the rules mid-study.** Thresholds chosen after seeing the data.
5. **Too few repeats.** One good week, or one lucky run, isn't a finding.
6. **Skipping the pilot.** Finding a broken instrument in week three costs you three weeks.
7. **Keeping only totals.** Without the raw readings, nobody can check or repeat your work.

## Check your understanding
<!-- bite: 181aff58-e9e9-4fcc-8ee0-fd0a07216c87 -->

Try each one before you open the answer.

1. <!-- q: mcq id="a7d30e1c" -->
   A student's model predicts whether a student will pass a course, and it's right 82% of the time. In the data, 80% of students pass. What should worry the student most?

   - [ ] 82% is below 90%
   - [x] Always guessing "pass" would already be right 80% of the time, so the model barely beats a simple baseline
   - [ ] The model should be tested on more courses first
   - [ ] Pass rates can't be predicted

   <details><summary>Answer</summary>

   The simple baseline "always pass" scores 80%. Beating it by 2 points shows the model has learned almost nothing.

   </details>

2. <!-- q: gap id="c51e9b84" answers="70" -->
   In 30 days of a rainy-season study, rain fell on 21 days. An app that always says "rain" would have a hit rate of ___ %.

   <details><summary>Answer</summary>

   It's right on every rainy day and wrong on every dry one: 21 ÷ 30 = 70%.

   </details>

3. <!-- q: mcq id="e2b84f07" -->
   A student compares her new sorting program with a library's. She tries 20 settings for hers and keeps the fastest, and runs the library's with its default settings. What's wrong?

   - [ ] Sorting speed isn't a valid metric
   - [ ] She should have used 40 settings
   - [x] Unequal effort: the library got no tuning, so her win may just be the tuning
   - [ ] Nothing, as long as she reports the speed

   <details><summary>Answer</summary>

   Unequal effort. A fair test gives both programs the same tuning budget, or both their defaults, and says which.

   </details>

4. <!-- q: mcq id="3f6c0a92" -->
   A study finds that cyclists wearing bright vests had fewer near-misses, using only riders in central Abuja during the dry season. A reader asks whether it also holds in Lagos traffic during the rains. Which validity is the reader questioning?

   - [ ] Internal
   - [ ] Construct
   - [x] External
   - [ ] Statistical

   <details><summary>Answer</summary>

   External validity: whether the result holds beyond the setting it was tested in.

   </details>

5. <!-- q: mcq id="81d7b5e3" -->
   A school measures "how much students learned" by counting how many classes each student attended. Which validity is weakest?

   - [ ] Internal
   - [x] Construct
   - [ ] External
   - [ ] Statistical

   <details><summary>Answer</summary>

   Construct validity: attendance isn't learning. A student can attend every class and learn little. A test score is closer to what's meant.

   </details>

6. <!-- q: mcq id="5b9e2c46" -->
   A team's new water filter uses sand, charcoal and a cloth layer, and removes 95% of the dirt. Which is an ablation?

   - [ ] Testing the filter on water from three different wells
   - [x] Testing the filter with the charcoal removed, then with the cloth removed, then with the sand removed
   - [ ] Comparing the filter with a store-bought one
   - [ ] Running the same test ten times

   <details><summary>Answer</summary>

   Removing one part at a time and measuring again shows which parts do the work. Different wells tests external validity; the store-bought filter is a baseline; repeats are for statistical validity.

   </details>

7. <!-- q: mcq id="d06a4f18" -->
   Two weeks into a study, a researcher sees that her chosen threshold makes her favourite app look bad, and switches to a lower one. What's the problem?

   - [ ] Thresholds should always be 50%
   - [x] Changing a rule after seeing the data lets her steer the result toward what she hoped
   - [ ] She should have changed it after one week
   - [ ] There is no problem if she explains the new threshold

   <details><summary>Answer</summary>

   Rules set after seeing the data can be tuned, even without meaning to, to produce the result she wanted. The honest version keeps the dated rule and reports the new threshold as exploratory.

   </details>

8. <!-- q: open id="f84b1d29" -->
   A student times how long a borehole pump takes to fill a 1,000-litre tank at three times of day. List five things a stranger would need written down to repeat the study.

   <details><summary>Answer</summary>

   For example: the pump's make, model and power; the depth of the borehole; how "full" is judged (a mark, an overflow); the exact times of day and how many days; the stopwatch or phone used and when it starts; the starting water level in the tank; and any power source (grid or generator), since voltage can change pump speed.

   </details>

## Before moving on
<!-- bite: e1a83e86-53e8-4912-9dd7-7c5bd97fc6d3 -->

You're done when you can design a fair comparison, pick simple and prior-work baselines, spot unequal effort, name the four kinds of validity with a threat to each, and your own study has a written method, a finished pilot, and four weeks of collection under way.

Recap: change only what you're testing, keep everything else the same, and shuffle what you can't hold still. Compare every result with baselines, especially the cheap guesses. Treat every option the same. Name the threats to internal, construct, external and statistical validity. Fix your rules before you look, repeat enough to beat luck, keep every raw reading, and pilot first.

Next: [[research/06-analyzing-and-interpreting-results|Analysing and Interpreting Results]], where your four weeks of data become an honest answer.

## Related
<!-- bite: ff4ddd3f-f4db-421b-acd4-8da3ff8f6091 -->

- [[research/04-research-questions-and-hypotheses|Research Questions and Hypotheses]]: the variables and hypothesis this method tests.
- [[research/06-analyzing-and-interpreting-results|Analysing and Interpreting Results]]: turning the measurements into honest conclusions.
- [[research/07-research-ethics-and-integrity|Research Ethics and Integrity]]: where moving the rules turns into misconduct.
- [[data-science/06-experimentation-and-ab-testing|Experimentation and A/B Testing]]: controlled experiments in practice.
- [[machine-learning/04-model-evaluation/05-validation-and-tuning|Validation and Tuning]] and [[machine-learning/02-working-with-data/03-train-val-test-splits|Train, Validation and Test Splits]]: the machine-learning version of fixing your rules first.

## About this lesson
<!-- bite: 73f4010c-207c-40d5-837e-a0b456154ecd -->

**Level:** intermediate. Lesson 05 of the research subject, part A (doing the research). It covers fair comparison and randomising, simple and prior-work baselines, equal effort, ablations, measuring well, the four kinds of validity and threats to validity, fixing rules before looking, how much data is enough, reproducibility, and notes for other fields. It moves the running study forward to a written method, a three-day pilot, and the start of four weeks of data collection.

**Source:** *The Craft of Research* (Booth, Colomb and Williams), Zobel's *Writing for Computer Science*, the validity framework of Shadish, Cook and Campbell, and standard forecast-verification practice (simple baselines such as persistence). Rewritten to the course standard, as a hands-on lesson, on 2026-11-26; the pictures come from `scripts/diagrams/research.py`, which asserts the example numbers.
