# Validation — Interaction fix 1

2026-10-21: seventeen gameplay and independent native-connection contract tests PASS.

- Baseline headset feedback: geometry looked good; doors/drawers and other triggers did not respond.
- The new independent contract tests FAILED on the baseline: 27 != 28 player slots, 4 != 6 trigger slots, and the old VM accepted incomplete layouts.
- Corrected player properties match the 28-slot layout independently extracted from the GRAB-exported September 2026 lobby.
- Trigger properties preserve the six exported slots and disable unused fields.
- Native controller START targets resolve for all 72 hand/head interaction triggers.
- All ten office doors and drawers toggle in the strict local VM.
- Existing gem, hiding, death, key, exit, timing and ten-player tests pass with the corrected contract.
- Binary protobuf round-trip preserves every field.
- Scene geometry is unchanged from the baseline.
- 637 nodes; 33 code blocks; estimated complexity 5,528.

**Headset validation of Interaction fix 1: NOT RUN.** These tests verify the exported layout and local logic, not GRAB collision, networking or headset behavior. Load the replacement `.level`; its title includes `Interaction fix 1`.

The independent connection fixture is in `tests/fixtures/native_connection_layout.json`, with upstream URL and source SHA-256. It does not import connection definitions from `src/build.py`.
