# ARIO token and program addresses

Source docs: 81 (Token), 117 (Get the Token), 74 (glossary), 91 (Testnet sandbox).

## Facts

- SPL Token on Solana, 6 decimals (1 ARIO = 1,000,000 mARIO), fixed supply 1,000,000,000 ARIO, non-inflationary (rewards recycled from protocol revenue).
- Uses: gateway operator stake, delegated stake, ArNS registration/extension/undernames, protocol rewards.
- A bridged ARIO exists on Base for EVM liquidity; Solana ARIO is canonical for protocol use.

## Mainnet addresses (verify before use in wallets, swaps, configs)

| Item | Address |
|---|---|
| ARIO SPL mint | `DcNnMuFxwhgV4WY1HVSaSEgr92bv2b1vUvEKiNxWqHdF` |
| `ario-core` | `73YoECm6NKXpVRoe5f1Q9BcP5DJGPFUjnFy6AxBE5Nvh` |
| `ario-gar` | `89fNiiwgpFSPHKuqfNUkgYTYjtAJAhyqHjXmgXeppGpf` |
| `ario-arns` | `2yCUx5edFvUrkibYaUa2ZXWyx9kuJkS8CwyzsgHPWdZZ` |
| `ario-ant` | `2MWexMHfMhGJwMHv9Qm9YAVCqjUFUJwDJAysW4oCUGk5` |
| `ario-ant-escrow` | `5HZhe9UqKL5zAsdz81nuuaxV41h8bFhudzxxBigAQndM` |
| Base ARIO (bridged) | `0x138746adfA52909E5920def027f5a8dc1C7EfFb6` |

Always confirm a DEX token's mint equals the ARIO mint above; impersonation tokens exist on every chain.

## Getting it

- Solana DEXs: Jupiter, Raydium. Wallets: Phantom, Solflare, Backpack.
- ARIO Bridge between Solana and Base.
- Earn: run a gateway (minimum operator stake stated as 20,000 ARIO on the token page), delegate to a gateway, grants and bug bounties.

## Testnet

- Testnet Sandbox on Solana devnet with **staging ARIO**, mint `6vTw5CysRXQ4ybbHkDUiisHWVsBeMtUzYvJqs2iqHyaN`.
- ar.io faucet (GitHub sign-in) dispenses 2,500 staging ARIO per claim; get devnet SOL from faucet.solana.com or `solana airdrop 1 <address> --url devnet`.
- Use staging ARIO for sandbox uploads and devnet ArNS names. Override program ids in `ARIO.init` for devnet.

## Turbo and ARIO

- Turbo accepts `token: 'ario'` (Solana key) for top-ups and on-demand upload funding; ARIO console top-ups are capped at USD 100 each.
- ArNS names can be paid in ARIO directly in the console name checkout, bypassing credits.
