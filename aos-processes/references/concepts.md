# AO concepts

Source docs: 67 (Messages), 68 (Specs), 200, 201 (How it works), 202 (Processes), 203 (Units), 223 (Eval), 225 (Deprecated), 73 (Welcome), 1 (glossary).

## Units

| Unit | Role |
|---|---|
| MU (Messenger) | front door; verifies signatures, takes Outbox messages/spawns from results, signs and forwards them to SUs ("pushing") |
| SU (Scheduler) | assigns each message to a process slot (monotonic order), stores assignment + message on Arweave, serves the ordered log |
| CU (Compute) | loads the module (WASM), replays ordered messages, returns results; CUs compete to serve state |

All three scale horizontally; there can be many of each.

## Lifecycle of one message

1. Client (aoconnect/aos) POSTs a signed data item (`Data-Protocol: ao`, `Type: Message`) to the MU.
2. MU → SU; SU stores assignment + message on Arweave.
3. Client asks a CU for the result of message id; CU pulls messages from the SU since its last evaluation and evaluates.
4. Result `{ Messages, Spawns, Assignments, Output, Error }`; MU pushes outbox messages, repeating 2–4 recursively.

## Process anatomy

- A process = an init (spawn) data item referencing a **Module** (WASM binary on Arweave) and a **Scheduler**, plus its message log.
- Tags at spawn: `Module`, `Scheduler`, `Authority` (MU allowed to deliver messages), optional `On-Boot` (code from Data or a tx id), `Cron-Interval`/`Cron-Tag-*`, `Settlement-Depth` for L1 assignments, custom tags readable from `ao.env.Process.Tags`.
- Holographic state: no shared global state; each process is evaluated independently.
- **Eval**: every process has an onboard Eval handler that runs code sent by the Owner; `.load` uses it. Changing or removing `Owner` changes who can push code.
- **Assignments**: put an existing message or an L1 transaction into a process's schedule (L1 needs 20 confirmations by default).
- **Cron**: scheduled ticks; someone must monitor/push them (aoconnect `monitor`).

## Networks and state reads

- **Legacynet** (2024-02-27): original fee-free network; dryrun widely used.
- **HyperBEAM** (current production): processes addressable over HTTP (`/<pid>~process@1.0/now|compute/...`), state exposed via `~patch@1.0`. Dryrun is deprecated for HyperBEAM processes because it bottlenecked CUs; see the cookbook's migration guide.

## Spec summary

ao is a Single System Image: many parallel processes on heterogeneous nodes, coordinating only through an open message-passing layer, like websites linked by hyperlinks. Messages are ANS-104 data items; `Owner`/`From` of Ethereum-signed items are EIP-55 addresses.
