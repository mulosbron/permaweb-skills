# aoconnect API

Source docs: 61 (message), 62 (spawn), 63 (signers), 196 (connect), 198 (results), 199 (assign), 224 (monitor), 230, 231.

Exports used here: `message`, `result`, `results`, `spawn`, `assign`, `monitor`, `unmonitor`, `dryrun` (legacy), `createDataItemSigner`, `connect`.

## message

```js
await message({ process, signer, tags?: [{ name, value }], data?: string, anchor? }) // → message id
```

Five parts of a message: target, data, tags, anchor, signature.

## result / results

```js
await result({ process, message })   // → { Messages, Spawns, Output, Error }
await results({ process, sort?, from?, to?, limit? })   // paginated list of results
```

Messages/Spawns in a result are already pushed by the MU; do not resend them.

## spawn

```js
await spawn({
  module: MODULE_TX_ID,                  // published ao module (WASM)
  scheduler: SU_ADDRESS,                 // legacynet SU in snapshot: _GQ33BkPtZrqxA84vM8Zk-N2aO0toNNu_C-l-rawrBA
  signer,
  tags: [{ name: "Authority", value: MU_ADDRESS }],  // legacynet MU: fcoN_xJeisVsPXA-trzVAuIiqO3ydLQxM-L4XbrQKzY
  data?: "...",                          // e.g. On-Boot code
}) // → process id
```

The addresses above are legacynet values from the snapshot. For HyperBEAM, take the scheduler/authority from the node or the cookbook migration guide.

## assign

```js
await assign({ process, message: EXISTING_MESSAGE_ID, exclude?: ["Data", "Anchor"] })
await assign({ process, message: L1_TX_ID, baseLayer: true })
```

- Loads one message into many processes without duplicating it.
- `exclude` drops capitalized DataItem fields from what the CU loads (Owner cannot be excluded).
- L1 assignments need 20 confirmations unless the process was spawned with a different `Settlement-Depth` tag.

## monitor (cron)

```js
await monitor({ process, signer });   // start pushing cron outbox results
await unmonitor({ process, signer });
```

## signers

`createDataItemSigner(walletOrJwk)` accepts an Arweave JWK or an injected browser wallet (Wander/ArConnect, Arweave Wallet Kit, arweave.app). A signer is any function `(data, tags, anchor, target) → { id, raw }` for a signed data item; Ethereum signers are accepted by AO. Create a test keyfile with `npx -y @permaweb/wallet > wallet.json`.

## connect

```js
import { connect } from "@permaweb/aoconnect";
const { message, result, spawn, dryrun } = connect({ MU_URL, CU_URL, GATEWAY_URL });  // all optional
```

Pin a specific MU/CU to debug which unit handled a message, or a non-default gateway (default arweave.net). For HyperBEAM nodes the library has a mainnet mode taking the node URL and signer; check the installed version's types.

## dryrun (legacy)

`dryrun({ process, tags, data })` evaluated a message on a CU without recording it. Deprecated for HyperBEAM: unsigned and unverifiable, it bottlenecked CUs, and state changes in the handler are discarded. Port to `~patch@1.0` + HTTP GET.
