# Energy and the Externalities

**[Intermediate]** — the numbers, what the Merge actually changed, and the criticisms that survive it.

## The proof-of-work numbers

Bitcoin's electricity consumption is on the order of **100–150 TWh per year** — comparable to a mid-sized country. Estimates vary by methodology (the Cambridge CBECI and Digiconomist differ meaningfully), but the order of magnitude isn't disputed.

**The uncomfortable part is that this is by design, not inefficiency.**

> **The energy expenditure *is* the security.** An attacker must out-spend the honest network, so the cost of attack is proportional to the ongoing cost of operation. **You cannot make proof-of-work cheap without making it weak** → [[web3/01-foundations/05-consensus|consensus]].

There is no optimisation available. Better hardware raises hashrate, difficulty adjusts, and consumption returns to whatever the block reward supports. **The energy use is a function of the reward, not of efficiency.**

## The Merge — what actually changed

Ethereum's move to proof-of-stake in September 2022 cut its energy use by **roughly 99.95%**, from tens of TWh per year to a few GWh — comparable to a large office building rather than a country.

**This is the single largest emissions reduction of any computing platform, and it happened in one day.** It's also the strongest evidence against the claim that this energy use is inherent to blockchains: **it isn't, it's inherent to proof-of-work**, and one major chain simply stopped.

**Which reframes the debate.** Most remaining energy use is Bitcoin, which will not change — its conservatism is deliberate, and its community regards PoW as essential rather than incidental → [[web3/05-beyond-ethereum/05-bitcoin-and-utxo|Bitcoin]].

## The arguments, weighed

**"It uses renewables."** Partly true — a substantial and growing share, since miners chase cheap power and stranded renewables are cheap. **The counter is real too:** demand that can be sited anywhere still competes for clean generation that would otherwise displace fossil fuels elsewhere. **Using renewable energy isn't the same as being carbon neutral** when the grid as a whole is not.

**"It monetises stranded and flared energy."** Genuinely true in specific cases: flared gas at oil wells, curtailed hydro. A real efficiency gain where it happens, and a small share of total consumption.

**"It's grid-stabilising."** Miners can shut down within seconds, making them useful demand response — demonstrated in ERCOT (Texas). Real, and it also means miners are paid to *not* compute, which is a strange thing to defend as efficiency.

**"Banking uses more energy."** The comparison is usually constructed unfavourably (including bank branches and ATMs against Bitcoin's mining alone) and, more importantly, **it's a comparison of systems with vastly different transaction volumes.** Per-transaction figures are also misleading in the other direction, since energy tracks the block reward, not transaction count. **The honest framing is: Bitcoin consumes a country's worth of electricity to secure a settlement network, and whether that's worth it depends on how much you value what it settles.**

**"E-waste."** Less discussed and real: ASICs are single-purpose and obsolete within a few years, producing tens of thousands of tonnes annually. Unlike energy, this has no renewable offset.

## The other externalities

**Wealth concentration.** Early adopters hold disproportionate supply, and proof-of-stake compounds it structurally — **stake earns stake**, so relative holdings grow without any productive activity. Whether this is worse than existing financial concentration is arguable; **that it's a redistribution upward is not.**

**Fraud harm.** Billions annually, concentrated on the least sophisticated participants. **Pig butchering operations involve human trafficking** — a serious harm the field rarely counts as its own → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]].

**Ransomware.** Crypto did not create ransomware, but pseudonymous, irreversible cross-border payment made it dramatically more scalable. **This is a genuine causal contribution to a real and growing harm**, and it is the criticism the field engages with least honestly.

**Opportunity cost.** A great deal of excellent engineering talent has gone into financial infrastructure for trading tokens. **This is a legitimate criticism** that doesn't depend on any technical claim being wrong.

## Holding it honestly

**Both of these are true:**

**The energy criticism has been substantially answered for proof-of-stake chains.** Ethereum uses negligible energy, and continuing to cite pre-2022 figures for it is simply out of date. Most new chains are PoS.

**It has not been answered for Bitcoin, and won't be.** The consumption is deliberate, and defences that begin "but banking..." are deflections. **The honest position is that Bitcoin's energy use is real, large, permanent, and a cost you are trading against whatever value you place on a censorship-resistant settlement network.**

**And the non-energy externalities are the ones with the weakest defences** — fraud harm, ransomware enablement and wealth concentration are less discussed than energy and, arguably, matter more.

## Key insight

**"Blockchains waste energy" was always really "proof-of-work costs energy, and that cost is the security."** Ethereum proved the criticism was contingent by eliminating 99.95% of its consumption overnight; Bitcoin demonstrates it's permanent where PoW is retained. **The field's remaining hard externalities aren't environmental — they're the fraud, the ransomware and the concentration**, which have no equivalent technical fix waiting.

## Related
- [[web3/01-foundations/05-consensus|consensus]] — why PoW costs what it costs
- [[web3/02-ethereum-and-the-evm/06-the-ethereum-roadmap|the Ethereum roadmap]] — the Merge
- [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]]
- [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|what blockchains are actually good for]]

*Source: [reference] — figures approximate, Aug 2026. Cambridge CBECI is the standard reference for Bitcoin consumption.*
