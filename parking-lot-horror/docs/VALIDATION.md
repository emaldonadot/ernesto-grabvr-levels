# Validation — Parking Lot Horror [1]

**Final local result:** 17 tests pass. Generated 778 nodes and 11 native controllers; conservative complexity estimate 2505 (actual game recalculation and Quest performance pending).

Local checks: generated JSON parses into native format25 protobuf; serialized `.level` round-trips exactly. Fresh depth-first object IDs, native trigger/animation target references and complete native connection slots are checked. Deterministic scalar bytecode VM covers phase timing, capped five hunts, key timing/ownership/recovery, safe hiding and occupancy, walking out, local and non-host movement intent, held/released gems, capture/spectators, fog restoration, all-dead reset and native door endpoints. Scene, vehicle and skeleton software previews are generated from actual primitive geometry.

Run `python -m unittest discover -s parking-lot-horror/tests -v` from repository root. Test assumptions live in `tests/native_vm.py`. They do not emulate GRAB physics, rendering, networking or smooth animation timing.

The browser opened GRAB Tools editor on 2026-10-22 but failed to create a WebGL context. No native editor import/render test was completed. No Quest playtest is claimed.

## Required Quest checks

- Load the new `.level` in user levels. Verify readable parking lines, sixty bays, columns, opaque covered ceiling, all nine vehicles and recognizable motorcycle/trike/SUV/sport/minivan silhouettes.
- Inspect skull, ribs, pelvis, limbs, skeleton size/facing/fumes. Check frame rate with ten clients and confirm current game accepts recalculated complexity.
- Open/close all four driver doors and both sliding doors. Confirm useful reach and swing/slide clearance, physical gems visible/reachable after opening, no gem sinking.
- Test van entry while crouched, automatic close, inside exit, occupancy, walking out and denial to another player. Confirm monster never captures a hidden player.
- Hold/release/throw each gem on two clients: only the living current holder gains immunity. Spectators cannot take shared loot through gallery windows.
- Observe 60 s calm/60 s hunt; fog appears during hunts and clears at each end. Monster disappears at 60 s, residual particles fade within 1 s. No sixth attack after fifth.
- Verify pursuit across all three aisles/side lanes and vehicle clearance. Capture on touch dispatches each client's own player to side gallery; view into garage is unobstructed.
- After fifth hunt, collect gold key only at pedestal, unlock gate, cross north opening and finish on each client. Death/disconnect of key owner restores pedestal key.
- Eliminate everyone:5-to-1 reset countdown, every client returns to spawn, doors/gems reset and fresh 60 s calm. Empty lobby/escaped player does not cause wipe reset.
- Test late join, disconnect/reconnect, host migration and up to ten simultaneous players. This is a ten-player design target, not yet a verified multiplayer guarantee.
