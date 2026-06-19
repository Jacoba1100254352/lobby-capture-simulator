#!/usr/bin/env python3
"""Extract direct source moments from normalized calibration tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


SNAPSHOT = Path("data/snapshots/2024-env/normalized")
FIXTURES = Path("data/fixtures")
OUTPUT = Path("reports")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    rows = []
    rows.extend(extract_scope("snapshot", args.snapshot, ""))
    rows.extend(extract_scope("fixture", args.fixtures, "normalized-"))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "source-moments.csv", rows)
    write_markdown(args.output / "source-moments.md", rows)
    print(f"Wrote {args.output / 'source-moments.csv'}")
    print(f"Wrote {args.output / 'source-moments.md'}")
    return 0


def extract_scope(scope: str, root: Path, prefix: str) -> list[dict[str, str]]:
    rows = []
    rows.extend(lda_moments(scope, root / f"{prefix}lda-lobbying.csv"))
    rows.extend(fec_moments(
        scope,
        root / f"{prefix}fec-campaign-finance.csv",
        root / f"{prefix}public-financing.csv",
        root / f"{prefix}dark-money.csv",
    ))
    rows.extend(regulatory_moments(scope, root / f"{prefix}regulatory-dockets.csv"))
    rows.extend(oira_meeting_moments(scope, root / f"{prefix}oira-meetings.csv"))
    rows.extend(usaspending_moments(
        scope,
        root / f"{prefix}usaspending-awards.csv",
        root / f"{prefix}usaspending-procurement-bridge.csv",
        root / f"{prefix}usaspending-procurement-actions.csv",
        root / f"{prefix}usaspending-procurement-national-actions.csv",
        root / f"{prefix}usaspending-procurement-bulk-summary.json",
        root / f"{prefix}sam-contract-awards.csv",
    ))
    rows.extend(revolving_door_moments(scope, root / f"{prefix}revolving-door.csv"))
    rows.extend(intermediary_moments(scope, root / f"{prefix}intermediaries.csv"))
    return rows


def lda_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "lda", "ldaRows", 0.0, "observed", f"{path} missing or empty")]
    amounts = [number(row.get("amount")) for row in rows]
    by_client = grouped_amount(rows, "client")
    by_registrant = grouped_amount(rows, "registrant")
    by_sector = grouped_amount(rows, "issueDomain")
    total = sum(amounts)
    return [
        moment(scope, "lda", "ldaRows", len(rows), "observed", "normalized LDA rows"),
        moment(scope, "lda", "ldaTotalSpend", total, "observed", "sum of normalized LDA amount"),
        moment(scope, "lda", "lobbyingClientTop1Share", top_share(by_client, 1), "observed", "largest client share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingClientTop3Share", top_share(by_client, 3), "observed", "top three clients share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingRegistrantTop3Share", top_share(by_registrant, 3), "observed", "top three registrants share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingSectorTopShare", top_share(by_sector, 1), "observed", "largest issue-domain share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingDisclosureLagMean", average([number(row.get("disclosureLag")) for row in rows]), "observed", "mean normalized LDA disclosure lag"),
        moment(scope, "lda", "coveredOfficialShareMean", average([number(row.get("coveredOfficialShare")) for row in rows]), "observed_proxy", "mean share of covered-official contact visibility"),
        moment(scope, "lda", "lobbyingClientHerfindahl", herfindahl(by_client), "observed", "client concentration Herfindahl over normalized LDA amount"),
    ]


def fec_moments(scope: str, path: Path, public_financing_path: Path, dark_money_path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    public_bridge_rows = read_rows(public_financing_path)
    dark_money_bridge_rows = read_rows(dark_money_path)
    if not rows and not public_bridge_rows and not dark_money_bridge_rows:
        return [moment(scope, "fec", "fecRows", 0.0, "observed", f"{path} missing or empty")]
    by_source = grouped_amount(rows, "source")
    by_recipient = grouped_amount(rows, "recipient")
    amounts = [number(row.get("amount")) for row in rows]
    total = sum(amounts)
    dark_money_rows = [row for row in rows if row.get("flowType", "").upper() == "DARK_MONEY"]
    all_dark_money_rows = dark_money_rows + dark_money_bridge_rows
    dark_money_capacity_proxy_rows = [row for row in all_dark_money_rows if is_dark_money_capacity_proxy(row)]
    dark_money_direct_routing_rows = [row for row in all_dark_money_rows if not is_dark_money_capacity_proxy(row)]
    all_dark_money_total = sum(number(row.get("amount")) for row in all_dark_money_rows)
    dark_money_direct_routing_total = sum(number(row.get("amount")) for row in dark_money_direct_routing_rows)
    super_pac_rows = [row for row in rows if row.get("flowType", "").upper() == "SUPER_PAC"]
    electioneering_rows = [row for row in rows if row.get("flowType", "").upper() == "ELECTIONEERING"]
    communication_cost_rows = [row for row in rows if row.get("flowType", "").upper() == "COMMUNICATION_COST"]
    electoral_communication_rows = electioneering_rows + communication_cost_rows
    public_rows = [row for row in rows if row.get("flowType", "").upper() in {"PUBLIC_MATCH", "DEMOCRACY_VOUCHER"}]
    all_public_rows = public_rows + public_bridge_rows
    all_public_total = sum(number(row.get("amount")) for row in all_public_rows)
    voucher_rows = [row for row in all_public_rows if row.get("flowType", "").upper() == "DEMOCRACY_VOUCHER"]
    public_match_rows = [row for row in all_public_rows if row.get("flowType", "").upper() == "PUBLIC_MATCH"]
    public_programs = {row.get("source", "") for row in all_public_rows if row.get("source", "")}
    opaque_electoral_rows = all_dark_money_rows + super_pac_rows
    outside_rows = [
        row for row in rows
        if row.get("flowType", "").upper() in {"DARK_MONEY", "SUPER_PAC", "TRADE_ASSOCIATION", "ELECTIONEERING", "COMMUNICATION_COST"}
    ] + dark_money_bridge_rows
    by_outside_source = grouped_amount(outside_rows, "source")
    campaign_total = total + all_public_total + all_dark_money_total
    return [
        moment(scope, "fec", "fecRows", len(rows), "observed", "normalized OpenFEC rows"),
        moment(scope, "fec", "fecTotalReceipts", total, "observed", "sum of normalized FEC amount"),
        moment(scope, "fec", "fecDonorTop1Share", top_share(by_source, 1), "observed", "largest donor share of normalized FEC amount"),
        moment(scope, "fec", "fecDonorTop3Share", top_share(by_source, 3), "observed", "top three donor share of normalized FEC amount"),
        moment(scope, "fec", "fecDonorGini", gini(amounts), "observed", "donor amount Gini across normalized FEC rows"),
        moment(scope, "fec", "fecRecipientTop3Share", top_share(by_recipient, 3), "observed", "top three recipient share of normalized FEC amount"),
        moment(scope, "fec", "fecLargeDonorWeightedShare", weighted(rows, "largeDonorShare", "amount"), "observed_proxy", "amount-weighted normalized large donor share"),
        moment(scope, "fec", "moneyFlowTraceability", weighted(rows, "traceability", "amount"), "observed_proxy", "amount-weighted traceability across all normalized FEC rows"),
        moment(scope, "fec", "darkMoneyRows", len(all_dark_money_rows), "observed_proxy", "DARK_MONEY rows from FEC or explicit dark-money/opaque-capacity bridge panels"),
        moment(scope, "fec", "darkMoneyCapacityProxyRows", len(dark_money_capacity_proxy_rows), "observed_proxy", "DARK_MONEY rows marked as IRS EO BMF opaque-capacity proxies"),
        moment(scope, "fec", "darkMoneyDirectRoutingRows", len(dark_money_direct_routing_rows), "observed", "non-proxy DARK_MONEY rows that can support direct hidden-donor or nonprofit-routing evidence"),
        moment(scope, "fec", "darkMoneyDirectRoutingSourceShare", safe_divide(dark_money_direct_routing_total, campaign_total), "observed", "non-proxy DARK_MONEY share of normalized campaign-finance plus bridge amount"),
        moment(scope, "fec", "darkMoneyDirectVisibility", weighted(dark_money_direct_routing_rows, "traceability", "amount"), "inferred", "amount-weighted traceability among non-proxy DARK_MONEY routing rows only"),
        moment(scope, "fec", "darkMoneySourceShare", safe_divide(all_dark_money_total, campaign_total), "observed_proxy", "DARK_MONEY or opaque-capacity bridge share of normalized campaign-finance plus bridge amount"),
        moment(scope, "fec", "superPacSourceShare", safe_divide(sum(number(row.get("amount")) for row in super_pac_rows), campaign_total), "observed_proxy", "SUPER_PAC share of normalized campaign-finance plus bridge amount"),
        moment(scope, "fec", "opaqueElectoralSourceShare", safe_divide(sum(number(row.get("amount")) for row in opaque_electoral_rows), campaign_total), "observed_proxy", "DARK_MONEY plus SUPER_PAC share of normalized campaign-finance plus bridge amount"),
        moment(scope, "fec", "electioneeringRows", len(electioneering_rows), "observed", "normalized OpenFEC electioneering communication rows"),
        moment(scope, "fec", "communicationCostRows", len(communication_cost_rows), "observed", "normalized OpenFEC communication-cost rows"),
        moment(scope, "fec", "electoralCommunicationRows", len(electoral_communication_rows), "observed", "normalized electioneering plus communication-cost rows"),
        moment(scope, "fec", "electoralCommunicationSourceShare", safe_divide(sum(number(row.get("amount")) for row in electoral_communication_rows), campaign_total), "observed_proxy", "electioneering and communication-cost share of normalized campaign-finance plus bridge amount"),
        moment(scope, "fec", "electoralCommunicationTraceabilityMean", weighted(electoral_communication_rows, "traceability", "amount"), "observed_proxy", "amount-weighted traceability among electioneering and communication-cost rows"),
        moment(scope, "fec", "outsideSpendingRows", len(outside_rows), "observed", "normalized independent expenditure, super PAC, dark-money, association, electioneering, or communication-cost rows"),
        moment(scope, "fec", "outsideSpendingSourceShare", safe_divide(sum(number(row.get("amount")) for row in outside_rows), campaign_total), "observed_proxy", "outside-spending bridge share of normalized campaign-finance plus bridge amount"),
        moment(scope, "fec", "outsideSpendingTop3SourceShare", top_share(by_outside_source, 3), "observed_proxy", "top three outside spenders by normalized amount"),
        moment(scope, "fec", "outsideSpendingDisclosureLagMean", weighted(outside_rows, "disclosureLag", "amount"), "observed_proxy", "amount-weighted reporting lag among outside-spending rows"),
        moment(scope, "fec", "publicFinancingRows", len(all_public_rows), "observed_proxy", "public-match or voucher rows from FEC or explicit public-financing panel"),
        moment(scope, "fec", "publicFinancingProgramCount", len(public_programs), "observed_proxy", "distinct public-financing program sources represented"),
        moment(scope, "fec", "publicFinancingVoucherRows", len(voucher_rows), "observed", "democracy-voucher rows from explicit public-financing panels"),
        moment(scope, "fec", "publicFinancingMatchingRows", len(public_match_rows), "observed", "public matching-fund rows from explicit public-financing panels"),
        moment(scope, "fec", "publicFinancingVoucherAmount", sum(number(row.get("amount")) for row in voucher_rows), "observed_proxy", "sum of normalized democracy-voucher amount"),
        moment(scope, "fec", "publicFinancingProgramAmount", all_public_total, "observed_proxy", "sum of public-match and voucher bridge amount"),
        moment(scope, "fec", "publicFinancingSourceShare", safe_divide(all_public_total, campaign_total), "observed_proxy", "public-match or voucher share of normalized campaign-finance plus bridge amount"),
        moment(scope, "fec", "publicFinancingTraceabilityMean", weighted(all_public_rows, "traceability", "amount"), "observed_proxy", "amount-weighted traceability among public-financing rows"),
        moment(scope, "fec", "publicFinancingLargeDonorWeightedShare", weighted(all_public_rows, "largeDonorShare", "amount"), "observed_proxy", "amount-weighted large-donor share among public-financing rows"),
    ]


def regulatory_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "regulatory", "regulatoryRows", 0.0, "observed", f"{path} missing or empty")]
    by_docket = grouped_amount(rows, "docketId", "commentVolume")
    return [
        moment(scope, "regulatory", "regulatoryRows", len(rows), "observed", "normalized regulatory rows"),
        moment(scope, "regulatory", "commentVolumeMean", average([number(row.get("commentVolume")) for row in rows]), "observed_proxy", "mean normalized comment volume"),
        moment(scope, "regulatory", "commentVolumeTop1DocketShare", top_share(by_docket, 1), "observed_proxy", "largest docket share of normalized comments"),
        moment(scope, "regulatory", "commentTemplateShareMean", average([number(row.get("templateShare")) for row in rows]), "observed_proxy", "mean normalized template share"),
        moment(scope, "regulatory", "commentAuthenticationShareMean", average([number(row.get("authenticationShare")) for row in rows]), "observed_proxy", "mean normalized authentication share"),
        moment(scope, "regulatory", "commentFloodingIndex", comment_flooding_index(rows, by_docket), "proxy", "combined top-docket concentration, template share, and low-authentication pressure"),
        moment(scope, "regulatory", "technicalClaimCredibilityMean", average([number(row.get("technicalClaimCredibility")) for row in rows]), "proxy", "mean normalized technical claim credibility"),
    ]


def oira_meeting_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "oira-meetings", "oiraMeetingRows", 0.0, "observed", f"{path} missing or empty")]
    by_requestor = grouped_count(rows, "requestorOrganization")
    by_client = grouped_count(rows, "requestorClient")
    by_agency = grouped_count(rows, "agency")
    by_rin = grouped_count(rows, "rin")
    detail_rows = [row for row in rows if flag(row.get("detailFetched"))]
    participant_rows = [row for row in rows if flag(row.get("participantDisclosure"))]
    client_rows = [row for row in rows if flag(row.get("clientDisclosure"))]
    completed_rows = [row for row in rows if "completed" in row.get("meetingStatus", "").lower()]
    scheduled_rows = [row for row in rows if "scheduled" in row.get("meetingStatus", "").lower()]
    return [
        moment(scope, "oira-meetings", "oiraMeetingRows", len(rows), "observed", "normalized Reginfo.gov EO 12866 public meeting rows"),
        moment(scope, "oira-meetings", "oiraMeetingDetailFetchedShare", safe_divide(len(detail_rows), len(rows)), "diagnostic", "share of meeting rows with detail pages fetched"),
        moment(scope, "oira-meetings", "oiraMeetingParticipantDisclosureShare", safe_divide(len(participant_rows), len(rows)), "observed", "share of rows with requestor or participant disclosure fields populated"),
        moment(scope, "oira-meetings", "oiraMeetingClientDisclosureShare", safe_divide(len(client_rows), len(rows)), "observed", "share of rows with requestor-client disclosure"),
        moment(scope, "oira-meetings", "oiraMeetingAgencyCount", len([key for key in by_agency if key != "unknown"]), "observed", "distinct agency acronyms in normalized EO 12866 meeting rows"),
        moment(scope, "oira-meetings", "oiraMeetingRinCount", len([key for key in by_rin if key != "unknown"]), "observed", "distinct RINs in normalized EO 12866 meeting rows"),
        moment(scope, "oira-meetings", "oiraMeetingRequestorTop3Share", top_share(by_requestor, 3), "observed_proxy", "top three requestors by normalized EO 12866 meeting count"),
        moment(scope, "oira-meetings", "oiraMeetingClientTop3Share", top_share(by_client, 3), "observed_proxy", "top three requestor clients by normalized EO 12866 meeting count"),
        moment(scope, "oira-meetings", "oiraMeetingCompletedShare", safe_divide(len(completed_rows), len(rows)), "observed", "share of rows marked completed"),
        moment(scope, "oira-meetings", "oiraMeetingScheduledShare", safe_divide(len(scheduled_rows), len(rows)), "observed", "share of rows marked scheduled"),
    ]


def usaspending_moments(
        scope: str,
        path: Path,
        bridge_path: Path,
        action_path: Path,
        national_action_path: Path,
        bulk_summary_path: Path,
        sam_path: Path,
) -> list[dict[str, str]]:
    rows = read_rows(path)
    bridge_rows = read_rows(bridge_path)
    usaspending_action_rows = read_rows(action_path)
    national_action_rows = read_rows(national_action_path)
    bulk_summary = read_json(bulk_summary_path)
    sam_action_rows = read_rows(sam_path)
    action_rows, action_note, action_source = procurement_action_panel(usaspending_action_rows, sam_action_rows)
    if not rows and not bridge_rows and not usaspending_action_rows and not national_action_rows and not bulk_summary and not sam_action_rows:
        return [moment(scope, "usaspending", "procurementRows", 0.0, "observed", f"{path} missing or empty")]
    concentration_rows, concentration_note, concentration_source = concentration_panel(
        rows,
        bridge_rows,
        action_rows,
        action_note,
        action_source,
        national_action_rows,
    )
    award_rows = rows if rows else concentration_rows
    competition_rows = [row for row in award_rows if has_competition_data(row)] or award_rows
    modification_rows_source = action_rows or [row for row in award_rows if has_modification_data(row)] or award_rows
    competition_note = "normalized USAspending award rows with competition fields" if rows else concentration_note
    modification_note = action_note if action_rows else ("normalized USAspending award rows with modification fields" if rows else concentration_note)
    by_recipient = grouped_amount(concentration_rows, "recipient")
    by_agency = grouped_amount(concentration_rows, "agency")
    by_agency_count = grouped_count(concentration_rows, "agency")
    by_sub_agency = grouped_amount(concentration_rows, "subAgency")
    action_agency_count = len({row.get("agency", "") for row in action_rows if row.get("agency", "").strip()})
    national_action_agency_count = len({row.get("agency", "") for row in national_action_rows if row.get("agency", "").strip()})
    concentration_agency_count = len({row.get("agency", "") for row in concentration_rows if row.get("agency", "").strip()})
    concentration_total = sum(number(row.get("amount")) for row in concentration_rows)
    competition_total = sum(number(row.get("amount")) for row in competition_rows)
    modification_total = sum(number(row.get("amount")) for row in modification_rows_source)
    single_bid_rows = [row for row in competition_rows if number(row.get("numberOfOffers")) <= 1.0 and number(row.get("numberOfOffers")) > 0.0]
    modified_rows = [
        row
        for row in modification_rows_source
        if flag(row.get("exPostModification")) or modification_sequence(row.get("modificationNumber")) > 0
    ]
    initial_rows = [
        row
        for row in modification_rows_source
        if not flag(row.get("exPostModification")) and modification_sequence(row.get("modificationNumber")) == 0
    ]
    price_only_rows = [row for row in competition_rows if flag(row.get("priceOnlyAward"))]
    firewall_rows = [row for row in award_rows if flag(row.get("firewallCovered"))]
    protest_rows = [row for row in award_rows if flag(row.get("protestFiled"))]
    exclusion_rows = [row for row in competition_rows if flag(row.get("exclusionFlag")) or "EXCLUSION" in row.get("competitionType", "").upper()]
    limited_competition_rows = [
        row
        for row in competition_rows
        if competition_limited(row.get("competitionType", "")) or (number(row.get("numberOfOffers")) <= 1.0 and number(row.get("numberOfOffers")) > 0.0)
    ]
    award_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in modification_rows_source:
        award_groups[procurement_award_key(row)].append(row)
    modified_award_groups = [
        group
        for group in award_groups.values()
        if any(flag(row.get("exPostModification")) or modification_sequence(row.get("modificationNumber")) > 0 for row in group)
    ]
    uei_rows = [row for row in award_rows if row.get("uei", "").strip()]
    piid_rows = [row for row in award_rows if row.get("piid", "").strip()]
    agency_count = len({row.get("agency", "") for row in bridge_rows if row.get("agency", "").strip()})
    output = [
        moment(scope, "usaspending", "procurementRows", len(rows), "observed", "normalized USAspending award rows"),
        moment(scope, "usaspending", "procurementBridgeRows", len(bridge_rows), "observed", "multi-agency USAspending bridge rows, if available"),
        moment(scope, "usaspending", "procurementActionRows", len(action_rows), "observed", f"primary procurement action denominator from {action_note}"),
        moment(scope, "usaspending", "procurementUsaspendingActionRows", len(usaspending_action_rows), "observed", "normalized USAspending transaction/action rows, if available"),
        moment(scope, "usaspending", "procurementNationalActionRows", len(national_action_rows), "observed", "national-volume no-agency-filtered USAspending transaction/action rows, if available"),
        moment(scope, "usaspending", "procurementNationalActionAgencyCount", national_action_agency_count, "diagnostic", "distinct awarding agencies in the national-volume USAspending transaction/action panel"),
        moment(scope, "sam", "procurementSamContractAwardRows", len(sam_action_rows), "observed", "normalized SAM.gov Contract Awards rows, if available"),
        moment(scope, "usaspending", "procurementActionPanelUsaspendingSample", 1.0 if action_source == "usaspending-action" else 0.0, "diagnostic", "1 when the primary procurement action denominator uses USAspending transaction/action rows"),
        moment(scope, "sam", "procurementActionPanelSamSample", 1.0 if action_source == "sam-contract-awards" else 0.0, "diagnostic", "1 when the primary procurement action denominator uses SAM.gov Contract Awards rows"),
        moment(scope, "usaspending", "procurementConcentrationPanelRows", len(concentration_rows), "diagnostic", f"rows used for concentration moments from {concentration_note}"),
        moment(scope, "usaspending", "procurementConcentrationPanelAgencyCount", concentration_agency_count, "observed", "distinct awarding agencies in the procurement concentration panel"),
        moment(scope, "usaspending", "procurementConcentrationPanelActionSample", 1.0 if concentration_source in {"usaspending-action", "usaspending-national-action", "sam-contract-awards"} else 0.0, "diagnostic", "1 when procurement concentration moments use a transaction/action panel"),
        moment(scope, "usaspending", "procurementConcentrationPanelNationalVolumeSample", 1.0 if concentration_source == "usaspending-national-action" else 0.0, "diagnostic", "1 when procurement concentration moments use the national-volume no-agency-filtered USAspending action panel"),
        moment(scope, "usaspending", "procurementConcentrationPanelTopAwardSample", 1.0 if concentration_source == "bridge" else 0.0, "diagnostic", "1 when procurement concentration moments use the multi-agency top-award bridge"),
        moment(scope, "usaspending", "procurementCompetitionPanelRows", len(competition_rows), "diagnostic", f"rows used for competition moments from {competition_note}"),
        moment(scope, "usaspending", "procurementModificationPanelRows", len(modification_rows_source), "diagnostic", f"rows used for modification moments from {modification_note}"),
        moment(scope, "usaspending", "procurementBridgeAgencyCount", agency_count, "observed", "distinct awarding agencies in procurement source moment panel"),
        moment(scope, "usaspending", "procurementActionAgencyCount", action_agency_count, "diagnostic", f"distinct awarding agencies in the primary transaction/action panel from {action_note}"),
        moment(scope, "usaspending", "procurementBridgeTopAwardSample", 1.0 if bridge_rows else 0.0, "diagnostic", "1 when a separate multi-agency top-award bridge is available"),
        moment(scope, "usaspending", "procurementLatestTransactionModificationProxy", 1.0 if bridge_rows else 0.0, "diagnostic", "1 when latest-transaction enrichment exists but is kept separate from action-level modification incidence"),
        moment(scope, "usaspending", "procurementTotalAwards", concentration_total, "observed", f"sum of {concentration_note} amount"),
        moment(scope, "usaspending", "procurementRecipientTop1Share", top_share(by_recipient, 1), "observed", f"largest recipient share of {concentration_note} amount"),
        moment(scope, "usaspending", "procurementRecipientTop3Share", top_share(by_recipient, 3), "observed", f"top three recipients share of {concentration_note} amount"),
        moment(scope, "usaspending", "procurementRecipientHerfindahl", herfindahl(by_recipient), "observed", f"recipient award-amount Herfindahl over {concentration_note}"),
        moment(scope, "usaspending", "procurementAgencyTop1Share", top_share(by_agency, 1), "observed", f"largest awarding agency share of {concentration_note} amount"),
        moment(scope, "usaspending", "procurementAgencyTop1CountShare", top_share(by_agency_count, 1), "diagnostic", f"largest awarding agency row-count share of {concentration_note}"),
        moment(scope, "usaspending", "procurementAgencyHerfindahl", herfindahl(by_agency), "observed", f"awarding-agency amount Herfindahl over {concentration_note}"),
        moment(scope, "usaspending", "procurementSubAgencyTop3Share", top_share(by_sub_agency, 3), "observed", f"top three sub-agencies share of {concentration_note} amount"),
        moment(scope, "usaspending", "procurementAwardCount", sum(number(row.get("awardCount")) for row in concentration_rows), "observed", f"sum of normalized award or transaction counts in {concentration_note}"),
        moment(scope, "usaspending", "procurementSingleBidShare", safe_divide(len(single_bid_rows), len(competition_rows)), "observed_proxy", f"share among {competition_note} that have one known offer"),
        moment(scope, "usaspending", "procurementAmountWeightedSingleBidShare", safe_divide(sum(number(row.get("amount")) for row in single_bid_rows), competition_total), "observed_proxy", f"award-amount share among {competition_note} with one known offer"),
        moment(scope, "usaspending", "procurementInitialAwardShare", safe_divide(len(initial_rows), len(modification_rows_source)), "observed_proxy", f"share of {modification_note} that appear to be initial awards"),
        moment(scope, "usaspending", "procurementExPostModificationShare", safe_divide(len(modified_rows), len(modification_rows_source)), "observed_proxy", f"share of {modification_note} marked as ex-post modifications or nonzero modification sequence"),
        moment(scope, "usaspending", "procurementActionDistinctAwards", len(award_groups), "diagnostic", f"distinct PIID/award identifiers in {modification_note} used for award-level modification diagnostics"),
        moment(scope, "usaspending", "procurementModifiedAwardCount", len(modified_award_groups), "diagnostic", f"distinct PIID/award identifiers in {modification_note} with at least one ex-post modification row"),
        moment(scope, "usaspending", "procurementModifiedAwardShare", safe_divide(len(modified_award_groups), len(award_groups)), "observed_proxy", f"share of distinct PIID/award identifiers in {modification_note} with at least one ex-post modification row"),
        moment(scope, "usaspending", "procurementModificationActionsPerModifiedAward", safe_divide(len(modified_rows), len(modified_award_groups)), "diagnostic", f"mean modified action rows per modified PIID/award identifier in {modification_note}"),
        moment(scope, "usaspending", "procurementAmountWeightedModificationShare", safe_divide(sum(number(row.get("amount")) for row in modified_rows), modification_total), "observed_proxy", f"award-amount share of {modification_note} marked as ex-post modifications"),
        moment(scope, "usaspending", "procurementActionModificationRows", len([row for row in action_rows if flag(row.get("exPostModification")) or modification_sequence(row.get("modificationNumber")) > 0]), "diagnostic", f"primary transaction/action rows from {action_note} marked as ex-post modifications"),
        moment(scope, "usaspending", "procurementPriceOnlyAwardShare", safe_divide(len(price_only_rows), len(competition_rows)), "observed_proxy", f"share among {competition_note} marked as price-only or one-offer awards"),
        moment(scope, "usaspending", "procurementLimitedCompetitionShare", safe_divide(len(limited_competition_rows), len(competition_rows)), "observed_proxy", f"share among {competition_note} with limited competition, exclusions, or one known offer"),
        moment(scope, "usaspending", "procurementProtestShare", safe_divide(len(protest_rows), len(award_rows)), "observed_proxy", "share of normalized award rows marked with a protest flag"),
        moment(scope, "usaspending", "procurementExclusionShare", safe_divide(len(exclusion_rows), len(competition_rows)), "observed_proxy", f"share among {competition_note} marked as exclusions or after-exclusion competition"),
        moment(scope, "usaspending", "procurementFirewallCoverageShare", safe_divide(len(firewall_rows), len(award_rows)), "observed_proxy", "share of normalized award rows covered by a procurement-firewall flag"),
        moment(scope, "usaspending", "procurementKnownUeiShare", safe_divide(len(uei_rows), len(award_rows)), "diagnostic", "share of normalized award rows carrying a recipient UEI"),
        moment(scope, "usaspending", "procurementKnownPiidShare", safe_divide(len(piid_rows), len(award_rows)), "diagnostic", "share of normalized award rows carrying a procurement instrument identifier"),
    ]
    if bulk_summary:
        output.extend(bulk_procurement_moments(scope, bulk_summary))
    return output


def bulk_procurement_moments(scope: str, summary: dict[str, object]) -> list[dict[str, str]]:
    note = "USAspending public bulk transaction download summary; normalized CSV/ZIP payloads are archived outside git"
    rows = number(summary.get("downloadedNormalizedRows"))
    return [
        moment(scope, "usaspending-bulk", "procurementActionRows", rows, "observed", note),
        moment(scope, "usaspending-bulk", "procurementBulkTransactionRows", rows, "observed", note),
        moment(scope, "usaspending-bulk", "procurementUsaspendingBulkSummaryRows", rows, "diagnostic", note),
        moment(scope, "usaspending-bulk", "procurementActionPanelBulkSample", 1.0, "diagnostic", "1 when the primary procurement action denominator uses the USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementActionPanelUsaspendingSample", 0.0, "diagnostic", "bounded USAspending action rows are superseded by the archived bulk summary for action-denominator moments"),
        moment(scope, "usaspending-bulk", "procurementActionPanelSamSample", 0.0, "diagnostic", "SAM.gov Contract Awards is not the active primary action denominator"),
        moment(scope, "usaspending-bulk", "procurementConcentrationPanelRows", rows, "diagnostic", "rows summarized in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementConcentrationPanelAgencyCount", number(summary.get("agencyCount")), "observed", "distinct awarding agencies in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementConcentrationPanelActionSample", 1.0, "diagnostic", "1 when procurement concentration moments use a transaction/action panel"),
        moment(scope, "usaspending-bulk", "procurementConcentrationPanelNationalVolumeSample", 0.0, "diagnostic", "bulk summary is agency-scoped rather than no-filter national-volume"),
        moment(scope, "usaspending-bulk", "procurementConcentrationPanelTopAwardSample", 0.0, "diagnostic", "bulk summary is not a top-award bridge"),
        moment(scope, "usaspending-bulk", "procurementModificationPanelRows", rows, "diagnostic", "rows summarized in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementActionAgencyCount", number(summary.get("agencyCount")), "diagnostic", "distinct awarding agencies in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementBridgeTopAwardSample", 0.0, "diagnostic", "bulk summary supersedes top-award bridge for action-denominator moments"),
        moment(scope, "usaspending-bulk", "procurementLatestTransactionModificationProxy", 0.0, "diagnostic", "bulk summary uses transaction rows rather than latest-transaction enrichment"),
        moment(scope, "usaspending-bulk", "procurementTotalAwards", number(summary.get("amount")), "observed", "sum of USAspending bulk transaction amount"),
        moment(scope, "usaspending-bulk", "procurementRecipientTop1Share", number(summary.get("topRecipientAmountShare")), "observed", "largest recipient amount share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementRecipientTop3Share", number(summary.get("top3RecipientAmountShare")), "observed", "top three recipient amount share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementRecipientHerfindahl", number(summary.get("recipientHerfindahl")), "observed", "recipient amount Herfindahl in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementAgencyTop1Share", number(summary.get("topAgencyAmountShare")), "observed", "largest agency amount share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementAgencyTop1CountShare", number(summary.get("topAgencyRowShare")), "diagnostic", "largest agency row-count share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementAgencyHerfindahl", number(summary.get("agencyHerfindahl")), "observed", "agency amount Herfindahl in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementSingleBidShare", number(summary.get("singleKnownOfferShare")), "observed_proxy", "single known-offer share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementAmountWeightedSingleBidShare", number(summary.get("singleKnownOfferShare")), "observed_proxy", "single known-offer amount share is unavailable in the compact summary and uses row share"),
        moment(scope, "usaspending-bulk", "procurementInitialAwardShare", number(summary.get("initialActionShare")), "observed_proxy", "initial-action share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementExPostModificationShare", number(summary.get("modifiedActionShare")), "observed_proxy", "modified-action share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementActionDistinctAwards", number(summary.get("distinctAwardCount")), "diagnostic", "distinct PIID/award identifiers in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementModifiedAwardCount", number(summary.get("modifiedAwardCount")), "diagnostic", "distinct PIID/award identifiers with at least one modified row in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementModifiedAwardShare", number(summary.get("modifiedAwardShare")), "observed_proxy", "distinct-award modification share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementModificationActionsPerModifiedAward", number(summary.get("modificationRowsPerModifiedAward")), "diagnostic", "modified rows per modified PIID/award identifier in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementAmountWeightedModificationShare", number(summary.get("amountWeightedModificationShare")), "observed_proxy", "amount-weighted modification share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementActionModificationRows", number(summary.get("modifiedActionShare")) * rows, "diagnostic", "modified action rows in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementPriceOnlyAwardShare", number(summary.get("priceOnlyAwardShare")), "observed_proxy", "price-only or one-offer share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementLimitedCompetitionShare", number(summary.get("priceOnlyAwardShare")), "observed_proxy", "limited-competition proxy in compact USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementProtestShare", number(summary.get("protestShare")), "observed_proxy", "protest flag share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementExclusionShare", number(summary.get("exclusionShare")), "observed_proxy", "exclusion flag share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementFirewallCoverageShare", number(summary.get("firewallCoverageShare")), "observed_proxy", "firewall flag share in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementKnownUeiShare", number(summary.get("knownUeiShare")), "diagnostic", "UEI coverage in USAspending bulk transaction summary"),
        moment(scope, "usaspending-bulk", "procurementKnownPiidShare", number(summary.get("knownPiidShare")), "diagnostic", "PIID coverage in USAspending bulk transaction summary"),
    ]


def concentration_panel(
        award_rows: list[dict[str, str]],
        bridge_rows: list[dict[str, str]],
        action_rows: list[dict[str, str]],
        action_note: str,
        action_source: str,
        national_action_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], str, str]:
    """Choose the least-narrow available denominator for concentration moments."""
    if sufficient_action_panel(action_rows) and action_source == "sam-contract-awards":
        return action_rows, action_note, action_source
    if sufficient_action_panel(national_action_rows):
        return national_action_rows, "national-volume no-agency-filtered USAspending transaction/action rows", "usaspending-national-action"
    if sufficient_action_panel(action_rows):
        return action_rows, action_note, action_source
    if bridge_rows:
        return bridge_rows, "multi-agency procurement top-award bridge rows", "bridge"
    if award_rows:
        return award_rows, "normalized USAspending award rows", "award"
    return action_rows, action_note, action_source


def sufficient_action_panel(rows: list[dict[str, str]]) -> bool:
    agencies = {row.get("agency", "").strip() for row in rows if row.get("agency", "").strip()}
    return len(rows) >= 500 and len(agencies) >= 2


def procurement_action_panel(
        usaspending_action_rows: list[dict[str, str]],
        sam_action_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], str, str]:
    """Choose one primary transaction/action denominator while keeping provenance separate."""
    candidates = [
        ("sam-contract-awards", sam_action_rows, "SAM.gov Contract Awards rows"),
        ("usaspending-action", usaspending_action_rows, "stratified USAspending transaction/action rows"),
    ]
    sufficient = [
        candidate
        for candidate in candidates
        if len(candidate[1]) >= 500 and len({row.get("agency", "").strip() for row in candidate[1] if row.get("agency", "").strip()}) >= 2
    ]
    if sufficient:
        source, rows, note = max(
            sufficient,
            key=lambda candidate: (
                len({row.get("agency", "").strip() for row in candidate[1] if row.get("agency", "").strip()}),
                len(candidate[1]),
            ),
        )
        return rows, note, source
    available = [candidate for candidate in candidates if candidate[1]]
    if available:
        source, rows, note = max(
            available,
            key=lambda candidate: (
                len({row.get("agency", "").strip() for row in candidate[1] if row.get("agency", "").strip()}),
                len(candidate[1]),
            ),
        )
        return rows, note, source
    return [], "no procurement transaction/action rows", "none"


def revolving_door_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "revolving-door", "revolvingDoorRows", 0.0, "observed", f"{path} missing or empty")]
    former_rows = [row for row in rows if row.get("formerOfficialRole", "").strip()]
    fixture_rows = [row for row in rows if "fixture" in row.get("sourceType", "").lower()]
    by_agency = grouped_count(rows, "agency")
    return [
        moment(scope, "revolving-door", "revolvingDoorRows", len(rows), "observed", "normalized revolving-door rows"),
        moment(scope, "revolving-door", "revolvingDoorFixtureShare", safe_divide(len(fixture_rows), len(rows)), "diagnostic", "share of rows marked as tracked fixture rather than live/exported source"),
        moment(scope, "revolving-door", "revolvingDoorFormerOfficialShare", safe_divide(len(former_rows), len(rows)), "observed_proxy", "share of rows with former official role"),
        moment(scope, "revolving-door", "revolvingDoorAgencyTop1Share", top_share(by_agency, 1), "observed_proxy", "largest agency share of normalized revolving-door rows"),
        moment(scope, "revolving-door", "revolvingDoorCoolingOffUnderOneYearShare", safe_divide(sum(1 for row in rows if number(row.get("coolingOffMonths")) < 12), len(rows)), "observed_proxy", "share of rows with cooling-off interval below one year"),
        moment(scope, "revolving-door", "revolvingDoorCoolingOffMeanMonths", average([number(row.get("coolingOffMonths")) for row in rows]), "observed_proxy", "mean cooling-off interval in months"),
        moment(scope, "revolving-door", "revolvingDoorHighInfluenceShare", safe_divide(sum(1 for row in rows if number(row.get("influenceShare")) >= 0.60), len(rows)), "proxy", "share of rows with high normalized influence"),
        moment(scope, "revolving-door", "revolvingDoorInfluenceWeightedFormerOfficialShare", weighted_indicator(rows, "formerOfficialRole", "influenceShare"), "proxy", "influence-weighted former-official share"),
        moment(scope, "revolving-door", "revolvingDoorInfluenceMean", average([number(row.get("influenceShare")) for row in rows]), "proxy", "mean normalized influence share from source panel"),
        moment(scope, "revolving-door", "revolvingDoorConfidenceMean", average([number(row.get("confidence")) for row in rows]), "diagnostic", "mean source-match confidence for revolving-door records"),
    ]


def intermediary_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "intermediary", "intermediaryRows", 0.0, "observed", f"{path} missing or empty")]
    by_org = grouped_amount(rows, "organization", "revenue")
    total_revenue = sum(number(row.get("revenue")) for row in rows)
    total_political = sum(number(row.get("politicalSpend")) for row in rows)
    total_grants = sum(number(row.get("grantmaking")) for row in rows)
    association_rows = [row for row in rows if "501(c)(6)" in row.get("subsection", "")]
    c4_rows = [row for row in rows if "501(c)(4)" in row.get("subsection", "")]
    c3_rows = [row for row in rows if "501(c)(3)" in row.get("subsection", "")]
    section_527_rows = [row for row in rows if "527" in row.get("subsection", "") or "8872" in row.get("sourceType", "").lower()]
    return [
        moment(scope, "intermediary", "intermediaryRows", len(rows), "observed", "normalized nonprofit, 527, association, or think-tank intermediary rows"),
        moment(scope, "intermediary", "intermediaryTotalRevenue", total_revenue, "observed_proxy", "sum of normalized intermediary revenue"),
        moment(scope, "intermediary", "intermediaryPoliticalSpendShare", safe_divide(total_political, total_revenue), "observed_proxy", "political spend share of normalized intermediary revenue"),
        moment(scope, "intermediary", "intermediaryTop3RevenueShare", top_share(by_org, 3), "observed_proxy", "top three intermediary organizations by revenue"),
        moment(scope, "intermediary", "intermediaryDonorDisclosureMean", average([number(row.get("donorDisclosure")) for row in rows]), "observed_proxy", "mean donor/source disclosure score"),
        moment(scope, "intermediary", "intermediaryAssociationShare", safe_divide(len(association_rows), len(rows)), "observed_proxy", "share of rows marked 501(c)(6) association"),
        moment(scope, "intermediary", "intermediaryC4Share", safe_divide(len(c4_rows), len(rows)), "observed_proxy", "share of rows marked 501(c)(4) social welfare"),
        moment(scope, "intermediary", "intermediaryC3Share", safe_divide(len(c3_rows), len(rows)), "observed_proxy", "share of rows marked 501(c)(3) nonprofit"),
        moment(scope, "intermediary", "intermediary527Rows", len(section_527_rows), "observed", "normalized IRS 527/Form 8872 intermediary rows"),
        moment(scope, "intermediary", "intermediary527PoliticalSpend", sum(number(row.get("politicalSpend")) for row in section_527_rows), "observed_proxy", "sum of normalized 527/IRS 8872 political spending"),
        moment(scope, "intermediary", "intermediary527PoliticalSpendShare", safe_divide(sum(number(row.get("politicalSpend")) for row in section_527_rows), total_political), "observed_proxy", "527/IRS 8872 share of intermediary political spending"),
        moment(scope, "intermediary", "intermediary527DonorDisclosureMean", average([number(row.get("donorDisclosure")) for row in section_527_rows]), "observed_proxy", "mean donor/source disclosure among 527/IRS 8872 rows"),
        moment(scope, "intermediary", "intermediaryGrantmakingShare", safe_divide(total_grants, total_revenue), "observed_proxy", "grantmaking share of normalized intermediary revenue"),
    ]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def grouped_amount(rows: list[dict[str, str]], key: str, amount_key: str = "amount") -> dict[str, float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row.get(key, "") or "unknown"] += number(row.get(amount_key))
    return dict(grouped)


def grouped_count(rows: list[dict[str, str]], key: str) -> dict[str, float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row.get(key, "") or "unknown"] += 1.0
    return dict(grouped)


def top_share(amounts: dict[str, float], count: int) -> float:
    total = sum(amounts.values())
    if total <= 0.0:
        return 0.0
    return sum(sorted(amounts.values(), reverse=True)[:count]) / total


def herfindahl(amounts: dict[str, float]) -> float:
    total = sum(amounts.values())
    if total <= 0.0:
        return 0.0
    return sum((amount / total) ** 2 for amount in amounts.values())


def gini(values: list[float]) -> float:
    positives = sorted(value for value in values if value >= 0.0)
    if not positives:
        return 0.0
    total = sum(positives)
    if total <= 0.0:
        return 0.0
    weighted_sum = sum((index + 1) * value for index, value in enumerate(positives))
    count = len(positives)
    return ((2.0 * weighted_sum) / (count * total)) - ((count + 1.0) / count)


def weighted(rows: list[dict[str, str]], value_key: str, weight_key: str) -> float:
    total = sum(number(row.get(weight_key)) for row in rows)
    if total <= 0.0:
        return 0.0
    return sum(number(row.get(value_key)) * number(row.get(weight_key)) for row in rows) / total


def weighted_indicator(rows: list[dict[str, str]], indicator_key: str, weight_key: str) -> float:
    total = sum(number(row.get(weight_key)) for row in rows)
    if total <= 0.0:
        return 0.0
    return sum((1.0 if row.get(indicator_key, "").strip() else 0.0) * number(row.get(weight_key)) for row in rows) / total


def comment_flooding_index(rows: list[dict[str, str]], by_docket: dict[str, float]) -> float:
    value = (
        (0.34 * top_share(by_docket, 1))
        + (0.30 * average([number(row.get("templateShare")) for row in rows]))
        + (0.20 * average([1.0 - number(row.get("authenticationShare")) for row in rows]))
        + (0.16 * average([number(row.get("commentVolume")) for row in rows]) / 2500.0)
    )
    return max(0.0, min(1.0, value))


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0.0 else 0.0


def number(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def flag(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def procurement_award_key(row: dict[str, str]) -> str:
    for key in ("piid", "awardId"):
        value = row.get(key, "").strip()
        if value:
            return value
    return "|".join(
        [
            row.get("recipient", "").strip(),
            row.get("agency", "").strip(),
            row.get("actionDate", "").strip(),
        ]
    )


def has_competition_data(row: dict[str, str]) -> bool:
    competition_type = row.get("competitionType", "").strip().lower()
    return (
        number(row.get("numberOfOffers")) > 0.0
        or competition_type not in {"", "unknown", "nan", "none", "null"}
        or flag(row.get("priceOnlyAward"))
        or flag(row.get("exclusionFlag"))
    )


def has_modification_data(row: dict[str, str]) -> bool:
    return (
        row.get("modificationNumber", "").strip() != ""
        or row.get("exPostModification", "").strip() != ""
    )


def modification_sequence(value: object) -> int:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return 0
    match = re.search(r"(\d+)$", text)
    if match:
        return int(match.group(1))
    return int(number(text))


def competition_limited(value: object) -> bool:
    text = str(value or "").upper()
    return any(marker in text for marker in ("NOT COMPETED", "LIMITED", "SOLE SOURCE", "EXCLUSION"))


def moment(scope: str, source: str, metric: str, value: float | int, evidence_type: str, notes: str) -> dict[str, str]:
    return {
        "scope": scope,
        "source": source,
        "metric": metric,
        "value": f"{float(value):.4f}",
        "evidenceType": evidence_type,
        "notes": notes,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["scope", "source", "metric", "value", "evidenceType", "notes"]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Source Moments",
        "",
        "These are direct moments from normalized calibration tables. They are source diagnostics, not causal estimates.",
        "",
    ]
    warnings = representativeness_warnings(rows)
    if warnings:
        lines.extend(["## Representativeness Warnings", ""])
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend([
        "| Scope | Source | Metric | Value | Evidence | Notes |",
        "| --- | --- | --- | ---: | --- | --- |",
    ])
    for row in rows:
        lines.append(
            f"| {row['scope']} | {row['source']} | `{row['metric']}` | {row['value']} | {row['evidenceType']} | {row['notes']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def representativeness_warnings(rows: list[dict[str, str]]) -> list[str]:
    warnings: list[str] = []
    lda_rows = metric_value(rows, "snapshot", "lda", "ldaRows")
    if lda_rows < 50:
        warnings.append(
            f"Snapshot LDA row count is {lda_rows:.0f}; treat LDA concentration and disclosure-lag moments as smoke-test diagnostics."
        )
    for metric_name in ("lobbyingClientTop1Share", "lobbyingClientTop3Share", "lobbyingRegistrantTop3Share"):
        value = metric_value(rows, "snapshot", "lda", metric_name)
        if value >= 0.95:
            warnings.append(
                f"Snapshot `{metric_name}` is {value:.4f}; this usually indicates a very narrow or incomplete LDA slice."
            )
    fec_rows = metric_value(rows, "snapshot", "fec", "fecRows")
    if fec_rows < 500:
        warnings.append(
            f"Snapshot FEC row count is {fec_rows:.0f}; use FEC moments as panel diagnostics rather than representative election-cycle estimates."
        )
    if metric_value(rows, "snapshot", "fec", "darkMoneyDirectRoutingRows") == 0.0:
        warnings.append("Snapshot campaign-finance rows contain no non-proxy direct DARK_MONEY routing rows; dark-money calibration still depends on benchmark and scenario assumptions even though opaque-capacity and outside-spending rows are present.")
    if metric_value(rows, "snapshot", "fec", "outsideSpendingRows") == 0.0:
        warnings.append("Snapshot campaign-finance rows contain no Schedule E or outside-spending bridge rows; substitution through outside spending remains weakly anchored.")
    if metric_value(rows, "snapshot", "fec", "electoralCommunicationRows") == 0.0:
        warnings.append("Snapshot campaign-finance rows contain no OpenFEC electioneering or communication-cost rows; electoral communication channels are parser-ready but not yet represented in the pinned snapshot.")
    if metric_value(rows, "snapshot", "fec", "publicFinancingRows") == 0.0:
        warnings.append("Snapshot campaign-finance rows contain no public-match or democracy-voucher bridge rows; public-financing calibration still depends on external benchmarks.")
    revolving_rows = metric_value(rows, "snapshot", "revolving-door", "revolvingDoorRows")
    if revolving_rows <= 10:
        warnings.append(
            f"Snapshot revolving-door row count is {revolving_rows:.0f}; replace the fixture/export stub before using revolving-door moments as empirical anchors."
        )
    if metric_value(rows, "snapshot", "revolving-door", "revolvingDoorFixtureShare") > 0.0:
        warnings.append(
            "Snapshot revolving-door rows are tracked fixtures; they support schema and mechanism tests, not empirical calibration."
        )
    intermediary_rows = metric_value(rows, "snapshot", "intermediary", "intermediaryRows")
    if intermediary_rows <= 0:
        warnings.append(
            "Think-tank, association, and sponsored-expert intermediary routing is modeled but not yet anchored by a direct public-data panel."
        )
    elif metric_value(rows, "snapshot", "intermediary", "intermediaryDonorDisclosureMean") < 0.50:
        warnings.append(
            "Snapshot intermediary donor/source disclosure is low; hidden-routing claims should remain source-diagnostic rather than causal."
        )
    oira_rows = metric_value(rows, "snapshot", "oira-meetings", "oiraMeetingRows")
    if oira_rows <= 0:
        warnings.append(
            "Snapshot contains no Reginfo.gov EO 12866 meeting rows; meeting-disclosure and public-access concentration remain unanchored."
        )
    elif metric_value(rows, "snapshot", "oira-meetings", "oiraMeetingClientDisclosureShare") < 0.50:
        warnings.append(
            "Snapshot EO 12866 meeting rows have limited requestor-client disclosure coverage; access-channel diagnostics should remain source-bounded."
        )
    if metric_value(rows, "snapshot", "usaspending", "procurementKnownUeiShare") < 0.50:
        warnings.append(
            "Snapshot procurement rows have weak UEI coverage; procurement-network validation should be treated as incomplete."
        )
    if metric_value(rows, "snapshot", "usaspending", "procurementKnownPiidShare") < 0.50:
        warnings.append(
            "Snapshot procurement rows have weak PIID coverage; SAM/FPDS-style bridge diagnostics remain incomplete."
        )
    if metric_value(rows, "snapshot", "usaspending-bulk", "procurementActionPanelBulkSample") >= 0.5:
        bulk_rows = metric_value(rows, "snapshot", "usaspending-bulk", "procurementBulkTransactionRows")
        warnings.append(
            f"Snapshot procurement uses an archived USAspending bulk transaction summary ({bulk_rows:.0f} rows) as the preferred public denominator; remaining procurement evidence work is SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, and causal calibration rather than bulk acquisition."
        )
    elif metric_value(rows, "snapshot", "sam", "procurementActionPanelSamSample") >= 0.5:
        warnings.append(
            "Snapshot procurement concentration uses SAM.gov Contract Awards rows; this is stronger source provenance than the top-award bridge but remains a bounded diagnostic rather than a representative SAM/FPDS panel."
        )
    elif metric_value(rows, "snapshot", "usaspending", "procurementConcentrationPanelNationalVolumeSample") >= 0.5:
        national_rows = metric_value(rows, "snapshot", "usaspending", "procurementNationalActionRows")
        warnings.append(
            f"Snapshot procurement concentration uses a national-volume no-agency-filtered USAspending transaction/action panel ({national_rows:.0f} rows); this is stronger for concentration than the balanced action panel, but the benchmark still needs denominator and SAM/FPDS coding reconciliation."
        )
    elif metric_value(rows, "snapshot", "usaspending", "procurementConcentrationPanelActionSample") >= 0.5:
        action_rows = metric_value(rows, "snapshot", "usaspending", "procurementActionRows")
        warnings.append(
            f"Snapshot procurement concentration uses an expanded stratified multi-agency USAspending transaction/action panel ({action_rows:.0f} rows); this is stronger than the top-award bridge but remains a bounded diagnostic rather than a representative SAM/FPDS panel."
        )
    elif metric_value(rows, "snapshot", "usaspending", "procurementConcentrationPanelTopAwardSample") >= 0.5:
        warnings.append(
            "Snapshot procurement concentration uses a multi-agency top-award bridge; this improves agency coverage but remains a sampling diagnostic rather than a representative SAM/FPDS panel."
        )
    action_rows = metric_value(rows, "snapshot", "usaspending", "procurementActionRows")
    bulk_rows = metric_value(rows, "snapshot", "usaspending-bulk", "procurementActionRows")
    active_rows = bulk_rows if bulk_rows > 0 else action_rows
    if metric_value(rows, "snapshot", "usaspending", "procurementLatestTransactionModificationProxy") >= 0.5 and active_rows <= 0:
        warnings.append(
            "Snapshot procurement latest-transaction modification enrichment is available, but modification incidence is reported from the award/action panel or bulk summary; denominator mapping is handled separately from SAM/FPDS coding and causal calibration."
        )
    if active_rows <= 0 and metric_value(rows, "snapshot", "usaspending", "procurementInitialAwardShare") >= 0.95 and metric_value(rows, "snapshot", "usaspending", "procurementExPostModificationShare") <= 0.05:
        warnings.append(
            "Snapshot procurement modification incidence is dominated by initial-award rows; use it as a coverage warning rather than an observed national modification rate."
        )
    if metric_value(rows, "snapshot", "usaspending", "procurementExPostModificationShare") >= 0.95 and metric_value(rows, "snapshot", "usaspending", "procurementInitialAwardShare") <= 0.05:
        warnings.append(
            "Snapshot procurement rows are dominated by post-award modification transactions; award and modification effects should be reported separately."
        )
    action_mod_share = metric_value(rows, "snapshot", "usaspending-bulk", "procurementExPostModificationShare") or metric_value(rows, "snapshot", "usaspending", "procurementExPostModificationShare")
    award_mod_share = metric_value(rows, "snapshot", "usaspending-bulk", "procurementModifiedAwardShare") or metric_value(rows, "snapshot", "usaspending", "procurementModifiedAwardShare")
    amount_mod_share = metric_value(rows, "snapshot", "usaspending-bulk", "procurementAmountWeightedModificationShare") or metric_value(rows, "snapshot", "usaspending", "procurementAmountWeightedModificationShare")
    if active_rows > 0 and award_mod_share > 0.0 and abs(action_mod_share - award_mod_share) >= 0.05:
        warnings.append(
            f"Snapshot procurement modification incidence differs by denominator: action-row share {action_mod_share:.4f}, distinct-award share {award_mod_share:.4f}, and amount-weighted share {amount_mod_share:.4f}; the benchmark crosswalk keeps these denominators separate while SAM/FPDS coding and causal calibration remain future evidence work."
        )
    return warnings


def metric_value(rows: list[dict[str, str]], scope: str, source: str, metric_name: str) -> float:
    for row in rows:
        if row["scope"] == scope and row["source"] == source and row["metric"] == metric_name:
            return number(row["value"])
    return 0.0


def is_dark_money_capacity_proxy(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("committeeType", ""),
            row.get("spendingPurpose", ""),
            row.get("sourceUrl", ""),
        ]
    ).lower()
    return "capacity proxy" in text or ("eo_" in text and "irs-soi" in text)


if __name__ == "__main__":
    raise SystemExit(main())
