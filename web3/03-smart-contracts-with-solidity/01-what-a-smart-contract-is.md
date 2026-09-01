# What a Smart Contract Is

**[Beginner]** — the definition, the four properties that make writing one unlike any other programming, and why the name is misleading.

## The kid version first

A smart contract is a program you **upload to the chain**, where it sits at an address. Anyone can call it. Every node runs it and they all agree on what happened.

The difference from normal code isn't the language. It's that **you can't fix it, you can't hide it, anyone can call any part of it, and it's holding money.** Those four things together change what "writing software" means.

## The name is wrong, and that matters

Szabo's 1994 term is unhelpful twice over:

- **Not smart.** It's a deterministic program with no intelligence, no discretion, and no ability to interpret intent
- **Not a contract.** It's not a legal agreement. It doesn't bind anyone, isn't enforceable in court by virtue of being on-chain, and a court will happily rule against what the code did

**"Code is law" was a slogan, and Ethereum abandoned it in practice within two years** — the 2016 DAO hack was resolved by hard-forking the chain to reverse the theft, precisely because the community would not accept the code's outcome as final. That fork is why Ethereum Classic exists. **The most-cited principle in the field was tested once and lost** → [[web3/04-smart-contract-security/08-case-studies|case studies]].

A better name is **"an autonomous agent with a bank account"**, or simply: a public API with money in it.

## The four properties that change everything

**1. Immutable.** Deployed code cannot be changed. No patch, no rollback, no hotfix. If it ships with a bug, the bug is permanent and public. Upgrade patterns exist, but they add a *different* trust assumption — someone can change the code — and that's a trade, not a solution → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]].

**2. Public.** Bytecode is readable by anyone, most contracts publish verified source, and **storage is readable regardless of the `private` keyword.** `private` is a *compiler* visibility modifier, not encryption — the value sits in a storage slot anyone can read with one RPC call. Putting a secret in a `private` variable is one of the most common beginner mistakes, and it is fully exploitable.

**3. Permissionless and adversarial.** Every public function is callable by anyone, in any order, at any time, with any arguments, arbitrarily many times, possibly from another contract, possibly re-entering mid-execution. **There is no "users won't do that."** Someone will, automatically, within minutes, if there's money in it.

**4. Financially incentivised.** The value held is the bug bounty for finding your mistake. Ordinary bugs cost embarrassment; these cost the entire balance, irreversibly, to an anonymous party. **This is the property that makes smart contract engineering a distinct discipline** rather than just "programming with extra steps."

## What contracts genuinely can't do

Worth learning early, because a great deal of wasted effort comes from assuming otherwise:

| Can't | Because | Workaround |
|---|---|---|
| Run on a schedule | Nothing executes without a paid transaction | Keeper networks (Chainlink Automation, Gelato) |
| Read the internet | Determinism — nodes would get different answers | [[web3/06-building-dapps/06-oracles\|Oracles]] |
| Generate randomness | Same reason. `block.timestamp` and `blockhash` are **proposer-influenced** | Chainlink VRF, or commit-reveal |
| Keep a secret | Storage is public | Commit-reveal, or off-chain computation with proofs |
| Know the "real" time | `block.timestamp` is proposer-set, tolerable drift ~12s | Don't rely on precision below a minute |
| Loop over unbounded data | Block gas limit | Pagination, or a pull-based pattern |
| Call itself later | No async, no callbacks | Someone must send a transaction |

**`block.timestamp` deserves a specific warning.** It is set by the block proposer, who has meaningful latitude. Using it as a randomness source is a known-exploitable pattern; using it for coarse deadlines ("after next Tuesday") is fine.

## The lifecycle

```
write  →  compile to EVM bytecode  →  deploy (a tx with no `to`)
                                          │
                                    address assigned = keccak(sender, nonce)
                                          │
       ← anyone calls it, forever ────────┘
                                          │
                        (it only ever runs when called, and paid for)
```

Deployment is one-way. The address is derived from your account and nonce, so it's predictable — or, with `CREATE2`, chosen via a salt.

## How this changes how you write code

The practices that are *nice to have* elsewhere are **mandatory here**:

- **Checks-Effects-Interactions** as a reflex, not a preference → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]]
- **Test the adversary, not the happy path.** Fuzzing and invariant testing are the default, not advanced techniques → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing]]
- **Minimise.** Every line is attack surface you cannot remove later. The best security property a contract can have is *not being there*
- **Assume every external call is hostile**, including calls to contracts you wrote
- **Get it audited before it holds real value**, and understand that an audit reduces risk rather than eliminating it → [[web3/04-smart-contract-security/07-the-audit-process|audits]]

## Key insight

**A smart contract is a public API, with no auth by default, that cannot be patched, holds money, and is called by adversaries who profit from your mistakes.** Every unusual practice in this folder is a response to that sentence. If you internalise nothing else, internalise that the environment — not the language — is what makes this hard.

## Related
- [[web3/03-smart-contracts-with-solidity/02-solidity-fundamentals|Solidity fundamentals]] — the language
- [[web3/04-smart-contract-security/01-why-this-is-different|why security is different here]] — the fuller argument
- [[web3/02-ethereum-and-the-evm/01-the-world-computer|the world computer]] — the machine underneath
- [[concepts/04-best-practices/README|best practices]] — the general versions of these habits

*Source: [reference] — Aug 2026.*
