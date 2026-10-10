# AGENTS.md — MOLI Visibility Observatory

Before changing code, read [devguide/README.md](devguide/README.md) and its seven linked chapters, then issues [#1](https://github.com/uibcdf/moli-visibility-observatory/issues/1) and [#2](https://github.com/uibcdf/moli-visibility-observatory/issues/2).

## Work rules

- Start with `python -m unittest discover -s tests -v`. Do not silently run any live API or paid workflows.
- V1 benchmark prompts are frozen in `queries/v1.json`. Version protocol changes and preserve existing evidence.
- Treat Tavily/Exa ranked URLs, Gemini closed-book mentions and Gemini+Exa recommendations as **separate** experiments; never average them as a consensus.
- An error, truncation, 429 or unattempted query is **missing** evidence, not a negative recommendation.
- No secret logging, private data publication, unauthorized billing, native Google grounding, or recurring API calls. Confirm terms/quotas and explicit owner approval before activation.
- Update the relevant `devguide` chapter and `04_checkpoint.md` with any meaningful change, evidence URL, limitations and next step.
- Make source-backed claims about actual CI and live runs. A committed implementation is not automatically qualified or deployed.

See [operations](devguide/06_operations.md) for commands and handoff procedure, [roadmap](devguide/05_roadmap.md) for sequencing, and [decisions](devguide/07_decisions.md) for preserved rationale.
