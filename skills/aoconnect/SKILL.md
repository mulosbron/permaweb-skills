---
name: aoconnect
description: "Use when a JavaScript/TypeScript app (Node or browser) talks to AO processes with @permaweb/aoconnect: sending messages, reading results, spawning processes, assignments, cron monitoring, data item signers (Arweave keyfile, Wander/ArConnect, Ethereum), choosing MU/CU/gateway or a HyperBEAM node, and replacing dryrun reads with HyperBEAM HTTP reads."
metadata:
  category: permaweb
  triggers: aoconnect, "@permaweb/aoconnect", createDataItemSigner, ao message from js, ao spawn js, ao result, ao dryrun replacement
---

# aoconnect (`@permaweb/aoconnect`)

JS/TS client for AO. Use it for **writes** (messages, spawns, assignments). For **reads**, call the HyperBEAM HTTP state endpoint (`../hyperbeam/SKILL.md`) instead of `dryrun`.

```bash
npm i @permaweb/aoconnect     # Node 18+; works in Node and browser
```

## Write a message, read its result

```js
import { message, result, createDataItemSigner } from "@permaweb/aoconnect";

const signer = createDataItemSigner(jwk);                     // Node: Arweave JWK
// browser: createDataItemSigner(globalThis.arweaveWallet)    // Wander/ArConnect, Arweave Wallet Kit, arweave.app

const messageId = await message({
  process: PROCESS_ID,                                         // becomes Target
  tags: [{ name: "Action", value: "AddBook" }],
  data: JSON.stringify(book),                                  // omit → random string
  signer,
});
const { Messages, Spawns, Output, Error } = await result({ process: PROCESS_ID, message: messageId });
```

`process` and `signer` are the only required fields. API details, spawn, assign, monitor, connect: `references/api.md`.

## Read state (no message, no dryrun)

```js
const res = await fetch(`${HB_NODE}/${PROCESS_ID}~process@1.0/compute/cache/books`);
const books = await res.json();   // published by the process with ~patch@1.0
```

## Rules

1. **Never write to read.** A `message` is signed, stored permanently on Arweave and costs; use HTTP reads for UI.
2. **Treat `dryrun` as legacy-only.** It is deprecated for HyperBEAM processes, unsigned, and drops any state change the handler makes. Migrating code: replace each `dryrun` read with a patched key + GET.
3. **Check `Error` in the result** and look for your reply in `Messages` (match `Action` and `X-Reference`); `result` does not throw on Lua errors.
4. **Never ship a JWK to the browser**; use the wallet extension signer.
5. **Tags are strings**; JSON goes in `data`.
6. **Spawning needs a Module tx id and a Scheduler (SU) address**, plus an `Authority` tag (MU) if the process must receive messages from other processes.

## Things that bite

- Results come from a CU; a just-sent message may need a moment before `result` resolves.
- Ethereum signers produce `From`/`Owner` as EIP-55 `0x` addresses inside the process.
- Cron results are only pushed if someone calls `monitor({ process, signer })`; stop with `unmonitor`.
- The cookbook pages in this snapshot lost most code blocks; signatures above follow the surviving examples. Check the installed package's types (and the cookbook "Using aoconnect with HyperBEAM" page) for `connect` options in HyperBEAM mode.

## Fetch the docs

```bash
python tools/docslice.py 61 62 63 196 198 199 224
```
