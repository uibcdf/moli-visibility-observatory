# Roadmap — phase gates, not promises

This roadmap guides priorities; current blockers and validated run evidence are in [checkpoint](04_checkpoint.md). Issue #1 holds global planning and #2 implementation tracking.

## P0 — documentation and audit (immediate)

- [x] Establish developer guide as source of durable intent and checkpoint.
- [x] Audit current code, CI, Pages and test coverage from a clean local clone; reconcile stale top-level docs. The 2026-10-10 audit and hosted verification are in the checkpoint; no new hosted run was triggered for this documentation change.
- [x] Record protocol/data-schema and workflow cost-risk inventory in the architecture guide.
- [ ] Resolve provider storage, metric-publication and redistribution rights against the actual account agreements. A preliminary 2026-10-10 reading flagged Tavily and Exa restrictions; see architecture and checkpoint before adding public metrics or raw archives.
- **Gate:** a new developer can reproduce local tests and explain each metric without conversation context.

## P1 — stabilize measurement contracts and quota handling

- [ ] Formalize provider version/configuration, complete/error/partial states, output token profile and explicit denominators. New closed-book batch checkpoints now record the prompt protocol and output token limit; historical runs and remaining fields still need review.
- [ ] Gemini 3.8: verify actual free-tier limits, 429 responses, rate limiting, backoff and fail-closed conditions.
- [ ] Improve transport timeouts and error categorization; do not silently hide failed queries.
- [ ] Validate 1-query then bounded multi-query pilot for concise-v2 and Exa-assisted.
- **Gate:** test evidence plus at least one complete live bounded assisted pilot; no unexpected spending.

## P2 — durable, verifiable evidence

- [ ] Define approved retention and publication of raw answers/results; enforce third-party ToS and privacy constraints.
- [ ] Store run manifests, query IDs, model/provider metadata, source lists and content hashes; immutable run identity. An offline `evidence-manifest-v1` builder now validates IDs/states and hashes exact source/benchmark bytes, but no approved durable store or source-list retention exists.
- [ ] Validated merge/resume across runs with duplicate/conflict checks and missing-data semantics. An offline `evidence-merge-v1` ledger now reconciles compatible local captures and rejects duplicate or competing complete attempts; automatic cross-workflow resume and approved source retention remain open.
- [ ] Separate unreviewed raw evidence from reviewed public summaries.
- **Gate:** raw-to-summary reconstruction validated from a retained run; no dependence on expiring artifacts. Offline web arithmetic and closed-book explicit-mention verifiers now have synthetic tests only; no licensed real source archive or recommendation-quality adjudication is established.

## P3 — Exa-assisted and scientific evaluation

- [x] Freeze the offline V2 question protocol: 15 paired primary intents plus separate six-question control, named-alternative and Spanish strata. Structural validator and byte hash guard the corpus; no V2 provider measurements exist.
- [x] Prepare offline 20/20/8 V2 segment plan; add bounded segment selection and exact benchmark-byte provenance to Tavily/Exa, checkpointed Gemini and Exa-assisted capture paths. Their manual Actions workflows still use V1; no V2 API call has occurred.
- [x] Add local, unreviewed V2 analysis by stratum and compatible track, with paired A/B and named-alternative/Spanish descriptions, retaining missingness. Synthetic tests only; no public V2 metric.
- [ ] Before V2 activation, review scientific wording with domain maintainers, applicable account terms, quota and retention rights; run a bounded authorized pilot. Human adjudication and permitted source provenance remain necessary before any public V2 metric.
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
