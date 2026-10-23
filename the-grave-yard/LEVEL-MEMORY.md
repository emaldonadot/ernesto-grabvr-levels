# The Grave Yard — level memory

## Current build and evidence

Revision `grave-yard-3`, 2026-10-23. Native format 25; ten-player design target. Source `src/build.py`, environment `src/environment.py`, zombie `src/zombie.py`; outputs `dist/the-grave-yard.json`, `dist/the-grave-yard.level`, controller `src/*.gasm` and `docs/manifest.json`.

31 local reference/layout/native-contract/bytecode tests passed. No Quest playtest is recorded. Browser editor initialization failed before import because WebGL context creation was unavailable. See [validation](docs/VALIDATION.md) and [Quest checklist](docs/QUEST-PLAYTEST.md).

## Latest accepted rules

- Fenced 4 × 4 graveyard with walk lanes, scary climbable trees, four lit pumpkins, full moon/clouds, three candles and famous-monster epitaphs.
- Ten-player cooperative survival; 60-second rest followed by 60-second zombie hunt, exactly five hunts. Zombie stops after hunt five.
- **Only holding one of three physical tree gems grants immunity. Climbing alone never grants immunity.** Zombie eligibility ignores legacy hiding/tree variables.
- Zombie speed 4.1 m/s; decayed exposed skull/arm/femur, reaching arms, shamble animation and green odor particles. Ground navigation detours around marker/trunk rectangles with 0.38 m clearance.
- Captured players spectate; survivors continue. Five-second all-dead wipe resets phases, props, gate, statuses and each client's local position. Living or escaped participants prevent wipe.
- Golden skull appears after the fifth hunt. A living player's held-then-released skull inside the pedestal socket opens the gate for survivors. Holding it nearby is insufficient. Lost skull recovers.
- Players enter an enclosed chamber and touch the native finish. Reload the level for a fresh game after successful completion; no automatic post-win replay is implemented.

## Selected reusable patterns

Adapted the parking/office native builder and contracts for monster pursuit, physical loot, native animated gate, local hunt fog, enclosed spectators and cooperative round/wipe. New environment has no hiding slots. Golden skull physics placement replaces the prior inventory key. All teleport writes are in non-shared `LocalMovement`.

References: [reuse index](../docs/reuse/README.md), [native contract](../docs/reuse/native-contract.md), [play model](../docs/reuse/play-model.md), [composition](../docs/reuse/new-level.md). Native schema and upstream license are retained under `vendor/`.

## Geometry and registries

Metres, Y up. Yard X ±24, Z ±28; 8m solid nongrabbable/nongrapplable perimeter, sealed gate header from Y=3.5..8m and a transparent collision cap at Y=8m (underside 7.9m), above all tree branches/twigs (~5m). Front wall/post/header geometry overlaps and the roofed exit has no route over the gate. The cap preserves sky visibility while catching high launches. Spawn near (0,0,-23), gate Z=-28, enclosed exit to Z=-36, native finish (0,1.2,-34). Spectator corridor centered X=28. Open grave is grave 14 at (3.5,10.5); zombie resting origin (3.5,-1.1,10.5). Skull initially (0,1.6,17), socket (4,2.15,-24), acceptance tolerance 0.42 m on each axis.

Six tree positions and all marker/trunk obstacles are in environment's returned layout and the generated manifest. Three gems start at a branch mount X offset -1.2 m, Y=4.1 m, outside trunks. Fresh depth-first IDs are resolved only after hierarchy/controller assembly; never reuse manifest IDs across builds.

## State and authority

| State | X | Y | Z |
| --- | --- | --- | --- |
| Clock | Hunt 0/1 | Completed hunts | Phase seconds |
| Round | Wipe 0/1 | Countdown seconds | Epoch, initially 1 |
| LootA/B/C | Reserved | Held player ID + 1, zero none | Reset epoch |
| GemMemory1..3 | Applied epoch | Pickup latch | Reserved |
| SkullState | Available | Last living holder ID + 1 | Pickup latch |
| ExitState | Unlocked | Reserved | Reserved |
| Target | Player ID + 1 | World target X | World target Z |

Player Var1: 0 alive, 1 dead, 2 escaped. Var2–4 reserved/cleared; Var5 client's acknowledged round epoch. Shared RoundClock owns phases/reset; three gem inventories own held estimates; SkullInventory validates physical release; MonsterAI owns pursuit/capture; ExitController exposes finish and records escape. Non-shared LocalFog applies ambience; non-shared LocalMovement selects `Player.LocalId` for spectator/revival. Navigation scratch nodes and zombie state remain private to monster/nav controllers.

## Build, validation and loading

```sh
python -m pip install -r the-grave-yard/requirements.txt
python the-grave-yard/src/build.py
python -m unittest discover -s the-grave-yard/tests -v
```

Copy `dist/the-grave-yard.level` to GRAB `levels/user` on Quest. Preserve extension; JSON/specification are not the import binary. Generated build has 343 nodes, eleven controllers and declared complexity 5679; actual engine complexity and performance await headset testing.

## Known limits and next work

Native physics/animation, grip handoff, networking, late join, host migration, actual completion and ten-player performance remain engine-pending. Capture requires head height -0.2..3 m: higher climbers remain targets but cannot be captured while out of physical reach. This is reach gating, with no climbing immunity state. Seek feedback on high-branch gameplay. Navigation tests cover a representative detour, not every possible full-map path. The software preview is geometry visualization, not a GRAB screenshot.

## Change history

- 2026-10-22: Preserved latest gem-only immunity and multiplayer rules; independent native gameplay, environment, zombie and QA agents integrated the prior specification/reference model into native artifacts. 22 local tests passed; Quest checks pending.

## 2026-10-23 — exit guidance and containment revision 2

Ernesto requested visible exit instructions like Office, plus taller perimeter barriers so kids cannot climb/launch out and fall. The yard's original fence was only 2.9m tall beneath ~5m tree twigs. Fence slabs now reach 8m; sides/back overlap at corners, the front posts seal the gate edges, and a full header seals the gap above the closed gate. All containment slabs explicitly disable grabbing, grappling and pass-through. A very faint transparent collision cap closes the top at 8m without covering the moon with an opaque roof. The six trees remain climbable and their gem mounts remain at 4.1m. Actual Quest collision/launch behavior still requires headset checks.

The physical golden-skull objective is unchanged: after hunt five, a living player must hold then release the skull in the socket. Four mutually exclusive signs at the inside face of the gate explain locked, skull ready, skull picked up/release required, and gate open/walk to green finish states. A gold passable ring marks the acceptance height at (4,2.15,-24); the skull spawn pedestal is labeled. Passable green floor lights lead from socket to gate and through the supported chamber to the native finish at (0,1.2,-34). Gate instructions at Z=-27.6 sit inside the front wall (inner face Z=-27.8), so the taller wall/header does not cover them.

Exit bookkeeping now also requires head distance <=1m to the native finish center, instead of marking escaped anywhere in the larger HEAD trigger box. No finish teleports were added. Seven new local tests cover continuous sampled perimeter/header coverage, tree clearance, solid transparent cap and corner overlap, staged instructions through actual physical release and two-player walk-to-finish, proximity rejection, reset guidance, and non-obstructing socket/path lights. Total: 29 passing checks; binary round-trip passes. Title: The Grave Yard [2].

## 2026-10-23 — spectator view 3

The 8m opaque east perimeter blocked the adjacent spectator gallery. The entire east wall is now a faint transparent collision slab (alpha 0.025); both long gallery walls use the same low-alpha transparency. All three remain solid, nongrabbable and nongrapplable. Wall height, sealed corners/header/cap, gallery position, local death/revival movement and exit rules remain unchanged. Spectators can walk the 52m gallery to follow survivors through the east viewing wall; ordinary trees and gravestones can still occlude individual sightlines.

31 local tests pass, including full-length transparent-wall coverage and a remote-client death that leaves the surviving player unchanged. Transparency rendering and actual visibility on Quest remain unverified. Title: The Grave Yard [Spectator view 3].
