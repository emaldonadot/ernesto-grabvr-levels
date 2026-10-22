# Working in Ernesto’s GRAB level repository

Start with [the reusable-level index](docs/reuse/README.md). Read only the component pages needed for the task, then the target game’s `LEVEL-MEMORY.md` and current generator.

- Each game owns its folder, generator, generated artifacts, tests, and `LEVEL-MEMORY.md`. Shared documentation describes patterns; it is not an extracted component runtime.
- Follow the [native connection and ID contract](docs/reuse/native-contract.md). Resolve symbolic names after the full hierarchy is assembled; never reuse numeric IDs from another build.
- Use [the play-model/state contract](docs/reuse/play-model.md) when composing mechanics. Record intentional differences in the target game’s memory/configuration.
- Treat gameplay defaults as configurable choices, not universal GRAB requirements. Preserve the user’s latest accepted rules.
- Change source generators for gameplay work; regenerate `.gasm`, JSON, `.level`, and manifests together when that work requires it. Do not hand-edit only a generated artifact.
- Distinguish headset feedback, local bytecode/format checks, and unverified engine behavior. Never describe local tests as a successful GRAB playtest.
- Native player teleport is local-only in the documented interface. Design each client’s movement accordingly; shared-controller remote teleports are not a verified solution.
- For documentation-only tasks, keep gameplay source, generated files and game behavior unchanged.
- Before publishing code/artifact changes, use the target game’s validation workflow. For documentation-only changes, check local links and the diff; no level rebuild is needed.

New games: follow [the composition workflow and memory template](docs/reuse/new-level.md). When a pattern changes, update its reusable page and the affected game’s memory, including its validation status.
