# ArFS privacy and v0.15 upgrades

Source docs: 138 (Privacy & Encryption), 140 (Upgrading Private Drives), 115 (Encryption), 110 (EthAReum).

## Model

- Privacy is chosen per **drive** at creation (`Drive-Privacy`). Files in a private drive are private.
- **Drive key D** = HKDF-SHA256(unsalted RSA-PSS signature by the owner wallet over the drive id, user password). Encrypts drive and folder metadata.
- **File key F** = HKDF-SHA256(D, file id). Encrypts the file's metadata **and** data. Same F for every version of that file.
- Sharing one file = sharing its F; it reveals nothing else in the drive.
- ArDrive uses AES-256-GCM for metadata and small files, AES-256-CTR for files over 100 MiB. Any cipher is allowed if named in `Cipher` (`AES256-GCM` tag value in ArFS).
- Every encrypted tx: `Cipher`, its own random 12-byte `Cipher-IV` (base64), `Content-Type: application/octet-stream`.
- Byte parameters go in `Cipher-*` tags as base64.

Reference implementations exist in Dart (ArDrive app) and TypeScript (ArDrive Core JS). Do not invent a derivation; reuse theirs, or the data is unreadable by every ArFS client.

## Why v0.15 exists

Wander (formerly ArConnect) is deprecating `signature()` in favor of `signDataItem()` / `signMessage()`. V1 drive keys depended on `signature()` output, so without a bridge, V1 private drives become undecryptable once it is gone.

v0.15:

- New key derivation using the modern signing APIs.
- `drive-signature` entity: the legacy (type 1) signature encrypted under the v0.15 scheme, stored on Arweave.
- Drive entity re-issued with `Signature-Type: "1"` tag.

## Upgrade a V1 private drive

Easiest: log into ArDrive web, click "Update Now!" in the banner, sign the prompts.

Programmatic:

1. Find drives (`Entity-Type: drive`, `Drive-Privacy: private`) owned by the wallet that lack `Signature-Type`.
2. Get the legacy signature with `signature()` while the deprecation period lasts (no end date announced; after it, extra steps will be needed).
3. Upload a `drive-signature` entity with the encrypted legacy signature.
4. Upload a new drive metadata tx with the same data plus `Signature-Type: "1"`.
5. Verify both with GraphQL (`Entity-Type: drive-signature` and `Signature-Type: 1` on the drive).

Test on one drive first and keep the password; the password is unrecoverable, and losing it loses the drive.

## Security reminders

- Arweave has no encryption of its own; everything not encrypted client-side is public forever.
- Never store drive or file keys in plain text or in repo; never log passwords.
- EthAReum-derived Arweave wallets (from ETH/Solana signature + password) work with private drives; the same password caveat applies.
