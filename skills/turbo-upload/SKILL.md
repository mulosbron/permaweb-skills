---
name: turbo-upload
description: "Use when uploading files, folders, static sites, or data items to Arweave via @ardrive/turbo-sdk, Turbo CLI, or turbo.ardrive.io HTTP API: Turbo credits (winc), fiat/crypto top-ups, OnDemandFunding JIT payments, x402 USDC Base uploads, credit sharing (x-paid-by), multipart chunking, incremental folder deploys (folderIndex), client-side encryption, or browser bundler polyfills (Vite, Next.js, HTML)."
metadata:
  category: permaweb
  triggers: turbo, "@ardrive/turbo-sdk", TurboFactory, uploadFolder, winc, x402, folderIndex, credit sharing, uploadFile
---

# Turbo Upload (`@ardrive/turbo-sdk`)

Uploads signed ANS-104 data items and folders to Arweave with Turbo credits (**winc**), just-in-time token funding, or x402 USDC payments.

```ts
import { TurboFactory } from '@ardrive/turbo-sdk';       // Node
// browser: import { TurboFactory } from '@ardrive/turbo-sdk/web';

const turbo = TurboFactory.authenticated({ privateKey: jwk });
const { id } = await turbo.uploadFile({ file: './dist/index.html' });
```

## References

- `TurboFactory`, signers (Arweave, EVM, Solana, browser wallets), and client methods: `references/sdk-clients.md`
- Units (`winc`), fees, free tier, top-ups, `OnDemandFunding`, `X402Funding`, credit sharing, buying ArNS names with credits: `references/credits-and-payments.md`
- Browser setup (CDN HTML, Vite, Next.js webpack polyfills, server-side signing): `references/browser-setup.md`
- HTTP endpoints (`https://turbo.ardrive.io`, `/v1/*` payment routes, x402 pricing): `references/rest-api.md`
- Multipart chunking, incremental `folderIndex` deploys, client-side encryption, CLI equivalents: `references/advanced-uploading.md`

## Rules

1. **Free tier covers data items up to 105 KiB** against a 10 MiB lifetime allowance per wallet and per subnet (never resets).
2. **Files over 10 MiB chunk automatically** (default 5 MiB chunks, `chunkingMode: 'auto'`).
3. **Incremental folder deploys (`folderIndex`)**: put per-deploy changing tags (e.g. `Git-Commit`) in `manifestDataItemOpts`, never in `dataItemOpts`—otherwise every file's cache key changes and the entire folder re-uploads.
4. **`createChainFolderIndex` needs the signer's public key** (or `{ publicKey }` / `{ address }`), not a bare `0x` or base58 address. Keep local `.turbo/folder-index.jsonl` outside the uploaded folder.
5. **Browser apps require Node polyfills** (`crypto`, `stream`, `buffer`, `process`, and rewriting `node:` imports in Next.js webpack) unless using a CDN ES module import of `@ardrive/turbo-sdk/web`. Never ship private keys to the browser.
6. **Encryption is client-side only** (`Content-Type: application/octet-stream`, `Cipher: AES-256-GCM`, unique `Cipher-IV`). For a private file system, use ArFS private drives (`../arfs/SKILL.md`).

## Fetch the docs

```bash
python tools/docslice.py 2 4 6 7 8 25 88 91 127
```
