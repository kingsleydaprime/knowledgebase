package architecture;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class ArchitectureCheck {
    private ArchitectureCheck() {}

    private static String fixed(double x, int places) {
        return String.format(Locale.ROOT, "%." + places + "f", x);
    }

    public static void main(String[] args) {
        assert Architecture.coordinationLinks(4) == 6 && Architecture.coordinationLinks(8) == 28 && Architecture.coordinationLinks(50) == 1_225;
        assert fixed(Architecture.releaseBreaks(40, 0.01) * 100, 1).equals("33.1") && fixed(Architecture.releaseBreaks(5, 0.01) * 100, 1).equals("4.9");

        var chatty = Architecture.extract(40, 1, 0.9999);
        var coarse = Architecture.extract(1, 1, 0.9999);
        assert chatty.addedMs() == 40 && fixed(chatty.availability() * 100, 2).equals("99.60") : chatty;
        assert coarse.addedMs() == 1 && fixed(coarse.availability() * 100, 2).equals("99.99") : coarse;

        var price = new Architecture.Pricing(0.2, 0.0000166667);
        assert fixed(Architecture.serverlessMonthly(1_000_000, 200, 0.5, price), 2).equals("1.87");
        assert fixed(Architecture.serverlessMonthly(50_000_000, 200, 0.5, price), 2).equals("93.33");
        assert Math.round(Architecture.breakEvenRequests(30, 200, 0.5, price) / 1e5) / 10.0 == 16.1;

        List<String> cold = new ArrayList<>();
        for (double rate : new double[] {10, 1, 0.1}) cold.add(fixed(Architecture.coldShare(rate, 5) * 100, 2));
        assert cold.equals(List.of("0.00", "0.67", "60.65")) : cold;
        for (double rate : new double[] {1, 0.1}) {
            double sim = Architecture.simulateColdShare(rate, 5, 100_000, 7);
            assert Math.abs(sim - Architecture.coldShare(rate, 5)) < 0.005 : sim;
        }

        var customers = new ArrayList<String>();
        var shop = List.of(new Architecture.Module("orders", List.of("billing", "catalog/internal/prices")),
                new Architecture.Module("billing", List.of("customers")),
                new Architecture.Module("catalog", List.of("catalog/internal/prices")),
                new Architecture.Module("customers", customers));
        assert Architecture.boundaryViolations(shop).equals(List.of("orders → catalog/internal/prices"));
        assert Architecture.findCycle(shop).isEmpty();
        customers.add("orders");
        assert Architecture.findCycle(shop).orElseThrow().equals(List.of("orders", "billing", "customers", "orders"));
        System.out.println("all architecture checks passed");
    }
}
