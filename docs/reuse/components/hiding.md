# Single-occupant safe hiding

Pattern `hiding.safe-slot.v1`. Sources: [generator: Office controllers and MonsterAI guards](../../../office-after-hours/src/build.py), [all-twenty-slot/catch tests](../../../office-after-hours/tests/test_hunt_polish.py), [occupancy/departure tests](../../../office-after-hours/tests/test_gameplay.py).

## Contract

A hiding slot has a unique nonzero ID, one occupancy field, an entry control, an inside leave control, an interior point, an outside point and a liveness/departure volume. Empty occupancy is zero; an occupied field stores `Player.Id+1`.

Office maps closet IDs to 1..10 and desk IDs to 11..20. `Spots{i}.X` holds closet ownership, `.Y` desk ownership. `Player.Var3` is the selected player’s current hiding ID. Alive status is `Var1=0`; a player already hidden elsewhere cannot claim another slot.

1. On an entry rising edge, select/validate the triggering living player.
2. If they own this slot, the entry control can also leave. Otherwise reject occupied slots and players hidden elsewhere.
3. Set occupancy and Var3 together; clear reserved Var4. Give the inside leave control a 0.5s entry debounce.
4. For a closet, close its native door; request the intended interior movement.
5. On leave, clear occupancy/Var3, open a closet door if needed, and request outside movement. Inside leave sets a 0.8s cooldown.
6. Release stale occupancy for invalid, dead, mismatched or departed owners.

**Active hiding always prevents targeting and killing**, even if the monster saw entry. Filter it during target selection and recheck it immediately before death. Old Var4 “seen” values must not bypass this rule.

## Office departure defaults

| Slot | Horizontal limits from hide center | Height handling |
| --- | --- | --- |
| Closet | abs(ΔX)≤0.62, abs(ΔZ)≤0.6 | Clear if selected head Y>2.5 |
| Desk | abs(ΔX)≤0.85, abs(ΔZ)≤0.6 | Head height alone does not cancel protection |

Entry teleports use feet Y=0.1. Desk crouching provides intended visual cover; protection is a game state, not an automatic geometric occlusion test. One spot per player and one player per spot are separate invariants. Visual door state is not the hiding flag.

## Reuse

Allocate hiding IDs independently of object IDs; remap Var3 and occupancy consistently. Supply volumes and movement points from actual geometry. Use a local movement handler for remote players; current shared Office teleport calls are not a verified multiplayer solution. Check simultaneous claims on two devices, entry debounce, repeated entry/leave, departure, death/disconnect cleanup, all hidden players ignored, and hiding after AI selected a target. The harness checks logic, not native networking, hand tracking, movement comfort or atomic cross-client claims.
