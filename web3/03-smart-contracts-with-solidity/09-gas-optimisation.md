# Gas Optimisation

**[Intermediate]** — the optimisations that are worth doing, in order, and the ones that trade safety for pennies.

## The one rule

**Storage dominates everything else.** 20,000 gas to create a slot, 2,900 to update, 2,100 to read cold — against 3 for arithmetic and 3 for a memory write.

```
one SSTORE  ≈  6,600 arithmetic operations
```

**So gas optimisation is almost entirely "touch storage less."** Optimising computation is, in nearly every case, a waste of your time and your reviewers'.

## The optimisations that actually matter

**1. Pack storage variables.** Free, mechanical, and worth 20,000 gas per slot avoided:

```solidity
// BAD — 3 slots
uint128 b;    // slot 0, half empty (nothing adjacent fits beside it)
uint256 a;    // slot 1
uint128 c;    // slot 2, half empty

// GOOD — 2 slots
uint256 a;    // slot 0
uint128 b;    // slot 1, bytes 0-15  ┐ packed
uint128 c;    // slot 1, bytes 16-31 ┘
```

Only variables **declared adjacently** pack. Reordering declarations costs nothing → [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]].

**2. Cache storage reads in locals.** Covered in [[web3/03-smart-contracts-with-solidity/03-storage-memory-calldata|storage/memory/calldata]] — hoist out of loops, write back once. Usually the largest single win in real code.

**3. Use `calldata` for external parameters.** Skips the copy to memory entirely. Free.

**4. `immutable` and `constant` are not storage.**

```solidity
address public immutable owner;    // set in constructor, baked into BYTECODE
uint256 public constant FEE = 30;  // baked in at compile time
```

Reading either costs ~3 gas instead of 2,100. **`immutable` for anything set once at deployment is close to a free win**, and it's frequently missed.

**5. Custom errors instead of strings.** `revert Unauthorized()` is four bytes; `require(x, "Unauthorized")` stores and returns a string. Saves deployment gas *and* runtime gas.

**6. Events instead of storage** for data the contract never reads back → [[web3/03-smart-contracts-with-solidity/05-events-and-logs|events]]. ~375 gas vs 20,000. A design decision, not a micro-optimisation.

**7. Transient storage for reentrancy guards.** `ReentrancyGuardTransient` costs ~200 gas instead of ~20,000 on first use.

**8. `unchecked` for provably-safe arithmetic.** Loop counters, mainly:

```solidity
for (uint256 i; i < len;) {
    // ...
    unchecked { ++i; }        // i < len < 2^256, cannot overflow
}
```

~30–40 gas per iteration. Justify each use in a comment; **this is where cleverness starts costing safety.**

## The pull-over-push pattern — safety and gas together

```solidity
// BAD: loops over an unbounded array, sends ETH to arbitrary addresses
function payAll() external {
    for (uint256 i; i < recipients.length; i++) {
        recipients[i].call{value: owed[recipients[i]]}("");   // one reverting recipient
    }                                                        // blocks EVERYONE
}

// GOOD: each recipient withdraws their own
function withdraw() external {
    uint256 amount = owed[msg.sender];
    owed[msg.sender] = 0;
    (bool ok,) = msg.sender.call{value: amount}("");
    require(ok);
}
```

The push version has **three** problems: it can exceed the block gas limit and become permanently uncallable; a single malicious recipient with a reverting `receive()` blocks all payments; and the caller pays everyone's gas. **This is a denial-of-service bug class, not just an inefficiency** → [[web3/04-smart-contract-security/README|security]].

## Measuring, which you should do before optimising

```bash
forge test --gas-report          # per-function min/avg/max
forge snapshot                   # write gas usage to a file
forge snapshot --diff            # compare against it — PUT THIS IN CI
```

**`forge snapshot --diff` in CI is the practical answer**: you see the gas cost of every PR, so regressions surface at review time rather than after deployment.

## What not to do

**Assembly for small wins.** Yul bypasses every compiler safety check — no overflow checks, no type safety, no bounds checks. It is appropriate in a hot loop after profiling, written by someone who reads the Yellow Paper for fun, and reviewed accordingly. **It is not appropriate to save 200 gas in a function called once a day.**

**Removing checks.** Deleting a `require` to save 50 gas is how funds get stolen. Every removed validation must be justified by a proven invariant, in a comment.

**Micro-optimising deployment.** You pay it once. Runtime cost, paid by every user forever, is where the actual money is.

**Optimising before it works.** Correctness, tests, then gas. Reversing that order produces fast contracts that lose money.

**Short-circuit ordering and `++i` vs `i++`** are real but tiny. Do them if free; don't contort code for them.

## The compiler settings that matter

```toml
# foundry.toml
optimizer = true
optimizer_runs = 200      # low = smaller bytecode; high = cheaper runtime
via_ir = true             # better optimisation, slower compiles
```

**`optimizer_runs` is a trade, not a quality dial**: it estimates how many times each function will be called over the contract's life. `200` favours deployment size; `1000000` favours runtime cost for a heavily-used contract. Set it to what your contract actually is.

## Key insight

**Gas optimisation is state-access optimisation.** Every genuinely large win — packing, caching, `immutable`, events-over-storage, pull-over-push — is about touching storage fewer times. Everything else is rounding error, and the assembly-level tricks trade a real safety property for an amount of gas that rarely justifies the review burden.

## Related
- [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas and fees]] — where the numbers come from
- [[web3/03-smart-contracts-with-solidity/03-storage-memory-calldata|storage, memory, calldata]]
- [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing and tooling]] — measuring it
- [[foundations/computer-architecture/12-performance|performance method]] — measure first, generally

*Source: [reference] — Aug 2026.*
