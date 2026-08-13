#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from spec_utils import cell_parts, load_specs, validate_spec


def audit(spec):
    errors, warnings = validate_spec(spec)
    significance = (spec.get("inference") or {}).get("significance", spec.get("significance", {}))
    stars_used = set()
    decimals_by_row = defaultdict(set)
    for row in spec.get("rows", []):
        for cell in (row.get("values") or {}).values():
            value, stars, decimals, _parentheses, _display = cell_parts(cell)
            if stars:
                stars_used.add(stars)
            if isinstance(value, float) and decimals is not None:
                decimals_by_row[row.get("label", "")].add(decimals)
        if row.get("kind") == "metadata" and str(row.get("label", "")).lower() in {"observations", "n", "样本量"}:
            for cell in (row.get("values") or {}).values():
                value, *_ = cell_parts(cell)
                if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
                    warnings.append("observations should be stored as integer values")
    undeclared = stars_used - set(significance)
    if undeclared:
        errors.append(f"stars used but not declared: {', '.join(sorted(undeclared))}")
    for label, decimals in decimals_by_row.items():
        if len(decimals) > 1:
            warnings.append(f"mixed decimal precision in row: {label}")
    notes = " ".join(str(note) for note in spec.get("notes", []))
    if stars_used and not any(token in notes for token in ("significance", "显著", "denote")):
        warnings.append("stars are used but the notes do not explain significance")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit economics/finance table semantics and display rules.")
    parser.add_argument("spec")
    args = parser.parse_args()
    try:
        specs = load_specs(args.spec)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    failed = False
    for index, spec in enumerate(specs, 1):
        errors, warnings = audit(spec)
        prefix = spec.get("label") or f"table {index}"
        for warning in warnings:
            print(f"WARNING [{prefix}]: {warning}")
        for error in errors:
            print(f"ERROR [{prefix}]: {error}")
        failed = failed or bool(errors)
    if not failed:
        print(f"OK: audited {len(specs)} table specification(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
