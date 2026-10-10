# Architecture and data contracts

## Current layout

```text
queries/v1.json                       frozen 20 unbranded queries (G/I/S/D)
visibility_observatory/__main__.py    web-ranked result validation, Presence@k/MRR@k, local HTML
visibility_observatory/providers.py   manual Tavily and Exa searches
visibility_observatory/brave.py       optional Brave collection
visibility_observatory/gemini.py      Gemini generation client (no native paid grounding)
visibility_observatory/agent_batch.py checkpointed closed-book Gemini batches
visibility_observatory/exa_assisted.py Exa titles/URLs passed to Gemini as context
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

The `validate.yml` workflow runs tests and builds a clearly synthetic preview on push and pull request. `pages.yml` deploys reviewed summaries on relevant pushes or manual dispatch. Provider workflows use manual dispatch only: Tavily/Exa can request 1, 5 or 20 queries; Brave requests all 20; Gemini closed-book can request 1, 5 or 20 and retry a transient 5xx once per query; Exa-assisted defaults to one query or explicitly selects I01–I05. These workflows can consume provider quota and must not be triggered during a documentation or test audit. The code does not enforce an account-level spending cap or inspect remaining quota.

The provider configuration, prompt profile and benchmark **all affect comparability**. Current Gemini `concise-v2` changes instruction length and output budget; it is not identical to earlier runs. `gemini.py` includes `protocol_version` and `output_token_limit` in direct captures; new `agent_batch.py` checkpoints copy those constants into the outer record before the first request. `exa_assisted.py` includes `protocol_version`. Earlier batch artifacts, including [the Gemini 3.1 baseline](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38052178041), were not rewritten; their protocol identity still depends on code/run provenance. Source URLs are not source page bodies: the current Exa-assisted implementation only supplies titles and URLs. A source may be stale or misleading.

## Known architectural debt

- No durable full-response archive with retention and provider terms reviewed; Actions artifacts expire.
- No automatic reviewed ingestion, adjudication, deduplicated merging or historical dashboard with trend confidence.
- Checkpoints are atomic files within a **single workflow run**, not resumable across GitHub Actions runs.
- Exa-assisted and closed-book tracks use related generation code; add explicit mode/protocol identity at every published level.
- Quota limits cannot be inferred reliably from HTTP 429 without inspecting authorized account dashboards or safe response headers.
- A successful GitHub Actions job does not by itself validate a scientific conclusion.

## Security and boundary contracts

Secrets remain GitHub Actions secrets: `TAVILY_API_KEY`, `EXA_API_KEY`, `GEMINI_API_KEY`; optional `BRAVE_SEARCH_API_KEY`. Never commit, log or copy credentials. No raw provider error bodies containing unknown identifiers. Public Pages reads reviewed summaries rather than unreviewed raw captures. Recheck provider storage/redistribution rules before archival publication.
