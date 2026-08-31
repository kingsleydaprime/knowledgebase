# Testing and Tooling

**[Intermediate]** — Foundry, the testing techniques that are mandatory rather than advanced, and a workable local workflow.

## Why testing is different here

You cannot patch. You cannot roll back. Your code is public and holds money, and someone is paid to find your bug. **The testing bar is closer to avionics than to web development** — and the tooling has evolved to match, which is genuinely one of the field's better outcomes.

## Foundry — the default

Tests are written **in Solidity**, run in a native EVM, and are fast enough to run on every save.

```solidity
import {Test} from "forge-std/Test.sol";

contract VaultTest is Test {
    Vault vault;
    address alice = makeAddr("alice");

    function setUp() public {              // runs before EVERY test
        vault = new Vault();
        vm.deal(alice, 10 ether);          // give alice a balance
    }

    function test_Deposit() public {
        vm.prank(alice);                   // next call comes FROM alice
        vault.deposit{value: 1 ether}();
        assertEq(vault.balances(alice), 1 ether);
    }

    function test_RevertWhen_Overdrawn() public {
        vm.prank(alice);
        vm.expectRevert(abi.encodeWithSelector(
            Vault.InsufficientBalance.selector, 1 ether, 0));
        vault.withdraw(1 ether);
    }
}
```

The cheatcodes worth memorising:

```solidity
vm.prank(addr)              // next call's msg.sender
vm.startPrank(addr)         // ...until stopPrank
vm.deal(addr, amount)       // set ETH balance
vm.warp(timestamp)          // set block.timestamp
vm.roll(blockNumber)        // set block.number
vm.expectRevert(...)        // assert the next call reverts
vm.expectEmit(...)          // assert an event was emitted
vm.mockCall(...)            // stub an external contract
vm.snapshot() / revertTo()  // save and restore chain state
deal(token, to, amount)     // give an ERC-20 balance (forge-std helper)
```

```bash
forge test -vvv          # traces for failing tests. -vvvv for all
forge coverage
forge fmt
forge test --gas-report
```

## Fuzzing — the default, not an extra

Declare a parameter and Foundry generates hundreds of random inputs automatically:

```solidity
function testFuzz_DepositThenWithdraw(uint96 amount) public {
    vm.assume(amount > 0);
    vm.deal(alice, amount);

    vm.startPrank(alice);
    vault.deposit{value: amount}();
    vault.withdraw(amount);
    vm.stopPrank();

    assertEq(alice.balance, amount);       // round-trips exactly, for ANY amount
}
```

**This costs one line and finds edge cases you would never enumerate** — zero, one wei, `type(uint96).max`, boundary values around your comparisons. `uint96` rather than `uint256` keeps values in a realistic range; `vm.assume` discards inputs that don't apply.

**Write fuzz tests by default.** In this domain a unit test with three hand-picked values is the weaker choice.

## Invariant testing — the technique that finds real bugs

State a property that must hold **no matter what sequence of calls anyone makes**, and let the fuzzer attack it:

```solidity
function invariant_SolvencyHolds() public view {
    assertGe(address(vault).balance, vault.totalDeposits());
}
```

Foundry generates random sequences of calls against your contract and checks the invariant after each. **This is the closest practical thing to a proof**, and it's the technique that catches the multi-step exploits that unit tests structurally cannot — the ones where each individual call is fine and the combination isn't.

**Good invariants to reach for:** total supply equals the sum of balances; the contract is always solvent; no user can withdraw more than they deposited; a monotonic value never decreases. If you write one test beyond the happy path, make it this.

## Fork testing

Run against real mainnet state:

```solidity
function setUp() public {
    vm.createSelectFork(vm.envString("MAINNET_RPC"), 19_000_000);
}
```

Now you can test against **the actual USDT contract, the actual Uniswap pool, the actual oracle** — including all their non-compliant behaviour. Any protocol integrating with existing contracts should fork-test, because the mock you wrote behaves better than the real thing does → [[web3/03-smart-contracts-with-solidity/07-token-standards|token standards]].

Pin the block number: unpinned fork tests are non-deterministic and will fail randomly in CI.

## Static analysis

```bash
slither .                    # the standard. Fast, high signal, some noise
aderyn                       # Rust-based, newer, good output
```

**Run Slither in CI.** It catches reentrancy, uninitialised storage, unchecked return values, and shadowed variables essentially for free. Triage the false positives once and suppress them with comments.

**Formal verification** — Certora, Halmos, and the SMTChecker built into solc — proves properties over all inputs rather than sampling. Expensive in effort, appropriate for high-value core logic, and worth knowing exists.

## The rest of the toolchain

| Tool | For |
|---|---|
| **Foundry** | Testing, scripting, deployment. The default |
| **Hardhat** | JS/TS ecosystem, complex deploy pipelines, existing JS test suites |
| **Anvil** | Local node (ships with Foundry). `anvil --fork-url $RPC` for a mainnet fork |
| **Cast** | CLI for chain interaction: `cast call`, `cast send`, `cast storage`, `cast 4byte` |
| **Tenderly** | Transaction simulation and debugging on live chains. Excellent for post-mortems |
| **Etherscan** | Verify source so users can read what they're calling. **Do this on every deployment** |

**Foundry vs Hardhat:** use Foundry unless you have a specific reason — Solidity tests remove a language boundary, fuzzing and invariants are first-class, and it's dramatically faster. Hardhat wins when your deployment pipeline is already TypeScript, and the two coexist in one repo without difficulty.

## A workflow that works

```
1. forge init, write the contract
2. Write unit tests for the happy path
3. Convert them to fuzz tests — nearly free
4. Write 2-3 invariants and let them run long
5. forge coverage — aim high, and read what's uncovered rather than chasing the number
6. slither . — triage everything
7. Fork-test against real integrations
8. forge snapshot --diff in CI, so gas regressions surface at review
9. Deploy to a testnet. Use it yourself. Break it
10. Get audited before it holds real value
```

## Key insight

**Fuzzing and invariant testing are the baseline in this domain, not advanced practice.** A hand-written unit test verifies the case you imagined; an invariant test attacks the ones you didn't. Since the attacker's whole job is to find the sequence of calls you never considered, testing that generates sequences you never considered is the only kind that meets them on their ground.

## Related
- [[web3/frameworks/solidity/README|the Solidity toolchain]] — installing and configuring these
- [[web3/04-smart-contract-security/07-the-audit-process|the audit process]] — what comes after
- [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]] — measuring
- [[concepts/04-best-practices/README|best practices]] — testing generally

*Source: [reference] — Foundry, Aug 2026.*
