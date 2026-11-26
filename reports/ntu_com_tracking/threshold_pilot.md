# NTU P001-P008: exploratory low-COM comparison

Status: exploratory analysis, NOT a calibrated h_thr or model evaluation.

## Data and method

Setup S001, camera C001, replication R001, performers P001-P010.
Actions: A043 falling, A008 sitting down, A006 picking up.

For each available skeleton clip, the script selected a body only when
selection was unambiguous. The exploratory proxy was:

COM Camera Y - median Camera Y of tracked FootRight in frames 1-20.

A clip was skipped when fewer than 15 of those FootRight samples were
tracked, or their Camera Y range exceeded 0.06 m. The 0.06 m rule and
0.25 m trial level are implementation choices for this inspection;
neither is specified by the research roadmap. The longest consecutive
run below 0.25 m was counted in FRAMES, not seconds.

## Observed results

| Performer | A043 fall: min m / longest frames | A008 sit: min m / longest frames | A006 pickup: min m / longest frames |
|---|---|---|---|
| P001 | 0.194 / 20 | skipped: unstable foot baseline | 0.266 / 0 |
| P002 | -0.152 / 38 | skipped: few tracked foot frames | 0.301 / 0 |
| P003 | skipped: unstable foot baseline | 0.420 / 0 | skipped: unstable foot baseline |
| P004 | 0.265 / 0 | 0.411 / 0 | 0.299 / 0 |
| P005 | 0.132 / 21 | skipped: unstable foot baseline | 0.255 / 0 |
| P006 | 0.104 / 22 | 0.622 / 0 | skipped: unstable foot baseline |
| P007 | skipped: unstable foot baseline | skipped: unstable foot baseline | 0.319 / 0 |
| P008 | 0.073 / 21 | 0.387 / 0 | 0.077 / 3 |
| P009-P010 | missing in the inspected S001/C001/R001 selection | missing | missing |

Of 24 named clips for P001-P008, 16 passed these inspection
conditions and 8 were skipped. At the 0.25 m trial level, 5/6
inspected falls, 0/4 sitting clips, and 1/6 pickup clips had at
least one low frame. These fractions are NOT sensitivity or
specificity: clips were excluded by a proposed quality rule.

Every frame classified as low in these clips had at least one
inferred joint used by the 14-segment COM approximation. There
were zero low frames with all 17 COM joints tracked. The negative
value -0.152 m in P002 A043 further shows that this proxy must
not be interpreted as physical height above the floor.

## Sprint 2 decision

The observations motivate examining low-height duration alongside
height, as in the roadmap's h and T_ground features. They do not
establish a valid h_thr. Before computing physical h and T_ground,
verify the vertical coordinate convention, obtain a defensible
floor reference, handle inferred joints explicitly, and establish
the skeleton sampling interval. Then evaluate across more subjects
and confounding actions.

No threshold was selected, no frame was removed or interpolated,
and the original dataset archives were unchanged.

## Torso angle and acceleration inspection

Three P008 clips were inspected: A043 falling (63 frames),
A008 sitting down (85), and A006 picking up (83).
Each RGB video reports 30 FPS and its decoded frame count matches
the corresponding skeleton frame count. This does not independently
verify skeleton timestamps or exact RGB-skeleton alignment.

For torso angle, Camera Y was moved to the third array component
for inspection. Camera tilt was not corrected. Neck, HipLeft and
HipRight were tracked in every frame of all three clips.

| Action | Theta range | Peak theta | Final theta |
|---|---:|---:|---:|
| A043 falling | 14.1-98.2 deg | 98.2 deg, frame 52 | 81.8 deg |
| A008 sitting | 15.3-63.7 deg | 63.7 deg, frame 41 | 18.3 deg |
| A006 pickup | 14.1-87.3 deg | 87.3 deg, frame 28 | 19.2 deg |

A006 also has a large torso angle, so peak angle alone does not
distinguish falling from picking up in these examples. Their
end-of-clip postures differ; this is exploratory, not a classifier.

Camera-Y COM derivatives were inspected using an ASSUMED 30 FPS,
Savitzky-Golay polynomial order 2, and windows of 5, 7, 9 frames:

| Action | a_peak window 5 | window 7 | window 9 |
|---|---:|---:|---:|
| A043 falling | 15.042 | 6.644 | 4.509 |
| A008 sitting | 22.912 | 10.213 | 6.091 |
| A006 pickup | 84.179 | 33.582 | 26.923 |

Units are m/s^2 under the assumed sampling rate and camera axis.
The values change strongly with SG window choice. They do not
establish impact time or validated vertical acceleration.

At the SG(7,2) peak for A006 (frame 33), COM Camera Y was
-0.172 m; it then jumped to -0.422 m at frame 34 and
-0.227 m at frame 35. Around these frames 8-9 joints used
for COM were inferred. This is a suspected tracking-related
artifact, not a proven cause. No interpolation or correction
was applied.

Decision: keep h_thr, SG parameters, a_peak and impact timing
unvalidated on real NTU data. Do not report these three clips
as measured fall-detection performance. Next implementation
work should expose tracking quality alongside physics features
and require a defensible floor reference for physical height.
