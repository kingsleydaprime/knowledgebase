# Regulation and the Legal Layer

**[Intermediate]** — the constraint that has shaped the field more than any technical limit. **Written Aug 2026; this note dates fastest of any in the folder, and it is not legal advice.**

## The premise that failed

The founding assumption was that sufficiently decentralised systems sit outside jurisdiction. **That has not held.**

Courts and regulators consistently reach the **people** — developers, founders, front-end operators, liquidity providers, DAO participants. **A protocol may be unstoppable; the humans who wrote and promote it are not.**

Three cases established this clearly:

- **Mango Markets (2022)** — the exploiter argued publicly that the protocol permitted his trades. He was prosecuted in the US for fraud and market manipulation. **"The code allowed it" is not a defence** → [[web3/04-smart-contract-security/08-case-studies|case studies]]
- **Tornado Cash (2022)** — OFAC sanctioned a *smart contract address*, and a developer was convicted in the Netherlands for money laundering through writing and maintaining the tool. **The US sanctions were later challenged successfully in part** (a court held immutable contracts aren't sanctionable "property"), and the prosecutions of developers proceeded regardless. **Writing privacy software carries demonstrated legal risk**
- **bZx DAO (2023)** — a US court allowed a claim treating a DAO as a **general partnership**, potentially making token-holding participants personally liable → [[web3/07-the-application-layer/03-daos-and-governance|DAOs]]

## The questions regulators are actually asking

**1. Is this a security?** The dominant question in the US. The **Howey** test asks whether there's an investment of money in a common enterprise with an expectation of profit from the efforts of others.

The SEC's position for years was that most tokens are securities, pursued through enforcement rather than rulemaking — **criticised across the political spectrum as "regulation by enforcement."** Court outcomes have been mixed and genuinely nuanced: the *Ripple* decision distinguished **institutional sales** (securities) from **programmatic exchange sales** (not), which pleased nobody and clarified less than either side claimed. The regulatory posture has shifted considerably since 2024, and **anything you read about US token classification more than a year old is probably stale.**

**2. Is this money transmission?** Running an exchange or custodying assets triggers licensing (US MSB/state licences, EU authorisation) plus AML/KYC obligations.

**3. Who is liable when it breaks?** Founders, front-end operators and, per bZx, potentially DAO participants.

**4. How is it taxed?** In most jurisdictions **every disposal is a taxable event** — including token-to-token swaps, which surprises people badly. DeFi creates enormous numbers of them.

## The regimes, briefly

**EU — MiCA.** The first comprehensive framework, fully applicable since December 2024. Licensing for service providers, strict stablecoin rules (reserve and redemption requirements), and market-abuse provisions. **Its significance is that it exists**: predictable rules, even strict ones, are what businesses need, and MiCA has drawn activity to the EU on that basis alone.

**United States.** Historically fragmented — SEC, CFTC, FinCEN, OCC, plus fifty states — with jurisdiction contested between the SEC and CFTC. Direction has changed markedly since 2024 and legislation has advanced; **the specifics move too fast for a note like this to be reliable.**

**Elsewhere.** Singapore, UAE, Switzerland and Hong Kong offer clearer, generally accommodating regimes. **China bans trading and mining while pursuing its CBDC.** India taxes heavily. Nigeria, Turkey and Argentina show high grassroots adoption with unsettled and shifting official positions.

## What this means for building

**Take these seriously regardless of your views on them:**

- **A front-end is a regulated surface.** Sanctioned-address blocking and geoblocking are now standard for DeFi front-ends, and operators have been pursued. The protocol may be neutral; **your website is a service you provide**
- **Fundraising via token sale is securities activity in most jurisdictions.** Get counsel before, not after
- **KYC/AML applies if you custody or exchange.** Non-custodial design isn't a loophole so much as a genuinely different activity — but the line is contested
- **Wrap your DAO in a legal entity.** Wyoming DAO LLC, Marshall Islands, Swiss association. Unwrapped DAOs may expose participants to personal liability
- **Privacy tooling carries real risk to its authors**, and that is a fact to plan around rather than an injustice to ignore
- **Keep records.** Tax authorities increasingly receive exchange data directly, and the OECD's CARF extends reporting internationally

## The honest tension

**Two things are true at once, and most commentary picks one:**

**Regulation addresses real harm.** FTX was fraud. Pig butchering is organised crime. Most token launches transfer money from unsophisticated buyers to insiders. **Consumer protection and anti-fraud enforcement are not attacks on the technology** → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]].

**And regulation is genuinely awkward here.** Securities law assumes an issuer; permissionless protocols may have none. AML assumes an intermediary; there may be none. Sanctioning a contract address does nothing to the contract and everything to the people who wrote it. **Prosecuting developers for writing tools raises real questions about code as speech** — questions with a history, from the 1990s cryptography export fights.

**Both are true.** The field's tendency to treat all regulation as persecution, and the regulatory tendency to treat the whole field as fraud, are each half-right and both unhelpful.

## Key insight

**Decentralisation is a property of a protocol, not a shield for the people around it** — and every enforcement action has landed on people: developers, founders, front-end operators, participants. The technical question "can this be stopped?" and the legal question "will someone be prosecuted?" have completely different answers, and conflating them has been the field's most expensive category of mistake.

## Related
- [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]] — what regulation responds to
- [[web3/07-the-application-layer/03-daos-and-governance|DAOs]] — legal status
- [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zk proofs]] — Tornado Cash and privacy tooling
- [[cybersecurity/08-governance-risk-and-compliance/README|governance, risk and compliance]]

*Source: [reference] — Aug 2026, and deliberately dated. Verify anything jurisdiction-specific before acting on it. Not legal advice.*
