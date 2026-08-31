# Smart Contracts with Solidity

**Writing programs for the machine in [[web3/02-ethereum-and-the-evm/README|section 02]].** Solidity is a small language pointed at a very strange computer — most of what surprises you is the EVM showing through.

**Read [[web3/04-smart-contract-security/README|section 04]] alongside this one, not after it.** The security material isn't an advanced topic here; it's part of learning the language.

## Reading order
1. [[web3/03-smart-contracts-with-solidity/01-what-a-smart-contract-is|what-a-smart-contract-is]] — **[Beginner]** — immutable, public, permissionless, holding money; what contracts genuinely can't do; and why "code is law" was tested once and lost
2. [[web3/03-smart-contracts-with-solidity/02-solidity-fundamentals|solidity-fundamentals]] — **[Intermediate]** — the language, assuming you can already program. Types, globals, errors, visibility, and the 0.8 arithmetic change that made SafeMath obsolete
3. [[web3/03-smart-contracts-with-solidity/03-storage-memory-calldata|storage-memory-calldata]] — **[Intermediate]** — **the reference-vs-copy rule that silently does nothing**, caching storage in loops, memory's quadratic cost, and transient storage
4. [[web3/03-smart-contracts-with-solidity/04-functions-modifiers-visibility|functions-modifiers-visibility]] — **[Intermediate]** — four-byte selectors, what modifiers compile to, `receive`/`fallback`, and why `.transfer()` is deprecated advice
5. [[web3/03-smart-contracts-with-solidity/05-events-and-logs|events-and-logs]] — **[Intermediate]** — the write-only side channel; indexed vs not; the bloom filter and why `eth_getLogs` is slow; reorg safety
6. [[web3/03-smart-contracts-with-solidity/06-inheritance-and-libraries|inheritance-and-libraries]] — **[Intermediate]** — C3 linearisation, what `library` really compiles to, and why inheritance depth is a security property here
7. [[web3/03-smart-contracts-with-solidity/07-token-standards|token-standards]] — **[Intermediate]** — ERC-20/721/1155/4626, **the four ways real tokens break the spec**, and why `SafeERC20` exists
8. [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|upgradeability-and-proxies]] — **[Advanced]** — `DELEGATECALL`, the three rules you can't break, and the honest argument that **upgradeability converts code-risk into key-risk**
9. [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas-optimisation]] — **[Intermediate]** — the wins worth taking, in order, and the ones that trade safety for pennies
10. [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing-and-tooling]] — **[Intermediate]** — Foundry, and **why fuzzing and invariant testing are the baseline here rather than advanced practice**

## Related
- [[web3/README|web3 curriculum map]]
- [[web3/04-smart-contract-security/README|04-smart-contract-security]] — read in parallel
- [[web3/frameworks/solidity/README|the Solidity toolchain]] — Foundry, Hardhat, OpenZeppelin
- [[web3/frameworks/rust/README|Rust for web3]] — the other major contract language
