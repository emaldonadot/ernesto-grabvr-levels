# The Grave Yard

A cooperative GRAB horror level for up to ten players: survive five zombie hunts, carry the golden skull to the gate pedestal, release it into the socket, and enter the finish chamber.

## Play and load

Download [the native level](dist/the-grave-yard.level) using GitHub's **Download raw file** action. Copy it to GRAB's `levels/user` folder on the Quest, preserving the `.level` extension. Open it from your local levels in GRAB. The JSON and scene specification are development sources, not the file to copy into the game.

- Each rest and hunt lasts 60 seconds. After exactly five hunts, the zombie stops and the golden skull becomes available.
- Three climbable trees carry protective gems. **Only holding a gem protects you.** Climbing alone gives no immunity.
- Captured players move to the spectator room; surviving players continue. If everyone dies, a five-second countdown resets the round.
- Carry the golden skull to the pedestal beside the exit and release it inside the socket. Merely holding it nearby does not open the gate.
- Once the gate opens, living players enter the enclosed chamber and touch the native finish block.

## Build and check

From the repository root:

```sh
python -m pip install -r the-grave-yard/requirements.txt
python the-grave-yard/src/build.py
python -m unittest discover -s the-grave-yard/tests -v
```

The generator emits JSON, protobuf `.level`, controller GASM and a fresh ID manifest together. [Source decisions](LEVEL-MEMORY.md), [validation evidence](docs/VALIDATION.md), [workstream status](docs/STATUS.md) and the [Quest checklist](docs/QUEST-PLAYTEST.md) describe this build.

Local format and bytecode checks do not establish actual Quest physics, networking or performance. The headset checklist remains the final in-game acceptance step.
