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

### Proposed first V2 pilot; not authorized

Use the frozen **primary, unbranded** query `S02A` at zero-based index `1`, one question per experiment: Tavily ranked search, Exa ranked search, Gemini 3.8 Flash closed-book, and Gemini 3.8 Flash with Exa titles/URLs. Run one experiment at a time, inspect its checkpoint/status and provider usage, and stop at a 429 or other nonretryable error. If all four are explicitly approved and attempted, the ceiling is one Tavily request, two Exa requests (one direct plus one assisted), and up to four Gemini requests (one closed-book and one assisted call, each with at most one existing 5xx retry). No second V2 question or larger segment is part of this pilot. Do not publish pilot output automatically.

Before invoking any `--execute-v2` command, the project owner must verify the actual Tavily/Exa account or order terms for capture/retention and public metrics, inspect remaining credits and rate limits in those accounts, and inspect the Gemini project's tier, model availability and RPM/TPM/RPD in AI Studio. Obtain explicit authorization for the selected experiment and its request ceiling. [Tavily terms](https://www.tavily.com/terms), [Exa terms](https://exa.ai/assets/Exa_Labs_Terms_of_Service.pdf), [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) are public references; they do not establish account-specific permission or free capacity. Never send secrets to chat or commit them.

For a read-only account check, Tavily documents `GET /usage`, which returns key and account usage/limits. [Exa billing](https://exa.ai/docs/admin/billing) directs users to its billing dashboard for the current credit balance; its documented [Get team info](https://exa.ai/docs/websets/api/teams/get-team-info) endpoint reports Websets concurrency, **not** available search credits. Exa's [API-key usage endpoint](https://exa.ai/docs/reference/team-management/get-api-key-usage) needs a separately enabled team-management service key and reports historical spending, not the current balance. [Gemini active rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and [billing/usage](https://ai.google.dev/gemini-api/docs/billing/) are project-specific views in AI Studio. Public free-tier tables cannot establish this project's remaining capacity.

Access audit on 2026-10-11: this local environment had no Tavily, Exa or Gemini API key variables; GitHub reported no repository-level Actions secrets/variables, and the organization-secret listing returned HTTP 403 for the available token. Organization secrets may still be supplied to Actions; the audit does not establish their absence. No authenticated provider usage endpoint or billing dashboard was accessed, and no provider request was made. To clear the pilot gate, use authorized read-only account/dashboard access or provide redacted current quota and applicable agreement details, then authorize the exact provider(s) and request ceiling. Do not put account usage, terms or raw API responses in public Actions logs/artifacts.

### Private bounded V2 collection

On 2026-10-11 the owner confirmed the accounts are free and authorized bounded internal testing until provider limits appear. The manual `V2 private bounded collection` workflow selects one track and a contiguous frozen V2 range. It defaults to the predeclared `S02A` pilot (index 1, count 1), runs tests before API use, and stops on nonretryable quota/auth errors according to each collector. A web track permits at most 20 searches; `gemini_closed` permits at most five generations per run, each with one possible 5xx retry. The Gemini cap was added after a 13-question run took nearly the original ten-minute job timeout; the job now has 25 minutes. Each capture remains private: the runner encrypts it with the committed public certificate before uploading a seven-day artifact. The matching private key is in ignored `.private/v2-pilot-key.pem` on this workspace and must never be committed, pasted into chat or placed in Actions. The workflow logs no result text, ranked URLs, key values or account usage. A success only means a capture was encrypted; it may contain HTTP 429 or another missing observation. Inspect each capture before selecting the next nonoverlapping range, so duplicate complete attempts do not enter a merged panel. A forced runner termination before encryption can still lose its local checkpoint; keep Gemini stages small.

The first three independent `S02A` pilots completed on 2026-10-11: [Gemini closed-book](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38126259765), [Tavily ranked](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38126337596), and [Exa ranked](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38126385153). No quota limit appeared then. A later Gemini closed-book stage received HTTP 429 and stopped; see the checkpoint. `gemini_exa` is excluded from the private workflow: [Exa terms §4.2(a)](https://exa.ai/assets/Exa_Labs_Terms_of_Service.pdf) restrict transmitting obtained information, and the assisted protocol sends Exa titles/URLs to Google. Obtain applicable permission/clarification before that experiment. The standalone search observations are internal; public search metrics require a separate rights review.

Use one track at a time and inspect its encrypted capture before trying the next. Download a run's artifact into the ignored `.private/` directory, then decrypt locally with `openssl cms -decrypt -binary -inform DER -in <capture.p7m> -recip .github/v2-pilot/recipient-cert.pem -inkey .private/v2-pilot-key.pem -out .private/<run-id>.json`. Validate that capture with the frozen V2 manifest/analyzer and record the Actions run URL, HTTP status, completeness and limitations in the checkpoint. Do not commit decrypted captures. The public Tavily and Exa terms still raise separate publication/retention questions; an internal pilot does not authorize a public V2 metric or a larger run. No paid tier, native Google grounding or recurring calls are activated.

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
