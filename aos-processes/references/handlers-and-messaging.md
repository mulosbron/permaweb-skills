# Handlers and messaging

Source docs: 1 (glossary: messaging patterns, handler flow), 184 (Inbox & Handlers), 186, 192 (Messaging), 183 (Pingpong), 59 (token blueprint), 41/60 (legacy continue wrapper).

## Handlers.add(name, pattern, handle)

| Pattern form | Matches |
|---|---|
| `"Info"` (aos 2.0+) | `msg.Action == "Info"` |
| `{ Action = "Transfer", Recipient = "_" }` | every listed tag; `"_"` = any value; values may be Lua string patterns |
| `{ Action = "X", Quantity = function(v) return tonumber(v) > 0 end }` | function-valued fields validate |
| `function(msg) return ... end` | custom: `true` / `"break"` handle and stop, `"continue"` handle and keep checking, `false`/`nil` skip |
| `Handlers.utils.hasMatchingTag("Action", "X")` | classic helper |
| `Handlers.utils.hasMatchingData("ping")` | exact Data match |

Legacy numeric returns seen in old blueprints: `-1` = continue, `1` = break, `0` = skip.

`handle` may be a function or a **resolver** table `{ [pattern] = fn, ... }` acting like switch/case.

Other registration helpers: `Handlers.once(name, pattern, fn)` (maxRuns = 1), `Handlers.utils.reply("pong")` as a canned handle, `Handlers.remove(name)`, `Handlers.list`.

Order: handlers run in `Handlers.list` order. Put "observe every message" handlers (cron ticks, finalizers, logging) first with `"continue"`.

## Sending

```lua
ao.send({ Target = pid, Action = "Transfer", Recipient = to, Quantity = "100", Data = "..." })  -- non-blocking
msg.reply({ Action = "Balance", Data = bal })      -- target = msg.From (or Reply-To); sets X-Reference
msg.forward(otherPid, { Extra = "tag" })           -- sanitized copy; keeps Reply-To, X-Reference; sets X-Origin
local res = ao.send({ Target = pid, Action = "Info" }).receive()   -- blocks until linked reply
local m = Receive({ Action = "Ready" })            -- blocks until any matching message
```

| Field | Meaning |
|---|---|
| `Reference` | per-message id assigned by the process |
| `X-Reference` | links replies to the request across hops |
| `Reply-To` | where replies should go instead of the sender |
| `X-Origin` | original sender through forwards (A → B → C → A) |
| `X-*` tags | forwarded by the token blueprint into credit/debit notices |
| `Cast` | when set on a Transfer, the token sends no notices |

## Reading in aos

```lua
#Inbox                 -- unhandled message count
Inbox[#Inbox].Data     -- newest unhandled message
Dump(Inbox[#Inbox])    -- pretty print
```

Handled messages never reach `Inbox`; that is expected.

## Message shape inside a handler

`msg.Id`, `msg.From`, `msg.Owner`, `msg.Target`, `msg.Data`, `msg.Tags` (and tags lifted as `msg.Action`, `msg.Quantity`, ...), `msg.Timestamp` (ms), `msg['Block-Height']`, `msg.Cron` for cron ticks. `ao.env.Process` has `Id`, `Owner`, `Tags`; `ao.env.Module` the module info.

## Patterns that work

- **Request/response between processes**: request handler `msg.reply(...)`; caller either handles the reply by `Action` asynchronously, or uses `.receive()` inside a coroutine-safe handler.
- **Pipelines**: A sends to B, B `msg.forward`s to C, C replies to `X-Origin`/`Reply-To` (A) directly.
- **Notify on state change**: send to subscribers on write; don't make clients poll via messages.
- **Reads for UIs**: patch state to HyperBEAM (`~patch@1.0`) and read via HTTP; don't send a message per page view.
