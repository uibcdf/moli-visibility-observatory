import io
import json
import unittest
from visibility_observatory.gemini import collect

BENCH={"version":"1.0","queries":[{"id":"G01","query":"best molecular simulation libraries"}]}
class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self,*args): self.close()
class GeminiTests(unittest.TestCase):
    def test_no_key(self):
        with self.assertRaises(ValueError):
            collect("",BENCH)
    def test_closed_book_response(self):
        def fake(req,timeout):
            self.assertNotIn("secret",req.full_url)
            self.assertEqual(req.get_header("X-goog-api-key"),"secret")
            payload=json.loads(req.data)
            self.assertNotIn("tools",payload)
            return Response(json.dumps({"candidates":[{"content":{"parts":[{"text":"Use MDTraj or MDAnalysis."}]},"finishReason":"STOP"}],"usageMetadata":{"totalTokenCount":27}}).encode())
        r=collect("secret",BENCH,opener=fake)
        self.assertEqual(r["samples"][0]["status"],"complete")
        self.assertEqual(r["evaluation_status"],"unadjudicated")
        self.assertNotIn("secret",json.dumps(r))
    def test_search_is_separate_track(self):
        def fake(req,timeout):
            self.assertEqual(json.loads(req.data)["tools"],[{"google_search":{}}])
            return Response(b'{"candidates":[{"content":{"parts":[{"text":"MDAnalysis"}]}}]}')
        result=collect("secret",BENCH,mode="google_search",opener=fake)
        self.assertEqual(result["track"],"agent_recommendation")
        self.assertEqual(result["mode"],"google_search")
    def test_bad_limits(self):
        with self.assertRaises(ValueError):
            collect("secret",BENCH,max_queries=21)
