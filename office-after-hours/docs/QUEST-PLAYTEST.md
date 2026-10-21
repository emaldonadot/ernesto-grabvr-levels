# Quest acceptance checklist

Status: Interaction fix 1 has NOT been tested on a headset. The original build was tested by Ernesto and had nonworking interactions. Use an unpublished copy. Start with two headsets, then test a full TEN-player session before release.

- [ ] Level loads in the in-game editor without unsupported-format or program errors.
- [ ] Exactly ten offices have desk, chair, closet, door and drawer; doors start closed.
- [ ] Doorways, standing height, seated height and closet/desk teleports are comfortable.
- [ ] Every door and drawer toggles from both relevant approach positions without repeat firing.
- [ ] Closed drawers conceal contents; open drawers allow contents pickup.
- [ ] Three gems occupy distinct drawers; no player can claim multiple gems.
- [ ] First fog/monster phase starts at 1:00 and lasts until 2:00, then repeats every two minutes.
- [ ] Native fog force controls correctly fade in/out on both headsets.
- [ ] Gem carriers are never selected or caught, including pickups during a chase.
- [ ] Safe hiding is ignored. Observed hiding remains vulnerable. Review and replace approximate visibility if inaccurate.
- [ ] Two simultaneous hiding requests cannot claim the same space. Vacated/dead/disconnected occupants release it.
- [ ] Leaving a hiding volume or standing up under a desk cancels hiding.
- [ ] Monster travels through doorways without crossing partition walls; correct furniture overlap before release.
- [ ] Monster cannot catch through walls or across height differences; add a final occlusion check before release.
- [ ] Death keeps the player present, shows their marker, removes targeting and blocks every gameplay interaction.
- [ ] Dead spectators cannot collect gems/key, occupy hiding spaces, unlock the exit, or finish.
- [ ] Key appears after the fifth completed hunt (10:00) and never earlier.
- [ ] Killing/disconnecting the key holder moves the key to a DIFFERENT drawer.
- [ ] Key unlocks the exit; surviving players complete by crossing it. Unkeyed and dead players cannot trigger completion.
- [ ] Late join, host departure, reconnect and shared-state migration are correct or blocked with a clear ready-up policy.
- [ ] Frame rate, draw cost, shared-code performance and official complexity fit the target Quest/player count.
- [ ] Reload resets all game state. Add ready-up / all-dead restart before public release if desired.

Local checks already run: protobuf encode/decode equality; 1-based depth-first node references; instruction operand bounds and destination permissions; ten scalar GASM gameplay regressions. These do not satisfy the engine checks above.
