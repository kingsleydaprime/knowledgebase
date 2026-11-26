---
id: a3537b96-3b38-4504-89ea-8ef108c7b440
---

# Research Ethics and Integrity

Research integrity means reporting exactly what you did and found, crediting everyone whose work you used, and protecting anyone your study touches.

## Before you start
<!-- bite: bd963430-c57e-47ef-9d42-731d378c22e8 -->

Read [[research/06-analyzing-and-interpreting-results|Analysing and Interpreting Results]] first, and have your study folder with `data.csv`, `analyse.py` and `results.md`. This lesson checks that everything in that folder is honest, credited and safe before any of it goes into a paper.

After this lesson you will be able to:

1. say why research depends on trust, and what breaks it;
2. name the three kinds of misconduct and the grey-zone practices that lead toward them;
3. keep a data trail anyone can follow, from what you wrote down to your results;
4. decide who is an author, who is thanked, and how to credit data and AI tools;
5. decide whether a study needs ethics approval and consent.

## What research integrity is
<!-- bite: 3e9d248d-3047-4ba5-82b2-9497f7dbcde2 -->

When you publish a result, other people build on it **without checking it again**. They cite it, design new studies around it, and sometimes make decisions about money, health or safety with it. They trust that you reported what actually happened.

So one faked or bent result doesn't only help the person who faked it. It wastes the time of everyone who trusted it, sometimes for years. That's why honesty is the value every other part of research rests on, and why the rules about it are strict.

## Where we stopped
<!-- bite: 9f31d188-3d2a-4dd6-9bc3-601d05a3f203 -->

Your study has four weeks of data, a script that scores it, and `results.md` with honest claims. Before you write the paper, you'll check three things: that every number traces back to what you actually wrote down, that everyone and everything you used is credited, and that your study didn't need permissions you haven't got.

## The kid version
<!-- bite: 5c5525c0-77ef-450b-8aff-5d7c9c9f2e93 -->

Imagine a game where everyone keeps their own score and nobody checks. It only works if everyone is honest. The moment one player lies, nobody can trust any score, and the game is ruined for everyone.

Research is that game, played by the whole world. Nobody re-checks most results; they build on them. So making up your score isn't a small rule-break: it poisons the game for everyone who trusted it. And there are sneaky half-cheats, like not counting the rounds you lost, that break the same trust more quietly.

**Where the analogy stops working.** In a game, a lie is obvious once someone notices. In research, many integrity failures are honest people fooling themselves, which is why good habits matter more than good intentions.

## From mistake to misconduct
<!-- bite: ea3d6905-d7ff-4980-84b8-16d024e9e167 -->

Integrity problems aren't one thing. They run along a line:

![Research integrity as a spectrum, with weather-study examples. Left, green: an honest mistake, such as typing 32 for 23 and then correcting it with a dated note, is fixed openly. Middle, amber: the grey zone of questionable practices, such as dropping the storm week as unusual or trying thresholds until one wins. Right, red: misconduct, which is fabrication, falsification or plagiarism, such as filling in a missed gauge reading from memory or copying someone else's literature review](images/rs-integrity-spectrum.svg)

1. **Honest mistakes** happen to everyone. Fix them openly, and record the fix.
2. The **grey zone** is practices that make work look stronger than it honestly is, often without anyone deciding to cheat.
3. **Misconduct** is the bright line. It ends careers.

## The three bright lines
<!-- bite: 37e106e5-81a2-4f15-ad13-57400ef5b294 -->

Research misconduct is three things, often shortened to **FFP**:

1. **Fabrication** is making up data or results. In the weather study: you missed Tuesday's gauge reading, so you write down "about 5 mm" from what you remember. That's fabrication, however close the guess.
2. **Falsification** is changing real data or results so they mislead: editing a number, dropping inconvenient days, or doctoring a figure.
3. **Plagiarism** is presenting someone else's words, ideas or work as your own.

There's no small version of these. The honest thing to do with a missed reading is to leave it blank and write why in `notes`. Your script already handles missing days fairly.

## The grey zone
<!-- bite: 3802d07b-2c0f-4aa6-b139-88310845cc40 -->

These are more dangerous than FFP because they feel forgivable. You've met most of them already:

1. **p-hacking** and **HARKing**, from the last two lessons.
2. **Cherry-picking**: reporting the best week or app and hiding the rest. Dropping the storm week "because it was unusual" is this, unless the rule for dropping it was in your plan.
3. **Salami-slicing**: cutting one study into several thin papers to have more papers.
4. **Misleading figures**: a chart whose axis starts at 50% to make a small gap look huge. [[research/10-figures-tables-and-presenting-data|Figures and tables]] covers this.
5. **Selective citation**: leaving out papers that make your work look less new.

What they share: making the work look stronger or newer than it honestly is. The defence is the same every time: report what you actually did, including what didn't work.

## Keeping a data trail
<!-- bite: 6902c05e-50d1-4310-a36d-b3ccbc15fc32 -->

The practical form of honesty is a **data trail**: anyone can follow every number in your results back to what you first wrote down.

![The data trail from notebook to results. data-raw.csv holds exactly what you wrote down and is never edited. corrections.md lists each fix with its date and reason. data.csv is the raw data with only those logged fixes applied. analyse.py reads data.csv and produces results.md. Anyone can follow every number in the results back to what was first written down](images/rs-data-trail.svg)

You will find mistakes: a 32 typed for 23, a date off by one. Fixing them is right. Fixing them *silently* is the problem, because nobody can then tell a correction from a convenient change. So the raw file is never edited, and every fix is written down with its date and reason.

## Credit: who is an author?
<!-- bite: aac7f05f-b363-41ca-859b-d0b54e1d0686 -->

Who goes on the paper is a real ethical question. The common rule (from the medical journal editors' guidelines, used well beyond medicine) is that an **author** made a **substantial contribution** to the ideas, the data or the analysis, *and* helped write or check the paper, *and* agrees to be answerable for it.

1. **Gift authorship**, adding a boss or a big name who didn't contribute, is improper.
2. **Ghost authorship**, leaving off someone who did contribute substantially, is improper too.
3. **Author order** differs by field. Often the first author did the main work and the last is the senior supervisor; maths and economics often go alphabetical.

In the weather study: if a friend read your gauge for three days while you travelled, that's real help but not authorship. Thank them in the **acknowledgements**.

## Credit: words, data and AI
<!-- bite: fd49cabc-1c54-4989-92f6-926ea01d50ec -->

Credit goes beyond people:

1. **Words and ideas.** Quote exact words and cite them. Paraphrasing means rewriting in your own words *and* citing; changing a few words of someone's sentence is still plagiarism. Reusing your own published text without saying so (**self-plagiarism**) counts too.
2. **Data.** If you used weather-station data, from NiMet (the Nigerian Meteorological Agency) or anyone else, check the terms you got it under, and credit it.
3. **AI tools.** Many journals now accept AI help with drafting, editing or code, *if you disclose it* following their policy. But you're responsible for every claim, number and reference. AI tools invent references that look real; a made-up citation in your paper is your integrity failure, not the tool's.

## People, animals and data about them
<!-- bite: 689f94a9-5a19-4186-922e-201175604ecf -->

Once a study involves people or animals, extra duties apply, and they apply **before** you collect anything:

![A three-question ethics check for a study. First: does it involve people or animals, through surveys, interviews, tests, photos or their data? If yes, get ethics-committee approval and informed consent before collecting anything. Second: does it use data someone else owns, such as a weather service, a website or a dataset? If yes, check its licence or terms and credit it in the paper. Third: do you gain if one answer wins, for example because you work for one of the app companies or someone pays you? If yes, declare it as a conflict of interest. After all three, write the answers in plan.md under Ethics and carry on](images/rs-ethics-check.svg)

## Approval, consent and privacy
<!-- bite: 3117f3a2-7503-4a50-a375-1f18742d3053 -->

If the answer to the first question is yes, three duties follow:

1. **Ethics-committee approval.** Most universities have a research ethics committee that must approve studies involving people. Ask yours before you start; approval can't be given afterwards.
2. **Informed consent.** Participants understand what they're agreeing to, and can stop at any time.
3. **Privacy.** Collect only what you need, store it safely, and remove names. Laws such as Nigeria's Data Protection Act (2023) and Europe's GDPR apply.

## The weather study, checked
<!-- bite: 8f4c4ce2-22ac-4857-a181-112023464335 -->

Run the weather study through the three questions:

1. **People?** No: it measures apps and weather. But if you added "ask 50 neighbours which app they trust", it would involve people, and you'd need approval and consent first.
2. **Someone else's data?** The app forecasts are free to read; you're recording what they show, not copying their data in bulk. If you used weather-station readings, check their terms and credit them.
3. **Conflict of interest?** If you worked for one of the app companies, or were paid by one, you'd declare it. It wouldn't stop the study, but readers deserve to know.

## Bigger responsibilities
<!-- bite: cb922338-face-4fff-8e39-7a8986765909 -->

A few duties reach beyond your own study:

1. **Dual use.** Could your work be misused? Security research is the classic case: if you find a flaw in a system, report it privately to its owner and give them time to fix it before you publish. This is called **responsible disclosure**.
2. **Environmental cost.** Training very large AI models uses a lot of energy; papers increasingly report it.
3. **Open science.** Sharing your data, code and a free copy of the paper makes your work checkable, which is honesty in practice. Your data trail and `analyse.py` are already most of this.

## Step 1: build your data trail
<!-- bite: 248332e7-cf95-46b6-b431-d3c88f7cb401 -->

Make `data-raw.csv`: what you actually wrote down each day, from your notebook, screenshots or phone notes. Don't tidy it. If your current `data.csv` *is* what you wrote down, copy it.

Then check `data.csv` against it, row by row. For every difference, write a line in `corrections.md`: the date you fixed it, the row, the old value, the new value, and why. If a difference has no good reason, put the raw value back. Run `analyse.py` again and update `results.md` if anything moved.

## Step 2: run the ethics check
<!-- bite: 63b7d1be-cffa-49c0-9f27-74ff4e8a153a -->

In `plan.md`, add a heading **Ethics** and answer the three questions from the picture, one line each, for your own study. If the answer to the first is yes and you haven't got approval, **stop** and contact your university's ethics committee before using any of that data.

## Step 3: check every reference exists
<!-- bite: d72c0178-06f3-4c9c-a3f6-ab78d73ba301 -->

Open `lit-review.md`. For every paper you cite, find it: open its DOI or link, and check the authors, year and title match what you wrote. Mark each one checked. Delete or fix any you can't find. This matters most for anything an AI tool suggested.

## Step 4: write down your credits
<!-- bite: a1bf43ad-9b17-4720-9a9a-3a6417f2aa08 -->

Create `credits.md` with three short lists:

1. **Acknowledgements**: everyone who helped but isn't an author, and what they did.
2. **Data and tools**: every data source with its terms, and software you used.
3. **AI use**: which tools you used, for what (drafting, editing, code, searching), and what you checked yourself.

Commit everything.

## Your project so far
<!-- bite: 1cee0004-98f3-40b2-9331-dedc5696762b -->

```text
my-study/
├── journal.md
├── reading-log.md
├── lit-review.md     ← every reference checked to exist
├── plan.md           ← + Ethics: the three questions answered
├── data-raw.csv      ← what you wrote down, never edited
├── corrections.md    ← every fix, dated, with its reason
├── data.csv
├── analyse.py
├── results.md        ← re-run if any correction moved a number
└── credits.md        ← acknowledgements, data and tools, AI use
```

**Done when** every difference between `data-raw.csv` and `data.csv` has a dated line in `corrections.md`, `plan.md` answers the three ethics questions, every reference in `lit-review.md` has been opened and checked, and `credits.md` lists helpers, data sources and AI use.

## Terms used in this lesson
<!-- bite: 76f89c5a-d0e1-4f4e-b03f-ae993339590c -->

1. **Research integrity** means reporting what you actually did and found, and crediting what you used.
2. **Fabrication** is making up data; **falsification** is changing real data to mislead; **plagiarism** is passing off someone else's work as yours. Together they're **FFP**, research misconduct.
3. **Questionable research practices** are grey-zone habits, like cherry-picking, that make work look stronger than it is.
4. A **data trail** lets anyone follow each result back to what was first written down.
5. An **author** made a substantial contribution, helped write or check the paper, and answers for it; other helpers go in the **acknowledgements**.
6. **Informed consent** is a participant's agreement, given with understanding, and withdrawable at any time.
7. A **conflict of interest** is a personal gain from one result winning, which must be declared.

## Common pitfalls and traps
<!-- bite: 780cc9de-9527-4946-94c6-cf37b19bfaf2 -->

1. **Filling a gap from memory.** A missed reading stays missing; write why.
2. **Silent fixes.** Corrections without a log look the same as falsification.
3. **Collecting first, asking permission later.** Ethics approval can't be given after the fact.
4. **Trusting AI references.** Open every one.
5. **Close paraphrase.** Swapping a few words in someone's sentence is still plagiarism.
6. **Gift authorship.** Thank helpers; only contributors are authors.

## Check your understanding
<!-- bite: 23e7949a-b932-458a-a2eb-061713f9d189 -->

Try each one before you open the answer.

1. <!-- q: mcq id="a4f81c27" -->
   A student measuring a borehole's water level forgets to measure on Thursday. Which is the honest thing to do?

   - [ ] Write the average of Wednesday and Friday
   - [ ] Write what the level probably was
   - [x] Leave Thursday blank and note that the reading was missed
   - [ ] Drop Wednesday and Friday too, so the gap isn't noticed

   <details><summary>Answer</summary>

   Leave it blank and note why. Writing any estimate as if it were a reading is fabrication, even a sensible average. If an analysis needs a filled value, that's a separate, labelled step, never a change to the data.

   </details>

2. <!-- q: mcq id="e09b3d62" -->
   Which of these is falsification?

   - [ ] Making up survey answers for people who never replied
   - [x] Removing the three plants that died from a fertiliser study, without saying so, so the average looks better
   - [ ] Copying a paragraph from a paper without quotation marks
   - [ ] Typing a number wrongly and fixing it with a dated note

   <details><summary>Answer</summary>

   Removing real data to mislead is falsification. The first is fabrication, the third is plagiarism, and the last is an honest mistake handled properly.

   </details>

3. <!-- q: mcq id="5d7c2a90" -->
   A student plans to ask 100 classmates how many hours they sleep before exams. What must happen first?

   - [ ] Nothing, because sleep isn't sensitive
   - [ ] Collect the answers, then ask the ethics committee
   - [x] Get the ethics committee's approval and plan how to get informed consent, before asking anyone
   - [ ] Ask the lecturer to sign the paper as an author

   <details><summary>Answer</summary>

   It involves people, so approval and consent come before any data is collected. Approval can't be given afterwards.

   </details>

4. <!-- q: mcq id="c26e8f14" -->
   Four people worked on a study of bus waiting times in Ibadan. Who should be an author?

   - [ ] The head of department, who approved the project but did nothing else
   - [x] The student who designed the timing method, collected half the data and wrote the analysis section
   - [ ] A cousin who lent a stopwatch
   - [ ] A friend who proofread the final draft

   <details><summary>Answer</summary>

   The student made a substantial contribution and wrote part of the paper. The head of department would be a gift author; the cousin and the friend go in the acknowledgements.

   </details>

5. <!-- q: mcq id="81f4b06d" -->
   An AI tool suggests five references for a literature review, and they all look real. What should the writer do?

   - [ ] Use them, since the tool is usually right
   - [ ] Use them and add a note that an AI found them
   - [x] Open every one, check the authors, year and title, and delete any that can't be found
   - [ ] Use only the three that sound most relevant

   <details><summary>Answer</summary>

   AI tools invent convincing references. The writer is responsible for every citation, so each must be found and checked.

   </details>

6. <!-- q: open id="f37a0c95" -->
   A researcher is paid by a solar company to compare its panels with a rival's. Is that allowed? What must the researcher do?

   <details><summary>Answer</summary>

   It's allowed, but it's a conflict of interest: the researcher gains if one answer wins. It must be declared in the paper, so readers can weigh it. Good practice is also to pre-register the method and share the data, so anyone can check the result wasn't steered.

   </details>

## Before moving on
<!-- bite: e4781a42-3d5e-4879-a2b3-a9c5b6f1120c -->

You're done when you can explain why research depends on trust, name FFP and the grey-zone practices, keep a data trail, decide who's an author and how to credit data and AI, and run the three-question ethics check; and your own study has its data trail, ethics answers, checked references and credits.

Recap: other people build on your work without re-checking it, so honesty holds everything up. Fabrication, falsification and plagiarism are bright lines; cherry-picking and its cousins are the grey zone that leads there. Keep raw data untouched and log every fix. Credit authors, helpers, data and AI tools, and check every reference exists. If people are involved, get approval and consent first.

Next: [[research/08-anatomy-of-a-paper|Anatomy of a Paper]], where your study starts becoming a paper.

## Related
<!-- bite: 4e4534bb-e212-45e3-92db-949f7551adbe -->

- [[research/06-analyzing-and-interpreting-results|Analysing and Interpreting Results]]: where p-hacking and HARKing happen.
- [[research/01-what-research-is|What Research Is]]: honesty as the core research value.
- [[research/12-citations-referencing-and-tools|Citations, Referencing and Tools]]: crediting prior work correctly.
- [[research/05-methodology-and-experiment-design|Methodology and Experiment Design]]: reproducibility as integrity in practice.

## About this lesson
<!-- bite: 630daa44-4d6c-48d5-a675-b7a03b997883 -->

**Level:** intermediate. Lesson 07 of the research subject, part A (doing the research). It covers why research depends on trust, the line from honest mistake to misconduct, FFP, questionable research practices, the data trail, authorship and acknowledgements, crediting words, data and AI tools, ethics approval, consent and privacy, conflicts of interest, and wider responsibilities. It moves the running study forward to a checked data trail, an ethics section, verified references and a credits file.

**Source:** the US Office of Research Integrity's definition of misconduct (FFP), the ICMJE authorship criteria, Nigeria's Data Protection Act 2023, and standard research-ethics practice. Rewritten to the course standard, as a hands-on lesson, on 2026-11-26; the pictures come from `scripts/diagrams/research.py`.
