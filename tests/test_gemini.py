import io
import json
import unittest
import urllib.error
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
    def test_search_disabled_without_billing_review(self):
        with self.assertRaisesRegex(ValueError, "billing review"):
            collect("secret", BENCH, mode="google_search")
    def test_truncated_answer_is_partial(self):
        def truncated(req, timeout):
            return Response(b'{"candidates":[{"content":{"parts":[{"text":"An incomplete recommendation"}]},"finishReason":"MAX_TOKENS"}]}')
        result = collect("secret", BENCH, opener=truncated)
        self.assertEqual(result["samples"][0]["status"], "partial")
    def test_http_status_is_preserved_without_provider_body(self):
        def fail(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 429, "private provider details", {}, None)
        result = collect("secret", BENCH, opener=fail)
        sample = result["samples"][0]
        self.assertEqual(sample["http_status"], 429)
        self.assertEqual(sample["error_type"], "HTTPError")
        self.assertNotIn("private provider details", json.dumps(result))
    def test_transient_503_retries_once(self):
        calls = []
        def transport(req, timeout):
            calls.append(1)
            if len(calls) == 1:
                raise urllib.error.HTTPError(req.full_url, 503, "temporary", {}, None)
            return Response(b'{"candidates":[{"content":{"parts":[{"text":"MDAnalysis"}]},"finishReason":"STOP"}]}')
        result = collect("secret", BENCH, opener=transport, pause=lambda _: None)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["samples"][0]["status"], "complete")
        self.assertEqual(result["samples"][0]["attempts"], 2)
    def test_persistent_503_stops_after_two(self):
        calls = []
        def fail(req, timeout):
            calls.append(1)
            raise urllib.error.HTTPError(req.full_url, 503, "temporary", {}, None)
        result = collect("secret", BENCH, opener=fail, pause=lambda _: None)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["samples"][0]["http_status"], 503)
    def test_bad_limits(self):
        with self.assertRaises(ValueError):
            collect("secret",BENCH,max_queries=21)
