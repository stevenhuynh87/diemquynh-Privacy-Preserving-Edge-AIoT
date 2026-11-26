# Sprint 2 — PhysicsExtractor Implementation Status
Date: 2026-11-26

## Implemented
- PhysicsExtractor(joints, fps) -> dict
- Mass-weighted COM using approximate NTU-Winter14 mapping
- COM height h(t)
- Vertical velocity v_z(t) using Savitzky-Golay
- Peak absolute vertical acceleration a_peak
- Torso angle theta
- Ground duration T_ground when h_thr is supplied

## Verification
- Project pytest: 35/35 PASS
- Synthetic free-fall: PASS
- Coordinate translation invariance: PASS
- Two-argument interface: PASS

## Synthetic h_thr pilot
- Lying left COM: 0.3401 m
- Lying right COM: 0.3401 m
- Lying back COM: 0.2434 m
- Demo threshold: 0.3901 m

These values are from manually constructed poses.
The threshold is NOT validated on real lying clips.

## Current limitations
- h_thr real-data calibration is pending.
- If h_thr is absent, T_ground returns None.
- Current implementation accepts NTU-style 25-joint poses.
- Input requires metres and z-up coordinates.
- Floor calibration and tracking-state handling are not implemented.
- Winter14-to-NTU anatomical mapping is approximate.
- Savitzky-Golay defaults are implementation choices.

## Status
Core implementation and synthetic tests: COMPLETED.
Real-pose validation and h_thr calibration: PENDING.
Ready for advisor review with limitations disclosed.
