# ArFS entity schemas (v0.15)

Source docs: 136 (Entity Types), 137 (Creating Drives), 135 (Data Model). `?` = optional.

Version notes: v0.13 adds pins, v0.14 adds `isHidden`, v0.15 adds `Signature-Type` on drives and the `drive-signature` entity. Gateways/filters commonly match `ArFS` values `0.10`–`0.15`.

## Drive (metadata tx)

```
ArFS: "0.15"
Cipher?: "AES256-GCM"                 # private only
Cipher-IV?: "<12-byte IV, base64>"    # private only
Content-Type: "application/json" | "application/octet-stream"(private)
Drive-Id: "<uuid>"
Drive-Privacy: "public" | "private"
Drive-Auth-Mode?: "password"          # private
Signature-Type?: "1"                  # set on upgraded v1 private drives
Entity-Type: "drive"
Unix-Time: "<seconds>"
data JSON: { "name": "...", "rootFolderId": "<uuid>", "isHidden"?: false }   # encrypted with drive key if private
```

## Folder (metadata tx only)

```
ArFS, Cipher?, Cipher-IV?, Content-Type
Drive-Id: "<drive uuid>"
Entity-Type: "folder"
Folder-Id: "<uuid>"
Parent-Folder-Id?: "<uuid>"           # omitted only on the root folder
Unix-Time
data JSON: { "name": "...", "isHidden": false }
```

## File

Metadata tx:

```
ArFS, Cipher?, Cipher-IV?, Content-Type
Drive-Id, Entity-Type: "file", File-Id: "<uuid>", Parent-Folder-Id: "<uuid>", Unix-Time
data JSON: {
  "name": "photo.jpg",
  "size": 12345,                       # int bytes
  "lastModifiedDate": 1700000000000,   # ms since epoch
  "dataTxId": "<data tx id>",
  "dataContentType": "image/jpeg",
  "isHidden": false,
  "pinnedDataOwner"?: "<address>"      # pins only
}
```

Data tx (no ArFS id tags):

```
Cipher?, Cipher-IV?
Content-Type: "<file mime>" | "application/octet-stream"(private)
data: file bytes (encrypted with file key if private)
```

New version of a file = new metadata tx with the same `File-Id` (and new data tx if content changed). One file key covers all versions.

## Snapshot

```
ArFS, Drive-Id, Entity-Type: "snapshot", Snapshot-Id: "<uuid>", Content-Type: "application/json",
Block-Start, Block-End, Data-Start, Data-End, Unix-Time
data: { "txSnapshots": [ { "gqlNode": { ...GraphQL node: id, owner, tags, block, bundledIn }, "jsonMetadata": "<escaped string or null>" } ] }
```

Worth it for drives over ~1,000 files; costs an upload, saves thousands of requests and gateway rate-limit delays.

## Drive-Signature

```
ArFS: "0.15", Entity-Type: "drive-signature", Signature-Format: "1",
Cipher?: "AES256-GCM", Cipher-IV: "<12-byte IV, base64>"
data: <encrypted legacy (type 1) wallet signature>
```

## GraphQL patterns

```graphql
# all entities of a drive, owner-filtered
transactions(owners: ["<drive owner>"], tags: [{ name: "Drive-Id", values: ["<id>"] }], first: 100, after: $cursor) { ... }
# folder listing
transactions(tags: [{ name: "ArFS", values: ["0.15"] }, { name: "Parent-Folder-Id", values: [$parentFolderId] }]) { ... }
# file history
transactions(tags: [{ name: "Entity-Type", values: ["file"] }, { name: "File-Id", values: [$fileId] }]) { ... }
# latest snapshot
transactions(tags: [{ name: "Entity-Type", values: ["snapshot"] }, { name: "Drive-Id", values: [$driveId] }], sort: HEIGHT_DESC, first: 1) { ... }
```

Pinning one `ArFS` version in queries misses entities written by older clients; include every version you support.
