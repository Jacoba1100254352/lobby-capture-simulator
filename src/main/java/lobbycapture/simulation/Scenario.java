package lobbycapture.simulation;

public record Scenario(String key, String name, String description, WorldSpec worldSpec) {
    public Scenario {
        if (key == null || key.isBlank()) {
            throw new IllegalArgumentException("key must not be blank.");
        }
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name must not be blank.");
        }
        if (description == null || description.isBlank()) {
            throw new IllegalArgumentException("description must not be blank.");
        }
        if (worldSpec == null) {
            throw new IllegalArgumentException("worldSpec must not be null.");
        }
    }
}

