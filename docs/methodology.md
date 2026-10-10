# Visibility Observatory methodology — draft v0.1

This prototype is **not** a completed baseline or agent benchmark. The original 20-query October 10, 2026 exercise did not retain enough ranked results and provider provenance to support numerical claims.

The 20 unbranded prompts in `queries/v1.json` form a versioned fixed questionnaire. Capture a provider-supplied observation as a JSON file: `schema_version: "1"`, `benchmark_version: "1.0"`, `track: "web_search"`, `provider`, `collected_at_utc` (UTC ISO 8601), `samples: [{query_id,status,results:[{url,title}]}]`. Allowed statuses: `complete`, `partial`, `error`.

Only a query with a **complete** response containing at least k ranked results contributes to Presence@k (whether a canonical MolSysMT URL appears in the first k) and MRR@k (mean reciprocal first-hit rank). Incomplete, errored, truncated and uncollected queries are missing information, **not negative results**. Report the denominator. Current URL matching is a conservative first-pass rule; independently review false positive/negative cases before scientific publication.

This measures **web discoverability**, not whether any AI agent recommends the library. Independent agent executions require a separately designed protocol and evaluator; this CLI explicitly rejects `agent_recommendation` inputs.

Before activating scheduled collection: select a permitted API and document terms, coverage, search region, language, source rank depth, raw-data retention permissions, request costs, rate limits, model/provider versioning, and error behavior. A monthly schedule is proposed but **not enabled**. Search response ranking is dynamic, provider-specific and affected by personalization/locale. Track sources rather than implying search rank indicates software quality.

Keep synthetic fixtures unmistakably labeled; keep credentials and any private data out of public artifacts. Coordinate with [MolSysSuite #114](https://github.com/uibcdf/molsyssuite/issues/114) and [MolSysMT #378](https://github.com/uibcdf/molsysmt/issues/378).
