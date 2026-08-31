# Build Your Own Token and Wallet

> **[Intermediate]** · An ERC-20, an NFT and an HD wallet, from scratch, deployed to a public testnet. **One evening for the contracts, one for the wallet — and at the end there is a token on a real chain that anyone in the world can hold.**

## What you're building

**Three things, deployed and usable:**

1. **An ERC-20 token** written from scratch — no OpenZeppelin — deployed to a testnet and visible in MetaMask
2. **An HD wallet** in ~150 lines: seed phrase → keys → addresses → signed transactions, using no wallet library
3. **An ERC-721 NFT** with fully on-chain SVG art, so it has no external dependency at all

**And what you're deliberately not:** launching anything with real value, writing production-grade code, or reimplementing MetaMask. **The goal is that "a token" and "a wallet" stop being products and become two hundred lines you have written.**

**This is the most applied of the three web3 guides and the best one to start with.** It produces something you can show someone.

## What you need first

- **Solidity basics** → [[web3/03-smart-contracts-with-solidity/02-solidity-fundamentals|Solidity fundamentals]]
- **What a token actually is** → [[web3/01-foundations/07-tokens-coins-and-nfts|tokens, coins and NFTs]]
- **Key derivation** → [[web3/01-foundations/03-cryptographic-primitives|cryptographic primitives]]
- **Foundry** → [[web3/frameworks/solidity/README|the Solidity toolchain]]

**Solidity for the contracts, Python or TypeScript for the wallet.** Python's `ecdsa`, `mnemonic` and `eth-utils` are the clearest; TypeScript works but the temptation to import a library that does the whole thing is stronger.

**Testnet ETH is free** — Sepolia or Base Sepolia, from a faucet. **This costs nothing.**

## Part 1 — the token

**1. The mapping, and transfer.**
Write the whole thing yourself:

```solidity
contract MyToken {
    string public name = "My Token";
    string public symbol = "MTK";
    uint8  public constant decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(uint256 initialSupply) {
        totalSupply = initialSupply;
        balanceOf[msg.sender] = initialSupply;
        emit Transfer(address(0), msg.sender, initialSupply);   // mints are a transfer from 0x0
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "insufficient");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }
}
```

*Works when:* Foundry tests pass for transfer, insufficient balance, and self-transfer.

**Stop and notice what this is.** A token is a mapping and some arithmetic. **There is no coin.** There is a row in a table with your address on it → [[web3/01-foundations/07-tokens-coins-and-nfts|tokens said plainly]].

**2. `approve` and `transferFrom`.**
The two-step dance that lets contracts spend on your behalf.

*Works when:* Alice approves Bob for 100; Bob calls `transferFrom` for 60; the allowance is 40.

**Now you understand the approve footgun.** Nothing here expires, and interfaces routinely request `type(uint256).max` to avoid a second transaction — so a later bug in the spender drains everything → [[web3/01-foundations/07-tokens-coins-and-nfts|the approve pattern]].

**3. The invariant test.**

```solidity
function invariant_SupplyEqualsSumOfBalances() public view {
    // sum tracked actors' balances; must equal totalSupply
}
```
*Works when:* Foundry's invariant fuzzer runs thousands of random call sequences and it holds → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|invariant testing]].

**4. Deploy to a testnet, and verify.**

```bash
cast wallet import deployer --interactive       # keystore, not a raw key in .env
forge create src/MyToken.sol:MyToken \
  --account deployer --rpc-url $SEPOLIA_RPC \
  --constructor-args 1000000000000000000000000 --verify
```

*Works when:* the contract is verified on the block explorer, **and you can add it to MetaMask by address and see your balance.**

**Send some to a friend.** That's a real transfer on a real chain, of a thing you wrote.

**5. Compare against OpenZeppelin.**
Read `OpenZeppelin/contracts/token/ERC20/ERC20.sol` and diff it against yours mentally. **Every difference is a lesson** — the `_update` hook, the zero-address checks, the `unchecked` blocks and why each is provably safe → [[web3/03-smart-contracts-with-solidity/06-inheritance-and-libraries|OpenZeppelin]].

**Then use OpenZeppelin from now on.** Having written it yourself is exactly what earns you the right to stop.

## Part 2 — the wallet

**6. Seed phrase to master key (BIP-39).**

```python
from mnemonic import Mnemonic
m = Mnemonic("english")
words = m.generate(strength=128)          # 12 words
seed  = m.to_seed(words)                  # 64 bytes, via PBKDF2
```
*Works when:* the same words always produce the same seed, and **a one-word change produces a completely different one.**

**7. HD derivation (BIP-32/44).**
Derive the child key at `m/44'/60'/0'/0/0` — HMAC-SHA512 down the path.

*Works when:* **your derived address matches what MetaMask shows for the same seed phrase.**

**That match is the moment worth building this for.** You've just independently reproduced what every wallet in the world does, and confirmed the standard is genuinely a standard → [[web3/01-foundations/03-cryptographic-primitives|BIP-32/39/44]].

**8. Public key to address.**

```python
pub = private_key.get_verifying_key().to_string()    # 64 bytes, uncompressed
address = '0x' + keccak(pub)[-20:].hex()            # last 20 bytes of keccak
```
*Works when:* it matches step 7's address. **Note it's Keccak-256, not SHA3-256** — the padding differs, and this trips up almost everyone once.

**9. Derive ten addresses**, incrementing the last path index.

*Works when:* MetaMask's accounts 1–10 for that seed are your list, in order. **Now "one backup restores every account" is a mechanism, not a claim.**

**10. Sign and broadcast a transaction, by hand.**
RLP-encode the transaction fields, hash, sign with ECDSA, attach `v/r/s`, and send the raw bytes:

```python
raw = rlp_encode(signed_tx)
requests.post(RPC, json={"jsonrpc":"2.0","method":"eth_sendRawTransaction",
                         "params":[raw.hex()],"id":1})
```

*Works when:* **the transaction confirms on a testnet and the explorer shows the correct sender** — which you never specified, because it was recovered from your signature → [[web3/01-foundations/03-cryptographic-primitives|recoverable signatures]].

**Include the `chainId`.** Without EIP-155's chain ID in the signed payload, the transaction is replayable on any other chain.

## Part 3 — the NFT

**11. ERC-721 with on-chain SVG.**

```solidity
function tokenURI(uint256 id) public pure returns (string memory) {
    string memory svg = string.concat(
        '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">',
        '<rect width="300" height="300" fill="#', colorFor(id), '"/>',
        '<text x="150" y="150" text-anchor="middle" fill="white">#', id.toString(), '</text>',
        '</svg>');
    return string.concat('data:application/json;base64,', Base64.encode(bytes(
        string.concat('{"name":"Token #', id.toString(),
                      '","image":"data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '"}'))));
}
```

*Works when:* you mint on a testnet and **the image renders in OpenSea's testnet view and in MetaMask.**

**No IPFS, no server, no pinning bill.** The art is in the contract, and it lasts exactly as long as the chain does → [[web3/06-building-dapps/05-decentralised-storage|storage]].

**12. Guard `safeMint`.**
`_safeMint` calls `onERC721Received` on the recipient — **handing control to the minter mid-transaction.** Add a per-wallet limit, then write a test contract that re-enters to bypass it. **Watch it work.** Then apply Checks-Effects-Interactions and watch it stop → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]].

## The parts that will bite you

**Decimals.** `1 token` is `1e18`, and every UI number needs converting at exactly one boundary. Convert twice and you're off by 10¹⁸ → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|arithmetic]].

**Keccak-256 vs SHA3-256.** They are different. Python's `hashlib.sha3_256` is **not** what Ethereum uses; you want `eth_hash` or `pycryptodome`'s `keccak`.

**RLP encoding.** Fiddly and unforgiving. Length prefixes for short vs long payloads differ, and an error produces a transaction the node rejects with an unhelpful message. **Test your encoder against a known-good encoding first.**

**Forgetting `chainId`.**

**A raw private key in `.env`.** Use `cast wallet import`. **And never reuse a testnet key on mainnet** — testnet keys leak constantly, and reuse is how a harmless leak becomes a real one → [[web3/04-smart-contract-security/03-access-control-and-key-management|key management]].

**Missing zero-address checks.** Transfers to `address(0)` burn tokens permanently. OpenZeppelin reverts; your version probably won't.

## How to know it works

1. **The token appears in MetaMask** and transfers between two accounts you control
2. **The invariant holds** under Foundry's fuzzer
3. **Your derived address matches MetaMask's** for the same seed — **the key test**
4. **A hand-signed transaction confirms on a testnet**
5. **The NFT renders** in a marketplace without any external request
6. **Your reentrancy test bypasses the mint limit**, then stops after the fix
7. **The contract is verified on the explorer** and someone else can interact with it

## Where to stop

**Stop after the NFT renders and the hand-signed transaction confirms.**

**Don't** deploy to mainnet, don't add real value, and don't build a wallet UI — that's ordinary frontend work and teaches nothing new here.

**Above all: do not launch a token.** An unaudited token holding other people's money is how the case studies in [[web3/04-smart-contract-security/08-case-studies|section 04]] start.

**You will have learned:** that a token is a mapping and nothing more; why the approve pattern is dangerous and unavoidable; that a seed phrase deterministically generates every key you'll ever have; that a transaction has no `from` field because the sender is *computed*; and that a wallet is a key manager, not a container.

**And you'll read token contracts differently.** A `mint` function, a blacklist or an upgrade key will jump out of a contract, because you know exactly what the honest version looks like → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|reading a token before touching it]].

## Related
- [[web3/03-smart-contracts-with-solidity/07-token-standards|token standards]] — what you just implemented, properly
- [[web3/01-foundations/07-tokens-coins-and-nfts|tokens, coins and NFTs]] — the theory
- [[web3/frameworks/solidity/README|the Solidity toolchain]] — Foundry, in detail
- [[build-your-own-shit/15-your-own-smart-contract-vm|your own smart contract VM]] — the machine this runs on

*Source: [reference] — build guide, Aug 2026.*
