import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


def build_subject(times, falls, raw_indices, review_events, rng):
    times = np.asarray(times, dtype=np.float64)
    falls = np.asarray(falls, dtype=np.float64)
    dt = np.diff(times)

    if len(times) < 2 or not np.isfinite(times).all() or not (dt > 0).all():
        raise ValueError("Thermal timestamps must be finite and strictly increasing")

    if not np.isfinite(falls).all():
        raise ValueError("Fall timestamps must be finite")

    max_gap = 3 * float(np.median(dt))
    half = 2.0

    # Conservative exclusion zones for non-fall candidates.
    blocked = [(float(t - 4), float(t + 4)) for t in falls]

    for event in review_events:
        value = float(raw_indices[event - 1])

        if not np.isfinite(value) or not value.is_integer():
            raise ValueError("Review event has an invalid supplied frame index")

        # Protect both interpretations without choosing an index base.
        for index in (int(value) - 1, int(value)):
            if 0 <= index < len(times):
                blocked.append((
                    float(times[index] - 4),
                    float(times[index] + 4),
                ))

    def window(center):
        start = float(center - half)
        end = float(center + half)

        if start < times[0] or end > times[-1]:
            return None, "outside_recording"

        left = int(np.searchsorted(times, start, side="left"))
        right = int(np.searchsorted(times, end, side="left"))

        # Include neighboring timestamps when checking boundary gaps.
        local = times[max(0, left - 1):min(len(times), right + 1)]

        if right - left < 2 or np.any(np.diff(local) > max_gap):
            return None, "insufficient_frames_or_large_gap"

        return {
            "start_s": start,
            "end_s": end,
            "start_row_0based": left,
            "stop_row_exclusive": right,
            "n_frames": right - left,
            "label_status": "candidate_unreviewed",
        }, "ok"

    positive = []
    excluded = []

    for event, center in enumerate(falls, 1):
        row, reason = window(center)

        if event in review_events:
            reason = "annotation_conflict_pending_review"

        if reason != "ok":
            excluded.append({"event": event, "reason": reason})
        else:
            positive.append(dict(row, candidate_label=1, event=event))

    negative = []

    # Non-overlapping candidate windows on a four-second grid.
    for center in np.arange(times[0] + half, times[-1] - half, 2 * half):
        start, end = center - half, center + half

        if any(start < b and end > a for a, b in blocked):
            continue

        row, reason = window(center)

        if reason == "ok":
            negative.append(dict(row, candidate_label=0, event=""))

    target = 3 * len(positive)
    chosen = rng.permutation(len(negative))[:target]
    selected = [negative[int(i)] for i in chosen]
    selected.sort(key=lambda row: row["start_s"])

    return positive + selected, excluded, len(negative), target


def main():
    project = Path(__file__).resolve().parents[1]
    config_path = project / "configs/sprint1_split.json"
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))

    root = Path(config["dataset_root"])
    if not root.is_absolute():
        root = project / root

    groups = {
        name: config[f"{name}_subjects"]
        for name in ("train", "validation", "test")
    }

    subjects = [subject for group in groups.values() for subject in group]

    if len(subjects) != len(set(subjects)) or set(subjects) != set(range(1, 11)):
        raise ValueError("Expected subjects 1-10, each in exactly one split")

    def source(folder, stem):
        matches = [
            path for path in folder.glob("*.csv")
            if path.stem.lower() == stem
        ]
        if len(matches) != 1:
            raise ValueError(f"Expected one {stem}.csv in {folder}")
        return matches[0]

    fall_files = [
        path for path in root.glob("*.csv")
        if path.stem.lower() in ("fall", "falls")
    ]

    if len(fall_files) != 1:
        raise ValueError("Expected exactly one fall.csv or falls.csv")

    falls = pd.read_csv(
        fall_files[0], header=None
    ).to_numpy(dtype=np.float64)

    raw = pd.read_csv(
        source(root, "ir_camera"), header=None
    ).to_numpy(dtype=np.float64)

    if falls.shape != (10, 10) or raw.shape != falls.shape:
        raise ValueError(
            f"Unexpected annotation shapes: {falls.shape}, {raw.shape}"
        )

    reviews = {}

    for review in config.get("pending_reviews", []):
        subject = int(review["subject"])
        event = int(review["event"])

        if subject not in subjects or not 1 <= event <= len(falls):
            raise ValueError("Pending review references an unknown subject/event")

        reviews.setdefault(subject, set()).add(event)

    rng = np.random.default_rng(int(config["seed"]))
    rows = []
    exclusions = []
    counts = []

    for split, group in groups.items():
        for subject in group:
            path = source(root / f"subject_{subject}", "ir_camera")

            times = pd.read_csv(
                path, header=None, usecols=[0]
            ).iloc[:, 0].to_numpy(dtype=np.float64)

            windows, omitted, pool, target = build_subject(
                times,
                falls[:, subject - 1],
                raw[:, subject - 1],
                reviews.get(subject, set()),
                rng,
            )

            rows.extend(
                dict(subject=subject, split=split, **row)
                for row in windows
            )

            exclusions.extend(
                dict(subject=subject, split=split, **row)
                for row in omitted
            )

            n_fall = sum(row["candidate_label"] == 1 for row in windows)
            n_nonfall = len(windows) - n_fall

            counts.append({
                "subject": subject,
                "split": split,
                "fall": n_fall,
                "nonfall": n_nonfall,
                "negative_pool": pool,
                "negative_shortfall": max(0, target - n_nonfall),
            })

    out = project / "reports"
    out.mkdir(exist_ok=True)

    fields = [
        "subject", "split", "candidate_label", "event",
        "start_s", "end_s", "start_row_0based",
        "stop_row_exclusive", "n_frames", "label_status",
    ]

    with (out / "thermal_window_candidates.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "training_ready": False,
        "config": config,
        "window_seconds": 4,
        "target_nonfall_per_fall": 3,
        "negative_guard_seconds_from_anchor": 4,
        "maximum_gap_multiple_of_median_dt": 3,
        "counts": counts,
        "excluded_events": exclusions,
        "interval": "[start_s, end_s)",
        "note": "Proposed window labels only; no per-frame ground truth assigned.",
    }

    (out / "thermal_window_candidates_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    for split in groups:
        selected = [row for row in rows if row["split"] == split]
        fall_count = sum(row["candidate_label"] == 1 for row in selected)
        print(
            f"{split}: fall={fall_count}, "
            f"nonfall={len(selected) - fall_count}"
        )

    shortfall = sum(row["negative_shortfall"] for row in counts)
    print(f"Excluded events: {len(exclusions)}")
    print(f"Negative shortfall: {shortfall}")
    print("Training ready: False; original files unchanged.")
    print("Saved: reports/thermal_window_candidates.csv")
    print("Saved: reports/thermal_window_candidates_summary.json")


if __name__ == "__main__":
    main()
