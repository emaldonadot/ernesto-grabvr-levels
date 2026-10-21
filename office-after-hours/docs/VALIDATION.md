# Validation — Playtest fixes 3

2026-10-21: 29 local tests PASS; protobuf encode/decode equality PASS. Build: 727 nodes, 35 code blocks, estimated complexity 5,586.

## Headset feedback

Ernesto confirmed the preceding revision’s office doors now work. Monster pursuit already worked in solo play. He reported backward closets, inactive closet doors, invisible fog, missing drawer gems, absent all-dead restart, and a monster that did not turn. Revision 3 addresses these reports; it has not yet been tested on a headset.

## Evidence and changes

- All ten closets now have their backs flush with exterior walls at x=+/-8 and their fronts toward room interiors. Amber buttons directly toggle native hinge animations. Blue hiding pads close doors; leaving opens them and exits toward the room. Existing single-occupant checks still pass.
- Hunt fog density increases from 0.075 to 0.72 with a gray tint. GRAB Tools’ LevelLoader maps density through the fourth power; the previous value was negligible at office scale. A local non-shared controller applies/clears ambience on phase changes and when a client starts during a hunt.
- All four physics properties independently extracted from the source-identified September 2026 lobby use Enabled INOUT / State INPUT. Corrected the generator’s Enabled OUTPUT binding. The fixture independently records this layout.
- Gems serialize inside three real drawers rather than below the map. Larger neon geometry fits the tray/desktop cavity. Relocation now yields after physics disable and after position writes before reenabling physics. Native movement remains free between relocations.
- Hunt-end relocation revokes protection and selects three distinct drawers outside the preceding set. Synthetic held/released tests still check immunity; native grip ownership remains a held-state/nearest-hand heuristic.
- Monster speed increases 2.6 → 3.1m/s. Signed heading checks in four directions verify that its local -Z eyes align with movement. Catch logic rejects calm/reset phases.
- A ten-client simulation verifies the 5 → 1 unanimous-death countdown, delayed revival, per-client hall teleports, key/hunt/exit/hiding reset, and native animation resets. Empty lobbies, survivors and escaped players do not trigger a wipe reset.
- Existing independent player/trigger contracts, hiding occupancy, key death/respawn, escape and hunt/key timing tests pass.

## Limits

The harness models animation endpoints and synthetic physics/hand states. It does not run GRAB’s collision solver, native grip system, ambience rendering, live multiplayer networking or headset tracking. Real-device checks remain necessary for gem visibility, holding/immunity, physics relocation/velocity, closet door contact, fog on each client and simultaneous ten-player restart. Keep the working office-door mechanism unchanged while testing.

Primary references: the fixture’s GRAB-exported lobby URL/SHA-256; `https://github.com/twhlynch/GRAB-Tools` LevelLoader implementation and native schema. The upstream helper’s physics Enabled direction differed from the exported level, so the exported layout is used.
