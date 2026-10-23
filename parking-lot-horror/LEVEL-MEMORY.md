# Parking Lot Horror — level memory

## Current build and evidence

- 2026-10-23, revision `parking-horror-3`, title `Parking Lot Horror [Exit guidance 3]`, native format25, ten-player design target. This target does not implement a custom lobby or enforce a player cap.
- Source: `src/build.py`, `src/parking.py`, `src/vehicles.py`, `src/monster.py`, `src/navigation.py`. Outputs: `dist/parking-lot-horror.level`, JSON, `src/*.gasm`, `docs/manifest.json`.
- 31 local native VM, schema round-trip, references/connection slot checks pass. Revision-3 build: 816 nodes, 12 native controllers, conservative complexity estimate 7114 (increased obstacle checks; actual engine cost and Quest performance pending). Software previews depict actual primitive geometry; they are not screenshots of GRAB.
- Headset feedback on build 1: Ernesto said the overall scene looks great, and reported aisle-limited monster pursuit, a falling exit hole, and stationary glass when opening car doors. Revision 2 addresses those reports; fixes are locally checked and await headset retest.
- GRAB Tools editor opened, but browser reported `PANIC: Browser failed to create WebGL context`; level was not imported or rendered. Quest and real multiplayer validation remain pending.

## Latest accepted rules

- User requested a separate covered Parking Lot Horror scene using Office After Hours survival mechanics, with 10 players, three immunity gems, safe hiding, five monster attacks, fog during attacks, key and escape gate after the fifth, capture to spectator.
- Preserve Office's 60 s calm followed by 60 s hunt. Hunts occur 01:00–02:00,03:00–04:00,05:00–06:00,07:00–08:00,09:00–10:00. **Exactly five:** unlike Office, no further hunts after 10:00.
- Three fixed gem mounts replace office drawer relocation: sport car, first minivan, blue SUV. Both minivans offer hiding; second minivan contains no fourth gem. This resolves the request's four potential vehicle gem mentions against the explicit total of three.
- Nine vehicles means six individually requested designs plus three crushed cars without functional doors. Capacity 60 describes marked bays, not 60 vehicles.
- One safe player per minivan (two slots total). Crouch in the rear cabin. No requirement for ten simultaneous hiding slots was supplied.
- A living key holder unlocks the gate for all survivors. The exit is an enclosed floor-supported room attached to the north opening. Players walk to the native finish block inside; completion no longer teleports them off-map. Key appears on gate-side pedestal after fifth completed hunt; loss/death returns it there. Touch-based key ownership, physical held gems.
- All-dead 5 s reset retained. No global victory screen; reload after completion.

## Selected reusable patterns

- Adapted `monster.pursuer.v1`, `door.hinge.v1`, `loot.gem-and-key.v1`, `hiding.safe-slot.v1`, `atmosphere.hunt.v1`, `spectator.enclosed.v1`, `round.cooperative-hunt.v1` from Office Hunt polish4 and `docs/reuse/`.
- No office geometry or controllers changed. New native helper implementation belongs to this game's generator; documented patterns remain conventions, not a shared prefab library.
- Revision 2 replaces aisle-only routes with obstacle-aware ground navigation across empty stalls. Vehicle bodies, conservative door sweep bounds and structural columns block movement and capture lines. No office room indices or numeric object IDs are reused.
- Corrected Office's shared remote-teleport limitation for this game: shared controllers set player intent; **only non-shared LocalMovement selects LocalId and teleports**.

## Geometry and registries

- Metres, Y up,43×59 m main garage, opaque physical roof underside 4.48 m. Six stall rows at Z[-23.75,-11.65,-6.05,6.05,11.65,23.75], ten 2.9×5.6 m stalls each. Three 6.5 m drive aisles centeredZ[-17.7,0,17.7]; side cross-aislesX±17.7. Sixteen support columns on stall back edges.
- SportCar; Minivan 1 and Minivan 2; ExplorerSUV blue; BlueStreetBike blue; RykerTrike black/gray; Wreck 1–3. Models have dashboards, seats, wheels, lamps and silhouette details built from native primitives.
- Four hinged driver doors and two sliding side doors. Glass, frame, real handle and driver mirror are children of the animated door assembly; fixed duplicate van glass was removed. Native triggers/animations, reset registry. Stable named metadata in fleet registry; fresh depth-first IDs built only after hierarchy completion.
- Spawn(0,.1,-27), gate at the north wall opening (0,0,29.35), enclosed exit room floor spanning Z 27.8..37.6, walls X ±3.15 and back Z 37.45, native finish (0,1.2,35). The finish is hidden below the map until authorized unlock, then remains inside the room. Escape bookkeeping checks actual distance ≤1 m to the finish; it does not teleport or replace native game completion.
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
| Waypoint | Route world X | Reserved | Route world Z | MonsterAI |
| NavA | First detour X | First detour Z | Active detour phase | MonsterAI |
| NavB | Second detour X | Second detour Z | Planned target Id+1 | MonsterAI |
| NavC | Proposed step X | Proposed step Z | Last movement time | MonsterAI |
| NavTime | Elapsed seconds | Reserved | Reserved | NavClock |
| NavRect/2/3 | Selected obstacle bounds and planning scratch | Planning scratch | Planning scratch | MonsterAI |

Player variables: Var 1 alive 0/dead 1/escaped 2; Var 2 local movement command(+hideId enter,-hideId exit,reserved); Var 3 active hideId; Var 4 acknowledged hideId; Var 5 acknowledged round epoch. Zero means unowned. Ownership uses stableId+1, never selection index.

RoundClock, hides, gem/key inventory, MonsterAI, NavClock and ExitController are shared; LocalFog and LocalMovement are non-shared. Final capture rechecks validity, alive status, hide, held-gem ownership and active hunt after scanning. The small shared NavClock accumulates elapsed time so route evaluation across native instruction slices does not treat each slice as a full new movement interval. Every proposed ground step is swept against inflated conservative blockers (0.38 m clearance), and capture additionally rejects vehicle interiors/roofs and obstructed sightlines. Actual networking/host migration remain engine checks.

## Build, validation and loading

See README build commands and `docs/VALIDATION.md`. Round-trip uses vendored protobuf schema; native connection layout uses the independent exported Office fixture. Validation inspects generated instructions, not only source strings.

Official references checked2026-10-22: https://grabvr.tools/ ; https://grabvr.tools/editor ; https://grabvr.tools/gasm ; https://grabvr.quest/ . Upstream `twhlynch/GRAB-Tools/website/src/assets/proto/proto.proto` Git blob`ce8a7e7e1a98818cbf56adeabe322ee6d8ce3181` matched vendored schema. Upstream license in `vendor/GRAB-Tools-LICENSE.txt`. Numeric local filenames are not mandatory in the documented format.

## Known limits and next work

- Quest appearance/physics/collision/grabbing, native animation timing, real fog/fumes clearing, actual performance/complexity need validation. Conservatively generated complexity counts instructions and nodes and may differ from game's recalculation.
- Scalar VM assumes second-based DeltaTime, immediate connection writes and synthetic hand/physics signals. It models one local client ID at a time; non-host intent checks are not a real multiplayer session.
- Gems use native held state plus nearest living hand ownership estimate inherited from Office. Simultaneous grabbing/shared hands needs headset checks.
- Navigation uses conservative 2D ground blockers, including maximum door sweeps, rather than full engine collision meshes. It can give cars extra clearance even with closed doors. Native animation/collision timing and ground chase appearance require headset assessment. Skeleton visual pieces remain passable; native GASM enforces its ground obstacle and capture guards.
- Only two single-occupant hides; minivan 2 is unstocked. Vehicle likenesses are primitive approximations. Player target 10 is design configuration, not enforced match capacity.

## Change history

-2026-10-22: Initial user-requested parallel creation: Coordinator, LevelCreator, ParkingLotCreator, VehicleCreator, MonsterCreator. Built independent game folder and registries, capped five hunts, improved local movement authority, side gallery sightlines, physical gems/native vehicle doors, detailed skeletal actor and fumes. Local tests/previews completed; engine validation pending.

- 2026-10-22, revision 2: Added free-direction obstacle-aware ground pursuit, vehicle/column collision and capture guards, animated window/frame/handle assemblies, and a continuous enclosed native-finish room. Gate moved into the actual north wall opening. Regenerated all gameplay artifacts, tests and previews.

- 2026-10-23, exit guidance 3: Added a neon gold lock parented to the lifting gate, instructions beside the key pedestal, inventory pickup feedback at the gate, and EXIT OPEN instructions. A living inventory key holder can unlock after hunt five by touching the lock or approaching the doorway (head X +/-2.3m, Z 27.7..29.35m, Y 0..3.2m). Non-owners, dead players and early unlocks remain rejected. Touching the key is inventory pickup; its visual floats 0.5m above the carrier’s head. Four passable green floor strips lead into the enclosed room to native finish (0,1.2,35). Finish placement, no-teleport completion and cooperative unlock remain unchanged. Stage signs reset with the round. Four new serialized-GASM/geometry regressions cover pickup, approach/touch and unauthorized paths, two survivors finishing, reset/reopen, lock parenting/trigger alignment and supported path markers. All 31 local tests pass; real headset completion/readability remains pending.
