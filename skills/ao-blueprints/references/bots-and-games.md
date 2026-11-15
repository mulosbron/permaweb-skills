# Arena games and autonomous agents

Source docs: 51 (Mechanics of the Arena, full blueprint), 188 (Expanding the Arena: ao-effect), 55 (Let's Play), 190, 189, 54, 50, 52, 53.

## Arena framework (`.load-blueprint arena`)

Game loop: `Not-Started → Waiting → Playing → (winner or timeout) → Waiting …`, driven by a catch-all handler that sets `Now = msg.Timestamp` on every message (cron ticks keep it moving).

| Global | Meaning |
|---|---|
| `WaitTime` / `GameTime` | 2 min / 20 min (ms) |
| `PaymentToken`, `PaymentQty`, `BonusQty` | entry fee token and amounts (strings) |
| `Waiting[addr] = paid?`, `Players[addr] = state`, `Listeners` | lobby, active players, announcement subscribers |
| `MinimumPlayers` | 2 |
| `playerInitState()`, `onTick()` | hooks your game defines |

Handlers: `Register` (`Mode = "Listen"` to only spectate), `Unregister`, payment via `Credit-Notice` from `PaymentToken` with `Quantity >= PaymentQty`, `GetGameState` (JSON `{ GameMode, TimeRemaining, Players }`), `Tick`, `AddBet` (`Reason = "AddBet"`), `RequestTokens` (faucet).

Functions to call from game logic: `eliminatePlayer(eliminated, eliminator)` (pays eliminator the deposit), `announce(event, text)`, `sendReward(to, qty, reason)`, `endGame()` (splits `BonusQty` among survivors plus refunds deposits).

## ao-effect game on top

40×40 wrapping grid, health 100, energy +1/s up to 100. `PlayerMove` (`Direction`: Up, Down, Left, Right, UpRight, UpLeft, DownRight, DownLeft; case-sensitive), `PlayerAttack` (`AttackEnergy`), damage random up to `2 × energy / 3` to everyone within range; targets get `Hit`, attacker `Successful-Hit`.

## Agent (bot) loop

```lua
LatestGameState = LatestGameState or nil
Handlers.add("HandleAnnouncements", { Action = "Announcement" }, function(msg)
  ao.send({ Target = Game, Action = "GetGameState" })
end)
Handlers.add("UpdateGameState", { Action = "GameState" }, function(msg)
  LatestGameState = require("json").decode(msg.Data)
  ao.send({ Target = ao.id, Action = "UpdatedGameState" })
end)
Handlers.add("decideNextAction", { Action = "UpdatedGameState" }, function()
  if LatestGameState.GameMode ~= "Playing" then return end
  decideNextAction()   -- attack if someone in range and energy > 5, else move
end)
Handlers.add("ReturnAttack", { Action = "Hit" }, function(msg) --[[ counterattack with current energy ]] end)
```

Pattern: event → request state → store → self-message → decide. It costs one message per step; on HyperBEAM a bot can instead GET the game's patched state over HTTP and only send moves.

## Doc bugs

- `endGame` computes `BonusQty / Winners` before counting winners (division by zero, then recomputed).
- `sendReward` checks `type(qty) ~= number` (unquoted `number` is a nil global), so it always converts; harmless but wrong.
- `undefined` in the code is just a nil global.
