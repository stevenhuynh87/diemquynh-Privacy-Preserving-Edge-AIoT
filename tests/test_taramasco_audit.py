"""Regression checks with generated CSV fixtures, never author data."""

import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from data.taramasco import SENSORS, TaramascoDS, to_seconds


class TestTaramascoAudit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "subject_1").mkdir()
        self.dataset = TaramascoDS(self.root)

    def write_sensor(self, sensor, text):
        path = self.root / "subject_1" / f"{sensor}.csv"
        path.write_text(text, encoding="utf-8")
        return path

    def test_root_annotations_excluded_and_inputs_unchanged(self):
        for sensor in SENSORS:
            self.write_sensor(sensor, "100,1\n101,2\n102,3\n")
            (self.root / f"{sensor}.csv").write_text(
                "418,267\n526,340\n", encoding="utf-8"
            )
        (self.root / "fall.csv").write_text(
            "100,200\n101,201\n", encoding="utf-8"
        )
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.root.rglob("*.csv")
        }
        audit = self.dataset.audit_all()
        self.assertEqual(len(audit), 4)
        self.assertEqual(set(audit["subject"]), {1})
        self.assertEqual(set(audit["sensor"]), set(SENSORS))
        self.assertTrue((audit["rows"] == 3).all())
        self.assertTrue((audit["approx_Hz"] == 1.0).all())
        self.assertEqual(
            before,
            {
                path: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*.csv")
            },
        )
        with self.assertRaisesRegex(ValueError, "annotations"):
            self.dataset.audit_sensor(None, "ir_camera")

    def test_ragged_radar_and_empty_frame_timestamp_preserved(self):
        self.write_sensor(
            "radar",
            "100\n100.1,1,2,3,4,5,6,7\n"
            "100.2,1,2,3,4,5,6,7,8,9,10,11,12,13,14\n",
        )
        info = self.dataset.audit_sensor(1, "radar")
        self.assertEqual(info["status"], "ok")
        self.assertEqual(info["rows"], 3)
        self.assertEqual(info["valid_timestamps"], 3)
        self.assertEqual(info["min_cols"], 1)
        self.assertEqual(info["n_cols"], 15)
        self.assertTrue(info["variable_width"])
        self.assertAlmostEqual(info["approx_Hz"], 10.0)

    def test_backwards_timestamp_not_hidden_by_positive_median(self):
        self.write_sensor(
            "accelerometer", "100,1\n100.016,2\n33.032,3\n33.048,4\n"
        )
        info = self.dataset.audit_sensor(1, "accelerometer")
        self.assertEqual(info["backwards_steps"], 1)
        self.assertEqual(info["status"], "REVIEW_TIMESTAMP_ERRORS")
        self.assertAlmostEqual(info["median_dt"], 0.016)
        self.assertNotIn("approx_Hz", info)

    def test_repeated_timestamp_suppresses_frequency(self):
        self.write_sensor("lidar", "100,1\n100,2\n100.1,3\n")
        info = self.dataset.audit_sensor(1, "lidar")
        self.assertEqual(info["repeated_timestamps"], 1)
        self.assertNotIn("approx_Hz", info)

    def test_invalid_time_retains_position_without_bridging(self):
        self.write_sensor("ir_camera", "100,1\nbad,2\n102,3\n")
        info = self.dataset.audit_sensor(1, "ir_camera")
        self.assertEqual(info["rows"], 3)
        self.assertEqual(info["invalid_timestamps"], 1)
        self.assertEqual(info["valid_timestamps"], 2)
        self.assertNotIn("median_dt", info)
        self.assertNotIn("approx_Hz", info)

    def test_blank_row_reported_without_bridging(self):
        self.write_sensor("ir_camera", "100,1\n\n102,3\n")
        info = self.dataset.audit_sensor(1, "ir_camera")
        self.assertEqual(info["rows"], 3)
        self.assertEqual(info["blank_rows"], 1)
        self.assertEqual(info["invalid_timestamps"], 1)
        self.assertNotIn("approx_Hz", info)

    def test_single_timestamp_cannot_estimate_frequency(self):
        self.write_sensor("radar", "100\n")
        info = self.dataset.audit_sensor(1, "radar")
        self.assertEqual(info["status"], "INSUFFICIENT_TIMESTAMPS")
        self.assertNotIn("approx_Hz", info)

    def test_large_gap_retained_and_flagged(self):
        self.write_sensor("lidar", "100,1\n101,2\n102,3\n110,4\n")
        info = self.dataset.audit_sensor(1, "lidar")
        self.assertEqual(info["large_gaps"], 1)
        self.assertEqual(info["large_gap_factor"], 3.0)
        self.assertEqual(info["status"], "REVIEW_IRREGULAR_SAMPLING")
        self.assertEqual(info["median_dt"], 1.0)
        self.assertEqual(info["approx_Hz"], 1.0)
        self.assertEqual(info["duration"], 10.0)

    def test_numeric_strings_not_guessed_as_calendar_dates(self):
        original = pd.Series(["100", "2026-10-16", "102"])
        converted = to_seconds(original)
        self.assertIsNotNone(converted)
        values, span = converted
        np.testing.assert_equal(values, [100.0, np.nan, 102.0])
        self.assertEqual(span, 2.0)
        self.assertEqual(original.iloc[1], "2026-10-16")


if __name__ == "__main__":
    unittest.main()
