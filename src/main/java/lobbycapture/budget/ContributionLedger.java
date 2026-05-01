package lobbycapture.budget;

import lobbycapture.util.Gini;

import java.util.ArrayList;
import java.util.List;

public final class ContributionLedger {
    private final List<MoneyFlow> flows = new ArrayList<>();

    public void add(MoneyFlow flow) {
        flows.add(flow);
    }

    public List<MoneyFlow> flows() {
        return List.copyOf(flows);
    }

    public double totalAmount() {
        return flows.stream().mapToDouble(MoneyFlow::amount).sum();
    }

    public double darkMoneyShare() {
        double total = totalAmount();
        if (total == 0.0) {
            return 0.0;
        }
        double dark = flows.stream()
                .filter(flow -> flow.flowType() == FundingSource.DARK_MONEY)
                .mapToDouble(MoneyFlow::amount)
                .sum();
        return dark / total;
    }

    public double averageTraceability() {
        double total = totalAmount();
        if (total == 0.0) {
            return 0.0;
        }
        return flows.stream().mapToDouble(flow -> flow.amount() * flow.traceability()).sum() / total;
    }

    public double donorInfluenceGini() {
        return Gini.of(flows.stream().map(MoneyFlow::amount).toList());
    }
}

