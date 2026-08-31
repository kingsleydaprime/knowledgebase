# Scams, Rugs and the Fraud Surface

**[Beginner]** — how people actually lose money, which is mostly not smart contract exploits.

## Why this note is in a technical folder

**Because the losses are overwhelmingly not technical.** Reading about reentrancy while getting phished is the field's characteristic failure, and the properties that make blockchains useful — irreversibility, pseudonymity, permissionless deployment, no recourse — are **exactly** the properties that make fraud efficient.

**This is not a bug in crypto culture. It's a structural consequence of the design**, and it should be taught as part of the design.

## Why fraud works so well here

| Property | Why it's good | Why fraud loves it |
|---|---|---|
| Irreversible | No chargebacks, final settlement | **No recovery, ever** |
| Permissionless | Anyone can build | **Anyone can deploy a scam for $5** |
| Pseudonymous | Privacy | **Hard to attribute, easy to vanish** |
| No intermediary | No gatekeepers | **No fraud department, no one to call** |
| Composable | Build on anything | **Malicious contracts compose too** |
| Global | Anyone can participate | **Jurisdictional arbitrage** |

## The catalogue

**Phishing — the largest single cause of individual loss.**

A fake site, a fake airdrop, a fake support agent, a poisoned search ad. The victim connects a wallet and signs something. **The signature is often `setApprovalForAll` or a `permit`** — it doesn't move funds *now*, so nothing looks wrong, and the wallet is drained later.

**"Wallet drainer" kits are sold as a service.** This is an industry with products and customer support.

Defences: **never sign anything you can't read** → [[web3/06-building-dapps/02-wallets-and-connection|signatures]]; bookmark real sites and never use search ads; a hardware wallet for anything meaningful; a separate "hot" wallet for interacting with new protocols; and **revoke old approvals periodically** (revoke.cash).

**Address poisoning.** The attacker sends a zero-value transfer from an address whose first and last characters match one you use. Later you copy the address from your transaction history — and send to theirs. **Always verify the middle characters, and use an address book or ENS.**

**Rug pulls.** The team takes the money. Variants: the liquidity pool is drained (**"soft rug"**); a hidden mint function creates unlimited tokens; a `blacklist` prevents everyone but the deployer from selling (**"honeypot"** — you can buy and never sell); or the contract is upgraded into something that drains it → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|upgradeability]].

**Deploying a token costs a few dollars and requires nobody's permission**, so this is manufactured at industrial scale → [[web3/01-foundations/07-tokens-coins-and-nfts|tokens]].

**Pump and dump.** Coordinated buying, promotion, then selling into the retail bid. **Ordinary securities fraud, executed on assets with no securities regulation and no disclosure requirements.** Now largely automated on memecoin launchpads.

**Ponzi and "yield" schemes.** Returns paid from new deposits. **Any protocol paying high fixed yields with no explicable source is paying you with someone else's deposit** — Anchor's 20% on UST was the largest example, and it worked exactly as long as inflows continued.

**"Pig butchering."** Long-form romance and investment fraud, often run from trafficked labour compounds in Southeast Asia — a serious organised-crime and human-rights problem, not just a financial one. Victims are groomed over months and shown a fake trading platform with fabricated gains. **The largest category by aggregate dollar value in recent years.**

**Fake support.** Nobody legitimate will ever ask for your seed phrase. **Ever.** Anyone who does is stealing from you, without exception.

**Exchange failure.** **FTX (Nov 2022) was not a crypto failure — it was customer funds being taken and used**, which is old-fashioned fraud that happened to involve crypto. Mt. Gox, Celsius and QuadrigaCX are variations. **"Not your keys, not your coins" is the accumulated lesson**, weighed against the fact that self-custody has its own irreversible failure modes.

## Reading a token before touching it

Mechanical checks, most of which take a minute:

1. **Is the source verified on Etherscan?** Unverified is a hard no
2. **Is there a `mint` function, and who can call it?**
3. **Is there a blacklist, a pause, a transfer fee, or a max-transaction limit?**
4. **Is it upgradeable? Who holds the key? Is there a timelock?**
5. **Is the liquidity locked, and for how long?** Unlocked liquidity can vanish in one transaction
6. **How is supply distributed?** A few wallets holding most of it is a countdown
7. **Does a linked audit exist, and does its commit hash match what's deployed?** → [[web3/04-smart-contract-security/07-the-audit-process|audits]]

Token sniffers (Token Sniffer, GoPlus) automate much of this. **They catch known patterns and miss novel ones** — useful as a filter, not as approval.

## The base rates

Worth internalising, because they're the actual expected value:

- **The overwhelming majority of new tokens go to zero.** Not a risk — the base rate
- **Most airdrop farming is unprofitable** after gas and time
- **Retail leveraged trading loses money in aggregate**, with more certainty here than in traditional markets, because of MEV, funding rates and 24/7 liquidations → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]]
- **Guaranteed yield is a marketing claim, not a financial instrument**

## For builders

You inherit a duty here, and most projects discharge it badly:

- **Publish and verify your source.** Unverified code is indistinguishable from a scam
- **Lock liquidity and say where.** Timelock privileged functions and publish the delay
- **Explain the risks plainly**, including what happens if you disappear
- **Never ask for a seed phrase, and say in your UI that you never will**
- **Make signature requests legible** — EIP-712, with a plain-language summary in your own interface before the wallet prompt
- **Don't promise yields you can't source.** If you can't explain where the return comes from, you're running a Ponzi whether you meant to or not

## Key insight

**The properties that make blockchains valuable are the same properties that make fraud efficient, and you cannot keep one without the other.** Irreversibility is why settlement is final and why theft is permanent. Permissionlessness is why anyone can build and why anyone can scam. **Security here is mostly operational discipline — what you sign, what you approve, where your keys live — not knowledge of vulnerability classes.**

## Related
- [[web3/06-building-dapps/02-wallets-and-connection|wallets]] — signature phishing
- [[web3/01-foundations/07-tokens-coins-and-nfts|tokens]] — why a token means nothing by itself
- [[web3/08-the-honest-assessment/03-regulation-and-the-legal-layer|regulation]] — the response
- [[cybersecurity/06-attacks-and-threats/01-social-engineering|social engineering]] — the same techniques, older
