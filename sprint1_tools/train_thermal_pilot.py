import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.metrics import precision_recall_fscore_support

from check_cnn import ThermalCNN


def main():
    # 1. Read configuration and proposed window labels.
    project = Path(__file__).resolve().parents[1]

    config = json.loads(
        (project / "configs/sprint1_split.json").read_text(
            encoding="utf-8-sig"
        )
    )
    norm = json.loads(
        (project / "reports/thermal_normalization.json").read_text(
            encoding="utf-8-sig"
        )
    )

    manifest_path = project / "reports/thermal_window_candidates.csv"
    windows = pd.read_csv(manifest_path)
    train = windows.loc[windows["split"] == "train"].copy()
    validation = windows.loc[windows["split"] == "validation"].copy()

    groups = [
        set(config[f"{name}_subjects"])
        for name in ("train", "validation", "test")
    ]

    assert all(
        not groups[i] & groups[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ), "Subjects overlap between splits"

    assert set(train["subject"]) == groups[0]
    assert set(validation["subject"]) == groups[1]
    assert set(norm["fit_subjects"]) == groups[0]
    assert norm["fit_split"] == "train"
    assert np.isfinite([norm["mean"], norm["std"]]).all()
    assert norm["std"] > 0
    assert set(train["candidate_label"]) == {0, 1}
    assert set(validation["candidate_label"]) == {0, 1}

    for review in config.get("pending_reviews", []):
        conflict = (
            (windows["subject"] == review["subject"])
            & (windows["event"] == review["event"])
        )
        assert not conflict.any(), "Pending-review event found in manifest"

    seed = int(config["seed"])
    epochs = 20
    batch_size = 8
    learning_rate = 0.001

    torch.manual_seed(seed)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)

    # 2. Load and normalize train/validation images only.
    root = Path(config["dataset_root"])
    if not root.is_absolute():
        root = project / root

    images = {}
    source_hashes = {}

    for subject in sorted(groups[0] | groups[1]):
        source = root / f"subject_{subject}" / "ir_camera.csv"
        source_hashes[str(subject)] = hashlib.sha256(
            source.read_bytes()
        ).hexdigest()

        record = pd.read_csv(source, header=None)
        assert record.shape[1] == 769

        times = record.iloc[:, 0].to_numpy(dtype=np.float64)
        assert np.isfinite(times).all()
        assert (np.diff(times) > 0).all()

        pixels = record.iloc[:, 1:].to_numpy(dtype=np.float32)
        assert np.isfinite(pixels).all()

        tensor = torch.from_numpy(pixels.reshape(-1, 1, 24, 32))
        images[subject] = (tensor - norm["mean"]) / norm["std"]

        subject_windows = windows.loc[windows["subject"] == subject]
        for row in subject_windows.itertuples(index=False):
            left = int(row.start_row_0based)
            right = int(row.stop_row_exclusive)

            assert 0 <= left < right <= len(times)
            assert right - left == int(row.n_frames)

            # Allow tiny CSV floating-point rounding differences.
            assert times[left] + 1e-6 >= row.start_s
            assert times[right - 1] < row.end_s + 1e-6

    # 3. Create separate output folders for this run.
    run = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    report_dir = project / "reports" / f"cnn_pilot_{run}"
    model_dir = project / "results" / f"cnn_pilot_{run}"
    report_dir.mkdir(parents=True)
    model_dir.mkdir(parents=True)

    shutil.copy2(__file__, report_dir / "training_script.py")
    shutil.copy2(
        Path(__file__).with_name("check_cnn.py"),
        report_dir / "model_script.py",
    )

    protocol = {
        "run_type": "pilot_with_proposed_window_labels",
        "config": config,
        "normalization": norm,
        "epochs": epochs,
        "batch_size_windows": batch_size,
        "optimizer": "Adam",
        "learning_rate": learning_rate,
        "loss": "unweighted_cross_entropy",
        "device": "cpu",
        "aggregation": "mean frame logits within each window",
        "checkpoint_selection": "lowest validation loss across 20 epochs",
        "test_images_used": False,
        "torch_version": str(torch.__version__),
        "manifest_sha256": hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest(),
        "thermal_csv_sha256": source_hashes,
        "checkpoint": str(
            (model_dir / "best_model.pt").relative_to(project)
        ),
        "ai_assistance": (
            "Training script drafted with ChatGPT/Codex assistance."
        ),
        "limits": (
            "Window labels are proposed; not per-frame ground truth "
            "or final paper results."
        ),
    }

    (report_dir / "protocol.json").write_text(
        json.dumps(protocol, indent=2), encoding="utf-8"
    )

    model = ThermalCNN()
    optimizer = torch.optim.Adam(
        model.parameters(), lr=learning_rate
    )
    criterion = torch.nn.CrossEntropyLoss()

    # One batch contains up to eight windows.
    def run_epoch(table, training):
        model.train(training)
        total_loss = 0.0
        truth = []
        predicted = []

        for offset in range(0, len(table), batch_size):
            batch = table.iloc[offset:offset + batch_size]
            labels = torch.tensor(
                batch["candidate_label"].to_numpy(),
                dtype=torch.long,
            )

            if training:
                optimizer.zero_grad()

            with torch.set_grad_enabled(training):
                outputs = []

                for row in batch.itertuples(index=False):
                    frames = images[int(row.subject)][
                        int(row.start_row_0based):
                        int(row.stop_row_exclusive)
                    ]
                    outputs.append(model(frames).mean(dim=0))

                logits = torch.stack(outputs)
                loss = criterion(logits, labels)

                if not torch.isfinite(loss).item():
                    raise ValueError("Non-finite loss")

                if training:
                    loss.backward()
                    optimizer.step()

            total_loss += loss.item() * len(batch)
            truth.extend(labels.tolist())
            predicted.extend(
                logits.detach().argmax(dim=1).tolist()
            )

        precision, recall, f1, _ = precision_recall_fscore_support(
            truth,
            predicted,
            average="binary",
            pos_label=1,
            zero_division=0,
        )

        metrics = {
            "loss": total_loss / len(table),
            "accuracy": float(accuracy_score(truth, predicted)),
            "balanced_accuracy": float(
                balanced_accuracy_score(truth, predicted)
            ),
            "fall_precision": float(precision),
            "fall_recall": float(recall),
            "fall_f1": float(f1),
        }
        return metrics, predicted

    # 4. Train and automatically save measurements.
    history = []
    best_loss = float("inf")

    print(
        "PILOT: proposed window labels; test images are not loaded.",
        flush=True,
    )

    for epoch in range(1, epochs + 1):
        shuffled = train.sample(
            frac=1, random_state=seed + epoch
        )

        train_metrics, _ = run_epoch(shuffled, True)
        val_metrics, predictions = run_epoch(validation, False)

        history.append({
            "epoch": epoch,
            **{
                f"train_{key}": value
                for key, value in train_metrics.items()
            },
            **{
                f"validation_{key}": value
                for key, value in val_metrics.items()
            },
        })

        pd.DataFrame(history).to_csv(
            report_dir / "history.csv", index=False
        )

        if val_metrics["loss"] < best_loss:
            best_loss = val_metrics["loss"]

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "epoch": epoch,
                    "normalization": norm,
                    "protocol": protocol,
                },
                model_dir / "best_model.pt",
            )

            best = {
                "epoch": epoch,
                "validation": val_metrics,
                "run_type": protocol["run_type"],
            }

            (report_dir / "best_validation.json").write_text(
                json.dumps(best, indent=2), encoding="utf-8"
            )

            validation.assign(
                predicted_label=predictions
            ).to_csv(
                report_dir / "validation_predictions.csv",
                index=False,
            )

        print(
            f"Epoch {epoch:02d}/{epochs}: "
            f"train_loss={train_metrics['loss']:.4f} "
            f"val_loss={val_metrics['loss']:.4f} "
            f"val_acc={val_metrics['accuracy']:.3f} "
            f"fall_recall={val_metrics['fall_recall']:.3f} "
            f"fall_f1={val_metrics['fall_f1']:.3f}",
            flush=True,
        )

    print("Best validation:", json.dumps(best), flush=True)
    print("Reports:", report_dir, flush=True)
    print("Checkpoint:", model_dir / "best_model.pt", flush=True)
    print("Test evaluation: not run", flush=True)


if __name__ == "__main__":
    main()
