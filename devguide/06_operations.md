# Operations, local development and Codex handoff

## Bootstrap / validation

```bash
git clone https://github.com/uibcdf/moli-visibility-observatory.git
cd moli-visibility-observatory
python -m unittest discover -s tests -v
python -m visibility_observatory.publish --output build/public-site
python -m http.server 8000 --directory build/public-site
```

Python standard library is sufficient for current commands. Check packaging and Python compatibility before changing dependencies. Do **not** use actual API credentials in unit tests.

An offline manifest can be generated and checked with the synthetic fixture; this does not query a provider or retain original answers:

```bash
python -m visibility_observatory.evidence_manifest --run examples/sample.json --output /tmp/moli-sample.manifest.json
python -m visibility_observatory.evidence_manifest --run examples/sample.json --check /tmp/moli-sample.manifest.json
```

For real captures, keep the source file and manifest in an access-controlled location only after the applicable provider terms, privacy and retention period have been approved. The manifest is marked `internal_unreviewed` and must not be fed into the public Pages workflow. Verification needs the exact capture and benchmark bytes; the command does not download expiring Actions artifacts or merge runs.

To reconcile two already-local captures of the **same provider/model/protocol**, use an internal destination outside the Pages input tree:

```bash
python -m visibility_observatory.evidence_merge --run /path/to/run-1.json --run /path/to/run-2.json --output /tmp/moli-merge.json
python -m visibility_observatory.evidence_merge --run /path/to/run-1.json --run /path/to/run-2.json --check /tmp/moli-merge.json
```

The command makes no provider requests. It rejects duplicate capture files, incompatible settings and multiple complete attempts for one query. It retains only status/provenance metadata; keep every permitted original capture separately for reconstruction. This is not an automatic retry launcher or a public summary.

To verify a web summary against an already-local capture, after retention rights are cleared, run:

```bash
python -m visibility_observatory.evidence_recompute --run /path/to/web-run.json --summary /path/to/reviewed.summary.json --output /tmp/moli-reconciliation.json
python -m visibility_observatory.evidence_recompute --run /path/to/web-run.json --summary /path/to/reviewed.summary.json --check /tmp/moli-reconciliation.json
```

This reads only local files and writes an internal hash/check report. A matching report does not prove that the supplied file came from the Actions run URL in the summary, does not review editorial titles or scientific relevance, and does not authorize public release. Do not download historical provider artifacts merely to run this command while retention rights remain unresolved.

## Manual experiments (require consent, validated free-tier quota and secrets)

- `Collect opt-in free-provider baseline`: Tavily/Exa ranked search, limited query count.
- `Gemini complete benchmark (checkpointed)`: closed-book Gemini with declared model and count; per-run checkpoints.
- `Gemini + Exa assisted pilot`: Exa top five titles/URLs → Gemini, optional `category=interoperability` for I01–I05.
- `Publish reviewed visibility summaries`: builds/deploys public Pages using committed reviewed summaries.
- `Validate visibility observatory`: tests and synthetic preview.

Repository secrets: `TAVILY_API_KEY`, `EXA_API_KEY`, `GEMINI_API_KEY`, optionally `BRAVE_SEARCH_API_KEY`. Access and billing must be confirmed out-of-band; credentials are never copied into chats, commits or logs. The project owner has **not** authorized billable operations. Never trigger a large live benchmark merely because tests pass.

## Troubleshooting

- **HTTP 429:** stop requests. Examine allowed quota/rate data in authorized provider console; do not guess at reset or silently switch to paid tier.
- **HTTP 502/503/504:** bounded transient retry only, record attempts; continue with explicit missingness when allowed.
- **MAX_TOKENS:** mark partial, modify a versioned prompt profile, do not count as absent mention.
- **Timeout:** differentiate Exa fetch and Gemini generation; current Gemini transport timeout is 120 seconds.
- **Incomplete Exa top-five:** mark retrieval partial; do not represent it as a matched five-source Gemini comparison.
- **Failed Pages:** check workflow and repository Pages configuration; do not claim site is live until verified.
- **Actions artifacts:** 30-day retention is not permanent scientific evidence.

## Safe continuation procedure

1. Read all `devguide/` files and issues #1/#2, then inspect `git status`, current commit, workflows and source. Identify stale docs and any upstream changes.
2. Execute offline tests; locate failures before modifying behavior.
3. Establish one scoped milestone with acceptance criteria from roadmap; avoid unrelated rearchitecture.
4. Use small changes and mocked network tests; preserve old run data.
5. Check Actions results after pushing. **No autonomous paid API runs, secret changes or scheduling without explicit owner authorization.**
6. Update checkpoint, roadmap and decision log with verified outcomes, run links and known limitations. Link relevant issues.
7. At handoff, report changes, test commands and actual results, unresolved blockers and the next safe step.

## Developer handoff note template

Date; branch/commit; current milestone; files changed; local CI; hosted CI run; provider calls (if any); artifact/run IDs; cost/quota status; protocol/schema changes; next action; blockers. Avoid ambiguous 'done' if only the code was written.
