# Build Your Own Smart Contract VM

> **[Intermediate → Advanced]** · A stack machine with gas metering, persistent storage and contract calls — a miniature EVM. **A weekend, ~600 lines, and `DELEGATECALL` stops being frightening because you implemented it.**

## What you're building

**A deterministic, metered virtual machine** that executes bytecode: a stack, memory, per-contract persistent storage, a gas counter that halts runaway programs, contract deployment, and contract-to-contract calls including `DELEGATECALL`.

**And what you're deliberately not:** implementing all 140 EVM opcodes, writing a Solidity compiler, or being fast. **The goal is that gas, storage costs, reverts and delegatecall stop being rules you follow and become mechanisms you built.**

**This is the deepest of the three web3 guides**, and it's the one that makes [[web3/03-smart-contracts-with-solidity/README|Solidity]] stop feeling arbitrary.

## What you need first

- **How a stack machine works** → [[foundations/compilers/09-bytecode-and-virtual-machines|bytecode VMs]] — **read this first, it's the direct prerequisite**
- **The EVM's shape** → [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]]
- Helpful: [[build-your-own-shit/04-your-own-language|your own language]] — if you've built that interpreter, this is familiar ground with new constraints

**Any language works.** Python is clearest for the interpreter loop; Go and Rust are more realistic. **The lesson is the semantics, not the performance.**

**You do not need [[build-your-own-shit/14-your-own-blockchain|guide 14]] first** — this VM runs standalone against an in-memory world state. Combining them afterwards is a satisfying extra step.

## The build order

**1. A stack machine that adds two numbers.**
Bytecode is a byte array. Loop: fetch opcode, dispatch, advance.

```python
PUSH1, ADD, STOP = 0x60, 0x01, 0x00

def run(code):
    pc, stack = 0, []
    while pc < len(code):
        op = code[pc]; pc += 1
        if op == PUSH1:
            stack.append(code[pc]); pc += 1
        elif op == ADD:
            a, b = stack.pop(), stack.pop(); stack.append(a + b)
        elif op == STOP:
            break
    return stack
```
*Works when:* `run([PUSH1, 2, PUSH1, 3, ADD, STOP])` returns `[5]`.

**2. 256-bit words, with wrapping.**
Every value is a `uint256`. Mask every arithmetic result:

```python
MAX = 2**256
def push(stack, v): stack.append(v % MAX)
```
*Works when:* `0 - 1` yields `2^256 - 1`, not `-1`. **You've just implemented the wrapping behaviour that made SafeMath necessary before Solidity 0.8** → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|arithmetic]].

**3. Gas metering.**
Each opcode has a cost. Decrement before executing; if it goes negative, throw `OutOfGas`.

```python
GAS = {ADD: 3, MUL: 5, PUSH1: 3, SSTORE: 20000, SLOAD: 2100, JUMPDEST: 1}
gas -= GAS.get(op, 1)
if gas < 0: raise OutOfGas()
```
*Works when:* an infinite loop **terminates** with `OutOfGas` instead of hanging.

**That's the whole point of gas, and you just proved it.** You cannot decide whether a program halts, so you charge it until it does → [[foundations/theory-of-computation/06-decidability|decidability]].

**4. Jumps, and why `JUMPDEST` exists.**
`JUMP` sets `pc` to a stack value. **Validate the destination is a `JUMPDEST` opcode** — otherwise a jump into the middle of a `PUSH`'s immediate data executes its argument bytes as instructions.

*Works when:* a loop counting to 10 works, and jumping to a non-`JUMPDEST` reverts.

**Pre-scan the code for valid jump destinations at load time.** Doing it per-jump is O(n) each time, and this is exactly why the real EVM has the same rule.

**5. Memory — cheap, expandable, byte-addressed.**
`MSTORE` writes 32 bytes at an offset; `MLOAD` reads. **Charge for expansion, quadratically:**

```python
def expand(mem, offset, size):
    needed = (offset + size + 31) // 32
    if needed > len(mem) // 32:
        cost = 3 * needed + needed**2 // 512    # the quadratic term
        charge(cost)
        mem.extend(b'\x00' * (needed * 32 - len(mem)))
```
*Works when:* writing at offset 1,000,000 costs vastly more than at offset 32. **Now you know why allocating big arrays in a loop is a DoS risk on yourself.**

**6. Storage — persistent, and expensive.**
A dict per contract address, surviving between calls. Charge 20,000 for zero→non-zero and 2,900 for an update.

*Works when:* two separate executions against the same contract see each other's writes, **and the gas report shows storage dominating everything else.**

**Print total gas broken down by opcode.** Seeing `SSTORE` account for 95% of a program's cost is the single most useful output this project produces → [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]].

**7. A world state, and deployment.**
`{address: {balance, code, storage}}`. Deployment runs **init code** whose *return value* becomes the stored code.

*Works when:* you deploy a contract, get an address, and can call it afterwards.

**This is where the EVM's oddest design decision lands.** The constructor isn't part of the deployed contract because the deployed contract is what the constructor *returned* → [[web3/02-ethereum-and-the-evm/02-the-evm|deployment]].

**8. `CALL` — a new execution context.**
Contract A calls B: a fresh stack, fresh memory, **B's storage**, `msg.sender = A`. Pass a gas budget; return unused gas.

*Works when:* A calls B, B writes to storage, and **the write lands in B's storage, not A's.**

**9. `REVERT`, and snapshotting.**
On revert, **all state changes in the call roll back — but gas is consumed.** The clean implementation is to snapshot state at the start of each call frame and restore on failure.

*Works when:* A calls B, B writes and reverts, and **B's write is gone while A's earlier write survives.**

**This is atomicity, hand-built.** Getting the nesting right — a revert in a nested call rolls back that frame and returns a failure flag to the parent, which may continue — is the subtle part.

**10. `DELEGATECALL` — the payoff.**
Identical to `CALL` with three changes: **use the *caller's* storage**, preserve the *original* `msg.sender`, and preserve `msg.value`.

```python
def delegatecall(target, storage_context, sender):
    code = world[target]['code']
    return execute(code, storage=storage_context, sender=sender)   # ← caller's storage
```

*Works when:* A delegatecalls B, B's code writes to slot 0, and **A's slot 0 changes while B's does not.**

**Now build a proxy:** contract A holds data and a pointer to B; every call to A delegatecalls B. **Then swap the pointer to C and watch A's behaviour change while its data persists.** You have just implemented upgradeable contracts in about 15 lines.

**And you'll immediately see the danger:** B's code writes whatever slot *it* thinks it's writing, into A's storage. **Change B's variable ordering and A's data is reinterpreted.** That's the storage-collision bug that has bricked real protocols, and it will be obvious → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]].

**11. Optional: `LOG`, and a tiny assembler.**
`LOG` appends to a receipt list — **and note there's no opcode to read it back.** That asymmetry is the whole of [[web3/03-smart-contracts-with-solidity/05-events-and-logs|events]].

A text assembler (`PUSH1 5 / PUSH1 3 / ADD`) makes writing test programs far less painful, and it's ~50 lines.

## The parts that will bite you

**Stack underflow.** Every opcode must check depth before popping. `ADD` on a one-item stack should revert, not crash your interpreter with an `IndexError`. **Wrap the dispatch loop and convert host exceptions into VM reverts** — otherwise a malicious program crashes the node, which is a real class of bug in real VMs.

**Forgetting to mask.** Miss one `% 2**256` and your VM diverges from the EVM in a way that only shows up on large numbers.

**PC advancement in `PUSH`.** `PUSH1` consumes one immediate byte, `PUSH32` consumes 32. Off by one and you execute data as code.

**Snapshot depth.** Nested calls need nested snapshots. A single global snapshot rolls back too much on a nested revert — and this bug is invisible until you have three levels of calls.

**Charging gas after execution.** Charge *before*, or an expensive operation completes and then reports out-of-gas, having already mutated state.

**Gas for the callee.** Real EVM forwards at most 63/64ths of remaining gas (EIP-150) so the caller always has enough left to handle the failure. Implementing this is optional; **knowing why it exists is not.**

## How to know it works

1. **An infinite loop halts** with `OutOfGas`
2. **Arithmetic wraps** at 2²⁵⁶
3. **Revert is atomic** — nested writes vanish, outer writes survive
4. **`CALL` vs `DELEGATECALL`** write to different storage. **The definitive test**
5. **Gas accounting is deterministic** — the same program costs exactly the same twice
6. **A proxy upgrade works**, and misaligned storage visibly corrupts data
7. **Fuzz it** — random bytes as bytecode should always terminate, never crash the host. **This catches the underflow and PC bugs immediately**

## Where to stop

**Stop after `DELEGATECALL` and the proxy demo.** That's the insight; everything past it is opcode coverage.

**Don't** implement all 140 opcodes, don't write a Solidity frontend (that's [[build-your-own-shit/04-your-own-language|the language guide]] plus this one, and it's a month), and don't optimise.

**You will have learned:** why gas exists and why it's charged the way it is; why storage costs 1000× memory and what that does to how contracts are written; what a revert actually rolls back; why `DELEGATECALL` powers every upgrade pattern and why storage layout is then load-bearing; and why determinism forces out floats, randomness and I/O.

**Solidity will stop feeling arbitrary.** Nearly every rule in [[web3/03-smart-contracts-with-solidity/README|section 03]] is a consequence of something you implemented here.

## Related
- [[foundations/compilers/09-bytecode-and-virtual-machines|bytecode VMs]] — the direct prerequisite
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] — what you're building a toy of
- [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]] — step 10, in production
- [[build-your-own-shit/04-your-own-language|your own language]] — the compiler front-end to this back-end

*Source: [reference] — build guide, Aug 2026.*
