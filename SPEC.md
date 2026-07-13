# Finding Declaration Schema — Specification v0.1 (draft)

## 1. Purpose

A machine-readable format for declaring experiment **findings** — the verdict
layer (what an experiment established), distinct from metrics, provenance, and
workflow. Exists because no tracking tool or metadata standard covers this layer
(verified across 40+ tools/standards, 2026-07).

The canonical structure is derived from a cross-domain survey (ML, clinical,
A/B, security, formal-methods, simulation, systematic reviews, physics) — see
`PLAN.md` for the derivation evidence.

## 2. Conformance language (RFC 2119)

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be
interpreted as described in RFC 2119.

## 3. Document structure

A finding-declaration document is a JSON object. The root object:

- **MUST** contain a `$schema` field pinning this spec version
  (self-declaring version — consumers MUST be able to tell what version they read).
- **MUST** contain a `findings` array with one or more finding objects.
- **MAY** contain an `experiment` string (identifier of the producing experiment)
  and a `generated_at` RFC 3339 timestamp (provenance — RECOMMENDED, not part of
  any finding).

## 4. Required finding fields (5)

Every object in `findings` **MUST** contain exactly these five fields:

### 4.1 `finding_id` (string, REQUIRED)
A stable, citable identifier. **MUST** match `^[A-Za-z0-9][A-Za-z0-9_.-]*$`.
**MUST** be unique within the document. Without an ID, a finding cannot be
referenced, deduplicated, or gated on — universal by operational necessity.

### 4.2 `claim` (string, REQUIRED)
The declarative assertion ("X holds under Y"). **MUST NOT** be empty. A finding
without a declarative claim is raw data, not a finding.

### 4.3 `verdict` (enum, REQUIRED)
The truth-status of the claim. **MUST** be exactly one of:

| Value | Meaning |
|---|---|
| `CONFIRMED` | The claim is supported by the evidence/proof. |
| `PARTIAL` | The claim is supported but weakly (attenuated, mixed across metrics, sub-threshold, e.g. physics 3σ, clinical non-inferiority). |
| `REFUTED` | The claim is contradicted by positive evidence against it (e.g. physics exclusion, formal disproof, ML degradation). |
| `INCONCLUSIVE` | Insufficient evidence to confirm or refute; the question remains open and could be settled by more work. |
| `UNDECIDABLE` | Proven that the question cannot be settled within the applicable framework (formal-methods independence/undecidability — a terminal positive result, NOT "we lack data"). |

This 5-state set is necessary and sufficient (8-domain derivation, `PLAN.md`).
`UNDECIDABLE` is categorically distinct from `INCONCLUSIVE` — collapsing them
loses the difference between "unsettled" and "proven-unsettlable."

### 4.4 `evidence` (object, REQUIRED — polymorphic)
The basis for the verdict. The **form** varies by domain; the **presence** does
not. A finding without evidence is an opinion. **MUST** contain:

- `type` (enum, REQUIRED): one of `NUMERIC`, `STATISTICAL`, `PROOF`, `POC`,
  `QUALITATIVE`, `CITATION`.
- `summary` (string, REQUIRED): one-line human-readable digest. **MUST NOT** be empty.
- `artifact` (string, RECOMMENDED): a reference (path, URI, metric key) to the
  backing artifact. Omitted only when the evidence is self-contained in `summary`.

### 4.5 `scope` (object, REQUIRED)
The conditions under which the claim is asserted. **MUST** have at least one
property. Overgeneralization is the #1 cross-experiment failure mode; scope is
the only defense. Every domain conditions its claims (env/population/axioms/
segment/parameter-range). Examples: `{"environment": "CartPole"}`, `{"axioms":
"ZFC"}`, `{"population": "adults, n=240"}`, `{"protocol_version": "v2"}`.

## 5. Optional extensions (domain-specific)

These **MAY** be present. They are NOT universal (some domains cannot represent
them; making them required would force fiction):

- `hypothesis` (string) — the pre-stated prediction, when the finding tests one.
  Absent for exploratory/formal/theorem-as-claim findings.
- `effect_size` (number | object) — continuous magnitude (clinical HR, ML perf gap).
- `severity` (enum) — categorical magnitude (security HIGH/MEDIUM/LOW).
- `confidence` (object) — `{ci: [lo,hi], p_value, n, test_type}` or `{rating: 1-5}`.
- `comparison` (string) — `finding_id` of a baseline this is compared against.
- `mechanism` (string | object) — causal/mechanistic model (failure-mode class, clinical mechanism).
- `localization` (object) — where the finding lives (`{file, line_range}` / `{module, theorem}`).
- `falsification_criterion` (string) — what evidence would overturn this verdict.
- `implication` (string) — what to do with this finding.

## 6. Excluded (belong to provenance, not findings)

These **MUST NOT** be required finding fields; they live in the provenance layer
(the experiment/document context): `timestamp`, `author`, `git_commit`, `seed`,
`compute`, `runtime`, `raw_data`, `logs`, `pre_registration_hash`,
`reproducibility_status`. Findings **MAY** reference provenance via
`evidence.artifact`, not embed it.

## 7. Versioning

This is v0.1 (draft). The `$schema` URI pins the version. When published:
- **Major** (1.0): breaking changes (new required field, removed field, changed enum) — new `$schema` URI + migration path.
- **Minor** (0.x): backward-compatible additions (new optional fields).
- **Patch**: clarifications that do not change validation outcomes.

Backward-compatibility rules (Avro-style): adding optional fields with defaults
is always safe; adding a required field or a verdict-enum value is a major change.

## 8. Serialization

JSON is the canonical serialization. YAML is an accepted alternative (same
structure). The `$schema` field **MUST** be present in either.

## 9. Provenance of this design

- 5 required fields: derived from 6-domain survey, confirmed by evoecos
  `decisions.md` converging on the same core from the consumption side.
- 5 verdict states: derived from 8-domain necessity/sufficiency proof, confirmed
  by evoecos `_normalize_verdict` independently arriving at cardinality 5.
- See `PLAN.md` for full evidence.
