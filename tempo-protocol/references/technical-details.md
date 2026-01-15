# Tempo Technical Reference

Detailed specifications for Tempo protocol components. Load this file when deeper technical questions arise.

## Table of Contents

- [TIP-20 Token Standard](#tip-20-token-standard)
  - [Factory Contract](#factory-contract)
  - [Interface Extensions](#interface-extensions-over-erc-20)
  - [Built-in Roles](#built-in-roles)
  - [Payment Lane Eligibility](#payment-lane-eligibility)
- [TIP-403 Policy Registry](#tip-403-policy-registry)
  - [Policy Types](#policy-types)
  - [Token-Policy Binding](#token-policy-binding)
- [Tempo Transactions](#tempo-transactions-type-0x76)
  - [Transaction Fields](#transaction-fields)
  - [Authentication Types](#authentication-types)
  - [Fee Sponsorship Flow](#fee-sponsorship-flow)
  - [Batched Operations](#batched-operations)
  - [Scheduled Payments](#scheduled-payments)
- [Fee AMM](#fee-amm)
- [Blockspace Architecture](#blockspace-architecture)
- [Simplex Consensus](#simplex-consensus)
- [Precompiled Contracts](#precompiled-contracts)
- [SDK Quick Reference](#sdk-quick-reference)
- [Validation Patterns](#validation-patterns-for-fragile-operations) ← Use for fragile operations

---

## TIP-20 Token Standard

### Factory Contract

All TIP-20 tokens must be created through the TIP-20 Factory contract using `createToken()`. Direct deployment of TIP-20 contracts is not supported.

### Interface Extensions over ERC-20

```solidity
// Transfer with memo
function transferWithMemo(address to, uint256 amount, bytes32 memo) external returns (bool);

// Transfer with commitment (for off-chain data)
function transferWithCommitment(address to, uint256 amount, bytes32 commitmentHash, bytes32 locator) external returns (bool);

// Currency identifier
function currency() external view returns (string memory); // e.g., "USD", "EUR"

// Role management
function grantRole(bytes32 role, address account) external;
function revokeRole(bytes32 role, address account) external;
function hasRole(bytes32 role, address account) external view returns (bool);
```

### Built-in Roles

| Role | Permission |
|------|------------|
| ISSUER_ROLE | Mint and burn tokens |
| PAUSE_ROLE | Pause token transfers |
| UNPAUSE_ROLE | Unpause token transfers |
| BURN_BLOCKED_ROLE | Burn tokens from blocked addresses |

### Payment Lane Eligibility

Only TIP-20 transfers qualify for the dedicated payment lane. Smart contract interactions using TIP-20 tokens execute in the general-purpose block space.

## TIP-403 Policy Registry

### Policy Types

**Whitelist Policy**: Transfers only succeed if both sender and recipient are on the whitelist.

**Blacklist Policy**: Transfers fail if either sender or recipient is on the blacklist.

### Policy Structure

```solidity
struct Policy {
    PolicyType policyType;      // WHITELIST or BLACKLIST
    address admin;              // Can update the policy
    mapping(address => bool) list;
}
```

### Token-Policy Binding

Multiple tokens can reference the same policy. When the policy updates, all bound tokens immediately enforce the new rules.

```solidity
// In TIP-20 token
function setPolicy(address policyAddress) external; // Restricted to admin
function policy() external view returns (address);
```

## Tempo Transactions (Type 0x76)

### Transaction Fields

```
type TempoTransaction struct {
    ChainID          uint256
    Nonce            uint64
    MaxFeePerGas     uint256
    MaxPriorityFee   uint256
    Gas              uint64
    To               address      // Can be nil for batch
    Value            uint256
    Data             bytes
    
    // Tempo-specific fields
    AuthType         uint8        // 0=ECDSA, 1=P256/Passkey
    Sponsor          address      // Fee sponsor (optional)
    ScheduleAfter    uint64       // Unix timestamp (optional)
    ScheduleBefore   uint64       // Unix timestamp (optional)
    Operations       []Operation  // For batching
}

type Operation struct {
    To    address
    Value uint256
    Data  bytes
}
```

### Authentication Types

**Type 0 (ECDSA)**: Standard secp256k1 signatures, compatible with existing Ethereum wallets.

**Type 1 (P256/Passkey)**: WebAuthn signatures using the P256 curve. Enables biometric authentication via secure enclaves.

### Fee Sponsorship Flow

1. User creates unsigned transaction with `Sponsor` field set
2. Sponsor signs a sponsorship authorization
3. Transaction includes both user signature and sponsor authorization
4. Protocol deducts fees from sponsor's balance

### Batched Operations

Operations execute atomically. If any operation fails, the entire batch reverts.

```javascript
// Example: Payroll batch
const operations = [
    { to: employee1, value: salary1, data: "0x" },
    { to: employee2, value: salary2, data: "0x" },
    { to: employee3, value: salary3, data: "0x" },
];
```

### Scheduled Payments

- `ScheduleAfter`: Transaction invalid before this timestamp
- `ScheduleBefore`: Transaction invalid after this timestamp
- Both can be combined for time-windowed execution

## Fee AMM

### Purpose

Converts user's fee payment stablecoin to validator's preferred stablecoin automatically.

### Mechanism

- Protocol maintains liquidity pools between supported USD stablecoins
- When user pays in USDC but validator wants USDT, the Fee AMM swaps automatically
- Swap occurs at protocol level, not as a separate transaction
- Slippage is minimal due to stablecoin peg arbitrage

### Supported Fee Tokens

Any TIP-20 token with `currency() == "USD"` can be used for fee payment.

## Blockspace Architecture

### Block Structure

```
Block
├── Header
├── GeneralSubBlock      // Smart contracts, DeFi, etc.
│   └── Transactions[]
└── PaymentSubBlock      // TIP-20 transfers only
    └── Transactions[]
```

### Payment Lane Allocation

A percentage of each block's gas limit is reserved for the payment lane. This reservation is protocol-enforced and cannot be consumed by general transactions.

### Priority

Payment lane transactions have guaranteed inclusion if they pay the base fee. No priority fee auction required for payment lane.

## Simplex Consensus

### Properties

- **Finality**: ~0.6 seconds under normal conditions
- **Deterministic**: No probabilistic finality, no reorgs
- **BFT**: Tolerates up to 1/3 Byzantine validators

### Degradation

Under network partition or high latency, consensus gracefully slows rather than halting. Finality time increases but chain continues producing blocks.

## Precompiled Contracts

Tempo includes precompiles for:

| Address | Function |
|---------|----------|
| 0x0...100 | P256 signature verification (for passkeys) |
| 0x0...101 | TIP-20 Factory |
| 0x0...102 | TIP-403 Registry |
| 0x0...103 | Fee AMM |
| 0x0...104 | Stablecoin DEX |

See https://docs.tempo.xyz/quickstart/predeployed-contracts for full list.

## SDK Quick Reference

### TypeScript

```bash
npm install @tempo-xyz/sdk
```

```typescript
import { TempoClient, TIP20 } from '@tempo-xyz/sdk';

const client = new TempoClient('https://rpc.testnet.tempo.xyz');

// Transfer with memo
const token = new TIP20(client, tokenAddress);
await token.transferWithMemo(recipient, amount, memo);

// Create passkey-authenticated account
const account = await client.createPasskeyAccount();
```

### Foundry

```bash
# Install tempo-foundry fork
curl -L https://tempo.xyz/foundryup | bash

# Use cast with Tempo RPC
cast send --rpc-url https://rpc.testnet.tempo.xyz ...
```

### Go / Rust

See https://docs.tempo.xyz/sdk for SDK-specific documentation.

---

## Validation Patterns for Fragile Operations

Use these patterns for operations that commonly fail.

### Fee Sponsorship Validation

```typescript
// BEFORE sponsoring, validate:
async function validateSponsorship(sponsor: Address, feeToken: Address, estimatedFee: bigint) {
  const balance = await tip20.balanceOf(sponsor, feeToken);
  if (balance < estimatedFee * 120n / 100n) { // 20% buffer
    throw new Error(`Sponsor balance ${balance} insufficient for fee ${estimatedFee}`);
  }
  // Check sponsor has approved fee spending if using allowance pattern
  return true;
}
```

### Passkey Account Creation

```typescript
// Validate WebAuthn support before attempting passkey creation
async function createPasskeyAccountSafe() {
  // 1. Check WebAuthn availability
  if (!window.PublicKeyCredential) {
    throw new Error('WebAuthn not supported in this browser');
  }
  
  // 2. Check platform authenticator availability
  const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
  if (!available) {
    console.warn('No platform authenticator, will use roaming authenticator');
  }
  
  // 3. Create credential with proper error handling
  try {
    const credential = await navigator.credentials.create({
      publicKey: {
        challenge: new Uint8Array(32), // Get from server
        rp: { name: "Your App", id: window.location.hostname },
        user: { id: new Uint8Array(16), name: "user", displayName: "User" },
        pubKeyCredParams: [{ alg: -7, type: "public-key" }], // ES256 (P-256)
        authenticatorSelection: {
          userVerification: "required",
          residentKey: "preferred"
        }
      }
    });
    return credential;
  } catch (e) {
    if (e.name === 'NotAllowedError') {
      throw new Error('User cancelled passkey creation');
    }
    throw e;
  }
}
```

### TIP-20 Token Creation

```typescript
// Validate before calling TIP20Factory.createToken()
async function validateTokenCreation(params: TokenParams) {
  // 1. Check name/symbol constraints
  if (params.name.length > 64) throw new Error('Name too long (max 64)');
  if (params.symbol.length > 8) throw new Error('Symbol too long (max 8)');
  
  // 2. Validate currency code if declaring one
  const validCurrencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF'];
  if (params.currency && !validCurrencies.includes(params.currency)) {
    console.warn(`Non-standard currency: ${params.currency}`);
  }
  
  // 3. Ensure caller has fee token balance for deployment
  const deployFee = await estimateCreateTokenGas();
  await validateFeeBalance(caller, deployFee);
  
  return true;
}
```

### Batched Payment Validation

```typescript
// Validate batch before submission
async function validateBatch(operations: Operation[], sender: Address, feeToken: Address) {
  let totalValue = 0n;
  
  for (const op of operations) {
    // Check each recipient is valid
    if (op.to === sender) {
      throw new Error('Cannot send to self in batch');
    }
    totalValue += op.value;
  }
  
  // Check sender has sufficient balance for all transfers
  const balance = await tip20.balanceOf(sender, feeToken);
  const estimatedFees = await estimateBatchGas(operations);
  
  if (balance < totalValue + estimatedFees) {
    throw new Error(`Insufficient balance: have ${balance}, need ${totalValue + estimatedFees}`);
  }
  
  // Batches are atomic - if one fails, all fail
  // Consider gas limits for large batches
  if (operations.length > 100) {
    console.warn('Large batch may exceed gas limits, consider splitting');
  }
  
  return true;
}
```
