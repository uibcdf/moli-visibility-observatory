import json
import tempfile
import unittest
from pathlib import Path
from visibility_observatory.publish import validated_records,render

RECORD={"schema_version":"baseline-summary-v1","date":"2026-10-10","track":"web_search","provider":"tavily-search-api","mode":"basic","run_url":"https://github.com/example/actions/runs/1","benchmark_version":"1.0","queries_requested":20,"complete":20,"partial":0,"errors":0,"k":10,"presence_at_10":0.05,"mrr_at_10":0.025,"hits":[{"query_id":"D05","rank":2,"url":"https://www.uibcdf.org/molsysmt/","title":"MolSysMT"}],"limitations":["single provider"]}

class PublishTests(unittest.TestCase):
    def test_validated_record(self):
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/"baseline.summary.json";f.write_text(json.dumps(RECORD))
            self.assertEqual(len(validated_records(temp)),1)
    def test_inconsistent_metrics_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/"baseline.summary.json";f.write_text(json.dumps({**RECORD,"presence_at_10":0.2}))
            with self.assertRaises(ValueError): validated_records(temp)
    def test_synthetic_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/"baseline.summary.json";f.write_text(json.dumps({**RECORD,"synthetic":True}))
            with self.assertRaises(ValueError): validated_records(temp)
    def test_site_contains_observation_disclaimer(self):
        with tempfile.TemporaryDirectory() as temp:
            render([RECORD],temp)
            content=(Path(temp)/"index.html").read_text()
            self.assertIn("AI-agent recommendation",content)
            self.assertIn("5%",content)
