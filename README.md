# Ernesto’s GRAB VR Levels

GRAB VR levels, reusable assets, native gameplay code, and per-game development notes.

## Office After Hours

An experimental cooperative office horror level designed for **10 players**: ten offices, three protective gems, individual hiding spaces, timed monster hunts, and a key-gated escape.

![Office After Hours layout](office-after-hours/docs/office-after-hours-preview.png)

- [Download the native .level file](office-after-hours/dist/office-after-hours.level?raw=true)
- [Game README and loading instructions](office-after-hours/README.md)
- [Requirements and design decisions](office-after-hours/LEVEL-MEMORY.md)
- [Quest play-test checklist](office-after-hours/docs/QUEST-PLAYTEST.md)

**Status:** Twenty-nine local gameplay and native-contract checks pass. Ernesto confirmed doors and solo monster pursuit. Revised closets, fog, gems and round restart await headset testing.

Latest build: **Playtest fixes 3** adds inward-facing closets with animated doors, stronger hunt fog, corrected gem physics, monster turning/speed, and a five-second all-dead round restart. Replace the previous level file and reload before retesting.

## Project organization

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
