# Cooperative hunt play model and state ownership

Pattern `round.cooperative-hunt.v1`. Sources: [generator](../../office-after-hours/src/build.py), [RoundClock](../../office-after-hours/src/RoundClock.gasm), [game memory](../../office-after-hours/LEVEL-MEMORY.md), [timing/reset tests](../../office-after-hours/tests/test_playtest_fixes.py).

## Office rules: configurable defaults

Ten players search ten offices with three gems and twenty individual hiding slots. The game starts on load, without ready-up. Calm lasts 60s; hunt lasts 60s, repeating. The monster randomly spawns at a hall end, but **timing is fixed**, not random. Holding a gem or active hiding prevents pursuit/catch. Dead players spectate; living survivors cooperate to escape.

First hunt is 01:00–02:00. Fifth is 09:00–10:00. The key appears after the **end** of that fifth hunt; hunts continue afterward. Key ownership unlocks the exit for all survivors. Current completion marks each living crossing player escaped and attempts teleport to the isolated native finish. No global victory/replay screen or automatic restart after a completed escape round exists; reload after that result.

### Full-death reset

Every valid connected player must have dead status for a wipe. An empty lobby, one surviving player or an escaped player does not trigger it. Once triggered:

1. Set hunt inactive, hide the monster, clear target and show a 5 → 1 countdown in the spectator area.
2. After five seconds, increment the round epoch and revive statuses.
3. Clear phase elapsed/completed hunts, key, exit lock, hiding occupancy and trigger latches. Reset native office/closet/exit door and drawer clips. Rearm exit forcing.
4. Relocate/revoke gems and return to a full calm phase.
5. Every client acknowledges the epoch and teleports its own player into the hall.

The counter does not cancel because a new player arrives after a countdown started. Late join, host migration and reconnect identity still need engine tests. Record a different policy explicitly in another game.

## State registry

Standardize meaning and writers before composing components. These positions are mutable scalar memory, not physical world coordinates. The names below are Office conventions; do not bind another game to them without a mapping.

| State | X | Y | Z | Main writer(s) |
| --- | --- | --- | --- | --- |
| Clock | Hunt 0/1 | Completed hunts | Phase seconds | RoundClock |
| Round | Wipe countdown active | Seconds remaining | Round epoch, initially 1 | RoundClock |
| Room{i} | Observed door yaw >45° | Drawer extension >0.35m | Reserved | Office{i} |
| Spots{i} | Closet owner ID+1 | Desk owner ID+1 | Reserved | Office{i}; reset authority clears |
| Edge{i} | Reserved | Reserved | LootUse latch | Office{i}; reset authority clears |
| EdgeB{i} | ClosetUse latch | DeskUse latch | Reserved | Office{i}; reset authority clears |
| LootA/B/C | Assigned drawer | Estimated holder ID+1 | Relocation epoch | RoundClock assigns/epochs; gem controller holds |
| GemMemory{i} | Applied relocation epoch | Picked up this epoch 0/1 | Reserved | Gem controller |
| KeyState | Drawer, or 0 when held | Owner ID+1 | Last drawer; 0 never spawned | RoundClock spawns/resets; Office claims; KeyInventory recovers |
| Target | Chosen player ID+1 | Target world X | Target world Z | MonsterAI |
| Waypoint | Route world X | Reserved | Route world Z | MonsterAI |
| ExitState | Unlocked 0/1 | Reserved | Reserved | ExitController; RoundClock resets |

| Selected-player variable | Meaning |
| --- | --- |
| Var1 | 0 living, 1 dead, 2 escaped |
| Var2 | Unused/reserved |
| Var3 | Active hiding ID; zero none, 1..10 closets, 11..20 desks |
| Var4 | Reserved/cleared legacy slot; must not make observed hiding vulnerable |
| Var5 | Last round epoch acknowledged by that client/player |

Store ownership by `Player.Id+1` rather than selection index; zero is the unowned sentinel. Marker display slots intentionally enumerate current player indices. Sharing one variable namespace across games requires an explicit mapping; do not silently assign a new ability to Var3 or Var5.

## Controller ownership and dependencies

| Controller | Intent | Important dependencies |
| --- | --- | --- |
| RoundClock, shared | Phase/reset authority and gem/key spawning | Player statuses, reset-animation registry, valid drawer set |
| OfficeXX, shared | Occupancy, entry/leave, key claims, observed open state | Native controls, selected player, room geometry |
| Gem1..3Inventory, shared | Seat/free latch, physical holder estimate, recovery | Physics, hands, drawers, loot epochs |
| KeyInventory, shared | Key visual and owner-loss recovery | Key state, selected player, drawers |
| MonsterAI, shared | Eligibility, route, facing, death guard | Phase, status, hiding, gem holders, doors |
| ExitController, shared | Key authorization and completion attempt | Key holder, status, exit/escape triggers |
| LocalFog, non-shared | This client’s phase ambience | Shared Clock and local ambience triggers |
| LocalSpectator, non-shared | This client’s spectator/round movement | LocalId, status, round epoch/Var5 |
| DeadMarker00..15, shared | Per-index dead display | Selected status/head position |

These flags describe the emitted blocks, not a claim that networking/host migration is verified. Shared Office/Exit teleports have a known local-only interface limitation; use [the native movement guidance](native-contract.md) for new games.

## Parameterization standard

For a new game, declare participant target, room/route topology, safe-slot registry, loot capacity, phase durations, monster speed/catch policy, objective unlock time, wipe/win conditions, spectators and reset behavior in one game-specific configuration or clearly marked configuration section. Current Office parameters are still spread through `build.py`; no config loader has been extracted. Select components, map their state and supply those parameters before generating nodes.
