package lobbycapture.reporting;

import java.time.Instant;

public record ReportProvenance(long seed, int runs, int contestsPerRun, Instant generatedAt) {
    public static ReportProvenance now(long seed, int runs, int contestsPerRun) {
        return new ReportProvenance(seed, runs, contestsPerRun, Instant.now());
    }
}

