# Compose a new level from these patterns

This is a workflow and documentation template, **not a new executable configuration API**. Current Office source must be adapted/refactored to consume a new game’s parameters. Start with [the pattern catalog](README.md), [native contracts](native-contract.md) and [play model](play-model.md).

## 1. Define the game before copying components

Create a separate game folder with its own `LEVEL-MEMORY.md`, source generator, schema/license references, tests and generated output locations. Keep another game’s accepted behavior intact. Select pattern IDs and record overrides: participant target, room count, dimensions, routes, controls, hiding rules, protection, round timing, objectives and reset/win policy.

Give frequently changed values one game-specific configuration source or a clearly marked configuration section. Office still has counts/coordinates embedded throughout geometry, GASM generation and controllers. Changing only its top-level manifest is insufficient. A future config might describe `rooms`, `route`, `drawers`, `hiding_slots`, `actor`, `phases`, `objective` and `spectator`, but **those fields are a design suggestion, not implemented builder inputs**.

## 2. Compose geometry and behavior together

1. Establish units/axes, room bounds, floor/ceiling, entry and exit.
2. Instantiate named doors, desks, drawers and closets. Keep pivot/local-frame contracts and controls attached to moving parents where needed.
3. Allocate player-variable meanings and component state names. Give hiding slots unique gameplay IDs distinct from object IDs.
4. Register drawers, hiding volumes/entry/exit points, monster routes/spawns, resettable animations and spectator bounds.
5. Add loot/objective controllers, shared round authority, monster eligibility/catch guards, and per-client atmosphere/movement handlers.
6. Resolve all symbolic object references only after the hierarchy and controller inventory are final; compile native instructions and targets using fresh IDs.
7. Serialize JSON and protobuf `.level` together, round-trip the protobuf, emit human-readable GASM and a generated name-to-ID manifest.

For a three-gem relocation rule that excludes all three previous drawers, provide at least six eligible drawers or explicitly change the policy. Replace Office’s fixed 1..10 loops, +10 hiding-ID offset, map bounds and hallway waypoint logic when adapting its layout.

## 3. Validate at the right level

| Layer | Required evidence |
| --- | --- |
| Documentation-only work | Relative links resolve; current source facts match; diff contains only intended docs |
| Format/contracts | Schema parse/round-trip, unique names, full connection slot layout, valid operand destinations, fresh depth-first references and target animation names |
| Geometry | Hinge edge stationary, swing/slide clearance, inward-facing closets, moving handle parenting, loot cavity bounds, accessible inside/outside controls |
| Logic | Eligibility and final-action guards, occupancy/liveness, held vs released immunity, seated vs free gem latch, phase/relocation epochs, key loss and authorization |
| Reset | All-dead countdown, every client’s local revival, state/latch clearing, animation reset/rearming, fog restoration, full next calm period |
| Headset | Actual native animation timing, grabbing/throwing/collision, fog clear and particles, comfort/readability, non-host movement and finish, simultaneous requests |
| Multiplayer/performance | Two clients first, then target player count; late join, disconnect, host migration, shared authority, frame rate and actual game complexity |

Office build/check commands, run from repository root:

```sh
python -m pip install -r office-after-hours/requirements.txt
python office-after-hours/src/build.py
python -m unittest discover -s office-after-hours/tests -v
```

Use the analogous commands in the **new** game folder, not Office’s generator against new artifacts. `src/render.py` produces a software geometry preview, not a GRAB engine screenshot. The VM models immediate writes, second-based DeltaTime, synthetic physics/hands and animation endpoints; passing it is not a headset playtest.

## 4. Keep artifacts and evidence discoverable

Include version/title, build commands, user controls, `.level` download, schema/license origin, manifest, latest validation and engine checklist. Local `.level` basenames need not be numeric according to the older official documentation; see [filename notes](native-contract.md). A new filename can be a different local entry, and neither filename nor display title is a published server ID.

When changing a documented pattern, update its page and affected game memory. Separate a suggested future extraction from an implementation actually present in the repository. Do not claim an importable prefab/library, automatic global registry, generic pathfinding or native spectator camera unless implemented and validated.

## Game memory template

Copy and fill the following headings in the new game’s own `LEVEL-MEMORY.md`:

```md
# <Game title> — level memory

## Current build and evidence
- Revision/date, source/artifact paths, target format and player count.
- Explicit headset feedback; local checks; engine-pending behavior.

## Latest accepted rules
- Play model, phase timing, hiding/protection, death/spectator, objective/win/reset.
- Decisions that supersede older requests.

## Selected reusable patterns
- Pattern ID/version, implementation source, game-specific parameter overrides.
- Dependencies and deviations from the shared contracts.

## Geometry and registries
- Axes/units, room/route/spawn data, drawers, hiding slots, resettable clips.
- Entry/exit/spectator bounds and readable control conventions.

## State and authority
- State XYZ meanings/writers, player variables, sentinels/epochs.
- Shared versus per-client logic; local movement dispatch and reset flow.

## Build, validation and loading
- Build/tests, protobuf and ID checks, headset/multiplayer checklist.
- Output filename, internal title/version, loading steps and schema license.

## Known limits and next work
- Actual unsupported/unverified behavior, not hypothetical feature claims.

## Change history
- Date, user trigger, change, evidence and unresolved engine checks.
```
