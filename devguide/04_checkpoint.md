# State checkpoint — 2026-10-10

**Repository:** `uibcdf/moli-visibility-observatory`. This is a dated checkpoint, not a claim about future runs. Refresh from GitHub Actions and authoritative files before new work.

## Verified experimental observations

| Track | Run | Outcome |
| --- | --- | --- |
| Tavily basic, 20 queries | [38040732355](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38040732355) | 20 complete, Presence@10 **1/20 (5%)**, MRR@10 **0.025** |
| Exa auto, 20 queries | [38043761135](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38043761135) | 20 complete, Presence@10 **12/20 (60%)**, MRR@10 **0.3917** |
| Gemini 3.1 Flash-Lite closed-book | [38052178041](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38052178041) | 20 complete, **0/20 explicit MolSysMT name mentions**; scientific recommendation adjudication pending |
| Gemini 3.8 Flash closed-book | [38053827033](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38053827033) | Incomplete: 4 complete, 10 truncated MAX_TOKENS, 3 HTTP failures (2×503, 1×429), 3 unattempted. **Not** a 20-query rate |
| Gemini 3.8 Flash + Exa G01 | [38061209671](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38061209671) | 5/5 Exa sources, complete Gemini answer, no MolSysMT mention |
| Gemini 3.8 Flash + Exa interoperability I01–I05 | [38062003242](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38062003242) | I01 completed: Exa retrieved canonical MolSysMT at ranks 1/3/5; Gemini **recommended MolSysMT first**. I02 HTTP 429; I03–I05 unattempted. Not a complete category result |

A manually reported Gemini 3.8 Flash **web app** answer also recommended MolSysMT when web search was used, but no URLs/retrieval trace were provided. Treat it as qualitative only. Do not infer a causal advantage of retrieval versus closed-book because model, protocol and context differ.

## Engineering status

- **Implemented/tested previously:** Tavily and Exa adapters, Gemini clients, bounded checkpoints, manual workflows, reviewed-summary Pages renderer, synthetic tests, Gemini `concise-v2` profile (4096 output tokens), Exa-assisted titles/URLs retrieval.
- **Latest observed Actions:** [38060534101](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38060534101) confirmed successful reviewed Pages deployment; subsequent CI runs must be checked from GitHub. Public dashboard: https://uibcdf.github.io/moli-visibility-observatory/ ; dedicated agent page path `agents.html`.
- **Operational blocker:** Gemini 3.8 free-tier 429 observed; exact quota dimension not established. A longer 120-second transport timeout fixed one G01 timeout but does not solve quota constraints.
- **Evidence debt:** full underlying responses are only in expiring Actions artifacts; durable versioned summaries are present in `data/baselines/` and `data/agent-baselines/`. No verified full long-term archive.
- **Automation:** manual-only provider runs; NO monthly provider schedule and NO authorized paid Google grounding.

## Do not misstate

Successful Actions != all measurements scientifically valid. 0/20 Gemini closed-book is an **explicit mention rate for one model/protocol**, not proof of ignorance. The first successful Exa-assisted I01 recommendation is a **single observation**, not a 5/5 benchmark. Earlier README and `docs/methodology.md` include initial-phase wording now stale; reconcile them in a scoped documentation cleanup.
