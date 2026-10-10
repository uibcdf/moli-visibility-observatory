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

## Future decision candidates

Whether to archive original responses in the public repository or a restricted licensed store; choosing a durable versioned schema; multi-provider temporal sampling; judging scientifically meaningful recommendations and prompt contamination; trial budget for Google native search grounding.
