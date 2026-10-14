---
name: ao-blueprints
description: "Use when building tokens or common app patterns as AO processes: the ao Standard Token spec (Info, Balance, Balances, Transfer, Mint, Burn, Total-Supply, Credit/Debit-Notice), the token/chatroom/staking/voting/arena blueprints, tokengating, autonomous bot agents and arena games, and reviewing token handler code for balance-math and authorization bugs."
metadata:
  category: permaweb
  triggers: ao token, token blueprint, Credit-Notice, Debit-Notice, ao staking, ao voting, chatroom blueprint, arena game, ao bot, tokengating
---

# AO blueprints and tokens

Blueprints are Lua files aos loads into your process: `.load-blueprint token|chatroom|staking|voting|arena|credUtils|apm|chat`. They are starting points, not audited contracts. Read them before shipping.

Details: `references/token-spec.md` (message API and a correct transfer), `references/blueprints.md` (chatroom, staking, voting, CRED, tokengating), `references/bots-and-games.md` (arena framework, agent loop).

## Token essentials

| Action | Reply / effect |
|---|---|
| `Info` | `Name`, `Ticker`, `Logo`, `Denomination` |
| `Balance` (`Recipient` or `Target` optional) | `Balance`, `Ticker`, `Account`, `Data` |
| `Balances` | `Data` = JSON of all balances |
| `Transfer` (`Recipient`, `Quantity`) | sender gets `Debit-Notice`, recipient gets `Credit-Notice` (unless `Cast`); `X-*` tags forwarded; failure → `Transfer-Error` |
| `Mint` (`Quantity`) | only when `msg.From == ao.id` in the blueprint |
| `Burn` (`Quantity`) | from sender's balance |
| `Total-Supply` | `Data` = supply (rejects calls from itself) |

## Rules

1. **Balances are strings, math is `bint`.** `Quantity` arrives as a string in the token's smallest unit (`Denomination`, blueprint default 12). Never `tonumber` large quantities.
2. **Assert inputs**: `Recipient` string, `Quantity` string and `> 0`, sender balance `>=` quantity, before mutating.
3. **Authorization by `msg.From`**, never by a tag the caller controls. Decide who can `Mint` (owner, process itself, or nobody) and enforce it.
4. **React to payments via `Credit-Notice` from the token process** (`msg.From == TokenProcess`), reading `Sender` and `Quantity`. Don't trust a user's "I paid" message.
5. **State init with `X = X or default`** so reloading the blueprint keeps balances.
6. **Expose balances for UIs with `~patch@1.0`** after transfers; don't make wallets dryrun `Balance` (deprecated) or send messages to read.

## Bugs in the doc code (don't copy)

- "Building a Token" error path sends to `msg.Tags.From` (nil); use `msg.From` / `msg.reply`.
- That guide uses Lua numbers and `Denomination = 10`; the blueprint uses `bint` and 12. Use the blueprint style.
- Staking/voting blueprints use the legacy `-1` pattern return wrapped in `continue()`, unbounded loops over all stakers on every message, and `Votes[target][side]` without validating `side`. Voting reads `Stakers` (needs the staking blueprint; its doc says "token").
- Arena `endGame` divides by `Winners` before counting them.
- CRED is deprecated (legacynet reward token); `credUtils` is historical.

## Fetch the docs

```bash
python tools/docslice.py 59 44 41 60 182
python tools/docslice.py 51 188      # arena framework and game
```
