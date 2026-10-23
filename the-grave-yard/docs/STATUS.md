# The Grave Yard — implementation board

Last update: 2026-10-22

| Workstream | Status | Deliverable |
| --- | --- | --- |
| Coordinator / contracts | In progress | LEVEL-MEMORY, integration checklist |
| Environment | Source committed; native integration pending | src/environment.py primitive geometry and layout test |
| Zombie | Queued | animated decayed actor, green particles, pursuit |
| Gameplay | In progress | src/rules.py reference rules and tests |
| Native adapter/export | Queued | native format25 JSON, GASM, .level |
| Automated validation | CI configured; execution unverified | tests/test_rules.py, tests/test_environment.py, GitHub Actions workflow |
| Quest validation | Blocked | requires headset import and multiplayer playtest |

No independent subagents were actually launched. The Python rules module is an engine-independent reference model, not wired to native GRAB controllers. Do not mark native level playable until serialization, native-contract tests and Quest validation pass.

## Coordinator handoffs
1. Environment exports unique symbolic node names and tree/grave collision registry.
2. Zombie consumes phase, player alive status and gem-held state; tree climbing alone never grants immunity.
3. Loot tracks three physical gems; skull placement requires physical release within socket after hunt five.
4. Native adapter translates tested rules into GRAB GASM and state nodes, then emits .json and .level together.
5. QA validates serialized references, VM behavior, performance and actual Quest multiplayer behavior.

## Progress update
- Committed primitive environment builder with 16 graves, six branch-bearing trees, four pumpkins, three candles, moon, clouds, fence and skull pedestal.
- Added layout unit test and GitHub Actions reference-test workflow; CI outcome has not been inspected.
- Native GRAB serializer and full gameplay integration remain unfinished. No playable .level artifact has been produced or verified.
