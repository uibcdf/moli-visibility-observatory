# Roadmap — phase gates, not promises

This roadmap guides priorities; current blockers and validated run evidence are in [checkpoint](04_checkpoint.md). Issue #1 holds global planning and #2 implementation tracking.

## P0 — documentation and audit (immediate)

- [x] Establish developer guide as source of durable intent and checkpoint.
- [ ] Audit current code, CI, Pages and test coverage from a clean checkout; reconcile stale top-level docs.
- [ ] Record protocol/data-schema inventory and source licensing; identify expensive/unsafe actions.
- **Gate:** a new developer can reproduce local tests and explain each metric without conversation context.

## P1 — stabilize measurement contracts and quota handling

- [ ] Formalize provider version/configuration, complete/error/partial states, output token profile and explicit denominators.
- [ ] Gemini 3.8: verify actual free-tier limits, 429 responses, rate limiting, backoff and fail-closed conditions.
- [ ] Improve transport timeouts and error categorization; do not silently hide failed queries.
- [ ] Validate 1-query then bounded multi-query pilot for concise-v2 and Exa-assisted.
- **Gate:** test evidence plus at least one complete live bounded assisted pilot; no unexpected spending.

## P2 — durable, verifiable evidence

- [ ] Define approved retention and publication of raw answers/results; enforce third-party ToS and privacy constraints.
- [ ] Store run manifests, query IDs, model/provider metadata, source lists and content hashes; immutable run identity.
- [ ] Validated merge/resume across runs with duplicate/conflict checks and missing-data semantics.
- [ ] Separate unreviewed raw evidence from reviewed public summaries.
- **Gate:** raw-to-summary reconstruction validated from a retained run; no dependence on expiring artifacts.

## P3 — Exa-assisted and scientific evaluation

- [ ] Review relevance of the Exa top-five source set; assess whether titles/URLs suffice versus licensed snippets/content.
- [ ] Complete controlled same-model `closed_book` vs `exa_assisted` under matched concise-v2 settings.
- [ ] Adjudicate mention versus recommendation, ranking and technical correctness; track older MolSysMT versions.
- **Gate:** an auditable non-synthetic experiment with explicit evaluation rubric and scope limits.

## P4 — public dashboard

- [ ] Build separate histories for Tavily, Exa, Gemini closed-book and Exa-assisted, with query drill-down and provenance.
- [ ] Publish only reviewed/legal datasets and visible sample-quality caveats.
- [ ] Check actual public deployment and verify links, accessibility and stale snapshots.
- **Gate:** a reader can reproduce every published summary from permitted archived evidence.

## P5 — qualified automation

- [ ] Propose monthly schedule only after free-tier quota, terms, costs, alerts and fault-tolerance have been reviewed.
- [ ] Prevent unexpected billing, monitor quota and preserve partial results.
- [ ] Future optional paid Gemini-native Google grounding remains **deferred**: require explicit spend approval and a hard budget plan.
- **Gate:** repeated scheduled runs preserve integrity across provider outages without silent failures.

Do not introduce a composite 'AI visibility score' or infer model training cutoff effects from a single uncontrolled answer.
