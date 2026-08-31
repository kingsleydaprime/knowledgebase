# Why Security Is Different Here

**[Intermediate]** — the specific ways smart contract security departs from [[cybersecurity/README|ordinary application security]], and why the usual defence-in-depth playbook doesn't transfer.

## The five differences

**1. No patching.** Web security assumes a patch cycle: find, fix, deploy, done. Here the vulnerable code stays vulnerable forever unless you built an upgrade path — which is [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|its own risk]]. **Detection without remediation is nearly worthless**, which inverts the usual value of monitoring.

**2. The attacker is funded, automated and instant.** Bots watch every deployment and every mempool transaction. A vulnerability in a contract holding $10M has a $10M bounty attached, payable immediately, to an anonymous party. **Exploitation happens in seconds, not in the weeks a normal disclosure cycle assumes.**

**3. No perimeter.** No firewall, no WAF, no rate limit, no IP block, no auth by default. Every function is a public endpoint reachable by anyone, from anywhere, arbitrarily often. The entire concept of network-layer defence is absent → [[cybersecurity/03-network-security/README|network security]] simply doesn't apply.

**4. The system is composable, and that's an attack surface.** Anyone can build on your contract without asking. Your contract will be called inside flash loans, wrapped by aggregators, and used as collateral by protocols you've never heard of. **You cannot enumerate your integrations**, so you cannot reason about the full system your code participates in. Composability is the ecosystem's best property and its worst security property, and those are the same property.

**5. Loss is final.** No chargeback, no insurance by default, no reversal. The DAO fork is the exception that proves the rule — and it required a contentious hard fork of the entire network, splitting the community permanently.

## What this does to the threat model

| Ordinary appsec | Smart contracts |
|---|---|
| Defence in depth, many layers | **One layer.** The contract is the whole perimeter |
| Patch on disclosure | **No patch.** Prevention is all you get |
| Rate limiting and monitoring | **No rate limits.** Monitoring rarely enables a response in time |
| Trusted internal services | **Nothing is trusted.** Every external call is hostile |
| Secrets in config | **No secrets.** All state and code is public |
| Auth via sessions/tokens | **Auth via `msg.sender` only** |
| Bugs cost reputation | **Bugs cost the balance, instantly** |

**The single most useful reframe:** in web security you defend a system with an inside and an outside. Here **there is no inside.** Every line of your contract is public API, and your only defence is that the code is correct.

## The categories of failure

Roughly where the money has actually gone, across the field's history:

1. **Access control** — a function that should have been restricted wasn't; or the admin key was stolen. **The largest category by value lost, by a wide margin**, and the least technically interesting → [[web3/04-smart-contract-security/03-access-control-and-key-management|access control]]
2. **Price/oracle manipulation** — the contract trusted a number it shouldn't have, usually a spot price, usually inside a flash loan → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|oracles]]
3. **Reentrancy** — the famous one, now well-understood and still recurring in new forms → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]]
4. **Arithmetic and rounding** — precision loss and rounding in the wrong direction → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|arithmetic]]
5. **Logic errors** — the contract does exactly what it says, and what it says is wrong. **No tool finds these.** This is what auditors are actually for
6. **Bridges** — cross-chain message verification. **The single largest losses in the field** → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]]

**Note what's near the top: access control and stolen keys.** The field's most-discussed vulnerability class (reentrancy) is not where most of the money went. **Most losses are operational or mundane**, which is unglamorous and worth internalising early.

## The mindset that works

**Assume every external call gives control to an adversary.** Because it does — the callee decides what to do with it, including calling back into you.

**Assume every input is malicious**, every caller is a contract, and every ordering is possible. There is no "no one would do that."

**Ask "what does this look like inside a flash loan?"** — an attacker can borrow a hundred million dollars for the duration of one transaction, with no collateral, provided they repay it before the transaction ends. **Any check based on a balance, a share of supply, or a spot price is defeated by that** → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|flash loans]].

**Minimise.** Every line is permanent attack surface. The most reliable security property is code that isn't there.

**Reason about invariants, not about flows.** "What must always be true?" is answerable and testable; "did I handle every path?" is not → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|invariant testing]].

## What actually reduces risk, ranked

1. **Do less.** Fewer features, fewer integrations, less code
2. **Use audited, battle-tested libraries** rather than writing your own primitives
3. **Invariant and fuzz testing** — the techniques that find multi-step exploits
4. **Multiple independent audits**, and understand they reduce risk rather than removing it
5. **A timelock on every privileged action**, so a compromise is visible before it executes
6. **A bug bounty** (Immunefi) — genuinely effective, because it gives a finder a legal payout that competes with exploiting
7. **Staged rollout with deposit caps** — limit the loss while the code is young
8. **Monitoring with a pause switch** — the one form of response that sometimes works in time

**Note that 1 and 2 outrank everything technical.** That ordering is the field's accumulated experience and it's routinely ignored.

## Key insight

**Smart contract security is closer to aerospace than to web security: you cannot patch after launch, so all the effort moves to before it.** The defence-in-depth reflexes from [[cybersecurity/README|application security]] mostly don't transfer, because they assume a perimeter, a patch cycle, and reversible losses — and this environment has none of the three.

## Related
- [[cybersecurity/README|cybersecurity]] — the general discipline this departs from
- [[web3/04-smart-contract-security/08-case-studies|case studies]] — where the money actually went
- [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing and tooling]]
- [[web3/04-smart-contract-security/07-the-audit-process|the audit process]]

*Source: [reference] — Aug 2026.*
