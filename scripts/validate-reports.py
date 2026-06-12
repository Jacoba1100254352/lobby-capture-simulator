#!/usr/bin/env python3
"""Compare report metrics against empirical benchmark plausibility ranges."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


BENCHMARKS = Path("data/calibration/empirical-benchmarks.csv")
PARAMETER_MAP = Path("data/calibration/parameter-map.csv")
REPORTS = Path("reports")
SOURCE_MOMENTS = Path("reports/source-moments.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks", type=Path, default=BENCHMARKS)
    parser.add_argument("--parameter-map", type=Path, default=PARAMETER_MAP)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--source-moments", type=Path, default=SOURCE_MOMENTS)
    parser.add_argument("--output", type=Path, default=REPORTS)
    args = parser.parse_args()

    benchmarks = read_benchmarks(args.benchmarks)
    if args.parameter_map.exists():
        benchmarks.extend(read_parameter_map(args.parameter_map))
    source_moments = read_source_moments(args.source_moments)
    source_metrics = set(source_moments)
    source_benchmarks = [benchmark for benchmark in benchmarks if benchmark["metric"] in source_metrics]
    report_benchmarks = [benchmark for benchmark in benchmarks if benchmark["metric"] not in source_metrics]
    report_paths = sorted(args.reports.glob("lobby-capture-*.csv"))
    report_paths = [path for path in report_paths if path.name != "validation-summary.csv"]
    if not report_paths:
        raise SystemExit(f"No report CSVs found in {args.reports}. Run make campaign first.")

    rows = []
    for report in report_paths:
        rows.extend(validate_report(report, report_benchmarks))
    rows.extend(validate_source_moments(args.source_moments, source_benchmarks, source_moments))
    substitution_rows = audit_substitution_warnings(report_paths)
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "validation-summary.csv", rows)
    write_markdown(args.output / "validation-summary.md", rows)
    write_substitution_csv(args.output / "substitution-audit.csv", substitution_rows)
    write_substitution_markdown(args.output / "substitution-audit.md", substitution_rows)
    print(f"Wrote {args.output / 'validation-summary.csv'}")
    print(f"Wrote {args.output / 'validation-summary.md'}")
    print(f"Wrote {args.output / 'substitution-audit.csv'}")
    print(f"Wrote {args.output / 'substitution-audit.md'}")
    return 0


def read_benchmarks(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = []
        for row in csv.DictReader(source):
            row.setdefault("evidenceType", "benchmark")
            row.setdefault("targetKind", "report_metric")
            rows.append(row)
        return rows


def read_parameter_map(path: Path) -> list[dict[str, str]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if row.get("implementationStatus") == "planned":
                continue
            rows.append(
                {
                    "key": "parameter-map:" + row["parameter"],
                    "source": row["sourceReport"],
                    "observable": row["modelTarget"],
                    "metric": row["modelMetric"],
                    "min": row["low"],
                    "max": row["high"],
                    "notes": row["notes"],
                    "evidenceType": row["evidenceType"],
                    "targetKind": row["implementationStatus"],
                }
            )
    return rows


def validate_report(report: Path, benchmarks: list[dict[str, str]]) -> list[dict[str, str]]:
    with report.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        return []
    output = []
    for benchmark in benchmarks:
        metric = benchmark["metric"]
        if metric not in rows[0]:
            output.append(summary_row(report, benchmark, "", "", "unknown", "metric not present in report"))
            continue
        scoped_rows, scope = benchmark_scope(rows, benchmark)
        if not scoped_rows:
            output.append(summary_row(
                report,
                benchmark,
                "",
                "",
                "not_applicable",
                f"no rows matched validation scope; scope={scope}; rows=0",
                scope,
                "0",
            ))
            continue
        values = [float(row[metric]) for row in scoped_rows if row.get(metric, "") != ""]
        if not values:
            output.append(summary_row(report, benchmark, "", "", "unknown", f"metric has no values in {scope}"))
            continue
        observed_min = min(values)
        observed_max = max(values)
        benchmark_min = float(benchmark["min"])
        benchmark_max = float(benchmark["max"])
        if observed_min >= benchmark_min and observed_max <= benchmark_max:
            status = "fit"
            note = "all scenario values inside benchmark range"
        elif observed_max >= benchmark_min and observed_min <= benchmark_max:
            status = "partial"
            note = "some scenario values overlap benchmark range"
        else:
            status = "miss"
            note = "scenario range outside benchmark range"
        output.append(summary_row(
            report,
            benchmark,
            f4(observed_min),
            f4(observed_max),
            status,
            f"{note}; scope={scope}; rows={len(scoped_rows)}",
            scope,
            str(len(scoped_rows)),
        ))
    return output


def benchmark_scope(rows: list[dict[str, str]], benchmark: dict[str, str]) -> tuple[list[dict[str, str]], str]:
    key = normalized_benchmark_key(benchmark)
    metric_name = benchmark.get("metric", "")
    if key == "public_financing_candidate_uptake":
        return filter_rows(rows, lambda row: metric(row, "publicFinancingShare") >= 0.45), "public-financing scenarios"
    if key == "voucher_participation":
        return filter_rows(rows, lambda row: metric(row, "voucherParticipation") >= 0.45), "voucher scenarios"
    if key == "super_pac_large_donor_dependence":
        return filter_rows(rows, campaign_finance_scope), "campaign-finance and outside-spending scenarios"
    if key == "dark_money_super_pac_routing":
        return filter_rows(rows, opaque_electoral_routing_scope), "opaque electoral-routing stress scenarios"
    if key == "shadow_lobbying_share":
        return filter_rows(rows, shadow_lobbying_scope), "shadow-lobbying stress scenarios"
    if key == "cooling_off_shadow_lobbying":
        return filter_rows(rows, cooling_or_venue_scope), "cooling-off and venue-shift scenarios"
    if metric_name in {"procurementNetworkExposure", "procurementBias"}:
        return filter_rows(rows, procurement_scope), "procurement scenarios"
    return rows, "all scenarios"


def normalized_benchmark_key(benchmark: dict[str, str]) -> str:
    key = benchmark.get("key", "")
    return key.split(":", 1)[1] if key.startswith("parameter-map:") else key


def filter_rows(rows: list[dict[str, str]], predicate) -> list[dict[str, str]]:
    return [row for row in rows if predicate(row)]


def campaign_finance_scope(row: dict[str, str]) -> bool:
    text = row_text(row)
    markers = ("campaign-finance", "campaign finance", "dark-money", "dark money", "outside", "super pac", "super-pac")
    marked = any(marker in text for marker in markers)
    money_heavy = metric(row, "campaignFinanceShare") + metric(row, "darkMoneyShare") >= 0.30
    public_financing_counterweight = (
        metric(row, "publicFinancingShare") >= 0.45
        or metric(row, "voucherParticipation") >= 0.45
        or metric(row, "participationProtectionIndex") >= 0.65
    )
    return marked or (money_heavy and not public_financing_counterweight)


def opaque_electoral_routing_scope(row: dict[str, str]) -> bool:
    text = row_text(row)
    markers = (
        "dark-money",
        "dark money",
        "outside-spending",
        "outside spending",
        "super pac",
        "super-pac",
        "visible-ban",
        "visible lobbying ban",
        "leakage",
        "public-finance dark-money",
        "maximum dark-money",
        "nonprofit issue-ad",
        "independent expenditure",
    )
    return any(marker in text for marker in markers)


def shadow_lobbying_scope(row: dict[str, str]) -> bool:
    text = row_text(row)
    markers = ("shadow", "hard-budget", "advisory", "venue", "bundle-with-evasion", "intermediary", "outside")
    return any(marker in text for marker in markers) or metric(row, "hiddenInfluenceShare") >= 0.30


def cooling_or_venue_scope(row: dict[str, str]) -> bool:
    text = row_text(row)
    markers = ("cooling", "revolving", "door", "advisory", "venue", "procurement-venue", "hard-budget")
    return any(marker in text for marker in markers) or metric(row, "venueSubstitutionRate") >= 0.10


def procurement_scope(row: dict[str, str]) -> bool:
    text = row_text(row)
    return "procurement" in text or metric(row, "procurementNetworkExposure") >= 0.10


def row_text(row: dict[str, str]) -> str:
    return " ".join([row.get("scenarioKey", ""), row.get("scenarioName", "")]).lower()


def read_source_moments(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {
            row["metric"]: float(row["value"])
            for row in csv.DictReader(source)
            if row.get("scope") == "snapshot" and row.get("metric") and row.get("value")
        }


def validate_source_moments(
        source_path: Path,
        benchmarks: list[dict[str, str]],
        source_moments: dict[str, float],
) -> list[dict[str, str]]:
    output = []
    for benchmark in benchmarks:
        metric = benchmark["metric"]
        if metric not in source_moments:
            output.append(summary_row(source_path, benchmark, "", "", "unknown", "source moment not present"))
            continue
        value = source_moments[metric]
        benchmark_min = float(benchmark["min"])
        benchmark_max = float(benchmark["max"])
        if benchmark_min <= value <= benchmark_max:
            status = "fit"
            note = "source moment inside benchmark range"
        else:
            gap_note = source_scope_gap(metric, value, source_moments)
            if gap_note:
                status = "source_gap"
                note = f"{gap_note}; source moment outside benchmark range"
            else:
                status = "miss"
                note = "source moment outside benchmark range"
        source_benchmark = dict(benchmark)
        source_benchmark["targetKind"] = "source_moment"
        output.append(summary_row(source_path, source_benchmark, f4(value), f4(value), status, note))
    return output


def source_scope_gap(metric: str, value: float, source_moments: dict[str, float]) -> str:
    """Return a source-coverage note when the panel cannot test the benchmark."""
    procurement_rows = source_moments.get("procurementRows", 0.0)
    procurement_bridge_rows = source_moments.get("procurementBridgeRows", 0.0)
    procurement_action_rows = source_moments.get("procurementActionRows", 0.0)
    procurement_bridge_agencies = source_moments.get("procurementBridgeAgencyCount", 0.0)
    top_award_bridge = source_moments.get("procurementBridgeTopAwardSample", 0.0) >= 0.5
    latest_transaction_mod_proxy = source_moments.get("procurementLatestTransactionModificationProxy", 0.0) >= 0.5
    single_agency_panel = (
        procurement_rows > 0
        and procurement_bridge_rows <= 0
        and source_moments.get("procurementAgencyTop1Share", 0.0) >= 0.98
    )
    initial_award_panel = (
        procurement_rows > 0
        and procurement_action_rows <= 0
        and source_moments.get("procurementInitialAwardShare", 0.0) >= 0.95
    )
    thin_dark_money_panel = source_moments.get("darkMoneySourceShare", 0.0) < 0.05
    if metric == "procurementAgencyTop1Share" and single_agency_panel:
        return "single-agency procurement snapshot cannot validate a multi-agency agency-concentration benchmark"
    if metric == "procurementAgencyTop1Share" and top_award_bridge and procurement_bridge_agencies > 1:
        return "multi-agency procurement bridge is present but top-award sampling is not representative enough for agency-concentration calibration"
    if metric == "procurementRecipientTop3Share" and single_agency_panel:
        return "single-agency procurement snapshot cannot validate a cross-agency recipient-concentration benchmark"
    if metric == "procurementSingleBidShare" and top_award_bridge:
        return "competition moments come from a limited top-award procurement slice, not representative SAM/FPDS action-level competition coverage"
    if metric == "procurementExPostModificationShare" and initial_award_panel and value <= 0.0:
        return "award-level procurement snapshot is dominated by initial awards; action-level FPDS/SAM modification transactions are needed"
    if metric == "procurementExPostModificationShare" and latest_transaction_mod_proxy and procurement_action_rows <= 0:
        return "latest-transaction modification enrichment is kept separate from action-level incidence; representative FPDS/SAM transaction denominators are still needed"
    if metric == "procurementExPostModificationShare" and procurement_action_rows > 0 and value > 0.40:
        return "bounded USAspending transaction-action panel is present, but the modification-action share is outside the benchmark range and still needs representative SAM/FPDS validation"
    if metric == "darkMoneyDirectVisibility" and thin_dark_money_panel:
        return "dark-money source panel is thin and proxy-backed; direct hidden-donor or nonprofit-routing records are needed, while electioneering rows remain separate electoral-communication evidence"
    return ""


def audit_substitution_warnings(report_paths: list[Path]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for report in report_paths:
        with report.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        if not rows:
            continue
        baseline = baseline_row(rows)
        for row in rows:
            if row is baseline:
                status = "baseline"
            else:
                status = substitution_status(row, baseline)
            output.append(substitution_row(report, row, baseline, status))
    return output


def baseline_row(rows: list[dict[str, str]]) -> dict[str, str]:
    for row in rows:
        if row.get("scenarioKey") == "open-access-lobbying":
            return row
    return max(rows, key=lambda row: metric(row, "visibleLobbyingSpendShare"))


def substitution_status(row: dict[str, str], baseline: dict[str, str]) -> str:
    capture_delta = metric(row, "observedCaptureRate") - metric(baseline, "observedCaptureRate")
    hidden_delta = metric(row, "hiddenInfluenceShare") - metric(baseline, "hiddenInfluenceShare")
    hidden_capture_delta = metric(row, "hiddenCaptureIndex") - metric(baseline, "hiddenCaptureIndex")
    distortion_delta = metric(row, "totalInfluenceDistortion") - metric(baseline, "totalInfluenceDistortion")
    risk_delta = metric(row, "substitutionRisk") - metric(baseline, "substitutionRisk")
    visible_delta = metric(row, "visibleLobbyingSpendShare") - metric(baseline, "visibleLobbyingSpendShare")
    network_delta = metric(row, "networkOpacityIndex") - metric(baseline, "networkOpacityIndex")
    venue_shift_delta = metric(row, "venueShiftNetworkLoad") - metric(baseline, "venueShiftNetworkLoad")
    channel_movement_delta = max(
        metric(row, "intermediaryCentrality") - metric(baseline, "intermediaryCentrality"),
        metric(row, "procurementNetworkExposure") - metric(baseline, "procurementNetworkExposure"),
        metric(row, "revolvingDoorBridgeIndex") - metric(baseline, "revolvingDoorBridgeIndex"),
        metric(row, "commentNetworkLoad") - metric(baseline, "commentNetworkLoad"),
    )
    observed_improvement = capture_delta < -0.02
    visible_suppression = visible_delta < -0.02
    hidden_worsening = any_moved(hidden_delta, hidden_capture_delta, risk_delta)
    channel_shift = any_moved(
        network_delta,
        venue_shift_delta,
        channel_movement_delta,
    )
    if observed_improvement and distortion_delta > 0.02:
        return "distortion_failure"
    if distortion_delta > 0.02:
        return "worse_total_distortion"
    if observed_improvement and hidden_worsening:
        return "substitution_warning"
    if observed_improvement and channel_shift:
        return "channel_shift_tradeoff"
    if visible_suppression and (hidden_worsening or channel_shift):
        return "visible_channel_warning"
    if capture_delta < -0.02 and distortion_delta <= 0.02 and risk_delta <= 0.02:
        return "improved"
    return "no_material_tradeoff"


def substitution_row(report: Path, row: dict[str, str], baseline: dict[str, str], status: str) -> dict[str, str]:
    capture_delta = metric(row, "observedCaptureRate") - metric(baseline, "observedCaptureRate")
    hidden_delta = metric(row, "hiddenInfluenceShare") - metric(baseline, "hiddenInfluenceShare")
    hidden_capture_delta = metric(row, "hiddenCaptureIndex") - metric(baseline, "hiddenCaptureIndex")
    distortion_delta = metric(row, "totalInfluenceDistortion") - metric(baseline, "totalInfluenceDistortion")
    risk_delta = metric(row, "substitutionRisk") - metric(baseline, "substitutionRisk")
    warning_score = max(0.0, -capture_delta) + max(0.0, hidden_delta) + max(0.0, hidden_capture_delta) + max(0.0, distortion_delta) + max(0.0, risk_delta)
    design_loss = metric(row, "designLoss") if row.get("designLoss") else (
        (0.30 * metric(row, "totalInfluenceDistortion"))
        + (0.20 * metric(row, "hiddenCaptureIndex"))
        + (0.16 * metric(row, "substitutionRisk"))
        + (0.10 * metric(row, "administrativeCost"))
        + (0.09 * metric(row, "networkOpacityIndex"))
        + (0.07 * metric(row, "legitimateAdvocacyChill"))
        + (0.06 * metric(row, "speechRestrictionRisk"))
        - (0.05 * metric(row, "crossVenueDetectionIndex"))
        - (0.03 * metric(row, "participationProtectionIndex"))
    )
    return {
        "report": report.name,
        "scenarioKey": row.get("scenarioKey", ""),
        "scenarioName": row.get("scenarioName", ""),
        "baselineScenarioKey": baseline.get("scenarioKey", ""),
        "status": status,
        "warningScore": f4(warning_score),
        "designLoss": f4(design_loss),
        "observedCaptureDelta": delta(row, baseline, "observedCaptureRate"),
        "hiddenInfluenceDelta": delta(row, baseline, "hiddenInfluenceShare"),
        "hiddenCaptureDelta": delta(row, baseline, "hiddenCaptureIndex"),
        "totalInfluenceDistortionDelta": delta(row, baseline, "totalInfluenceDistortion"),
        "substitutionRiskDelta": delta(row, baseline, "substitutionRisk"),
        "visibleLobbyingSpendShareDelta": delta(row, baseline, "visibleLobbyingSpendShare"),
        "networkOpacityDelta": delta(row, baseline, "networkOpacityIndex"),
        "venueShiftNetworkLoadDelta": delta(row, baseline, "venueShiftNetworkLoad"),
        "intermediaryCentralityDelta": delta(row, baseline, "intermediaryCentrality"),
        "procurementNetworkExposureDelta": delta(row, baseline, "procurementNetworkExposure"),
        "revolvingDoorBridgeDelta": delta(row, baseline, "revolvingDoorBridgeIndex"),
        "commentNetworkLoadDelta": delta(row, baseline, "commentNetworkLoad"),
        "intermediarySpendShare": f4(metric(row, "intermediaryShare")),
        "darkMoneySpendShare": f4(metric(row, "darkMoneyShare")),
        "defensiveReformSpendShare": f4(metric(row, "defensiveReformSpendShare")),
        "administrativeCost": f4(metric(row, "administrativeCost")),
    }


def delta(row: dict[str, str], baseline: dict[str, str], key: str) -> str:
    return f4(metric(row, key) - metric(baseline, key))


def metric(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "0") or "0")
    except ValueError:
        return 0.0


def any_moved(*deltas: float) -> bool:
    return any(delta > 0.02 for delta in deltas)


def summary_row(
        report: Path,
        benchmark: dict[str, str],
        observed_min: str,
        observed_max: str,
        status: str,
        validation_note: str,
        validation_scope: str = "all scenarios",
        validated_rows: str = "",
) -> dict[str, str]:
    return {
        "report": report.name,
        "benchmarkKey": benchmark["key"],
        "metric": benchmark["metric"],
        "observedMin": observed_min,
        "observedMax": observed_max,
        "benchmarkMin": benchmark["min"],
        "benchmarkMax": benchmark["max"],
        "status": status,
        "source": benchmark["source"],
        "observable": benchmark["observable"],
        "evidenceType": benchmark.get("evidenceType", "benchmark"),
        "targetKind": benchmark.get("targetKind", "report_metric"),
        "validationScope": validation_scope,
        "validatedRows": validated_rows,
        "notes": benchmark["notes"],
        "validationNote": validation_note,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "report",
        "benchmarkKey",
        "metric",
        "observedMin",
        "observedMax",
        "benchmarkMin",
        "benchmarkMax",
        "status",
        "source",
        "observable",
        "evidenceType",
        "targetKind",
        "validationScope",
        "validatedRows",
        "notes",
        "validationNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_substitution_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "report",
        "scenarioKey",
        "scenarioName",
        "baselineScenarioKey",
        "status",
        "warningScore",
        "designLoss",
        "observedCaptureDelta",
        "hiddenInfluenceDelta",
        "hiddenCaptureDelta",
        "totalInfluenceDistortionDelta",
        "substitutionRiskDelta",
        "visibleLobbyingSpendShareDelta",
        "networkOpacityDelta",
        "venueShiftNetworkLoadDelta",
        "intermediaryCentralityDelta",
        "procurementNetworkExposureDelta",
        "revolvingDoorBridgeDelta",
        "commentNetworkLoadDelta",
        "intermediarySpendShare",
        "darkMoneySpendShare",
        "defensiveReformSpendShare",
        "administrativeCost",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {
        status: sum(1 for row in rows if row["status"] == status)
        for status in ("fit", "partial", "miss", "source_gap", "unknown", "not_applicable")
    }
    lines = [
        "# Validation Summary",
        "",
        "Benchmark ranges are plausibility checks, not causal empirical claims. `source_gap` rows mark source panels that are too narrow or too proxy-backed to test a benchmark directly.",
        "",
        f"- Fit: `{counts['fit']}`",
        f"- Partial: `{counts['partial']}`",
        f"- Miss: `{counts['miss']}`",
        f"- Source gap: `{counts['source_gap']}`",
        f"- Unknown: `{counts['unknown']}`",
        f"- Not applicable: `{counts['not_applicable']}`",
        "",
        "## Evidence Classes",
        "",
    ]
    for evidence_type in sorted({row["evidenceType"] for row in rows}):
        evidence_rows = [row for row in rows if row["evidenceType"] == evidence_type]
        fit = sum(1 for row in evidence_rows if row["status"] == "fit")
        partial = sum(1 for row in evidence_rows if row["status"] == "partial")
        miss = sum(1 for row in evidence_rows if row["status"] == "miss")
        source_gap = sum(1 for row in evidence_rows if row["status"] == "source_gap")
        unknown = sum(1 for row in evidence_rows if row["status"] == "unknown")
        not_applicable = sum(1 for row in evidence_rows if row["status"] == "not_applicable")
        lines.append(
            f"- `{evidence_type}`: fit `{fit}`, partial `{partial}`, miss `{miss}`, "
            f"source gap `{source_gap}`, unknown `{unknown}`, not applicable `{not_applicable}`"
        )
    lines.extend([
        "",
        "| Report | Metric | Observed | Benchmark | Status | Note |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ])
    for row in rows:
        observed = range_label(row["observedMin"], row["observedMax"])
        benchmark = range_label(row["benchmarkMin"], row["benchmarkMax"])
        lines.append(
            f"| {row['report']} | {row['metric']} | {observed} | {benchmark} | {row['status']} | {row['validationNote']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_substitution_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {
        status: sum(1 for row in rows if row["status"] == status)
        for status in (
            "distortion_failure",
            "worse_total_distortion",
            "hidden_capture_warning",
            "hidden_influence_warning",
            "substitution_warning",
            "visible_channel_warning",
            "channel_shift_tradeoff",
            "improved",
            "no_material_tradeoff",
            "baseline",
        )
    }
    lines = [
        "# Substitution Audit",
        "",
        "This audit treats lower observed capture as insufficient when hidden influence, hidden capture, total distortion, or substitution risk rises. It distinguishes total-distortion failures from hidden-influence warnings and channel-shift tradeoffs, so reforms are not called failures merely because one hidden metric rises while total modeled distortion falls. It is a diagnostic over synthetic simulation reports, not an empirical causal claim.",
        "",
        f"- Distortion failure: `{counts['distortion_failure']}`",
        f"- Worse total distortion: `{counts['worse_total_distortion']}`",
        f"- Hidden-capture warning: `{counts['hidden_capture_warning']}`",
        f"- Hidden-influence warning: `{counts['hidden_influence_warning']}`",
        f"- Substitution warning: `{counts['substitution_warning']}`",
        f"- Visible-channel warning: `{counts['visible_channel_warning']}`",
        f"- Channel-shift tradeoff: `{counts['channel_shift_tradeoff']}`",
        f"- Improved: `{counts['improved']}`",
        f"- No material tradeoff: `{counts['no_material_tradeoff']}`",
        f"- Baseline rows: `{counts['baseline']}`",
        "",
        "## Flagged Rows",
        "",
        "| Report | Scenario | Status | Warning score | Design loss | Capture delta | Hidden delta | Hidden capture delta | Total distortion delta | Risk delta | Visible spend delta | Network opacity delta | Venue delta | Interm. load delta | Procurement delta | Revolving delta | Comment delta | Intermediary | Dark money | Defensive | Admin |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    flagged = [
        row for row in rows
        if row["status"] in {
            "distortion_failure",
            "worse_total_distortion",
            "hidden_capture_warning",
            "hidden_influence_warning",
            "substitution_warning",
            "visible_channel_warning",
            "channel_shift_tradeoff",
        }
    ]
    for row in flagged:
        lines.append(
            f"| {row['report']} | {row['scenarioName']} | {row['status']} | "
            f"{row['warningScore']} | {row['designLoss']} | "
            f"{row['observedCaptureDelta']} | {row['hiddenInfluenceDelta']} | "
            f"{row['hiddenCaptureDelta']} | {row['totalInfluenceDistortionDelta']} | "
            f"{row['substitutionRiskDelta']} | {row['visibleLobbyingSpendShareDelta']} | "
            f"{row['networkOpacityDelta']} | {row['venueShiftNetworkLoadDelta']} | "
            f"{row['intermediaryCentralityDelta']} | {row['procurementNetworkExposureDelta']} | "
            f"{row['revolvingDoorBridgeDelta']} | {row['commentNetworkLoadDelta']} | "
            f"{row['intermediarySpendShare']} | {row['darkMoneySpendShare']} | "
            f"{row['defensiveReformSpendShare']} | {row['administrativeCost']} |"
        )
    if not flagged:
        lines.append("| n/a | n/a | no flagged rows |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def range_label(low: str, high: str) -> str:
    if not low or not high:
        return "n/a"
    return f"{low}-{high}"


def f4(value: float) -> str:
    return f"{value:.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
