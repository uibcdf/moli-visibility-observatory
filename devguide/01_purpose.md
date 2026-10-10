# Purpose, audience and scientific questions

MOLI Visibility Observatory studies how scientific software is **found, cited, mentioned and recommended** by modern search and AI systems. MolSysMT is the first monitored package; the architecture should permit future MolSysSuite tools and independently chosen comparison tools. This is an open methodology and evidence project, not an SEO manipulation pipeline.

## Distinct research questions

- **Discoverability:** does a ranked web search recover a verified canonical MolSysMT URL for an unbranded scientific request?
- **Spontaneous model mention:** does an LLM mention MolSysMT when asked to recommend tools without being given its name and without external retrieval?
- **Retrieval-assisted recommendation:** does an LLM recommend MolSysMT after being shown sources returned by a specified retriever?
- **Correctness and quality:** are any recommendations accurate, relevant, appropriately qualified and traceable to evidence?

Presence in results is not model knowledge; a model mention is not an endorsement; endorsement is not technical superiority. **Never calculate a synthetic combined consensus score across Tavily, Exa and Gemini.**

## Audiences

Scientific software developers (visibility gap); computational researchers (tool discovery); software-methodology researchers (reproducible evaluation); open-source contributors (auditable data and reusable methods).

## Success

Versioned experiments with transparent denominators, missingness, controlled prompts, exact model/provider identity, reproducible calculation and source/answer traceability; safe scheduled monitoring **only after** provider quotas and terms are qualified. Public dashboard communicates both results and their limitations.

## Non-goals

- Proving MolSysMT is best, manipulating rankings or hiding its limitations.
- Claiming proprietary models' training-data contents from output behavior.
- Treating an exploratory chat or manually pasted answer as a controlled API trial.
- Scraping unapproved sites, releasing private data, exposing tokens or making unapproved paid API calls.
- Conflating development observability (separate `moli-dev-observatory`) with scientific-tool visibility.
