#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from spec_utils import load_specs, validate_spec


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate canonical economics/finance table JSON.")
    parser.add_argument("spec", help="Path to a JSON table specification")
    args = parser.parse_args()
    try:
        specs = load_specs(args.spec)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    failed = False
    for index, spec in enumerate(specs, 1):
        errors, warnings = validate_spec(spec)
        prefix = spec.get("label") or f"table {index}"
        for warning in warnings:
            print(f"WARNING [{prefix}]: {warning}")
        for error in errors:
            print(f"ERROR [{prefix}]: {error}")
        failed = failed or bool(errors)
    if not failed:
        print(f"OK: validated {len(specs)} table specification(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
