# Hunt fog and phase ambiance

Pattern `atmosphere.hunt.v1`. Sources: [generator: FogOn/FogOff and LocalFog](../../../office-after-hours/src/build.py), [LocalFog GASM](../../../office-after-hours/src/LocalFog.gasm), [native leave/retry tests](../../../office-after-hours/tests/test_hunt_polish.py).

## Contract

Shared `Clock.X` is the hunt flag. Each client applies its own visual ambiance using non-shared `LocalFog` and non-shared empty-source trigger nodes. Do not make a local visual depend solely on one client entering a physical volume.

| Setting | Hunt | Calm/initial/reset |
| --- | --- | --- |
| Fog density | 0.72 | **0** |
| Sky color | Gray `(0.36,0.42,0.44)` | Dark blue-gray `(0.08,0.12,0.14)` for target restore |
| Ambient brightness | 0.35 | 0.7 |
| Transition | 1s fade in | Instant, duration 0 |

`FogOn` has ONENTER dense ambiance **and ONLEAVE zero-fog restoration**. `FogOff` independently applies the calm target. `LocalFog` rearms force values across `SLEEP 0` frame boundaries, activates the appropriate target on phase change, and refreshes calm clearing every 0.5s. It checks the phase again after yielding so a calm retry does not deliberately override a newly started hunt. A new local controller applies the current shared phase for late clients.

Restore every altered ambiance field, not just density. Different future components must not fight by repeatedly applying conflicting sky/fog targets. The older renderer reference maps density through a fourth power, so small numeric values can be nearly invisible at indoor scale; choose the palette/density in the actual headset.

## Reuse and acceptance

Supply phase source, target palette, fog density, brightness, fade durations and retry interval. Initial calm should serialize clear, and any death reset must set the shared phase calm. Keep native ONLEAVE support in tests; an enter-only harness would miss a restoration path. Test repeated full hunts, reset during hunt, late join in both phases and a second client. Office’s latest explicit clearing/retry logic is locally checked after a headset report of lingering fog; **the fix is not yet headset-confirmed**. Monster particles are a separate short-lived localized effect, not global fog.
