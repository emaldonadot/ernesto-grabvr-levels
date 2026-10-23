# Ernesto’s GRAB VR Levels

GRAB VR levels, reusable assets, native gameplay code, and per-game development notes.

## Office After Hours

An experimental cooperative office horror level designed for **10 players**: ten offices, three protective gems, individual hiding spaces, timed monster hunts, and a key-gated escape.

![Office After Hours layout](office-after-hours/docs/office-after-hours-preview.png)

- [Download the native .level file](office-after-hours/dist/office-after-hours.level?raw=true)
- [Game README and loading instructions](office-after-hours/README.md)
- [Requirements and design decisions](office-after-hours/LEVEL-MEMORY.md)
- [Quest play-test checklist](office-after-hours/docs/QUEST-PLAYTEST.md)

**Status:** Forty-one local gameplay and native-contract checks pass. Ernesto has tested earlier builds on Quest. Exit fix 5 needs headset verification of key feedback, gate opening and native completion, along with the prior hunt polish.

Latest build: **Exit fix 5** places the native finish one meter behind the exit, removes the off-map finish teleport, adds a visible gold lock and key pickup feedback, and lets the inventory key holder unlock by approaching the doorway. It retains the prior hunt polish. Replace the previous level file and reload before retesting.

## Parking Lot Horror

A separate ten-player survival scene: sixty covered parking spaces, nine vehicles, three physical immunity gems, two sliding-minivan hiding spots and a detailed skeleton. Five 60-second hunts, temporary fog, a key-gated finish room and enclosed spectator gallery. Revision 3 adds a visible gold lock, inventory-key pickup feedback, owner-approach unlocking and green floor strips leading to the native finish; it retains revision 2’s pursuit, animated windows and supported exit room.

![Parking Lot Horror layout](parking-lot-horror/docs/parking-lot-horror-preview.png)

- [Download the native .level file](parking-lot-horror/dist/parking-lot-horror.level?raw=true)
- [Game README and loading instructions](parking-lot-horror/README.md)
- [Requirements and design decisions](parking-lot-horror/LEVEL-MEMORY.md)
- [Vehicle and skeleton preview](parking-lot-horror/docs/vehicles-and-monster-preview.png)
- [Validation and Quest checklist](parking-lot-horror/docs/VALIDATION.md)

**Status:** 31 local tests pass, including inventory pickup, authorized unlock and two survivors reaching the finish without teleport. Quest/multiplayer testing pending. Editor rendering was unavailable because the browser could not create a WebGL context.

## Project organization

Start new games with the [reusable element catalog and ChatGPT entrypoint](docs/reuse/README.md): component specifications, native/state contracts, and a composition workflow with a game-memory template. These document existing generator patterns; they are not an extracted prefab/runtime library.

Each new game gets its own folder and `LEVEL-MEMORY.md` documenting requirements, decisions, implementation details, and outstanding validation.

To build and test Office After Hours:

```sh
git clone https://github.com/emaldonadot/ernesto-grabvr-levels.git
cd ernesto-grabvr-levels/office-after-hours
python -m pip install -r requirements.txt
python src/build.py
python -m unittest discover -s tests -v
```

See the included upstream license for the third-party GRAB format schema.

## The Grave Yard

A fenced graveyard horror project with 16 graves, climbable trees, a decaying zombie, five hunts and a golden-skull gate puzzle. Revision 3 clears the spectator sightline through the east wall while retaining solid containment. Revision 2 added staged skull/socket instructions, a green route to the native finish, 8m solid walls, a sealed gate header and a transparent overhead collision cap. **31 local checks pass; native build ready for headset testing. Quest/multiplayer validation pending.**

- [Download the native .level file](the-grave-yard/dist/the-grave-yard.level?raw=true)
- [Game README](the-grave-yard/README.md)
- [Layout preview](the-grave-yard/docs/the-grave-yard-preview.png)
- [Validation and Quest checklist](the-grave-yard/docs/VALIDATION.md)
- [Requirements and workstream handoffs](the-grave-yard/LEVEL-MEMORY.md)
- [Scene specification JSON (not native level JSON)](the-grave-yard/scene-spec.json)
