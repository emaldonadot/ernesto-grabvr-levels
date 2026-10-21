# Office After Hours — level memory

Created for Ernesto on 2026-10-20. Status: experimental native GRAB build, not published and not verified on Quest.

## Requested game

A central hall with ten offices, five per side. Each office has a desk, one opening drawer, a chair behind the desk, a closet, and an initially closed door that requires interaction. Players search drawers for three randomly placed gems. Gem holders are immune and ignored by the monster. Each closet and desk supports one hiding player. A monster that witnesses entry into a hiding place can still catch that player. Death removes participation but leaves the player present as a spectator with an overhead dead marker and no gameplay interactions. After the fifth monster appearance, a key permits escape through the main door at the end of the hall. If its carrier dies, the key goes into another drawer.

## Decisions for this build

- Cooperative office horror; title and muted green/teal office palette are provisional.
- Exactly 60 seconds calm followed by exactly 60 seconds hunting. This final explicit timing supersedes the earlier request for randomly timed attacks.
- First attack starts at 01:00. Fifth attack runs 09:00–10:00. The key appears when the fifth attack ENDS, at 10:00. Hunts continue thereafter.
- The monster randomly appears at either end of the corridor. Spawn timing itself is fixed.
- All three gems exist from round start. Three distinct drawers are selected at round start and after every hunt. Ownership is revoked when they relocate.
- At most one gem per player, so three players can receive protection. Gem possession is a scripted inventory state; the visible gem floats above its holder. Pickup uses the inside-drawer hand trigger.
- Doors lift vertically to avoid swinging into VR players. Drawer trays move outwards. Touching a handle toggles it; no controller-specific button mapping is assumed.
- Blue pads enter hiding; a second reachable pad leaves. Walking out also cancels hiding. No forced camera lock.
- The closet remains visually closed while occupied. Players enter by a short scripted teleport. Desk entry places the head under the desktop. These heights need seated/standing VR calibration.
- The key is inventory-based. Its holder unlocks the exit for all survivors. Only living players can activate escape completion. If its owner dies or disconnects, it respawns in a drawer different from its last drawer.
- Scripted death: player variable status becomes dead; no native respawn is requested. Dead players can move around the map, are ignored by AI, and cannot activate doors, drawers, loot, hiding or exit. No physics-grabbable props are included.
- Sixteen overhead dead markers are provisioned. AI and interaction logic do not hard-code player IDs or assume a fixed player count. Ernesto confirmed a target of TEN simultaneous players on 2026-10-21. With three gems, up to three players are protected and seven must hide or evade. There are twenty individual hiding spaces. Sixteen markers are retained as spare capacity. This target is not an enforced platform lobby-size limit; ten-headset performance and synchronization remain unverified.
- A single GRAB level is supplied, with generated native GASM, not a JavaScript file presented as a GRAB script.

## Native state contract

| State | X | Y | Z |
| --- | --- | --- | --- |
| Clock | attack active 0/1 | completed attacks | phase elapsed seconds |
| Room1..10 | door target open 0/1 | drawer open 0/1 | reserved |
| Spots1..10 | closet occupant player ID + 1 | desk occupant player ID + 1 | reserved |
| Edge / EdgeB | trigger latches | trigger latches | trigger latches |
| LootA/B/C | drawer number 1..10, or 0 when held | owner player ID + 1, or 0 | reserved |
| KeyState | drawer number, or 0 when held | owner player ID + 1, or 0 | last drawer; 0 means not spawned yet |
| Target | chosen player ID + 1 | target X | target Z |
| Waypoint | navigation X | reserved | navigation Z |
| ExitState | exit unlocked 0/1 | reserved | reserved |

Player.Var1 = 0 living, 1 dead, 2 escaped; Player.Var3 = hiding spot (1..10 closet, 11..20 desk); Player.Var4 = witnessed hiding. Var2 and Var5 are unused. Gem/key ownership is authoritative in shared loot state.

## Outstanding engine validation and limitations

This is a generated experimental prototype, not a claim of a fully tested multiplayer level.

1. Confirm selection/teleport/trigger-force connection semantics and shared player-variable writes on the current Quest build. They follow the current GRAB Tools connection schema, but a local instruction harness cannot establish engine behavior.
2. Witnessed hiding currently uses a room/corridor visibility approximation. It does not ray-test furniture or use a monster field-of-view cone. Exact occlusion remains to implement/verify.
3. Monster movement follows corridor and doorway waypoints and opens office doors. It does not run a navigation mesh or avoid desk/chair geometry. It can overlap furniture. Catch distance is horizontal and needs wall/height safeguards before release.
4. Shared GASM authority, host migration, joins during a round, disconnects and simultaneous input need two-headset testing. Working-register reset/migration behavior is unverified.
5. Dead players are blocked from this level's scripted actions. Platform menus, locomotion, native avatar collisions and external GRAB controls are not disabled; this is not an engine-provided spectator mode.
6. The native finish is isolated off-map and only reached through the living-player escape trigger, to keep dead players from completing via the exit area.
7. Global clock begins on level load. There is no ready-up lobby, round reset, all-dead reset, or reconnect identity persistence yet. Reload the level to start a fresh round.
8. Counterpart collection and code-block budget are unverified. The local VM enforces a 500-instruction-per-frame budget; large multiplayer populations can slow AI scans.
9. Complexity metadata is an estimate. Re-save in GRAB before publishing to let the game calculate its current official value.
10. The browser editor failed before import because it could not create a WebGL context. No browser-engine validation or Quest performance measurement was completed.
11. The requested YouTube channel could not be fetched. No specific animation technique is attributed to that channel. Native neon eyes, emissive fixtures and timed fog are used.

## Questions for the next design pass

- Resolved: ten simultaneous players. Keep three gems and twenty hiding spaces.
- Keep cooperative office horror, or add competitive scoring / a different monster theme?
- Should the key appear at the START or END of the fifth attack? This prototype uses the end.

## Sources checked

- https://grabvr.tools/ and https://grabvr.tools/editor
- https://grabvr.quest/
- https://github.com/Slin/GRAB-Level-Format (binary format and installation conventions; older schema)
- https://github.com/twhlynch/GRAB-Tools (current format 25 schema, connection ordering, assembly conversion, object ID traversal)
- https://blog.twhlynch.me/introduction-to-gasm/
- https://youtube.com/@make.money.with.ai.nowwwww (requested; not retrievable in this session)
