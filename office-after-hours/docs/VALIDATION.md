# Validation — Hunt polish 4

2026-10-22: **35 local tests PASS**. Protobuf encode/decode equality PASS. 728 nodes, 35 code blocks; estimated complexity 5,459.

Ernesto reports that the scene looks good, but fog persists after hunts and gems fall from opening drawers. He requests unconditional hiding safety, monster fumes and a slightly faster monster. This revision has not yet been tested in GRAB on a headset.

- Calm and initial fog density are exactly zero. FogOn has an instant native ONLEAVE clear target. LocalFog rearms trigger edges across frames and refreshes calm clear every 0.5s. Repeated hunt cycles, native leave dispatch, forced ambience interference and all-dead reset clear in the harness.
- MonsterFumes is a native emitter inside the Monster group: 18 particles/s, 0.55–1s lifetime, upward/spreading velocity, size expansion, transparent end color. Emitter parenting and bounded particle configuration are checked. Native particles are not rendered by the harness.
- Unclaimed gems follow tray positions until first valid pickup. Injected falls during opening/closing are corrected in all three gem scripts. After pickup, drop/throw positions are left to physics until relocation. Post-hunt seating resets in three distinct new drawers. The native grip transition, motion smoothness and physical collision/velocity remain headset checks.
- All twenty hiding slots are excluded from target selection even with an old observed-entry flag. A catch-phase test confirms hiding is checked again immediately before killing. Desk height does not instantly revoke hiding. Occupancy and leaving checks still pass; entry debounce avoids immediate inside-pad exit.
- Monster movement remains facing-correct and increases from 3.1 to 3.4m/s. Four direction checks verify heading and nominal displacement.
- Prior native contracts, gem immunity/release, key/escape timing and respawn, and simulated ten-client all-dead countdown/revival tests still pass.

The local harness executes serialized GASM, synthetic hand/physics states and native animation endpoints. It does not reproduce the GRAB renderer, physics solver, grip system, native networking or actual headset tracking. The Quest checklist remains necessary; local tests are not a confirmed headset fix.
