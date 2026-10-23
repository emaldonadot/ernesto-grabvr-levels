# The Grave Yard — implementation board

Updated 2026-10-22; revision `grave-yard-1`.

| Workstream | Status | Deliverable |
| --- | --- | --- |
| Coordinator / integration | Complete locally | Native build, state contracts, regenerated outputs, test gate |
| Environment | Complete locally | Fenced 16-grave yard, climbable trees, pumpkins, moon/clouds, three candles, skull pedestal |
| Zombie | Complete locally | Decayed actor, shamble clip, green particles, obstacle detours, held-gem-only eligibility |
| Loot and exit | Complete locally | Three physical tree gems, physical skull release socket, animated gate, enclosed native finish |
| Multiplayer state | Complete locally; engine pending | Shared phases/status, local spectator/revival, five-second wipe |
| Native export | Complete | Format 25 JSON, binary `.level`, GASM and ID manifest |
| Automated validation | Passed | 22 reference, layout, native contract and bytecode tests |
| Editor validation | Blocked by environment | Browser WebGL initialization failed before import |
| Quest validation | Pending user headset test | Import, physics, multiplayer, actual finish, performance |

Independent agents handled native gameplay, zombie, environment and QA under coordinator integration. The deliverable is an experimental native build ready for headset testing; no successful GRAB/Quest playtest is claimed.

See [validation details](VALIDATION.md), [headset checklist](QUEST-PLAYTEST.md) and [level download](../dist/the-grave-yard.level).

## Revision 2 — 2026-10-23

Complete locally: staged physical-skull exit guidance, gold socket ring, green walk-to-finish route, 8m solid nongrabbable perimeter/header and transparent collision cap above trees. Seven added checks bring the total to 29 passing tests. Rebuilt native artifacts and inspected the software preview. Quest collision/visibility/native completion validation remains pending.

Spectator view 3 makes the tall east boundary and gallery glass transparent while retaining collision and player separation. Quest visibility checks are pending.
