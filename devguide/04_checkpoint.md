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
- **Verified Actions on 2026-10-10:** [validation run 38062658257](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38062658257) succeeded for commit `b2cf007`; [Pages run 38060544005](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38060544005) succeeded for an earlier commit. Later validation of the documentation and batch-metadata commit is linked below; no Pages deployment of that commit is claimed.
- **Public routes checked on 2026-10-10:** the direct HTTPS [web dashboard](https://www.uibcdf.org/moli-visibility-observatory/) and [agent page](https://www.uibcdf.org/moli-visibility-observatory/agents.html) returned HTTP 200. The served web page contained Tavily and Exa sections; the agent page contained the Gemini 3.1 Flash-Lite summary. The `https://uibcdf.github.io/...` aliases currently redirect to `http://www.uibcdf.org/...`; review Pages HTTPS enforcement/redirect configuration before treating those aliases as canonical. Recheck after future deployments.
- **Operational blocker:** Gemini 3.8 free-tier 429 observed; exact quota dimension not established. A longer 120-second transport timeout fixed one G01 timeout but does not solve quota constraints.
- **Evidence debt:** full underlying responses are only in expiring Actions artifacts; durable versioned summaries are present in `data/baselines/` and `data/agent-baselines/`. No verified full long-term archive.
- **Automation:** manual-only provider runs; NO monthly provider schedule and NO authorized paid Google grounding.

## Do not misstate

Successful Actions != all measurements scientifically valid. 0/20 Gemini closed-book is an **explicit mention rate for one model/protocol**, not proof of ignorance. The first successful Exa-assisted I01 recommendation is a **single observation**, not a 5/5 benchmark.

## P0 documentation and local audit — 2026-10-10

- Reconciled `README.md` and `docs/methodology.md` with the code and dated run summaries. They now distinguish deployed reviewed pages, the complete Gemini 3.1 name-mention baseline and the partial Gemini 3.8 Exa-assisted pilot. No experimental records or V1 questions changed.
- A fresh local clone of commit `b2cf007` passed 32 tests and generated two reviewed web summaries plus the agent page offline. The working tree also passed 32 tests before the documentation edit. The tests use mocked network calls and do not certify current provider quotas, scientific adjudication or hosted deployment of these edits.
- Inventory in [architecture](02_architecture.md): three raw capture schemas, two public summary schemas and seven workflows. Current public summaries cannot reconstruct all source URLs or original model answers. Earlier closed-book batch checkpoints omitted explicit prompt protocol and output-token-limit fields; their historical identity must be recovered from code/run provenance. A preliminary provider-terms review now exists, but applicable rights and durable raw retention remain unresolved.
- After the documentation edit, the working-tree suite passed 32 tests, the reviewed site generated offline and local Markdown links resolved; `git diff --check` passed. Hosted CI later passed for commit `cc0804c`, as linked below.
- **Next safe step:** design a terms-reviewed retained-evidence contract with immutable run IDs, checksums and validated raw-to-summary recomputation. Do not repeat the Gemini 3.8 assisted batch until the authorized project quota behind HTTP 429 is understood.

## P1 checkpoint metadata correction — 2026-10-10

- `agent_batch.py` now writes `protocol_version=concise-v2` and `output_token_limit=4096` to the initial and subsequent atomic checkpoints, sourced from the same constants as the Gemini client. A mocked 429 test checks both the pre-request and final files. The existing `agent-observation-v1` schema identifier is preserved because this is additive metadata.
- This is implemented and locally tested; [push CI run 38066775048](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38066775048) and [PR CI run 38066807589](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38066807589) both passed for commit `cc0804c`. No provider call was made, and [historical Gemini 3.1 evidence](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38052178041) remains unchanged. Future batches can be self-describing on these two settings; full prompt text or a prompt hash is still not stored.
- Public [web results](https://www.uibcdf.org/moli-visibility-observatory/) and [agent results](https://www.uibcdf.org/moli-visibility-observatory/agents.html) were checked again on 2026-10-10: both returned HTTPS 200 and contained the reviewed Tavily/Exa and Gemini 3.1 summaries respectively. These pages do not yet present Exa-assisted pilots or a historical trend.
- **Next:** review retention rights, then add immutable run provenance and raw-to-summary reconstruction without changing the frozen V1 benchmark or treating incomplete Gemini 3.8 responses as negatives.

## Preliminary retention-terms finding — 2026-10-10

- The source inventory in [architecture](02_architecture.md) found potential publication restrictions in current [Tavily terms](https://www.tavily.com/terms) and broad output-copying restrictions in current [Exa terms](https://exa.ai/assets/Exa_Labs_Terms_of_Service.pdf). This is a terms flag, not a legal conclusion about the current site or the applicable account agreements.
- No full output was downloaded or newly published. Pause any expansion of public provider metrics or raw archival until the owner checks the actual account/order terms and obtains clarification or permission where required. The existing public summaries also need review against those terms.
- The 20 frozen V1 prompts remain useful as a dated exploratory panel, but they are English-only, concentrated in four task families and include named alternative tools. A V2 design should be predeclared separately with wider task coverage and prompt variants; do not mix its rates with V1.
