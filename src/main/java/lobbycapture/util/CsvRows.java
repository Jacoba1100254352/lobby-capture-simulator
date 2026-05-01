package lobbycapture.util;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class CsvRows {
    private CsvRows() {
    }

    public static List<Map<String, String>> read(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path).stream()
                .filter(line -> !line.isBlank())
                .filter(line -> !line.stripLeading().startsWith("#"))
                .toList();
        if (lines.isEmpty()) {
            return List.of();
        }
        List<String> headers = parse(lines.get(0));
        List<Map<String, String>> rows = new ArrayList<>();
        for (String line : lines.subList(1, lines.size())) {
            List<String> values = parse(line);
            Map<String, String> row = new LinkedHashMap<>();
            for (int index = 0; index < headers.size(); index++) {
                row.put(headers.get(index), index < values.size() ? values.get(index) : "");
            }
            rows.add(Map.copyOf(row));
        }
        return List.copyOf(rows);
    }

    private static List<String> parse(String line) {
        List<String> values = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean inQuotes = false;
        for (int index = 0; index < line.length(); index++) {
            char character = line.charAt(index);
            if (character == '"') {
                if (inQuotes && index + 1 < line.length() && line.charAt(index + 1) == '"') {
                    current.append('"');
                    index++;
                } else {
                    inQuotes = !inQuotes;
                }
            } else if (character == ',' && !inQuotes) {
                values.add(current.toString());
                current.setLength(0);
            } else {
                current.append(character);
            }
        }
        values.add(current.toString());
        return values;
    }
}

