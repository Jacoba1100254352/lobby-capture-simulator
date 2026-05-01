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
            if (Files.exists(lda) && Files.exists(fec) && Files.exists(dockets)) {
                return new CalibrationProfile(readLda(lda), readFec(fec), readDockets(dockets));
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

    private static double parse(Map<String, String> row, String key) {
        String value = row.get(key);
        if (value == null || value.isBlank()) {
            return 0.0;
        }
        return Double.parseDouble(value);
    }
}

