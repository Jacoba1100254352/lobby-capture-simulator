package lobbycapture.network;

import lobbycapture.util.Values;

import java.util.List;

public record InfluenceNetworkSnapshot(
        double pathWeight,
        double networkOpacityIndex,
        double donorNetworkConcentration,
        double intermediaryCentrality,
        double officialAccessCentrality,
        double procurementNetworkExposure,
        double revolvingDoorBridgeIndex,
        double commentNetworkLoad,
        double venueShiftNetworkLoad,
        double networkLegibilityIndex
) {
    public InfluenceNetworkSnapshot {
        Values.requireRange("pathWeight", pathWeight, 0.0, 1_000_000.0);
        Values.requireRange("networkOpacityIndex", networkOpacityIndex, 0.0, 1.0);
        Values.requireRange("donorNetworkConcentration", donorNetworkConcentration, 0.0, 1.0);
        Values.requireRange("intermediaryCentrality", intermediaryCentrality, 0.0, 1.0);
        Values.requireRange("officialAccessCentrality", officialAccessCentrality, 0.0, 1.0);
        Values.requireRange("procurementNetworkExposure", procurementNetworkExposure, 0.0, 1.0);
        Values.requireRange("revolvingDoorBridgeIndex", revolvingDoorBridgeIndex, 0.0, 1.0);
        Values.requireRange("commentNetworkLoad", commentNetworkLoad, 0.0, 1.0);
        Values.requireRange("venueShiftNetworkLoad", venueShiftNetworkLoad, 0.0, 1.0);
        Values.requireRange("networkLegibilityIndex", networkLegibilityIndex, 0.0, 1.0);
    }

    public static InfluenceNetworkSnapshot zero() {
        return new InfluenceNetworkSnapshot(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0);
    }

    public static InfluenceNetworkSnapshot fromPaths(List<InfluenceNetworkPath> paths) {
        double weight = paths.stream().mapToDouble(InfluenceNetworkPath::weight).sum();
        if (weight <= 0.0) {
            return zero();
        }
        double opacity = weighted(paths, weight, InfluenceNetworkPath::opacity);
        return new InfluenceNetworkSnapshot(
                weight,
                opacity,
                weighted(paths, weight, InfluenceNetworkPath::donorConcentration),
                weighted(paths, weight, InfluenceNetworkPath::intermediaryDependence),
                weighted(paths, weight, InfluenceNetworkPath::officialAccess),
                weighted(paths, weight, InfluenceNetworkPath::procurementLink),
                weighted(paths, weight, InfluenceNetworkPath::revolvingDoorLink),
                weighted(paths, weight, InfluenceNetworkPath::commentMobilization),
                weighted(paths, weight, InfluenceNetworkPath::venueShift),
                Values.clamp(1.0 - opacity, 0.0, 1.0)
        );
    }

    private static double weighted(List<InfluenceNetworkPath> paths, double weight, PathMetric metric) {
        return Values.clamp(
                paths.stream().mapToDouble(path -> path.weight() * metric.value(path)).sum() / weight,
                0.0,
                1.0
        );
    }

    @FunctionalInterface
    private interface PathMetric {
        double value(InfluenceNetworkPath path);
    }
}
