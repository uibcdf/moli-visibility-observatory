import unittest
from visibility_observatory.__main__ import compute
BENCH={'version':'1.0','queries':[{'id':'G01','family':'general'}]}
BASE={'schema_version':'1','benchmark_version':'1.0','track':'web_search','provider':'test','collected_at_utc':'2026-10-10T00:00:00Z'}
class TestMetrics(unittest.TestCase):
    def test_partial_not_miss(self):
        m=compute({**BASE,'samples':[{'query_id':'G01','status':'partial','results':[]}]},BENCH,10)
        self.assertIsNone(m['presence'])
    def test_complete(self):
        results=[{'url':'https://example.org/'+str(i)} for i in range(10)]
        results[2]={'url':'https://github.com/uibcdf/molsysmt'}
        m=compute({**BASE,'samples':[{'query_id':'G01','status':'complete','results':results}]},BENCH,10)
        self.assertEqual(m['presence'],1)
        self.assertAlmostEqual(m['mrr'],1/3)
    def test_agent_rejected(self):
        with self.assertRaises(ValueError):compute({**BASE,'track':'agent_recommendation'},BENCH,10)
