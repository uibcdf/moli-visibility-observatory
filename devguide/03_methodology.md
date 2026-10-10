# Scientific methodology and interpretation

## Frozen benchmark

`queries/v1.json`: 20 English-language **unbranded** task queries in four families (G general, I interoperability, S scientific tasks, D differentiation), five each. Keep V1 unchanged; changes require a new version and explicit comparability notes. Some V1 questions name *other* tools; this may bias recall toward those tools.

## Track A: ranked search retrieval

Evaluate each provider **separately**. At k=10, a query is evaluable only with a declared complete capture of >=10 ordered results. Presence@10 = number of eligible queries containing a canonical MolSysMT URL in top ten / number of eligible queries. MRR@10 = mean reciprocal first canonical hit rank across eligible queries. Report exact numerator and denominator. Canonical URL detection is provisional; audit false negatives, mirrors, redirects and out-of-date docs.

Provider ranking methods differ: Tavily basic and Exa auto must not be treated as interchangeable search populations. Search dates, language, locale, depth and provider configuration matter.

## Track B: Gemini without search

A response is complete only when it contains substantive output and `finishReason=STOP`. `MAX_TOKENS` or HTTP errors are **missing observations**, not negative mentions. Count explicit MolSysMT occurrences separately from whether Gemini genuinely recommends it. Record model ID, prompt protocol (including `concise-v2`), max output tokens, tool settings, date and token accounting. At least one earlier complete 20-query run exists for Gemini 3.1 Flash-Lite; see checkpoint.

## Track C: Exa-assisted Gemini

For each frozen query, retrieve a bounded Exa result set and record exact URL/title/rank. Pass the evidence to a separately identified Gemini model and store the answer, finish reason and usage. **Current content is titles and URLs only**; no full fetched documents. A complete retrieval can still be off-topic. Audit relevance and distinguish MolSysMT in retrieved sources, in model mention, and in recommendation. Compare to same-model closed-book only after controlling prompt protocol, timing and model settings.

## Track D: future Gemini native Google Search

Deferred because API grounding may involve billing. Only consider after explicit spending permission, current tariff review and bounded pilot. Gemini-web manual observations are qualitative, not interchangeable with API experiments.

## Validity requirements

- Keep response completeness, explicit mention, recommendation and correctness separate.
- Preserve missing/errored/unattempted counts and run IDs.
- No pooled score across fundamentally different tracks.
- Annotate stale MolSysMT documentation (0.21/0.22 versus later releases) and distinguish model output claims from verified code/API claims.
- A single recommendation is an observation, not a statistically stable rate.
- Snapshot reproducibility requires retaining allowed raw answers and retrieved evidence with checksums; compact summaries alone are insufficient.
- Provider API policies, quotas and datasets may change; check contemporaneous documentation before automation.

## Proposed adjudication rubric (not yet deployed)

A second-stage reviewer should classify each completed answer as: explicit name mention (exact evidence span), recommended or merely compared, top-ranked or alternative, stated reason, scientifically relevant/irrelevant, accurate/inaccurate/unknown claims, and cited source grounding. Store reviewer identity and disagreements rather than treating automatic string matching as scientific judgment.
