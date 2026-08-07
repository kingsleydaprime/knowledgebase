# Research Ethics & Integrity

**[reference]** — from the ORI (Office of Research Integrity) framework, ICMJE authorship guidelines, and standard research-ethics practice. Research is built entirely on **trust** — the whole system assumes people report what actually happened. This note is the non-negotiables, the grey areas that trip up honest people, and how to stay clearly on the right side of both.

## The kid version first

Imagine a game where **everyone keeps their own score and just reports it** — no referee checking. The game only works if everyone is honest. The moment *one* kid lies about their score, you can't trust *any* score, and the whole game is ruined.

Science is exactly that game, played by the whole world across generations. When you publish a result, thousands of people **build on it without re-checking** — they trust you. So the rules about honesty are absolute: **making up or fudging your "score" isn't just against the rules, it poisons the game for everyone who trusted it.** And there are *sneaky* ways to sort-of-cheat — not outright lying, but bending things in your favor — that you also have to avoid, because they erode the same trust. That's this whole note.

## Why it's the load-bearing value

A faked result doesn't just help one cheater — it **wastes everyone downstream**: people cite it, build methods on it, run companies or treatments on it, and spend years failing to reproduce what was never real. The cost of dishonesty is paid by the *honest* people who trusted the record. That's why misconduct is treated as career-ending, and why [[research/01-what-research-is|honesty]] is the value every other research virtue rests on.

## The cardinal sins — FFP

The three things that end careers, universally recognized as misconduct:
- **Fabrication** — **making up** data or results that were never collected. (Inventing measurements.)
- **Falsification** — **manipulating** real data, images, or results to misrepresent them (doctoring a figure, dropping inconvenient data points, tweaking numbers). 
- **Plagiarism** — presenting someone else's **words, ideas, or work as your own** without credit.

There is no "small" version of these. They are bright lines.

## The subtle misconduct — questionable research practices

More dangerous *because* they feel forgivable — the grey-zone practices that most researchers are tempted by, often without noticing they've crossed a line ([[research/06-analyzing-and-interpreting-results|analysis integrity]]):
- **p-hacking** — trying analyses until one is "significant," reporting only that.
- **HARKing** — inventing the hypothesis *after* seeing results, presenting it as predicted.
- **Cherry-picking** — reporting the best run/dataset/metric, hiding the rest.
- **Salami-slicing** — splitting one study into many thin papers to inflate your publication count.
- **Misleading figures** — truncated axes, misleading scales ([[research/10-figures-tables-and-presenting-data|honest visualization]]).
- **Selective citation** — ignoring prior work that undercuts your novelty.

The common thread: **making your work look stronger or more novel than it honestly is.** The defense is transparency — report what you actually did, including what didn't work.

## Authorship & credit

Who goes on the paper is a real ethical (and political) minefield:
- **Who earns authorship** — someone who made a **substantial intellectual contribution** *and* helped write/approve it (the ICMJE-style criteria). Running one script or funding the lab isn't automatically authorship.
- **Gift / honorary authorship** — adding a big name or a boss who didn't contribute. **Improper.**
- **Ghost authorship** — someone who *did* contribute substantially (or wrote it) left *off*. Also improper.
- **Author order** — conventions differ by field: often **first author = the person who did the main work**, **last author = the senior/PI** who supervised; some fields (math, econ, theory) use **alphabetical**. Know your field's convention.
- **Acknowledge** non-author help (advice, compute, proofreading), **disclose funding**, and declare **conflicts of interest** (financial or personal stakes in the outcome).

## Citing properly (and self-plagiarism)

Beyond avoiding [[research/12-citations-referencing-and-tools|plagiarism]]: cite the **original** source, **quote** when using exact words (and cite), **paraphrase properly** (rewrite *and* cite — changing a few words is still plagiarism), and beware **self-plagiarism** — reusing your *own* previously published text without disclosure is a real violation (you can't publish the same thing twice as if new).

**AI-tool disclosure (the emerging norm):** using an LLM to draft, edit, or brainstorm is increasingly acceptable *if disclosed* per the venue's policy — but **you remain fully responsible for every claim, citation, and number.** LLMs fabricate references and facts; an AI-hallucinated citation in your paper is *your* integrity failure, not the tool's. Check the venue's specific AI policy (they vary and are evolving fast).

## Human & animal subjects

If your research involves people or animals, extra duties kick in — highly relevant for HCI, surveys, user studies, medical, and some robotics work:
- **Informed consent** — participants understand what they're agreeing to and can withdraw.
- **Ethics-board approval (IRB / ethics committee)** — required *before* collecting data involving human/animal subjects at most institutions.
- **Privacy & data protection** — anonymize, secure, and lawfully handle personal data (GDPR and similar); minimize what you collect.
- **Minimize harm** — physical, psychological, or social.

## Data, code & broader responsibility

- **Dataset ethics** — was the data collected/licensed with consent? Are you allowed to use and redistribute it? (Scraped data has real legal/ethical constraints.)
- **Dual-use** — could your work be **misused** (a security exploit, a surveillance tool, a bioweapon-adjacent method)? Responsible researchers weigh this and sometimes practice **responsible disclosure** (report a vulnerability privately before publishing).
- **Environmental cost** — training huge models has a real carbon footprint worth acknowledging.
- **Open science *is* integrity** — releasing preprints, data, and code makes your work checkable, which is the practical form of honesty. Transparency is the antidote to most of the grey-zone temptations above.

## Key insight

**Research runs on trust — people build on your results without re-checking them — so honesty isn't a nicety, it's the load-bearing value, and dishonesty's cost is paid by the honest people who believed you.** The bright lines are **FFP** (fabrication, falsification, plagiarism), career-ending with no small version. The more insidious risks are the **grey-zone practices** (p-hacking, HARKing, cherry-picking, salami-slicing, misleading figures) that make work look better than it honestly is — defended against by **transparency** (report what you actually did, including failures). Handle **authorship** fairly, **cite** scrupulously (including your own prior work and any AI tools, whose output you fully own), protect **human/animal subjects** and **data**, and weigh **dual-use** — because the whole enterprise only works if the record can be trusted.

## Related
- [[research/06-analyzing-and-interpreting-results|Analyzing & Interpreting Results]] — where p-hacking/HARKing live technically
- [[research/01-what-research-is|What Research Is]] — honesty as the core research value
- [[research/12-citations-referencing-and-tools|Citations & Tools]] — crediting prior work correctly
- [[research/05-methodology-and-experiment-design|Methodology]] — reproducibility & transparency as integrity in practice
