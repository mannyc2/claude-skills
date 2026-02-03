---
name: tempo-protocol
description: Tempo blockchain protocol knowledge and documentation access. Use when answering questions about Tempo, its architecture, what makes it different from other blockchains, TIP-20 tokens, payment lanes, fee sponsorship, passkey authentication, TIP-403 compliance policies, or reasoning about what to build on Tempo. Also use for Tempo-specific errors like PathUSD balance issues, eth_getBalance returning large numbers, BALANCE opcode returning zero, fee token selection problems, or TIP-20 Factory deployment. Includes scripts to fetch live docs from docs.tempo.xyz and search the GitHub repo. Essential context since Tempo launched in late 2025 and Claude lacks training data on it.
---

# Tempo Protocol

Tempo is a Layer-1 blockchain purpose-built for stablecoin payments, incubated by Stripe and Paradigm. It launched public testnet in December 2025 with mainnet planned for 2026.

## Core Thesis

General-purpose blockchains optimize for trading/DeFi, not payments. This creates problems for payment use cases: unpredictable fees during congestion, volatile gas tokens, no native compliance tooling, poor reconciliation support. Tempo makes deliberate tradeoffs to solve these specific problems.

## What Makes Tempo Different

### 1. Payment Lanes (Guaranteed Blockspace)

Tempo reserves dedicated blockspace for TIP-20 payment transactions. Payment transfers don't compete with DeFi activity, NFT mints, or smart contract calls.

**Why it matters**: A payroll run or merchant settlement executes predictably even during network congestion. Fees stay at ~$0.001 per transfer regardless of other activity.

**Technical detail**: Blocks contain isolated "sub-blocks" for payment lane transactions. Only TIP-20 transfers qualify for the payment lane.

### 2. Stablecoin-Native Gas (No Volatile Token)

Users pay transaction fees directly in USD-denominated stablecoins. The protocol includes an enshrined Fee AMM that automatically converts the user's stablecoin to the validator's preferred fee token.

**Why it matters**: No need to hold ETH/SOL/native tokens. Costs are dollar-denominated and predictable. Simpler accounting for businesses.

**Technical detail**: Any USD-denominated TIP-20 token can pay fees. The Fee AMM is a protocol-level component, not a user-deployed contract.

### 3. TIP-20 Token Standard (Enshrined ERC-20 Extensions)

TIP-20 extends ERC-20 with payment-specific features:

- **Transfer memos**: 32-byte field for invoice IDs, payment references, ISO 20022 alignment
- **Commitment patterns**: Hash/locator fields for off-chain PII and large data reconciliation
- **Currency declaration**: Tokens declare backing currency (USD, EUR) for DEX routing and fee payment eligibility
- **Built-in RBAC**: ISSUER_ROLE, PAUSE_ROLE, BURN_BLOCKED_ROLE without custom contract code
- **Reward distribution**: Opt-in yield mechanism for token holders

All TIP-20 tokens are created via the TIP-20 Factory contract. ERC-20 functions work normally.

### 4. TIP-403 Policy Registry (Shared Compliance)

Protocol-level compliance policies that can be shared across multiple tokens:

- **Whitelist policies**: Only approved addresses can transfer
- **Blacklist policies**: Blocked addresses cannot transfer
- **Single update**: Change policy once, enforced everywhere it's referenced

**Why it matters**: Regulated issuers (banks, fintechs) can enforce KYC/AML at protocol level. Multiple tokens from same issuer share one policy.

### 5. Tempo Transactions (EIP-2718 Type 0x76)

Native transaction type with smart account features without deploying contract wallets:

- **Passkey authentication**: WebAuthn/P256 signing via biometrics, secure enclave, cross-device sync
- **Batched payments**: Atomic multi-operation payouts (payroll, settlements, refunds)
- **Fee sponsorship**: Apps pay users' gas to streamline onboarding
- **Scheduled payments**: Protocol-level time windows for recurring disbursements

### 6. Sub-Second Finality

- Simplex Consensus (via Commonware): ~0.6 second finality in normal conditions
- Deterministic settlement with no reorgs
- Graceful degradation under adverse network conditions

### 7. Native Stablecoin DEX

Enshrined DEX optimized for stablecoin-to-stablecoin swaps:

- TIP-20 tokens serve as quote tokens
- Low-slippage concentrated liquidity
- Integrated with Fee AMM for gas conversion

## EVM Compatibility

- Fully EVM-compatible targeting Osaka hardfork
- Solidity, Foundry, Hardhat work out of the box
- All Ethereum JSON-RPC methods supported
- Built on Reth SDK (Paradigm's high-performance Ethereum client)

**Key differences from Ethereum**: See EVM Differences docs at https://docs.tempo.xyz/quickstart/evm-compatibility for specifics.

## Design Partners & Ecosystem

Early design input from: Visa, Mastercard, Deutsche Bank, UBS, Shopify, Nubank, Revolut, OpenAI, Klarna, Anthropic.

Klarna launched KlarnaUSD (first digital bank stablecoin on Tempo) in late 2025.

Infrastructure partners: Chainlink CCIP, Alchemy, Fireblocks, MetaMask, Phantom, LayerZero, and 40+ others.

## Target Use Cases

1. **Cross-border payments/remittances**: Instant settlement, stablecoin gas, deterministic finality
2. **Payroll & disbursements**: Batched payments, payment lanes, fee sponsorship
3. **Merchant settlements**: Memos for reconciliation, predictable fees
4. **Tokenized deposits**: Banks moving customer funds on-chain for 24/7 settlement
5. **Microtransactions**: Sub-cent fees enable digital goods, streaming payments
6. **Agentic commerce**: AI agents conducting autonomous low-cost payments

## Coming Soon (Roadmap)

- On-chain FX and non-USD stablecoin support
- Native private token standard (opt-in privacy with issuer compliance)
- Permissionless PoS validator set (currently invited validators)

## Common Gotchas & What Doesn't Work

### Wallet Integration Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| "Insufficient balance" error | Wallet checks `eth_getBalance` which returns huge number on Tempo | Remove native balance checks, use TIP-20 `balanceOf()` |
| Can't send non-TIP-20 tx | No PathUSD balance for fallback fee token | Get PathUSD from faucet, or use Tempo Transactions with explicit `fee_token` |
| `msg.value` always 0 | No native token on Tempo | Use TIP-20 transfers instead of native ETH patterns |

### Smart Contract Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| `address.balance` returns 0 | `BALANCE` opcode returns 0 on Tempo | Use `ITIP20(token).balanceOf(addr)` |
| Contract can't receive "ETH" | No native token transfers | Accept TIP-20 tokens, implement `onTIP20Received` if needed |
| Can't deploy TIP-20 directly | Must use TIP-20 Factory | Call `TIP20Factory.createToken()` at precompile address |

### Fee Sponsorship Failures

| Problem | Cause | Solution |
|---------|-------|----------|
| Sponsored tx reverts | Sponsor has insufficient balance | Verify sponsor's TIP-20 balance before signing |
| Wrong fee token used | Fee token selection cascade | Explicitly set `fee_token` in Tempo Transaction |
| High fees on non-TIP-20 calls | Falls back to PathUSD with general blockspace | Use payment lane via TIP-20 transfers when possible |

### Passkey Authentication

| Problem | Cause | Solution |
|---------|-------|----------|
| P256 signature fails | Wrong signature format | Use WebAuthn signature format, not raw ECDSA |
| Cross-device sync issues | Platform authenticator vs roaming | Test with both platform (TouchID) and roaming (YubiKey) authenticators |
| Account recovery | Passkey lost | Implement backup authentication method or social recovery |

For validation code patterns to prevent these issues, see [references/technical-details.md#validation-patterns-for-fragile-operations](references/technical-details.md#validation-patterns-for-fragile-operations).

## Network Details (Testnet)

| Property | Value |
|----------|-------|
| Network Name | Tempo Testnet (Andantino) |
| Currency | USD |
| Chain ID | 42429 |
| HTTP RPC | https://rpc.testnet.tempo.xyz |
| WebSocket | wss://rpc.testnet.tempo.xyz |
| Explorer | https://explore.tempo.xyz |
| Faucet | https://docs.tempo.xyz/quickstart/faucet |

## Accessing Tempo Documentation

### For Claude Code: How to Use This Skill

**IMPORTANT**: Script paths use `${CLAUDE_PLUGIN_ROOT}` which resolves to the plugin root directory. DO NOT use `cd` commands to navigate to the plugin directory.

**Fetching documentation:**
1. **ALWAYS check [references/docs-map.md](references/docs-map.md) first** to find the correct path
2. Use `uv run ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/fetch_docs.py <path>` to retrieve docs
3. If you get a 404 error, consult docs-map.md for alternative paths

**Fetching complete pages:**
```bash
# ✅ Correct - validates path exists in docs-map.md first, then fetches
uv run ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/fetch_docs.py /protocol/tip20/spec
uv run ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/fetch_docs.py /guide/payments

# ❌ Wrong - uses python instead of uv run
python ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/fetch_docs.py /protocol/tip20/spec

# ❌ Wrong - don't cd, use ${CLAUDE_PLUGIN_ROOT} paths directly
cd tempo-protocol && uv run scripts/fetch_docs.py /protocol/tip20/spec
```

**Searching across all docs:**
```bash
# Search for keywords in docs
uv run ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/search_repo.py "passkey" --max-matches 5
uv run ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/search_repo.py "TIP-20" --context 2 --ignore-case

# Search with regex
uv run ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/search_repo.py "0x[0-9a-f]{40}" --regex --max-matches 10

# Filter by file type
uv run ${CLAUDE_PLUGIN_ROOT}/skills/tempo-protocol/scripts/search_repo.py "transaction" --include "*.mdx,*.md" --max-matches 5
```

**When to use which:**
- Use `fetch_docs.py` when you know the exact page path (faster, cleaner output)
- Use `search_repo.py` when searching for keywords across all docs (finds all occurrences)

**Error handling strategy:**
- 404 error? Check docs-map.md for the correct path name
- Common mistake: `/protocol/transactions/spec` doesn't exist, but `/protocol/transactions/spec-tempo-transaction` does
- See docs-map.md for complete list of valid paths

### Documentation Structure

See [references/docs-map.md](references/docs-map.md) for the complete docs navigation structure and all available paths.

Common paths:
- `/quickstart/*` - Getting started, network config, EVM differences
- `/guide/*` - Building guides (accounts, payments, issuance, exchange)
- `/protocol/*` - Protocol specs (TIP-20, TIP-403, fees, transactions, blockspace)
- `/sdk/*` - SDK documentation (TypeScript, Rust, Go, Foundry)

## Deeper Technical Details

For detailed specifications on TIP-20 interfaces, TIP-403 policy structure, Tempo Transaction fields, Fee AMM mechanics, and SDK usage examples, see [references/technical-details.md](references/technical-details.md).

## Key Resources

- Documentation: https://docs.tempo.xyz
- GitHub: https://github.com/tempoxyz/tempo
- SDKs: TypeScript, Rust, Go, Foundry
- Protocol specs: https://docs.tempo.xyz/protocol
