# Grave Yard validation — grave-yard-1

Local checks completed on 2026-10-22. **22 tests passed** using Python 3.12 and protobuf 7.36.2:

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
| Pursuit | Representative marker detour reaches target without entering inflated obstacle rectangles |

Coordinator also confirmed a deterministic rebuild: hashes of all 13 generated native artifacts remained identical.

Generated build: 326 nodes, ten native controllers, declared complexity 5598. The complexity is the generator's value, not an observed engine measurement. Performance at ten players remains unverified.

A second build produced identical SHA-256 hashes for all 13 native/JSON/GASM/manifest artifacts.

## Limits of the evidence

The deterministic VM executes serialized native instructions with immediate writes, synthetic hand/physics state, second-based DeltaTime and animation endpoints. It enforces local-only teleport but does not simulate GRAB networking, gravity, collision response, animation timing or render performance. The physics-held signal is combined with nearest-hand proximity to estimate a holder; actual handoff/throw timing needs Quest testing.

The zombie has a 3 m head-height capture reach. It continues targeting players above that height, but cannot capture them until within physical reach. Tree climbing does not set an immunity flag. Elevated branch behavior and the reach value need headset feedback.

The coordinator attempted to open `https://grabvr.tools/editor`; the cloud browser could not create a WebGL context (`PANIC: Browser failed to create WebGL context: Error creating WebGL context.`). No level import or engine playtest occurred there. [Quest acceptance checks](QUEST-PLAYTEST.md) remain pending, including actual completion on each client, late joins, host migration and full-map collision behavior.
