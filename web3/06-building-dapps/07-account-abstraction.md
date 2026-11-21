---
id: 661ee8ba-932a-4aae-9c42-9702f242c674
---

# Account Abstraction

## The problem it solves
<!-- bite: f4908699-df9a-4548-a041-3f9b8b753897 -->

Ethereum's EOA has been unchanged since 2015, and it is a straitjacket:

- **One signature scheme** (ECDSA on secp256k1). No passkeys, no biometrics, no multisig natively
- **You must hold ETH to do anything** — including receiving your first token
- **One operation per transaction.** Approve then swap is two signatures, two waits
- **No recovery.** Lose the key, lose everything
- **No limits, no sessions, no policies.** Every signature is unlimited authority

**Every one of these is a self-inflicted wound from a design choice made once**, and account abstraction is the effort to undo them without reintroducing a custodian.

## The core idea
<!-- bite: 0f2a6a8e-3281-4d7a-90e4-3ac34808d9d1 -->

**Make the account a smart contract, so its validation logic is programmable.**

```
EOA:                       Smart account:
  fixed ECDSA check          YOUR code decides what a valid operation is
  ↓                          ↓
  "is this signature         "is this a passkey signature? is it under the daily
   from this key?"            limit? is it a whitelisted contract? did 2 of 3
                              guardians approve?"
```

Once validation is code, everything else follows: **social recovery, spending limits, session keys, batching, gas sponsorship, any signature scheme.**

## ERC-4337 — without changing the protocol
<!-- bite: 7932798e-60fa-4c5b-aeb1-ed42a56fa631 -->

Shipped March 2023, entirely in contracts and off-chain infrastructure — **no hard fork**, which is why it happened at all.

```
UserOperation           a pseudo-transaction: sender, calldata, signature, gas fields
      │
   alt mempool          a separate mempool, not Ethereum's
      │
   Bundler              collects UserOps, bundles them into ONE real transaction
      │
   EntryPoint           the singleton contract: validates each, then executes each
      │
   your Smart Account   validateUserOp() — YOUR rules
      │
   Paymaster (optional) sponsors gas — the user needs no ETH at all
```

**The paymaster is the most immediately valuable piece.** An app can pay its users' gas, or accept USDC as payment for it. **"You need ETH before you can do anything" — the single worst onboarding barrier — is simply removed.**

**Session keys** are the second: authorise a temporary key with narrow permissions ("may call this game contract, up to this amount, for the next hour"). **No wallet popup per action**, which is what makes on-chain games playable.

**The costs:** a UserOp is more expensive than a plain transaction (the EntryPoint runs validation logic on-chain); bundler infrastructure is a new, partly centralised dependency; and it was a parallel system that ordinary EOAs couldn't use.

## EIP-7702 — the one that changed adoption
<!-- bite: 76a933ba-eb80-4ee0-a4bb-2ab9a9be2d8d -->

Shipped in **Pectra (2025)**, and it's the more consequential of the two for most users.

**It lets an existing EOA temporarily set contract code**, via a new transaction type. Your normal MetaMask address gains smart-account behaviour **for a transaction, without migrating to a new address.**

That last part is why it matters: ERC-4337 required moving to a *new* smart-account address, abandoning your history, your ENS, your NFTs, your positions. **Nobody wanted to.** 7702 removes the migration entirely — your existing address gets batching, sponsorship and session keys.

**The two now compose:** 7702 for existing EOAs, 4337's infrastructure (bundlers, paymasters) underneath, with smart accounts still available for anyone wanting full programmability from the start.

## What it enables, concretely
<!-- bite: 4f7109bc-233f-4b75-8e99-548382513d52 -->

- **Sponsored gas** — onboard a user who has never held crypto
- **Pay fees in USDC** — no native token required
- **Batching** — approve and swap in one signature, one confirmation
- **Social recovery** — guardians (friends, devices, an institution) can rotate your key. **The seed phrase stops being a single point of catastrophic failure**
- **Spending limits and allowlists** — a compromised session key costs you a bounded amount
- **Passkeys** — sign with Face ID or a security key instead of a seed phrase
- **Session keys** — playable games, tradeable interfaces, no popup per action

## The honest status
<!-- bite: 50ebcb77-87d9-4b14-b956-fdee255a2e79 -->

**What genuinely works today:** gas sponsorship and batching are in production and materially improve onboarding. Safe has secured very large sums with smart-account logic for years. Passkey-based wallets exist and work.

**What's still rough:**

- **Wallet and dapp support is uneven.** Support for 7702 and 4337 varies by wallet, chain and library
- **Bundlers and paymasters are centralised infrastructure** — another vendor in your "decentralised" stack → [[web3/06-building-dapps/01-the-dapp-architecture|dapp architecture]]
- **Smart accounts are contracts, so they have contract bugs.** A wallet with a vulnerability is a wallet that can be drained, and now your *account* has an attack surface. **Use audited implementations** (Safe, Kernel, Alchemy's Light Account) — this is not the place to write your own
- **7702 introduced its own risks.** An EOA that can delegate to arbitrary code is a new phishing surface: sign the wrong delegation and your account executes hostile code. Wallets are still working out how to present this safely
- **Cross-chain address consistency** requires care with `CREATE2` and deployment ordering

## For building
<!-- bite: 5fc2af2d-8ad4-4f12-8306-01aa12d0f5b3 -->

- **Use a provider** — Alchemy Account Kit, Pimlico, Biconomy, ZeroDev, Privy. Running bundler and paymaster infrastructure yourself is a real operational burden with little upside
- **Sponsored gas is the highest-value feature to adopt first.** It removes the biggest onboarding barrier for a modest cost, and it's the easiest to add
- **Don't force it.** Support both EOAs and smart accounts; most users still arrive with MetaMask
- **Never write your own account contract**

## Key insight
<!-- bite: 86144f9d-37e4-488b-aee1-44ff65fb923f -->

**Account abstraction turns "who may spend this" from a fixed protocol rule into application code** — which is what finally allows recovery, limits, sessions and sponsorship without a custodian holding your keys. ERC-4337 proved it could work without a fork; **EIP-7702 made it available to the accounts people already have, which is what actually moves adoption.** The remaining barrier is that the infrastructure making it convenient is itself centralised.

## Related
<!-- bite: a148213d-9e32-4486-a41e-c083ceed3c82 -->
- [[web3/06-building-dapps/02-wallets-and-connection|wallets and connection]] — the UX problems this addresses
- [[web3/02-ethereum-and-the-evm/04-transactions-and-the-mempool|transaction types]] — where 7702 fits
- [[web3/04-smart-contract-security/03-access-control-and-key-management|key management]]
- [[web3/01-foundations/03-cryptographic-primitives|key derivation]] — what a seed phrase is

## About this lesson
<!-- bite: 00e6517d-9c5b-4c75-817b-b729e7dfae82 -->

**Level:** Advanced. **Covers:** the attempt to fix wallet UX without giving up self-custody, and where it actually stands.
