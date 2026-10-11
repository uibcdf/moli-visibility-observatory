# Decision record

This file preserves why the Observatory works as it does. Add dated decisions rather than rewriting history.

| Date | Decision | Rationale / consequence |
| --- | --- | --- |
| 2026-10-10 | Establish dedicated `moli-visibility-observatory` | Different responsibility from issue/commit development observatory. |
| 2026-10-10 | Freeze 20 unbranded V1 queries | Longitudinal comparability; variants require versioning. |
| 2026-10-10 | Keep Tavily, Exa and Gemini as **independent tracks** | Web ranked retrieval and generated recommendations are not interchangeable; no aggregate consensus. |
| 2026-10-10 | Keep synthetic data out of public real-results claims | Research integrity and reproducibility. |
| 2026-10-10 | Use reviewed summaries for public Pages | Avoid leaking API credentials, unreviewed data or improperly redistributing provider responses. |
| 2026-10-10 | Gemini closed-book and Exa-assisted separate | Distinguish baseline model behavior from evidence-assisted output; no causal claims from unmatched model/protocol. |
| 2026-10-10 | Preserve first 20-query Gemini 3.1 baseline; create `concise-v2` for Gemini 3.8 | Prevent truncated answers while retaining historical provenance, without pretending profiles are identical. |
| 2026-10-10 | Stop on nonretryable 429/403 and bound 5xx retries | Respect service limits and cost; missing data stays missing. |
| 2026-10-10 | Exa-assisted V0 uses source titles and URLs only | Safe first integration but insufficient to claim full documentary grounding; review relevance and content policy. |
| 2026-10-10 | Defer paid Gemini native Google Search grounding | Consumer subscription is not API entitlement; require explicit budget/authorization first. |
| 2026-10-10 | Plan, but do not enable, monthly collection | Need proven quota, provider terms, robust persistence and alerts first. |
| 2026-10-10 | Add prompt protocol and output token limit to new closed-book batch checkpoints | These settings affect comparability and should survive independently of code lookup; preserve historical artifacts and the additive V1 schema. |
| 2026-10-10 | Keep the first evidence manifest internal and content-free | Hash exact capture/benchmark bytes and preserve missingness without copying provider results into public data; a manifest cannot replace licensed source retention or authorize publication. |
| 2026-10-10 | Reconcile compatible local captures as an attempt ledger | Keep every missing/failed attempt and choose a result only when exactly one complete attempt exists; stop on duplicate complete evidence rather than silently overwriting it. Require explicit comparison metadata, including generation profile and token budget; historical captures missing it need separate provenance review. The panel remains internal and spans multiple runs. |
| 2026-10-10 | Verify web summaries offline without importing raw results into Pages | Recompute top-ten arithmetic and hit identity from an approved local capture while emitting only hashes/check names. Report that the historical Actions artifact identity, title wording and scientific URL-matcher validity are not proven by the existing summary schema. |
| 2026-10-10 | Version the closed-book explicit-name matching rule separately | Recompute only the text occurrence in complete STOP answers, preserving truncation/error/unattempted states as missing. Do not turn this automated mention check into a recommendation or accuracy judgment. |
| 2026-10-10 | Freeze V2 as a separate 48-prompt, four-stratum corpus | Broaden five documented use-case families with paired formulations, six unrelated controls and six each named-alternative and Spanish variants. Fixed order and exact bytes preserve repeatability; report each stratum and provider track separately. This is a protocol artifact, not a live result or authorization to spend quota. |
| 2026-10-11 | Prepare V2 segments without activating live workflows | Use a fixed 20/20/8 plan, exact corpus SHA-256 in new captures, an explicit V2 CLI switch and manifest checks for contiguous IDs. Keep Actions on V1 and reject V2 in the old pooled web renderer until stratum-aware analysis and rights review are complete. |
| 2026-10-11 | Analyze V2 strata only from compatible, local captures | Reuse exact-byte manifests and conflict checks, report web URL presence or model name occurrence by stratum and paired intent, and retain missingness. Keep the derivative internal; no automatic recommendation or publication claim. |

## Future decision candidates

Whether to archive original responses in the public repository or a restricted licensed store; choosing a durable versioned schema; multi-provider temporal sampling; judging scientifically meaningful recommendations and prompt contamination; trial budget for Google native search grounding.
