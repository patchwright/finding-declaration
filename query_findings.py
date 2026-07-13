#!/usr/bin/env python3
"""
Minimal finding-query consumer (the dogfood).

Reads a schema-validated findings document and answers metabolism-relevant
questions — proving the schema is consumable, not just valid. This is the
internal dogfood: evoecos's finding-navigation works off the schema instead of
re-parsing decisions.md / experiments_db each time.

NOT the full aggregator (that's the 'then we'll see' step) — just enough query
surface to prove the schema serves a real need.
"""
import json
import sys
from collections import Counter
from pathlib import Path

# Reuse the validator to ensure we only ever read valid findings
sys.path.insert(0, str(Path(__file__).parent / "src"))
from findcheck.validator import validate


def load(path: str) -> dict:
    doc = json.loads(Path(path).read_text())
    result = validate(doc)
    if not result.valid:
        print(f"ERROR: {path} is not a valid finding-declaration ({len(result.errors)} errors)", file=sys.stderr)
        for e in result.errors[:3]:
            print(f"  {e.path}: {e.message}", file=sys.stderr)
        sys.exit(2)
    return doc


def cmd_stats(doc: dict) -> None:
    findings = doc["findings"]
    verdicts = Counter(f["verdict"] for f in findings)
    scopes = Counter(next(iter(f["scope"])) if f["scope"] else "?" for f in findings)
    print(f"{len(findings)} findings")
    print("verdict distribution:")
    for v, n in verdicts.most_common():
        print(f"  {v:14s} {n}")
    print(f"distinct scope keys: {len(scopes)}")


def cmd_by_verdict(doc: dict, verdict: str) -> None:
    matches = [f for f in doc["findings"] if f["verdict"] == verdict.upper()]
    print(f"{len(matches)} {verdict.upper()} findings:")
    for f in matches[:20]:
        print(f"  {f['finding_id']:40s} {f['claim'][:70]}")


def cmd_get(doc: dict, finding_id: str) -> None:
    for f in doc["findings"]:
        if f["finding_id"] == finding_id:
            print(json.dumps(f, indent=2))
            return
    print(f"finding_id {finding_id!r} not found", file=sys.stderr)
    sys.exit(1)


def cmd_rescue_candidates(doc: dict, audit_path: str | None = None) -> None:
    """CONFIRMED/PARTIAL findings worth re-examining for metabolism.

    Without --audit: shows all CONFIRMED/PARTIAL findings (over-includes ones
    already closed).
    With --audit PATH: cross-references loop_closure_audit JSON and shows only
    findings whose experiment is still LEAK (not CLOSED/CITED/METABOLIZED/WIRED) —
    the TRUE rescue pool (orphaned positive findings that haven't reached action).
    """
    candidates = [f for f in doc["findings"] if f["verdict"] in ("CONFIRMED", "PARTIAL")]
    if not audit_path:
        print(f"{len(candidates)} CONFIRMED/PARTIAL findings (no closure cross-ref — may include already-closed):")
        for f in candidates[:15]:
            print(f"  [{f['verdict']:9s}] {f['finding_id']:40s} {f['claim'][:60]}")
        return
    # Cross-reference closure status from loop_closure_audit JSON
    audit = json.loads(Path(audit_path).read_text())
    closed_verdicts = {"CLOSED", "METABOLIZED", "WIRED", "CITED", "COMPOSTED"}
    status_map = {a["id"]: a["verdict"] for a in audit.get("artifacts", [])}
    true_rescue, already_closed, unknown = [], [], []
    for f in candidates:
        exp = f.get("scope", {}).get("experiment", "")
        status = status_map.get(f"experiment:{exp}")
        if status in closed_verdicts:
            already_closed.append((f, status))
        elif status == "LEAK":
            true_rescue.append(f)
        else:
            unknown.append((f, status))  # not in audit — conservatively surface
    print(f"rescue pool (CONFIRMED/PARTIAL AND still LEAK): {len(true_rescue)} true candidates")
    for f in true_rescue[:20]:
        print(f"  [{f['verdict']:9s}] {f['finding_id']:40s} {f['claim'][:55]}")
    if unknown:
        print(f"  (+ {len(unknown)} not in audit — status unknown, surfaced conservatively)")
    print(f"  (excluded {len(already_closed)} already-closed CONFIRMED/PARTIAL findings — reached action)")


def main():
    if len(sys.argv) < 3:
        print("usage: query_findings.py <findings.json> {stats|by-verdict VERDICT|get ID|rescue}", file=sys.stderr)
        sys.exit(1)
    doc = load(sys.argv[1])
    cmd = sys.argv[2]
    if cmd == "stats":
        cmd_stats(doc)
    elif cmd == "by-verdict" and len(sys.argv) > 3:
        cmd_by_verdict(doc, sys.argv[3])
    elif cmd == "get" and len(sys.argv) > 3:
        cmd_get(doc, sys.argv[3])
    elif cmd == "rescue":
        # optional --audit PATH flag for closure cross-reference
        audit_path = None
        if "--audit" in sys.argv:
            idx = sys.argv.index("--audit")
            if idx + 1 < len(sys.argv):
                audit_path = sys.argv[idx + 1]
        cmd_rescue_candidates(doc, audit_path)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
