# Reusable GRAB level patterns

A small reference library for ChatGPT and human level authors. **These are documented patterns from the current procedural generator, not prebuilt prefabs, an importable API, or an extracted shared runtime.** Reuse currently means adapting generator code, symbolic names, state and tests together.

Documentation version: **1.0**, 2026-10-22. Implementation baseline: Office After Hours **Hunt polish 4**, commit `c082e9b94d0151fe98a2f5a14f8a73ae11a80b7f`, format 25. Future game defaults may differ.

## Start here

1. Read the target game’s `LEVEL-MEMORY.md` for its latest rules.
2. Choose components from the table below; load only those pages into context.
3. Read [native contracts](native-contract.md) before changing serialization, connections, animations or hierarchy.
4. Use [play model and state](play-model.md) to connect components without state collisions.
5. Follow [new-level composition](new-level.md) to build and validate another game.

| Pattern ID | Read for | Main dependencies |
| --- | --- | --- |
| `monster.pursuer.v1` | [Monster, chase, facing, fumes](components/monster.md) | Round phase, player status, hiding, gem holders, route graph, doors |
| `door.hinge.v1` | [Doors, native animations, gated exit](components/doors.md) | Named animation, hand/forced trigger, reset registry |
| `lighting.office.v1` | [Lights, signs, ambiance](components/lighting.md) | Static materials; optional native light schema |
| `desk.drawer.v1` | [Desk, chair, moving drawer](components/desk.md) | Native slide, attached handle trigger, loot, hiding |
| `closet.hide.v1` | [Closet, orientation, door controls](components/closet.md) | Local hierarchy, hinge, hiding occupancy |
| `loot.gem-and-key.v1` | [Physical gems and inventory key](components/loot.md) | Drawer registry, physics contract, round/relocation epochs |
| `hiding.safe-slot.v1` | [Single-occupant safe hiding](components/hiding.md) | Player status, occupancy, entry/leave controls, AI guard |
| `atmosphere.hunt.v1` | [Fog lifecycle](components/atmosphere.md) | Shared phase, per-client controller, native ambience targets |
| `spectator.enclosed.v1` | [Death, spectator area, markers](components/spectator.md) | Player status, local teleport, round epoch |
| `round.cooperative-hunt.v1` | [Game mechanics and play model](play-model.md) | Component state registry, reset registry, win condition |

IDs identify **documentation patterns**, not object IDs or an implemented loader. Use a new version when changing a pattern’s external state/behavior contract; note game-specific parameter overrides in that game’s memory.

## Evidence labels

| Label | Meaning in this library |
| --- | --- |
| **Standard** | Repository convention recommended for new work; not necessarily enforced by code |
| **Office default** | Actual current Office After Hours value or behavior |
| **Headset feedback** | Ernesto explicitly reported behavior in GRAB |
| **Local checked** | Serialized-data/bytecode/endpoint test coverage; not native physics or rendering |
| **Engine pending** | Requires current GRAB/Quest validation, especially multiple clients |

Explicit headset feedback confirms office doors and solo monster pursuit, and that the scene looks good. Reports also identified persistent fog and falling drawer gems. **The Hunt polish 4 fixes, particles, grip transitions and multiplayer behavior have not been confirmed on a headset.** Current local baseline reports 35 checks; see [game validation](../../office-after-hours/docs/VALIDATION.md) and [Quest checklist](../../office-after-hours/docs/QUEST-PLAYTEST.md).

## Source of truth

- [Generator](../../office-after-hours/src/build.py): geometry, helpers, GASM, connections, trigger targets and serialization.
- [Native schema](../../office-after-hours/vendor/grab.proto): supported serialized node/field definitions; include its upstream license when reusing it.
- [Independent native connection fixture](../../office-after-hours/tests/fixtures/native_connection_layout.json): exported-layout evidence and source hash.
- [Native contract tests](../../office-after-hours/tests/test_native_contract.py), [hunt tests](../../office-after-hours/tests/test_hunt_polish.py), [play-model tests](../../office-after-hours/tests/test_playtest_fixes.py), [gameplay tests](../../office-after-hours/tests/test_gameplay.py).
- [Generated manifest](../../office-after-hours/docs/manifest.json): this build’s name-to-ID map and counts, **not stable reusable IDs**.
- [Game memory](../../office-after-hours/LEVEL-MEMORY.md): game-specific decisions and historical changes. Latest decisions override older release notes.

A future extracted library should preserve these contracts behind parameterized builders. That extraction has not been performed by this documentation task.
