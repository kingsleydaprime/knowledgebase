package fees;

import java.util.Map;
import java.util.function.LongUnaryOperator;

public final class Fees {
    // Open for extension: a map from method name to rule. A new method is a new entry.
    public static final Map<String, LongUnaryOperator> OPEN_RULES = Map.of(
        "card", amount -> amount * 29 / 1000,
        "transfer", amount -> 50);

    // Closed: a sealed interface and an exhaustive switch (Java 21). A new record that
    // implements Method makes every such switch fail to compile until it handles it.
    public sealed interface Method permits Card, Transfer {}
    public record Card() implements Method {}
    public record Transfer() implements Method {}

    public static long fee(Method method, long amountKobo) {
        return switch (method) {
            case Card c -> amountKobo * 29 / 1000;
            case Transfer t -> 50;
        };
    }

    public static void main(String[] args) {
        assert OPEN_RULES.get("card").applyAsLong(10_000) == 290;
        assert fee(new Card(), 10_000) == 290;
        assert fee(new Transfer(), 10_000) == 50;
        System.out.println("ok: open map and sealed switch agree");
    }
}
