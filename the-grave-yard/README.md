# The Grave Yard

A cooperative GRAB horror level for up to ten players: survive five zombie hunts, carry the golden skull to the gate pedestal, release it into the socket, and enter the finish chamber.

Current title: **The Grave Yard [Spectator view 3]**. Revision 2 adds staged exit instructions, a gold release ring, green route lights, and 8m perimeter walls with a transparent collision cap. Local checks pass; headset retesting is pending.

Current title: **The Grave Yard [Spectator view 3]**. The east perimeter and spectator gallery glass are transparent, so eliminated players can walk along the gallery and watch survivors. The tall viewing barrier remains solid.

## Play and load

Download [the native level](dist/the-grave-yard.level) using GitHub's **Download raw file** action. Copy it to GRAB's `levels/user` folder on the Quest, preserving the `.level` extension. Open it from your local levels in GRAB. The JSON and scene specification are development sources, not the file to copy into the game.

- Each rest and hunt lasts 60 seconds. After exactly five hunts, the zombie stops and the golden skull becomes available.
- Three climbable trees carry protective gems. **Only holding a gem protects you.** Climbing alone gives no immunity.
- Captured players move to the spectator room; surviving players continue. If everyone dies, a five-second countdown resets the round.
- Follow the gate’s objective signs: survive five hunts, grab the skull from the labeled north pedestal, then carry it to the gold ring beside the exit. **Release the skull inside the ring**; merely holding or touching it nearby does not open the gate.
- Once the gate opens, follow the green floor lights through the supported chamber and touch the native green finish block six meters past the gate.
- Perimeter walls are now 8m tall, nongrabbable and nongrapplable, with sealed corners/gate header and a transparent collision cap above all tree branches. The outdoor moon remains visible; verify containment on Quest before children play.

## Build and check

From the repository root:

```sh
python -m pip install -r the-grave-yard/requirements.txt
python the-grave-yard/src/build.py
python -m unittest discover -s the-grave-yard/tests -v
```

The generator emits JSON, protobuf `.level`, controller GASM and a fresh ID manifest together. [Source decisions](LEVEL-MEMORY.md), [validation evidence](docs/VALIDATION.md), [workstream status](docs/STATUS.md) and the [Quest checklist](docs/QUEST-PLAYTEST.md) describe this build.

Local format and bytecode checks do not establish actual Quest physics, networking or performance. The headset checklist remains the final in-game acceptance step.
