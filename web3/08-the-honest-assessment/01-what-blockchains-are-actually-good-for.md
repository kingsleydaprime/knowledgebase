# What Blockchains Are Actually Good For

**[Intermediate]** — the test that kills most proposals, the cases that survive it, and why that's still worth learning.

## The test

**A blockchain is a slow, expensive, public database with no administrator.** You accept all of the first three to get the fourth. So:

> **Is there any party who could be trusted to run this, and if so, use a database.**

That's the whole test, and it eliminates the large majority of blockchain proposals — including nearly every enterprise pilot from 2016–2020, most supply chain projects, and essentially every "blockchain for X" where X has a natural operator.

**The extended version, four questions:**

1. **Do the participants distrust each other?** If not, one of them can run the database
2. **Is there an acceptable administrator?** If yes, use them. They'll be faster, cheaper and fixable
3. **Does the data originate on-chain?** If a human types it in, **the chain guarantees the record wasn't altered, not that it was ever true**
4. **Does anything break if a company shuts down?** If not, you didn't need censorship resistance

## What survives — and it's a real list

**1. Censorship-resistant value transfer.** Sending money that no intermediary can block. This is the original use case and it remains the strongest.

**Concretely useful where the alternative is bad:** remittances to countries with expensive or restricted corridors; holding savings under high inflation or capital controls — **Argentina, Turkey, Nigeria, Venezuela have real, non-speculative stablecoin usage**, driven by currency collapse rather than ideology; and payments to people excluded from the banking system for political reasons.

**This is not a hypothetical benefit, and it's the case Western critiques most often miss** because dollar-denominated bank accounts make the problem invisible.

**2. Trust-minimised coordination between adversaries.** Escrow, settlement and clearing between parties with no basis for trust and no shared jurisdiction. Where a neutral operator either doesn't exist or would be too powerful.

**3. Credibly permanent commitments.** Rules that cannot be changed later, *provably* — an immutable contract, a fixed supply, a distribution nobody can alter. **The value is in the impossibility of the change**, and no ordinary system can offer that, because "we promise not to" is always revocable.

**4. Permissionless composability.** Anyone can build on a deployed contract without asking. No API keys, no terms of service, no revocation. **This is genuinely novel and underrated** — it's why DeFi assembled as fast as it did, and there's no equivalent in ordinary software → [[web3/07-the-application-layer/01-defi-primitives|composability]].

**5. Verifiable computation.** The zk proof machinery is a genuine primitive that didn't exist before — proving a computation was performed correctly, cheaply, without redoing it. **Its applications extend well beyond blockchains** → [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zk proofs]].

**6. Public, permanent registries where the entry *is* the asset.** ENS names, on-chain art, DAO membership. Not pointers to things elsewhere — the record itself → [[web3/07-the-application-layer/04-identity-and-naming|ENS]].

## What doesn't survive, and why

**Supply chain provenance.** The chain preserves what was written, not whether it was true. Someone scans a QR onto a pallet, and a lie is now permanent and tamper-proof. **Garbage in, immutable garbage out** → [[web3/06-building-dapps/06-oracles|the oracle problem]].

**Enterprise consortium chains.** Known participants, a shared operator, no censorship concern. **A replicated database with signed writes is the same thing at a thousandth of the cost**, and this is broadly what those projects concluded.

**Voting in public elections.** A public ledger makes vote-buying *verifiable*, which is worse than the problem it solves. Secret ballots exist for good reasons, and the failure modes of election systems are overwhelmingly about identity, coercion and endpoint security — none of which a chain addresses.

**Most identity.** Needs a trusted issuer, which is the thing being avoided → [[web3/07-the-application-layer/04-identity-and-naming|identity]].

**Storing files.** Wildly more expensive than any alternative, for content addressing you can get from a hash → [[web3/06-building-dapps/05-decentralised-storage|storage]].

**Anything needing speed, privacy, or the ability to fix a mistake.**

## The honest summary

**Blockchains are a narrow, expensive tool that does one thing nothing else does: maintain agreed state among parties who don't trust each other, without an administrator.**

That is genuinely valuable in a small number of situations, and **the field has spent enormous energy pretending it's valuable in a large number.** Most of the value created has been financial — trading, speculation and the infrastructure serving them — plus a real, under-reported base of people using stablecoins because their own currency failed them.

**A blockchain in an application where a database would do isn't neutral — it's strictly worse**: slower, costlier, publicly leaking your data, and unfixable when wrong.

## Why learn it anyway

**Because it's a genuinely interesting piece of distributed systems engineering**, and because the surviving use cases are real. Also:

- **The engineering transfers.** Adversarial thinking, invariant-based design, and building where you cannot patch make you better at everything else
- **The economics are novel.** Mechanism design where the code enforces incentives is a real discipline, applicable well beyond chains
- **The cryptography is real.** zk proofs and threshold signatures matter regardless of what happens to crypto markets
- **It employs people well**, and knowing it properly — including its limits — makes you far more useful than the average practitioner

**Learn it as a distributed systems specialisation with a strong adversarial security component.** That framing is accurate, it survives market cycles, and it's what the good engineers in the field actually do.

## Key insight

**Ask "who would I have to trust, and can I?" — if there's an acceptable answer, you don't need a blockchain.** That question resolves nearly every proposal in seconds, and being the person in the room who asks it is more valuable than being the person who can write Solidity.

## Related
- [[web3/01-foundations/01-what-web3-actually-is|what web3 actually is]] — the same argument, at the start
- [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]]
- [[web3/07-the-application-layer/05-gaming-and-the-rest|gaming and the rest]] — the four-question test applied
- [[architecture/04-distributed-systems/README|distributed systems]] — the field this belongs to
