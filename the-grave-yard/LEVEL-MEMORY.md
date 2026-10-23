# The Grave Yard — project memory
Date: 2026-10-22. Status: specification committed; native build and Quest testing pending.

## Requirements
- Fenced graveyard with 4 x 4 graves, clear walkable paths, spawn and gate exit.
- Climbable scary trees, four illuminated jack-o'-lanterns, full moon, clouds, three grave candles, famous monster epitaphs.
- Decaying zombie with exposed skull, arm and femur bones, reaching arms, walking legs and green odor particles; faster than parking skeleton (3.7 m/s baseline). Proposed 4.1 m/s, pending headset tuning.
- Zombie rests in an open grave, emerges after 60 seconds, hunts for 60 seconds, repeats for exactly five hunts; then stops.
- Three physical protective gems mounted on climbable trees, provisional reuse of prior game's gem mechanics.
- Golden skull replaces key; after hunt five, physically place skull on pedestal by exit to unlock gate; walk into enclosed finish chamber and touch native finish block.
- Reuse cooperative survival, capture, spectators, wipe reset and fog lifecycle patterns, pending user confirmation of 10-player capacity and spectator behavior.

## Defaults / decisions to validate
- 10-player design target; 60 s calm/60 s hunt, five attacks; 5-second all-dead reset.
- Gem held = temporary immunity; climbing trees alone is not immunity unless zombie cannot reach player. Trees should have real colliders and climbable surfaces.
- Zombie should chase living unprotected players on ground; no clipping through grave markers, fences or tree trunks. Avoid per-object high-cost checks when possible.
- Distinguish physical skull placement from mere proximity: snap/accept only when a living player releases the skull inside pedestal socket; restore skull if lost.
- Use named controller state and fresh generated IDs, not copied numeric IDs.
- Native .level, JSON, manifest, tests, preview, build script and README must be generated together before declaring playable.

## Source knowledge base
- ../docs/reuse/README.md
- ../docs/reuse/native-contract.md
- ../docs/reuse/play-model.md
- ../docs/reuse/components/monster.md
- ../docs/reuse/components/loot.md
- ../docs/reuse/components/doors.md
- ../parking-lot-horror/src/build.py and ../parking-lot-horror/src/monster.py

## Workstream boundaries (parallel conceptual tasks; no agents have been launched)
1. Coordinator: integration contracts, naming, performance budget, test gate.
2. Environment: grave grid, collision, trees, sky, pumpkin and candle geometry.
3. Zombie: actor primitives, animation, fumes, pursuit and hunt timing.
4. Loot/exit: tree gems, golden skull socket, gate, native finish.
5. Gameplay/QA: player state, spectator, wipe reset, native schema, tests, Quest checklist.

## Acceptance
- Five and only five attacks; zombie speed > 3.7 m/s; fog/particles stop appropriately; protection and spectators work in multiplayer; physical skull placement unlocks door; finish block marks completion.
- Build passes native schema and reference tests; Quest playtest required for gameplay/performance claims.
