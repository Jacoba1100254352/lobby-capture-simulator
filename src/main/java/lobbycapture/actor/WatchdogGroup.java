package lobbycapture.actor;

import lobbycapture.util.Values;

public record WatchdogGroup(String id, double investigativeCapacity, double publicReach, double enforcementReferralSkill) {
    public WatchdogGroup {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        Values.requireRange("investigativeCapacity", investigativeCapacity, 0.0, 1.0);
        Values.requireRange("publicReach", publicReach, 0.0, 1.0);
        Values.requireRange("enforcementReferralSkill", enforcementReferralSkill, 0.0, 1.0);
    }
}

