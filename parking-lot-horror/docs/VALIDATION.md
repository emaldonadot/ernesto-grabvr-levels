# Validation — Parking Lot Horror [2]

**Final local result:** 27 tests pass. Generated 808 nodes and 12 native controllers; conservative complexity estimate 7061 (actual game recalculation and Quest performance pending).

Local checks: generated JSON parses into native format25 protobuf; serialized `.level` round-trips exactly. Fresh depth-first object IDs, native trigger/animation target references and complete native connection slots are checked. Deterministic scalar bytecode VM covers phase timing, capped five hunts, key timing/ownership/recovery, safe hiding and occupancy, walking out, local and non-host movement intent, held/released gems, capture/spectators, fog restoration, all-dead reset and native door endpoints. Independent ground-path checks exercise direct diagonal motion, routes around cars/columns and across multiple rows, moving targets, swept obstacle clearance, roof/interior capture denial and hunt termination during different instruction slices with ten simulated players. Twenty-five additional valid random start/target pairs were audited locally for reachability within one 60-second hunt. Door tests inspect all six serialized glass/frame/handle assemblies and reject fixed panes covering their openings. Exit tests verify floor continuity, the enclosed room, a gate aligned with the real wall opening, native finish activation after unlock, no premature escape bookkeeping and no off-map exit teleport. Scene, vehicle and skeleton software previews are generated from actual primitive geometry.

Run `python -m unittest discover -s parking-lot-horror/tests -v` from repository root. Test assumptions live in `tests/native_vm.py`. They do not emulate GRAB physics, rendering, networking or smooth animation timing.

Revision 2 uses more native instructions for swept obstacle checks; its estimate of 7061 is not a verified current game complexity limit or a Quest performance measurement.

The browser opened GRAB Tools editor on 2026-10-22 but failed to create a WebGL context. No native editor import/render test was completed. Ernesto inspected build 1 on Quest and said the overall appearance looks great; he reported the three issues addressed in revision 2. No headset verification of revision 2 is claimed.

## Required Quest checks

- Load the new `.level` in user levels. Verify readable parking lines, sixty bays, columns, opaque covered ceiling, all nine vehicles and recognizable motorcycle/trike/SUV/sport/minivan silhouettes.
- Inspect skull, ribs, pelvis, limbs, skeleton size/facing/fumes. Check frame rate with ten clients and confirm current game accepts recalculated complexity.
- Open/close all four driver doors and both sliding doors. Confirm glass, frame, mirror and actual handles move with each door, no stationary pane remains in the doorway, useful reach and swing/slide clearance, physical gems visible/reachable after opening, no gem sinking.
- Test van entry while crouched, automatic close, inside exit, occupancy, walking out and denial to another player. Confirm monster never captures a hidden player.
- Hold/release/throw each gem on two clients: only the living current holder gains immunity. Spectators cannot take shared loot through gallery windows.
- Observe 60 s calm/60 s hunt; fog appears during hunts and clears at each end. Monster disappears at 60 s, residual particles fade within 1 s. No sixth attack after fifth.
- Verify direct diagonal pursuit through empty stalls and routes around all car bodies, conservative open-door envelopes and columns. Verify the skeleton cannot climb roofs, cross vehicles or capture through a car. Capture on touch dispatches each client's own player to side gallery; view into garage is unobstructed.
- After fifth hunt, collect gold key only at pedestal, unlock gate, walk through the raised gate into the enclosed exit room, then physically touch the native finish block and confirm GRAB marks the level completed on each client. Check floor continuity and that the full-height locked gate seals the wall opening. No exit teleport should occur. Death/disconnect of key owner restores pedestal key.
- Eliminate everyone:5-to-1 reset countdown, every client returns to spawn, doors/gems reset and fresh 60 s calm. Empty lobby/escaped player does not cause wipe reset.
- Test late join, disconnect/reconnect, host migration and up to ten simultaneous players. This is a ten-player design target, not yet a verified multiplayer guarantee.
