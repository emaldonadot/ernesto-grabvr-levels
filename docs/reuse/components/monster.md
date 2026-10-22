# Monster, pursuit and fumes

Pattern `monster.pursuer.v1`. Office defaults below are tuning choices, not GRAB requirements.

Implementation: [generator: Monster geometry, MonsterFumes, MonsterAI](../../../office-after-hours/src/build.py), [generated AI](../../../office-after-hours/src/MonsterAI.gasm), [hunt tests](../../../office-after-hours/tests/test_hunt_polish.py), [heading/speed tests](../../../office-after-hours/tests/test_playtest_fixes.py).

## Contract and composition

A named `Monster` group owns visible non-lava body parts, eyes and its native particle emitter. Front is local **-Z**. `MonsterAI` reads `Clock.X`, player status/hiding and gem holder states, and writes Monster position/yaw, Target and Waypoint. Route geometry is specific to the current hall/office topology; it is not a general pathfinder.

| Parameter | Office default |
| --- | --- |
| Speed | 3.4m/s × DeltaTime, step clamped to remaining waypoint distance |
| Spawn | Random hall end `(0,0,0)` or `(0,0,30)` at hunt start |
| Inactive placement | Y = -100; Target.X = 0 |
| Heading | `degrees(atan2(dx,dz)) + 180` for the -Z-facing mesh |
| Catch | Horizontal squared distance ≤ 0.65, about 0.806m radius; **not** 0.65m radius |
| Protection | Skip invalid, dead/escaped, active hidden, or estimated gem-holding players |
| Recheck | Phase, selection, player status, gem ownership and hiding immediately before death |

Nearest eligible player is selected by horizontal squared distance. Corridor/doorway waypoints route into/out of rooms, with `DoorMonster{i}` forced native START to open a needed door. With no eligible target, the monster stays present but does not pursue. It must never use native lava contact to bypass scripted immunity.

### Fume emitter

`MonsterFumes` is a child of Monster at `(0,1.3,0)`, scale `(0.7,1.35,0.45)`. It emits 18 particles/s, lifetime 0.55–1s, rising velocity Y 0.2–0.6 with slight spread, start size 0.06–0.12, end size 0.28–0.42, gray color ending at alpha zero. Nominal maximum is 18 live particles. Parenting makes emission follow movement/rotation; old world-space puffs may last up to one second after the actor is hidden below the map.

## Reuse

1. Supply a spawn set and route graph/room bounds for the new layout; replace Office-specific waypoint logic.
2. Keep mesh front/pivot explicit; recompute heading offset if changing the mesh orientation.
3. Bind the new game’s status, hiding and protection registry; preserve both selection and catch guards.
4. Register doors the monster can open, and a clear inactive/reset behavior.
5. Parent effects to the actor; budget particles independently of decorative geometry.

**Evidence:** Solo pursuit was confirmed by Ernesto. Current 3.4m/s heading, safe hiding, catch recheck and emitter configuration are locally checked. Particle rendering, native multiplayer authority, performance and the latest tuning remain engine pending. The current AI has no navmesh, furniture avoidance, wall raycast or vertical catch-distance guard; do not copy it as a complete obstacle-aware monster.

## Parking ground-navigation variant

[Parking Lot Horror revision 2](../../../parking-lot-horror/LEVEL-MEMORY.md) adds a separate [native navigation generator](../../../parking-lot-horror/src/navigation.py). It permits diagonal ground pursuit across empty stalls and uses conservative vehicle/column footprints, actor clearance and swept movement checks to avoid solid obstacles. Vehicle footprints include opening-door envelopes. The skeleton stays at ground height; capture also checks vehicle occlusion and player height rather than treating horizontal proximity alone as contact.

An inexpensive shared clock supplies elapsed movement time while route evaluation spans instruction slices. Keep final phase, status, hiding and immunity checks immediately before capture after any expensive geometry checks. [Navigation tests](../../../parking-lot-horror/tests/test_navigation.py) inspect paths produced by serialized bytecode against an independent segment-intersection calculation, including diagonal pursuit, detours and elevated/interior targets. This is a game-specific static-footprint planner, not native physics or a general dynamic navmesh; engine collision and performance remain Quest checks. Office's original behavior is unchanged.
