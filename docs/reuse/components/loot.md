# Physical gems and inventory key

Pattern `loot.gem-and-key.v1`. Sources: [generator: Gem, GemMemory, seat_gem, GemInventory, KeyInventory](../../../office-after-hours/src/build.py), [physics fixture](../../../office-after-hours/tests/fixtures/native_connection_layout.json), [loot/hunt tests](../../../office-after-hours/tests/test_hunt_polish.py), [gameplay tests](../../../office-after-hours/tests/test_gameplay.py).

## Gem contract

Each gem is its own shared physics group (`physicsObject=True`, `localPhysicsObject=False`, mass 0.15), containing a collidable grabbable neon pyramid. Office size is `(0.22,0.20,0.22)`. Serialize it inside a valid drawer initially, not below the map waiting for code to rescue it.

| State field | Meaning |
| --- | --- |
| Loot.X | Assigned drawer for seating/recovery; remains a drawer number while held |
| Loot.Y | Estimated holder `Player.Id+1`, or zero |
| Loot.Z | Relocation epoch |
| GemMemory.X | Last applied relocation epoch |
| GemMemory.Y | First valid pickup occurred this epoch, 0/1 |

Before pickup, the controller seats the gem at its moving tray center every frame while physics stays enabled for grabbing. A physics-state-3 gem plus nearest living hand within **0.28m** identifies a carrier and sets the pickup latch. The latch stops drawer position writes even after release/throw. No authoritative holder-ID input is exposed by this pattern: close hands/handoffs can be ambiguous. Do not describe proximity alone as certain grip ownership.

Held ownership grants immunity; released/non-held gems clear it. The AI reads Loot.Y during target selection **and again before death**. A player can physically hold multiple gems; three gems do not guarantee three different protected players.

At hunt end, revoke holders, choose three distinct new drawers outside the previous set, and increment epochs. Relocation clears the pickup latch, disables physics, yields, sets drawer position, yields, then enables physics. Office recovers out-of-bounds gems (Y outside -10..6, |X|>9, Z outside -3..35) to their assigned drawer. Replace those map-specific bounds in another game. Native grip release/velocity reset during relocation remains unverified.

## Key contract

The key is **inventory-based**, not a throwable gem. `KeyState.X` is drawer number or zero when owned; Y is owner ID+1; Z is last drawer, with zero meaning never spawned. Visuals follow a drawer or float 0.5m above the carrier’s head; they are passable/non-grabbable.

A living player touches `LootUse` in an observed-open matching drawer to claim it. It appears after the fifth completed hunt. Death/disconnect rerolls a different drawer. A living key owner unlocks the [exit](doors.md) for everyone; only living players can escape.

## Reuse checks

Supply a drawer registry, three compatible empty positions, relocation policy, map bounds, slot/epoch mapping and key objective rules. Three new drawers outside three previous ones require at least **six eligible drawers**; with fewer, define another policy rather than copying rejection loops that may never terminate. Reset all ownership, latches and epochs coherently. Local tests cover injected falls/seating, free release, synthetic holding/immunity, relocation uniqueness and key respawn. Native grip, drawer motion, collision, velocity and shared ownership need engine tests.
