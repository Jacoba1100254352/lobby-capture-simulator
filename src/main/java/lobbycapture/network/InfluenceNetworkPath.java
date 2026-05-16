package lobbycapture.network;


import lobbycapture.strategy.InfluenceChannel;
import lobbycapture.util.Values;


public record InfluenceNetworkPath(
		String sourceId,
		String targetDomain,
		InfluenceChannel channel,
		double weight,
		double opacity,
		double donorConcentration,
		double intermediaryDependence,
		double officialAccess,
		double procurementLink,
		double revolvingDoorLink,
		double commentMobilization,
		double venueShift
)
{
	public InfluenceNetworkPath {
		requireText("sourceId", sourceId);
		requireText("targetDomain", targetDomain);
		if (channel == null) {
			throw new IllegalArgumentException("channel must not be null.");
		}
		Values.requireRange("weight", weight, 0.0, 1_000_000.0);
		Values.requireRange("opacity", opacity, 0.0, 1.0);
		Values.requireRange("donorConcentration", donorConcentration, 0.0, 1.0);
		Values.requireRange("intermediaryDependence", intermediaryDependence, 0.0, 1.0);
		Values.requireRange("officialAccess", officialAccess, 0.0, 1.0);
		Values.requireRange("procurementLink", procurementLink, 0.0, 1.0);
		Values.requireRange("revolvingDoorLink", revolvingDoorLink, 0.0, 1.0);
		Values.requireRange("commentMobilization", commentMobilization, 0.0, 1.0);
		Values.requireRange("venueShift", venueShift, 0.0, 1.0);
	}
	
	private static void requireText(String name, String value) {
		if (value == null || value.isBlank()) {
			throw new IllegalArgumentException(name + " must not be blank.");
		}
	}
}
