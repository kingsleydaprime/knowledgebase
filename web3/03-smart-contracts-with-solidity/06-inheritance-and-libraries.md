---
id: 15645ec4-39fd-499f-9d61-c36b476b72cb
---

# Inheritance, Libraries and Composition

Inheritance and libraries are two ways to reuse code in Solidity, so one contract can build on another instead of starting from nothing. Most real token contracts are built from ready-made, tested pieces rather than written from scratch. This lesson covers the rules for combining those pieces safely.

## Inheritance, and the linearisation rule
<!-- bite: 77c3ad2b-0037-4e01-8bee-fbd879f1c634 -->

Solidity has multiple inheritance resolved by **C3 linearisation** — the same algorithm as Python. The rule you need:

```solidity
contract Token is Context, ERC20, Ownable, Pausable { }
//                ↑ most base-like ................ most derived ↑
```

**Bases are declared from "most base-like" to "most derived", left to right**, and that is the reverse of the order they're called in. Get it wrong and the compiler rejects it with a linearisation error that reads like nonsense until you know this rule.

`super` calls the **next contract in the linearised order**, not the immediate parent — so in a diamond, `super.foo()` may land somewhere you didn't declare. This is how OpenZeppelin's hook pattern composes: each `_update` override calls `super._update`, and the chain runs through every mixin exactly once.

```solidity
function _update(address from, address to, uint256 v)
    internal override(ERC20, ERC20Pausable)     // must name every parent that defines it
{
    super._update(from, to, v);
}
```

**`override(A, B)` is mandatory when multiple parents define the function.** The compiler forcing you to name them is a deliberate guard against silently inheriting the wrong implementation.

## Abstract contracts and interfaces
<!-- bite: 65f65cc0-7e18-47c3-969b-cacca25782f2 -->

```solidity
interface IVault {                  // no state, no constructor, all external
    function deposit() external payable;
}

abstract contract Base {            // may have state and implemented functions
    function _hook() internal virtual;   // `virtual` = overridable
}
```

**Interfaces cost nothing at runtime** — they're a compile-time ABI description, and calling through one emits the same `CALL` as calling a raw address with the right selector.

## Libraries — two very different things under one keyword
<!-- bite: 2878035e-f881-4596-8451-5d3a6748dd35 -->

```solidity
library Math {
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }
}

using Math for uint256;             // now: someUint.max(other)
```

**`internal` library functions are inlined into your bytecode at compile time.** No call, no deployment, no gas overhead. This is how almost every library you'll use (OpenZeppelin's `Math`, `SafeCast`, `Strings`) works, and it's just code reuse with no runtime cost.

**`external`/`public` library functions are different**: the library is deployed separately, and calls to it are `DELEGATECALL`s that must be *linked* at deployment. That means:

- The library's code runs **in your contract's storage context**
- Deployment requires a link step (`--libraries` in Foundry/Hardhat)
- It saves bytecode size when several contracts share large logic — the main reason to bother
- **A library can never hold state or receive ETH**, which is the safety property that makes `DELEGATECALL` to one acceptable

**`using X for Y` is syntax only.** It attaches functions to a type for readability; nothing about dispatch changes. `using SafeERC20 for IERC20` is the most common instance you'll see, and it's the correct default for any token interaction.

## Composition beats inheritance, more here than elsewhere
<!-- bite: 7925b544-047e-4690-adaa-ca271ba81e93 -->

Deep inheritance hierarchies are actively harmful in this environment:

- **Every parent's storage variables occupy slots in the child**, so the inheritance chain *is* your storage layout — and a change in a base contract shifts every derived contract's slots → [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]]
- **Bytecode accumulates** against the 24KB deployment limit (EIP-170)
- **Auditors must read the whole chain** to know what a function does. Reviewability is a security property here, not a nicety

**Prefer separate contracts with explicit interfaces**, or small mixins with clear responsibilities. The `__gap` convention — `uint256[50] private __gap;` at the end of every upgradeable base — exists so a base can add variables later without shifting its children, and it is mandatory in upgradeable systems.

## Use OpenZeppelin
<!-- bite: 72e8588b-2ace-4750-a50f-ca9d842643d4 -->

This is the practical takeaway, and it's not a cop-out:

```solidity
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
```

**These implementations are audited, adversarially reviewed for a decade, and battle-tested across billions of dollars.** Your hand-rolled ERC-20 is not, and the bugs in it are the specific bugs OpenZeppelin already fixed.

Two caveats: **v5 made breaking changes** (`Ownable`'s constructor now requires an explicit owner argument; `_beforeTokenTransfer` was replaced by the `_update` hook), so version-match your tutorials. And **use `@openzeppelin/contracts-upgradeable` for proxy-based systems** — the standard package's constructors don't run behind a proxy → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]].

Solady is the notable alternative: same primitives, aggressively gas-optimised, assembly-heavy, less approachable to read. A reasonable choice when gas dominates and your reviewers are comfortable with it.

## Key insight
<!-- bite: bc14bd66-cb4a-44d2-a105-49ebc8500858 -->

**Inheritance in Solidity determines your storage layout, your bytecode size, and how readable your contract is to an auditor — all three of which are security-relevant.** The general advice to favour composition applies here with unusual force, and the strongest form of it is: inherit from OpenZeppelin, compose everything else.

## Related
<!-- bite: a9e161a6-b04c-4c4f-83de-dfb50fb029ed -->
- [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|upgradeability and proxies]] — where inheritance and storage collide
- [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]]
- [[concepts/02-design-patterns/index|design patterns]] — composition over inheritance, generally
- [[web3/frameworks/solidity/index|the Solidity toolchain]]

## About this lesson
<!-- bite: f3a7361d-7ccd-4ede-b60e-10cfe429fa57 -->

**Level:** Intermediate. **Covers:** C3 linearisation, what a library actually compiles to, and why OpenZeppelin is the answer to most of this.

*Source: [reference] — OpenZeppelin v5. Aug 2026.*
