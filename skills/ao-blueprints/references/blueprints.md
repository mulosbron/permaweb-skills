# Other blueprints

Source docs: 182 (Chatroom), 191 (Building a Chatroom), 58 (Tokengating), 41 (Staking), 60 (Voting), 42 (CRED Utils), 232.

## Chatroom

State `Members = Members or {}`.

- `Register` (`Action = "Register"`): add `msg.From` to `Members`, reply confirmation.
- `Broadcast` (`Action = "Broadcast"`): send `msg.Data` to every member.

Hardening: dedupe registrations, cap message size, rate-limit per sender, let members `Unregister`. Broadcasting is one outbound message per member per post; large rooms get expensive.

## Tokengating

Replace the Broadcast handler so it only broadcasts when `Balances[msg.From]` (in the same process, if it is also the token) or a cached balance from the token process is positive. If the token lives in another process, keep a local `Holders` table updated from `Credit-Notice`/`Debit-Notice` or a balance query, never from the sender's claim.

## Staking (needs token state: `Balances`)

- `Stake` (`Quantity`, `UnstakeDelay`): move from `Balances` to `Stakers[from] = { amount, unstake_at = height + delay }`.
- `Unstake` (`Quantity`): move to `Unstaking[from] = { amount, release_at }`.
- `finalize`: runs on **every** message (pattern returns `-1`), releasing matured unstakes by `Block-Height`.

Caveats: `tonumber` math (use `bint`), `UnstakeDelay` chosen by the caller, a second `Unstake` overwrites the first pending entry, O(n) loop on every message.

## Voting (needs `Stakers` from staking)

- `Vote` (`Target`, `Side` = `yay`|`nay`, `Deadline` in blocks): adds the caller's staked amount to `Votes[target][side]`.
- `finalize` per message: past-deadline targets with `yay > nay` reach a placeholder `print("Handle Vote")`, then the record is cleared.

Caveats: no double-vote protection, `Side` not validated, staked amount counted at vote time only.

## CRED utils (deprecated)

CRED was the legacynet developer reward token; no longer earnable or redeemable. The blueprint shows a metatable pattern (`CRED.balance`, `CRED.send(target, amount)`, `CRED.update`) and notice handlers filtered by `msg.From == CRED_PROCESS`, which is the right way to trust token notices.

## Using any blueprint

```lua
.load-blueprint token
Handlers.list            -- confirm names, then customize by re-adding handlers with the same name
```

Re-adding a handler name replaces it; load your overrides after the blueprint.
