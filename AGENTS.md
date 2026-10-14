# Permaweb Skills

Skills for building on the permaweb: storing data on Arweave, reading and naming it through ar.io, and computing on AO / HyperBEAM. Read only the skills that match the task.

| Skill | Read when |
|---|---|
| `arweave-core/SKILL.md` | Unsure which layer applies; units (Winston, winc, mARIO); tags; path manifests; ETH/Solana owner addresses. Entry point. |
| `turbo-upload/SKILL.md` | Uploading files, folders or sites; Turbo credits, top-ups, x402; browser bundler setup. |
| `arweave-data-access/SKILL.md` | Fetching bytes from gateways; GraphQL queries by tag/owner; gateway HTTP API. |
| `wayfinder/SKILL.md` | Reading via `ar://` across many gateways with verification; replacing `arweave.net` links. |
| `arns/SKILL.md` | Human-readable names, ANT records, undernames, deploy-time pointer updates, primary names. |
| `ario-sdk/SKILL.md` | `@ar.io/sdk` on Solana: gateways, staking, vaults, epochs, ARIO token, program ids. |
| `ario-gateway-operator/SKILL.md` | Running or debugging an ar.io gateway (ar-io-node), filters, observer, joining the network. |
| `arfs/SKILL.md` | File-system data on Arweave (ArDrive protocol): drives, folders, files, private drives. |
| `aos-processes/SKILL.md` | Writing AO processes in Lua with aos; handlers, messaging, modules. |
| `aoconnect/SKILL.md` | JS/TS apps sending messages to, spawning or assigning AO processes. |
| `ao-blueprints/SKILL.md` | AO tokens (standard token spec), chatroom/staking/voting/arena blueprints, bots. |
| `hyperbeam/SKILL.md` | Reading AO state over HTTP, `~patch@1.0`, AO-Core paths and devices, running a HyperBEAM node. |

Source snapshot: `_source/permaweb-docs-2026-10-13.llms.txt` (232 documents). `_source/doc-index.md` maps every document to its skill. `python tools/docslice.py <No> | --find <term> | --list` prints documents from it.

## How to work

1. **Locate the layer before writing code.** Storage (Arweave/Turbo), access (gateways/GraphQL/Wayfinder), naming (ArNS), compute (AO/HyperBEAM) and protocol (ar.io on Solana) each have their own SDK. Mixing them up is the most common mistake.
2. **Scan the workspace** for `@ardrive/turbo-sdk`, `@ar.io/sdk`, `@ar.io/wayfinder-*`, `@permaweb/aoconnect`, `*.lua`, wallet files, `.env` gateway or process ids. Read them first; match the SDK versions you find.
3. **Check the API in the snapshot or live docs before using a method you have not seen in the skill.** These SDKs change often; the skills list the doc numbers to read.
4. **Prefer testnet first**: ar.io Testnet Sandbox (Solana devnet, faucet ARIO, data purged after ~3 days) for uploads and ArNS; a throwaway aos process for AO.

## Cross-cutting rules

- **AO: reads are HTTP GETs on HyperBEAM, writes are signed messages.** Read with `/<pid>~process@1.0/compute|now/...` and keys published via `~patch@1.0`. Do not use `dryrun` (deprecated, unsigned, drops state changes) and do not send a message just to read.
- **ar.io protocol lives on Solana now.** ARIO is an SPL token, ANTs are Metaplex Core NFTs, `@ar.io/sdk` is initialized with `ARIO.init({ rpc })`. AO-era ar.io code (`ARIO.mainnet()` on AO, ANT process ids) is legacy.
- **Everything uploaded is public and permanent.** Encrypt client-side before upload if it is private; never upload keys, `.env` files or personal data by accident.
- **Quantities are integer strings in the smallest unit** (Winston, winc, mARIO, token base units). Use bigint/`bint`, never floats.

## Boundaries

- Do not spend funds (uploads on mainnet, top-ups, ArNS purchases, staking, transfers) without explicit confirmation of amount and wallet.
- Never put a private key or JWK in browser code, a commit, or a log line.
- For a gateway operator: do not edit `.env`, restart, block content or change stake without confirmation.
- Say when information comes from a part of the docs that conflicts with another part, rather than picking silently.
