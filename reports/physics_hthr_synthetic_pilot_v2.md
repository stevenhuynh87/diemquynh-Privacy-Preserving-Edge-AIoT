# PhysicsExtractor — h_thr Synthetic Pilot V2

## Data
- Source: Three manually constructed 25-joint NTU-style poses.
- Pose types: lying_left, lying_right, lying_back.
- Coordinate convention: metres, z-up.
- Floor assumption: lowest joint at z = 0.08 m.
- Each clip: 30 identical frames, 30 FPS.
- These are synthetic examples, not real lying recordings.

## COM results
| Pose | COM height (m) | Torso angle (deg) |
|---|---:|---:|
| lying_left | 0.3401 | 88.0 |
| lying_right | 0.3401 | 88.0 |
| lying_back | 0.2434 | 88.0 |

## Candidate threshold
- Rule: maximum lying COM height + 0.05 m.
- h_thr_demo = 0.3901 m.
- The 0.05 m margin is an assistant-proposed assumption.
- This threshold is valid only as a synthetic demonstration.

## Validation
- PhysicsExtractor unit tests: 10/10 PASS.
- Synthetic free-fall test: PASS.
- Coordinate-reference shift test: PASS.
- Synthetic ground duration: 0.9667 s per 30-frame clip.

## Remaining limitation
- No real lying-pose COM calibration has been completed.
- NTU camera coordinates have not been floor-calibrated.
- Synthetic poses do not establish a population-level threshold.
- Real/SMPL lying clips and non-fall low-posture samples are needed
  before adopting a production threshold.

## Status
PhysicsExtractor mathematical implementation: tested.
h_thr selection procedure: demonstrated on synthetic poses.
h_thr real-data validation: NOT COMPLETED.
