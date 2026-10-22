# Desk, chair and animated drawer

Pattern `desk.drawer.v1`. Sources: [generator: office desk/chair loop, Drawer, seat_gem](../../../office-after-hours/src/build.py), [drawer tests](../../../office-after-hours/tests/test_hunt_polish.py), [hiding](hiding.md), [loot](loot.md).

## Geometry and moving hierarchy

Office desk local layout uses a top at Y=1.3, size `(2.8,0.13,1.2)`, four legs and a rear panel, leaving central knee space. A chair is behind it toward +Z: seat Y=0.55, back center Y=0.95, stem/base below. Chair/monitor/paper are static decoration, not seat interactions.

| Part | Office default |
| --- | --- |
| Drawer group origin | `(deskX-0.85,0.98,deskZ)` |
| Tray | Bottom, front, back and two sides, plus handle; collidable static child geometry |
| Slide | Relative `(0,0,-0.7)`, 0.65s native `Slide` clip |
| Handle trigger | Drawer child at `(0,0.1,-0.58)`; moves with tray |
| Key pickup trigger | Drawer child `LootUse` at `(0,0.16,-0.1)` |
| Open observation | Original Z minus observed drawer Z >0.35m |
| Gem seat center | Drawer position plus `(0,0.145,0)` |

The fixed housing and desktop conceal a closed drawer. The current gem height 0.20m fits between the tray top and desktop underside; its center is Y=1.125 when the tray is at Y=0.98. Changing drawer dimensions requires checking the **whole gem bounding box**, not only its center.

Manual input is HAND/ONENTER → animation TOGGLE_REVERSE, non-looping. Register `Slide` for round RESET. Do not animate the desk housing or write the drawer transform from Office GASM. Native motion does not automatically guarantee that a loose physics item rides with it: the current [gem seating latch](loot.md) supplies that behavior until pickup.

## Reuse and hiding

Choose desk axes/front, top/leg clearance, drawer dimensions/slide, chair offset, trigger placements, loot registry and hiding slot ID. Attach moving controls before resolving IDs. The blue desk pad activates one safe hiding slot; use the separate [hiding contract](hiding.md). Crouching provides visual cover, while current protection does not cancel solely due to headset height.

Local tests check target wiring, moving trigger parenting, clip endpoints, gem seating/free release and occupancy. Native swept collisions, hand access, physical gem transition and seated/standing comfort need a headset test. Office’s shared hiding-controller teleport is not proven for remote clients; do not copy it as a general multiplayer movement handler.
