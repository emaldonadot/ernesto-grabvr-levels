# Grave Yard validation — grave-yard-3

Local checks completed on 2026-10-23. **31 tests passed** using Python 3.12 and protobuf 7.36.2:

```sh
python the-grave-yard/src/build.py
python -m unittest discover -s the-grave-yard/tests -v
```

| Evidence | Result |
| --- | --- |
| Native format 25 JSON/protobuf | Parse and binary round-trip passed |
| Native connections | Player 28-slot directions, six-slot triggers, two-slot physics, complete indices and target references passed |
| Phase bytecode | Five 60-second hunts with 60-second rests; no sixth hunt |
| Protection/capture | Held owner tracked, release clears protection, reachable climber captured despite legacy hiding flag, elevated target remains selected |
| Skull bytecode | Locked before fifth hunt; held socket proximity insufficient; living-holder release in socket unlocks; wrong X/Y and dead holder rejected; lost skull recovered |
| Round bytecode | Five-second wipe, fresh calm, survivor/escaped player prevents wipe |
| Client movement | Teleport writes confined to non-shared LocalMovement; nonhost spectator and epoch revival tested with local-only teleport model |
| Atmosphere | Local hunt fog clears after hunt |
| Geometry | Six trees, 16 epitaphs/graves, four pumpkins, three candles; enclosed finish floor overlaps gate approach |
| Exit guidance | Staged locked/ready/picked-up/open signs follow actual physical skull release; two synthetic players walk to finish without teleport; larger trigger-box corners do not set escaped status |
| Containment | 8m solid nongrabbable/nongrapplable slabs exceed all tree geometry; sampled side/front/back coverage including closed gate/header at six heights; corners and transparent cap overlap |
| Path | Gold release ring and green route lights are passable; finish-room lights remain above continuously supported floor |
| Pursuit | Representative marker detour reaches target without entering inflated obstacle rectangles |

Coordinator also confirmed a deterministic rebuild: hashes of all generated native artifacts remained identical.

Generated build: 343 nodes, eleven native controllers, declared complexity 5679. The complexity is the generator's value, not an observed engine measurement. Performance at ten players remains unverified.

A second build produced identical SHA-256 hashes for all native/JSON/GASM/manifest artifacts.

The top-view software preview was rebuilt and inspected. It omits the faint safety cap and overlays the supported green route through the roofed chamber. Gate signage is at Z=-27.6 inside the wall’s inner face (-27.8), avoiding obstruction by the new header.

## Limits of the evidence

The deterministic VM executes serialized native instructions with immediate writes, synthetic hand/physics state, second-based DeltaTime and animation endpoints. It enforces local-only teleport but does not simulate GRAB networking, gravity, collision response, animation timing or render performance. The physics-held signal is combined with nearest-hand proximity to estimate a holder; actual handoff/throw timing needs Quest testing.

The 8m enclosure and transparent cap are checked as serialized geometry, not simulated collision. Verify wall/corner/cap contact, high tree launches, the closed gate seam, roof bypasses and spectators in GRAB; no universal escape-proof guarantee is established by local checks.

The zombie has a 3 m head-height capture reach. It continues targeting players above that height, but cannot capture them until within physical reach. Tree climbing does not set an immunity flag. Elevated branch behavior and the reach value need headset feedback.

The coordinator attempted to open `https://grabvr.tools/editor`; the cloud browser could not create a WebGL context (`PANIC: Browser failed to create WebGL context: Error creating WebGL context.`). No level import or engine playtest occurred there. [Quest acceptance checks](QUEST-PLAYTEST.md) remain pending, including actual completion on each client, late joins, host migration and full-map collision behavior.

Spectator revision 3: transparent east perimeter plus low-alpha gallery glass restore visual access through the formerly opaque 8m wall. Two additional checks verify transparent, solid, nongrabbable layers along the whole gallery and nonhost spectator separation without moving a survivor. Headset visibility/rendering remains pending.
