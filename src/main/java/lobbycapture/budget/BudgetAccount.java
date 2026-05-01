package lobbycapture.budget;

import lobbycapture.util.Values;

public final class BudgetAccount {
    private double balance;

    public BudgetAccount(double openingBalance) {
        Values.requireRange("openingBalance", openingBalance, 0.0, 1_000_000.0);
        this.balance = openingBalance;
    }

    public double balance() {
        return balance;
    }

    public double spend(double requested) {
        Values.requireRange("requested", requested, 0.0, 1_000_000.0);
        double spent = Math.min(balance, requested);
        balance -= spent;
        return spent;
    }

    public void deposit(double amount) {
        Values.requireRange("amount", amount, 0.0, 1_000_000.0);
        balance += amount;
    }
}

