# Quest acceptance checklist

This checklist requires GRAB on a Quest. No headset checks are recorded as completed by the local automated tests.

## Import and scene

- Import `dist/the-grave-yard.level`; confirm the title, spawn, 16 graves, walkable lanes, six climbable trees, four lit pumpkins, three candles, round moon and clouds.
- Walk all fence edges and the exit chamber floor; confirm no gaps, unintended falls or route out of the spectator room.
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
- After hunt five, hold the skull in the pedestal socket: gate stays closed. Release outside: gate stays closed. Release inside: gate opens.
- Drop the skull outside the map and disconnect its holder; confirm recovery.
- Verify each surviving client can reach and trigger native completion. Dead players must not finish from the spectator room.

Record device, GRAB version, player count, observed result and any failure coordinates when reporting feedback.
