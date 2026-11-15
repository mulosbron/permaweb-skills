---
name: arfs
description: "Use when storing or reading file-system-shaped data on Arweave with ArFS (the ArDrive protocol): drives, folders, files, snapshots, renames/moves/versions/hiding via append-only metadata, public vs private drives, drive and file key derivation, Cipher/Cipher-IV tags, GraphQL queries to rebuild drive state, pins, or upgrading private drives to v0.15 drive signatures."
metadata:
  category: permaweb
  triggers: arfs, ardrive, private drive, drive-id, entity-type, folder-id, arweave file system, drive snapshot
---

# ArFS (Arweave File System)

ArFS models a mutable file system on immutable storage. Every change is a **new metadata transaction** with the same entity id; clients rebuild current state by replaying the timeline. References point **bottom-up** (file → parent folder → drive), so no parent ever needs rewriting.

| Entity | Transactions | Key tags |
|---|---|---|
| Drive | 1 metadata tx (+ root folder) | `Entity-Type: drive`, `Drive-Id`, `Drive-Privacy: public\|private`, `Drive-Auth-Mode?: password`, `Signature-Type?` |
| Folder | 1 metadata tx | `Entity-Type: folder`, `Folder-Id`, `Drive-Id`, `Parent-Folder-Id` (absent ⇒ root folder) |
| File | metadata tx **+** data tx | `Entity-Type: file`, `File-Id`, `Drive-Id`, `Parent-Folder-Id`; JSON has `dataTxId` |
| Snapshot | 1 tx | `Entity-Type: snapshot`, `Snapshot-Id`, `Block-Start/End`, `Data-Start/End` |
| Drive-Signature | 1 tx (v0.15) | `Entity-Type: drive-signature`, `Signature-Format: 1` |

All metadata txs also carry `ArFS: <version>` (current `0.15`), `Content-Type`, `Unix-Time` (seconds). Full schemas: `references/entity-types.md`. Encryption and v0.15 upgrade: `references/privacy-and-upgrades.md`.

## Rules

1. **Never "update" a tx.** Rename/move/edit = upload a new metadata tx with the same `File-Id`/`Folder-Id` and changed JSON or `Parent-Folder-Id`. Delete = `isHidden: true` (reversible; history stays).
2. **File content changes need a new data tx**; metadata-only changes (rename, move) do not re-upload bytes.
3. **Public metadata**: `Content-Type: application/json`. **Private**: `application/octet-stream` on both metadata and data, plus `Cipher` and a unique `Cipher-IV` per tx.
4. **Creating a drive = drive entity + root folder entity**, same name, folder's `Folder-Id` = drive JSON `rootFolderId`, folder has no `Parent-Folder-Id`. Ids are uuidv4.
5. **Ownership = first Drive entity tx's owner** for that `Drive-Id`. Ignore entities in the drive from other wallets (spam) and filter GraphQL by `owners`.
6. **Order by block height**, not `Unix-Time`. `Unix-Time` only breaks ties inside one block and can be faked.
7. **Paths are not stored.** Build them from names client-side.
8. **Pins** (v0.13+): a file entity whose `dataTxId` points to someone else's tx; only the metadata tx is created; optional `pinnedDataOwner`.

## Rebuild drive state

1. GraphQL: all txs with `Drive-Id` (and `ArFS` version, `owners: [driveOwner]`), paginate.
2. If a snapshot exists (`Entity-Type: snapshot`, `sort: HEIGHT_DESC, first: 1`), load it and only query blocks after `Block-End`.
3. Sort by height; for each entity id keep the latest; build tree from `Parent-Folder-Id`; drop `isHidden`.
4. Cache locally; next sync queries only blocks above the last seen.

Snapshot `txSnapshots[]` items are `{ gqlNode, jsonMetadata }` where `jsonMetadata` is an escaped **string** (encrypted text for private drives) and may be `null`.

## Tools

ArDrive web app (create/upgrade private drives), ArDrive CLI and ArDrive Core JS implement ArFS; Turbo pays for uploads. Gateways index ArFS with `ANS104_INDEX_FILTER` on the `ArFS` tag.

## Fetch the docs

```bash
python tools/docslice.py 136 137 138 139 140
```
