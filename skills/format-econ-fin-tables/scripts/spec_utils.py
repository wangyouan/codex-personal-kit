from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

TABLE_TYPES = {
    "regression",
    "descriptive",
    "correlation",
    "variable_definition",
    "difference",
    "robustness",
}
ROW_KINDS = {"coefficient", "statistic", "data", "metadata", "panel", "spacer"}
STATISTIC_TYPES = {"standard_error", "t_statistic", "z_statistic"}


def load_specs(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    specs = data if isinstance(data, list) else [data]
    if not all(isinstance(item, dict) for item in specs):
        raise ValueError("The JSON root must be a table object or an array of table objects.")
    return specs


def validate_spec(spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    required = ("version", "table_type", "language", "label", "title", "columns", "rows")
    for field in required:
        if field not in spec:
            errors.append(f"missing required field: {field}")
    if errors:
        return errors, warnings
    if spec["version"] != 1:
        errors.append("version must be 1")
    if spec["table_type"] not in TABLE_TYPES:
        errors.append(f"unsupported table_type: {spec['table_type']}")
    if spec["language"] not in {"en", "zh"}:
        errors.append("language must be 'en' or 'zh'")
    if not isinstance(spec["columns"], list) or not spec["columns"]:
        errors.append("columns must be a non-empty array")
        return errors, warnings
    keys = [col.get("key") for col in spec["columns"] if isinstance(col, dict)]
    if len(keys) != len(spec["columns"]) or any(not key for key in keys):
        errors.append("every column must be an object with a non-empty key")
    if len(set(keys)) != len(keys):
        errors.append("column keys must be unique")
    if not isinstance(spec["rows"], list):
        errors.append("rows must be an array")
        return errors, warnings
    previous: dict[str, Any] | None = None
    seen_pairs: set[str] = set()
    for index, row in enumerate(spec["rows"], 1):
        if not isinstance(row, dict):
            errors.append(f"row {index} must be an object")
            continue
        kind = row.get("kind")
        if kind not in ROW_KINDS:
            errors.append(f"row {index} has unsupported kind: {kind}")
        if kind not in {"panel", "spacer"} and "label" not in row:
            errors.append(f"row {index} is missing label")
        values = row.get("values", {})
        if values is not None and not isinstance(values, dict):
            errors.append(f"row {index} values must be an object")
        elif isinstance(values, dict):
            unknown = sorted(set(values) - set(keys))
            if unknown:
                errors.append(f"row {index} uses unknown columns: {', '.join(unknown)}")
        if kind == "coefficient":
            pair_id = row.get("pair_id")
            if not pair_id:
                errors.append(f"coefficient row {index} requires pair_id")
            else:
                seen_pairs.add(str(pair_id))
        if kind == "statistic":
            pair_id = row.get("pair_id")
            if not pair_id:
                errors.append(f"statistic row {index} requires pair_id")
            if not previous or previous.get("kind") != "coefficient" or previous.get("pair_id") != pair_id:
                errors.append(f"statistic row {index} must immediately follow its coefficient pair")
        previous = row
    coefficient_pairs = {str(r.get("pair_id")) for r in spec["rows"] if r.get("kind") == "coefficient"}
    statistic_pairs = {str(r.get("pair_id")) for r in spec["rows"] if r.get("kind") == "statistic"}
    for pair in sorted(coefficient_pairs - statistic_pairs):
        errors.append(f"coefficient pair {pair} has no statistic row")
    if spec["table_type"] in {"regression", "robustness"}:
        inference = spec.get("inference")
        if not isinstance(inference, dict):
            errors.append("regression-style tables require inference")
        else:
            if inference.get("statistic_type") not in STATISTIC_TYPES:
                errors.append("inference.statistic_type must identify standard error, t, or z")
            if not inference.get("cluster"):
                errors.append("inference.cluster is required; use 'none' only when intended")
            if not isinstance(inference.get("significance"), dict):
                errors.append("inference.significance is required")
    if len(spec["columns"]) > 8:
        warnings.append("more than eight result columns: consider landscape or splitting panels")
    if any(len(str(row.get("label", ""))) > 42 for row in spec["rows"]):
        warnings.append("long row label detected: widen, wrap at words, or define an abbreviation")
    if not spec.get("notes"):
        warnings.append("no table notes supplied")
    return errors, warnings


def cell_parts(cell: Any, default_decimals: int = 3) -> tuple[Any, str, int | None, bool, str | None]:
    if isinstance(cell, dict):
        return (
            cell.get("value"),
            str(cell.get("stars", "")),
            cell.get("decimals", default_decimals),
            bool(cell.get("parentheses", False)),
            cell.get("display"),
        )
    return cell, "", default_decimals, False, None


def display_cell(cell: Any, default_decimals: int = 3) -> str:
    if cell is None:
        return ""
    value, stars, decimals, parentheses, display = cell_parts(cell, default_decimals)
    if display is not None:
        text = str(display)
    elif isinstance(value, bool):
        text = "Yes" if value else "No"
    elif isinstance(value, int):
        text = f"{value:,}"
    elif isinstance(value, float):
        if math.isnan(value):
            text = ""
        else:
            text = f"{value:.{decimals if decimals is not None else default_decimals}f}"
    elif value is None:
        text = ""
    else:
        text = str(value)
    text = f"{text}{stars}"
    return f"({text})" if parentheses and text else text


def raw_value(cell: Any) -> Any:
    if isinstance(cell, dict):
        return cell.get("value")
    return cell


def latex_escape(text: Any) -> str:
    value = str(text or "")
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def safe_tex_label(spec: dict[str, Any]) -> str:
    explicit = spec.get("tex_label")
    if explicit:
        return str(explicit)
    slug = re.sub(r"[^a-z0-9]+", "-", str(spec.get("title", "table")).lower()).strip("-")
    return f"tab:{slug or 'table'}"


def split_logical_rows(rows: list[dict[str, Any]], limit: int) -> list[list[dict[str, Any]]]:
    units: list[list[dict[str, Any]]] = []
    index = 0
    while index < len(rows):
        row = rows[index]
        if row.get("kind") == "coefficient" and index + 1 < len(rows):
            nxt = rows[index + 1]
            if nxt.get("kind") == "statistic" and nxt.get("pair_id") == row.get("pair_id"):
                units.append([row, nxt])
                index += 2
                continue
        units.append([row])
        index += 1
    pages: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for unit in units:
        if current and len(current) + len(unit) > limit:
            pages.append(current)
            current = []
        current.extend(unit)
    if current:
        pages.append(current)
    return pages or [[]]


def contiguous_groups(columns: Iterable[dict[str, Any]]) -> list[tuple[str, int]]:
    groups: list[tuple[str, int]] = []
    for column in columns:
        group = str(column.get("group", ""))
        if groups and groups[-1][0] == group:
            groups[-1] = (group, groups[-1][1] + 1)
        else:
            groups.append((group, 1))
    return groups
