# Arithmetic, Precision and Rounding

**[Intermediate]** — no floats, integer division truncates, and rounding in the user's favour is how protocols bleed to death.

## What changed in 0.8, and what didn't

**Solidity 0.8+ checks overflow and underflow automatically.** SafeMath is obsolete; tutorials that import it predate 2021.

**What 0.8 did *not* fix:**
- **Integer division truncates.** `7 / 2 == 3`. Always. Silently
- **Precision loss from operation order**
- **Rounding direction**
- **Type casting truncation** — `uint128(x)` on a too-large `x` silently discards the high bits
- **Anything inside `unchecked { }`**

**The overflow era is over. The precision era is permanent**, because it's a consequence of having no floats at all.

## Division truncates, so order matters

```solidity
// WRONG — divides first, loses everything below the divisor
uint256 fee = (amount / 10000) * feeBps;
//     amount = 5000, feeBps = 30  →  (5000/10000)=0 → 0 * 30 = 0.  Fee is FREE.

// RIGHT — multiply first, divide last
uint256 fee = (amount * feeBps) / 10000;
//     5000 * 30 = 150000 / 10000 = 15  ✓
```

**Rule: multiply before you divide, always.** The only reason to divide first is imminent overflow, which in `uint256` is rare and should be handled with a wider intermediate type or `mulDiv` rather than by reordering.

**And beware repeated division** — each one truncates, and the errors compound. Compute once from the original values rather than chaining.

## Fixed-point, by hand

There are no decimals, so protocols pick a scaling factor and maintain it manually:

```solidity
uint256 constant WAD = 1e18;         // the ERC-20 / DeFi convention
uint256 constant RAY = 1e27;         // higher precision, used by Aave for rates

// multiply two WAD-scaled numbers
function wmul(uint256 a, uint256 b) internal pure returns (uint256) {
    return (a * b) / WAD;            // without the /WAD you'd be at 1e36
}
```

**Every multiplication doubles the scale; every division halves it.** Losing track of scale by one factor of 1e18 is a routine bug, and it is catastrophic — off by a billion billion.

Use a library rather than hand-rolling: **`Math.mulDiv` (OpenZeppelin)** or **Solady's `FixedPointMathLib`** compute `a * b / c` at full 512-bit intermediate precision, so they don't overflow *and* don't lose precision. `mulDiv` also takes an explicit rounding direction, which is the next section.

## Rounding direction — the exploit that looks like a rounding error

**Always round in the protocol's favour.** Every "one wei" discrepancy is a free withdrawal an attacker will repeat a million times in one transaction.

```
deposit  → round shares DOWN   (user gets slightly fewer)
withdraw → round assets  DOWN  (user gets slightly less)
borrow   → round debt    UP    (user owes slightly more)
repay    → round debt    UP    (user pays slightly more)
```

The unifying rule: **when in doubt, the user gets less and owes more.** ERC-4626 specifies this normatively because so many implementations got it backwards → [[web3/03-smart-contracts-with-solidity/07-token-standards|ERC-4626]].

## The vault inflation attack

The canonical rounding exploit, and it has hit production repeatedly:

```
1. Vault is empty. Attacker deposits 1 wei → receives 1 share
2. Attacker DONATES 10,000 tokens directly to the vault (a plain transfer,
   no deposit call — so totalSupply is still 1 share, totalAssets is now huge)
3. Victim deposits 19,999 tokens
       shares = 19999e18 * 1 / 10000e18  =  1.9999...  →  truncates to 1 share
4. Attacker redeems their 1 share for half of everything
```

**The truncation in step 3 is the whole exploit.** The victim paid 19,999 for a share worth the same as one bought for 1 wei.

Defences: **seed the vault** with a real deposit at deployment so the ratio can never be manipulated from empty; use **virtual shares and assets** (OpenZeppelin's ERC4626 adds a virtual offset, making the attack cost grow exponentially); or track assets internally instead of using `balanceOf`, so donations don't count. **Do at least one.**

## Casting

```solidity
uint256 big = 2**200;
uint128 small = uint128(big);        // SILENT truncation — no revert, wrong value
```

**Explicit downcasts do not check.** Use `SafeCast`:

```solidity
using SafeCast for uint256;
uint128 small = big.toUint128();     // reverts if it doesn't fit
```

Also: `int256` ↔ `uint256` casts reinterpret bits, so casting a negative `int` to `uint` gives an astronomically large number. Any arithmetic mixing signed and unsigned deserves a second look.

## `unchecked`, used correctly

```solidity
for (uint256 i; i < len;) {
    // ...
    unchecked { ++i; }        // i < len, and len ≤ 2^256-1. Cannot overflow
}
```

Legitimate where overflow is **provably** impossible, and worth ~30–40 gas per iteration. **Justify each use in a comment** — an `unchecked` block whose premise later stops holding is a silent, permanent vulnerability.

## What to check in review

- **Every division: could the numerator be smaller than the denominator?** That's a silent zero
- **Every division: does a multiplication follow it that should have come first?**
- **Every rounding: which direction, and who benefits?**
- **Every cast: can the source exceed the destination's range?**
- **Every `unchecked`: is the premise stated and still true?**
- **Every share/asset conversion: what happens when total supply is zero?**

Fuzz tests catch most of these almost for free, because the fuzzer will try zero and `type(uint256).max` immediately → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing]].

## Key insight

**Overflow was solved by the compiler; precision cannot be, because the machine has no fractions.** Every fixed-point protocol is manually maintaining a scale factor and manually choosing a rounding direction, and the attacker's job is to find the one place you rounded toward the user. Round in the protocol's favour, multiply before dividing, and use `mulDiv`.

## Related
- [[web3/03-smart-contracts-with-solidity/07-token-standards|ERC-4626]] — where rounding is normative
- [[foundations/numerical-methods/02-floating-point-and-error|floating point and error]] — the same problems, different representation
- [[web3/07-the-application-layer/01-defi-primitives|DeFi primitives]] — where this maths lives
- [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|fuzz testing]]

*Source: [reference] — Aug 2026.*
