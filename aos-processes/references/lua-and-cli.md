# aos CLI, REPL and Lua traps

Source docs: 47 (CLI), 56 (Preparations), 73 (Welcome), 174 (Installing), 185 (.load), 187 (Prompt), 69 (Lua tour), 70 (aos tour), 43 (FAQ), 45/71 (Editor), 46 (ao.link), 205 (Release notes).

## Starting

```bash
aos                        # default process for the wallet (~/.aos.json is generated if no --wallet)
aos myproc                 # named process: create or reconnect
aos myproc --wallet ./key.json
aos myproc --load a.lua --load b.lua
aos mycron --cron 1-minute # cron interval only at creation time
aos mydb --sqlite          # spawn with the SQLite module
aos --tag-name Env --tag-value prod   # extra spawn tags (static config); check `aos --help` for exact flag names
```

Each `aos <name>` with the same wallet maps to the same process; use another name for a second test process (e.g. a token recipient).

The welcome guide recommends connecting directly to a HyperBEAM node for new work (exact flag in `aos --help` / cookbook "Using aos with HyperBEAM"); plain `aos` uses defaults. Release notes: aos 2.0.7 added HyperBEAM support, 2.0.8 an SDK/headless mode and state-cache support, 2.0.9 Hyper AOS with forward.computer.

## REPL commands

| Command | Effect |
|---|---|
| `.editor` … `.done` | multi-line input |
| `.load file.lua` | evaluate a local file in the process (via the Eval handler) |
| `.load-blueprint name` | load `token`, `chatroom`, `staking`, `voting`, `arena`, `apm`, `chat`, ... |
| `Handlers.list` | registered handlers |
| `#Inbox`, `Inbox[#Inbox]` | unhandled messages |
| `ao.id` | this process id |
| Ctrl-C twice | exit |

Custom prompt: define `function Prompt() return "Name@aos> " end` (e.g. show `#Inbox`, members, a token balance).

## Lua traps

- Arrays start at 1; `#t` counts the array part only (not map keys).
- Not-equal is `~=`; string concat is `..`; integer division `//`.
- Undeclared globals are `nil` (cookbook code uses `undefined`, which is just an unset global = `nil`).
- Globals persist in process memory; `local` inside a loaded file does not survive into later handlers unless captured.
- Capitalized globals (`Balances`, `Members`) are the convention for persisted state.
- `tonumber` on a 20-digit string loses precision; use `bint`.

## Debugging

- `print` output shows in the REPL and the result `Output`.
- `ao.link` shows each message's tags, data, result and the CU computation; "Fetch" calls the Info handler.
- Typical silent failures: handler order (an earlier catch-all consumed the message), case-sensitive tag values, `Data` vs tag mismatch, missing `Target`.
