# MOLI Visibility Observatory

A reproducible research prototype for measuring **scientific software discoverability** in web search. Initial case: **MolSysMT**.

> **First real web-search baseline recorded:** Tavily basic, 2026-10-10, 20/20 evaluable queries, Presence@10 5%, MRR@10 0.025. These are provider-specific discovery metrics, **not agent recommendation rates**. The earlier unarchived exploratory searches are not a quantitative baseline.

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

Independent AI-agent evaluation, monthly API schedules, and automatic paid usage are not enabled. An opt-in live Tavily adapter has been run successfully. Pages deployment uses reviewed summaries only and requires enabling GitHub Pages with GitHub Actions as its source. These require source terms/cost review and an auditable first real baseline. See [methodology](docs/methodology.md).

### Project issues

- [MolSysSuite #114](https://github.com/uibcdf/molsyssuite/issues/114): observatory methodology and publication.
- [MolSysMT #378](https://github.com/uibcdf/molsysmt/issues/378): scientific discoverability, tutorials and comparisons.
- [MOLI Development Observatory](https://github.com/uibcdf/moli-dev-observatory): a different project monitoring development activity.

## Opt-in Brave Search collection

A real provider adapter is now included (`visibility_observatory/brave.py`) but **not activated**. Official pricing: https://brave.com/search/api/ (provider credits and billing policy may change). The user must first authorize their own Brave API enrollment/terms and create a GitHub repository secret named `BRAVE_SEARCH_API_KEY`. No API key is committed. The collector requests the frozen 20 queries and records each ranked URL, title, provider settings and UTC timestamp; errors/short lists are not treated as negative observations.

**To start an explicitly authorized first baseline:** GitHub → repository **Settings → Secrets and variables → Actions** → New repository secret `BRAVE_SEARCH_API_KEY`; then Actions → **Collect opt-in Brave baseline** → Run workflow. The workflow uploads a temporary artifact containing recorded results and HTML; it does **not** publish Pages or schedule future API calls. Results must be reviewed for completeness, provider licensing and representativeness before public publication. Prefer configuring required reviewers on the `visibility-data-collection` environment if supported.

This adapter measures **search result presence, not agent recommendations**. Provider response count and rankings can vary by locale/time. The manual workflow has not been independently verified running in GitHub Actions.

## Free-tier candidate providers (manual opt-in)

Tavily and Exa adapters are available alongside the existing optional Brave connector.
They are **not enabled automatically** and their search results are **not AI-agent recommendations**.

1. Obtain a free-tier API key from [Tavily](https://www.tavily.com/) and/or [Exa](https://exa.ai/), subject to their current terms, account verification and allowed research/publication uses.
2. Save `TAVILY_API_KEY` or `EXA_API_KEY` at GitHub repository **Settings → Secrets and variables → Actions**. Never commit keys or paste them in issues.
3. Open **Actions → Collect opt-in free-provider baseline → Run workflow**. Select a provider; start with **1 query**, review the resulting artifact and API account usage, then run 20 if acceptable.
4. A completed 20-query run produces an observation JSON and a static HTML preview artifact. No cron or public Pages publishing is configured. The provider might return fewer than 10 results, and those samples will remain **unevaluable**.

CLI alternatives:

```bash
TAVILY_API_KEY=... python -m visibility_observatory.providers --provider tavily --max-queries 1
EXA_API_KEY=... python -m visibility_observatory.providers --provider exa --max-queries 1
python -m visibility_observatory --run build/observations/tavily.json --output build/tavily-site
```

**Budget and semantics:** each collector run makes at most the `--max-queries` configured search requests; Tavily uses basic search and Exa uses auto search. Free-tier credits and provider terms can change. Do not assume both ranked lists or presence@10 results are interchangeable. Calls are sequential and have no automated retries. Provider errors are recorded without exposing API keys.

## Public dashboard

A separate `visibility_observatory.publish` program renders **reviewed, committed summary records only** from `data/baselines/*.summary.json`. It never publishes synthetic examples, credentials or unreviewed raw search responses.

```bash
python -m visibility_observatory.publish --output build/public-site
python -m http.server --directory build/public-site 8000
```

[First reviewed summary](data/baselines/2026-10-10-tavily-basic.summary.json) · [Tavily source run](https://github.com/uibcdf/moli-visibility-observatory/actions/runs/38040732355).

**GitHub Pages setup:** Under **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**. The workflow `Publish reviewed visibility summaries` is configured to deploy only the reviewed dashboard. If Pages is not enabled, the deploy action may fail; re-run it after enabling. Expected Pages location (once published): https://uibcdf.github.io/moli-visibility-observatory/ . No monthly API collection is enabled.

## Gemini recommendation evaluation (opt-in; experimental)

A **separate** Gemini agent-response track is now available. It captures unprompted tool recommendations under two declared conditions: `closed_book` (no external search) and `google_search` (Google Search grounding). Answers remain **unadjudicated**; they are **not** evaluated with web Presence@10 or MRR@10 and are excluded from the public reviewed web-search dashboard.

Set `GEMINI_API_KEY` as an Actions repository secret, then manually run **Capture opt-in Gemini agent recommendations** with mode `closed_book` and **1** query first. Inspect the artifact and API usage before increasing to 5 or 20. Do not run `google_search` until confirming your Gemini API project/model is eligible for free grounding and has no billing risk. Default pinned identifier: `gemini-3.1-flash-lite`; availability and quotas may change. API subscription/billing is separate from Google AI Pro.

Captured data include model, mode, UTC time, responses, usage and (for search mode) grounding metadata. This track is only the **data capture** foundation; independent recommendation scoring and a longitudinal agent dashboard have not been implemented. See [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

No recurring runs or automatic Pages publication of agent responses are enabled.

### Gemini HTTP 404 recovery — 2026-10-10

The initial one-query run returned HTTP 404 for `gemini-2.5-flash-lite`. Google staff publicly documented that newly created projects may lack generation access to 2.5 models, even when those models appear in model listings. We therefore switched the default to the documented stable `gemini-3.1-flash-lite`, which has a text-generation free tier (subject to project quotas). This requires a new one-query run to validate your specific API project; no success is yet claimed. **Google Search grounding has been disabled** in the adapter/workflow because it is not available on that model's free tier; do not infer that all Gemini functionality is free. Sources: https://discuss.ai.google.dev/t/gemini-api-models-list-returns-gemini-2-5-flash-with-generatecontent-support-but-generatecontent-returns-404-not-found/184047 and https://ai.google.dev/gemini-api/docs/pricing .

## Full Gemini benchmark: checkpointed execution

The new manual workflow **Gemini complete benchmark (checkpointed)** executes up to all 20 closed-book queries in one run. It waits 8 seconds between prompts, allows the Gemini adapter's single retry for transient 502/503/504 failures, writes an atomic JSON checkpoint after each query, **continues** after persistent 5xx, and stops on 400/401/403/404/429 (configuration, authorization or quota). Incomplete responses and failed calls remain explicitly in the data and cannot count as non-mentions. The workflow uploads the partial/full checkpoint as an artifact even when the job fails.

It does **not** run automatically or make paid API calls on a schedule. Check free-tier quota before manually starting 20 queries. It does not currently restore a checkpoint across different GitHub Actions runs; it preserves within-run evidence to support future deduplicated merging.

No joint consensus is computed. Tavily and Exa measure separate web-search discoverability, and Gemini measures independent model output. Agent recommendations must be scored and adjudicated separately, rather than being assigned search-engine ranks.

## Gemini 3.8 Flash: model-controlled experiment (2026-10-10)

The manual `Gemini complete benchmark (checkpointed)` workflow now offers two **separate model identities**: `gemini-3.8-flash` (selected by default) and the previous `gemini-3.1-flash-lite`. Each capture stores its chosen model in the result. First test **count=1**, inspect the API project's quotas and token consumption, then consider a 20-query run. Distinct models must not be merged into one trend or silently replace the historical baseline.

Google's published [pricing](https://ai.google.dev/gemini-api/docs/pricing) lists free-tier text generation for Gemini 3.8 Flash but **Google Search grounding is unavailable on the API free tier**. The repository keeps grounding disabled; no paid/grounded workflow has been enabled. The favorable Gemini-web 3.8 Flash answer with web search is a separate qualitative observation, not a reproducible API record. A future grounded comparison requires explicit billing approval, cost caps and review of terms.

Web discovery, semantic search and model recommendation remain independently reported; no composite consensus score is justified.
