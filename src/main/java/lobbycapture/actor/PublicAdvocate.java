package lobbycapture.actor;

import lobbycapture.util.Values;

public record PublicAdvocate(String id, double budget, double expertise, double credibility, double litigationCapacity) {
    public PublicAdvocate {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        Values.requireRange("budget", budget, 0.0, 1.0);
        Values.requireRange("expertise", expertise, 0.0, 1.0);
        Values.requireRange("credibility", credibility, 0.0, 1.0);
        Values.requireRange("litigationCapacity", litigationCapacity, 0.0, 1.0);
    }
}

