"""The manual pilot must not upload readable provider output."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from visibility_observatory.v2_private_pilot import run_one


class PrivatePilotTests(unittest.TestCase):
    def test_one_frozen_query_is_encrypted_before_upload(self):
        marker = "PRIVATE_PROVIDER_RESPONSE_123"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "capture.p7m"
            with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}), patch(
                "visibility_observatory.v2_private_pilot.collect",
                return_value={"answer": marker},
            ) as mocked:
                run_one("tavily", output)
            self.assertEqual(mocked.call_args.kwargs["start_index"], 1)
            self.assertEqual(mocked.call_args.kwargs["max_queries"], 1)
            self.assertTrue(output.is_file())
            self.assertNotIn(marker.encode(), output.read_bytes())
            subprocess.run(["openssl", "cms", "-cmsout", "-inform", "DER",
                            "-in", str(output), "-noout"], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    unittest.main()
