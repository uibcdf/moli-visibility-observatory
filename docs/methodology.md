# Visibility Observatory methodology

This is the public summary of the current protocol. The [developer methodology](../devguide/03_methodology.md) and [dated checkpoint](../devguide/04_checkpoint.md) give the full interpretation and evidence links.

## Benchmark and separate tracks

[queries/v1.json](../queries/v1.json) freezes 20 English, unbranded task queries: five each for general use, interoperability, scientific tasks and differentiation. A prompt change requires a new benchmark version. Some questions name other tools, which may affect what a search provider retrieves or a model mentions.

**Ranked web search.** Tavily basic and Exa auto are evaluated separately. For each provider, a query is eligible for Presence@10 and MRR@10 only when its capture is marked complete and contains at least ten ordered results. Presence@10 is the number of eligible queries with a canonical MolSysMT URL in the top ten divided by the number of eligible queries. MRR@10 is the mean of `1 / first canonical hit rank`, using zero for an eligible query with no hit. The repository's canonical URL matcher is provisional and needs an independent audit of mirrors, redirects, stale pages and false negatives. Provider rankings, locale and time affect the result.

**Gemini closed-book.** The model receives the task query without retrieved search evidence. A response is complete only with substantive text and `finishReason=STOP`; `MAX_TOKENS` and API failures are missing observations. Count an explicit MolSysMT name occurrence separately from a recommendation, relevance and technical correctness. Record the exact model, prompt profile, output token limit, date, usage and query ID. The 2026-10-10 Gemini 3.1 Flash-Lite run is a complete 20-query **name-mention** baseline; it is not an adjudicated recommendation-quality benchmark.

**Gemini with Exa context.** Exa supplies ranked titles and URLs, up to five in the current pilot. Those strings are passed to Gemini as external context; the implementation does not fetch page bodies. A retrieval with fewer than five sources is partial and is not sent as a matched five-source model trial. Record the source rank, title, URL, retrieval status, model response and usage. Presence in the retrieved list, model mention and recommendation are distinct outcomes. Compare this mode with closed-book only under matched model and prompt settings.

Native Gemini Google Search grounding is deferred; no paid grounding experiment or recurring API collection is authorized. A manually reported Gemini web-app answer is qualitative evidence only, without controlled API or retrieval provenance.

## Missingness, publication and reproducibility

Report exact numerator and denominator for every rate and preserve partial, error and unattempted counts. A 429, truncation, short search result set or absent response never counts as a negative recommendation. Do not average results across providers or across search and generation tracks. A single model answer does not establish a stable rate or a causal effect of retrieval.

Public Pages uses reviewed compact summaries from [web baselines](../data/baselines/) and [agent baselines](../data/agent-baselines/). Synthetic fixtures and raw provider results are excluded. The original full responses currently reside in time-limited Actions artifacts; reproducible raw-to-summary reconstruction needs a lawful, privacy-reviewed retention contract, immutable run provenance and checksums. Recommendation quality and capability claims still need independent human adjudication.
