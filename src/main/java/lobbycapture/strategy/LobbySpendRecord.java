package lobbycapture.strategy;

public record LobbySpendRecord(
        String lobbyId,
        InfluenceStrategy strategy,
        double spend,
        double preference,
        boolean defensive
) {
}

