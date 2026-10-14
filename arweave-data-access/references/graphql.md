# Arweave GraphQL

Source docs: 5 (Find Data), 98 (Index Querying), 10 (DePIN queries).

## Endpoints

| Endpoint | Coverage |
|---|---|
| `https://turbo-gateway.com/graphql` | all Arweave data; browser opens an Apollo Sandbox with schema docs |
| `https://arweave-search.goldsky.com/graphql` | all Arweave data, high performance |
| `https://<any ar.io gateway>/graphql` | only what that gateway indexed (see its unbundle/index filters) |

Request: `POST` with `Content-Type: application/json` and body `{ "query": "...", "variables": { ... } }`.

## Root fields

- `transaction(id: "...")` — single transaction or data item.
- `transactions(...)` — connection with `edges { cursor node }` and `pageInfo { hasNextPage }`.
- Block queries by id and height are also supported.

### `transactions` arguments

| Arg | Use |
|---|---|
| `ids: [ID!]` | fetch specific ids |
| `owners: [String!]` | normalized owner addresses |
| `recipients: [String!]` | `target` addresses |
| `tags: [{ name, values: [..] }]` | AND across entries, OR across `values` |
| `bundledIn: [ID!]` | items inside given bundles |
| `block: { min, max }` | height range |
| `sort: HEIGHT_DESC \| HEIGHT_ASC` | order |
| `first`, `after` | page size, cursor |

### Useful node fields

`id`, `owner { address key }`, `recipient`, `tags { name value }`, `data { size type }`, `block { height timestamp id }` (`null` while unmined), `bundledIn { id }`, `signature`, `fee`, `quantity`.

## Pagination loop

```ts
let cursor: string | null = null, all = [];
do {
  const res = await fetch('https://turbo-gateway.com/graphql', { method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: Q, variables: cursor ? { cursor } : {} }) }).then(r => r.json());
  const { edges, pageInfo } = res.data.transactions;
  all.push(...edges);
  cursor = pageInfo.hasNextPage && edges.length ? edges.at(-1).cursor : null;
} while (cursor);
```

Declare `query($cursor: String)` and pass `after: $cursor`; GraphQL treats a null cursor as the first page.

## Query design

- Order tags most specific to most general.
- Add `owners` whenever the data was written by known wallets; it is cheap and blocks spoofed data from strangers using your tag names.
- Do not trust tags alone for authenticity: anyone can write `App-Name: YourApp`. Filter by owner or verify signatures.
- Ask only for fields you need; `tags` on thousands of nodes is heavy.
- Latest-version patterns: tag each version with an entity id and query `sort: HEIGHT_DESC, first: 1`. Unmined items have no height, so check the most recent upload separately if ordering matters immediately after upload.

## Examples

Latest 10 HTML pages from an app:

```graphql
query { transactions(tags: [{ name: "Content-Type", values: ["text/html"] }, { name: "App-Name", values: ["MyApp"] }],
                     sort: HEIGHT_DESC, first: 10) { edges { node { id tags { name value } data { size } } } } }
```

Which bundle holds an item, and is it mined:

```graphql
query { transaction(id: "<id>") { owner { address } bundledIn { id } block { height } } }
```
