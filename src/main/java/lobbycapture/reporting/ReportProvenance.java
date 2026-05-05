package lobbycapture.reporting;

import java.time.Instant;
import java.time.format.DateTimeParseException;

public record ReportProvenance(long seed, int runs, int contestsPerRun, Instant generatedAt) {
    public static ReportProvenance now(long seed, int runs, int contestsPerRun) {
        return new ReportProvenance(seed, runs, contestsPerRun, resolveGeneratedAt());
    }

    private static Instant resolveGeneratedAt() {
        String configuredTimestamp = System.getenv("LOBBY_CAPTURE_REPORT_TIMESTAMP");
        if (configuredTimestamp != null && !configuredTimestamp.isBlank()) {
            try {
                return Instant.parse(configuredTimestamp);
            } catch (DateTimeParseException exception) {
                throw new IllegalArgumentException(
                        "LOBBY_CAPTURE_REPORT_TIMESTAMP must be an ISO-8601 instant.",
                        exception
                );
            }
        }

        String sourceDateEpoch = System.getenv("SOURCE_DATE_EPOCH");
        if (sourceDateEpoch != null && !sourceDateEpoch.isBlank()) {
            try {
                return Instant.ofEpochSecond(Long.parseLong(sourceDateEpoch));
            } catch (NumberFormatException exception) {
                throw new IllegalArgumentException(
                        "SOURCE_DATE_EPOCH must be an integer epoch-second timestamp.",
                        exception
                );
            }
        }

        return Instant.now();
    }
}
