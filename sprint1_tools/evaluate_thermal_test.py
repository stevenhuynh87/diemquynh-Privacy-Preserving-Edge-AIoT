import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from check_cnn import ThermalCNN


def main():
    project = Path(__file__).resolve().parents[1]
    checkpoint_path = (
        project
        / "results/cnn_pilot_20261016_164312_452288/best_model.pt"
    )
    output = (
        project / "reports"
        / checkpoint_path.parent.name / "test_evaluation"
    )
    metrics_path = output / "metrics.json"

    if metrics_path.exists():
        print("Showing saved test results; evaluation is not repeated.")
        print(metrics_path.read_text(encoding="utf-8"))
        return

    # Load the selected model and its saved training settings.
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)

    checkpoint = torch.load(
        checkpoint_path, map_location="cpu", weights_only=True
    )
    protocol = checkpoint["protocol"]
    config = protocol["config"]
    norm = checkpoint["normalization"]

    assert int(checkpoint["epoch"]) == 20
    assert protocol["loss"] == "mean_class_weighted_cross_entropy"
    assert np.allclose(protocol["class_weights"], [2.0 / 3.0, 2.0])
    assert set(config["test_subjects"]) == {9, 10}
    assert set(norm["fit_subjects"]) == set(config["train_subjects"])
    assert not set(config["test_subjects"]) & (
        set(config["train_subjects"])
        | set(config["validation_subjects"])
    )
    assert np.isfinite([norm["mean"], norm["std"]]).all()
    assert norm["std"] > 0

    # Confirm that the window table has not changed since training.
    manifest = project / "reports/thermal_window_candidates.csv"
    manifest_hash = hashlib.sha256(
        manifest.read_bytes()
    ).hexdigest()

    assert manifest_hash == protocol["manifest_sha256"], (
        "Window manifest changed since training"
    )

    windows = pd.read_csv(manifest)
    test = windows.loc[windows["split"] == "test"].copy()

    assert set(test["subject"]) == {9, 10}
    assert len(test) == 80
    assert int((test["candidate_label"] == 1).sum()) == 20
    assert int((test["candidate_label"] == 0).sum()) == 60

    # Save the evaluation plan before reading test images or scores.
    plan = {
        "checkpoint": str(checkpoint_path.relative_to(project)),
        "checkpoint_sha256": hashlib.sha256(
            checkpoint_path.read_bytes()
        ).hexdigest(),
        "manifest_sha256": manifest_hash,
        "selection": (
            "Weighted pilot selected by validation balanced accuracy "
            "and fall F1; epoch selected by validation loss."
        ),
        "aggregation": "mean frame logits within each window",
        "decision": "argmax; no threshold tuning on test",
        "normalization": norm,
        "label_status": (
            "proposed window labels; not fully visually verified"
        ),
        "ai_assistance": (
            "Evaluation script drafted with ChatGPT/Codex assistance."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    plan_path = output / "evaluation_plan.json"

    if plan_path.exists():
        assert json.loads(
            plan_path.read_text(encoding="utf-8")
        ) == plan
    else:
        plan_path.write_text(
            json.dumps(plan, indent=2), encoding="utf-8"
        )

    # Read test images and apply the saved TRAIN normalization.
    root = Path(config["dataset_root"])
    if not root.is_absolute():
        root = project / root

    images = {}
    times_by_subject = {}
    source_hashes = {}

    for subject in config["test_subjects"]:
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
        times_by_subject[subject] = times

    # Predict without updating model parameters.
    model = ThermalCNN()
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    predictions = []

    with torch.inference_mode():
        for row in test.itertuples(index=False):
            subject = int(row.subject)
            left = int(row.start_row_0based)
            right = int(row.stop_row_exclusive)
            times = times_by_subject[subject]

            assert 0 <= left < right <= len(times)
            assert right - left == int(row.n_frames)
            assert times[left] + 1e-6 >= row.start_s
            assert times[right - 1] < row.end_s + 1e-6

            logits = model(
                images[subject][left:right]
            ).mean(dim=0)

            assert torch.isfinite(logits).all().item()
            predictions.append(int(logits.argmax().item()))

    # Calculate and save window-level test metrics.
    truth = test["candidate_label"].to_numpy(dtype=np.int64)

    precision, recall, f1, _ = precision_recall_fscore_support(
        truth,
        predictions,
        average="binary",
        pos_label=1,
        zero_division=0,
    )

    matrix = confusion_matrix(
        truth, predictions, labels=[0, 1]
    )
    tn, fp, fn, tp = map(int, matrix.ravel())

    metrics = {
        "evaluation_unit": "4-second window",
        "subjects": config["test_subjects"],
        "windows": len(test),
        "accuracy": float(accuracy_score(truth, predictions)),
        "balanced_accuracy": float(
            balanced_accuracy_score(truth, predictions)
        ),
        "fall_precision": float(precision),
        "fall_recall": float(recall),
        "fall_f1": float(f1),
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp,
        "thermal_csv_sha256": source_hashes,
        "limits": (
            "Pilot on proposed labels from two held-out subjects; "
            "not proof of real-world performance."
        ),
    }

    test.assign(
        predicted_label=predictions
    ).to_csv(output / "predictions.csv", index=False)

    pd.DataFrame(
        matrix,
        index=["actual_nonfall", "actual_fall"],
        columns=["predicted_nonfall", "predicted_fall"],
    ).to_csv(output / "confusion_matrix.csv")

    metrics_path.write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    for name in (
        "accuracy", "balanced_accuracy",
        "fall_precision", "fall_recall", "fall_f1",
    ):
        print(f"{name}: {metrics[name]:.6f}")

    print(f"TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print("Saved:", output)
    print("Training performed: False")


if __name__ == "__main__":
    main()
