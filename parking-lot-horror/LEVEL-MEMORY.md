# Parking Lot Horror — level memory

## Current build and evidence

- 2026-10-22, revision `parking-horror-1`, title `Parking Lot Horror [1]`, native format25, ten-player design target. This target does not implement a custom lobby or enforce a player cap.
- Source: `src/build.py`, `src/parking.py`, `src/vehicles.py`, `src/monster.py`. Outputs: `dist/parking-lot-horror.level`, JSON, `src/*.gasm`, `docs/manifest.json`.
- Local native VM, schema round-trip, references/connection slot checks pass. Software previews depict actual primitive geometry; they are not screenshots of GRAB.
- GRAB Tools editor opened, but browser reported `PANIC: Browser failed to create WebGL context`; level was not imported or rendered. Quest and real multiplayer validation remain pending.

## Latest accepted rules

- User requested a separate covered Parking Lot Horror scene using Office After Hours survival mechanics, with 10 players, three immunity gems, safe hiding, five monster attacks, fog during attacks, key and escape gate after the fifth, capture to spectator.
- Preserve Office's 60 s calm followed by 60 s hunt. Hunts occur 01:00–02:00,03:00–04:00,05:00–06:00,07:00–08:00,09:00–10:00. **Exactly five:** unlike Office, no further hunts after 10:00.
- Three fixed gem mounts replace office drawer relocation: sport car, first minivan, blue SUV. Both minivans offer hiding; second minivan contains no fourth gem. This resolves the request's four potential vehicle gem mentions against the explicit total of three.
- Nine vehicles means six individually requested designs plus three crushed cars without functional doors. Capacity 60 describes marked bays, not 60 vehicles.
- One safe player per minivan (two slots total). Crouch in the rear cabin. No requirement for ten simultaneous hiding slots was supplied.
- A living key holder unlocks the gate for all survivors. Key appears on gate-side pedestal after fifth completed hunt; loss/death returns it there. Touch-based key ownership, physical held gems.
- All-dead 5 s reset retained. No global victory screen; reload after completion.

## Selected reusable patterns

- Adapted `monster.pursuer.v1`, `door.hinge.v1`, `loot.gem-and-key.v1`, `hiding.safe-slot.v1`, `atmosphere.hunt.v1`, `spectator.enclosed.v1`, `round.cooperative-hunt.v1` from Office Hunt polish4 and `docs/reuse/`.
- No office geometry or controllers changed. New native helper implementation belongs to this game's generator; documented patterns remain conventions, not a shared prefab library.
- Changed office-specific room routing to three drive aisles and two side cross-aisles; no office room indices or numeric object IDs reused.
- Corrected Office's shared remote-teleport limitation for this game: shared controllers set player intent; **only non-shared LocalMovement selects LocalId and teleports**.

## Geometry and registries

- Metres, Y up,43×59 m main garage, opaque physical roof underside 4.48 m. Six stall rows at Z[-23.75,-11.65,-6.05,6.05,11.65,23.75], ten 2.9×5.6 m stalls each. Three 6.5 m drive aisles centeredZ[-17.7,0,17.7]; side cross-aislesX±17.7. Sixteen support columns on stall back edges.
- SportCar; Minivan 1 and Minivan 2; ExplorerSUV blue; BlueStreetBike blue; RykerTrike black/gray; Wreck 1–3. Models have dashboards, seats, wheels, lamps and silhouette details built from native primitives.
- Four hinged driver doors and two sliding side doors. Native triggers/animations, reset registry. Stable named metadata in fleet registry; fresh depth-first IDs built only after hierarchy completion.
- Spawn(0,.1,-27), gate(0,0,28), north wall openingZ 29.35, escape triggerZ 29.2, isolated native finish(100,-49,0).
- Spectator gallery alongside east wall, centerX 24, floor 0, roof 3.3, Z±26. Two physical transparent window layers separate spectators from active garage. Opaque garage ceiling preserves covered scene. Elimination movement is client-local.
- Skeleton same 2.525 m height as Office,3.7 m/s versus 3.4 m/s,130 skeletal pieces with visible ribs/spine/pelvis/skull/teeth/limb bones. All actor pieces passable; AI is scripted. Attached emitter 18 puffs/s, lifetime≤1 s, so residual puffs dissipate briefly after disappearance.

## State and authority

| State | X | Y | Z | Writer |
|---|---|---|---|---|
| Clock | Hunt active0/1 | Completed hunts0..5 | Phase seconds | RoundClock |
| Round | Wipe countdown active | Seconds remaining | Round epoch | RoundClock |
| LootA/B/C | Reserved | Estimated holderId+1 | Reset epoch | Gem inventory/RoundClock |
| GemMemory1..3 | Applied epoch | Ever picked up this epoch | Reserved | Gem inventory |
| HideState1..2 | OccupantId+1 | Outside-pad edge latch | Reserved | Hide controllers/reset |
| KeyState | Available0/1 | OwnerId+1 | Spawned after fifth0/1 | Round/key controllers |
| ExitState | Unlocked | Reserved | Reserved | Exit/reset controllers |
| Target | PlayerId+1 | Player worldX | Player worldZ | MonsterAI |
| Waypoint | Route worldX | Reserved | Route worldZ | MonsterAI |

Player variables: Var 1 alive 0/dead 1/escaped 2; Var 2 local movement command(+hideId enter,-hideId exit,99 finish); Var 3 active hideId; Var 4 acknowledged hideId; Var 5 acknowledged round epoch. Zero means unowned. Ownership uses stableId+1, never selection index.

RoundClock, hides, gem/key inventory, MonsterAI and ExitController are shared; LocalFog and LocalMovement are non-shared. Final capture rechecks validity, alive status, hide, held-gem ownership and active hunt after scanning. Actual networking/host migration remain engine checks.

## Build, validation and loading

See README build commands and `docs/VALIDATION.md`. Round-trip uses vendored protobuf schema; native connection layout uses the independent exported Office fixture. Validation inspects generated instructions, not only source strings.

Official references checked2026-10-22: https://grabvr.tools/ ; https://grabvr.tools/editor ; https://grabvr.tools/gasm ; https://grabvr.quest/ . Upstream `twhlynch/GRAB-Tools/website/src/assets/proto/proto.proto` Git blob`ce8a7e7e1a98818cbf56adeabe322ee6d8ce3181` matched vendored schema. Upstream license in `vendor/GRAB-Tools-LICENSE.txt`. Numeric local filenames are not mandatory in the documented format.

## Known limits and next work

- Quest appearance/physics/collision/grabbing, native animation timing, real fog/fumes clearing, actual performance/complexity need validation. Conservatively generated complexity counts instructions and nodes and may differ from game's recalculation.
- Scalar VM assumes second-based DeltaTime, immediate connection writes and synthetic hand/physics signals. It models one local client ID at a time; non-host intent checks are not a real multiplayer session.
- Gems use native held state plus nearest living hand ownership estimate inherited from Office. Simultaneous grabbing/shared hands needs headset checks.
- Aisle routing is game-specific, not generic obstacle pathfinding; stall furniture/vehicle-body intersections require headset assessment. Skeleton is spectral/passable but still only captures eligible touching players.
- Only two single-occupant hides; minivan 2 is unstocked. Vehicle likenesses are primitive approximations. Player target 10 is design configuration, not enforced match capacity.

## Change history

-2026-10-22: Initial user-requested parallel creation: Coordinator, LevelCreator, ParkingLotCreator, VehicleCreator, MonsterCreator. Built independent game folder and registries, capped five hunts, improved local movement authority, side gallery sightlines, physical gems/native vehicle doors, detailed skeletal actor and fumes. Local tests/previews completed; engine validation pending.
