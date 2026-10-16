# Privacy-Preserving Fall Detection

Sprint 1 project for privacy-preserving fall detection
using thermal and radar sensing.

The Sprint 1 CNN pilot uses thermal images. Radar work currently
covers raw-frame reading and sensor checks.

## Sprint 1

Period: 01/10/2026 - 18/10/2026

Phase: P1 - Gap, Data, Simulation

## Objectives

- Literature gap analysis
- Dataset acquisition and audit
- Taramasco dataset loader
- Thermal fall/non-fall CNN baseline
- Reproducible experiments

## Progress recorded on 16/10/2026

- Python virtual environment works in `C:\phykd_fall`.
- Taramasco audit covers 10 subjects and 40 sensor CSV files.
- Subject 1 thermal reader preserves all 1,785 frames.
- Subject 1 radar reader preserves 5,396 frames, including 242 empty frames.
- Latest reported local pytest run: **18 passed**.
- Pre-commit checks passed for the latest loader/audit commit.
- Both unweighted and class-weighted thermal CNN pilots have run.
- Saved test predictions were checked against the test-window manifest;
  recomputed metrics agree with the saved report.

## Thermal CNN pilot

The model has 1,282 parameters and averages frame logits within each
4-second window. Subject split: train 1–6, validation 7–8, test 9–10.
Normalization uses unique frames selected by training windows only.

Method provenance: the +/-2-second fall window and the 1:3 fall/non-fall
ratio follow the Dataset segmentation section of
[Taramasco et al. (2025), DOI: 10.7717/peerj.19004](https://doi.org/10.7717/peerj.19004).
These rules are inherited methods, not a new contribution of this project.
The project additionally guards +/-4 seconds around fall anchors,
rejects windows with timestamp gaps greater than three times median
positive dt, and protects both supplied-index interpretations for the
pending-review event. These are project preprocessing choices.

The original annotation table retains all 100 fall timestamps.
The pilot uses 99 proposed fall windows: 59 train, 20 validation and
20 test, plus three proposed non-fall windows per retained fall window.
Subject 3, event 2 is temporarily omitted because its supplied timestamp
and thermal-frame index disagree under the current comparison.
This is a documented project selection decision; original files remain unchanged.

The selected weighted run is `cnn_pilot_20261016_164312_452288`.
It was selected using validation results; its checkpoint was selected
by validation loss. Saved test results cover 80 windows from subjects 9–10:

| Metric | Value |
| --- | ---: |
| Accuracy | 78.75% |
| Balanced accuracy | 84.17% |
| Fall precision | 54.29% |
| Fall recall | 95.00% |
| Fall F1 | 69.09% |

Confusion counts: TN=44, FP=16, FN=1, TP=19.
These are window-level pilot results using proposed labels and a selected
1:3 fall/non-fall ratio. They do not establish real-world performance
or performance using every original annotation.

Inspect existing outputs under
`reports/cnn_pilot_20261016_164312_452288/test_evaluation/`.
Keep the completed run's manifest, normalization and reports unchanged
while reviewing it. The manifest is bound to the run by a SHA-256 hash.

Details: [dataset card](docs/data_card.md) and
[audit notes](reports/data_audit_notes.md).

## Open items

- Taramasco dataset reuse permission remains unconfirmed: the observed
  OSF license status was "No License"; see the dataset card.
- The S3/event-2 annotation discrepancy, thermal pixel layout and
  multimodal synchronization remain unresolved.
- Literature matrix target: at least 25 papers. Latest confirmed progress
  is 11 entries; literature work is currently paused.
- Gap/novelty synthesis and the requested formulation/phi(t) write-up
  remain pending; the exact Section 3.1 reference needs clarification.
- Finalize `reports/sprint_01.md` within two pages and complete the
  30-minute advisor demo. The current Sprint report is an older draft.
- Complete the repository review and GitHub handoff. Local commits
  alone do not establish that all Sprint code has reached the remote `main`.

## Repository structure

- `data/`: dataset loader and local datasets
- `configs/`: subject split and pilot configuration
- `docs/`: documentation and literature matrix
- `reports/`: audit outputs, saved pilot records and sprint reports
- `sprint1_tools/`: Sprint 1 checks, preprocessing and CNN scripts
- `src/`: additional project source files
- `tests/`: automated tests
- `results/`: generated experiment results

Large local datasets and model checkpoints under `results/` are excluded
by the current `.gitignore`, except for `results/.gitkeep`.

## AI assistance

ChatGPT/Codex assisted with drafting and reviewing code and documentation.
Commands were executed locally by the student. Saved measurements,
proposed labels and known limitations must be checked and reported accurately.
