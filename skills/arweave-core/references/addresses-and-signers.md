# Addresses, public keys and cross-chain signers

Source docs: 108 (Normalized Addresses), 110 (EthAReum), 74.

## Native vs normalized

| | Arweave | ETH / POL / Base | Solana |
|---|---|---|---|
| Public key | JWK `n` (RSA-4096), base64url | 65-byte uncompressed ECDSA (`0x04...`) | 32 bytes |
| Native address | base64url(sha256(pubkey)), 43 chars | `0x` + last 20 bytes of keccak256(pubkey without `04`) | base58(pubkey) |
| Normalized public key (GraphQL `owner.key`) | the JWK `n` | base64url(pubkey without `0x` and `04`) | base64url(32-byte pubkey) |
| Normalized address (GraphQL `owner.address`, `owners:` filter) | same as native | base64url(sha256(normalized pubkey)) | base64url(sha256(normalized pubkey)) |

Consequences:

- GraphQL `owners: ["0x..."]` or a base58 address returns nothing. Convert to the normalized address first.
- To normalize you need the **public key**, not just the address. EVM: recover it from any transaction the address **sent** (ECDSA recovery from r, s, v; v is 0/1 for EIP-1559/2930, 27/28 legacy, `chainId*2+35+bit` for EIP-155). Solana: the first account key of any transaction it signed. An address that never sent a transaction cannot be normalized.
- The tool `ar://normalize-my-key` does this lookup.
- Turbo credits for an EVM or Solana wallet are keyed by its native address; data items it signs show the normalized owner.

## EthAReum

Derives a full Arweave wallet (JWK) deterministically from an Ethereum or Solana wallet **signature plus a user password**. Used by ArDrive so MetaMask/Phantom users get an Arweave wallet without a keyfile.

- The derived Arweave address differs from the ETH/Solana address.
- The password is part of the derivation; lose it and the wallet is gone. No admin recovery.
- One-way: the derived wallet cannot touch the ETH/Solana assets.
- Only sign derivation messages on trusted dApps; a malicious site can disguise an authorization as a "sign to connect" prompt.

## Signing on other chains directly

Turbo and AO accept data items signed by Arweave, EVM and Solana keys (ANS-104 supports multiple signature types). You often do not need an Arweave wallet at all: use the chain's signer (`EthereumSigner`, `InjectedEthereumSigner`, Solana keypair) and set the matching `token` in Turbo.

## Keyfile vs seed phrase

The Arweave ecosystem mostly uses JWK keyfiles. Seed phrases exist but not every dApp supports them. Create a wallet for scripts with `npx permaweb/wallet > key.json`; never commit it.
