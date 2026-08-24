#!/usr/bin/env python3
"""Import a long-format regression export into the canonical table schema.

The importer is deliberately conservative: it preserves input order, rejects
duplicate specification/outcome/term cells, and never invents missing results.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


ALIASES = {
    "outcome": ["outcome", "depvar", "dependent_variable", "因变量", "被解释变量", "因变量名称"],
    "spec": ["spec", "model", "specification", "规格", "模型", "样本", "控制变量组"],
    "term": ["term", "variable", "var", "coefficient_name", "变量", "变量名", "系数变量"],
    "coef": ["coef", "coefficient", "estimate", "b", "系数", "估计系数", "估计值"],
    "se": ["se", "std_error", "standard_error", "stderr", "标准误", "标准误差"],
    "t": ["t", "t_stat", "t_statistic", "t值", "t统计量"],
    "z": ["z", "z_stat", "z_statistic", "z值", "z统计量"],
    "p": ["p", "p_value", "pvalue", "p值", "显著性"],
    "stars": ["stars", "star", "significance_stars", "显著性星号"],
    "n": ["n", "N", "observations", "obs", "sample_size", "观测值", "样本量"],
    "unit_count": ["unit_count", "unit_n", "units", "firms", "counties", "县数", "企业数", "个体数", "单位数"],
    "defined_unit_count": ["defined_unit_count", "defined_unit_n", "defined_units", "定义样本单位数", "定义样本个体数"],
    "unit_fe": ["unit_fe", "firm_fe", "county_fe", "individual_fe", "unit_fixed_effects", "个体固定效应", "县固定效应"],
    "time_fe": ["time_fe", "year_fe", "time_fixed_effects", "year_fixed_effects", "年份固定效应", "时间固定效应"],
    "controls": ["controls", "control_variables", "control_set", "控制变量", "控制变量组"],
    "estimator": ["estimator", "method", "estimation_method", "估计方法", "估计量"],
    "cluster": ["cluster", "cluster_level", "clustering", "聚类层级", "聚类标准误"],
    "sample_stage": ["sample_stage", "stage", "样本阶段", "样本筛选阶段"],
    "sample_n": ["sample_n", "stage_n", "stage_count", "阶段样本量", "阶段观测值"],
}

SAMPLE_AUDIT_ALIASES = {
    "defined_sample_units": ["defined_sample_units", "defined_units", "定义样本单位数"],
    "outcome_nonmissing": ["outcome_nonmissing", "outcome_available", "因变量非缺失"],
    "treatment_merge_success": ["treatment_merge_success", "treatment_merge", "处理变量匹配成功"],
    "controls_merge_success": ["controls_merge_success", "controls_merge", "控制变量匹配成功"],
    "all_controls_nonmissing": ["all_controls_nonmissing", "controls_complete", "所有控制变量非缺失"],
    "final_sample": ["final_sample", "e_sample", "esample", "最终样本"],
}

PROFILE_DEFAULTS = {
    "chinese-journal": {"language": "zh", "decimals": 4, "title": "回归结果"},
    "english-paper": {"language": "en", "decimals": 3, "title": "Regression Results"},
    "compact-report": {"language": "en", "decimals": 4, "title": "Compact Results"},
}


def normalise_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", str(value).strip().lower())


def find_column(columns: list[str], aliases: list[str], explicit: str | None = None) -> str | None:
    if explicit:
        if explicit not in columns:
            raise ValueError(f"requested column not found: {explicit}")
        return explicit
    normalised = {normalise_name(column): column for column in columns}
    for alias in aliases:
        match = normalised.get(normalise_name(alias))
        if match:
            return match
    return None


def read_input(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("pandas is required; run this script with the Anaconda codex environment") from exc
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return pd.read_csv(path, encoding=encoding, keep_default_na=True)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise ValueError(f"could not decode CSV {path}: {last_error}")


def missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        import pandas as pd
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def as_text(value: Any, default: str = "") -> str:
    return default if missing(value) else str(value).strip()


def as_number(value: Any) -> float | int | None:
    if missing(value) or as_text(value) == "":
        return None
    if isinstance(value, bool):
        return value
    try:
        number = float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", str(value))
        if not match:
            return None
        number = float(match.group(0))
    if not math.isfinite(number):
        return None
    return int(number) if number.is_integer() else number


def extract_stars(value: Any) -> str:
    if missing(value):
        return ""
    text = str(value)
    return "".join(ch for ch in text if ch == "*")


def p_to_stars(value: Any, thresholds: dict[str, float]) -> str:
    p_value = as_number(value)
    if p_value is None:
        return ""
    ordered = sorted(thresholds.items(), key=lambda item: item[1])
    for marker, cutoff in ordered:
        if p_value <= cutoff:
            return marker
    return ""


def python_value(value: Any) -> Any:
    if missing(value):
        return None
    if isinstance(value, bool):
        return value
    number = as_number(value)
    if number is not None and isinstance(value, str) and re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value.strip()):
        return number
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            pass
    return value


def order_values(values: list[str], requested: str | None) -> list[str]:
    if not requested:
        return values
    wanted = [item.strip() for item in requested.split(",") if item.strip()]
    remainder = [value for value in values if value not in wanted]
    return [value for value in wanted if value in values] + remainder


def cell(value: Any, decimals: int, *, stars: str = "", parentheses: bool = False) -> Any:
    typed = python_value(value)
    if typed is None:
        return None
    result: dict[str, Any] = {"value": typed, "decimals": decimals}
    if stars:
        result["stars"] = stars
    if parentheses:
        result["parentheses"] = True
    return result


def label_for(key: str, language: str) -> str:
    labels = {
        "n": ("样本量" if language == "zh" else "Observations"),
        "unit_count": ("样本单位数" if language == "zh" else "Sample units"),
        "defined_unit_count": ("定义样本单位数" if language == "zh" else "Defined sample units"),
        "unit_fe": ("个体固定效应" if language == "zh" else "Unit FE"),
        "time_fe": ("时间固定效应" if language == "zh" else "Time FE"),
        "controls": ("控制变量" if language == "zh" else "Controls"),
        "estimator": ("估计方法" if language == "zh" else "Estimator"),
        "cluster": ("聚类层级" if language == "zh" else "Clustering level"),
        "sample_stage": ("样本阶段" if language == "zh" else "Sample stage"),
        "sample_n": ("阶段样本量" if language == "zh" else "Stage observations"),
    }
    return labels[key]


def make_notes(language: str, statistic_type: str, cluster: str, user_notes: list[str]) -> list[str]:
    if language == "zh":
        statistic_label = {"standard_error": "标准误", "t_statistic": "t统计量", "z_statistic": "z统计量"}[statistic_type]
        notes = [f"括号内为{statistic_label}，标准误按{cluster}层级聚类。", "*、**和***分别表示在10%、5%和1%的水平上显著。"]
    else:
        statistic_label = {"standard_error": "standard errors", "t_statistic": "t-statistics", "z_statistic": "z-statistics"}[statistic_type]
        notes = [f"{statistic_label.capitalize()} are in parentheses; standard errors are clustered by {cluster}.", "*, **, and *** denote significance at the 10%, 5%, and 1% levels, respectively."]
    return notes + user_notes


def import_spec(args: argparse.Namespace) -> dict[str, Any]:
    frame = read_input(Path(args.input))
    columns = [str(column) for column in frame.columns]
    selected: dict[str, str | None] = {}
    for key, aliases in ALIASES.items():
        selected[key] = find_column(columns, aliases, getattr(args, f"{key}_column", None))
    for key, aliases in SAMPLE_AUDIT_ALIASES.items():
        selected[key] = find_column(columns, aliases, None)

    coef_column = selected["coef"]
    if not coef_column:
        raise ValueError("no coefficient column found; expected coef/coefficient/estimate/系数")
    statistic_type = args.statistic_type
    if args.statistic_column:
        statistic_column = find_column(columns, ALIASES["se"] + ALIASES["t"] + ALIASES["z"], args.statistic_column)
    else:
        statistic_column = {"standard_error": selected["se"], "t_statistic": selected["t"], "z_statistic": selected["z"]}[statistic_type]
    if statistic_type == "standard_error" and not statistic_column:
        statistic_type = "t_statistic" if selected["t"] else "z_statistic" if selected["z"] else "standard_error"
        statistic_column = selected["t"] or selected["z"]
    if not statistic_column:
        raise ValueError("no inference column found; expected se/t/z or an explicit --statistic-column")

    profile = PROFILE_DEFAULTS[args.profile]
    language = args.language or profile["language"]
    decimals = args.decimals if args.decimals is not None else profile["decimals"]
    outcome_column = selected["outcome"]
    spec_column = selected["spec"]
    term_column = selected["term"]
    outcomes = [as_text(value, "Outcome") for value in (frame[outcome_column].drop_duplicates().tolist() if outcome_column else ["Outcome"])]
    specifications = [as_text(value, "Specification") for value in (frame[spec_column].drop_duplicates().tolist() if spec_column else ["Specification"])]
    outcomes = order_values(outcomes, args.outcome_order)
    specifications = order_values(specifications, args.spec_order)

    records: dict[tuple[str, str, str], dict[str, Any]] = {}
    duplicate_keys: list[tuple[str, str, str]] = []
    for _, row in frame.iterrows():
        outcome = as_text(row[outcome_column], "Outcome") if outcome_column else "Outcome"
        specification = as_text(row[spec_column], "Specification") if spec_column else "Specification"
        term = as_text(row[term_column], args.default_term) if term_column else args.default_term
        key = (specification, outcome, term)
        if key in records:
            duplicate_keys.append(key)
            continue
        raw_coef = row[coef_column]
        explicit_stars = extract_stars(row[selected["stars"]]) if selected["stars"] else extract_stars(raw_coef)
        records[key] = {
            "row": row,
            "coef": as_number(raw_coef),
            "stars": explicit_stars or p_to_stars(row[selected["p"]], args.significance) if selected["p"] else explicit_stars,
            "stat": as_number(row[statistic_column]),
        }
    if duplicate_keys:
        shown = ", ".join("/".join(item) for item in duplicate_keys[:5])
        raise ValueError(f"duplicate specification/outcome/term cells detected ({shown}); aggregate or disambiguate the CSV first")

    column_records: list[tuple[str, str, str]] = []
    for outcome in outcomes:
        for specification in specifications:
            if any(key[:2] == (specification, outcome) for key in records):
                column_records.append((specification, outcome, f"m{len(column_records) + 1}"))
    table_columns = []
    for index, (specification, outcome, key) in enumerate(column_records, 1):
        model = as_text(next((records[(specification, outcome, term)]["row"].get(selected["model"]) for term in records if term[:2] == (specification, outcome) and selected["model"]), ""), "") if selected.get("model") else ""
        table_columns.append({"key": key, "model": model or f"({index}) {specification}", "label": outcome, "group": outcome})

    terms: list[str] = []
    for key in records:
        if key[2] not in terms:
            terms.append(key[2])
    rows: list[dict[str, Any]] = []
    for term in terms:
        pair_id = f"coef-{len(rows) + 1}"
        coefficient_values: dict[str, Any] = {}
        statistic_values: dict[str, Any] = {}
        for specification, outcome, column_key in column_records:
            record = records.get((specification, outcome, term))
            if record:
                coefficient_values[column_key] = cell(record["coef"], decimals, stars=record["stars"])
                statistic_values[column_key] = cell(record["stat"], decimals, parentheses=True)
        rows.append({"kind": "coefficient", "label": term, "pair_id": pair_id, "values": coefficient_values})
        rows.append({"kind": "statistic", "label": "", "pair_id": pair_id, "values": statistic_values})

    metadata_keys = ["controls", "unit_fe", "time_fe", "estimator", "cluster", "n", "unit_count", "defined_unit_count", "sample_stage", "sample_n"] + list(SAMPLE_AUDIT_ALIASES)
    for metadata_key in metadata_keys:
        source_column = selected.get(metadata_key)
        if not source_column:
            continue
        values: dict[str, Any] = {}
        for specification, outcome, column_key in column_records:
            source_rows = frame[(frame[spec_column].map(lambda value: as_text(value, "Specification")) == specification) & (frame[outcome_column].map(lambda value: as_text(value, "Outcome")) == outcome)] if spec_column and outcome_column else frame
            value = source_rows.iloc[0][source_column] if not source_rows.empty else None
            count_key = metadata_key in {"n", "unit_count", "defined_unit_count", "sample_n", "defined_sample_units", "outcome_nonmissing", "treatment_merge_success", "controls_merge_success", "all_controls_nonmissing", "final_sample"}
            values[column_key] = cell(value, 0 if count_key else decimals)
        if any(value is not None for value in values.values()):
            label_key = metadata_key if metadata_key in ALIASES else "defined_unit_count" if metadata_key == "defined_sample_units" else metadata_key
            label = label_for(label_key, language) if label_key in {key for key in ALIASES if key in {"n", "unit_count", "defined_unit_count", "unit_fe", "time_fe", "controls", "estimator", "cluster", "sample_stage", "sample_n"}} else metadata_key.replace("_", " ").title()
            rows.append({"kind": "metadata", "label": label, "values": values})

    cluster = args.cluster or next((as_text(records[key]["row"][selected["cluster"]]) for key in records if selected["cluster"] and not missing(records[key]["row"][selected["cluster"]])), None)
    if not cluster:
        raise ValueError("clustering level is ambiguous; supply --cluster or include a cluster column")
    notes = make_notes(language, statistic_type, cluster, args.notes)
    integrity_warnings: list[str] = []
    for term in terms:
        signs = {1 if records[key]["coef"] > 0 else -1 for key in records if key[2] == term and records[key]["coef"] not in (None, 0)}
        if len(signs) > 1:
            integrity_warnings.append(f"coefficient sign changes across specifications for {term}; verify the specification comparison")
    n_values = [as_number(records[key]["row"][selected["n"]]) for key in records if selected["n"] and as_number(records[key]["row"][selected["n"]]) is not None]
    if n_values and len(set(n_values)) > 1:
        integrity_warnings.append("observations change across specifications; disclose denominator or sample restrictions")
    for metadata_key in ("unit_fe", "time_fe", "controls", "estimator", "cluster"):
        source_column = selected.get(metadata_key)
        if source_column:
            values = {as_text(row[source_column]) for _, row in frame.iterrows() if not missing(row[source_column])}
            if len(values) > 1:
                integrity_warnings.append(f"{metadata_key} varies across specifications; label the design change explicitly")
    if integrity_warnings:
        notes.append(("检测到规格间存在需要核查的变化：" if language == "zh" else "Specification-review flags are recorded in the audit metadata; verify them before publication."))

    spec: dict[str, Any] = {
        "version": 1,
        "table_type": args.table_type,
        "language": language,
        "profile": args.profile,
        "label": args.label,
        "title": args.title or profile["title"],
        "columns": table_columns,
        "rows": rows,
        "inference": {"statistic_type": statistic_type, "cluster": cluster, "significance": args.significance},
        "notes": notes,
        "source": "Imported from a long-format CSV with pandas.",
    }
    if args.mode:
        spec["mode"] = args.mode
    if args.purpose:
        spec["purpose"] = args.purpose
    if args.expected_result:
        spec["expected_result"] = args.expected_result
    if integrity_warnings:
        spec["integrity_warnings"] = integrity_warnings
    return spec


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a long-format regression CSV into the canonical table specification.")
    parser.add_argument("input")
    parser.add_argument("--output", required=True)
    parser.add_argument("--table-type", choices=("regression", "robustness"), default="regression")
    parser.add_argument("--profile", choices=tuple(PROFILE_DEFAULTS), default="english-paper")
    parser.add_argument("--language", choices=("en", "zh"))
    parser.add_argument("--label", default="Table 1")
    parser.add_argument("--title")
    parser.add_argument("--mode", choices=("publication", "working-shell"))
    parser.add_argument("--purpose")
    parser.add_argument("--expected-result")
    parser.add_argument("--decimals", type=int)
    parser.add_argument("--default-term", default="Treatment")
    parser.add_argument("--outcome-order")
    parser.add_argument("--spec-order")
    parser.add_argument("--cluster")
    parser.add_argument("--statistic-type", choices=("standard_error", "t_statistic", "z_statistic"), default="standard_error")
    parser.add_argument("--statistic-column")
    parser.add_argument("--notes", action="append", default=[])
    parser.add_argument("--force", action="store_true")
    for key in ("outcome", "spec", "term", "coef", "se", "t", "z", "p", "stars", "n"):
        parser.add_argument(f"--{key}-column")
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists() and not args.force:
        print(f"ERROR: output exists: {output}; use --force to replace", file=sys.stderr)
        return 2
    try:
        thresholds = {"*": 0.10, "**": 0.05, "***": 0.01}
        args.significance = thresholds
        spec = import_spec(args)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: wrote {output}")
    if spec.get("integrity_warnings"):
        for warning in spec["integrity_warnings"]:
            print(f"WARNING: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
