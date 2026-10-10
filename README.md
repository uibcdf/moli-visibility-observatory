# MOLI Visibility Observatory

MOLI Visibility Observatory is a research prototype for measuring how scientific software is found and mentioned. MolSysMT is the first case. Start with the [developer guide](devguide/README.md) for the architecture, methodology, dated evidence, operations and roadmap.

The project keeps three experiments separate:

| Experiment | What it observes | Current measure or status |
| --- | --- | --- |
| Tavily / Exa ranked search | Whether a canonical MolSysMT URL appears among ordered web results | Presence@10 and MRR@10, per provider |
| Gemini closed-book | What the model says without retrieved sources | Explicit MolSysMT name mentions |
| Gemini with Exa context | What the model says after receiving Exa result titles and URLs | Pilot observations only; no category rate |

Search presence, model mention and recommendation quality answer different questions. No combined visibility score is calculated. Errors, truncated responses, short result lists and unattempted queries are missing evidence, not negative results.

## Dated observations

The [2026-10-10 checkpoint](devguide/04_checkpoint.md) links the source runs and states their limits. Reviewed summaries in [web baselines](data/baselines/) and [agent baselines](data/agent-baselines/) record:

| Track | Complete queries | Observation |
| --- | ---: | --- |
| Tavily basic | 20/20 | Presence@10 1/20 (5%); MRR@10 0.025 |
| Exa auto | 20/20 | Presence@10 12/20 (60%); MRR@10 0.3917 |
| Gemini 3.1 Flash-Lite closed-book | 20/20 | 0/20 explicit MolSysMT name mentions; recommendation quality awaits adjudication |

Gemini 3.8 Flash runs are incomplete. In the Exa-assisted interoperability pilot, I01 produced a complete response recommending MolSysMT first, I02 hit HTTP 429 and I03–I05 were unattempted. This is one observation, not a five-query rate. The Exa context contains **titles and URLs only**, not page bodies. Full response artifacts have limited Actions retention; compact reviewed summaries do not permit full raw-to-summary reconstruction.

## Public site

The [web dashboard](https://www.uibcdf.org/moli-visibility-observatory/) and [AI-model page](https://www.uibcdf.org/moli-visibility-observatory/agents.html) publish committed, reviewed summaries only. The Pages workflow has deployed successfully; both custom-domain HTTPS routes returned HTTP 200 on 2026-10-10. The public pages do not publish raw provider captures or synthetic fixtures.

To generate the same pages locally without network access or API credentials:

~~~bash
python -m unittest discover -s tests -v
python -m visibility_observatory.publish --output build/public-site
python -m http.server 8000 --directory build/public-site
~~~

The synthetic CLI preview is separate:

~~~bash
python -m visibility_observatory --run examples/sample.json --output build/site
~~~

It is labeled synthetic and must not be presented as a measured baseline.

## Collection and safety

The benchmark is frozen in [queries/v1.json](queries/v1.json): 20 unbranded English queries in four families. Web captures store ordered URLs and status per query. New Gemini batch checkpoints record the model, prompt protocol and output token limit; individual samples record response status, plus finish reason and usage when available. Historical batch artifacts are unchanged. The [methodology](docs/methodology.md) explains denominators and evidence limits.

Collection workflows are **manual only**: Tavily/Exa, optional Brave, Gemini closed-book and Gemini with Exa context. They require the relevant Actions secrets (`TAVILY_API_KEY`, `EXA_API_KEY`, `BRAVE_SEARCH_API_KEY`, `GEMINI_API_KEY`). No monthly collection is scheduled. Gemini native Google Search grounding is disabled pending separate terms, quota, price and explicit spending approval. A consumer subscription does not authorize API billing.

Before any manual live run, confirm current provider terms and project quotas, start with a bounded one-query pilot, and inspect usage and the resulting artifact. The Gemini 3.8 Flash 429 quota dimension is still unknown; do not rerun the five-query assisted batch until the authorized project quota is inspected. See [operations](devguide/06_operations.md) for the exact workflows and handoff procedure.

## Project tracking

- [Observatory #1](https://github.com/uibcdf/moli-visibility-observatory/issues/1): collection and public reporting history.
- [Observatory #2](https://github.com/uibcdf/moli-visibility-observatory/issues/2): Gemini stabilization and Exa-assisted evaluation.
- [MolSysSuite #114](https://github.com/uibcdf/molsyssuite/issues/114) and [MolSysMT #378](https://github.com/uibcdf/molsysmt/issues/378): upstream scientific context.
