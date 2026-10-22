# Native doors and gated openings

Pattern `door.hinge.v1`. Implementation: [generator: Door, ExitDoor, animation and trigger wiring](../../../office-after-hours/src/build.py), [native contract tests](../../../office-after-hours/tests/test_native_contract.py). Read [native mode/ID contracts](../native-contract.md) before composing.

## Hinge contract

Put the animated group origin **on the hinge edge**. Offset the panel and handle as child geometry so the closed position is correct. Animate the group, not the panel center. Keep the trigger accessible after opening: Office doors use a fixed blue wall button on either approach side.

| Parameter | Office default |
| --- | --- |
| Panel | Thickness 0.16m, height 2.5m, width along Z 1.45m |
| Hinge | Doorway center Z minus 0.725m |
| Panel local center | `(0,1.25,0.725)` |
| Clip | `Hinge`, 0.65s, zero offset → yaw `side × 90°` |
| Manual input | HAND → ONENTER → animation TOGGLE_REVERSE 3; loop false |
| Initial state | `activeAnimation=-1`, closed |
| Observed open threshold | Absolute GASM yaw >45°; not an animation target state variable |
| Monster opening | Empty-source forced trigger → animation START 1 |
| Round reset | Animation RESET 5, registered by symbolic name |

A player withdraws the hand before touching again. Do not drive the same transform each frame with GASM while its native animation runs. Native GASM START targets are for guarded logic; they are not substitutes for a direct animation target when no gameplay authorization is needed.

## Gated exit variant

Office exit uses a 2.4m-wide panel with hinge at X=-1.2, clip `ExitHinge` yaw +90°. `ExitUse` goes to `ExitController`, which verifies a living player owns the inventory key. Only then does it set the cooperative unlock flag and force `ExitOpen` to START the native clip. A separate HEAD escape trigger checks alive/unlocked state before setting escaped status and attempting the off-map finish teleport.

When resetting an exit, clear its unlock flag and rearm the force trigger as well as resetting the clip; otherwise the next round may lack a fresh activation edge. The current tests cover rearming. See [loot](loot.md) and [local-only teleport limitation](../native-contract.md).

## Reuse and checks

Supply pivot, panel dimensions, swing side, clip name/duration, button location, authorization policy and reset registration. Recompute every child local offset when dimensions change. Check swept clearance, buttons reachable from both sides, full open/close, repeated touches and reset-then-reopen. Office door opening has explicit headset confirmation. Closet/exit variants and timing/reset behavior have local checks but require their own headset validation. Native manual triggers do not filter spectators; Office physically separates dead players instead.
