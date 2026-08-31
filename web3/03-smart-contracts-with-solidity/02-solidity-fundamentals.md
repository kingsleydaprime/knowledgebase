# Solidity Fundamentals

**[Intermediate]** — the language, assuming you can already program. Focused on what's *different*, not on syntax you can guess.

**If you know any C-family language, most of Solidity's syntax is free.** This note covers the parts that aren't.

## A whole contract, annotated

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;              // ^0.8 gives you checked arithmetic — see below

contract Vault {
    address public immutable owner;    // set once in the constructor, stored in CODE not storage
    uint256 public totalDeposits;      // `public` auto-generates a getter
    mapping(address => uint256) public balances;

    event Deposited(address indexed who, uint256 amount);   // indexed → filterable
    error InsufficientBalance(uint256 requested, uint256 available);  // cheaper than a string

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;                             // the function body is inlined here
    }

    constructor() {
        owner = msg.sender;            // runs once, at deployment, then is discarded
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
        totalDeposits += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        uint256 bal = balances[msg.sender];
        if (amount > bal) revert InsufficientBalance(amount, bal);

        balances[msg.sender] = bal - amount;   // EFFECT before INTERACTION
        totalDeposits -= amount;

        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");
    }

    receive() external payable {}      // plain ETH transfers land here
}
```

## Types — what's different

- **No floats.** `uint256` is the workhorse; fixed-point is done by hand → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|arithmetic]]
- **`uint256` is the *cheapest* integer** despite being the largest, because the EVM word is 256 bits. Smaller types cost extra gas to mask — **except** when several pack into one storage slot, where they save far more → [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|packing]]
- **`address`** (20 bytes) and **`address payable`** — the latter can receive ETH via `.transfer`/`.send`. Cast with `payable(addr)`
- **`bytes32`** is a fixed value type and cheap; **`bytes`/`string`** are dynamic arrays and expensive. Prefer `bytes32` for short fixed labels
- **`mapping`** is not iterable, has no length, and every key exists with a zero value by default. **There is no "key not found"** — you cannot distinguish "never set" from "set to zero" without a separate flag
- **Structs and enums** work as expected; enums are `uint8` underneath

## The three data locations, in the language

Every reference type must declare where it lives, and getting this wrong is a real bug class:

```solidity
function f(uint256[] calldata input) external {   // calldata: read-only, cheapest
    uint256[] memory copy = input;                // memory: mutable, dies at end of call
    uint256[] storage saved = myArray;            // storage: a POINTER to persistent state
    saved[0] = 1;                                 // ← writes to the chain
    copy[0] = 1;                                  // ← writes to nothing that survives
}
```

**`storage` variables are references, `memory` variables are copies.** Assigning a storage struct to a `memory` local and mutating it changes nothing on-chain — a bug that passes review because it looks correct.

**Use `calldata` for external function array/string parameters.** It's free to read and skips the copy. This is the easiest gas win in the language.

## The globals

```solidity
msg.sender     // the IMMEDIATE caller — a contract if called by a contract
msg.value      // wei sent with this call
msg.data       // raw calldata
tx.origin      // the EOA that started the chain of calls — NEVER use for auth
block.timestamp, block.number, block.chainid
address(this).balance
gasleft()
```

**`tx.origin` for authorisation is a classic exploitable bug.** If your contract checks `tx.origin == owner`, then any contract the owner is tricked into calling can call yours and pass the check. **Use `msg.sender`, always** → [[web3/04-smart-contract-security/03-access-control-and-key-management|access control]].

## Errors: `require`, `revert`, `assert`

```solidity
require(cond, "message");             // input validation. Refunds remaining gas
revert MyError(a, b);                 // custom error — MUCH cheaper, and typed
assert(invariant);                    // "this must never happen". Consumes ALL gas (Panic)
```

**Custom errors (0.8.4+) are strictly better than string messages** — a four-byte selector plus ABI-encoded arguments instead of a stored string, and you get structured data at the call site. There's no reason to use string reverts in new code.

**Every revert rolls back all state changes in the entire transaction**, including those made by callers. Reverting is the safe default, and "fail loudly" is the correct instinct here in a way it isn't in a web service.

## Function modifiers, and the two that matter most

```
external  // callable from outside only — cheapest for large params
public    // callable from anywhere
internal  // this contract and children
private   // this contract only — STILL PUBLICLY READABLE ON-CHAIN

view      // reads state, doesn't write — free when called off-chain
pure      // touches no state at all
payable   // may receive ETH. Without it, sending ETH reverts
```

**`view` and `pure` are enforced by the EVM** (they compile to `STATICCALL`), so they're a real guarantee rather than documentation. **`private` is not a security boundary** and never was.

## The `0.8` arithmetic change

Before Solidity 0.8, integer overflow wrapped silently, and SafeMath was mandatory boilerplate. **Since 0.8, all arithmetic is checked and reverts on overflow.** Two things follow:

- **You no longer need SafeMath.** Tutorials telling you to import it are pre-2021
- **`unchecked { }` opts out** for a small gas saving, and is legitimate where overflow is provably impossible — canonically a `for` loop counter. Use it deliberately and rarely

## Interfaces and calling other contracts

```solidity
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

IERC20(tokenAddress).transfer(recipient, amount);
```

This compiles to an ABI-encoded `CALL`. **Nothing verifies that the address actually holds a contract with that function.** Calling a non-existent address succeeds silently with empty returndata — which is why `SafeERC20` exists, and why "the call didn't revert" is not the same as "it worked" → [[web3/03-smart-contracts-with-solidity/07-token-standards|token standards]].

## What Solidity doesn't have

No garbage collection (nothing is freed), no threads, no exceptions to catch — `try/catch` exists but only around *external calls* — no `null` (uninitialised is zero), no generics, no floats, and no standard library worth the name. **OpenZeppelin is the de facto stdlib**, and using it rather than reimplementing is the correct default.

## Key insight

**Solidity is a small, ordinary language pointed at an extremely unusual machine.** Almost every surprising rule — storage vs memory semantics, why `uint256` is cheapest, why `private` isn't private, why mappings can't be iterated — is the EVM showing through. Learn [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] and Solidity stops being arbitrary.

## Related
- [[web3/03-smart-contracts-with-solidity/03-storage-memory-calldata|storage, memory, calldata]] — this, in depth
- [[web3/04-smart-contract-security/README|smart contract security]] — read alongside, not after
- [[web3/frameworks/solidity/README|the Solidity toolchain]] — Foundry, Hardhat
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]]

*Source: [reference] — Solidity 0.8.24+. Aug 2026.*
