# Quest acceptance checklist

Status: **Hunt polish 4** awaits headset testing. Ernesto confirmed the prior revision’s office doors work and solo monster pursuit works. Replace the file and check the new title. Test solo, then two headsets, then TEN players.

- [ ] Level loads in the in-game editor without unsupported-format or program errors.
- [ ] Exactly ten offices have desk, chair, closet, door and drawer; doors start closed. Closet backs touch exterior walls and their fronts face into rooms.
- [ ] All amber closet buttons toggle hinged doors. Blue pads hide/close; leaving opens the door toward the room. One occupant per closet remains enforced.
- [ ] Doorways, standing height, seated height and closet/desk teleports are comfortable.
- [ ] Blue door buttons directly start hinge animations; all ten doors swing 90 degrees around their frame edge and close on the next touch. Withdraw hands between touches.
- [ ] Drawer handles slide with trays by 0.7m; repeated touches close them. No runaway loops, per-frame snapping, or stuck triggers.
- [ ] Closed drawers conceal contents; open drawers allow contents pickup.
- [ ] Three physical gems start in distinct drawers without penetrating desktops or tray walls.
- [ ] Open/close every occupied drawer: the unclaimed gem stays visible inside its tray, with no floor drop.
- [ ] Grab a seated gem with either hand: seating releases immediately; carry/drop/throw uses native physics and the gem does not snap back to its drawer before relocation.
- [ ] Released gems do not snap to drawers/players. After each hunt all three relocate to drawers outside the preceding set, including held gems; no stale grips or retained launch velocity.
- [ ] Hand-state carrier detection handles left/right hands, two gems in one player’s hands, adjacent hands and passing a gem between players. No nearby non-holder gains immunity.
- [ ] First fog/monster phase starts at 1:00 and lasts until 2:00, then repeats every two minutes.
- [ ] Gray hunt fog visibly reduces corridor visibility and clears completely when the monster leaves, including repeated hunts and all-dead resets, on both headsets. A late client joining during a hunt sees fog; a late client joining during calm sees no fog.
- [ ] Held-gem carriers are ignored; releasing/throwing immediately removes immunity. Test pickup during a chase.
- [ ] The monster ignores and cannot kill players in ALL ten closets and ALL ten desk hiding spots, even if it saw entry. Test entering while already being chased and nearly touched.
- [ ] Two simultaneous hiding requests cannot claim the same space. Vacated/dead/disconnected occupants release it.
- [ ] Leaving the horizontal hiding area or using the leave pad cancels hiding. Desk headset height alone does not cancel protection. The entry debounce prevents immediate accidental exit; inside leave works after 0.5 seconds.
- [ ] Monster turns its eyes along the walking direction, moves at 3.4m/s, and travels through doorways without crossing partition walls; correct furniture overlap before release.
- [ ] Gray fumes rise from and follow the moving monster, fade naturally, and disappear within a second after it leaves. Check Quest frame rate with particles active.
- [ ] Monster cannot catch through walls or across height differences; add a final occlusion check before release.
- [ ] Death shows a marker and moves the LOCAL player (including a non-host) to the enclosed viewing balcony. The transparent ceiling/floor allow spectating.
- [ ] Dead spectators cannot leave the enclosure or reach physical gems; the monster ignores them.
- [ ] Dead spectators cannot collect gems/key, occupy hiding spaces, unlock the exit, or finish.
- [ ] Key appears after the fifth completed hunt (10:00) and never earlier.
- [ ] Killing/disconnecting the key holder moves the key to a DIFFERENT drawer.
- [ ] Key unlocks the exit; surviving players complete by crossing it. Unkeyed and dead players cannot trigger completion.
- [ ] Late join, host departure, reconnect and shared-state migration are correct or blocked with a clear ready-up policy.
- [ ] Frame rate, draw cost, shared-code performance and official complexity fit the target Quest/player count.
- [ ] With one surviving player, no restart occurs. When ALL connected players die, the spectator area shows 5 → 1 and everyone returns alive to the hall after five seconds. Test both host and remote clients, then ten players.
- [ ] The new round clears key, exit lock, hiding occupancy and hunt count; doors/drawers reset closed, gems move to valid drawers, fog clears, and a full calm minute occurs before the next hunt. No immediate kill during reset.
- [ ] Reload also resets all game state. Escaped players prevent the all-dead reset; reload after a completed escape round.

Local checks already run: protobuf encode/decode equality; 1-based depth-first node references; instruction operand bounds and destination permissions; 35 gameplay/native-contract regressions with synthetic hand/physics states and an animation endpoint model. These do not satisfy the engine checks above.
