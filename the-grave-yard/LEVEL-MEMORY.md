# The Grave Yard — level memory

## Current build and evidence

Revision `grave-yard-1`, 2026-10-22. Native format 25; ten-player design target. Source `src/build.py`, environment `src/environment.py`, zombie `src/zombie.py`; outputs `dist/the-grave-yard.json`, `dist/the-grave-yard.level`, controller `src/*.gasm` and `docs/manifest.json`.

22 local reference/layout/native-contract/bytecode tests passed. No Quest playtest is recorded. Browser editor initialization failed before import because WebGL context creation was unavailable. See [validation](docs/VALIDATION.md) and [Quest checklist](docs/QUEST-PLAYTEST.md).

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

Metres, Y up. Yard X ±24, Z ±28; spawn near (0,0,-23), gate Z=-28, enclosed exit to Z=-36, native finish (0,1.2,-34). Spectator corridor centered X=28. Open grave is grave 14 at (3.5,10.5); zombie resting origin (3.5,-1.1,10.5). Skull initially (0,1.6,17), socket (4,2.15,-24), acceptance tolerance 0.42 m on each axis.

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

Copy `dist/the-grave-yard.level` to GRAB `levels/user` on Quest. Preserve extension; JSON/specification are not the import binary. Generated build has 326 nodes, ten controllers and declared complexity 5598; actual engine complexity and performance await headset testing.

## Known limits and next work

Native physics/animation, grip handoff, networking, late join, host migration, actual completion and ten-player performance remain engine-pending. Capture requires head height -0.2..3 m: higher climbers remain targets but cannot be captured while out of physical reach. This is reach gating, with no climbing immunity state. Seek feedback on high-branch gameplay. Navigation tests cover a representative detour, not every possible full-map path. The software preview is geometry visualization, not a GRAB screenshot.

## Change history

- 2026-10-22: Preserved latest gem-only immunity and multiplayer rules; independent native gameplay, environment, zombie and QA agents integrated the prior specification/reference model into native artifacts. 22 local tests passed; Quest checks pending.
