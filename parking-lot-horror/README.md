# Parking Lot Horror

A cooperative GRAB horror level designed for ten players in a covered 60-space garage. Six rows of ten spaces, supporting columns, painted parking lines and nine primitive vehicles create the new scene. A detailed 2.525 m skeleton with ghostly fumes pursues survivors at 3.7 m/s.

- [Native `.level` download](dist/parking-lot-horror.level?raw=true)
- [Scene preview](docs/parking-lot-horror-preview.png)
- [Vehicle and skeleton preview](docs/vehicles-and-monster-preview.png)
- [Requirements and implementation memory](LEVEL-MEMORY.md)
- [Validation and Quest checklist](docs/VALIDATION.md)
- [Generated object/controller manifest](docs/manifest.json)

## Rules and controls

The round starts with 60 seconds of calm. Each of five hunts lasts 60 seconds, with a fresh 60-second calm before every hunt; fog and the monster appear only during hunts. After hunt five, the hunts stop and a gold key appears on the pedestal by the escape gate. Touch the key, then the gate lock; surviving players cross the raised gate to finish.

Touch blue driver handles on the sport car, both minivans and SUV to open their hinged doors. Three shared physical immunity gems are mounted inside the sport car, first minivan and blue SUV. **Hold** a gem to gain protection; release it to lose protection. The second minivan is unstocked to keep the total at three.

Both minivans have sliding side doors and blue hiding pads. Touch a pad to enter the rear cabin and close the sliding door; touch the inside pad to leave. Crouch inside the realistic low roof. Each van holds one protected player. Hiding makes the player ineligible for pursuit and capture, even while being watched. Walking out of the hiding volume releases protection.

The blue street motorcycle resembles an MT-07; the black/gray three-wheeler resembles a Ryker Sport. Three additional cars are crushed, with no functional doors. These are native primitive interpretations, not imported manufacturer meshes.

A skeleton touch eliminates an unprotected player and sends that client's player to the enclosed side spectator gallery. The gallery looks through physical transparent windows into the garage. If every connected participant dies, a five-second countdown resets the round, doors, gems and players. Escaped players prevent a wipe reset. Reload after a completed escape round.

## Build and load

From repository root:

```sh
python -m pip install -r parking-lot-horror/requirements.txt
python parking-lot-horror/src/build.py
python -m unittest discover -s parking-lot-horror/tests -v
python parking-lot-horror/src/render.py
python parking-lot-horror/src/render_details.py
```

Transfer `dist/parking-lot-horror.level` into GRAB's user-level directory on Quest, under `Android/data/com.slindev.grab` (or `com.slindev.grab_demo`), with relative level folder `levels/user`, then reload the game and open user levels. The `.level` extension matters; a numeric basename is not required by the documented local-file format. Use a unique name for this new level and keep it when replacing the same local entry. See the existing [loading notes](../office-after-hours/README.md) for transfer alternatives.

The JSON and GASM are generated with the binary from source. Format 25 schema and license are vendored in `vendor/`, copied from the current office baseline; upstream schema was independently checked against GRAB Tools on 2026-10-22.

**Status:** local bytecode/format tests and software geometry inspection only. GRAB Tools could not create a WebGL context in the available browser, so no editor rendering or Quest playtest is claimed. Multiplayer synchronization, current native physics, actual complexity/performance and final headset appearance need testing.
