# The Audit Process

**[Intermediate]** — what an audit is and isn't, how to prepare for one, how to read a report, and what an audit badge actually tells you.

## What an audit is

**A time-boxed manual review by security specialists, producing a report of findings.** Typically 1–4 weeks, 2–4 auditors, and a cost from around $20k for something small to hundreds of thousands for a large protocol.

**What it is not:**

- **Not a guarantee.** Audited protocols get exploited regularly, including by bugs that were in scope
- **Not a proof.** It's expert human review, sampling a space it cannot exhaust
- **Not a substitute for your own testing.** Auditors reviewing untested code spend the engagement finding bugs your test suite should have caught — the most expensive possible use of them
- **Not permanent.** It covers a specific commit. Change one line and it no longer describes your code

**What it genuinely provides:** a second set of adversarial eyes, from people who have seen how these systems fail. That is worth a great deal, and it is not the same as safety.

## Preparing — this determines what you get

Auditors bill by the week. Every hour spent understanding your intent is an hour not spent finding bugs.

**Before you engage:**

1. **Freeze the code.** A moving target wastes the engagement, and mid-audit changes are unreviewed by definition
2. **Write the tests first.** High coverage, plus fuzz and invariant tests. **Anything your own tests catch is money saved**
3. **Run Slither and fix everything real.** Auditors reporting what a free tool found is a waste of the budget
4. **Document the intent** — what each contract does, what the invariants are, what's trusted, what's out of scope, what the privileged roles can do. **This is the highest-value preparation**, because auditors find logic bugs by comparing intent to implementation, and without stated intent they can only guess it
5. **Explicit threat model.** "We assume the oracle is honest." "We assume the multisig is not compromised." Auditors will challenge these, which is the point
6. **NatSpec on every external function**

**A useful test of readiness:** if you can't write a one-page document stating your protocol's invariants, you are not ready to be audited — you're not yet clear on what "correct" means for your own system.

## Severity, and how it's judged

```
              IMPACT
              High        Medium      Low
   High   │  Critical  │  High     │  Medium
LIKELIHOOD Medium │  High      │  Medium   │  Low
   Low    │  Medium    │  Low      │  Info
```

- **Critical** — direct loss of funds, likely. Fix before deploying, no exceptions
- **High** — loss of funds under specific conditions, or a permanent freeze
- **Medium** — value leak, griefing, or a broken assumption without direct theft
- **Low / Informational** — style, gas, defence-in-depth, documentation

**Findings are negotiable, and that's legitimate.** You may dispute severity or accept a risk with a written rationale. What isn't legitimate is quietly marking something "acknowledged" and shipping — the acknowledgement is public in the report, and the reasoning should stand up.

## The kinds of audit

| Kind | What it is | When |
|---|---|---|
| **Traditional firm** | A fixed team, fixed weeks, private report. Trail of Bits, OpenZeppelin, Spearbit, Consensys Diligence | The default. Deep, contextual review |
| **Competitive audit** | Public contest, dozens–hundreds of researchers, prize pool by findings. Code4rena, Sherlock, Cantina | Broad coverage, excellent for well-specified scopes. Enormous duplicate/noise volume |
| **Bug bounty** | Ongoing, pay-per-finding. Immunefi | **Continuous, and covers the code you have now rather than a frozen commit.** Should be permanent, not a phase |
| **Formal verification** | Machine-checked proofs of stated properties. Certora, Halmos | High-value core invariants. Expensive; proves only what you thought to state |

**A serious protocol does several.** The strongest common pattern is: firm audit → competitive audit → permanent bug bounty → staged rollout with deposit caps.

## Reading someone else's audit report

When evaluating a protocol you didn't write — which is most of the time — these questions are the whole exercise:

1. **What commit was audited, and is it what's deployed?** Check the hash. **This alone eliminates a lot of "audited" projects**
2. **What was in scope?** Reports state it explicitly. The exploited contract is often the one excluded
3. **Were the findings fixed, or just acknowledged?** Read the resolution column
4. **Who audited it?** Reputations vary enormously, and there is a market in cheap logo-supplying reports
5. **How many criticals were found?** **A report with many criticals found and fixed is often a better signal than a clean one** — a clean report can mean the code was excellent, or that the review was shallow
6. **How old is it?** An audit of a protocol that has shipped three upgrades since describes different code

**"Audited by X" as a marketing badge, with no linked report, means nothing at all.** Ask for the report; if it isn't public, that is itself the answer.

## What auditors actually find

In rough order of frequency:

1. **Logic errors** — the code correctly implements the wrong thing. **No tool finds these, and this is the real value of an audit**
2. **Missing validation** — an unchecked input, an unchecked return value, a missing bound
3. **Broken assumptions** — "we assumed this token is standard"; "we assumed this is called once"
4. **Access control gaps** — a function that should have been restricted
5. **Precision and rounding** — the direction chosen wrong → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|arithmetic]]
6. **Integration bugs** — how your contract behaves against the *real* Uniswap, the *real* USDT

**Reentrancy and overflow are rarely the finding any more** — tooling and the 0.8 compiler handle them. The bugs that survive are the ones that require understanding what the protocol is *supposed* to do.

## After the audit

- **Fix, then get the fixes reviewed.** Fixes introduce bugs; a fix-review round is standard and worth paying for
- **Publish the report.** Refusing to is a signal
- **Deploy with caps.** Limit deposits initially and raise them as confidence accumulates. **Cheap, effective, and often skipped**
- **Monitor, with a pause switch and a rehearsed response.** Knowing about an exploit without a tested procedure is not much use at 3am
- **Keep the bounty open forever**

## Key insight

**An audit is a sample of the bug space by experts, not a proof of correctness — and its value is bounded by how well you specified what "correct" means.** The teams that get the most from audits arrive with tests, documented invariants, and a stated threat model, so the auditors spend their weeks on logic errors rather than reading code and guessing intent.

## Related
- [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing and tooling]] — what to do before
- [[web3/04-smart-contract-security/08-case-studies|case studies]] — audited protocols that were exploited anyway
- [[cybersecurity/08-governance-risk-and-compliance/README|governance, risk and compliance]] — the general discipline
- [[web3/04-smart-contract-security/01-why-this-is-different|why security is different here]]

*Source: [reference] — Aug 2026.*
