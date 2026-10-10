import tempfile
import unittest
from pathlib import Path
from visibility_observatory.agent_publish import read_agent_summaries,render_agents

class AgentPublishTests(unittest.TestCase):
    def test_existing_reviewed_baseline(self):
        records=read_agent_summaries()
        self.assertTrue(records)
        self.assertEqual(records[0]["model"],"gemini-3.1-flash-lite")
        with tempfile.TemporaryDirectory() as folder:
            render_agents(records,folder)
            self.assertIn("Explicit MolSysMT mentions", (Path(folder)/"agents.html").read_text())
    def test_rate_invalid(self):
        records=read_agent_summaries()
        with tempfile.TemporaryDirectory() as folder:
            src=Path(folder)/"bad.summary.json"
            import json
            src.write_text(json.dumps({**records[0],"explicit_name_mention_rate":0.9}))
            with self.assertRaises(ValueError):read_agent_summaries(folder)
