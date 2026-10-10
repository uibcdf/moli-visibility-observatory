# Scientific methodology and interpretation

## Frozen benchmark

`queries/v1.json`: 20 English-language **unbranded** task queries in four families (G general, I interoperability, S scientific tasks, D differentiation), five each. Keep V1 unchanged; changes require a new version and explicit comparability notes. Some V1 questions name *other* tools; this may bias recall toward those tools.

## Candidate V2 design (not frozen or executed)

Twenty V1 prompts are sufficient for an exploratory, dated panel, but each observation changes a 20-query rate by five percentage points. Their English-only wording, four broad families and named alternatives limit generalization. Repeating the same prompts helps track those prompts over time; it does not make them a random sample of scientific-software needs. Keep V1 intact and report any future V2 separately.

Before writing `queries/v2.json`, define the target use cases and a balanced matrix. Candidate dimensions are: structure preparation and repair; topology/coordinate/trajectory conversion; atom selection and structural analysis; simulation setup and interoperability; reproducibility/storage; and deliberately out-of-scope tasks that test over-recommendation. For each task, vary wording (researcher request versus feature description), specificity (broad versus concrete input/output), and named-alternative anchoring. Keep the primary discovery stratum unbranded; place prompts naming other packages and any Spanish-language prompts in explicitly separate strata. Include cases where MolSysMT should not be recommended.

Draft examples for review, not measurement prompts: “Which Python tools can prepare a protein structure with missing atoms and hydrogens for simulation?”, “How can I move topology and coordinates between molecular Python libraries while checking what information is lost?”, and “What can compare contacts across a molecular-dynamics trajectory stored separately from its topology?” Validate scientific relevance and current package capabilities before freezing wording. Set sample size from the intended claim and quota/cost budget, then pilot a few questions before any full run. Do not merge V1 and V2 denominators.

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

## Offline multi-run reconciliation

The internal `evidence-merge-v1` format can reconcile multiple captures only when their exact benchmark bytes and measurement settings agree. It retains the source run IDs, timestamps and every attempted status. For a query with one complete attempt, that attempt is identified; any earlier failure or truncation stays in the ledger. Two complete attempts are a conflict requiring review, even if they look similar. Queries with no complete attempt remain non-evaluable. A merged panel spans multiple capture times and can suffer retry/selection bias; do not present its counts as an independent single-run rate or mix tracks/providers. No public metric is calculated by the merge command.

## Proposed adjudication rubric (not yet deployed)

A second-stage reviewer should classify each completed answer as: explicit name mention (exact evidence span), recommended or merely compared, top-ranked or alternative, stated reason, scientifically relevant/irrelevant, accurate/inaccurate/unknown claims, and cited source grounding. Store reviewer identity and disagreements rather than treating automatic string matching as scientific judgment.
