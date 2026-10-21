# Validation — Native animation 2

2026-10-21: twenty gameplay/native-contract tests PASS; binary protobuf encode/decode equality PASS. Build: 669 nodes, 34 code blocks, estimated complexity 5,177.

Ernesto confirmed solo play mode: monster appears and follows him, but the preceding build’s doors/drawers still did not open. The current revision replaces their motion path with direct native animation targets.

Validated locally:

- All ten door buttons resolve directly to non-looping TOGGLE_REVERSE hinge animations. Group origins lie on the door edge; panels swing +/-90 degrees into offices.
- All ten drawer handles resolve directly to slide animations and move with the tray hierarchy. No Office GASM writes door/drawer transforms each frame.
- Key authorization forces the native exit hinge animation; ordinary exit contact without a key does not unlock it.
- Three shared physics groups contain collidable, grabbable gem geometry. Their 0.14m size fits the drawer cavity. Gem code positions them only on relocation/recovery, leaving normal native carry/throw/collision movement alone.
- Synthetic held physics state plus hand positions grants immunity; release clears immunity. Dead players receive no immunity. Hunt completion relocates three gems into distinct drawers.
- A non-shared controller selects the local dead player and places them in an enclosed spectator balcony. AI and scripted loot/hiding/exit reject dead players.
- Existing hiding occupancy, witnessed hiding, timing, key death/respawn, escape and ten-player eligibility checks pass.
- Existing independent 28-slot player / six-slot trigger connection fixture checks pass.

**Limitations:** The local harness models animation endpoints and synthetic physics/hand states. It does not run GRAB’s animation timing, collision solver, grip system, multiplayer synchronization or headset tracking. Carrier identification is a nearest-hand heuristic (held state plus 28cm radius), not an authoritative native holder ID. Native physics disable/re-enable during relocation, gem velocity reset, handoffs, moving-tray collisions and non-host spectator teleport all require headset validation. This is not a confirmed headset interaction fix.
