# Office After Hours — level memory

Created for Ernesto on 2026-10-20. Status: experimental native GRAB build, repository public; office doors and solo monster pursuit confirmed by Ernesto; revision 5 awaits Quest testing.

Reusable cross-game patterns: [catalog and ChatGPT entrypoint](../docs/reuse/README.md). This file remains the authority for Office-specific rules, parameters and validation history.

## Requested game

A central hall with ten offices, five per side. Each office has a desk, one opening drawer, a chair behind the desk, a closet, and an initially closed door that requires interaction. Players search drawers for three randomly placed gems. Gem holders are immune and ignored by the monster. Each closet and desk supports one hiding player. Originally, a monster that witnessed entry could catch that player. Ernesto superseded this on 2026-10-22: active hiding must always prevent targeting and killing. Death removes participation but leaves the player present as a spectator with an overhead dead marker and no gameplay interactions. After the fifth monster appearance, a key permits escape through the main door at the end of the hall. If its carrier dies, the key goes into another drawer.

## Decisions for this build

- Cooperative office horror; title and muted green/teal office palette are provisional.
- Exactly 60 seconds calm followed by exactly 60 seconds hunting. This final explicit timing supersedes the earlier request for randomly timed attacks.
- First attack starts at 01:00. Fifth attack runs 09:00–10:00. The key appears when the fifth attack ENDS, at 10:00. Hunts continue thereafter.
- The monster randomly appears at either end of the corridor. Spawn timing itself is fixed.
- All three gems exist from round start. Three distinct drawers are selected at round start and after every hunt. After a hunt, none of the three previous drawers is reused. Ownership is revoked when they relocate.
- Gems are shared physics groups with collidable, grabbable child geometry and 0.15kg mass. Direct native grabbing/throwing replaces scripted gem inventory. At most three distinct players can be protected; native grabbing can allow one player to hold two gems. Physics state 3 and the nearest living hand within 28cm estimate the holder; there is no exposed holder-ID input. Released gems confer no protection. Test handoffs and overlapping hands on devices.
- Office door group origins sit at the side hinge. Native ONENTER targets use TOGGLE_REVERSE, non-looping, 0.65s, +/-90-degree yaw. Fixed blue wall buttons are reachable on both sides. Drawer groups slide 0.7m with their handle triggers attached. Door/drawer transforms are no longer written each frame by Office GASM. The key-gated exit also uses a native hinge animation via an authorized forced trigger.
- Blue pads enter hiding; a second reachable pad leaves. Walking out also cancels hiding. No forced camera lock.
- Active hiding is unconditional protection, even if entry is observed. The AI filters it during selection and immediately before death. Desk protection is latched until leaving its horizontal space or using the leave control, rather than revoked by headset height. Closet shells are rotated +/-90 degrees against the exterior walls, facing the room. Amber buttons toggle native hinge doors. Blue hiding pads close doors and teleport the player inside; leaving opens doors toward the room. Desk entry places the head under the desktop. Heights need seated/standing VR calibration.
- The key is inventory-based. Its holder unlocks the exit for all survivors. Only living players can activate escape completion. If its owner dies or disconnects, it respawns in a drawer different from its last drawer.
- Scripted death: status becomes dead. A non-shared LocalSpectator controller selects its local player and teleports them to an enclosed observation balcony, away from physical gems. This also handles non-host clients because native teleport is local-only. Transparent ceiling/floor permit viewing. AI ignores dead players and loot/hiding/exit actions reject them. Native door/drawer triggers intentionally do not filter dead players; physical separation normally prevents their reaching them. Ernesto accepted doors/drawers being usable by spectators, conditional on no monster/gem interaction.
- Sixteen overhead dead markers are provisioned. AI and interaction logic do not hard-code player IDs or assume a fixed player count. Ernesto confirmed a target of TEN simultaneous players on 2026-10-21. With three gems, up to three players are protected and seven must hide or evade. There are twenty individual hiding spaces. Sixteen markers are retained as spare capacity. This target is not an enforced platform lobby-size limit; ten-headset performance and synchronization remain unverified.
- A single GRAB level is supplied, with generated native GASM, not a JavaScript file presented as a GRAB script.

## Native state contract

| State | X | Y | Z |
| --- | --- | --- | --- |
| Clock | attack active 0/1 | completed attacks | phase elapsed seconds |
| Round | death reset active 0/1 | countdown seconds remaining | round epoch, initially 1 |
| Room1..10 | observed door yaw above 45 degrees | observed drawer extension above 0.35m | reserved |
| Spots1..10 | closet occupant player ID + 1 | desk occupant player ID + 1 | reserved |
| Edge / EdgeB | trigger latches | trigger latches | trigger latches |
| LootA/B/C | assigned recovery/relocation drawer 1..10 | estimated held-by player ID + 1, or 0 | relocation epoch |
| GemMemory1..3 | last applied relocation epoch | picked up at least once in this epoch, 0/1 | reserved |
| KeyState | drawer number, or 0 when held | owner player ID + 1, or 0 | last drawer; 0 means not spawned yet |
| Target | chosen player ID + 1 | target X | target Z |
| Waypoint | navigation X | reserved | navigation Z |
| ExitState | exit unlocked 0/1 | reserved | reserved |

Player.Var1 = 0 living, 1 dead, 2 escaped; Player.Var3 = hiding spot (1..10 closet, 11..20 desk); Player.Var4 = reserved/cleared compatibility slot; old witnessed-hiding flags no longer affect safety. Var2 is unused. Var5 records the local player’s acknowledged round epoch; a new epoch revives and teleports that player into the hall on their own client. Key ownership is authoritative in shared state. Gem ownership is a physics/hand-proximity heuristic, cleared when released; positions follow the tray while unclaimed, then are only written on relocation or out-of-bounds recovery after first pickup. Initial spawn fits below the desktop and above the tray bottom.

## Outstanding engine validation and limitations

This is a generated experimental prototype, not a claim of a fully tested multiplayer level.

1. Confirm selection/teleport/trigger-force connection semantics and shared player-variable writes on the current Quest build. They follow the current GRAB Tools connection schema, but a local instruction harness cannot establish engine behavior.
2. Hiding intentionally grants unconditional protection while active. Verify that entry/leave triggers and occupancy cleanup register reliably on each headset. Desk crouching is visual cover; head height alone no longer cancels protection.
3. Monster movement follows corridor and doorway waypoints and opens office doors. It does not run a navigation mesh or avoid desk/chair geometry. It can overlap furniture. Catch distance is horizontal and needs wall/height safeguards before release.
4. Shared GASM authority, host migration, joins during a round, disconnects and simultaneous input need two-headset testing. Working-register reset/migration behavior is unverified.
5. Dead spectators are physically separated on a balcony. Local teleport, boundaries, transparent viewing, and non-host behavior need headset testing. Platform menus and external controls remain available; this is not engine-provided spectator mode.
6. Revision 5 places the native finish at (0,1.2,33), one meter behind the exit, after unlocking. It starts below the map while locked. Dead players remain separated in the balcony; native finish collision does not independently enforce scripted player status.
7. Global clock begins on level load. Unanimous connected-player death shows a five-second countdown, then resets round state/animations and revives everyone in the hall. Local client epoch acknowledgments handle teleport. There is no ready-up lobby or reconnect identity persistence. Escaped players prevent the all-dead reset; reload after a completed escape round.
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

## 2026-10-21 — interaction repair 1

Ernesto tested the original level in GRAB: the scene looked good, but none of the triggers worked; office doors and drawers did not open. Preserve the existing geometry.

Investigation found that the connection helper assumptions were incomplete. A GRAB-exported September 2026 lobby contains fourteen 28-component player properties and twenty-seven 6-component trigger properties. The original generator emitted 27 / 4 and put velocity before teleport instead of including Respawn at slot 19. The previous VM copied this faulty layout, so its tests were not a native compatibility check.

Changes: player properties now preserve all 28 slots with Respawn=19, teleport=20..24 and velocity=25..27; trigger properties now preserve six slots, leaving unused trailing slots unbound. All 72 interaction triggers explicitly START their office/exit controller, without restarting debounce state. The VM rejects incomplete properties and uses the corrected teleport slots. A source-identified fixture records the external layout; seventeen regression checks now pass, including all ten doors/drawers toggling and rejection of the old layouts. Geometry is byte-equivalent as JSON values to the original scene after excluding code and trigger targets.

The rebuilt in-game title is `Office After Hours [Interaction fix 1]`. This corrects demonstrated file-format discrepancies and improves trigger wiring. It is not yet a confirmed headset fix. Further engine behavior, especially local-only teleport and multiplayer spectator handling, still needs real GRAB testing.

## 2026-10-21 — native animations and physics revision

Ernesto confirmed play mode and solo monster pursuit, but door/drawer interaction still failed. He requested triggers that start side-hinge door animations, animated drawers, and gems that can be held, thrown and collide with walls/moving trays. He accepted spectators operating doors/drawers if they cannot interact with monsters/gems. Current revision replaces the old per-frame motion and gem inventory; see decisions and state contract above. Uses direct native animation targets, idle `activeAnimation=-1`, and a guarded native exit animation. Twenty local tests pass; the harness only models animation endpoints and synthetic physics/hand states, not actual collisions, grips, timing or networking. Do not call this a confirmed headset fix.

## 2026-10-21 — playtest fixes 3

Ernesto confirmed office doors work. He reported backward closets, inactive closet doors, invisible hunt fog, missing drawer gems, no all-dead restart, and a monster that does not turn; requested slightly faster pursuit.

Implemented inward-facing closets at x=+/-7.35, native closet hinges/buttons, and correctly oriented hiding exits. Added gray fog density 0.72 and per-client ambience application, including late clients. The GRAB Tools renderer maps density through a fourth power, so the previous 0.075 was too small for this indoor scale. Reference: `https://github.com/twhlynch/GRAB-Tools` / `website/src` LevelLoader implementation (local research copy).

Independently re-parsed the September 2026 lobby. All four physics connections expose Enabled as INOUT and State as INPUT; the generator previously used OUTPUT following the helper. Corrected this and extended the independent fixture. Gems serialize inside valid drawers, measure 0.22 x 0.20 x 0.22m, and relocate using disable/yield/position/yield/enable. A post-hunt set never reuses the preceding three drawers. Actual gripping, velocity reset and tray collisions remain engine tests.

Monster eyes use atan2 of the walking vector plus 180 degrees because the mesh faces local -Z. Speed is 3.1m/s, up from 2.6. A catch guard rejects calm/reset frames even if an AI scan spans a phase change. Unanimous death starts a five-second countdown and round epoch increment, clears hunt/key/exit/hiding state, resets native animations, and revives/teleports every local client. 29 checks pass, including a simulated ten-client wipe and recovery. These checks do not prove engine behavior.

## 2026-10-22 — hunt polish 4

Ernesto likes the current scene. Latest requests supersede the original witnessed-hiding exception: hidden players must not be targeted or killed. He reports fog persisting after hunts and gems falling to the floor when drawers open; requests monster fumes and another slight speed increase.

Fog clear is now density zero with zero transition duration, attached to the hunt trigger ONLEAVE as well as a distinct calm target. LocalFog rearms triggers across frame boundaries and repeats calm clearing every 0.5 seconds, including resets and late clients. Initial ambience also has zero fog.

MonsterFumes is a native emitter parented to Monster, not a static decoration: 18 particles/second, 0.55–1s lifespan, rising/spreading velocity, expanding sizes, end alpha zero. Nominal peak is 18 live particles. Moving the monster below the map stops visible emission; existing puffs dissipate within one second. Pursuit speed rises from 3.1 to 3.4m/s (~9.7%).

Unclaimed gem seating uses GemMemory.Y=0: follow the assigned tray center every frame while leaving physics enabled for grabbing. A held-state plus living-hand match sets GemMemory.Y=1, then the gem is free from drawer position writes even after release/throw. Relocation clears the latch. Physical collision/velocity and first-grip transitions still require Quest validation.

Removed observed-entry checks from Office and MonsterAI. A stale Var4 cannot bypass protection. Desk entry uses feet height 0.1m, not the old head-oriented 0.55m assumption. Head height no longer revokes desk hiding; horizontal departure and leave controls still do. Entry gives the inside leave pad a 0.5s debounce.

35 local tests pass: repeated fog ONLEAVE/calm clears, all-dead clearing, injected gem falls during tray movement followed by free pickup/release, all twenty safe hiding spots (including stale observed flags), a catch-phase hiding race, native particle configuration, revised speed and prior round/key/native contracts. The VM now dispatches native ONLEAVE targets; it still does not emulate engine rendering, grip physics or networking.

## 2026-10-23 — exit fix 5

Ernesto reports the key disappears on touch and he cannot exit. Inspection found intentional inventory pickup (owner ID+1 retained, visual moved 0.5m above the carrier’s head), an unmarked hand trigger requiring a second interaction, and an off-map finish reached through an unsupported shared-controller teleport. The exact headset unlock failure is not established by the local harness.

The exit now has a neon gold lock attached to its moving panel, a shared KEY COLLECTED instruction sign at the exit while a living player owns the key, and a proximity fallback: the living key holder unlocks within X +/-1.1m, Z 30.5..32m and head Y 0..2.7m. Touching the gold lock remains supported. Ownership and death/disconnect recovery remain inventory-based; touching the key is not physical grabbing. Unlock is cooperative for all survivors.

Removed the off-map platform and all ExitController teleport writes. The native finish is raised from Y=-100 to (0,1.2,33), radius 0.65m, once unlocked. This is one meter behind the door on the existing continuous floor, before the back wall at Z=33.9m. The scripted escape flag requires a living player’s HEAD escape trigger and distance <=0.65m from the finish center. Reset hides the finish and rearms the forced animation. The local harness verifies pickup, ownership, touch and proximity unlocking, two survivors finishing without teleport, invalid/distant/balcony rejection, reset and chamber clearance.

41 local tests pass; protobuf round-trip matches. These are synthetic bytecode and geometry checks, not a confirmed Quest completion test. Load title: Office After Hours [Exit fix 5].
