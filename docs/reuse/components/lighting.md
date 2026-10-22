# Lights, signs and visual language

Pattern `lighting.office.v1`. Sources: [generator: HallLight, RoomLight, Screen, pads and sign helper](../../../office-after-hours/src/build.py), [native light schema](../../../office-after-hours/vendor/grab.proto), [atmosphere](atmosphere.md).

## Three separate systems

| System | Current use | Reuse implication |
| --- | --- | --- |
| Neon static geometry | Hall/room fixtures, screens, eyes, pads | `isNeon=True` makes visible emissive-looking surfaces; do not describe it as a native point/spot light illuminating neighbors |
| Global/client ambience | Calm/hunt sky color, ambient brightness, fog | Give one phase controller ownership; restore every changed setting on exit/reset |
| `LevelNodeLight` | Available in schema; **not instantiated by Office** | A future point/spot implementation needs rendering/performance validation; it is not an existing reusable Office light builder |

Native light schema exposes position, rotation, type POINT 0 / SPOT 1, color, intensity, range, angle, optional distance/cone falloff shapes and creation order. Merely having these fields does not establish a tested configuration or performance budget.

## Office defaults

- Hall fixtures: `(1.4,0.06,0.5)` at Y=3.44; room fixtures `(1.6,0.06,0.45)` at Y=3.44. Both use neon static colored cubes.
- Cyan/blue means door/hiding interaction; amber means closet opening; green means exit guidance; pink/green/purple distinguish gems. These are game conventions, not engine behavior.
- `sign()` creates neon signs with `hideModel=True`, explicit yaw, scale and color. It is used for rules, room numbers, countdowns and red overhead dead markers.
- Calm ambient brightness 0.7, hunt 0.35; see the atmosphere component for restoration. Ceiling and spectator floor/walls use transparency to permit viewing.

## Reuse

Declare the new game’s color semantics, fixture spacing, readable signs and ambience palette in its configuration/memory. Separate collidable fixture geometry from any decorative surface where necessary. Rotate signs toward the intended approach; check legibility at seated/standing height and under hunt fog. Countdown visibility and marker orientation are not a guaranteed HUD/billboard system. True dynamic lights, transparent visibility, sign readability and Quest draw cost remain engine checks; scene appearance alone does not verify native illumination.
