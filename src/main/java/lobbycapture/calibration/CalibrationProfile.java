package lobbycapture.calibration;

import lobbycapture.budget.FundingSource;
import lobbycapture.policy.Docket;
import lobbycapture.util.Values;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public record CalibrationProfile(
        List<LdaRecord> ldaRecords,
        List<FecRecord> fecRecords,
        List<RegulatoryDocketRecord> docketRecords,
        List<ProcurementAwardRecord> procurementRecords,
        List<IntermediaryRecord> intermediaryRecords,
        List<RevolvingDoorRecord> revolvingDoorRecords
) {
    public CalibrationProfile {
        ldaRecords = List.copyOf(ldaRecords);
        fecRecords = List.copyOf(fecRecords);
        docketRecords = List.copyOf(docketRecords);
        procurementRecords = List.copyOf(procurementRecords);
        intermediaryRecords = List.copyOf(intermediaryRecords);
        revolvingDoorRecords = List.copyOf(revolvingDoorRecords);
    }

    public static CalibrationProfile embedded() {
        return new CalibrationProfile(
                List.of(
                        new LdaRecord("Energy Producers Association", "Energy Trade Council", "energy", 7.8, 0.55, 0.24),
                        new LdaRecord("Platform Operators Coalition", "Digital Platform Coalition", "technology", 8.2, 0.48, 0.18),
                        new LdaRecord("Financial Markets Roundtable", "Financial Markets Network", "finance", 9.1, 0.52, 0.31),
                        new LdaRecord("Federal Services Contractors", "Federal Contractor Alliance", "procurement", 5.4, 0.42, 0.27)
                ),
                List.of(
                        new FecRecord("Finance Leadership PAC", "incumbent-a", "finance", 6.8, FundingSource.PAC, 0.72, 0.84),
                        new FecRecord("Energy Independent Expenditure", "incumbent-a", "energy", 4.6, FundingSource.SUPER_PAC, 0.58, 0.76),
                        new FecRecord("Platform Civic Fund", "challenger-b", "technology", 3.9, FundingSource.DARK_MONEY, 0.24, 0.69),
                        new FecRecord("Small Donor Match Pool", "challenger-b", "democracy", 3.1, FundingSource.PUBLIC_MATCH, 0.96, 0.18),
                        new FecRecord("Voucher Participants", "challenger-b", "democracy", 2.4, FundingSource.DEMOCRACY_VOUCHER, 0.98, 0.08)
                ),
                List.of(
                        new RegulatoryDocketRecord("TECH-2026-001", "technology", "market-agency", 1800, 0.34, 0.52, 0.46, 0.28),
                        new RegulatoryDocketRecord("ENERGY-2026-004", "energy", "safety-agency", 1420, 0.42, 0.44, 0.52, 0.34),
                        new RegulatoryDocketRecord("FIN-2026-002", "finance", "market-agency", 960, 0.30, 0.58, 0.41, 0.22),
                        new RegulatoryDocketRecord("PROC-2026-003", "procurement", "market-agency", 410, 0.46, 0.38, 0.56, 0.40)
                ),
                List.of(
                        new ProcurementAwardRecord("EPA-ENV-001", "CDM Federal Programs Corporation", "procurement", 240.0, 4.0, false, false, true, true, true),
                        new ProcurementAwardRecord("EPA-ENV-002", "Environmental Systems Research Institute", "procurement", 180.0, 1.0, true, true, false, true, true),
                        new ProcurementAwardRecord("EPA-ENV-003", "Clean Water Engineering Partners", "procurement", 150.0, 3.0, false, true, true, true, true),
                        new ProcurementAwardRecord("EPA-ENV-004", "Regional Remediation Services", "procurement", 70.0, 2.0, false, false, true, true, true),
                        new ProcurementAwardRecord("EPA-ENV-005", "Public Comment Technology Cooperative", "procurement", 60.0, 1.0, true, true, false, true, true)
                ),
                List.of(
                        new IntermediaryRecord("Clean Energy Policy Institute", "501(c)(3)", "energy", 18.5, 0.0, 4.2, 0.82),
                        new IntermediaryRecord("Platform Future Association", "501(c)(6)", "technology", 42.0, 3.8, 7.4, 0.28),
                        new IntermediaryRecord("Market Structure Action Fund", "527", "finance", 12.2, 9.6, 1.1, 0.66),
                        new IntermediaryRecord("Infrastructure Procurement Council", "501(c)(6)", "procurement", 25.6, 2.7, 5.3, 0.34),
                        new IntermediaryRecord("Citizens Climate Messaging Fund", "501(c)(4)", "energy", 30.1, 6.8, 3.9, 0.18)
                ),
                List.of(
                        new RevolvingDoorRecord("Alex Morgan", "Energy Policy Advisors", "energy", "Environmental Protection Agency", true, 8.0, 0.72, 0.72),
                        new RevolvingDoorRecord("Blair Chen", "Federal Contractor Alliance", "procurement", "Environmental Protection Agency", true, 14.0, 0.61, 0.67),
                        new RevolvingDoorRecord("Casey Rivera", "Clean Air Industry Council", "energy", "Environmental Protection Agency", true, 6.0, 0.66, 0.70),
                        new RevolvingDoorRecord("Emerson Brooks", "Market Rules Forum", "finance", "Securities and Exchange Commission", false, 36.0, 0.31, 0.46)
                )
        );
    }

    public double issueFundingScale(String issueDomain) {
        double average = ldaRecords.stream().mapToDouble(LdaRecord::amount).average().orElse(1.0);
        double issueAverage = ldaRecords.stream()
                .filter(record -> record.issueDomain().equals(issueDomain))
                .mapToDouble(LdaRecord::amount)
                .average()
                .orElse(average);
        return Values.clamp(issueAverage / Math.max(0.01, average), 0.45, 1.85);
    }

    public double disclosureLag(String issueDomain) {
        return ldaRecords.stream()
                .filter(record -> record.issueDomain().equals(issueDomain))
                .mapToDouble(LdaRecord::disclosureLag)
                .average()
                .orElse(0.45);
    }

    public double largeDonorShare(String issueDomain) {
        return fecRecords.stream()
                .filter(record -> record.issueDomain().equals(issueDomain) || record.issueDomain().equals("democracy"))
                .mapToDouble(FecRecord::largeDonorShare)
                .average()
                .orElse(0.50);
    }

    public double averageTraceability(String issueDomain) {
        return fecRecords.stream()
                .filter(record -> record.issueDomain().equals(issueDomain) || record.issueDomain().equals("democracy"))
                .mapToDouble(FecRecord::traceability)
                .average()
                .orElse(0.65);
    }

    public Docket docketFor(String issueDomain) {
        RegulatoryDocketRecord record = docketRecords.stream()
                .filter(docket -> docket.issueDomain().equals(issueDomain))
                .findFirst()
                .orElse(null);
        if (record == null) {
            return Docket.empty(issueDomain);
        }
        int genuine = (int) Math.round(record.commentVolume() * record.genuineShare());
        int template = (int) Math.round(record.commentVolume() * record.templateShare());
        int astroturf = Math.max(0, record.commentVolume() - genuine - template);
        return new Docket(
                record.docketId(),
                record.issueDomain(),
                record.agency(),
                genuine,
                template,
                astroturf,
                record.technicalClaimCredibility(),
                record.authenticationShare()
        );
    }

    public Map<String, Double> issueSpendShares() {
        double total = ldaRecords.stream().mapToDouble(LdaRecord::amount).sum();
        if (total == 0.0) {
            return Map.of();
        }
        return ldaRecords.stream().collect(Collectors.groupingBy(
                LdaRecord::issueDomain,
                Collectors.summingDouble(record -> record.amount() / total)
        ));
    }

    public double procurementBridgeRisk(String issueDomain) {
        List<ProcurementAwardRecord> records = procurementRecordsFor(issueDomain);
        if (records.isEmpty()) {
            return issueDomain.equals("procurement") ? 0.32 : 0.08;
        }
        double total = records.stream().mapToDouble(ProcurementAwardRecord::amount).sum();
        double top3Share = topShareByRecipient(records, total, 3);
        double singleBidShare = amountShare(records, total, record -> record.numberOfOffers() > 0.0 && record.numberOfOffers() <= 1.0);
        double modificationShare = amountShare(records, total, ProcurementAwardRecord::exPostModification);
        double priceOnlyShare = amountShare(records, total, ProcurementAwardRecord::priceOnlyAward);
        double firewallCoverage = amountShare(records, total, ProcurementAwardRecord::firewallCovered);
        return Values.clamp(
                (0.30 * top3Share)
                        + (0.24 * singleBidShare)
                        + (0.20 * modificationShare)
                        + (0.16 * priceOnlyShare)
                        + (0.10 * (1.0 - firewallCoverage)),
                0.0,
                1.0
        );
    }

    public double intermediaryOpacity(String issueDomain) {
        List<IntermediaryRecord> records = intermediaryRecordsFor(issueDomain);
        if (records.isEmpty()) {
            return 0.35;
        }
        double disclosure = records.stream().mapToDouble(IntermediaryRecord::donorDisclosure).average().orElse(0.50);
        return Values.clamp(1.0 - disclosure, 0.0, 1.0);
    }

    public double intermediaryPoliticalPressure(String issueDomain) {
        List<IntermediaryRecord> records = intermediaryRecordsFor(issueDomain);
        double revenue = records.stream().mapToDouble(IntermediaryRecord::revenue).sum();
        if (revenue <= 0.0) {
            return 0.10;
        }
        double political = records.stream().mapToDouble(IntermediaryRecord::politicalSpend).sum();
        double grants = records.stream().mapToDouble(IntermediaryRecord::grantmaking).sum();
        return Values.clamp((political / revenue) + (0.35 * grants / revenue), 0.0, 1.0);
    }

    public double revolvingDoorSourcePressure(String issueDomain) {
        List<RevolvingDoorRecord> records = revolvingDoorRecordsFor(issueDomain);
        if (records.isEmpty()) {
            return 0.22;
        }
        double weightedInfluence = records.stream()
                .mapToDouble(record -> record.influenceShare() * record.confidence() * (record.formerOfficial() ? 1.0 : 0.45))
                .average()
                .orElse(0.0);
        double shortCooling = records.stream()
                .filter(record -> record.formerOfficial() && record.coolingOffMonths() < 12.0)
                .count() / (double) records.size();
        return Values.clamp((0.70 * weightedInfluence) + (0.30 * shortCooling), 0.0, 1.0);
    }

    private List<ProcurementAwardRecord> procurementRecordsFor(String issueDomain) {
        List<ProcurementAwardRecord> filtered = procurementRecords.stream()
                .filter(record -> record.issueDomain().equals(issueDomain))
                .toList();
        return filtered.isEmpty() && issueDomain.equals("procurement") ? procurementRecords : filtered;
    }

    private List<IntermediaryRecord> intermediaryRecordsFor(String issueDomain) {
        List<IntermediaryRecord> filtered = intermediaryRecords.stream()
                .filter(record -> record.issueDomain().equals(issueDomain))
                .toList();
        return filtered.isEmpty() ? intermediaryRecords : filtered;
    }

    private List<RevolvingDoorRecord> revolvingDoorRecordsFor(String issueDomain) {
        List<RevolvingDoorRecord> filtered = revolvingDoorRecords.stream()
                .filter(record -> record.sector().equals(issueDomain))
                .toList();
        return filtered.isEmpty() ? revolvingDoorRecords : filtered;
    }

    private static double topShareByRecipient(List<ProcurementAwardRecord> records, double total, int count) {
        if (total <= 0.0) {
            return 0.0;
        }
        Map<String, Double> byRecipient = records.stream().collect(Collectors.groupingBy(
                ProcurementAwardRecord::recipient,
                Collectors.summingDouble(ProcurementAwardRecord::amount)
        ));
        return byRecipient.values().stream()
                .sorted((left, right) -> Double.compare(right, left))
                .limit(count)
                .mapToDouble(Double::doubleValue)
                .sum() / total;
    }

    private static double amountShare(List<ProcurementAwardRecord> records, double total, ProcurementPredicate predicate) {
        if (total <= 0.0) {
            return 0.0;
        }
        return records.stream()
                .filter(predicate::matches)
                .mapToDouble(ProcurementAwardRecord::amount)
                .sum() / total;
    }

    @FunctionalInterface
    private interface ProcurementPredicate {
        boolean matches(ProcurementAwardRecord record);
    }
}
