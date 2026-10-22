# Closet shell, hinge and hiding controls

Pattern `closet.hide.v1`. Sources: [generator: Closet hierarchy and Office controllers](../../../office-after-hours/src/build.py), [orientation/door tests](../../../office-after-hours/tests/test_playtest_fixes.py), [safe hiding tests](../../../office-after-hours/tests/test_hunt_polish.py).

## Local frame and placement

Define closet front as local **-Z**, rear +Z. Put the shell, hinged door, pads and button triggers in one parent group, then rotate the parent to face into the room. Avoid rotating only the visible panel while leaving controls/entry positions facing a wall.

| Parameter | Office default |
| --- | --- |
| Closet parent center | X=`side × 7.35`, Z=`officeZ-1.1`, Y=0 |
| Parent yaw | `side × 90°`; rear flush with outer wall at X=±8 |
| Shell | About 1.4m wide, 2.7m high, 1.3m deep |
| Door hinge in parent | `(-0.645,0,-0.62)` |
| Door panel local center | `(0.645,1.32,0)`, size `(1.29,2.6,0.08)` |
| Clip | `ClosetHinge`, +100° local yaw, 0.65s |
| Amber manual button | Parent local `(0.86,1.3,-0.65)`; native toggle |
| Blue enter pad/trigger | Parent local `(0,1.2,-0.83)` |
| Inside leave trigger | Parent local `(0,1.3,-0.43)` |

`ClosetDoorUse` directly toggles the hinge. `ClosetUse`/`ClosetLeave` route to guarded Office logic. `ClosetClose` and `ClosetOpen` are empty-source forced animation START triggers; close uses `reverse=True`. Register the door clip for round RESET.

## Interaction contract

A living, currently unhidden player can claim the empty closet slot. The slot stores `Player.Id+1`. Entry sets safe hiding, closes the door and attempts a feet-position teleport to the interior. The inside leave control is suppressed for 0.5s after entry to avoid an immediate accidental exit. Leaving clears occupancy/protection, opens the door and uses a world-space exit point **in front of the rotated closet**. Death, disconnect and departure release the slot.

A second player cannot claim an occupied closet. Active hiding is safe even when entry was observed; opening/closing the visual door is not itself the protection flag.

## Reuse and checks

Supply shell dimensions, local front, wall transform, hinge, controls, interior/exit locations and a globally unique hiding ID. Compute world entry/exit coordinates from the same parent transform; do not reuse Office’s ±X formula in an arbitrary layout. Validate wall clearance, door swing, accessible buttons inside/outside, occupancy and all escape routes. Parent orientation/native endpoint and local hiding checks exist. Physical comfort, contact behavior and remote-client entry teleports remain engine pending; see [native contract](../native-contract.md).
