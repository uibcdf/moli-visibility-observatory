# MOLI Visibility Observatory

A reproducible research prototype for measuring **scientific software discoverability** in web search. Initial case: **MolSysMT**.

> **No validated visibility baseline has been collected.** The exploratory October 2026 conversation did not preserve full result ranks and provenance; it is not a 0/20 recall@10 measurement or a multiple-agent benchmark.

## Current features

- 20 frozen, unbranded, task-oriented queries: [queries/v1.json](queries/v1.json).
- Ingest provider-supplied ranked results with explicit provenance and capture status.
- Compute web **presence@k** and **MRR@k**, excluding incomplete and failed responses from the denominator.
- Generate static HTML and machine-readable JSON; tests and manual CI build available.
- A **clearly synthetic** sample fixture validates rendering; it is not observational data.

## Try locally

```bash
python -m unittest discover -s tests -v
python -m visibility_observatory --run examples/sample.json --output build/site
python -m http.server --directory build/site 8000
```

## Not yet enabled

No live search provider, independent AI-agent evaluation, monthly schedule, paid API usage, or automatic public Pages deployment. These require source terms/cost review and an auditable first real baseline. See [methodology](docs/methodology.md).

### Project issues

- [MolSysSuite #114](https://github.com/uibcdf/molsyssuite/issues/114): observatory methodology and publication.
- [MolSysMT #378](https://github.com/uibcdf/molsysmt/issues/378): scientific discoverability, tutorials and comparisons.
- [MOLI Development Observatory](https://github.com/uibcdf/moli-dev-observatory): a different project monitoring development activity.
