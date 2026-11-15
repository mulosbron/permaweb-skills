---
name: aos-processes
description: "Use when writing or debugging AO processes in Lua with aos: the aos CLI and REPL (.load, .editor, --wallet, --cron, --sqlite), Handlers.add patterns and handler flow, msg.reply / ao.send / Receive messaging, Inbox, globals (Owner, Name, ao.env), built-in modules (json, bint, crypto, base64, utils, pretty), WeaveDrive, SQLite, eval, determinism, and MU/SU/CU message flow."
metadata:
  category: permaweb
  triggers: aos, ao process, lua handler, Handlers.add, msg.reply, ao.send, .load, ao computer, ao inbox
---

# aos and AO processes

An AO **process** is an actor: its state is implied by the ordered log of messages it received (holographic state). You write its logic in Lua (or any WASM language) and talk to it only with **messages** (ANS-104 data items). `aos` is the Lua runtime plus an interactive shell.

Messages flow: client → **MU** (checks signature, pushes outbox messages) → **SU** (assigns slot/order, stores on Arweave) → **CU** (replays messages through the module, returns `{ Messages, Spawns, Output, Error }`). The MU keeps pushing outbox messages until none are left.

Details: `references/handlers-and-messaging.md` (patterns, flow control, reply chains), `references/modules.md` (json, bint, crypto, base64, utils, pretty, ao), `references/lua-and-cli.md` (aos CLI, REPL commands, Lua traps), `references/concepts.md` (units, process anatomy, eval, Ethereum signers), `references/weavedrive-sqlite.md`.

## Minimal process

```lua
-- counter.lua   (load with: .load counter.lua)
Counter = Counter or 0          -- `X = X or default` keeps state across reloads

Handlers.add("Increment", "Increment", function(msg)   -- string pattern = Action tag match (aos 2.0+)
  Counter = Counter + 1
  msg.reply({ Data = tostring(Counter) })
end)

Handlers.add("Get", { Action = "Get" }, function(msg)  -- table pattern
  msg.reply({ Action = "Count", Data = tostring(Counter) })
end)
```

```lua
Send({ Target = ao.id, Action = "Increment" })   -- from the aos prompt
Inbox[#Inbox].Data                                 -- read the reply
```

## Reads vs writes (decide this first)

| Need | Do | Never |
|---|---|---|
| Change state | signed **message** (`ao.send` / aoconnect `message`) → stored on Arweave, ordered by the SU | – |
| Read state (UI, API, other services) | HTTP GET on HyperBEAM: `/<pid>~process@1.0/compute/...` (last known, fast) or `/now/...` (recompute); publish only what clients need with `~patch@1.0` and read it under `/cache/...` | send a real message per read (permanent, costs, slow); use **dryrun** (deprecated: unsigned, unverifiable, bottlenecked CUs) |

Consequences for handler design:

- A "read" handler that also mutates (`Books[id].views = Books[id].views + 1` inside `GetBook`) silently did nothing under dryrun and does nothing over HTTP reads either. Count views with an explicit write message (or off-chain), not inside a getter.
- After every write that changes public data, re-publish it with `~patch@1.0` in the same handler so HTTP readers see it at the next `compute`.
- HyperBEAM responses are signed by the node's key (and TEE nodes can attest their hardware), so HTTP reads are verifiable; dryrun answers were not.
- Existing code full of `dryrun(...)` is legacy-network code. Port reads to HTTP + patch; keep dryrun only when you are explicitly on legacynet and say so.

Patch and path details: `../hyperbeam/references/pathing-and-devices.md`.

## Rules

1. **Initialize state with `X = X or default`.** `.load` re-runs the whole file; a bare `X = {}` wipes state on every reload.
2. **Handlers run in order and the first match handles the message** unless its pattern returns `"continue"`. Unmatched messages go to `Inbox` (bounded). Use `Handlers.list` to inspect order and names; re-adding a name replaces that handler.
3. **Validate `msg.From`** for anything privileged (mint, config, admin). Anyone can send any tags. `Owner` and `ao.env.Process.Owner` identify the owner; `Owner = nil` locks the process.
4. **Tag values are strings.** Quantities travel as strings; use `bint` for token math, never Lua floats.
5. **Be deterministic.** No wall clock, no `math.random` without a seed derived from message data, no I/O. Use `msg.Timestamp` / `msg['Block-Height']` for time.
6. **Reply with `msg.reply`** so `X-Reference` links the response to the request; use `msg.forward` for pipelines (keeps `X-Origin`, `Reply-To`).
7. **Ethereum-signed messages/processes** have `From`/`Owner` as an EIP-55 `0x...` address, not a 43-char id. Compare accordingly.

## Things that bite

- The aos 2.0 string pattern `"Name"` matches `Action == "Name"`; older code uses `Handlers.utils.hasMatchingTag("Action", "Name")`. Old blueprints return `-1`/`1`/`0` from patterns (legacy for continue/break/skip); prefer `"continue"`/`"break"`.
- `Send` (REPL convenience) and `ao.send` are interchangeable in aos; `ao.send` returns the message and is preferred inside handlers.
- `.receive()` on a send, and `Receive(pattern)`, **block** the handler (coroutine) until a matching message arrives.
- `Data` may be a string; JSON must be `json.decode`d. `msg.Tags.X` and `msg.X` both work in aos 2 (tags are lifted onto msg).
- Lua tables are 1-indexed, `~=` is not-equal, `#t` counts only the array part.
- The cookbook pages in this snapshot lost their code blocks during extraction; when exact syntax matters, check `cookbook_ao.arweave.net` (`llms.txt` / `llms-full.txt`).

## Tooling

- Install: Node 20+, then the aos installer from the cookbook (`npm i -g https://get_ao.g8way.io` in this snapshot; on Windows prefer WSL).
- Editor: VS Code `sumneko.lua` + "ao" addon in the Lua Addon Manager, or BetterIDEa (web IDE with ao LSP and APM).
- Explorer: `https://ao.link` (messages, results, process graph, token balances).
- Packages: `.load-blueprint apm` then `apm.install('@scope/pkg')`.

## Fetch the docs

```bash
python tools/docslice.py 184 186 192 201 202 203
python tools/docslice.py --find Handlers.add
```

Live: `https://cookbook_ao.arweave.net` (`llms.txt`, `llms-full.txt`).
