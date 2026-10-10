import tempfile
import unittest
from pathlib import Path
from visibility_observatory.exa_assisted import capture
from visibility_observatory.gemini import OUTPUT_TOKENS

BENCH={"version":"1.0","queries":[{"id":"G01","query":"library"},{"id":"G02","query":"converter"}]}

class Tests(unittest.TestCase):
    def test_provenance_and_separation(self):
        def search(provider,key,query,depth,opener):
            return [{"url":"https://example.org/item","title":"Candidate"}]
        def model(key,bench,**kwargs):
            self.assertIn("[1] Candidate | https://example.org/item",kwargs["context"])
            return {"samples":[{"query_id":bench["queries"][kwargs["start_index"]]["id"],
                "status":"complete","answer":"Try MDAnalysis","finish_reason":"STOP"}]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"observations.json"
            d=capture("gemini-secret","exa-secret",BENCH,output=p,count=2,top_k=1,
                      search=search,model_call=model,pause=lambda x:None)
            self.assertEqual(d["complete_count"],2)
            self.assertEqual(d["mode"],"exa_assisted")
            self.assertEqual(d["output_token_limit"],OUTPUT_TOKENS)
            self.assertEqual([x["query_id"] for x in d["samples"]],["G01","G02"])
            self.assertNotIn("secret",p.read_text())
    def test_short_retrieval_never_calls_gemini(self):
        def search(provider,key,query,depth,opener):
            return [{"url":"https://example.org/one","title":"One result"}]
        def forbidden(*args,**kwargs):
            raise AssertionError("Gemini must not receive incomplete retrieval context")
        with tempfile.TemporaryDirectory() as tmp:
            data=capture("gemini-secret","exa-secret",BENCH,
                output=Path(tmp)/"response.json",count=1,top_k=5,
                search=search,model_call=forbidden,pause=lambda _:None)
            self.assertEqual(data["complete_count"],0)
            self.assertEqual(data["samples"][0]["status"],"partial")
    def test_missing_key_does_not_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                capture("x",None,BENCH,output=Path(tmp)/"file.json")
