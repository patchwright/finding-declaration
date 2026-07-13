"""findcheck CLI — validate finding-declaration documents."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from findcheck.validator import validate_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="findcheck",
        description="Validate finding-declaration documents against the v0.1 schema.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="validate a finding-declaration file")
    p_val.add_argument("file", help="path to the finding-declaration JSON (or '-' for stdin)")
    p_val.add_argument("--quiet", "-q", action="store_true",
                       help="exit code only, no output (for CI)")
    p_val.add_argument("--json", action="store_true",
                       help="structured JSON output")

    args = parser.parse_args(argv)

    if args.command == "validate":
        if args.file == "-":
            doc = json.load(sys.stdin)
            from findcheck.validator import validate
            result = validate(doc)
        else:
            result = validate_file(args.file)

        if args.json:
            out = {
                "valid": result.valid,
                "errors": [{"path": e.path, "message": e.message} for e in result.errors],
            }
            print(json.dumps(out, indent=2))
        elif not args.quiet:
            if result.valid:
                print(f"findcheck: valid ({Path(args.file).name})")
            else:
                print(f"findcheck: {len(result.errors)} error(s) in {Path(args.file).name}:")
                for e in result.errors:
                    print(f"  {e.path}: {e.message}")
        return result.exit_code

    return 0  # unreachable


if __name__ == "__main__":
    sys.exit(main())
