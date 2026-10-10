import json
import tempfile
import unittest
from pathlib import Path
from visibility_observatory.agent_batch import run_batch
BENCH={"version":"1.0","queries":[{"id":f"I{i:02}","query":"test"} for i in range(4)]}
class BatchTests(unittest.TestCase):
    def test_503_continues_and_checkpoints(self):
        def fake(key,bench,*,start_index,max_queries,model,mode):
            i=start_index
            sample={"query_id":bench["queries"][i]["id"],"status":"error" if i==1 else "complete"}
            if i==1:sample["http_status"]=503
            else:sample["answer"]="MDAnalysis"
            return {"samples":[sample]}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"result.json"
            x=run_batch("secret",BENCH,output=path,count=4,collect_one=fake,pause=lambda t:None)
            self.assertEqual([s["query_id"] for s in x["samples"]],["I00","I01","I02","I03"])
            self.assertEqual(x["failed_count"],1)
            self.assertEqual(json.loads(path.read_text())["complete_count"],3)
    def test_quota_429_stops(self):
        checkpoints=[]
        def fake(key,bench,*,start_index,max_queries,model,mode):
            checkpoints.append(json.loads(path.read_text()))
            return {"samples":[{"query_id":bench["queries"][start_index]["id"],"status":"error","http_status":429}]}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"result.json"
            x=run_batch("secret",BENCH,output=path,count=4,collect_one=fake,pause=lambda t:None)
            self.assertEqual(checkpoints[0]["protocol_version"],"concise-v2")
            self.assertEqual(checkpoints[0]["output_token_limit"],4096)
            self.assertEqual(json.loads(path.read_text())["protocol_version"],"concise-v2")
            self.assertEqual(json.loads(path.read_text())["output_token_limit"],4096)
            self.assertEqual(x["unattempted_count"],3)
            self.assertEqual(x["stop_reason"],"provider_nonretryable_error")
