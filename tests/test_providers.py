import io
import json
import unittest

from visibility_observatory.providers import collect

BENCH = {"version": "1.0", "queries": [{"id": "G01", "query": "molecular modeling interoperability"}]}

class Stream(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

class ProviderTests(unittest.TestCase):
    def test_missing_credentials(self):
        for provider in ("tavily", "exa"):
            with self.subTest(provider=provider), self.assertRaises(ValueError):
                collect(provider, None, BENCH)
    def test_ranked_results_and_secret_protection(self):
        for provider in ("tavily", "exa"):
            with self.subTest(provider=provider):
                def mock(request, timeout):
                    self.assertEqual(request.get_method(), "POST")
                    self.assertNotIn("secret", request.full_url)
                    data = json.loads(request.data)
                    self.assertTrue("max_results" in data if provider == "tavily" else "numResults" in data)
                    return Stream(json.dumps({"results":[{"url":f"https://example.org/{i}", "title":"Example"} for i in range(10)]}).encode())
                run = collect(provider, "secret", BENCH, opener=mock)
                self.assertEqual(run["samples"][0]["status"], "complete")
                self.assertNotIn("secret", json.dumps(run))
    def test_partial_is_unknown(self):
        run = collect("exa", "secret", BENCH, opener=lambda request,timeout: Stream(b'{"results":[]}'))
        self.assertEqual(run["samples"][0]["status"], "partial")
    def test_query_cap(self):
        with self.assertRaises(ValueError):
            collect("exa", "secret", BENCH, max_queries=21)

if __name__ == "__main__":
    unittest.main()
