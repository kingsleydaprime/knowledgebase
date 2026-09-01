# Bridges and Interoperability

**[Advanced]** — how assets move between chains, why bridges hold the worst security record in the field, and how to evaluate one.

## The kid version first

Your ETH exists on Ethereum. **It cannot leave.** There is no mechanism by which an Ethereum coin appears on another chain — the chains don't know each other exists.

So bridges fake it: **lock your ETH on Ethereum, and mint an IOU on the other chain.** The IOU is worth something only because someone is holding the real ETH and promises to give it back.

**That "someone" is the bridge, and it is holding everyone's money in one place.**

## The mechanisms

**Lock-and-mint.** Deposit on chain A into a bridge contract; a wrapped token is minted on chain B. Burn the wrapper to unlock the original. **The bridge contract accumulates every asset ever bridged** — one contract, enormous value, permanent target.

**Burn-and-mint.** For natively multichain tokens, burn on A, mint on B. No honeypot, because there's no locked pool — but it requires the token issuer to control both sides. Circle's CCTP for USDC works this way, and it's structurally safer.

**Liquidity networks.** Pools on both sides; you sell into A's pool and buy from B's. No wrapped assets, no honeypot, and capital efficiency plus slippage as the costs. Across and Hop work like this.

**Native / canonical bridges.** Rollups have one built in, secured by the L1 itself. **Slower (a 7-day window for optimistic rollups) and strictly the most secure option** → [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]].

## The hard problem

**A blockchain cannot observe another blockchain.** It has no network access and no way to verify a foreign chain's state. So every bridge needs someone to tell chain B what happened on chain A — **and the security of the bridge is exactly the security of that messenger.**

The options, in descending order of trust required:

| Verification | How | Trust |
|---|---|---|
| **Externally verified** | A multisig or committee attests | **Trust the committee.** Most bridges. Fastest, cheapest, worst |
| **Optimistically verified** | Assume valid, allow challenges | Trust ≥1 honest watcher |
| **Natively / light-client verified** | Chain B verifies chain A's consensus directly, in a contract | **Trust only the chains.** Correct, expensive, hard |
| **ZK light client** | Verify a proof of A's consensus | **The endgame.** Cheap verification, mathematically sound → [[web3/05-beyond-ethereum/03-zero-knowledge-proofs\|zk]] |

**The overwhelming majority of deployed bridges are externally verified**, because it's the only one that was easy to build. That is the whole story of the losses below.

## The losses

Bridges hold the worst record in the field, and it isn't close:

| Bridge | Date | Loss | Cause |
|---|---|---|---|
| **Ronin** | Mar 2022 | **~$625M** | 5 of 9 validator keys compromised — 4 held by one entity, plus stale delegated access |
| **Poly Network** | Aug 2021 | ~$611M | A function let the caller change the keeper. Funds were returned |
| **Wormhole** | Feb 2022 | ~$326M | Forged guardian signature via a verification flaw |
| **Nomad** | Aug 2022 | ~$190M | Upgrade set a trusted root to zero — every message valid. Crowd-drained |
| **Harmony Horizon** | Jun 2022 | ~$100M | 2-of-5 multisig, both keys compromised |

**Add these up and bridges account for the majority of all value stolen in the field's history.**

Three reasons this is structural rather than bad luck:

1. **Concentration.** All bridged value sits in one contract. Maximum reward for one exploit
2. **Complexity.** Two chains, two codebases, cryptographic message verification, relayers, upgrade paths. Enormous surface
3. **Weak verification.** A small multisig protecting hundreds of millions is an economically irrational amount of value behind a handful of keys → [[web3/04-smart-contract-security/03-access-control-and-key-management|key management]]

## Messaging protocols

The generalisation: pass **arbitrary messages**, not just assets — so a contract on one chain can call one on another. LayerZero, Wormhole, Axelar, Chainlink CCIP, Hyperlane.

**Same trust question, harder to see.** "Configurable security" and "decentralised verifier network" typically mean *a set of nodes attesting*, which is the externally-verified model with better branding. **Find out who signs and how many are needed** — that's the security model, regardless of what the documentation calls it.

## Evaluating a bridge

1. **Who verifies messages?** If the answer is a multisig or committee, that's your trust assumption. **Everything else is secondary**
2. **How many signers, held by how many *independent* parties?** Ronin was 5-of-9 on paper and effectively 1-of-1
3. **Who can upgrade it, and is there a timelock?**
4. **How much value is locked?** That's the bounty
5. **Is there a canonical alternative?** For rollups, **use the native bridge unless the 7-day wait is genuinely unacceptable**
6. **Is the wrapped asset the canonical one?** Multiple incompatible wrapped versions of the same token on one chain is common, and holding the wrong one means holding an illiquid IOU

## Practical advice

- **Use canonical/native bridges** where they exist. Slower and much safer
- **Don't leave assets bridged** longer than you need. Every day is exposure
- **Prefer CCTP for USDC** — burn-and-mint, no honeypot
- **Bridge small first.** Always
- **Treat any wrapped asset as a claim on a bridge**, not as the underlying asset. If the bridge dies, the wrapper goes to zero **while the original is still locked and unreachable**

## Key insight

**A bridge is a claim that something happened on a chain you cannot see, and the security of every bridged asset is the security of whoever makes that claim.** Most bridges answer this with a multisig, which is why they have lost more money than every other category combined. The real fix — light clients verifying consensus directly, made affordable by zk proofs — is finally being built, roughly a decade after the problem appeared.

## Related
- [[web3/04-smart-contract-security/08-case-studies|case studies]] — Ronin, Wormhole, Nomad in full
- [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zero-knowledge proofs]] — the endgame for verification
- [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]] — native bridges
- [[web3/04-smart-contract-security/03-access-control-and-key-management|key management]]

*Source: [reference] — Aug 2026.*
