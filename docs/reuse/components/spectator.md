# Scripted death and enclosed spectator mode

Pattern `spectator.enclosed.v1`. Sources: [generator: LocalSpectator, DeadMarker, balcony](../../../office-after-hours/src/build.py), [round/client tests](../../../office-after-hours/tests/test_playtest_fixes.py), [gameplay tests](../../../office-after-hours/tests/test_gameplay.py).

## Contract

Death sets `Player.Var1=1` and clears hiding state. It does not request native respawn or remove the player from the lobby. Dead players are excluded from AI, gem/key claims, hiding and exit authorization.

`LocalSpectator` is non-shared and selects `Player.LocalId` every loop. It moves its own dead player into an enclosed viewing area, correcting departures from its allowed bounds. This is important because native teleport is local-only: a shared host controller cannot be assumed to move every remote avatar.

| Parameter | Office default |
| --- | --- |
| Entry feet position | `(0,8.05,16)` |
| Allowed selected-head bounds | Y 8..11, abs(X)≤2, Z 0..32 |
| Physical enclosure | Floor top Y=8; side/end walls and roof |
| Viewing | Transparent floor/walls and game ceiling |
| Dead marker | Red `[ X ] / DEAD` sign at head Y+0.65 |
| Marker provision | 16 player-index slots; game target is 10 |

Physical separation prevents dead players from reaching shared physical gems without globally disabling gems for survivors. Native manual door/drawer triggers do not contain a dead-player guard; they are normally unreachable from the balcony. This matches Ernesto’s acceptance of spectator door/drawer interaction provided monsters/gems remain protected.

## Round revival

`Round.Z` is an epoch. Each client compares it with its player’s Var5. When it acknowledges a new epoch greater than 1, it clears dead/hiding state and teleports itself into the hall. Current spawn spreading uses player ID modulo 10; it is not a general collision-free spawn allocator. On the initial epoch, the handler acknowledges state without moving every new living player to the hall again.

## Reuse and limits

Supply an enclosure, viewing method, local bounds/entry point, marker count/style, status mapping, epoch acknowledgement and safe spawn allocator. Keep an isolated, authorized finish so a spectator cannot complete by walking into the ordinary exit area. Test non-host death/revival, late clients, boundaries, gem reach, disconnect/reindexing and markers.

This is **scripted spectator behavior**, not an engine spectator/free-camera mode. Menus, external controls and native avatar interactions are not globally disabled. Platform escape/glitches and multiplayer synchronization are engine pending; local ten-client simulation does not prove them.
