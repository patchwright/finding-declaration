"""Conformance test suite — the reference for what's valid and invalid.

Auto-discovers examples/valid/*.json (must pass) and examples/invalid/*.json
(must fail). Adding a fixture automatically extends the suite. This is the
Bowtie-analog: the corpus IS the reference.
"""
import json
from pathlib import Path

import pytest

from findcheck.validator import validate

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


@pytest.mark.parametrize("fixture", sorted((EXAMPLES / "valid").glob("*.json")),
                         ids=lambda p: p.stem)
def test_valid_fixtures_pass(fixture):
    """Every valid fixture MUST validate clean."""
    result = validate(_load(fixture))
    assert result.valid, f"{fixture.name} unexpectedly INVALID: {[e.message for e in result.errors]}"


@pytest.mark.parametrize("fixture", sorted((EXAMPLES / "invalid").glob("*.json")),
                         ids=lambda p: p.stem)
def test_invalid_fixtures_rejected(fixture):
    """Every invalid fixture MUST be rejected (at least one error)."""
    result = validate(_load(fixture))
    assert not result.valid, f"{fixture.name} unexpectedly VALID (validator missed a rule)"


class TestExitCodes:
    """The CI contract: valid → exit 0, invalid → exit 1."""

    def test_valid_exit_zero(self):
        assert validate(_load(EXAMPLES / "valid" / "experiment.json")).exit_code == 0

    def test_invalid_exit_one(self):
        assert validate(_load(EXAMPLES / "invalid" / "bad-verdict.json")).exit_code == 1


class TestErrorStructure:
    """Errors carry path + message (standardized output for tooling)."""

    def test_error_has_path_and_message(self):
        result = validate(_load(EXAMPLES / "invalid" / "missing-verdict.json"))
        assert not result.valid
        e = result.errors[0]
        assert hasattr(e, "path") and hasattr(e, "message")
        assert "findings" in e.path  # the error is on a finding
