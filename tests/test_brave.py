import io
import json
import unittest
from visibility_observatory.brave import collect
BENCH={"version":"1.0","queries":[{"id":"G01","query":"test molecular analysis"}]}
class FakeResponse(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self,*args): self.close()
class BraveTests(unittest.TestCase):
    def test_missing_key_fails_without_call(self):
        with self.assertRaises(ValueError):collect(None,BENCH)
    def test_complete_ten(self):
        def fake(req,timeout):
            self.assertEqual(req.get_header("X-subscription-token"),"secret")
            self.assertNotIn("secret",req.full_url)
            return FakeResponse(json.dumps({"web":{"results":[{"url":f"https://example.org/{i}","title":"x"} for i in range(10)]}}).encode())
        r=collect("secret",BENCH,opener=fake)
        self.assertEqual(r["samples"][0]["status"],"complete")
        self.assertNotIn("secret",json.dumps(r))
    def test_partial_does_not_become_absence(self):
        r=collect("secret",BENCH,opener=lambda req,timeout:FakeResponse(b'{"web":{"results":[]}}'))
        self.assertEqual(r["samples"][0]["status"],"partial")
if __name__=="__main__":unittest.main()
