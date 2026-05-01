package lobbycapture.budget;

import lobbycapture.util.Gini;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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

    public double darkMoneyDirectVisibility() {
        double darkTotal = flows.stream()
                .filter(flow -> flow.flowType() == FundingSource.DARK_MONEY || flow.flowType() == FundingSource.SUPER_PAC)
                .mapToDouble(MoneyFlow::amount)
                .sum();
        if (darkTotal == 0.0) {
            return 0.0;
        }
        return flows.stream()
                .filter(flow -> flow.flowType() == FundingSource.DARK_MONEY || flow.flowType() == FundingSource.SUPER_PAC)
                .mapToDouble(flow -> flow.amount() * flow.traceability())
                .sum() / darkTotal;
    }

    public double largeDonorDependence() {
        double total = totalAmount();
        if (total == 0.0) {
            return 0.0;
        }
        return flows.stream().mapToDouble(flow -> flow.amount() * flow.coordinationRisk()).sum() / total;
    }

    public double publicFinancingSourceShare() {
        double total = totalAmount();
        if (total == 0.0) {
            return 0.0;
        }
        double publicFunding = flows.stream()
                .filter(flow -> flow.flowType() == FundingSource.PUBLIC_MATCH || flow.flowType() == FundingSource.DEMOCRACY_VOUCHER)
                .mapToDouble(MoneyFlow::amount)
                .sum();
        return publicFunding / total;
    }

    public double donorInfluenceGini() {
        Map<String, Double> amountBySource = new HashMap<>();
        for (MoneyFlow flow : flows) {
            amountBySource.merge(flow.sourceId(), flow.amount(), Double::sum);
        }
        return Gini.of(amountBySource.values().stream().toList());
    }
}
