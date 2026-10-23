# Native format, connection and hierarchy contract

**Standard:** adapt the actual schema, independent fixture and generator together. A JSON key that serializes successfully is not proof that its connection slots match the game.

Sources: [schema](../../office-after-hours/vendor/grab.proto), [generator: `G.bind`, `G.compile`, `walk`, `animation`, `attach`](../../office-after-hours/src/build.py), [independent fixture](../../office-after-hours/tests/fixtures/native_connection_layout.json), [contract tests](../../office-after-hours/tests/test_native_contract.py).

## Geometry and identity

- Distances use meters; Y is up. `Q(yaw)` in the current builder encodes a Y-axis quaternion from degrees. GASM rotation components are handled as Euler degrees by the current pattern.
- Child positions/rotations are local to their parent. Attach a moving handle trigger to its animated drawer, and particles to their actor. Parent rotation must also rotate shell parts, controls and computed world entry/exit positions.
- Keep symbolic object names unique. Complete the hierarchy first, then assign **1-based depth-first IDs**, counting each group before its children. Preallocate GASM node IDs before compiling cross-controller trigger references.
- Grouping/adding/removing a node changes subsequent IDs. Never copy a manifest’s numeric IDs into another game or revision.
- Normal object connections use type `NODE=0`; virtual player connections use `PLAYER=1`, object ID 0. Each property also carries its resolved object ID.
- Empty groups are used as scalar memory (`position.X/Y/Z`); their XYZ fields are intentionally mutable state. Do not apply geometry transforms, animate/reparent/delete them, or repurpose them as visible geometry.

## Native animations and triggers

Node `animations` and `activeAnimation` are siblings of the node payload. Idle animated objects start with `activeAnimation=-1`. Current clips have a zero-position/identity-rotation first frame and a final relative offset/rotation, speed 1, linear interpolation, non-looping trigger target.

| Contract | Value / use |
| --- | --- |
| Basic trigger sources | HAND 0, HEAD 1, GRAPPLE 2, FEET 3, BLOCK 4, SPAWN 5 |
| Target event mode | ONENTER 0, ONLEAVE 1, ONENTERONLEAVE 2, NONE 3 |
| Animation target modes | STOP 0, START 1, TOGGLE 2, TOGGLE_REVERSE 3, RESTART 4, RESET 5 |
| GASM target modes | STOP 0, START 1, TOGGLE 2, RESTART 3, RESET 4 |
| Manual door/drawer | HAND + ONENTER + animation TOGGLE_REVERSE 3 |
| Controller wake-up | Native GASM START 1; does not deliberately restart debounce working state |
| Forced controls | Empty source list, isolated position, GASM `.Trg.Force`; rearm across frames when a fresh edge is needed |
| Round geometry reset | Animation RESET 5 on all registered moving door/drawer clips |

Animation and GASM mode numbers differ: animation RESTART is 4, GASM RESTART is 3. Identify the target type before assigning mode.

**Do not write animated door/drawer transforms every frame from GASM.** That old motion path was replaced by native animation targets. GASM may read their observed transforms for open thresholds. Test actual animation/reading semantics on the target game version.

## Connection slots

Every component contains all three indices: `inputRegisterIndex`, `outputRegisterIndex`, `inoutRegisterIndex`. Unbound directions must be `-1`, not omitted/default 0. Preserve the complete slot array and order.

| Property | Slots in this implementation |
| --- | --- |
| `position` | X/Y/Z, all INOUT |
| `rotation` | X/Y/Z, all INOUT |
| `triggerActive` | Six total: 0 Active INPUT, 1 PlayerId INPUT, 2 Force INOUT; 3–5 unbound |
| `physics` | Two: 0 Enabled INOUT, 1 State INPUT |
| `playerVariables` | Five selected-player INOUT slots, Var1 through Var5 |

The fixture independently records fourteen 28-slot player properties, twenty-seven six-slot trigger properties, and four two-slot physics properties from an exported September 2026 lobby (format 24). Its source URL and SHA-256 are retained. Physics Enabled differs from an upstream helper that labelled it OUTPUT; the exported INOUT layout is the current reference. Unknown trigger slots are deliberately unbound.

### Player property: exactly 28 slots

| Slots | Names | Direction |
| --- | --- | --- |
| 0–3 | SelIndex, SelId, SelPart, Control | OUTPUT |
| 4–6 | Count, Valid, Id | INPUT |
| 7–9 | Pos.X/Y/Z | INPUT |
| 10–12 | Rot.X/Y/Z | INPUT |
| 13 | Name | INPUT |
| 14 | Col.Sel | OUTPUT |
| 15–17 | Col.R/G/B | INPUT |
| 18 | LocalId | INPUT |
| 19 | Respawn | OUTPUT |
| 20–22 | Tel.Pos.X/Y/Z | OUTPUT |
| 23 | Tel.Rot.Y | OUTPUT |
| 24 | Tel.Apply | OUTPUT |
| 25–27 | Vel.X/Y/Z | INOUT |

Select by index while scanning, but store stable selected `Player.Id + 1` for ownership; zero means unowned. Validate selection before actions. `SelPart` is 0 head, 1 body, 2 feet, 3 left hand, 4 right hand in the documented interface. Normal actor scans select head; gem proximity scans select hands.

**Teleport applies to the selected local player only**, and its target is feet position. Each client should select `Player.LocalId` for its own movement. Office’s shared `OfficeXX` controllers still contain hiding teleport calls; remote hiding movement is not a verified generic solution. Revision 5 removes ExitController teleport calls and uses a reachable native finish behind the exit door. For a future game, design a shared intent plus local movement handler rather than copying those calls as proven multiplayer behavior. Local spectator/revival already follows the local-player pattern; engine testing is still pending.

## GASM execution and authority

- Current generated blocks are `startActive=True`. `LocalFog` and `LocalSpectator` use `isShared=False`; other current controllers use `isShared=True`.
- Shared-state intent and a single phase authority must be preserved. Actual shared execution/host migration behavior remains an engine check; do not assume networking was simulated.
- Operand types used: INPUT 0, OUTPUT 1, WORKING 2, SPECIAL 3, CONSTANT 4, LABEL 5, INOUT 7. Labels are compiled from symbolic names. Eight working registers are used (`R0`–`R7`); R7 is routinely temporary.
- The builder maps `DeltaTime` to special register index 4; the harness treats it as seconds. `SLEEP 0` yields one frame. Nonzero SLEEP is modeled in milliseconds by the harness.
- The harness caps a block at 500 instructions per frame. Long player scans can span frames, so recheck status, protection and phase immediately before a kill or other irreversible gameplay transition.
- `.gasm` text, `.json`, `.level` and manifest are generated outputs. Build source is authoritative; regenerate together when changing gameplay.

## Local files, editor title and published IDs

The official [GRAB level-format README](https://github.com/Slin/GRAB-Level-Format) documents user files under `levels/user`, a required `.level` extension and an arbitrary unique basename. Timestamps are the default collision-avoidance convention; numeric names are **not documented as mandatory**. GRAB Tools export defaults to a Unix-seconds name; that is separate from the title inside the file and from a published server level ID/version.

`office-after-hours.level` is valid according to that documented local-file contract. The official README is older in other format details; the current closed-source headset loader was not tested during the filename research. Keep an existing chosen filename when replacing the same local entry; a new name can create a separate entry. Use the game’s [loading notes](../../office-after-hours/README.md) for paths and transfer details.
