# Scientific methodology and interpretation

## Frozen benchmark

`queries/v1.json`: 20 English-language **unbranded** task queries in four families (G general, I interoperability, S scientific tasks, D differentiation), five each. Keep V1 unchanged; changes require a new version and explicit comparability notes. Some V1 questions name *other* tools; this may bias recall toward those tools.

## Frozen V2 question protocol (not executed)

[`queries/v2.json`](../queries/v2.json) freezes 48 prompts in a fixed, seeded shuffle order (seed `20261010`; SHA-256 `fab3c490c1ff158f0ae4528bf147c8aea216da527c2d65e5e4f4330315ee6335`). [`benchmark_v2.py`](../visibility_observatory/benchmark_v2.py) validates the offline corpus. The V1 bytes and historical observations remain unchanged. A wording, order, pairing or stratum change needs a new benchmark version and comparability note.

The primary stratum has **15 task intents × two English, unbranded formulations = 30 prompts**, with three intents in each family: preparation/repair, data-form conversion, selection/analysis, simulation interoperability, and storage/reproducibility. The A formulation is a researcher request; B names more concrete input/output. Because wording and specificity change together, this design cannot isolate their effects. The two prompts for one intent are correlated probes, not independent tasks. The target is discoverability for these declared use cases, not a random sample of all molecular software questions.

Three separate six-prompt strata probe different failure modes: `negative_control` covers unrelated scientific workflows; `named_alternative` adds competitor names to six selected A prompts; `spanish_unbranded` translates those same six A prompts. `paired_with` records the reference ID. Controls carry a preregistered `out_of_scope` expectation, which is a hypothesis for human review rather than proof that every mention is wrong. The six paired tasks span all five primary families, with two conversion tasks. Prompts themselves never name MolSysMT. V2 is deliberately broader than V1, but 48 prompts are a scope/cost choice, **not** a power calculation or representative sample.

The scope was checked against primary MolSysMT documentation: [toolbox overview](https://www.uibcdf.org/molsysmt/content/user/foundations/entrance/toolbox_overview.html), [forms and interoperability](https://www.uibcdf.org/molsysmt/content/user/foundations/molecular_system/forms.html), [selections](https://www.uibcdf.org/molsysmt/content/user/tools/basic/select.html), [structure preparation](https://www.uibcdf.org/molsysmt/content/user/cookbook/from_pdb_to_solvated_box.html), [trajectory analysis](https://www.uibcdf.org/molsysmt/content/user/cookbook/07_Trajectory_Performance_Analysis.html), [OpenMM workflow](https://www.uibcdf.org/molsysmt/content/user/cookbook/simulation_workflow.html), and [H5MSM storage](https://www.uibcdf.org/molsysmt/content/user/foundations/native_world/files/file_h5msm.html). Some pages document older releases. Recheck the current package/API and judge answers for technical accuracy before claiming any capability or recommendation quality. The controls are inferred from the documented scope, not validated impossibility claims.

For each provider/mode, report **primary prompt coverage** over eligible completed primary prompts (`≤30`) and **intent coverage** only for intents with both A and B eligible (`≤15`). The preregistered intent outcome is presence/mention/recommendation in **either** completed formulation; also report the stricter **both** count as a consistency check. For search, apply the track's complete top-ten rule; for model outputs, report explicit name mentions separately from human-adjudicated recommendations. Report control over-recommendations only among completed, human-reviewed control answers. Describe each six-pair anchor and Spanish comparison as a within-track paired observation, with exact eligible pairs and directions. Do not pool the four V2 strata, V1 and V2, or distinct providers/modes. Missing, truncated, errored and unattempted prompts are excluded from outcome denominators and shown separately. The fixed order limits order randomness; collection timing, locale and provider drift remain limitations.

No V2 provider capture, pilot, public metric or deployment is claimed here. Activation requires account terms/retention and quota review, owner approval for the intended live workflow, a bounded pilot, and segment-capable collectors with exact benchmark-byte provenance. Current manual workflows still select V1, and the ranked-search collector cannot resume at a V2 offset. The frozen corpus can be inspected and validated offline without credentials.

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

For web search, an offline verifier can compare a local capture to a reviewed-style summary using the current canonical URL matcher and top-ten denominator. This is an arithmetic/provenance consistency check, not independent validation that every canonical URL rule or scientific judgment is correct. The current summary has no source hash, so a matching capture cannot by itself prove that it is the historical Actions artifact named in the summary. Gemini recommendation adjudication remains a separate unimplemented reconstruction step.

For Gemini closed-book, a separate offline verifier reproduces only **explicit name mentions** with a versioned text rule. Its denominator includes complete `STOP` answers only; `MAX_TOKENS`, errors and unattempted queries remain missing for this metric. A name occurrence is not evidence of endorsement, technical correctness, external grounding or model training knowledge. Human recommendation and claim adjudication remains pending even if the mention counts reconcile.

## Proposed adjudication rubric (not yet deployed)

A second-stage reviewer should classify each completed answer as: explicit name mention (exact evidence span), recommended or merely compared, top-ranked or alternative, stated reason, scientifically relevant/irrelevant, accurate/inaccurate/unknown claims, and cited source grounding. Store reviewer identity and disagreements rather than treating automatic string matching as scientific judgment.
