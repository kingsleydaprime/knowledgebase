# Identity and Naming

**[Intermediate]** — ENS, the Sybil problem, and why decentralised identity is the field's most important unsolved problem.

## Why this matters more than it looks

**Almost every hard problem in this folder reduces to not being able to tell people apart:**

- [[web3/07-the-application-layer/03-daos-and-governance|Governance]] is plutocratic because one-person-one-vote requires knowing what a person is
- [[web3/07-the-application-layer/01-defi-primitives|Lending]] must be over-collateralised because anonymous default is free
- Airdrops are farmed by thousands of wallets belonging to one person
- Spam and Sybil attacks are unpreventable because identities are free

**Blockchains deliberately made identity free and unlimited — that's what "permissionless" means — and then inherited every problem that follows.** Solving it without reintroducing a central authority is genuinely hard, and it's the field's most consequential open problem.

## ENS — the clear success

The Ethereum Name Service maps human-readable names to addresses and much else:

```
vitalik.eth  →  0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
             →  a content hash (an IPFS site)
             →  an avatar, a text record, other chains' addresses
```

**Why it works when so much else hasn't:**

- **It solves a real, felt problem.** Nobody wants to paste a 42-character hex string, and sending to a wrong address is irreversible
- **The token *is* the asset.** An ENS name is an NFT, and there's no off-chain thing it points at that could disappear → [[web3/07-the-application-layer/02-nfts-in-practice|NFTs in practice]]
- **Renewal fees** prevent permanent squatting and fund the protocol
- **It's a general resolver**, not just addresses — content hashes let you host a censorship-resistant frontend at `yourapp.eth` → [[web3/06-building-dapps/05-decentralised-storage|storage]]

**Support ENS in any dapp you build.** Resolve names in inputs and display them instead of addresses — it's a small change that measurably reduces the most costly user error there is.

Others exist (Unstoppable Domains, Solana's SNS, Farcaster names). ENS is the one with real integration.

## The Sybil problem

**Creating an address is free and unlimited**, so any system distributing anything per-address is farmed:

- **Airdrops** — professional farmers run thousands of wallets, each performing the qualifying actions. **A large fraction of most airdrops goes to farmers**, not users
- **Governance** — splitting tokens across wallets is trivial (though token-weighting means it doesn't help, which is why plutocracy is the *stable* equilibrium)
- **Quadratic funding** — collapses entirely without Sybil resistance, since it weights by contributor count

**You cannot solve this with cleverness on-chain.** Something outside the chain must attest that an identity is distinct — and that something is a trusted party, which is the thing being avoided.

## The approaches, and their honest status

**Proof of personhood.**

**Worldcoin** scans irises to produce a unique biometric hash. Technically ambitious, with zero-knowledge proofs so the biometric isn't stored. **Banned or investigated in multiple jurisdictions** (Spain, Portugal, Kenya, Hong Kong) over biometric data collection, and the practice of gathering iris scans from people in low-income countries in exchange for tokens drew heavy criticism. **The clearest illustration of the trade: to prove uniqueness you must collect something unique about a person, and that is exactly what privacy law restricts.**

**Proof of Humanity / BrightID** use social graphs and video verification. Less invasive, much smaller scale, and harder to grow.

**Verifiable credentials and DIDs.** W3C standards for issuer-signed claims you hold and present selectively, ideally with a zk proof so you reveal "over 18" rather than a birthdate. **Technically sound, standards-mature, and adoption remains limited** — the bottleneck is that issuers (governments, universities, employers) must participate, and they mostly haven't.

**Soulbound tokens.** Non-transferable tokens representing credentials, attendance or membership. **The right primitive for credentials**, since transferability defeats the purpose. ERC-5192 standardises them. Modest adoption, and no answer to the underlying uniqueness problem — a person can still hold many wallets.

**Attestations.** The Ethereum Attestation Service lets anyone sign a claim about anything. **A useful primitive rather than a solution** — it moves the problem to "whose attestations do you trust," which is a social question, not a technical one.

**On-chain reputation.** Score an address by its history — transactions, repayments, longevity. Cannot distinguish "one honest person" from "one of a farmer's thousand wallets," but it does raise the cost of farming, and it's the basis of the tentative work on under-collateralised lending.

## The unavoidable tension

**Every approach that actually works reintroduces a trusted party or collects personal data.** That's not a failure of imagination — it's structural:

> **Proving uniqueness requires something unique to a person, and something must vouch that it is.**

The genuine progress is in **selective disclosure**: zero-knowledge proofs let you prove a credential's *implication* without revealing the credential — "I hold a passport from an EU country" without which country, which passport, or which person → [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zk proofs]]. **That's real, and it narrows the trade rather than eliminating it:** you still trust the issuer, but you no longer expose the data to every verifier.

## What's usable today

- **ENS** for naming. Mature, use it
- **Sign-In With Ethereum (EIP-4361)** for authentication. Standardised and simple → [[web3/06-building-dapps/02-wallets-and-connection|wallets]]
- **Attestations** for application-specific claims where you choose the trusted issuers
- **Soulbound tokens** for credentials
- **Nothing** for general-purpose Sybil resistance. If your design needs it, **design around it instead** — cap per-address impact, use time-weighting, or accept a trusted issuer explicitly

## Key insight

**Permissionless means identities are free, and free identities break every one-per-person mechanism.** This is a design consequence, not an oversight — and it's why governance is plutocratic, lending is over-collateralised and airdrops are farmed. The field's most valuable open problem is proving uniqueness without a central authority, and every partial answer so far trades away either privacy or decentralisation.

## Related
- [[web3/07-the-application-layer/03-daos-and-governance|DAOs and governance]] — where this bites hardest
- [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zero-knowledge proofs]] — selective disclosure
- [[web3/06-building-dapps/02-wallets-and-connection|wallets and connection]] — SIWE
- [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]] — the ordinary version
