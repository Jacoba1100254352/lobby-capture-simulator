#!/usr/bin/env python3
"""Audit paired source availability and a legacy design alias, without estimating effects.

The caller validates the upstream source products before this cross-product join.
Presence in this audit is not a final LDA version, an actor spending total, a
continuous PAC affiliation, or a provision-specific treatment assignment.
"""

from collections import defaultdict
import csv
from datetime import date
from fractions import Fraction
import hashlib
import json


START_YEAR, END_YEAR = 2003, 2008
OUTCOMES = ("candidateContributionsDollars", "independentExpendituresDollars", "totalDisbursementsDollars")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows, fields, name):
    index = {tuple(r[k] for k in fields): r for r in rows}
    require(len(index) == len(rows), f"Duplicate {name} key")
    return index


def halfyear(year, half):
    return (f"{year}H{half}", f"{year}-{'01-01' if half == 1 else '07-01'}",
            f"{year}-{'06-30' if half == 1 else '12-31'}")


def source_availability(metadata, cohort, coverage, outcomes):
    """Keep every observed LDA candidate and every declared PAC period, including gaps."""
    unique(metadata, ("filingUuid",), "LDA filing")
    require(metadata, "Empty LDA source frame")
    actors = {}
    grouped = defaultdict(list)
    for row in metadata:
        actor = row["canonicalActorId"]
        require(actor not in actors or actors[actor] == row["primaryName"], "Conflicting LDA actor names")
        actors[actor] = row["primaryName"]
        if row["filingType"] in {"RR", "RA"}:
            continue
        start, end = date.fromisoformat(row["periodStart"]), date.fromisoformat(row["periodEnd"])
        h = 1 if start.month <= 6 else 2
        key, begin, finish = halfyear(start.year, h)
        require(START_YEAR <= start.year <= END_YEAR and begin <= start.isoformat() <= end.isoformat() <= finish,
                "LDA native period crosses the declared half-year frame")
        grouped[(actor, key)].append(row)
    by_actor = unique(cohort, ("canonicalActorId",), "PAC actor")
    unique(cohort, ("committeeId",), "PAC committee")
    require(all(r["canonicalActorId"] in actors and r["exposureGroup"] == "unassigned_design_candidate"
                and int(r["startYear"]) == START_YEAR and int(r["endYear"]) == END_YEAR for r in cohort),
            "PAC cohort outside source frame or exposure assigned")
    cov = unique(coverage, ("canonicalActorId", "committeeId", "halfYear"), "PAC coverage")
    obs = unique(outcomes, ("canonicalActorId", "committeeId", "halfYear"), "PAC outcome")
    expected = {(r["canonicalActorId"], r["committeeId"], halfyear(y, h)[0])
                for r in cohort for y in range(START_YEAR, END_YEAR + 1) for h in (1, 2)}
    require(set(cov) == expected, "PAC coverage must retain every declared period")
    require(set(obs) == {k for k, r in cov.items() if r["status"] == "observed_complete"},
            "PAC outcome/coverage mismatch; unresolved is not zero")
    result = []
    for actor, name in sorted(actors.items()):
        pac = by_actor.get((actor,))
        for year in range(START_YEAR, END_YEAR + 1):
            for half in (1, 2):
                key, begin, end = halfyear(year, half)
                rows = grouped[(actor, key)]
                periods = sorted({(r["periodStart"], r["periodEnd"]) for r in rows})
                expected_periods = ([(begin, end)] if year < 2008 else
                    [(f"{year}-01-01", f"{year}-03-31"), (f"{year}-04-01", f"{year}-06-30")]
                    if half == 1 else
                    [(f"{year}-07-01", f"{year}-09-30"), (f"{year}-10-01", f"{year}-12-31")])
                require(set(periods) <= set(expected_periods), "Unsupported LDA native reporting period")
                coverage_row = cov[(actor, pac["committeeId"], key)] if pac else None
                observed = obs.get((actor, pac["committeeId"], key)) if pac else None
                for source in (coverage_row, observed):
                    if source is not None:
                        require((source["periodStart"], source["periodEnd"]) == (begin, end),
                                "PAC period dates disagree with half-year key")
                if observed is not None:
                    require(observed["completeCoverage"] == "true"
                            and all(observed.get(k) not in ("", None) for k in OUTCOMES), "Incomplete PAC outcome row")
                result.append({
                    "canonicalActorId": actor, "actorName": name, "halfYear": key,
                    "periodStart": begin, "periodEnd": end,
                    "ldaActivityFilingCount": len(rows), "ldaNativePeriodsPresent": len(periods),
                    "ldaNativePeriodsExpected": len(expected_periods),
                    "ldaNativePeriodFootprint": "present" if periods == expected_periods else "partial_or_missing",
                    "ldaFilingUuids": ";".join(sorted(r["filingUuid"] for r in rows)),
                    "ldaExpenseRecords": sum(r["amountKind"] == "expenses" for r in rows),
                    "ldaIncomeRecords": sum(r["amountKind"] == "income" for r in rows),
                    "ldaExpenseMethodMissing": sum(r["amountKind"] == "expenses" and not r["expensesMethod"] for r in rows),
                    "ldaApiExpenseMethods": ";".join(sorted({r["expensesMethod"].upper() for r in rows
                                                              if r["amountKind"] == "expenses" and r["expensesMethod"]})),
                    "committeeId": pac["committeeId"] if pac else "",
                    "pacStatus": coverage_row["status"] if pac else "outside_pac_acquisition_cohort",
                    "pacReasonCodes": coverage_row["reasonCodes"] if pac else "not_acquired_in_this_cohort",
                    **{k: observed[k] if observed else "" for k in OUTCOMES},
                    "pacSourceRecordIds": observed["sourceRecordIds"] if observed else "",
                    "pairedSourcePresence": "true" if rows and observed else "false",
                    "provisionExposure": "not_established_by_source_presence",
                    "interpretation": "Source presence only; no LDA total, matched control or causal effect established.",
                })
    return result


def exact_rank(rows):
    matrix = [list(map(Fraction, r)) for r in sorted(set(map(tuple, rows)))]
    rank = 0
    for col in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][col]
        matrix[rank] = [v / scale for v in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            scale = matrix[i][col]
            matrix[i] = [v - scale * p for v, p in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank


def legacy_source_alias(panel):
    """Test an unrestricted federal-source post shock, not an observed shock or effect."""
    unique(panel, ("canonicalActorId", "quarter"), "legacy actor-quarter")
    rows = [r for r in panel if r["includedInPrimary"] == "yes"]
    require(rows, "Empty legacy primary panel")
    matrix = []
    for r in rows:
        require(r["treated"] in {"0", "1"} and r["prePostClass"] in {"clean_pre", "post"}
                and r["sourceSystem"] in {"Official LDA API", "Colorado Secretary of State lobbyist income data"},
                "Unknown legacy treatment, source or period")
        treated, post = int(r["treated"]), int(r["prePostClass"] == "post")
        federal = int(r["sourceSystem"] == "Official LDA API")
        matrix.append([1, treated, post, treated * post, federal * post])
    alias = all(r[3] == r[4] for r in matrix)
    return {"primaryObservations": len(rows),
            "actors": len({r["canonicalActorId"] for r in rows}),
            "preObservations": sum(r["prePostClass"] == "clean_pre" for r in rows),
            "postObservations": sum(r["prePostClass"] == "post" for r in rows),
            "columns": ["intercept", "treated", "post", "treated_post", "federal_source_post"],
            "exactRank": exact_rank(matrix), "columnCount": 5,
            "interactionColumnsIdentical": alias,
            "maxPredictionChangeForOppositeUnitCoefficientShifts": max(abs(r[3] - r[4]) for r in matrix),
            "causalEffect": "not_identified"}


def write_review(root, metadata, cohort, coverage, outcomes, legacy):
    rows = source_availability(metadata, cohort, coverage, outcomes)
    alias = legacy_source_alias(legacy)
    require(alias["interactionColumnsIdentical"],
            "Legacy comparison changed; reassess the source-alias conclusion before writing the report")
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    with (reports / "substitution-comparison-availability.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    totals = {"observedLdaActors": len({r["canonicalActorId"] for r in rows}),
              "actorHalfYears": len(rows), "ldaPeriodFootprintsPresent": sum(r["ldaNativePeriodFootprint"] == "present" for r in rows),
              "pacCohortActors": len(cohort), "expectedPacHalfYears": len(coverage),
              "observedPacHalfYears": len(outcomes),
              "unresolvedPacHalfYears": sum(r["status"] != "observed_complete" for r in coverage),
              "outsidePacCohortHalfYears": sum(r["pacStatus"] == "outside_pac_acquisition_cohort" for r in rows),
              "pairedSourceHalfYears": sum(r["pairedSourcePresence"] == "true" for r in rows),
              "causalEffect": "not_identified"}
    snapshots = {}
    for name, values in (("substitution-lda-filing-metadata.csv", metadata),
                         ("substitution-fec-acquisition-cohort.csv", cohort),
                         ("substitution-fec-halfyear-coverage.csv", coverage),
                         ("substitution-fec-halfyear-panel.csv", outcomes),
                         ("substitution-estimation-panel.csv", legacy)):
        snapshots[name] = hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    payload = {"schema": "substitution-comparison-review-v1", "sourceAvailability": totals,
               "legacySourceAlias": alias, "parsedInputFingerprints": snapshots,
               "boundary": "Negative identification result for the current source products, not an observed null effect or a representative sample."}
    (reports / "substitution-comparison-review.json").write_text(json.dumps(payload, indent=2) + "\n")
    lines = ["# Substitution comparison: negative identification result", "",
             "**Assessment: usable for documenting why the current study cannot estimate a causal substitution effect.** "
             "No new effect is fitted. Missing exposure and comparison evidence is not evidence of a zero effect.", "",
             "## What the expanded records actually pair", "",
             f"The observed LDA source frame contains {totals['observedLdaActors']} API-attributed candidates across "
             f"{totals['actorHalfYears']} actor-half-years in 2003-2008. This is the frame of actors with returned source rows, "
             "not the full acquisition-query frame, a population sample or a validated control cohort. "
             "Registrations are excluded. A complete native-period footprint means at least one activity filing is present "
             "for each expected reporting period; it does not certify exhaustive filings, final amendments, identity or comparable spending.", "",
             f"The {len(cohort)}-PAC acquisition frame retains {len(coverage)} expected periods: {len(outcomes)} with usable "
             f"prepared outcomes and {totals['unresolvedPacHalfYears']} unresolved. "
             f"Another {totals['outsidePacCohortHalfYears']} actor-half-years are outside that PAC cohort. "
             f"There are {totals['pairedSourceHalfYears']} same-candidate periods with both an LDA filing and a PAC outcome. "
             "They are source overlaps, not independent observations or validated two-channel causal outcomes.", "",
             "| API-attributed candidate | LDA half-years with full native-period footprint | PAC usable / expected | PAC acquisition status | Missing API expense methods / expense records |",
             "|---|---:|---:|---|---:|"]
    for actor in sorted({r["canonicalActorId"] for r in rows}):
        selected = [r for r in rows if r["canonicalActorId"] == actor]
        in_cohort = bool(selected[0]["committeeId"])
        observed = sum(r["pacStatus"] == "observed_complete" for r in selected)
        lines.append(f"| {selected[0]['actorName']} | {sum(r['ldaNativePeriodFootprint'] == 'present' for r in selected)} / {len(selected)} | "
                     f"{str(observed) + ' / ' + str(len(selected)) if in_cohort else 'not acquired'} | "
                     f"{'retained, including unresolved periods' if in_cohort else 'outside this PAC cohort'} | "
                     f"{sum(r['ldaExpenseMethodMissing'] for r in selected)} / {sum(r['ldaExpenseRecords'] for r in selected)} |")
    lines += ["", "The [availability CSV](substitution-comparison-availability.csv) preserves filing IDs, native-period counts, "
              "separate income/expense record counts, PAC evidence IDs and observed PAC amounts. Unknown or unacquired PAC "
              "amounts stay blank; an observed zero stays zero. API accounting-method missingness remains visible even where "
              "a separate source review has recovered a method. The earlier ledgers remain authoritative for those readings. "
              "No LDA monetary total or spending ratio is constructed.", "",
              "## Why the legacy control comparison cannot separate a source change", "",
              f"On the legacy panel's {alias['primaryObservations']} included actor-quarters ({alias['actors']} actors; "
              f"{alias['preObservations']} nominal pre and {alias['postObservations']} post observations), the diagnostic basis "
              f"`[1, treated, post, treated*post, federal_source*post]` has exact rank {alias['exactRank']} of {alias['columnCount']}. "
              f"The two interaction columns are identical: `{str(alias['interactionColumnsIdentical']).lower()}`. "
              "Increasing the treatment coefficient by one and decreasing the source-specific post coefficient by one "
              f"changes fitted predictions by at most {alias['maxPredictionChangeForOppositeUnitCoefficientShifts']}.", "",
              "This is an algebraic non-identification result for an augmented model allowing an unrestricted federal-source "
              "post change. It does not show that such a shock actually occurred or that every difference-in-differences "
              "design with different sources is invalid. An estimate would require additional credible restrictions or "
              "comparison evidence that distinguishes the reform from source/jurisdiction-specific changes. The current "
              "federal amounts and Colorado income records also have different measurement definitions. "
              "The old descriptive estimate and its bootstrap interval remain unchanged; an interval crossing zero is "
              "not itself an identification failure. No causal coefficient or null-effect test follows from this rank check.", "",
              "## Provision-specific conclusions", "",
              "| Proposed contrast | Present failure | Evidence needed to reopen estimation |",
              "|---|---|---|",
              "| Quarterly reporting | No verified unexposed group in the same reporting system; filing frequency changes mechanically. | A comparable outcome and credible comparison or other design separating reporting changes from behavior. |",
              "| Gift/travel restrictions | No pre-reform reliance or provision-specific exposure assignment; earlier scrutiny may contaminate nominal pre periods. | Dated pre-reform reliance, applicable timing, comparable actors, and both channels observed for both groups. |",
              "| Coalition disclosure | Names, membership websites and empty affiliate arrays do not establish qualifying funding, participation or prior disclosure. | Pre-reform funding/participation and disclosure evidence, with comparably measured lower-exposure controls. |",
              "", "The [enacted HLOGA, sections 201 and 215](https://www.govinfo.gov/content/pkg/PLAW-110publ81/html/PLAW-110publ81.htm) "
              "sets quarterly reporting from January 2008; sections 206 and 207 require separate provision-specific treatment "
              "definitions. The prepared PAC series' 2007H2 exclusion is an enactment/anticipation convention, not a verified "
              "common implementation date. Nine nominal pre-enactment half-years do not certify an unaffected baseline. "
              "Splitting semiannual observations into quarters adds no independent history.", "",
              "## Decision and stopping rule for this evidence freeze", "",
              "Do not fit a successor causal model from these products. Reopen that decision when dated pre-reform exposure "
              "and a defensible comparison are supplied, then resolve source versions, comparable accounting scope, actor/PAC "
              "links and common period coverage before estimation. Additional filing rows alone do not clear the design. "
              "A reform-induced change in two separately measured channels would still require interpretation before calling "
              "it substitution; an elasticity additionally needs a defined response to a measured cost or constraint change. "
              "PAC contributions and lobbying expense are not exhaustive measures of influence or hidden-channel spending.", "",
              "This closes the inference decision for the present substitution freeze with a documented negative result. "
              "It does not close the full empirical goal, obtain a representative SAM export, resolve procurement links, "
              "or independently adjudicate comment coding. The detailed [redesign and source reviews](../docs/substitution-study-redesign.md) "
              "retain the evidence and acquisition limits.", "",
              "Reproduce with `make empirical-expansion-audit` and the companion `notebooks/empirical-expansion-review.ipynb`. "
              "The [machine-readable review](substitution-comparison-review.json) fingerprints parsed input tables in stored "
              "row order. These hashes identify the checked products; they do not authenticate upstream raw responses or "
              "independently validate source readings.", ""]
    (reports / "substitution-comparison-review.md").write_text("\n".join(lines), encoding="utf-8")
    return totals, alias
