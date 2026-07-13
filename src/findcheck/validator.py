"""findcheck — reference validator for finding-declaration documents.

Wraps the JSON Schema 2020-12 meta-schema with standardized output and exit
codes. The validator's value is ENABLING: producers emit valid findings with
confidence, consumers trust what they read. Rejecting invalid documents is a
side effect of precision, not the primary purpose.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class ValidationError:
    """One validation error: where + what."""
    path: str       # dot-path to the offending field (e.g. "findings.0.verdict")
    message: str    # human-readable description


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating one document."""
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return 0 if self.valid else 1


def _load_schema() -> dict:
    """Load the bundled meta-schema (finding-declaration v0.1)."""
    schema_text = resources.files("findcheck").joinpath("schema.json").read_text()
    return json.loads(schema_text)


def _path(error) -> str:
    """Render a jsonschema error's path as a dot-string."""
    parts = [str(p) for p in error.absolute_path]
    return ".".join(parts) if parts else "(root)"


def validate(doc: dict) -> ValidationResult:
    """Validate a finding-declaration document (already parsed).

    Zero false positives by construction: the verdict is determined by the
    JSON Schema meta-schema, which is machine-checked and self-describing.
    """
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(
        (ValidationError(_path(e), e.message) for e in validator.iter_errors(doc)),
        key=lambda e: e.path,
    )
    return ValidationResult(not errors, errors)


def validate_file(path: str | Path) -> ValidationResult:
    """Validate a finding-declaration file (JSON)."""
    doc = json.loads(Path(path).read_text())
    return validate(doc)
