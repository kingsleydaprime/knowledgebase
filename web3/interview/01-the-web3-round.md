# The Web3 Round

**[Intermediate → Advanced]** — the questions that come up, what a strong answer covers, and the detail that separates memorised from understood. 🔥 marks the ones asked constantly.

## Fundamentals

**🔥 Q: What problem does a blockchain actually solve?**

**A strong answer covers:** not double-spending — *ordering*. Detecting a conflicting spend is trivial; agreeing globally on which came first, with no trusted clock and no authority, is the hard part. Add open membership and you get the Sybil problem: votes can't be counted per identity because identities are free. So influence is tied to something costly — work or stake.

**The detail worth adding:** every cryptographic primitive Bitcoin used existed by 1998. **The contribution was economic, not cryptographic** — making the right to write costly enough that lying costs more than it earns → [[web3/01-foundations/02-the-double-spend-problem|the double-spend problem]].

**🔥 Q: When would you *not* use a blockchain?**

**A strong answer covers:** almost always. If any party could be trusted to run the database, use a database — it's faster, cheaper, private and fixable. Blockchains buy exactly one property: no administrator.

**The detail worth adding:** the sharpest follow-up is about **data origin**. A chain guarantees a record wasn't altered, not that it was ever true. Supply chain provenance fails on this — someone scans a QR onto a pallet and the lie becomes permanent → [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|what blockchains are good for]].

**Q: UTXO vs account model?**

**A strong answer covers:** UTXO has no stored balances — value is discrete unspent outputs, consumed whole, with change. Accounts are a mutable map. UTXO parallelises (disjoint outputs don't conflict) and gets replay protection free. Accounts are natural for stateful contracts, and need a nonce precisely *because* they lost that property.

**The detail worth adding:** Ethereum's sequential execution is a direct consequence, and Solana's declared-account model is an attempt to recover UTXO's parallelism inside an account model → [[web3/01-foundations/04-blocks-chains-and-state|state models]].

**Q: What did the Merge change?**

**A strong answer covers:** consensus only — PoW to PoS. ~99.95% less energy, much lower issuance. **No throughput change.** Anyone who expected it to make Ethereum fast or cheap misunderstood what it was.

## The EVM

**🔥 Q: Walk me through storage, memory and calldata.**

**A strong answer covers:** storage is persistent, ~20,000 gas to create a slot, 2,100 to read cold. Memory is per-call, ~3 gas, quadratic when it expands. Calldata is read-only transaction input, cheapest to read.

**The detail worth adding — this is the real question:** assigning a storage struct to a `memory` local makes a **copy**, so mutating it writes nothing on-chain. It compiles, it runs, it silently does nothing. `storage` locals are references; `memory` from storage is a copy → [[web3/03-smart-contracts-with-solidity/03-storage-memory-calldata|storage/memory/calldata]].

**Q: Why does gas exist?**

**A strong answer covers:** the halting problem. You can't decide whether a program terminates, and on a network where every node executes everything, an infinite loop is a DoS. Gas converts an undecidable question into an economic one — bound the budget instead of proving termination. It also prices resources: storage burdens every node forever, so it costs far more than arithmetic.

**The detail worth adding:** **a revert refunds state but not gas.** That asymmetry is what makes spam expensive → [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas and fees]].

**Q: What does `DELEGATECALL` do, and why is it dangerous?**

**A strong answer covers:** runs another contract's code in *your* storage context, with your `msg.sender` and `msg.value`. It's how libraries and every proxy work. Dangerous because the callee can write any of your storage slots — so delegating to untrusted code is total compromise.

## Solidity and security

**🔥 Q: Explain reentrancy and how you'd prevent it.**

**A strong answer covers:** an external call transfers control; if state wasn't updated first, the callee re-enters and sees stale state. Fix with Checks-Effects-Interactions — update state before calling out — plus a `nonReentrant` guard as backup.

**The detail worth adding, and this is what separates candidates:** the **three variants**. Cross-function (the guard is on `withdraw` but not on `transfer`, which reads the same state). Cross-contract (each contract's guard holds; the system invariant doesn't). **Read-only** (re-entering a `view` function during your inconsistent window, so a *different* protocol reads a wrong price). And: `.transfer()`'s 2300-gas stipend is **not** the answer — it breaks smart-contract wallets and gas costs get repriced → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]].

**🔥 Q: Where has most of the money actually been lost?**

**A strong answer covers:** **not reentrancy.** Access control and operational failures dominate — Ronin ($625M) was compromised keys and stale permissions; Parity ($280M) was an uninitialised library. Then oracle manipulation, then bridges. Bridges alone account for the majority of the largest losses.

**The detail worth adding:** this reframes what security work is. The field's attention goes to clever vulnerability classes; **the losses come from operations, key management, and trusting a manipulable number** → [[web3/04-smart-contract-security/08-case-studies|case studies]].

**🔥 Q: How would a flash loan break my protocol?**

**A strong answer covers:** capital is rentable for the duration of one transaction with no collateral. So **any check based on a balance, share of supply, vote weight, or spot price is defeated for a fee.** "Only large holders can do this" is not a security control.

**The detail worth adding:** the classic form is manipulating an AMM's reserve ratio — which *is* its price — then calling a protocol that reads it as truth. Defences: real oracles with staleness checks, TWAPs (with the caveat that thin pools are cheap to hold), sanity bounds, or **designing so you never need an external price at all**, which is what Uniswap's core does → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|price manipulation]].

**Q: `tx.origin` vs `msg.sender`?**

**A strong answer covers:** `msg.sender` is the immediate caller; `tx.origin` is the EOA that started the chain. **Never use `tx.origin` for auth** — any contract the owner is tricked into calling can then call yours and pass the check.

**Q: Why is `private` not private?**

**A strong answer covers:** it's a compiler visibility modifier. Storage is readable by anyone via `eth_getStorageAt`, and bytecode is public. There is no confidentiality on a public chain.

**Q: What breaks when you upgrade a proxy?**

**A strong answer covers:** storage layout. The implementation's declaration order decides which of the *proxy's* slots it reads — so reordering, retyping or removing a variable makes new code read old data as something else. Rules: append only, reserve `__gap`, use ERC-1967 slots for proxy metadata, and **diff the layout in CI**.

**The detail worth adding:** `_disableInitializers()` in the implementation's constructor. Skipping it is the Parity freeze — anyone initialises the implementation, becomes its owner, and bricks every proxy → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]].

**Q: How do you test a contract?**

**A strong answer covers:** Foundry. Unit tests, then **fuzz tests by default** (one line, and it tries zero, one wei, and max), then **invariant tests** — state a property that must hold under any call sequence and let the fuzzer attack it. Fork tests against real mainnet integrations. Slither in CI.

**The detail worth adding:** invariants are what catch multi-step exploits, where each individual call is fine and the combination isn't. **That's the class unit tests structurally cannot find** → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing]].

## Building

**🔥 Q: How do you show a user their transaction history?**

**A strong answer covers:** you can't ask the chain. There's no query language — it answers point lookups and log queries over bounded ranges. **You need an indexer**: replay logs into Postgres, serve from there. The Graph, Ponder, or a prebuilt provider API.

**The detail worth adding:** **reorgs.** An indexed block can be un-happened, so you either wait for finality or track block hashes and unwind on mismatch. Ignoring `log.removed` is the standard bug in hand-rolled indexers → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

**Q: What states does a transaction have?**

**A strong answer covers:** idle, awaiting signature, rejected, pending, mined-success, **mined-and-reverted**, dropped, replaced — and success is still reorg-able briefly.

**The detail worth adding:** **mined-and-reverted is the one people miss.** It succeeded at the network level, failed at the application level, and the user paid. A UI showing "success" on receipt without checking `status` is wrong.

**Q: Is your dapp decentralised?**

**A strong answer covers:** honestly, mostly not. The contract is; the RPC provider, indexer, frontend host, domain and storage gateway usually aren't. Infura has censored addresses and its outages take down large parts of the ecosystem.

**The detail worth adding:** the question that matters is **"if your company disappears, can users still get their assets out?"** Verified source on Etherscan is a real escape hatch and costs nothing to provide → [[web3/06-building-dapps/01-the-dapp-architecture|dapp architecture]].

**Q: How do you get randomness on-chain?**

**A strong answer covers:** you don't, natively. Everything available is proposer-influenced or predictable. `block.timestamp` is proposer-set; `prevrandao` is biasable by slot-skipping. Use Chainlink VRF, or commit-reveal.

**The detail worth adding:** **an attacker can revert.** Call your lottery from a contract that checks the result and reverts if it lost — retrying for gas. **Any randomness resolved in the same transaction as the entry is defeated regardless of source** → [[web3/06-building-dapps/06-oracles|oracles]].

## The judgement questions

**Q: Optimistic vs zk rollups?**

**A strong answer covers:** optimistic assumes validity with a 7-day fraud-proof window (hence 7-day withdrawals); zk proves validity, so finality is immediate. zk costs more to prove, less to trust.

**The detail worth adding:** both usually run **one sequencer** that can censor and reorder but not steal. Check for forced inclusion via L1, and check who holds the upgrade keys — L2Beat's staging classification tracks exactly this → [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]].

**Q: Why do bridges get hacked so much?**

**A strong answer covers:** a chain can't observe another chain, so someone must attest. Most bridges use a small multisig — **hundreds of millions secured by a handful of keys.** Add concentration (all value in one contract) and complexity (two chains, two codebases).

**The detail worth adding:** Ronin was 5-of-9 on paper, with 4 keys at one entity and a 5th reachable through unrevoked delegated access. **Count independent signers, not keys.** The real fix is light-client verification, made affordable by zk proofs → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]].

**Q: What's your view on the industry?**

**A strong answer covers:** an honest one. The engineering is genuinely interesting; the use cases that survive scrutiny are narrower than the marketing; most value created has been financial; and there's real, under-reported non-speculative use of stablecoins where currencies have failed.

**The detail worth adding:** **interviewers are testing calibration, not enthusiasm.** Uncritical boosterism and blanket dismissal both read as not having thought about it. Naming what doesn't work is what demonstrates you understand what does.

## What this round is really testing

**Three things:**

1. **Do you think adversarially by default?** Every question above has a "what if the caller is hostile" version, and reaching for it unprompted is the strongest signal
2. **Do you understand the machine, not just the syntax?** Storage costs, gas, `DELEGATECALL`, determinism — the Solidity questions are EVM questions
3. **Are you calibrated?** Knowing where the money actually went, and what blockchains are bad at, distinguishes people who've engaged with the field from people who've read its marketing

## Related
- [[web3/README|the web3 course]]
- [[web3/04-smart-contract-security/README|smart contract security]] — most of the hard questions live here
- [[INTERVIEW|Interview Prep Index]]
