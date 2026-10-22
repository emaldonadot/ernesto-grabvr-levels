# Office After Hours

**Experimental GRAB level prototype. Earlier builds tested by Ernesto on Quest; revision 4 awaits headset testing.**

Designed for **10 simultaneous players**. Ten furnished offices surround a central corridor. Search drawers for three protective gems, hide in closets or under desks, survive five one-minute hunts, then find the key and unlock the exit.

## Hunt polish 4 — 2026-10-22

Replace the old `.level` and reload. The title is **Office After Hours [Hunt polish 4]**.

- Hunt fog explicitly clears to density **zero** with an instant native ONLEAVE ambience target. A separate calm trigger also clears it, and each client refreshes the clear every 0.5 seconds during calm/reset phases.
- A native particle emitter attached to the monster produces 18 soft gray puffs/second. Puffs rise, expand and fade, with lifetimes no longer than one second. The emitter follows the monster and moves below the map when it disappears.
- Unclaimed gems stay seated in their assigned moving drawer. The first valid pickup releases that seating behavior for the rest of the gem epoch. Carrying, dropping and throwing then use native physics. Hunt-end relocation resets the seating latch in three new drawers.
- **Active hiding always protects you**, including when the monster saw you enter. The AI excludes hidden players from targeting and rechecks hiding immediately before a kill. A short entry debounce prevents the inside leave pad from immediately canceling entry. Desk hiding no longer cancels just because the headset is above the desktop; crouch for the intended visual cover, and leave with the pad or by walking out.
- Monster speed increases **3.1 → 3.4m/s**, about 10%, while keeping movement-facing rotation.

The prior office/closet animations, 60s calm/60s hunt timing, five-second all-dead round restart, key-gated exit and spectator balcony remain in place. Holding a gem grants immunity; releasing it ends protection. Carrier identification remains a held-state/nearest-hand heuristic, so close handoffs need headset verification.

**35 local checks pass. These are bytecode/serialized-data checks with synthetic physics and animation endpoints, not a GRAB engine playtest.**

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

Touch blue office-door buttons and drawer handles to toggle them. Grab gems directly; touch inside an open drawer to collect the inventory key. Blue pads enter hiding; the inside pad leaves after the short entry debounce. One player fits in each spot. Hidden players cannot be targeted or killed, even if their entry was seen. Touch the exit lock while carrying the key; it triggers the exit hinge animation and survivors can leave. Dead players watch from the balcony and cannot collect loot, hide, unlock or finish.

The first minute is calm; hunts then alternate with calm minutes. The fifth hunt ends at 10:00, spawning the key. All players dying starts a five-second countdown and a fresh round. Reload also starts over.

## Build and verify

Python 3.12+ with `protobuf` is required; `grpcio-tools` regenerates Python bindings if the schema changes. The checked-in binding was produced with protobuf compiler 7.35.1 / grpcio-tools 1.84.0 (runtime 7.36.2). Install matching dependencies in an isolated environment, then:

```sh
python src/build.py
python -m unittest discover -s tests -v
```

`src/render.py` additionally uses matplotlib. Run it to rebuild the geometry preview.

Thirty-five gameplay and native-contract regression tests pass in the included local harness. The harness assumes immediate connection writes, writable shared player variables and second-based DeltaTime. Native animation targets are checked with an endpoint model; the harness does not emulate engine animation timing, networking, collision, rendering, or VR tracking. Read `LEVEL-MEMORY.md` before treating the prototype as release-ready, particularly its native physics, multiplayer and furniture-navigation limitations.

## Repository

This game lives in the `office-after-hours/` folder of [ernesto-grabvr-levels](https://github.com/emaldonadot/ernesto-grabvr-levels). Clone the repository and enter this folder before building or testing.

## Third-party format reference

`vendor/grab.proto` comes from the GRAB Tools repository; its upstream license is included. Geometry, game-specific source and tests were created for this project. No upstream editor implementation is bundled.
