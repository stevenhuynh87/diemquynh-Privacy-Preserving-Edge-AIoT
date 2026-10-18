# Privacy-Preserving Fall Detection

Sprint 1 project for privacy-preserving fall detection using thermal and
radar sensing. The CNN pilot uses thermal frames. Radar work currently
covers raw-frame reading and sensor checks.

## Sprint 1

Period: 01/10/2026 - 18/10/2026. Phase: P1 - Gap, Data, Simulation.

## Progress recorded on 18/10/2026

- Literature matrix: **25 Sprint 1 papers**, plus four early Sprint 2
  readings kept separately, for 29 entries in `docs/lit_matrix.xlsx`.
- Python virtual environment works in `C:\phykd_fall`; experiments use CPU.
- Taramasco audit covers 10 subjects and 40 sensor CSV files.
- Subject 1 thermal reader preserves all 1,785 frames.
- Subject 1 radar reader preserves 5,396 frames, including 242 empty frames.
- `data/taramasco.py::TaramascoDS.load_record` returns thermal frames,
  radar frames, timestamps, original annotations and subject ID.
- Latest saved local pytest result: **18 passed**, with no failures.
- Pre-commit checks passed for the committed source/configuration.
- Both unweighted and class-weighted thermal CNN pilots have run.
- Saved test predictions match the test-window manifest; recomputed
  metrics agree with the saved report.
- Dataset card v0, audit notes and the Sprint report are available below.

See [Sprint report](reports/sprint_01.md),
[dataset card](docs/data_card.md) and
[audit notes](reports/data_audit_notes.md).

## Thermal CNN pilot

The model has 1,282 parameters and averages frame logits within each
4-second window. Subject split: train 1-6, validation 7-8, test 9-10.
Normalization uses unique frames selected by training windows only.

Method provenance: the +/-2-second fall window and the 1:3 fall/non-fall
ratio follow the Dataset segmentation section of
[Taramasco et al. (2025), DOI: 10.7717/peerj.19004](https://doi.org/10.7717/peerj.19004).
The project additionally guards +/-4 seconds around fall anchors,
rejects windows with timestamp gaps greater than three times median
positive dt, and protects both supplied-index interpretations for the
pending-review event. These are project preprocessing choices.

The original annotation table retains all 100 fall timestamps.
The pilot uses 99 proposed fall windows: 59 train, 20 validation and
20 test, plus three proposed non-fall windows per retained fall window.
Subject 3, event 2 is temporarily omitted because its supplied timestamp
and thermal-frame index disagree under the current comparison.
The original files remain unchanged.

The selected weighted run is `cnn_pilot_20261016_164312_452288`.
It was selected using validation results; its checkpoint was selected
by validation loss. Saved test results cover 80 windows from subjects 9-10:

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

`label_policy: pending` and `training_ready: false` record that annotation
validation remains incomplete. Training was performed as an explicitly
documented pilot with proposed labels.

## Setup and checks

Run commands from the repository root in PowerShell. For a fresh checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pre_commit install
```

The full test suite requires the locally obtained Taramasco files under
`data/Taramasco/dataset/subject_1/` and the original root annotation tables.
Dataset access and reuse terms must be checked separately.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pre_commit run --all-files
```

The nine audit regression tests use generated fixtures and can run
without the real dataset:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_taramasco_audit.py
```

## Experiment files

| File | Purpose |
| --- | --- |
| `configs/sprint1_split.json` | Subject split and pending annotation review |
| `sprint1_tools/check_cnn.py` | Thermal CNN definition and forward check |
| `sprint1_tools/build_thermal_windows.py` | Proposed window construction |
| `sprint1_tools/fit_thermal_normalization.py` | Train-only normalization |
| `sprint1_tools/train_thermal_pilot.py` | Unweighted pilot |
| `sprint1_tools/train_thermal_weighted.py` | Class-weighted pilot |
| `sprint1_tools/evaluate_thermal_test.py` | Selected pilot's held-out evaluation |

Inspect existing outputs under
`reports/cnn_pilot_20261016_164312_452288/test_evaluation/`.
Both pilot folders retain their protocol, history, predictions and source
snapshots. The protocol records the environment, source hashes and
manifest SHA-256. Checkpoints are stored locally under `results/` and
are excluded from Git. Saved results can be inspected without a checkpoint;
re-running inference requires the corresponding checkpoint and data.

Preserve the completed runs' manifests, normalization and generated
reports when reviewing them. Rebuilding the manifest or normalization
writes their shared files; a new experiment needs separate provenance.

## Open items

- Taramasco dataset reuse permission remains unconfirmed: the observed
  OSF license status was "No License"; see the dataset card.
- The S3/event-2 annotation discrepancy, S8 accelerometer timestamp
  reversal, thermal pixel layout and multimodal synchronization remain open.
- The IEEE paper linked alongside A5, document 8965661, has not been read
  in full because full-text access was unavailable. It is separate from
  the mmFall paper recorded in the matrix.
- A complete query/screening log for systematic search under Section 5.5
  is not present in the handoff. The report includes a preliminary gap
  synthesis; novelty still needs further verification.
- The requested formulation and phi(t) write-up remain pending because
  the exact Section 3.1 reference has not been identified in the supplied
  Brief Roadmap. The report records this reason and the needed clarification.

Outstanding items and their reasons are recorded in the Sprint report
under the teacher's Definition of Done.

## Repository structure

- `data/`: dataset loader and local datasets
- `configs/`: subject split and pilot configuration
- `docs/`: dataset card and literature matrix
- `reports/`: audit outputs, saved pilot records and Sprint report
- `sprint1_tools/`: Sprint 1 checks, preprocessing and CNN scripts
- `tests/`: automated tests
- `results/`: local checkpoints and generated experiment results

Large local datasets and model checkpoints under `results/` are excluded
by `.gitignore`, except for `results/.gitkeep`.
MM-Fi, NTU RGB+D 120 and UR Fall checks cover the samples stated in their
saved reports; they do not certify every downloaded file.

## AI assistance

ChatGPT/Codex assisted with drafting and reviewing code and documentation.
Commands and experiments were executed locally by the student. Method
sources, proposed labels, preprocessing decisions and pilot limitations
are recorded in the documentation and run protocols.
