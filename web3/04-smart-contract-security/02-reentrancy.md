---
id: 6ee0c3bf-810d-465e-996e-9e221b1f9fd4
---

# Reentrancy

**[Intermediate]** — the canonical smart contract vulnerability, the three variants people miss, and the two defences that work.

## The kid version first
<!-- bite: b3700317-f476-47b9-a243-275145c0b6ee -->

You ask the bank teller for £100. The teller **hands you the money first**, then reaches for the ledger to write down that your balance dropped.

Before they write it down, you ask again. The ledger still says you have money. They hand you another £100.

**The bug isn't the withdrawal. It's doing things in the wrong order** — and in the EVM, "handing over the money" gives the recipient a chance to speak before you've finished.

## The vulnerable pattern
<!-- bite: ec593fe5-2429-4fe4-9874-f9dd9c2c08bf -->

```solidity
mapping(address => uint256) public balances;

function withdraw() external {
    uint256 amount = balances[msg.sender];

    (bool ok, ) = msg.sender.call{value: amount}("");   // ← INTERACTION
    require(ok);

    balances[msg.sender] = 0;                           // ← EFFECT, too late
}
```

`msg.sender.call` transfers control to the recipient's code. If that's a contract, its `receive()` runs — **and can call `withdraw()` again, while `balances[msg.sender]` is still the original amount.**

```solidity
contract Attacker {
    Vault vault;
    receive() external payable {
        if (address(vault).balance >= 1 ether) vault.withdraw();   // recurse
    }
    function attack() external payable {
        vault.deposit{value: 1 ether}();
        vault.withdraw();          // drains until the vault is empty or gas runs out
    }
}
```

**This is The DAO, June 2016 — ~3.6M ETH.** It caused the hard fork that created Ethereum Classic, and it remains the field's founding trauma → [[web3/04-smart-contract-security/08-case-studies|case studies]].

## Why the EVM makes this easy to hit
<!-- bite: 829fe68b-0a59-4b26-900d-7c337e3b3cea -->

**Every value transfer is a function call.** There is no way to send ETH without potentially executing the recipient's code. `send`, `transfer` and `call` all invoke `receive`/`fallback`.

And it isn't only ETH. **Any external call hands over control**, including calls that look innocuous:

- `onERC721Received` / `onERC1155Received` — the "safe" transfer callbacks
- ERC-777's `tokensReceived` hook — **a plain token transfer becomes a reentrancy vector**, which is what broke Uniswap V1's imBTC pool in April 2020
- Any call to a token contract you don't control, since it might not be the token you think

## The three variants people miss
<!-- bite: d54fb60b-4eb6-49e3-b476-06345824691d -->

**1. Cross-function reentrancy.** `withdraw()` is guarded — but the attacker re-enters through `transfer()`, which reads the same stale balance:

```solidity
function withdraw() external nonReentrant { ... }   // guarded
function transfer(address to, uint256 amt) external {   // NOT guarded — same state
    balances[msg.sender] -= amt;                        // reads stale balance
    balances[to] += amt;
}
```

**The guard must cover every function touching the shared state, not just the one that makes the call.**

**2. Cross-contract reentrancy.** Contract A calls out mid-update; the attacker re-enters **contract B**, which reads A's now-inconsistent state. Each contract's guard is intact; the *system* invariant is broken. This is what hit **Curve's Vyper pools in July 2023 (~$70M)** — a compiler bug meant the guards didn't actually work across functions.

**3. Read-only reentrancy.** The attacker re-enters a **`view`** function during your inconsistent window. Your contract's state is never modified — but a *different* protocol reads that view, gets a wrong price or share value, and acts on it. **`view` functions are not safe from this**, and this variant is subtle enough that it went unrecognised for years while being actively exploited.

## The defences
<!-- bite: 67732618-44df-405f-857c-4c9e6fc8bbb8 -->

**1. Checks-Effects-Interactions.** Order every function:

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    require(amount > 0, "nothing to withdraw");   // CHECKS

    balances[msg.sender] = 0;                     // EFFECTS — state updated first

    (bool ok, ) = msg.sender.call{value: amount}("");   // INTERACTIONS — last
    require(ok);
}
```

**Update state before calling out, always.** When the attacker re-enters, the balance is already zero and the second withdrawal reverts. This is the primary defence: free, and it removes the vulnerability rather than blocking it.

**2. A reentrancy guard, as backup.**

```solidity
import {ReentrancyGuardTransient} from "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";

contract Vault is ReentrancyGuardTransient {
    function withdraw() external nonReentrant { ... }
}
```

The transient-storage version costs ~200 gas instead of ~20,000 → [[web3/03-smart-contracts-with-solidity/03-storage-memory-calldata|transient storage]].

**Use both.** CEI is the real fix; the guard catches what you missed, and covers the cross-function case if applied consistently.

**3. Pull over push.** Don't send funds inside complex logic — let users withdraw in a separate, minimal transaction. Removes the reentrancy point entirely → [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|pull over push]].

## What does *not* work
<!-- bite: fd919e71-a1c7-4765-a281-73439b405a8b -->

**`.transfer()` and its 2300-gas stipend.** For years this was the recommended defence — 2300 gas isn't enough to re-enter. It's obsolete: gas costs are repriced in network upgrades, and the stipend **breaks smart-contract wallets that legitimately need more than 2300 gas to receive**. Use `.call` plus a guard. Any tutorial recommending `.transfer()` for reentrancy protection predates 2019 → [[web3/03-smart-contracts-with-solidity/04-functions-modifiers-visibility|sending ETH]].

**A boolean flag you wrote yourself** — usually right, occasionally missing a path. Use OpenZeppelin's.

**"We don't call untrusted contracts."** You call token contracts. Tokens are untrusted contracts.

## Detection
<!-- bite: 565b950c-d86c-4c39-85b6-488b118559fc -->

- **Slither** flags the basic pattern reliably. Run it in CI
- **Invariant tests** catch cross-function and cross-contract variants that static analysis misses, because they explore call sequences → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing]]
- **In review, grep for external calls** and check what state changes come after them. It's a mechanical, high-yield review pass

## Key insight
<!-- bite: 78290740-58fd-4c81-bda8-1e68c0d34af8 -->

**Reentrancy is not a special vulnerability — it's a violation of atomicity.** You made a state change in two steps and let an adversary run arbitrary code in between. Ordering effects before interactions restores atomicity, which is why CEI fixes the whole class rather than the instance. Recognising it as "an interleaving bug in a system where every external call is a yield point" also tells you where to look for the variants.

## Related
<!-- bite: 78e07a45-17ed-4163-ab62-93242be362f8 -->
- [[web3/04-smart-contract-security/01-why-this-is-different|why security is different here]]
- [[web3/04-smart-contract-security/08-case-studies|case studies]] — The DAO, Curve
- [[web3/03-smart-contracts-with-solidity/07-token-standards|token standards]] — the callback hooks
- [[os/03-scheduling|concurrency and interleaving]] — the same shape of bug, different substrate

*Source: [reference] — Aug 2026.*
