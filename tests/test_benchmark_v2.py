"""Guard the frozen V1 bytes and the V2 sampling design."""

import copy
import hashlib
import json
from pathlib import Path
import unittest

from visibility_observatory.benchmark_v2 import validate_v2


ROOT = Path(__file__).resolve().parents[1]
V1_SHA256 = "733c7280bee7e06f08091c77b542e80b43a77d2a41f9f455d31599194fc36071"
V2_SHA256 = "fab3c490c1ff158f0ae4528bf147c8aea216da527c2d65e5e4f4330315ee6335"


class BenchmarkV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "queries/v2.json").read_bytes()
        cls.benchmark = json.loads(cls.source)

    def test_frozen_bytes_and_design(self):
        self.assertEqual(hashlib.sha256((ROOT / "queries/v1.json").read_bytes()).hexdigest(), V1_SHA256)
        self.assertEqual(hashlib.sha256(self.source).hexdigest(), V2_SHA256)
        self.assertEqual(validate_v2(self.benchmark), {
            "primary_unbranded": 30, "negative_control": 6,
            "named_alternative": 6, "spanish_unbranded": 6})

    def test_duplicate_prompt_rejected(self):
        changed = copy.deepcopy(self.benchmark)
        changed["queries"][1]["query"] = changed["queries"][0]["query"]
        with self.assertRaises(ValueError):
            validate_v2(changed)

    def test_branded_primary_rejected(self):
        changed = copy.deepcopy(self.benchmark)
        primary = next(q for q in changed["queries"] if q["id"] == "P01A")
        primary["query"] += " Consider MolSysMT."
        with self.assertRaises(ValueError):
            validate_v2(changed)

    def test_pair_mapping_rejected(self):
        changed = copy.deepcopy(self.benchmark)
        pair = next(q for q in changed["queries"] if q["id"] == "E01")
        pair["paired_with"] = "C01A"
        with self.assertRaises(ValueError):
            validate_v2(changed)

    def test_missing_control_rejected(self):
        changed = copy.deepcopy(self.benchmark)
        changed["queries"] = [q for q in changed["queries"] if q["id"] != "N06"]
        with self.assertRaises(ValueError):
            validate_v2(changed)


if __name__ == "__main__":
    unittest.main()
