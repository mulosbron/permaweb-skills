# Bundles, data items and tags

Source docs: 211 (What are Bundles), 116 (Tagging), 74 (ar.io glossary), 85 (What is Arweave).

## Vocabulary

| Term | Meaning |
|---|---|
| Base layer (L1) transaction | One of up to 1,000 transactions in an Arweave block |
| Data item | A signed ANS-104 binary object: owner, signature, target, anchor, tags, data. Its id is fixed at signing |
| Bundle | A transaction or data item whose data holds a set of data items in ANS-104 format. A bundle contains data items; it is not one |
| Root transaction | The L1 transaction that ultimately contains a data item (walk up through nested bundles) |
| Bundler | Service that signs/packs/posts data items (Turbo is one; gateways can run one as a sidecar) |
| Optimistic indexing | Gateways index data item headers before the L1 transaction is confirmed |
| Chunk | 256 KiB unit stored in a Merkle tree on the weave |

Why bundle: cheaper and faster for small items, fewer L1 transactions, multi-chain signing (ETH, Solana and others can sign data items), and instant ids. AO messages are data items with protocol tags.

## Tags

Key-value strings on a transaction or data item. They drive serving (`Content-Type`) and discovery (GraphQL).

Limits:

- Total tag bytes: **4 KB** for bundled data items (Turbo), **2 KB** for L1 transactions.
- No fixed count limit, only the size limit.
- Names are case-sensitive. The docs say duplicate tag names are not allowed; do not rely on duplicates.

Essential:

| Tag | Use |
|---|---|
| `Content-Type` | MIME type the gateway sends. Required in practice |
| `App-Name` | Versioned app id (`ProjectName-vMajor.Minor`), the main GraphQL filter |
| `Title`, `Description`, `Author`, `Version` | Human metadata |
| `License`, `License-Fee` | Universal Data License tx id and fee in Winston |

Protocol tags you will see:

- Bundles: `Bundle-Format: binary`, `Bundle-Version: 2.0.0`.
- Manifests: `Content-Type: application/x.arweave-manifest+json`.
- Encryption: `Cipher`, `Cipher-IV`.
- ArFS: `ArFS`, `Entity-Type`, `Drive-Id`, `Folder-Id`, `File-Id`, `Parent-Folder-Id` (see `../../arfs/SKILL.md`).
- AO: `Data-Protocol: ao`, `Variant`, `Type: Message|Process`, `Action`, `From-Process`, `Reference`, `X-Reference`, `Reply-To`.
- Turbo incremental folders: `File-SHA256`.

## Designing tags for later queries

- Put every field you will filter on into a tag; GraphQL cannot search inside data.
- Keep the value vocabulary closed and consistent (`Device-Type: Environmental-Sensor`, not free text).
- ISO-8601 timestamps in tags if you need time filters beyond block height.
- Don't put a deploy-varying value on every file of a site (see Turbo `folderIndex`).
