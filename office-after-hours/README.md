# Office After Hours

**Experimental GRAB level prototype. Not yet play-tested in GRAB or on Meta Quest.**

Designed for **10 simultaneous players**. Ten furnished offices surround a central corridor. Search drawers for three protective gems, hide in closets or under desks, survive five one-minute hunts, then find the key and unlock the exit.

## Interaction fix 1 — 2026-10-21

Replace the older `.level` with the current download and reload the level. The in-game title is **Office After Hours [Interaction fix 1]**. Touch the door/drawer handles with a VR hand, then withdraw the hand before touching again to toggle closed.

The original file used an incomplete native connection layout: 27 player slots rather than 28, four trigger slots rather than six, and misplaced teleport/velocity slots. This revision uses a layout independently extracted from a GRAB-exported level, preserves unused slots, and explicitly links each interaction trigger to its controller using native START targets. The local VM now rejects the old incomplete layouts. **The repair has not yet been confirmed on a headset.**

## Files

- `dist/office-after-hours.level` — native protobuf level, format 25.
- `dist/office-after-hours.json` — editable representation of the same level.
- `docs/office-after-hours-preview.png` — floor plan and software-rendered geometry cutaway.
- `src/build.py` — procedural geometry, native GASM generation and serialization.
- `src/*.gasm` — generated human-readable native programs; regenerate from `build.py` after edits.
- `tests/` — interpreter and gameplay regression tests executing the serialized GASM instructions.
- `LEVEL-MEMORY.md` — requirements, decisions, state contract and current limitations.
- `docs/QUEST-PLAYTEST.md` — required in-game acceptance checks.

## Load in GRAB

Back up your existing levels. Put `office-after-hours.level` in your own GRAB level folder, then open it in the in-game editor. The format documentation identifies Quest's game data directory as `Android/data/com.slindev.grab` (or `com.slindev.grab_demo`) and the relative level folder as `levels/user`. Android restrictions may require your usual Quest file-transfer method. Windows uses `Documents/GRAB/levels/user`.

You can also open the `.level` in https://grabvr.tools/editor on a browser with WebGL. The editable JSON is included as a second route. Save from the actual in-game editor before publishing. This project does not install anything on your headset or upload a public level.

## Controls

Touch office door and drawer handles to toggle them. Open a drawer and touch inside it to collect its contents. Blue pads enter hiding; the inside pad leaves hiding. One player fits in each spot. Gems float above their owners and protect them until the next relocation. Touch the exit lock while holding the key; survivors can then pass through the exit. Dead players remain in the scene with a red overhead marker, but their scripted interactions are ignored.

The first minute is calm; hunts then alternate with calm minutes. The fifth hunt ends at 10:00, spawning the key. Reload the map for a new round.

## Build and verify

Python 3.12+ with `protobuf` is required; `grpcio-tools` regenerates Python bindings if the schema changes. The checked-in binding was produced with protobuf compiler 7.35.1 / grpcio-tools 1.84.0 (runtime 7.36.2). Install matching dependencies in an isolated environment, then:

```sh
python src/build.py
python -m unittest discover -s tests -v
```

`src/render.py` additionally uses matplotlib. Run it to rebuild the geometry preview.

Seventeen gameplay and native-contract regression tests pass in the included local harness. The harness assumes immediate connection writes, writable shared player variables and second-based DeltaTime. It does not emulate GRAB networking, collision, rendering, or VR tracking. Read `LEVEL-MEMORY.md` before treating the prototype as release-ready, particularly its witnessed-hiding and furniture-navigation limitations.

## Repository

This game lives in the `office-after-hours/` folder of [ernesto-grabvr-levels](https://github.com/emaldonadot/ernesto-grabvr-levels). Clone the repository and enter this folder before building or testing.

## Third-party format reference

`vendor/grab.proto` comes from the GRAB Tools repository; its upstream license is included. Geometry, game-specific source and tests were created for this project. No upstream editor implementation is bundled.
