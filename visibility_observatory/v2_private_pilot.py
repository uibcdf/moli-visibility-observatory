"""Run one authorized V2 prompt and encrypt the capture before artifact upload.

The public Actions log must never contain provider answers, ranked URLs or keys.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from visibility_observatory.agent_batch import run_batch
from visibility_observatory.benchmark_run import load_frozen
from visibility_observatory.exa_assisted import capture
from visibility_observatory.providers import collect


QUERY_INDEX = 1  # Frozen V2 S02A, the predeclared primary unbranded pilot.
CERT = Path(__file__).resolve().parents[1] / ".github/v2-pilot/recipient-cert.pem"
TRACKS = ("tavily", "exa", "gemini_closed", "gemini_exa")


def run_one(track, output):
    if track not in TRACKS:
        raise ValueError("Unsupported pilot track")
    benchmark, digest = load_frozen("v2")
    if benchmark["queries"][QUERY_INDEX]["id"] != "S02A":
        raise ValueError("Pilot query identity changed")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="moli-v2-pilot-") as directory:
        raw = Path(directory) / "capture.json"
        if track in ("tavily", "exa"):
            key = os.environ.get("TAVILY_API_KEY" if track == "tavily" else "EXA_API_KEY")
            result = collect(track, key, benchmark, max_queries=1,
                             start_index=QUERY_INDEX, benchmark_sha256=digest)
            raw.write_text(json.dumps(result, ensure_ascii=False) + "\n", encoding="utf-8")
        elif track == "gemini_closed":
            run_batch(os.environ.get("GEMINI_API_KEY"), benchmark, output=raw,
                      model="gemini-3.8-flash", start_index=QUERY_INDEX, count=1,
                      benchmark_sha256=digest)
        else:
            capture(os.environ.get("GEMINI_API_KEY"), os.environ.get("EXA_API_KEY"),
                    benchmark, output=raw, model="gemini-3.8-flash",
                    start_index=QUERY_INDEX, count=1, benchmark_sha256=digest)
        subprocess.run(["openssl", "cms", "-encrypt", "-binary", "-aes-256-cbc",
                        "-in", str(raw), "-outform", "DER", "-out", str(output),
                        str(CERT)], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    print("Encrypted one-query V2 capture; inspect privately after download")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", choices=TRACKS, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        run_one(args.track, args.output)
    except Exception as error:
        # Avoid provider exception strings, request headers and response bodies in public logs.
        print("Pilot failed before encrypted capture: " + type(error).__name__)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
