package lobbycapture.calibration;


public record RevolvingDoorRecord(
		String person,
		String organization,
		String sector,
		String agency,
		boolean formerOfficial,
		double coolingOffMonths,
		double influenceShare,
		double confidence
)
{
}
