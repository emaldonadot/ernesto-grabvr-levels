# Office After Hours

**Experimental GRAB level prototype. Monster pursuit confirmed by Ernesto in solo play; revised interactions await headset testing.**

Designed for **10 simultaneous players**. Ten furnished offices surround a central corridor. Search drawers for three protective gems, hide in closets or under desks, survive five one-minute hunts, then find the key and unlock the exit.

## Native animation 2 — 2026-10-21

Replace the old `.level` and reload. The title is **Office After Hours [Native animation 2]**.

- Touch the blue button beside an office door. It directly triggers a native 90-degree hinge animation. Withdraw your hand and touch again to close.
- Touch a drawer handle. Its native animation slides the tray 0.7m; its trigger moves with the handle. Touch again to close.
- Gems are small, solid, grabbable shared physics objects. Grab, carry, release and throw them normally. Walls and moving trays can collide with them; code does not pin them to drawers or players.
- Immunity applies while a gem is held and ends on release. Carrier detection uses physics state plus the nearest living hand within 28cm because the exposed GASM interface has no holder ID. Closely overlapping hands and multiplayer handoffs need real-device validation.
- After each hunt, gems return to three distinct randomly selected drawers, including carried/thrown gems. Out-of-bounds gems recover to their assigned drawer.
- Eliminated players move to an enclosed observation balcony with a dead marker. Physical separation keeps them away from gems; AI and scripted gameplay ignore them. The ceiling and balcony floor are transparent for viewing.

Ernesto confirmed that the previous build's monster appears and follows him in play mode, but its doors and drawers still did not work. This revision replaces that interaction path. **Native animation, physics collisions and carrier detection have not yet been confirmed on a headset.**

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

Touch blue office-door buttons and drawer handles to toggle them. Grab gems directly; touch inside an open drawer to collect the inventory key. Blue pads enter hiding; the inside pad leaves. One player fits in each spot. Touch the exit lock while carrying the key; it triggers the exit hinge animation and survivors can leave. Dead players watch from the balcony and cannot collect loot, hide, unlock or finish.

The first minute is calm; hunts then alternate with calm minutes. The fifth hunt ends at 10:00, spawning the key. Reload the map for a new round.

## Build and verify

Python 3.12+ with `protobuf` is required; `grpcio-tools` regenerates Python bindings if the schema changes. The checked-in binding was produced with protobuf compiler 7.35.1 / grpcio-tools 1.84.0 (runtime 7.36.2). Install matching dependencies in an isolated environment, then:

```sh
python src/build.py
python -m unittest discover -s tests -v
```

`src/render.py` additionally uses matplotlib. Run it to rebuild the geometry preview.

Twenty gameplay and native-contract regression tests pass in the included local harness. The harness assumes immediate connection writes, writable shared player variables and second-based DeltaTime. Native animation targets are checked with an endpoint model; the harness does not emulate engine animation timing, networking, collision, rendering, or VR tracking. Read `LEVEL-MEMORY.md` before treating the prototype as release-ready, particularly its witnessed-hiding and furniture-navigation limitations.

## Repository

This game lives in the `office-after-hours/` folder of [ernesto-grabvr-levels](https://github.com/emaldonadot/ernesto-grabvr-levels). Clone the repository and enter this folder before building or testing.

## Third-party format reference

`vendor/grab.proto` comes from the GRAB Tools repository; its upstream license is included. Geometry, game-specific source and tests were created for this project. No upstream editor implementation is bundled.
