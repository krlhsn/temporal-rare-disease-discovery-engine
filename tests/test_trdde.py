"""Automated tests for the TRDDE synthetic research prototype."""

import json
import tempfile
import unittest
from pathlib import Path

import main


class DatasetTests(unittest.TestCase):
    def test_builtin_dataset_passes_validation(self):
        self.assertEqual(main.validate_dataset(), [])

    def test_expected_demo_dataset_size(self):
        self.assertEqual(len(main.PROFILES), 10)
        self.assertEqual(len(main.FEATURES), 20)
        self.assertEqual(
            sum(len(profile.observations) for profile in main.PROFILES), 50
        )

    def test_all_profiles_have_unique_observation_features(self):
        for profile in main.PROFILES:
            feature_ids = [item.feature_id for item in profile.observations]
            self.assertEqual(len(feature_ids), len(set(feature_ids)))


class SimilarityTests(unittest.TestCase):
    def test_weighted_jaccard_identical_sets_is_one(self):
        weights = {"A": 1.0, "B": 2.0}
        score = main.weighted_jaccard({"A", "B"}, {"A", "B"}, weights)
        self.assertAlmostEqual(score, 1.0)

    def test_weighted_jaccard_disjoint_sets_is_zero(self):
        weights = {"A": 1.0, "B": 1.0}
        score = main.weighted_jaccard({"A"}, {"B"}, weights)
        self.assertAlmostEqual(score, 0.0)

    def test_weighted_jaccard_empty_union_is_zero(self):
        self.assertEqual(main.weighted_jaccard(set(), set(), {}), 0.0)

    def test_interval_overlap_includes_shared_boundary(self):
        self.assertTrue(main.intervals_overlap((1, 3), (3, 5)))

    def test_separate_intervals_do_not_overlap(self):
        self.assertFalse(main.intervals_overlap((1, 2), (3, 4)))

    def test_profile_comparison_for_profiles_b_and_d(self):
        profile_b = main.PROFILES[1]
        profile_d = main.PROFILES[3]
        result = main.compare_profiles(profile_b, profile_d)
        self.assertEqual(
            result.shared_feature_ids, ("SYN-001", "SYN-003")
        )
        self.assertAlmostEqual(result.temporal_compatibility, 1.0)
        self.assertEqual(len(result.interval_details), 2)


class DiscoveryTests(unittest.TestCase):
    def test_candidate_pairs_meet_discovery_rule(self):
        candidates = main.discover_candidates()
        self.assertEqual(len(candidates), 14)
        for item in candidates:
            self.assertGreaterEqual(len(item.shared_feature_ids), 2)
            self.assertGreaterEqual(len(item.shared_systems), 2)

    def test_hypothesis_ids_are_stable_and_status_is_unvalidated(self):
        items = main.generate_hypotheses()
        self.assertEqual(len(items), 14)
        self.assertEqual(items[0].hypothesis_id, "TRDDE-H001")
        self.assertTrue(all(item.status == "Unvalidated research question" for item in items))

    def test_report_contains_limitations_and_candidate_pairs(self):
        report = main.build_research_report()
        self.assertEqual(report["version"], main.VERSION)
        self.assertEqual(report["dataset"]["profile_count"], 10)
        self.assertEqual(report["dataset"]["observation_count"], 50)
        self.assertEqual(len(report["candidate_pairs"]), 14)
        self.assertTrue(report["limitations"])
        self.assertIn("not a diagnostic", report["safety_notice"].lower())

    def test_export_creates_valid_json(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "report.json"
            result_path = main.export_report(destination)
            parsed = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["short_name"], "TRDDE")
            self.assertEqual(len(parsed["hypotheses"]), 14)


if __name__ == "__main__":
    unittest.main()
