# Advanced uploading

Source docs: 2 (chunking, folder index), 6 (Advanced Uploading), 10 (DePIN), 115 (Encryption).

## Multipart chunking

Files over 10 MiB are chunked automatically.

| Option | Default | Range / values |
|---|---|---|
| `chunkByteCount` | 5 MiB | 5 MiB to 500 MiB |
| `maxChunkConcurrency` | 5 | lower = less memory |
| `chunkingMode` | `'auto'` (chunk when it yields 3+ chunks) | `'force'`, `'disabled'` |
| `maxFinalizeMs` | 1 minute per GiB | wait for finalization |

Pass `signal: AbortSignal.timeout(ms)` to cancel.

## Incremental folder deploys (`folderIndex`)

Uploading the same static site twice pays twice unless you pass an index. The SDK hashes each file and uploads only the ones not already on Arweave; the manifest is rebuilt from reused plus new ids.

```ts
import { composeFolderIndex, createFileFolderIndex, createChainFolderIndex } from '@ardrive/turbo-sdk/node';
const folderIndex = composeFolderIndex([
  createFileFolderIndex({ filePath: '.turbo/folder-index.jsonl' }),            // local cache, keep outside the folder
  createChainFolderIndex({ owner: await turbo.signer.getPublicKey() }),        // gateway GraphQL fallback for fresh CI runners
]);
const { manifest, folderIndexSummary } = await turbo.uploadFolder({
  folderPath: './dist', folderIndex,
  manifestDataItemOpts: { tags: [{ name: 'Git-Commit', value: process.env.GITHUB_SHA }] },
});
```

- Key = sha256(bytes) + sha256(tags). A tag that changes per deploy in `dataItemOpts` changes every key and re-uploads the whole folder at full price. Move it to `manifestDataItemOpts`. The SDK logs a warning when it sees this.
- Indexed files carry an extra `File-SHA256` tag, which the chain index filters on. `hashTagName` must be identical on every layer and must not reuse a tag you write for anything else.
- `createChainFolderIndex` needs the owner as the signer's public key (or `{ publicKey }` / `{ address }`). A bare string, `0x` address or base58 Solana address is rejected.
- Chain sweep scans `pageSize * maxPages` (2,000 by default); raise it or front it with the file index for large sites.
- Browser: memory and chain indexes only; files are buffered whole for hashing, so very large files can exhaust the tab.
- Index failures count as misses: an unreachable gateway costs a re-upload, never a failed deploy.

## Encryption

Arweave has no encryption. Encrypt client-side before upload and tag it:

| Tag | Value |
|---|---|
| `Content-Type` | `application/octet-stream` |
| `Cipher` | `AES-256-GCM` (recommended) or `AES-256-CTR` for large streams |
| `Cipher-IV` | base64 IV (12 bytes for GCM) |

Anything uploaded is public and permanent. Key management is entirely yours. For a standard private file system use ArFS private drives (`../../arfs/SKILL.md`).

## Tagging recipe for discoverable data

Use consistent names and put the app version in `App-Name`:

```json
[{ "name": "Content-Type", "value": "application/json" },
 { "name": "App-Name", "value": "AirQuality-DePIN-v1.0" },
 { "name": "Device-ID", "value": "airmon-007" },
 { "name": "Data-Category", "value": "Air-Quality" }]
```

Then query by those tags with GraphQL (`../../arweave-data-access/references/graphql.md`).

## CLI equivalents

```bash
turbo upload-file --file-path data.json --tag "Content-Type:application/json" --tag "App-Name:MyApp"
turbo upload-folder --folder-path ./dist --index-file index.html
```
