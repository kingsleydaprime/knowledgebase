# Analyzing & Interpreting Results

**[reference]** — from standard statistical practice, *The Craft of Research*, and the reproducibility literature (Ioannidis, "Why Most Published Research Findings Are False"). You ran the experiment; now, *what does it actually mean?* The discipline of drawing **honest, defensible conclusions** — and not one inch more than the data supports. This is where good intentions meet the easiest place to fool yourself.

## The kid version first

You flip two coins 10 times each. Coin A gets **6 heads**, Coin B gets **4**. Is Coin A a "better heads-flipper"? **No** — that's just *luck*. Flip them again and it might reverse. The difference is **noise**, not a real property of the coins.

That's the trap at the heart of analyzing results: **it is dangerously easy to see a "win" that's really just random luck.** Your new method scored 85% and the old one 83% — is your method *better*, or did it just get a lucky set of test examples? Numbers don't announce whether they're signal or noise; *you* have to figure that out, carefully, and resist the strong pull to believe the numbers that flatter you.

Two jobs, then: (1) **is this difference real, or is it luck?** and (2) **say exactly what the numbers show — and nothing more.**

## Signal vs noise — is the difference real?

The tools for "real or luck?":
- **Report variance, not just a mean.** Run it multiple times ([[research/05-methodology-and-experiment-design|repeated trials]]) and report **mean ± standard deviation** or **error bars / confidence intervals.** A single number (85%) is nearly meaningless — 85% ± 0.3 across 10 seeds is a solid result; 85% ± 9 is noise wearing a result's clothes. **Rule of thumb: if the error bars overlap heavily, the methods probably aren't different.**
- **Statistical significance** ([[ai-ml/01-data-scientist/03-inferential-statistics|inferential statistics]]) — a **significance test** (t-test, etc.) estimates the probability you'd see a difference *this big* if there were *really no difference* (i.e. if the [[research/04-research-questions-and-hypotheses|null hypothesis]] were true). Low probability → the difference is probably real (you "reject the null").
- **Confidence intervals** — often more informative than a p-value: "the improvement is 2% ± 1.5% (95% CI)" tells you both the size *and* the uncertainty at a glance.

### The p-value, and its traps
The **p-value** is the most used and most abused number in science. What it **is**: the probability of a result at least this extreme *assuming the null hypothesis is true.* What it is **NOT** (the classic misreadings):
- It is **not** "the probability the null is true," and **not** "the probability my result was luck."
- **`p < 0.05` is an arbitrary convention**, not a law of nature — and *not* a synonym for "important."
- **Statistical significance ≠ practical significance.** With enough data, a *trivially tiny* effect (0.01% improvement) becomes "statistically significant" and still be *useless*. Always report the **effect size** (how big is the difference?), not just whether it's significant. A significant-but-tiny effect is a favorite way to dress up a nothing result.

## The over-claiming trap — say only what you showed

The single most common interpretation sin: the leap from *"A scored higher than B in my experiment"* to *"A is better than B."* Those are **different claims**, and the data only supports the first. State the **narrowest claim your evidence supports**, with its scope attached:
- Not "our method is better" → **"our method achieved 3% higher accuracy than [baselines] on [datasets D₁, D₂] under [these conditions]."**
- If you tested one dataset, you showed it *on that dataset* — not in general ([[research/05-methodology-and-experiment-design|external validity]]).
- If you showed correlation, you have **not** shown causation.

Writing the modest, precise version is the mark of a mature researcher; the grand version is what gets a paper (rightly) torn apart in [[research/14-peer-review-and-rebuttals|review]].

## Hunt the boring explanation

Before you celebrate a result, **actively try to kill it** — assume it's an artifact and look for the mundane cause:
- Is there a **confound** ([[research/05-methodology-and-experiment-design|internal validity]]) — did something *other* than your method produce the effect?
- Is it **[[research/05-methodology-and-experiment-design|data leakage]]** inflating the number?
- Did you get a **lucky seed / lucky split**? (Re-run.)
- Is it **correlation mistaken for causation** — A and B move together because both are driven by C?

Your reflex on a result that's *too good* should be suspicion, not joy. The results that survive your own hardest attempts to explain them away are the ones worth reporting.

## Negative and null results are real knowledge

"It didn't work" or "there was no significant difference" is a **genuine finding** — it saves others from the same dead end. But two forces conspire to bury them:
- **Publication bias / the file-drawer problem** — journals and authors favor positive results, so negatives go unpublished, and the literature ends up *systematically overstating* effects (everyone sees the lucky positives, none of the honest negatives). This distorts entire fields.
- Report your negatives honestly anyway; venues and norms increasingly value them, and they're the antidote to the distortion.

## The ways you (or others) cheat at analysis — honest and not

The subtle, often-unconscious failure modes — know them so you don't commit them:
- **p-hacking / data dredging** — trying many analyses, subsets, or metrics until *something* crosses `p < 0.05`, then reporting only that. 
- **The multiple-comparisons problem** — test 20 hypotheses and, by pure chance, ~1 will be "significant" at p<0.05 *even if nothing is real.* If you test many things, **correct for it** (Bonferroni, false-discovery-rate) or you'll "find" noise.
- **The garden of forking paths** — even without malice, making analysis choices *after* seeing the data quietly inflates false positives.
- **HARKing** — Hypothesizing After Results are Known: inventing the hypothesis to fit the result, then presenting it as if predicted. ([[research/04-research-questions-and-hypotheses|confirmatory vs exploratory]] honesty.)
- **Cherry-picking** — reporting the best run/dataset/metric and hiding the rest.

The defenses are the same few: **pre-register** the analysis, **correct for multiple comparisons**, keep a clean **test set touched once**, and **report everything you tried** (not just what worked). These live on a spectrum from honest-mistake to [[research/07-research-ethics-and-integrity|misconduct]] — the fix is transparency.

## From numbers to meaning

Finally, *interpret*: connect the result back to the [[research/04-research-questions-and-hypotheses|question]]. What does it **mean** for the field? Why did it come out this way (mechanism, not just outcome)? What are the **limitations** — the conditions under which it might not hold? Honest interpretation states what you learned, why it matters, and where the edges are — it doesn't oversell, and it doesn't leave the reader to guess what the table of numbers was *for*.

*(For **qualitative** work, "analysis" means systematically **coding** data into themes, **triangulating** across sources, and checking **inter-rater reliability** — rigor there is about transparent, defensible interpretation rather than p-values.)*

## Key insight

**Numbers don't tell you whether they're signal or luck — you have to, and the pull to believe the flattering ones is strong.** Report **variance, not bare means** (overlapping error bars ≈ no difference), use significance tests + **effect sizes** to separate real from noise, and never confuse *statistical* significance with *mattering*. State the **narrowest claim the data supports** with its scope attached (higher-here ≠ better; correlation ≠ causation), actively **hunt the boring explanation** before celebrating, and treat **negative results** as real knowledge. Avoid the fooling-yourself failure modes — **p-hacking, multiple comparisons, HARKing, cherry-picking** — with pre-registration, multiple-comparison corrections, a once-touched test set, and reporting everything you tried. Honesty here *is* the science.

## Related
- [[research/05-methodology-and-experiment-design|Methodology & Experiment Design]] — the design that makes analysis trustworthy
- [[research/04-research-questions-and-hypotheses|Research Questions & Hypotheses]] — H₀/H₁, confirmatory vs exploratory
- [[research/07-research-ethics-and-integrity|Ethics & Integrity]] — where p-hacking crosses into misconduct
- [[ai-ml/01-data-scientist/03-inferential-statistics|Inferential Statistics]] — significance, CIs, the stats in depth
- [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability & Statistics]] — the foundations underneath
