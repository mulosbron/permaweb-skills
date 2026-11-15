---
name: arweave-core
description: "Use as the entry point when building on Arweave or unsure which permaweb layer applies: storage vs access vs naming vs compute, units (Winston, winc, mARIO, Armstrong), ANS-104 bundles and tags, path manifests (arweave/paths v0.2.0), normalized ETH/Solana owner addresses for GraphQL, EthAReum wallet derivation, or permaweb glossary terms."
metadata:
  category: permaweb
  triggers: arweave, winston, winc, ans-104, bundle, tags, path manifest, normalized address, ethareum, udl
---

# Arweave Core

Entry point for the permaweb stack. Identify the right layer before picking an SDK, then follow the matching skill.

## Layer map

| Need | Skill |
|---|---|
| Upload files, folders, sites, pay with Turbo | `../turbo-upload/SKILL.md` |
| Query tags/owners via GraphQL or gateway HTTP API | `../arweave-data-access/SKILL.md` |
| Route `ar://` across gateways with verification | `../wayfinder/SKILL.md` |
| Human-readable names, ANTs, undernames | `../arns/SKILL.md` |
| Mutable file systems, drives, folders, private drives | `../arfs/SKILL.md` |
| `@ar.io/sdk` on Solana (gateways, staking, ARIO) | `../ario-sdk/SKILL.md` |
| Run or debug an ar.io gateway | `../ario-gateway-operator/SKILL.md` |
| Write AO processes in Lua (`aos`) | `../aos-processes/SKILL.md` |
| Send AO messages / spawns from JS/TS | `../aoconnect/SKILL.md` |
| AO token spec, blueprints, bots | `../ao-blueprints/SKILL.md` |
| Read AO state over HTTP (`~patch@1.0`), AO-Core paths | `../hyperbeam/SKILL.md` |

## References

- Vocabulary across Arweave, ar.io, AO, and HyperBEAM: `references/glossary.md`
- L1 transactions vs ANS-104 bundles, data items, and tag design: `references/bundles-and-tags.md`
- Path manifests (`arweave/paths` `0.2.0`) and static site hosting: `references/manifests.md`
- Native vs normalized addresses (Arweave, EVM, Solana) and EthAReum: `references/addresses-and-signers.md`

## Rules

1. **Quantities are integer strings in the smallest unit**, never floats: **Winston** (`10^-12 AR`), **winc** (Turbo credits), **mARIO** (`10^-6 ARIO`), **Armstrong** (`10^-12 AO`).
2. **Normalize EVM and Solana addresses before GraphQL `owners:` queries.** Raw `0x...` or base58 addresses return nothing; GraphQL indexes `base64url(sha256(normalizedPubkey))`, which requires recovering the public key from a prior signed tx.
3. **Tag size limits**: 4 KB total tag bytes for bundled data items (Turbo), 2 KB for L1 transactions. Names are case-sensitive; do not rely on duplicate tag names.
4. **Path manifests need `Content-Type: application/x.arweave-manifest+json`** and relative asset paths (`./...`) so sites resolve under both `https://<gateway>/<manifestId>/` and ArNS subdomains.
5. **Everything uploaded is public and permanent.** Encrypt client-side before upload if data is private, and never commit or upload JWK keyfiles.

## Fetch the docs

```bash
python tools/docslice.py 1 74 103 108 110 116 211
```
