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
        List<RegulatoryDocketRecord> docketRecords
) {
    public CalibrationProfile {
        ldaRecords = List.copyOf(ldaRecords);
        fecRecords = List.copyOf(fecRecords);
        docketRecords = List.copyOf(docketRecords);
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
}

