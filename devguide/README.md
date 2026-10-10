# Developer guide — MOLI Visibility Observatory

**Checkpoint:** 2026-10-10. **Status:** research prototype with working public site and several real provider observations; NOT a fully automated longitudinal monitoring service.

This directory is the durable onboarding, architecture, methodology, execution and roadmap entry point for developers and Codex agents. Read it before making code changes.

## Read in order

1. [Purpose and boundaries](01_purpose.md) — why this exists; what is and is not measured.
2. [Architecture and data](02_architecture.md) — repository map, flows, contracts and security boundaries.
3. [Scientific methodology](03_methodology.md) — experimental tracks, denominators, evidence and threats to validity.
4. [State checkpoint](04_checkpoint.md) — verified observations, working pieces, limitations and blockers as of the dated checkpoint.
5. [Roadmap](05_roadmap.md) — ordered phases, acceptance tests and decision gates.
6. [Operations and handoff](06_operations.md) — local commands, workflows, review before running APIs, continuity procedure.
7. [Decision log](07_decisions.md) — architectural and methodological rationale.

The frozen query corpus lives in [`queries/v1.json`](../queries/v1.json). The public-facing [`docs/methodology.md`](../docs/methodology.md) summarizes the current tracks; this guide adds architecture, operations and the dated evidence checkpoint. The code, workflow definitions and source run records are authoritative when discrepancies exist.

## External planning

- [Observatory #1](https://github.com/uibcdf/moli-visibility-observatory/issues/1): general operations and measurement.
- [Observatory #2](https://github.com/uibcdf/moli-visibility-observatory/issues/2): Gemini stabilization, Exa-assisted evaluation and evidence preservation.
- [MolSysSuite #114](https://github.com/uibcdf/molsyssuite/issues/114): suite-level visibility methodology.
- [MolSysMT #378](https://github.com/uibcdf/molsysmt/issues/378): component-specific discoverability and scientific positioning.

## Rules for updating this guide

Any change to provider assumptions, costs, protocols, schemas, interpretation, publication or cadence **must** update the affected guide and checkpoint in the same change. Record verified facts with run URL/date; distinguish `implemented`, `tested`, `observed live` and `planned`. Never turn a missing result, truncation, quota error or unfinished run into a negative recommendation. No paid activation without explicit approval.
