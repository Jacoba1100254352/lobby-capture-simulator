package lobbycapture.calibration;

import lobbycapture.budget.FundingSource;
import lobbycapture.util.CsvRows;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

public final class CalibrationDataLoader {
    private CalibrationDataLoader() {
    }

    public static CalibrationProfile loadOrEmbedded(Path directory) {
        try {
            Path lda = directory.resolve("lda-lobbying.csv");
            Path fec = directory.resolve("fec-campaign-finance.csv");
            Path dockets = directory.resolve("regulatory-dockets.csv");
            Path procurement = directory.resolve("usaspending-awards.csv");
            Path revolvingDoor = directory.resolve("revolving-door.csv");
            Path intermediaries = directory.resolve("intermediaries.csv");
            if (Files.exists(lda) && Files.exists(fec) && Files.exists(dockets)) {
                return new CalibrationProfile(
                        readLda(lda),
                        readFec(fec),
                        readDockets(dockets),
                        Files.exists(procurement) ? readProcurement(procurement) : List.of(),
                        Files.exists(intermediaries) ? readIntermediaries(intermediaries) : List.of(),
                        Files.exists(revolvingDoor) ? readRevolvingDoor(revolvingDoor) : List.of()
                );
            }
        } catch (IOException exception) {
            throw new IllegalStateException("Unable to load calibration data from " + directory, exception);
        }
        return CalibrationProfile.embedded();
    }

    public static List<LdaRecord> readLda(Path path) throws IOException {
        return CsvRows.read(path).stream()
                .map(row -> new LdaRecord(
                        row.get("client"),
                        row.get("registrant"),
                        row.get("issueDomain"),
                        parse(row, "amount"),
                        parse(row, "disclosureLag"),
                        parse(row, "coveredOfficialShare")
                ))
                .toList();
    }

    public static List<FecRecord> readFec(Path path) throws IOException {
        return CsvRows.read(path).stream()
                .map(row -> new FecRecord(
                        row.get("source"),
                        row.get("recipient"),
                        row.get("issueDomain"),
                        parse(row, "amount"),
                        FundingSource.valueOf(row.get("flowType")),
                        parse(row, "traceability"),
                        parse(row, "largeDonorShare")
                ))
                .toList();
    }

    public static List<RegulatoryDocketRecord> readDockets(Path path) throws IOException {
        return CsvRows.read(path).stream()
                .map(row -> new RegulatoryDocketRecord(
                        row.get("docketId"),
                        row.get("issueDomain"),
                        row.get("agency"),
                        (int) parse(row, "commentVolume"),
                        parse(row, "genuineShare"),
                        parse(row, "templateShare"),
                        parse(row, "technicalClaimCredibility"),
                        parse(row, "authenticationShare")
                ))
                .toList();
    }

    public static List<ProcurementAwardRecord> readProcurement(Path path) throws IOException {
        return CsvRows.read(path).stream()
                .map(row -> new ProcurementAwardRecord(
                        row.get("awardId"),
                        row.get("recipient"),
                        row.get("issueDomain"),
                        parse(row, "amount"),
                        parse(row, "numberOfOffers"),
                        flag(row.get("priceOnlyAward")),
                        flag(row.get("exPostModification")) || parse(row, "modificationNumber") > 0.0,
                        flag(row.get("firewallCovered")),
                        present(row.get("uei")),
                        present(row.get("piid"))
                ))
                .toList();
    }

    public static List<IntermediaryRecord> readIntermediaries(Path path) throws IOException {
        return CsvRows.read(path).stream()
                .map(row -> new IntermediaryRecord(
                        row.get("organization"),
                        row.get("subsection"),
                        row.get("issueDomain"),
                        parse(row, "revenue"),
                        parse(row, "politicalSpend"),
                        parse(row, "grantmaking"),
                        parse(row, "donorDisclosure")
                ))
                .toList();
    }

    public static List<RevolvingDoorRecord> readRevolvingDoor(Path path) throws IOException {
        return CsvRows.read(path).stream()
                .map(row -> new RevolvingDoorRecord(
                        row.get("person"),
                        row.get("organization"),
                        row.get("sector"),
                        row.get("agency"),
                        present(row.get("formerOfficialRole")),
                        parse(row, "coolingOffMonths"),
                        parse(row, "influenceShare"),
                        parse(row, "confidence")
                ))
                .toList();
    }

    private static double parse(Map<String, String> row, String key) {
        String value = row.get(key);
        if (value == null || value.isBlank()) {
            return 0.0;
        }
        return Double.parseDouble(value);
    }

    private static boolean flag(String value) {
        return value != null && List.of("1", "true", "yes", "y").contains(value.trim().toLowerCase());
    }

    private static boolean present(String value) {
        return value != null && !value.isBlank();
    }
}
