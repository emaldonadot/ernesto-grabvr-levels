# Local validation result

2026-10-20: PASS, eleven native-bytecode gameplay tests (updated 2026-10-21 for ten-player target).

- 637 nodes, 33 GASM blocks, estimated complexity 5,528.
- Binary protobuf round-trip preserves every field.
- All connection object IDs resolve within the 1-based depth-first node list.
- All register and label operand indices are within bounds.
- Actual generated geometry rendered and visually inspected.
- No Quest, network, or engine validation performed.
- Web editor blocked by lack of WebGL in the available browser.

The tests cover phase timing and key gating, three distinct gem drawers and relocation, doors/drawers and dead interaction guards, hiding capacity, walking out of hiding, open-drawer pickup and one-gem maximum, immunity/hidden/dead target filtering, witnessed hiding, key relocation after owner death and exit checks, dead marker following, and a ten-player case with three protected players and seven vulnerable players.

The test harness models the scalar instruction set, immediate property reads/writes, player selection, trigger inputs, variable writes and teleports. It enforces the documented 500-instruction frame budget; it does not prove current engine semantics.
