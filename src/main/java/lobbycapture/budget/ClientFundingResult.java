package lobbycapture.budget;


public record ClientFundingResult(
		double totalFunding,
		double donorInfluenceGini,
		double averageDisclosureLag,
		double lobbyingDisclosureLag,
		double campaignDisclosureLag
)
{
}
