---
id: ee065a7a-e5ea-4c16-b04d-7dfec371413b
---

# Research Questions and Hypotheses

A research question is a precise thing you can measure your way to an answer for, and a hypothesis is the answer you predict before you look, stated so that the data could prove it wrong.

## Before you start
<!-- bite: 39eb8dbf-3272-491e-b881-57ae3a9af050 -->

Read [[research/03-finding-a-problem-and-literature-review|Finding a Problem and the Literature Review]] first, and have your scoped question, its FINER check and your `lit-review.md` from its steps. This lesson sharpens that question until you could hand it to someone else and they'd collect the same data you would.

After this lesson you will be able to:

1. turn a topic into a question, and a question into a hypothesis;
2. turn every fuzzy word in a question into something you can measure;
3. name the independent, dependent, controlled and confounding variables in a study;
4. tell descriptive, comparative and causal questions apart, and say what each needs;
5. write a hypothesis that could be proved wrong, with its null hypothesis;
6. write your plan down, dated, before you collect any data.

## What a research question is
<!-- bite: fc8c0338-896d-431e-88e9-ced7f2a987ce -->

Your question from the last lesson is scoped, but it isn't sharp yet. "How accurate are three free weather apps for Lagos?" still hides a problem: **what does "accurate" mean?** Two people could run that study and measure completely different things.

A **research question** is sharp when every word in it points at something you can measure, so you know what data to collect and when you're done. A **hypothesis** goes one step further: it's the answer you *predict*, written down before you look, in a form the data could show is wrong.

## Where we stopped
<!-- bite: 0d2efdfc-0211-45ee-b5a8-43ffce52ccf9 -->

You have a question that passes FINER and the "so what?" test, and a one-page literature review that ends in a gap. For the weather study, that's: *how accurate are three free weather apps for next-day rain and temperature in Lagos, over four weeks?* Now you'll make it precise enough to test.

## The kid version
<!-- bite: 53002fdc-dc7f-4151-9d59-ba88696dec4f -->

"Are dogs smart?" is a **wish**, not a question you can answer. You can't tell when you're done, and you don't know what to count. Now grind it down: *"Can my dog learn to sit in fewer tries than my cat?"*

Look what the sharp version gives you for free:

1. **What to count**: the number of tries to learn "sit".
2. **What to change**: dog or cat.
3. **When you're done**: when you've counted tries for both.
4. **A clear answer**: either the dog took fewer tries, or it didn't.

**Where the analogy stops working.** "Fewer tries" is easy to count. In real research, deciding *what* to count is the hard part, and two sensible choices can give opposite answers.

## From topic to hypothesis
<!-- bite: 9f6185fb-80ea-4072-bf41-e3ba57c82530 -->

That grind has three stages, and each one is narrower than the last:

![The funnel from topic to hypothesis, using the weather study. Top, widest: the topic, weather apps in Lagos, which is a direction, not something you can answer. Middle: the question, how often is each free app right about tomorrow's rain, over four weeks of rainy season, which you can answer. Bottom, narrowest: the hypothesis, each app is right about rain more often than simply guessing tomorrow will be like today, a predicted answer that could turn out false](images/rs-question-funnel.svg)

1. A **topic** is a direction. You can't finish it.
2. A **question** is something specific you can answer.
3. A **hypothesis** is the answer you predict, and it could turn out wrong.

Every study needs the question. Not every study needs a hypothesis, as you'll see near the end. Beginners often stop at the topic and call it a plan.

## Turning fuzzy words into measurements
<!-- bite: ee5fa233-8854-43fd-9977-5a09b2105a62 -->

To sharpen a question, find every fuzzy word in it and turn it into a measurement. This is called **operationalising**. A word you can't measure means you haven't got a research question yet.

In the weather study the fuzzy word is "accurate", and it splits into two measurements, one for rain and one for temperature:

1. **Rain:** each evening at 8 pm, write down each app's chance of rain for tomorrow. Count it as "the app said rain" if the chance is 50% or more. Count it as "it rained" if your gauge catches 1 mm or more. The app is **right** on a day when the two agree.
2. **Temperature:** write down each app's forecast high for tomorrow, then the high you actually measure. The day's **error** is the gap between them, whichever way it's wrong.

Each of these is a **metric**: a named number that stands for the fuzzy word.

## Scoring a week for rain
<!-- bite: b54c4fce-ebeb-4d51-956d-ad4c0a209866 -->

Here's one week of one app, scored for rain:

![One week of the weather study, scored for rain. For each day, Monday to Sunday, the top row shows whether the app said rain (its chance of rain was 50 percent or more) and the second row whether the rain gauge caught 1 millimetre or more. The app was right on Monday, Wednesday, Thursday, Saturday and Sunday, five days out of seven, a hit rate of 71 percent. On Tuesday it said rain and none fell, a false alarm; on Friday it said dry and rain fell, a missed rain](images/rs-rain-week.svg)

The app was right on five of the seven days.

## The hit rate
<!-- bite: 5a989260-9cef-4c78-b156-7bec99ca2b64 -->

The **hit rate** is the share of days a forecast got right:

$$\text{hit rate} = \frac{\text{days right}}{\text{days counted}} = \frac{5}{7} \approx 71\%$$

The two wrong days are wrong in different ways. Tuesday was a **false alarm**: it said rain and none came. Friday was a **missed rain**: it said dry and you got soaked. You'll want to count those separately later, because a farmer and a trader may care about different ones.

## Scoring a week for temperature
<!-- bite: ed0301d1-a686-459a-adb3-7b7af1e4d589 -->

Now the same week, for the daily high:

![The same week scored for temperature. For each day the blue dot is the app's forecast high and the orange dot is the measured high, in degrees Celsius, on a scale from 27 to 34. The grey gap between them is that day's error, ignoring which way it was wrong: 2, 0, 2, 0, 1, 1 and 1 degrees. Their average is 7 divided by 7, an average error of 1.0 degree](images/rs-temp-week.svg)

Each grey gap is one day's error: 2, 0, 2, 0, 1, 1 and 1 degrees.

## The average error
<!-- bite: 4c0c0b51-8a2e-496f-a5d1-2675074592dd -->

To turn the gaps into one number, ignore whether the app guessed too high or too low, add the gaps up, and divide by the number of days. That's the **average error** (its full name is the *mean absolute error*):

$$\text{average error} = \frac{|f_1 - a_1| + |f_2 - a_2| + \dots + |f_n - a_n|}{n} = \frac{2+0+2+0+1+1+1}{7} = 1.0\,^\circ\text{C}$$

Here $f$ is the forecast high, $a$ is the actual high, and $n$ is the number of days. The bars $|\;|$ mean "the size of the gap, ignoring its sign", so an app that's 2° too hot and an app that's 2° too cold are equally wrong.

## A metric is a choice
<!-- bite: 733becd1-d536-4ecb-b0ff-0fe902b577e0 -->

Every number in those metrics was a decision: 50% chance counts as "said rain", 1 mm counts as "it rained", 8 pm is when you read the apps. Change them and the answer can change. Set the rain line at 70% instead, and an app that often says "60% chance" suddenly looks like it never predicts rain.

One trap is worth seeing now. In the dry season, an app that *always* says "dry" would score a high hit rate without forecasting anything. That's why the weather study runs in the rainy season, and why the next lesson compares every app against a simple guess.

So: pick metrics that match what people actually care about, write them down exactly, and say why you chose them. Many weak papers are weak because "better" was never pinned to a number.

## The four kinds of variable
<!-- bite: d55045b7-ccaf-48ab-ae94-07c2676865f3 -->

Every study is "change one thing, measure another, keep the rest the same". Those things have names:

![The four kinds of variable in the weather study. The independent variable, which app, is what you change; an arrow runs from it to the dependent variable, the rain hit rate and temperature error, which is what you measure. Below, the controlled variables are held the same for every app: the same time of reading, the same location setting, the same rain gauge. Above, a confound sneaks in with a dashed arrow: if you read app A at 6 pm but app B at 10 pm, app B has seen four more hours of weather, and that, not the app, could be why it scores better](images/rs-variables.svg)

1. The **independent variable** is what you change: which app.
2. The **dependent variable** is what you measure: hit rate and average error.
3. The **controlled variables** are what you keep the same for every app: the reading time, the location, the gauge.
4. A **confounding variable** (a confound) is something that changes *along with* the independent variable, so it could be the real cause of any difference.

## Hunting confounds
<!-- bite: 20f0899d-f566-4155-9a64-bfce08c5f371 -->

Confounds are how honest studies give wrong answers, so hunt for them before you collect anything. For each one, ask: *does this differ between the things I'm comparing?* In the weather study:

1. **Reading time.** Read app A at 6 pm and app B at 10 pm, and app B has seen four more hours of weather. Fix: read all three within the same few minutes.
2. **Location.** If one app is set to "Lagos" and another uses your phone's GPS in Yaba, they're forecasting different places. Fix: set the same location in all three.
3. **Different weeks.** Test app A in week 1 and app B in week 3, and the weather itself differs. Fix: test all three on the same days.
4. **Where the gauge is.** A gauge under a tree catches less rain than one in the open, but that affects every app equally, so it's a measurement problem rather than a confound. Note it anyway; lesson 05 deals with it.

Finding confounds is the heart of [[research/05-methodology-and-experiment-design|experiment design]], the next lesson.

## Three kinds of question
<!-- bite: 4975b584-5d01-49ad-8528-f62a1677d28f -->

The *kind* of question decides how much work it takes to answer. From easiest to hardest:

1. **Descriptive**: what, how much, how often? *"How often is each app right about tomorrow's rain?"* You measure carefully, and that's it.
2. **Comparative**: does A differ from B? *"Is app B right more often than app A?"* You need a fair comparison, and later some statistics.
3. **Causal**: does A *cause* B? *"Do apps that use a local weather service forecast better* because *of the local data?"* Much harder: you'd have to rule out every other difference between the apps, and you can't change where an app gets its data.

The weather study is descriptive and comparative. It can't claim causes, and an honest paper says so. Claiming a cause when you've only seen two things go together is one of the oldest mistakes in research; [[data-science/07-causal-inference-and-econometrics|causal inference]] is the field that tackles cause properly.

## A hypothesis that could be wrong
<!-- bite: 334a0895-d29e-49e2-be64-50c786bb205c -->

A real hypothesis makes a specific prediction that some result could prove **wrong**. This is called being **falsifiable**, an idea from the philosopher Karl Popper: a claim is scientific only if you can say what result would disprove it.

Compare two hypotheses for the weather study:

1. *"The apps are quite good."* What result would prove that wrong? None. It's unfalsifiable.
2. *"Each app is right about tomorrow's rain more often than simply guessing that tomorrow will be like today."* Run four weeks and count. If an app loses to the guess, the hypothesis is wrong.

The second one also has a reason behind it, which every hypothesis should: forecasting tools are built to beat that guess, so an app that can't is failing at its job. Your literature review is where a reason like this comes from.

## The null and the alternative
<!-- bite: b312dc1a-ceec-45aa-847b-ca3d43a309ec -->

Formally, a hypothesis comes as a pair:

1. The **null hypothesis**, written H₀, is the boring default: there's no effect. *"The app is right no more often than 'tomorrow will be like today'."*
2. The **alternative hypothesis**, written H₁, is what you suspect: there is an effect. *"The app is right more often."*

You collect data to see whether it lets you **reject the null**. You never *prove* H₁; you show that the null doesn't fit the data well. And if you can't reject the null, that doesn't prove there's no effect: four weeks may just be too short to tell. [[research/06-analyzing-and-interpreting-results|Analysing results]] shows how to decide.

In the week you scored, the guess would have been right on only 2 days, against the app's 5. One week proves nothing, but it shows what the full study will count.

## Exploring or confirming
<!-- bite: 213b4d11-06c6-4b56-8fb3-91b78849b7b9 -->

Not all good research tests a hypothesis:

1. **Exploratory** research maps unknown ground: *"what patterns show up in this data?"* Its output is new questions and hypotheses. That's legitimate.
2. **Confirmatory** research tests a hypothesis you stated beforehand.
3. **Engineering** research asks *"can we build something that does X, and how well?"* The build and its measurements are the answer.

The dishonest move is exploring, finding something, and then writing the paper as though you'd predicted it. That's called **HARKing** (hypothesising after the results are known), and it makes chance findings look like confirmed ones.

## Write it down first
<!-- bite: f96afb5c-140c-44ba-98a1-24c5af91fc17 -->

The cure for HARKing is simple: **write your question, hypothesis and metrics down, with a date, before you collect any data.** Doing this publicly is called **pre-registration**, and many fields now expect it. The Open Science Framework (osf.io) lets anyone register a plan for free.

For your study, a dated file is enough to start. If you keep your study in git, commit it, and the commit records the date for you. Later, anything you report that wasn't in the plan gets labelled honestly as exploratory.

## A good question, checked
<!-- bite: 80d9f381-4b0d-488f-bb55-68a56751634d -->

Before you move on, run your question through five checks:

1. **Specific**: one clear thing, not a bundle.
2. **Measurable**: every fuzzy word has a metric, written down exactly.
3. **Answerable in scope**: it still passes FINER's *feasible*.
4. **Connected to the gap**: answering it fills the gap your literature review named.
5. **Honest about its type**: descriptive, comparative or causal; exploratory or confirmatory.

## Step 1: find and measure your fuzzy words
<!-- bite: a568f22d-2505-4d82-9c8e-8fd46a1168da -->

Write your question at the top of a new file, `plan.md`. Underline every fuzzy word: "accurate", "better", "fast", "reliable", "effective". For each one, write the exact metric that stands for it, including every number you had to choose (thresholds, times, units), and one line on why.

## Step 2: name your variables and hunt confounds
<!-- bite: 725275cb-70e9-4d85-a079-ba43108b99c3 -->

In `plan.md`, under a heading **Variables**, write your independent variable, your dependent variables, and your controls. Then list **at least three possible confounds**, and next to each, how you'll stop it (keep it the same, test everything on the same days, and so on).

## Step 3: write your questions and hypothesis
<!-- bite: 1a19e674-c0c4-47d0-838e-38b2c439a888 -->

Under **Questions**, write one descriptive question and one comparative question. Label each with its kind.

Under **Hypothesis**, write H₀ and H₁ as a pair, then one line saying where your prediction comes from (a paper, a reason, a pattern you noticed). Then write the result that would prove H₁ wrong. If you can't write that result, the hypothesis isn't falsifiable yet; sharpen it.

If your study is exploratory, write *"Exploratory: no hypothesis"* instead, and say what you hope to find out.

## Step 4: date it before you collect
<!-- bite: 09d12db2-98a5-48bf-9bda-b97a147ed6b8 -->

Put today's date at the top of `plan.md`. If your study folder is a git repository, commit the file. Don't collect a single data point until this is done.

## Your project so far
<!-- bite: 30cda468-9250-40bd-b4ea-722d73ea2e75 -->

```text
my-study/
├── journal.md
├── reading-log.md
├── lit-review.md
└── plan.md          ← dated: question, metrics, variables, confounds, H₀ and H₁
```

**Done when** `plan.md` is dated, every fuzzy word in your question has an exact metric, you've named your variables and at least three confounds with a fix for each, and your hypothesis pair comes with the result that would prove it wrong (or the plan says plainly that the study is exploratory).

## Terms used in this lesson
<!-- bite: 72635185-893d-451e-bea9-1d1abe48f401 -->

1. A **research question** is a specific question whose every word points at something you can measure.
2. A **hypothesis** is a predicted answer, written before you look, that the data could prove wrong.
3. **Operationalising** a word means turning it into an exact measurement, called a **metric**.
4. The **hit rate** is the share of days a forecast was right; the **average error** (mean absolute error) is the average size of the gap between forecast and actual.
5. The **independent variable** is what you change, the **dependent variable** is what you measure, **controlled variables** are what you keep the same, and a **confound** changes along with the independent variable and could be the real cause.
6. A claim is **falsifiable** when some result could prove it wrong.
7. The **null hypothesis** (H₀) says there's no effect; the **alternative hypothesis** (H₁) says there is one.
8. **HARKing** is presenting a finding as if you'd predicted it, after seeing the results; **pre-registration** prevents it by recording the plan first.

## Common pitfalls and traps
<!-- bite: ab3e941c-afa7-40e4-8af3-39d93993f756 -->

1. **Stopping at the topic.** "I'm studying weather apps" isn't a plan.
2. **Leaving "better" unmeasured.** If you can't say what number would show it, you can't show it.
3. **Comparing under different conditions.** Different times, places or weeks for each thing you compare, and the comparison means nothing.
4. **An unfalsifiable hypothesis.** "Works well" can't lose, so it can't tell you anything.
5. **Claiming a cause from a comparison.** Seeing that two things go together isn't proof that one causes the other.
6. **Deciding the hypothesis after the data.** Write it down and date it first.

## Check your understanding
<!-- bite: 76eeefbb-fcf1-46b4-934f-a15676b9ad7a -->

Try each one before you open the answer.

1. <!-- q: mcq id="c3e8a170" -->
   A student wants to study "whether WhatsApp groups help students do better". Which version is the sharpest research question?

   - [ ] "Do WhatsApp groups help students?"
   - [ ] "How do students use WhatsApp?"
   - [x] "Do 300-level students in course study groups on WhatsApp score higher on the mid-semester test than those not in one?"
   - [ ] "Is social media good or bad for education?"

   <details><summary>Answer</summary>

   The third: it names who (300-level students), what changes (in a study group or not) and what's measured (the mid-semester test score). The others never say what to measure.

   </details>

2. <!-- q: gap id="5b91d4e2" answers="3;60" -->
   An app's rain forecast is checked for five days.

   | Day | App said rain? | Rain fell? |
   |---|---|---|
   | 1 | yes | yes |
   | 2 | no | yes |
   | 3 | no | no |
   | 4 | yes | no |
   | 5 | yes | yes |

   The app was right on ___ days, so its hit rate is ___ %.

   <details><summary>Answer</summary>

   Right on days 1, 3 and 5: 3 days. Hit rate = 3 ÷ 5 = 60%. Day 2 was a missed rain and day 4 a false alarm.

   </details>

3. <!-- q: gap id="e07a3c59" answers="1.5" -->
   An app forecast highs of 31, 30, 33 and 29 °C for four days. The measured highs were 30, 32, 33 and 26 °C. What is its average error, in °C?

   <details><summary>Answer</summary>

   The gaps, ignoring sign, are 1, 2, 0 and 3. Their sum is 6, and 6 ÷ 4 = 1.5 °C.

   </details>

4. <!-- q: mcq id="8d2f6b41" -->
   A farmer compares two fertilisers. Fertiliser A goes on her plot by the stream; fertiliser B goes on her plot on the dry hillside. A's maize grows taller. Why can't she say A is the better fertiliser?

   - [ ] Maize height is not a dependent variable
   - [x] Where the plot is changes along with the fertiliser, so the water by the stream could be the real cause
   - [ ] She should have used three fertilisers
   - [ ] Fertiliser is a controlled variable

   <details><summary>Answer</summary>

   Location is a confound: it changes along with the fertiliser. The fix is to use both fertilisers on similar land, for example on alternating strips across both plots.

   </details>

5. <!-- q: mcq id="41c9e7a6" -->
   Which hypothesis is falsifiable?

   - [ ] "Our new solar charger performs well."
   - [ ] "Students may sometimes learn better with videos."
   - [x] "Our charger fills a 10,000 mAh power bank in under 6 hours of Lagos sunshine."
   - [ ] "Good teachers make a difference."

   <details><summary>Answer</summary>

   The third: it names a number, and a charge that takes 7 hours would prove it wrong. The others have no result that could count against them.

   </details>

6. <!-- q: mcq id="f6a2b083" -->
   A researcher tests whether a new phone keyboard lets people type faster than the old one. What is the null hypothesis?

   - [ ] The new keyboard is faster
   - [x] People type no faster on the new keyboard than on the old one
   - [ ] The old keyboard is faster
   - [ ] Typing speed can't be measured

   <details><summary>Answer</summary>

   The null is the "no effect" default: no difference in speed. The study then asks whether the data let you reject it.

   </details>

7. <!-- q: mcq id="9e5c1d72" -->
   "Do danfo buses that use a mobile-money payment system cause fewer fare arguments, because the money doesn't change hands?" What kind of question is this?

   - [ ] Descriptive
   - [ ] Comparative
   - [x] Causal
   - [ ] Exploratory

   <details><summary>Answer</summary>

   Causal: it asks whether the payment system *causes* the change, and why. Comparing buses with and without it would only show whether the two go together; other differences between the buses (routes, conductors) could explain it.

   </details>

8. <!-- q: open id="b2d07e94" -->
   Take the question "Is pidgin radio more popular than English radio in Port Harcourt?" Turn "popular" into one exact metric, name the independent and dependent variables, and give one confound with its fix.

   <details><summary>Answer</summary>

   For example: "popular" becomes the share of a random sample of 200 adults who say they listened to a station in the past week. The independent variable is the station's language (pidgin or English); the dependent variable is that share. A confound: if you survey only near a university, you'll get younger, more English-schooled listeners; fix it by sampling markets, parks and offices across the city in the same week.

   </details>

## Before moving on
<!-- bite: a3747abf-257d-438c-8a65-fd261f381632 -->

You're done when you can turn a topic into a measurable question and a falsifiable hypothesis, name the four kinds of variable, spot a confound, say whether a question is descriptive, comparative or causal, and your dated `plan.md` exists.

Recap: a topic is a direction, a question is answerable, and a hypothesis is a prediction that could be wrong. Turn every fuzzy word into a metric, and remember each metric is a choice. Change one thing, measure another, keep the rest the same, and hunt the confounds that could fool you. Write the null and the alternative as a pair, and write the plan down, dated, before you collect anything.

Next: [[research/05-methodology-and-experiment-design|Methodology and Experiment Design]], where your plan becomes a fair test.

## Related
<!-- bite: f0501b7a-94c7-43d4-bb29-8ee813369981 -->

- [[research/03-finding-a-problem-and-literature-review|Finding a Problem and the Literature Review]]: where the question comes from.
- [[research/05-methodology-and-experiment-design|Methodology and Experiment Design]]: how you answer it fairly.
- [[research/06-analyzing-and-interpreting-results|Analysing and Interpreting Results]]: H₀, H₁ and honest conclusions.
- [[data-science/06-experimentation-and-ab-testing|Experimentation and A/B Testing]]: variables and hypotheses in practice.
- [[data-science/07-causal-inference-and-econometrics|Causal Inference]]: when the question is about cause.

## About this lesson
<!-- bite: 6f513463-1e90-468e-99ca-60b7425723e7 -->

**Level:** intermediate. Lesson 04 of the research subject, part A (doing the research). It covers the funnel from topic to question to hypothesis, operationalising with metrics (hit rate and average error, worked on one week of data), the four kinds of variable and hunting confounds, descriptive, comparative and causal questions, falsifiability, the null and alternative hypotheses, exploratory versus confirmatory work, and pre-registration. It moves the running study forward to a dated `plan.md`.

**Source:** *The Craft of Research* (Booth, Colomb and Williams), Popper's falsifiability, and standard forecast-verification practice (hit rate, mean absolute error, the persistence forecast "tomorrow will be like today"). Rewritten to the course standard, as a hands-on lesson, on 2026-11-26; the pictures and the worked week's numbers come from `scripts/diagrams/research.py`, which asserts them.
