# Tempo EVM Differences

Tempo is fully EVM-compatible targeting the Osaka hardfork. However, there are important differences optimized for payments.

## Wallet Differences

### No Native Gas Token

On Tempo, there is **no native gas token**. The `eth_getBalance` RPC method returns an extremely large number (`0x9612084f0316e0ebd5182f398e5195a51b5ca47667d4c9b26c9b26c9b26c9b2`) to prevent "insufficient balance" errors in wallets.

**Recommendations for wallets:**
- Remove native balance checks
- Don't display "native balance" in UI
- Use currency symbol "USD" when a native token symbol is required

### Fee Token Selection

Tempo Transactions (type 0x76) allow setting the `fee_token` field to any TIP-20 token. For legacy EVM transactions, a cascading fee token selection algorithm applies:

1. **User default fee token** - If set via account preferences
2. **TIP-20 contract being called** - If calling a TIP-20 method like `transfer`, fees paid in that token
3. **Fallback to PathUSD** - For non-TIP-20 contracts

**Important**: When calling TIP-20 `transfer`, the full `amount` is sent to recipient. Fees are deducted separately from sender's balance.

## VM Layer Differences

### Balance Opcodes

| Opcode/Feature | Behavior on Tempo | Alternative |
|---------------|-------------------|-------------|
| `BALANCE` | Always returns 0 | Use TIP-20 `balanceOf()` |
| `SELFBALANCE` | Always returns 0 | Use TIP-20 `balanceOf()` |
| `CALLVALUE` | Always returns 0 | No alternative (no native value transfers) |

### Solidity Compatibility

Standard Solidity works. However:
- `msg.value` is always 0
- `address.balance` is always 0
- Use TIP-20 token transfers instead of native ETH transfers

## Consensus & Finality

| Property | Tempo | Ethereum |
|----------|-------|----------|
| Consensus | Simplex BFT | Casper FFG |
| Finality | Deterministic, ~0.6s | Probabilistic, ~12 min |
| Block time | ~0.5 seconds | ~12 seconds |
| Validator set | Permissioned (at launch) | Permissionless PoS |

## Transaction Types

Tempo supports standard EVM transaction types plus:

| Type | Description |
|------|-------------|
| 0x00 | Legacy transactions |
| 0x01 | EIP-2930 access lists |
| 0x02 | EIP-1559 dynamic fees |
| **0x76** | **Tempo Transactions** (passkeys, batching, sponsorship, scheduling) |

**Recommendation**: Use Tempo Transactions (0x76) when possible to leverage native features.

## Precompiled Contracts

Tempo adds precompiles for protocol features. Standard Ethereum precompiles (ecrecover, SHA256, etc.) are available at their usual addresses.

| Address | Contract |
|---------|----------|
| Standard | Ethereum precompiles (0x01-0x0a) |
| 0x0...100 | P256 signature verification |
| 0x0...101 | TIP-20 Factory |
| 0x0...102 | TIP-403 Registry |
| 0x0...103 | Fee AMM |
| 0x0...104 | Stablecoin DEX |

See https://docs.tempo.xyz/quickstart/predeployed-contracts for full addresses.
