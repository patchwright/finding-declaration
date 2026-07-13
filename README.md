# finding-declaration

**A machine-readable standard for declaring experiment findings — the verdict layer no tracking tool or metadata standard covers.**

Experiments produce results in ad-hoc formats. The *finding* — what was established (hypothesis verdict + evidence) — is trapped in prose docstrings or reverse-engineered by fragile parsers. This standard declares findings in a structured, machine-validatable format so they can be extracted deterministically, aggregated across experiments, and consumed by downstream tools.

## What it is

A JSON Schema (2020-12) for declaring findings, plus `findcheck` — the reference validator.

**Verified uncovered:** 40+ tracking tools (MLflow, W&B, DVC…) and metadata standards (Frictionless, RO-Crate, schema.org, PROV-O, PRISMA…) cover metrics, provenance, and data description — *none* covers the verdict layer. Demand validated: PaperClaw (arXiv:2606.22610) invented its own verdict vocabulary because no standard existed.

## The schema (5 required fields × 5 verdict states)

```
finding_id  — stable, citable identifier
claim       — the declarative assertion
verdict     — CONFIRMED | PARTIAL | REFUTED | INCONCLUSIVE | UNDECIDABLE
evidence    — {type, summary, artifact} (polymorphic: NUMERIC/STATISTICAL/PROOF/POC/QUALITATIVE/CITATION)
scope       — conditions under which the claim holds
```

Optional extensions: `hypothesis`, `effect_size`, `severity`, `confidence`, `comparison`, `mechanism`, `localization`, `falsification_criterion`, `implication`, + domain-specific (e.g. `lifecycle_status` for decision ledgers).

`UNDECIDABLE` (formal-methods: proven-unsettlable) is distinct from `INCONCLUSIVE` (insufficient evidence, could be settled). Derived from an 8-domain survey; evoecos's own `_normalize_verdict` independently arrived at the same cardinality.

## Install + use

```bash
pip install -e .  # findcheck validator + bundled schema
findcheck validate my-findings.json        # exit 0 valid, 1 invalid
findcheck validate my-findings.json --json # structured output
findcheck validate my-findings.json -q     # CI mode (exit only)
```

## Proven on real data

- **evoecos experiments_db:** 100/100 findings migrate + validate (CONFIRMED 29, PARTIAL 10, REFUTED 13, INCONCLUSIVE 47, UNDECIDABLE 1)
- **evoecos decisions.md:** 70/70 entries migrate + validate, lifecycle axis preserved as extension
- **External:** ClinicalTrials.gov-style results + ML benchmark ablations migrate losslessly — not evoecos-shaped
- **Conformance:** 7 valid cross-domain + 6 invalid-per-rule fixtures, 19 tests

## Why it matters

evoecos's own finding infrastructure exhibited all 7 classic shipped-too-early failure modes (fragile regex parsing, 3 incompatible status vocabularies, substring-matching aggregation, no version field, overfit to one producer, no conformance suite, implicit contracts). This schema fixes all of them: stable IDs replace substring matching, a single normative enum replaces the vocabulary chaos, the `$schema` field makes versioning self-declaring, and the conformance suite makes validity machine-checkable.

## Versioning

v0.1 (draft). Semver: major = breaking (new required field, changed enum), minor = backward-compatible additions, patch = clarifications. The `$schema` URI pins the version. See `SPEC.md` §7 for the full evolution rules.

## Status

Phase 1 (spec + meta-schema) ✅ · Phase 2 (validator + conformance + roundtrip) ✅ · Phase 3 (migration: 170 findings dogfooded) ✅ · Phase 4 (external generality proven) ✅. The production consumer-rewire (decision-gate.cjs / loop_closure_audit.py reading schema natively) is the remaining dogfood step — gated as a production change.

## License

MIT
