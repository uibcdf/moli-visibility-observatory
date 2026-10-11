# Architecture and data contracts

## Current layout

```text
queries/v1.json                       frozen 20 unbranded queries (G/I/S/D)
queries/v2.json                       frozen 48-prompt, four-stratum question protocol; no captures
visibility_observatory/benchmark_v2.py offline V2 design validator
visibility_observatory/benchmark_run.py offline frozen-byte loader and three-segment V2 plan
visibility_observatory/v2_analysis.py internal separate-stratum analysis of local V2 captures
visibility_observatory/__main__.py    web-ranked result validation, Presence@k/MRR@k, local HTML
visibility_observatory/providers.py   manual Tavily and Exa searches
visibility_observatory/brave.py       optional Brave collection
visibility_observatory/gemini.py      Gemini generation client (no native paid grounding)
visibility_observatory/agent_batch.py checkpointed closed-book Gemini batches
visibility_observatory/exa_assisted.py Exa titles/URLs passed to Gemini as context
visibility_observatory/evidence_manifest.py offline internal manifest and byte-hash verification
visibility_observatory/evidence_merge.py offline reconciliation of compatible local captures
visibility_observatory/evidence_recompute.py offline web capture-to-summary verification
visibility_observatory/evidence_agent_recompute.py offline closed-book mention-summary verification
visibility_observatory/publish.py     reviewed-only public web-summary dashboard
visibility_observatory/agent_publish.py reviewed-only independent agent-summary page
data/baselines/                     reviewed Tavily and Exa compact web summaries
data/agent-baselines/               reviewed Gemini closed-book compact summary
examples/                           synthetic fixtures, never observational evidence
tests/                              standard-library unittest tests
.github/workflows/                   validation, manual provider captures, Pages publishing
```

Main data paths:

```text
Frozen benchmark
  ├─ Tavily / Exa / optional Brave → ordered URLs → web metrics → reviewed summaries → Pages
  ├─ Gemini closed-book → answer + finish reason + usage → adjudication → agent summary
  └─ Exa → ranked title/URL evidence → Gemini → answer + provenance → separate assisted track
```

## Existing contracts

Web capture uses schema version `1`, `track=web_search`, provider and UTC timestamp, and per-query complete/partial/error records with ordered URLs. Review-derived summaries use `baseline-summary-v1`.

Gemini closed-book stores `agent-observation-v1`, model, mode, prompt benchmark version, samples, answer, finish reason and token usage. Exa-assisted uses `agent-assisted-observation-v1` and records retrieved source ranks, titles, URLs and response data. Public agent-summary records use `agent-baseline-summary-v1`.

| Record | Producer | Persisted/public form | Reconstruction limit |
| --- | --- | --- | --- |
| Web capture `1` | `providers.py` / `brave.py` | 30-day Actions artifact; reviewed `baseline-summary-v1` committed | Summary retains hit ranks, not every returned result |
| Agent capture `agent-observation-v1` | `gemini.py` / `agent_batch.py` | 30-day Actions artifact; reviewed `agent-baseline-summary-v1` committed for one complete run | Summary retains mention count, not response text |
| Assisted capture `agent-assisted-observation-v1` | `exa_assisted.py` | 30-day Actions artifact; no reviewed public assisted summary yet | Source lists and answer are not in a durable committed record |

`evidence-manifest-v1` is a separate **internal, unreviewed** derivative. `evidence_manifest.py` reads an existing local capture and the exact benchmark bytes, validates query IDs and statuses, and computes SHA-256 digests plus a deterministic run ID. It records provider/model/protocol metadata when present, approved web configuration fields, per-query complete/partial/error/unattempted states, safe numeric HTTP status and finish reason. It omits ranked URLs, titles, prompts and generated answers. Verification requires the exact original bytes: a hash is a reference to evidence, not a replacement for it. The public Pages renderer does not ingest manifests. No raw capture is archived or made publishable by this command.

`evidence-merge-v1` is another internal derivative. It rebuilds each source manifest from local capture bytes, checks identical benchmark bytes and compatible track/provider/model/protocol/search settings, then records a per-query attempt ledger in benchmark order. Different query caps select segments and do not change web-search protocol. Its declared `exactly_one_complete_attempt_v1` rule keeps an error, truncation or unattempted query visible; a sole complete attempt can be selected after an incomplete attempt, while multiple complete attempts for one query stop the merge for review. The merge ID hashes sorted source run IDs and benchmark bytes. This is an explicitly multi-run panel, not a new single-run experiment or a replacement for retained raw evidence. Neither derivative is ingested by Pages.

`evidence_recompute.py` checks one already-local web capture against one `baseline-summary-v1` record. It validates the raw schema, recalculates complete/partial/error counts, Presence@10, MRR@10 and the first canonical hit's query/rank/URL, then checks those against the summary. Its optional `web-summary-reconciliation-v1` report contains hashes and check names, not provider results. The existing summary schema does **not** cryptographically bind the Actions run/artifact URL to the capture; title labels, stated limitations, search depth/locale and scientific relevance are not reconstructed. This verifier does not run for Gemini or publish anything.

`evidence_agent_recompute.py` checks one closed-book `agent-observation-v1` capture against one `agent-baseline-summary-v1` record. Its fixed `molsysmt-text-mention-v1` rule counts case-insensitive MolSysMT spelling with optional spaces/hyphens **only in complete STOP answers**. It verifies requested/complete/partial/error/unattempted counts, mention query IDs and the rate over complete answers. The optional internal report binds exact input hashes but contains no answer text. It does not infer recommendation quality, scientific accuracy, historical Actions artifact identity or Exa-assisted outcomes. The raw answers must already be locally available under an approved retention policy.

The `validate.yml` workflow runs tests and builds a clearly synthetic preview on push and pull request. `pages.yml` deploys reviewed summaries on relevant pushes or manual dispatch. Provider workflows use manual dispatch only: Tavily/Exa can request 1, 5 or 20 queries; Brave requests all 20; Gemini closed-book can request 1, 5 or 20 and retry a transient 5xx once per query; Exa-assisted defaults to one query or explicitly selects I01–I05. These workflows can consume provider quota and must not be triggered during a documentation or test audit. The code does not enforce an account-level spending cap or inspect remaining quota.

The provider configuration, prompt profile and benchmark **all affect comparability**. Current Gemini `concise-v2` changes instruction length and output budget; it is not identical to earlier runs. `gemini.py` includes `protocol_version` and `output_token_limit` in direct captures; new `agent_batch.py` checkpoints copy those constants into the outer record before the first request. New `exa_assisted.py` captures now also include both fields. Earlier artifacts, including [the Gemini 3.1 baseline](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38052178041), were not rewritten; their protocol identity still depends on code/run provenance and missing fields cause the offline merge to reject them. Source URLs are not source page bodies: the current Exa-assisted implementation only supplies titles and URLs. A source may be stale or misleading.

The V2 file adds `stratum`, `intent_id`, `variant`, `language`, `expected_scope` and optional `paired_with` to each `id`/`query`. `benchmark_run.py` checks exact frozen V1/V2 bytes and prints V2's three contiguous segments (20/20/8) without network access. Tavily/Exa, checkpointed Gemini and Exa-assisted CLIs now accept an explicit benchmark version and segment; V2 requires `--execute-v2`, while the default and every manual Actions workflow remain V1. Their new captures include a source-file SHA-256; web and assisted captures also state the start index and requested query IDs. The manifest rejects a V2 capture without a matching hash or with IDs inconsistent with the declared segment. Existing historical artifacts are not rewritten. The old web metric renderer deliberately rejects V2 to prevent a pooled 48-prompt score. `v2_analysis.py` reads compatible, already-local captures and writes an **internal, unreviewed** per-stratum summary without answers or URLs. It keeps web presence, closed-book name mentions and Exa-assisted name mentions distinct, preserves missingness and requires both A/B observations for intent comparisons. Recommendation quality and reviewed public publication are separate remaining work, subject to rights and scientific review.

## Known architectural debt

- No durable full-response archive with retention and provider terms reviewed; Actions artifacts expire.
- No automatic reviewed ingestion, adjudication, deduplicated merging or historical dashboard with trend confidence.
- Checkpoints are atomic files within a **single workflow run**, not resumable across GitHub Actions runs.
- Exa-assisted and closed-book tracks use related generation code; add explicit mode/protocol identity at every published level.
- Quota limits cannot be inferred reliably from HTTP 429 without inspecting authorized account dashboards or safe response headers.
- A successful GitHub Actions job does not by itself validate a scientific conclusion.

## Security and boundary contracts

Secrets remain GitHub Actions secrets: `TAVILY_API_KEY`, `EXA_API_KEY`, `GEMINI_API_KEY`; optional `BRAVE_SEARCH_API_KEY`. Never commit, log or copy credentials. No raw provider error bodies containing unknown identifiers. Public Pages reads reviewed summaries rather than unreviewed raw captures. Recheck provider storage/redistribution rules before archival publication.

## Preliminary provider-terms review — 2026-10-10

This is a source inventory, not a determination that the existing public summaries or any future archive is licensed. The applicable account agreement or order form may differ; obtain owner/provider review before expanding publication or retaining full provider output.

| Provider | Current primary-source concern | Working boundary |
| --- | --- | --- |
| Tavily | [Platform Terms §3.2](https://www.tavily.com/terms) restrict disclosure to third parties of performance information or analysis relating to the service. Public Presence@10/MRR@10 may fall within that wording; the actual account terms and permission need review. | Do not add further Tavily public metrics or full ranked output until clarified. |
| Exa | [Terms §4.2(a)](https://exa.ai/assets/Exa_Labs_Terms_of_Service.pdf) broadly restrict copying, downloading and publishing information obtained through the service unless otherwise permitted. The scope for API result URLs/titles and derived metrics is unclear; check the applicable API agreement and obtain written clarification if needed. | Do not treat the existing artifact or summary as permission for a durable public raw archive. |
| Gemini | [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms) say Google does not claim ownership of generated content, while use remains subject to law and the API terms. The terms distinguish unpaid and paid data handling, including a regional exception; this does not authorize billable runs or indiscriminate publication of submitted or generated content. | Keep prompts free of sensitive data and review attribution, privacy and output rights before storing or publishing full answers. |

The existing public Tavily/Exa summaries predate this terms review. Their continued publication needs an explicit owner/legal determination. No source response was downloaded or newly published during this review.
