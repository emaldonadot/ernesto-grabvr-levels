# Quest acceptance checklist

This checklist requires GRAB on a Quest. No headset checks are recorded as completed by the local automated tests.

## Import and scene

- Import `dist/the-grave-yard.level`; confirm title **The Grave Yard [2]**, spawn, 16 graves, walkable lanes, six climbable trees, four lit pumpkins, three candles, round moon and clouds.
- Walk all 8m fence edges, corners, gate posts/header and the exit chamber floor; confirm no gaps, unintended falls or route out of the spectator room. Try climbing/launching from all six trees toward the perimeter and transparent safety cap. Verify the cap collides, the moon remains visible and no route over the closed gate or finish-room roof exists.
- Climb each gem tree. Check that the gems can be reached, grabbed, released and thrown.

## Zombie and timing

- First hunt begins after 60 seconds, lasts 60 seconds, then fog clears. Repeat through hunt five; wait another two minutes and confirm no sixth attack.
- Confirm zombie emerges from the open grave, limbs walk, green fumes follow it, and the actor returns to rest between hunts.
- Lead it around both sides of stones and tree trunks. Check collision clearance, direction changes and pursuit speed.
- Confirm unprotected players remain eligible while climbing; check reachable elevated capture without teleporting the zombie through solid geometry.
- Hold a gem during pursuit, then release it. Confirm protection ends on release and the zombie can capture you.

## Multiplayer and reset

- Test host and a second Quest first, then the ten-player target. Capture each client and verify only that client's player moves into the spectator room.
- A survivor continues while dead players spectate. A five-second all-dead reset returns every client to spawn with a full calm period.
- Check that reset closes the gate, hides the finish, restores gems/skull, clears fog and resets the hunt count.
- Test late join during rest, hunt and wipe countdown; disconnect a gem holder; test host migration.
- Check smooth frame rate at target player count and record GRAB's actual complexity value.

## Skull and completion

- Before hunt five ends, confirm the skull cannot unlock the gate.
- Gate instructions change from locked to skull ready after hunt five. Grab the skull at its labeled north pedestal and confirm picked-up/release instructions. Hold it in the glowing gold ring: gate stays closed. Release outside: gate stays closed. Release inside: gate opens and instructions turn green.
- Drop the skull outside the map and disconnect its holder; confirm recovery.
- Follow green floor lights through the gate and across the supported chamber to the native green finish six meters beyond the door. Verify each surviving client can reach and trigger native completion without teleport. Dead players must not finish from the spectator room.

Record device, GRAB version, player count, observed result and any failure coordinates when reporting feedback.

- With a survivor in the yard, eliminate a second player. From the spectator gallery, verify survivors are visible through both the clear gallery wall and the tall east boundary. Walk along the gallery to follow them. Check both headsets, tree/gravestone occlusion, collision at the glass, and no access to shared props through it.
