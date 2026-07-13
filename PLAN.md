Status: COMPLETE
# Finding-Declaration Schema — Plan + Definition-of-Done

## Design (evidence-backed)

**5 universal required fields** (agent 2, 6-domain survey + decisions.md convergence):
- `finding_id` — stable, citable identifier
- `claim` — the declarative assertion
- `verdict` — 5-state enum (below)
- `evidence` — polymorphic: {type: NUMERIC|STATISTICAL|PROOF|POC|QUALITATIVE|CITATION, artifact: ref, summary: string}
- `scope` — conditions under which the claim holds (env/population/axioms/segment)

**5 canonical verdict states** (agent 1, 8-domain derivation, necessity+sufficiency proven):
- CONFIRMED — supported by evidence/proof
- PARTIAL — supported weakly (attenuated, mixed, sub-threshold)
- REFUTED — contradicted by positive evidence against
- INCONCLUSIVE — insufficient evidence; question open
- UNDECIDABLE — proven the question can't be settled (formal-methods only; ≠ inconclusive)

**Optional extensions:** hypothesis, effect_size/severity, confidence, comparison, mechanism, localization, falsification_criterion, implication.
**Excluded (provenance layer):** timestamp, author, git_commit, seed, raw_data, pre_registration_hash.

## Dogfooding case (evoecos current-state audit — agent 3)

evoecos exhibits all 7 classic shipped-too-early failure modes:
1. decisions.md parsed by fragile regex (no machine-readable schema)
2. 3 incompatible status vocabularies (decisions.md / findings.json / findings.md)
3. substring matching as aggregation (loop_closure_audit.py GENERIC_STEMS)
4. no version field anywhere
5. findings.json overfit to smart-contract-audit shape
6. no conformance test suite
7. implicit optional/required contracts (parser treats Next: as optional)

## Plan (phased build)

### Phase 1 — the schema (the standard) ✅ DONE
- [x] Prose spec (RFC 2119 MUST/SHOULD/MAY): 5 required fields, 5 verdict states, optional extensions, conditional rules
- [x] JSON Schema meta-schema (machine-readable, self-describing, validates itself)
- [x] `$schema` version URI pinned (https://raw.githubusercontent.com/patchwright/finding-declaration/v0.1/schema.json)

### Phase 2 — validation ✅ DONE (v0.1 shippable)
- [x] Reference validator (`findcheck`): wraps JSON Schema 2020-12, standardized output, exit codes, --json/--quiet
- [x] Conformance test suite: 7 valid (per domain) + 6 invalid (per rule) fixtures, auto-discovered; 19 tests pass
- [x] Round-trip proof: real evoecos finding → migrate → validate → render to decision-gate.cjs format; stable-ID replaces substring matching

### Phase 3 — dogfooding (the internal proof) ✅ DONE (migration); rewire DEFERRED
- [x] Migration script: experiments_db 100/100 + decisions.md 70/70 → schema-validated JSON (170 findings dogfooded)
- [x] Profile mechanism: lifecycle_status extension for decisions (orthogonal axis preserved); optional extensions cover finding-type-specific needs
- [ ] Rewire decision-gate.cjs + loop_closure_audit.py to read schema natively — DEFERRED (production change touching the every-prompt gate; compatibility proven in Phase 2 roundtrip, ready to rewire but user-gated)

### Phase 4 — generalization + release ✅ DONE (generality + artifact); publish DECISION PENDING
- [x] Validate against external corpora: ClinicalTrials.gov-style + ML benchmark ablation migrate losslessly (not evoecos-shaped)
- [x] Worked examples: 7 valid cross-domain fixtures (double as conformance fixtures) + 2 external
- [x] Semver + backward-compat rules (SPEC §7) + README
- [ ] Package + publish — DECISION PENDING: see publish-tension below

## Definition-of-done (agent 3, derived from JSON Schema / Frictionless / RO-Crate / OpenAPI / Protobuf / Avro)

A v1.0 finding-declaration schema is DONE when:
1. Any producer can emit a finding; any consumer can validate it against a published JSON Schema
2. Validation outcome is determined by machine-checked rules (not a regex parser)
3. Schema version is self-declaring (`$schema` field)
4. A conformance test suite proves valid findings from every finding-type round-trip through every runtime consumer
5. Single normative status enum with documented migration from legacy vocabularies
6. Profile/extension mechanism (no overfit to one producer)
7. Semver + backward-compat rules + changelog written before ship, not after

**One-line:** the format is done when it is a schema with a validator and a conformance suite, not prose parsed by regex.

## Reconciliation note

Agent 2's preliminary hint (CONFIRMED|FALSIFIED|PARTIAL|NULL|UNKNOWN|OPEN) is superseded by agent 1's rigorous 8-domain derivation (CONFIRMED|PARTIAL|REFUTED|INCONCLUSIVE|UNDECIDABLE). Mapping: REFUTED=FALSIFIED; INCONCLUSIVE absorbs NULL/UNKNOWN; UNDECIDABLE is the formal-methods addition the 6-value hint lacked. OPEN is a lifecycle status (orthogonal axis, like deviated/superseded), not a verdict.

## Scope honesty

This is bigger than mutaprobe (a function). It's a standard + validator + conformance suite + migration + consumer-rewiring. Phase 1-2 (schema + validator + conformance) is the core deliverable. Phase 3 (dogfooding) is the internal proof. Phase 4 (generalize + release) is the external step. The full scope is a multi-session commitment; Phase 1-2 alone is shippable as a v0.1.
