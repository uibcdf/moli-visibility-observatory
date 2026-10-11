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

The V2 question corpus is frozen but has **no live results**. Validate its schema, strata, pairs and exact SHA-256 offline with:

```bash
python -m visibility_observatory.benchmark_v2
```

The output should report 30 primary, 6 control, 6 named-alternative and 6 Spanish prompts with SHA-256 `fab3c490c1ff158f0ae4528bf147c8aea216da527c2d65e5e4f4330315ee6335`. V1 remains the default of all manual collection workflows. Do not pass V2 to a live client until the activation gates in [methodology](03_methodology.md) are met.

Preview the exact V2 collection order and three bounded segments without credentials or network calls:

```bash
python -m visibility_observatory.benchmark_run
```

The plan lists `(start_index, count)` as `(0, 20)`, `(20, 20)` and `(40, 8)`, each with original query IDs and the frozen file hash. The Tavily/Exa, checkpointed Gemini and Exa-assisted CLIs accept `--benchmark-version v2` and the relevant start/count arguments, but refuse V2 without `--execute-v2`. This switch only prevents accidental local invocation; the owner must still approve a bounded live plan after checking the applicable account terms, quotas and retention rights. Existing manual Actions workflows remain V1 and have no V2 option. Do not feed V2 captures into the existing web metric renderer: it rejects pooled V2 scoring.

Once source retention is permitted, an **offline, internal** V2 analysis of already-local captures from one compatible provider/mode can be written with:

```bash
python -m visibility_observatory.v2_analysis --run /path/to/segment-1.json --run /path/to/segment-2.json --run /path/to/segment-3.json --output /tmp/moli-v2-internal.json
```

The command makes no provider requests. It rejects conflicting complete attempts or mixed tracks/settings, leaves missing observations unevaluable, and reports each stratum and paired comparison separately. For model output it counts only explicit name occurrences; recommendation quality and technical correctness need human review. The report is marked `internal_unreviewed`, omits source URLs and answers, and must not be fed to Pages or published before rights and scientific review.

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

The analogous **closed-book Gemini explicit-mention** check is separate from web search and Exa-assisted interpretation:

```bash
python -m visibility_observatory.evidence_agent_recompute --run /path/to/agent-run.json --summary /path/to/reviewed-agent.summary.json --output /tmp/moli-agent-reconciliation.json
python -m visibility_observatory.evidence_agent_recompute --run /path/to/agent-run.json --summary /path/to/reviewed-agent.summary.json --check /tmp/moli-agent-reconciliation.json
```

It reads already-local answers only, reports hashes/check names, and counts mentions in complete responses. It does not adjudicate recommendations or download historical artifacts. Apply the same retention and access-control gate as for web captures.

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
