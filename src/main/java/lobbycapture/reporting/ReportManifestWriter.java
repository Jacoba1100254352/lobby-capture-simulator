package lobbycapture.reporting;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HexFormat;
import java.util.List;

public final class ReportManifestWriter {
    private static final List<String> GENERATED_STATUS_PREFIXES = List.of(
            "reports/",
            "paper/tables/",
            "paper/figures/",
            "data/snapshots/2024-env/"
    );

    private ReportManifestWriter() {
    }

    public static void write(
            Path reportsDir,
            String baseName,
            String command,
            ReportProvenance provenance,
            List<String> reportFiles
    ) throws IOException {
        Files.createDirectories(reportsDir);
        StringBuilder builder = new StringBuilder();
        builder.append("{\n");
        append(builder, "report", baseName, true);
        append(builder, "generatedAt", provenance.generatedAt().toString(), true);
        append(builder, "seed", Long.toString(provenance.seed()), false, true);
        append(builder, "runs", Integer.toString(provenance.runs()), false, true);
        append(builder, "contestsPerRun", Integer.toString(provenance.contestsPerRun()), false, true);
        append(builder, "command", command, true);
        append(builder, "gitCommit", git("rev-parse", "--short", "HEAD"), true);
        append(builder, "workingTreeDirty", Boolean.toString(!sourceStatus().isBlank()), false, true);
        append(builder, "workingTreeDirtyScope", "tracked status excluding generated reports, paper tables, paper figures, and 2024-env snapshot outputs", true);
        append(builder, "javaVersion", System.getProperty("java.version"), true);
        append(builder, "calibrationChecksum", checksumDirectory(Path.of("data", "raw")), true);
        appendArray(builder, "reportFiles", reportFiles);
        builder.append("}\n");
        Files.writeString(reportsDir.resolve(baseName + ".manifest.json"), builder.toString(), StandardCharsets.UTF_8);
    }

    private static void append(StringBuilder builder, String key, String value, boolean comma) {
        append(builder, key, value, true, comma);
    }

    private static void append(StringBuilder builder, String key, String value, boolean quoteValue, boolean comma) {
        builder.append("  \"").append(escape(key)).append("\": ");
        if (quoteValue) {
            builder.append("\"").append(escape(value)).append("\"");
        } else {
            builder.append(value);
        }
        if (comma) {
            builder.append(',');
        }
        builder.append('\n');
    }

    private static void appendArray(StringBuilder builder, String key, List<String> values) {
        builder.append("  \"").append(escape(key)).append("\": [");
        for (int index = 0; index < values.size(); index++) {
            if (index > 0) {
                builder.append(", ");
            }
            builder.append("\"").append(escape(values.get(index))).append("\"");
        }
        builder.append("]\n");
    }

    private static String git(String... args) {
        try {
            List<String> command = new ArrayList<>();
            command.add("git");
            command.addAll(List.of(args));
            Process process = new ProcessBuilder(command)
                    .redirectErrorStream(true)
                    .start();
            String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            int status = process.waitFor();
            return status == 0 ? output.trim() : "unknown";
        } catch (IOException exception) {
            return "unknown";
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            return "unknown";
        }
    }

    private static String sourceStatus() {
        String status = git("status", "--porcelain");
        if ("unknown".equals(status)) {
            return status;
        }
        StringBuilder dirty = new StringBuilder();
        for (String line : status.split("\\R")) {
            if (line.isBlank()) {
                continue;
            }
            String path = line.length() > 3 ? line.substring(3) : line;
            if (path.contains(" -> ")) {
                path = path.substring(path.indexOf(" -> ") + 4);
            }
            if (isGeneratedPath(path)) {
                continue;
            }
            dirty.append(line).append('\n');
        }
        return dirty.toString();
    }

    private static boolean isGeneratedPath(String path) {
        for (String prefix : GENERATED_STATUS_PREFIXES) {
            if (path.equals(prefix.substring(0, prefix.length() - 1)) || path.startsWith(prefix)) {
                return true;
            }
        }
        return false;
    }

    private static String checksumDirectory(Path directory) throws IOException {
        if (!Files.exists(directory)) {
            return "missing";
        }
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            List<Path> files;
            try (var stream = Files.walk(directory)) {
                files = stream
                        .filter(Files::isRegularFile)
                        .sorted(Comparator.comparing(Path::toString))
                        .toList();
            }
            for (Path file : files) {
                digest.update(directory.relativize(file).toString().getBytes(StandardCharsets.UTF_8));
                digest.update((byte) 0);
                digest.update(Files.readAllBytes(file));
                digest.update((byte) 0);
            }
            return HexFormat.of().formatHex(digest.digest());
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is unavailable.", exception);
        }
    }

    private static String escape(String value) {
        return value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n");
    }
}
