# Tempo Documentation Map

Complete navigation structure for docs.tempo.xyz. Use `scripts/fetch_docs.py` to retrieve any page.

## Quickstart / Integration

| Path | Description |
|------|-------------|
| `/quickstart/integrate-tempo` | Overview and getting started guide |
| `/quickstart/connection-details` | RPC URLs, chain ID, network config |
| `/quickstart/faucet` | Testnet faucet for test stablecoins |
| `/quickstart/developer-tools` | Third-party integrations (Alchemy, MetaMask, etc.) |
| `/quickstart/evm-compatibility` | Differences from standard Ethereum EVM |
| `/quickstart/predeployed-contracts` | Addresses of protocol contracts |

## Building Guides

### Accounts
| Path | Description |
|------|-------------|
| `/guide/use-accounts` | Overview of account types |
| `/guide/use-accounts/embed-passkeys` | WebAuthn/P256 passkey integration |
| `/guide/use-accounts/webauthn-p256-signatures` | WebAuthn P256 signature details |
| `/guide/use-accounts/connect-to-wallets` | MetaMask and wallet connections |
| `/guide/use-accounts/add-funds` | Faucet usage |

### Payments
| Path | Description |
|------|-------------|
| `/guide/payments` | Payment overview |
| `/guide/payments/send-payments` | Sending TIP-20 transfers |
| `/guide/payments/receive-payments` | Receiving and detecting payments |
| `/guide/payments/sponsor-fees` | Fee sponsorship implementation |

### Stablecoin Issuance
| Path | Description |
|------|-------------|
| `/guide/issuance` | Issuance overview |
| `/guide/issuance/create-stablecoin` | TIP-20 token creation |
| `/guide/issuance/manage-stablecoin` | Supply, roles, policies |

### Exchange
| Path | Description |
|------|-------------|
| `/guide/stablecoin-exchange` | DEX overview |

## Protocol Specifications

### TIP-20 Token Standard
| Path | Description |
|------|-------------|
| `/protocol/tip20/overview` | TIP-20 features and benefits |
| `/protocol/tip20/spec` | Full technical specification |

### TIP-20 Rewards
| Path | Description |
|------|-------------|
| `/protocol/tip20-rewards/overview` | Reward distribution system |
| `/protocol/tip20-rewards/spec` | Rewards specification |

### TIP-403 Policy Registry
| Path | Description |
|------|-------------|
| `/protocol/tip403/overview` | Compliance policy system |
| `/protocol/tip403/spec` | Policy specification |

### Fees
| Path | Description |
|------|-------------|
| `/protocol/fees` | Fee system overview |
| `/protocol/fees/fee-amm` | Fee AMM mechanics |
| `/protocol/fees/spec-fee-amm` | Fee AMM specification |

### Tempo Transactions
| Path | Description |
|------|-------------|
| `/protocol/transactions` | Transaction type 0x76 overview |
| `/protocol/transactions/spec-tempo-transaction` | Transaction specification |
| `/protocol/transactions/AccountKeychain` | Account keychain specification |

### Blockspace
| Path | Description |
|------|-------------|
| `/protocol/blockspace/overview` | Block structure overview |
| `/protocol/blockspace/payment-lane-specification` | Payment lane spec |

### Stablecoin DEX
| Path | Description |
|------|-------------|
| `/protocol/exchange` | Enshrined DEX overview |

## SDKs

| Path | Description |
|------|-------------|
| `/sdk` | SDK overview |
| `/sdk/typescript` | TypeScript SDK docs |
| `/sdk/rust` | Rust SDK docs |
| `/sdk/go` | Go SDK docs |
| `/sdk/foundry` | Foundry fork docs |

## Node Operation

| Path | Description |
|------|-------------|
| `/guide/node` | Node overview |
| `/guide/node/installation` | Installation methods |
| `/guide/node/configuration` | Node configuration |

## GitHub Source Code

Key directories in https://github.com/tempoxyz/tempo:

| Path | Contents |
|------|----------|
| `docs/` | Documentation source |
| `docs/specs/src/` | Solidity reference implementations |
| `crates/` | Rust node implementation |
| `crates/precompiles/` | Precompiled contracts (TIP-20, TIP-403, etc.) |
| `bin/` | Node binaries |

### Reference Implementations (Solidity)
- `docs/specs/src/TIP20.sol` - TIP-20 token implementation
- `docs/specs/src/TIP20Factory.sol` - Token factory
- `docs/specs/src/TIP403Registry.sol` - Policy registry
- `docs/specs/src/FeeAMM.sol` - Fee AMM contract

## Usage Examples

### Fetching Complete Pages
```bash
# Fetch a specific docs page (faster, cleaner output)
uv run scripts/fetch_docs.py /protocol/tip20/spec
uv run scripts/fetch_docs.py /guide/payments/send-payments
```

### Searching Across All Docs
```bash
# Search for keywords in docs (finds all occurrences)
uv run scripts/search_repo.py "passkey" --max-matches 5
uv run scripts/search_repo.py "TIP-20" --context 2 --ignore-case

# Search with regex patterns
uv run scripts/search_repo.py "0x[0-9a-f]{40}" --regex --max-matches 10

# Filter by file type
uv run scripts/search_repo.py "transaction" --include "*.mdx,*.md"
```

## External Resources

- Main docs: https://docs.tempo.xyz
- GitHub: https://github.com/tempoxyz/tempo
- Block explorer: https://explore.tempo.xyz
- Main site: https://tempo.xyz
- Blog: https://tempo.xyz/blog
