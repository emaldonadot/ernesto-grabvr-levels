# The Grave Yard

**Status: design/specification only — not yet a playable native GRAB level.**

A cooperative graveyard horror level with 16 graves, climbable haunted trees, jack-o'-lanterns, a full moon, a decaying zombie, five timed hunts, protective gems and a golden-skull gate puzzle.

See [requirements, decisions and workstream handoffs](LEVEL-MEMORY.md) and [scene manifest](scene-spec.json).

Native outputs to produce: `dist/the-grave-yard.level`, `dist/the-grave-yard.json`, native controllers, build scripts and validation tests. Do not treat the scene-spec JSON as an importable GRAB level.

## Implementation progress

- [Live workstream status](docs/STATUS.md)
- [Engine-independent gameplay reference](src/rules.py)
- [Gameplay unit tests](tests/test_rules.py)

Run reference tests from this folder with `python -m unittest discover -s tests -v`. These tests have been authored but not executed in a checked-out repository environment. They do not validate native GRAB runtime behavior.
