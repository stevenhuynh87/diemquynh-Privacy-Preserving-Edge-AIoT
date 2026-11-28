# h_thr pilot on synthetic lying poses v2

Status: exploratory threshold for synthetic z-up poses only. Not validated
on real NTU clips and not a calibrated physical floor threshold.

## Source and method

Planning Section 7.2 defines h(t) = COM_z(t) and T_ground as continuous
time with h(t) < h_thr. The instructor asked for h_thr chosen from COM
heights in several lying sample clips, with the selection method recorded.

Input: reports/physics_lying_synthetic_clips_v2.npz. Each named pose is
repeated for 30 frames. PhysicsExtractor was called at fps=30 with its
existing NTU COM calculation. These synthetic poses do not establish
the floor plane or tracking quality of real NTU skeletons.

| Synthetic sample | Median COM z (m) | Frames below 0.35 m | Final T_ground (s) |
|---|---:|---:|---:|
| lying_left | 0.340108 | 30/30 | 0.966667 |
| lying_right | 0.340108 | 30/30 | 0.966667 |
| lying_back | 0.243425 | 30/30 | 0.966667 |

Assistant-proposed trial value: h_thr = 0.35 m in this synthetic
coordinate system. It is 0.009892 m above the largest measured lying
COM height, so the margin is small. The comparison is strictly h < h_thr.
The first below-threshold frame has T_ground = 0; after 30 consecutive
frames, T_ground = 29/30 s.

The older reports/physics_hthr_synthetic_pilot.csv corresponds to
physics_lying_synthetic_clips.npz (v1), not v2. Its left/right COM value
0.690739 m must not be used to justify this v2 threshold.

## What remains

These are three static synthetic sequences; left and right have the same
COM height. No ADL negative controls in the same coordinate system and
no real lying clips have passed this threshold test. Existing NTU
Camera Y or foot-baseline results cannot be compared directly with
this synthetic z-up threshold. Do not call h_thr = 0.35 m a validated
NTU threshold or mark Sprint 2 PhysicsExtractor Part 1 complete on
the basis of this pilot alone.
