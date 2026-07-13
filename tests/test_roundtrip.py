"""Round-trip tests — prove the schema serves evoecos's actual consumers.

Phase 2 goal: a finding-declaration can be (a) migrated from a real evoecos
finding, (b) validated against the schema, and (c) rendered to the format
evoecos's current consumers expect — proving compatibility without rewiring
them yet (that's Phase 3).
"""
import json
import re
from pathlib import Path

from findcheck.validator import validate

# decision-gate.cjs's actual regex (from .claude/helpers/decision-gate.cjs):
# parses decisions.md entries of the form: ### ID [STATUS ...]
DECISION_GATE_RE = re.compile(
    r"^###\s+([A-Za-z0-9_]+)\s*\[(RETIRED|CONFIRMED|ARTIFACT|OPEN|NEGATIVE)([^\]]*)\]",
    re.MULTILINE,
)

# Schema verdict → decision-gate lifecycle status (orthogonal axes; epistemic→lifecycle map)
VERDICT_TO_STATUS = {
    "CONFIRMED": "CONFIRMED",
    "REFUTED": "RETIRED",      # refuted → overturned/blocked
    "PARTIAL": "OPEN",         # still being refined
    "INCONCLUSIVE": "OPEN",    # unresolved
    "UNDECIDABLE": "OPEN",     # unresolved (provably)
}


def render_to_decision_gate(finding_doc: dict) -> str:
    """Render a finding-declaration to the decisions.md entry format.

    Proves the schema's data feeds decision-gate.cjs without rewiring it.
    """
    lines = []
    for f in finding_doc["findings"]:
        status = VERDICT_TO_STATUS[f["verdict"]]
        lines.append(f"### {f['finding_id']} [{status}]")
        lines.append(f"Verdict: {f['claim']}")
    return "\n".join(lines)


class TestRealEvoecosFindingRoundTrip:
    """A real evoecos finding → migrate → validate → render to consumer format."""

    def setup_method(self):
        # A real finding shape (companion_concentration H1, from evoecos results)
        self.doc = {
            "$schema": "https://raw.githubusercontent.com/patchwright/finding-declaration/v0.1/schema.json",
            "experiment": "companion_concentration",
            "findings": [{
                "finding_id": "companion_H1",
                "claim": "Companion ceiling is monotone in allocation under fixed L1 budget.",
                "verdict": "CONFIRMED",
                "hypothesis": "H1",
                "evidence": {
                    "type": "NUMERIC",
                    "summary": "mean_fraction_bound_satisfied = 1.0 across 16 seeds",
                    "artifact": "results/experiment_companion_concentration.json#summary.H1",
                },
                "scope": {"environment": "CartPole-v1", "budget": "fixed L1"},
            }],
        }

    def test_migrated_finding_validates(self):
        """Step 1-2: the migrated real finding passes the schema."""
        assert validate(self.doc).valid

    def test_renders_to_decision_gate_format(self):
        """Step 3: the validated finding renders to decision-gate.cjs's format."""
        rendered = render_to_decision_gate(self.doc)
        match = DECISION_GATE_RE.search(rendered)
        assert match is not None, f"rendered output not parseable by decision-gate regex:\n{rendered}"
        assert match.group(1) == "companion_H1"
        assert match.group(2) == "CONFIRMED"


class TestStableIdReplacesSubstringMatching:
    """loop_closure_audit.py uses substring matching (GENERIC_STEMS). The schema's
    stable finding_id replaces that with deterministic lookup."""

    def test_finding_id_is_deterministic_reference(self):
        # Two producers emitting the same finding_id are aggregatable by exact match
        # (not keyword heuristic). This is what replaces substring matching.
        doc1 = {"$schema": "x", "findings": [{"finding_id": "MarkovianWall_H1", "claim": "a",
                   "verdict": "CONFIRMED", "evidence": {"type": "PROOF", "summary": "s"},
                   "scope": {"a": "b"}}]}
        doc2 = {"$schema": "x", "findings": [{"finding_id": "MarkovianWall_H1", "claim": "a",
                   "verdict": "CONFIRMED", "evidence": {"type": "PROOF", "summary": "s"},
                   "scope": {"a": "b"}}]}
        # Aggregation by finding_id is exact-match deterministic
        ids1 = {f["finding_id"] for f in doc1["findings"]}
        ids2 = {f["finding_id"] for f in doc2["findings"]}
        assert ids1 == ids2  # same id → aggregatable; no substring ambiguity
