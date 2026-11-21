---
id: a941daa8-887e-48ff-80d7-a86870acbab9
---

# DAOs and Governance

A DAO is a group that makes decisions by voting on a blockchain, where the winning vote carries out the decision automatically. Votes are counted by how many tokens each person holds, not one vote per person. This lesson shows how DAOs work and why a few large holders often decide the outcome.

## The kid version first
<!-- bite: 68d027d2-1bda-4783-af46-83be71aa1797 -->

A DAO is **a group that makes decisions by on-chain vote, where the vote directly executes the outcome.** No board, no bank account requiring signatures, no incorporation.

The catch: **votes are weighted by tokens.** One person with a lot of tokens outvotes a thousand people with few. **"Decentralised" in the name is a claim about the mechanism, not about the power distribution.**

## The mechanism
<!-- bite: 6ab744d0-933d-4b94-b3f0-c5cbf403ee23 -->

The standard stack, and it's genuinely well-engineered:

```text
Governance token  (ERC20Votes — balances are checkpointed per block)
        │
   Governor contract:
     propose  → a proposal is (targets, values, calldatas)
     delay    → voting doesn't start immediately
     vote     → for / against / abstain, weighted by tokens at the SNAPSHOT block
     quorum   → minimum participation required
     succeed  → queued into a Timelock
        │
   Timelock (48h+)  ← the window where a malicious proposal can be seen and exited
        │
   execute → the Timelock CALLS the targets. The vote directly performs the action
```

**Two details carry most of the security:**

**Snapshot voting.** Voting power is read at the block a proposal was created, so **you cannot flash-loan tokens, vote, and repay** — the exploit this defends against, and it's not hypothetical: **Beanstalk lost ~$182M in April 2022** to exactly that, via a proposal that passed with borrowed voting power and transferred everything to the attacker.

**The timelock.** Nothing executes immediately. It's the same protection as in [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|upgradeability]]: it converts a silent capture into a public one, and gives users time to exit.

**Off-chain signalling** (Snapshot) is used for most votes — gasless, signature-based, non-binding. The binding on-chain vote follows for things that actually move funds.

## The problems, stated honestly
<!-- bite: a81a28ae-37d7-457c-9acf-35c94d35e1e8 -->

**1. Plutocracy.** One token one vote means wealth is power, directly. Founders, VCs and early holders often control a majority outright, and "community governance" describes the process rather than the outcome. **This is the central unresolved problem, and no proposed fix has worked at scale.**

**2. Voter apathy.** Participation is routinely in the low single digits of supply. Most holders never vote, which means a small active minority — usually large holders and delegates — decides everything. **Quorum requirements are frequently unmet**, and proposals fail through indifference rather than opposition.

**3. Vote buying and delegation markets.** Voting power is a transferable asset, so it can be rented. Bribe markets exist openly — **Curve's "bribe" ecosystem, where protocols pay veCRV holders to direct emissions, is a multi-billion-dollar market that is simply vote buying with better branding.** Whether that's corruption or an efficient market for governance is genuinely debated.

**4. Governance attacks.** Acquire enough tokens to pass a proposal that drains the treasury. Rational whenever the treasury is worth more than the tokens needed to control it — **and several DAOs have traded below the value of their own treasury**, making the attack straightforwardly profitable.

**5. Nobody reads proposals.** Voting on a proposal means voting on `(targets, values, calldatas)` — raw bytes. **Almost nobody verifies that the calldata does what the description says.** This is a live risk and it has been exploited.

**6. Speed.** A timelocked governance process cannot respond to an exploit in progress. Every serious protocol therefore keeps an **emergency multisig** that can pause without a vote — **which means the "decentralised" protocol has a small group who can halt it**, and that group is the real answer to "who controls this."

## What has actually worked
<!-- bite: f8224de2-1567-4205-bf8a-0a4516a3d0a8 -->

**Delegation.** Holders delegate to active delegates who research and vote. Concentrates informed participation without requiring everyone to engage. **The most successful mechanism so far**, and it recreates representative democracy with all its trade-offs.

**Optimism's Citizens' House.** A bicameral design: Token House (token-weighted) and Citizens' House (identity-weighted, non-transferable). **The most serious deployed attempt at escaping plutocracy**, and worth watching.

**Narrow scope.** DAOs governing a few parameters (fee rates, collateral factors) work far better than DAOs attempting to run an organisation. **Governance is good at bounded decisions with clear options and bad at open-ended management.**

**Quadratic funding.** Gitcoin Grants weights by the *number* of contributors rather than amount, favouring broad support over concentrated wealth. Works well for public-goods funding; requires Sybil resistance, which is unsolved in general → [[web3/07-the-application-layer/04-identity-and-naming|identity]].

## The legal reality
<!-- bite: cea93a32-4aa5-4121-835d-1855af328dbc -->

**A DAO is not a legal entity by default**, and this matters more than most participants realise:

- **A US court has treated a DAO as a general partnership** (*Sarcuni v. bZx DAO*, 2023), which would make **token-holding participants personally liable** for its obligations
- DAOs cannot easily hold bank accounts, sign contracts, employ people, or pay taxes as an entity
- **Wyoming, the Marshall Islands and others now offer DAO LLC structures** — most serious DAOs now wrap themselves in a legal entity, which reintroduces jurisdiction and a legal identity

**"Code is the only law" does not survive contact with a court** → [[web3/08-the-honest-assessment/03-regulation-and-the-legal-layer|regulation]].

## Key insight
<!-- bite: 61e05e24-50d8-4f45-ac95-0efba769c407 -->

**DAO tooling is good; DAO governance is hard, and the hard part isn't technical.** Snapshot voting, timelocks and on-chain execution are solid mechanism design that solves the problems it can solve. What it cannot solve is that token-weighted voting is plutocracy by construction — and every attempt to escape it needs a way to tell people apart, which is exactly the problem blockchains chose not to solve.

## Related
<!-- bite: a9ea28c2-7f4b-43b8-8aea-10a6d5ec8c4f -->
- [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|upgradeability]] — timelocks, and who holds the keys
- [[web3/07-the-application-layer/04-identity-and-naming|identity]] — the Sybil problem underneath all of it
- [[web3/08-the-honest-assessment/03-regulation-and-the-legal-layer|regulation]]
- [[web3/04-smart-contract-security/08-case-studies|case studies]] — Beanstalk

## About this lesson
<!-- bite: 69a4ee81-39ac-43b4-ba63-5fe43cd3ad28 -->

**Level:** Intermediate. **Covers:** how on-chain governance works, why token voting keeps producing plutocracy, and what a DAO actually is legally.
