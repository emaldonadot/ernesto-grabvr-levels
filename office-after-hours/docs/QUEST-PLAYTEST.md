# Quest acceptance checklist

Status: Native animation 2 awaits headset testing. Ernesto confirmed that the previous monster appears and follows him in solo play mode, but doors/drawers still failed. Replace the file and verify the new title before testing. Start solo, then two headsets, then TEN players.

- [ ] Level loads in the in-game editor without unsupported-format or program errors.
- [ ] Exactly ten offices have desk, chair, closet, door and drawer; doors start closed.
- [ ] Doorways, standing height, seated height and closet/desk teleports are comfortable.
- [ ] Blue door buttons directly start hinge animations; all ten doors swing 90 degrees around their frame edge and close on the next touch. Withdraw hands between touches.
- [ ] Drawer handles slide with trays by 0.7m; repeated touches close them. No runaway loops, per-frame snapping, or stuck triggers.
- [ ] Closed drawers conceal contents; open drawers allow contents pickup.
- [ ] Three physical gems start in distinct drawers without penetrating desktops or tray walls.
- [ ] Grab, carry, drop and throw each gem. It collides with floor/walls and moves when an animated drawer pushes it.
- [ ] Released gems do not snap to drawers/players. After each hunt all three relocate, including held gems; no stale grips or retained launch velocity.
- [ ] Hand-state carrier detection handles left/right hands, two gems in one player’s hands, adjacent hands and passing a gem between players. No nearby non-holder gains immunity.
- [ ] First fog/monster phase starts at 1:00 and lasts until 2:00, then repeats every two minutes.
- [ ] Native fog force controls correctly fade in/out on both headsets.
- [ ] Held-gem carriers are ignored; releasing/throwing immediately removes immunity. Test pickup during a chase.
- [ ] Safe hiding is ignored. Observed hiding remains vulnerable. Review and replace approximate visibility if inaccurate.
- [ ] Two simultaneous hiding requests cannot claim the same space. Vacated/dead/disconnected occupants release it.
- [ ] Leaving a hiding volume or standing up under a desk cancels hiding.
- [ ] Monster travels through doorways without crossing partition walls; correct furniture overlap before release.
- [ ] Monster cannot catch through walls or across height differences; add a final occlusion check before release.
- [ ] Death shows a marker and moves the LOCAL player (including a non-host) to the enclosed viewing balcony. The transparent ceiling/floor allow spectating.
- [ ] Dead spectators cannot leave the enclosure or reach physical gems; the monster ignores them.
- [ ] Dead spectators cannot collect gems/key, occupy hiding spaces, unlock the exit, or finish.
- [ ] Key appears after the fifth completed hunt (10:00) and never earlier.
- [ ] Killing/disconnecting the key holder moves the key to a DIFFERENT drawer.
- [ ] Key unlocks the exit; surviving players complete by crossing it. Unkeyed and dead players cannot trigger completion.
- [ ] Late join, host departure, reconnect and shared-state migration are correct or blocked with a clear ready-up policy.
- [ ] Frame rate, draw cost, shared-code performance and official complexity fit the target Quest/player count.
- [ ] Reload resets all game state. Add ready-up / all-dead restart before public release if desired.

Local checks already run: protobuf encode/decode equality; 1-based depth-first node references; instruction operand bounds and destination permissions; twenty gameplay/native-contract regressions with synthetic hand/physics states and an animation endpoint model. These do not satisfy the engine checks above.
