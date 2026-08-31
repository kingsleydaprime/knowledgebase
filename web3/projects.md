# Web3 — Projects

*The vault's newest track and its most `[reference]`-heavy: **nothing in `web3/` has been deployed, audited or exploited by its author.** These projects exist to change that, and the first three cost nothing but time — testnets are free.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

**One rule before anything else:** deploy to testnets only, and never put real value behind unaudited code you wrote. [[web3/04-smart-contract-security/08-case-studies|The case studies]] are what happens when people skip that.

## The ladder

- 🟢 ⭐ **Token and wallet from scratch** — the guide: [[build-your-own-shit/16-your-own-token-and-wallet|16-your-own-token-and-wallet]]. **Done when:** your ERC-20 shows in MetaMask, and your hand-rolled HD wallet derives the *same addresses* MetaMask does from the same seed. **The best first rep here** — one evening, and it makes [[web3/01-foundations/07-tokens-coins-and-nfts|"a token is a row in a mapping"]] concrete.

- 🟢 **Read a real contract** — pick a deployed protocol on Etherscan, read the verified source, and write a page on what its privileged roles can do, whether it's upgradeable, and where the timelock is. **Done when:** you can state exactly who could rug it and how fast. Exercises: [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]].

- 🟢 **Break your own contract** — write a vulnerable contract (reentrancy, bad access control, spot-price oracle), then write the Foundry exploit that drains it. **Done when:** the exploit test passes, then you fix it and it fails. Exercises: [[web3/04-smart-contract-security/README|security]].

- 🟡 **Invariant-test something real** — take your token or vault and write invariants (supply equals sum of balances; solvency holds; no one withdraws more than they deposited), then let Foundry's fuzzer attack them for an hour. **Done when:** it finds something you didn't expect. Exercises: [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing]].

- 🟡 **A full dapp, indexed** — contract + Next.js frontend + a Ponder indexer, deployed on an L2 testnet. **Done when:** your UI shows a *history* view — which is the moment you learn [[web3/06-building-dapps/04-indexing-and-events|you cannot query a blockchain]].

- 🟡 **Build your own blockchain** — the guide: [[build-your-own-shit/14-your-own-blockchain|14-your-own-blockchain]]. **Done when:** you partition two of your nodes, mine on both, reconnect, and watch one discard its chain.

- 🔴 ⭐ **Build your own smart contract VM** — the guide: [[build-your-own-shit/15-your-own-smart-contract-vm|15-your-own-smart-contract-vm]]. **Done when:** `DELEGATECALL` works and you've upgraded a proxy you wrote. **The deepest of the three.**

- 🔴 **Audit something, properly** — take a Code4rena or Sherlock contest whose report is public, audit the code *first* without reading the findings, then compare. **Done when:** you've compared your list to the real one honestly. **This is the single best calibration exercise in security work** — and it's free.

- 🔴 **Submit to a live contest or bounty** — Code4rena, Sherlock, or Immunefi. **Done when:** you've submitted a finding, valid or not. The rejection teaches as much.

## If you only do one

**The token and wallet guide**, then immediately **break your own contract**. Together that's two evenings, and it takes you from "read about reentrancy" to "wrote the exploit and watched it drain."

## Related
- [[web3/README|the web3 course]] · [[web3/interview/README|interview bank]]
- [[web3/04-smart-contract-security/README|smart contract security]] — read before deploying anything
- [[project-ideas|Project Ideas]] — the vault-wide index
