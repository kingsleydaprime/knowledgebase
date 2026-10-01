package orders;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class Orders {
    public record Item(String sku, int quantity) {}

    // Domain errors: unchecked exceptions named in the business's language.
    public static final class EmptyOrderException extends RuntimeException {
        public EmptyOrderException() { super("an order needs at least one item"); }
    }
    public static final class OutOfStockException extends RuntimeException {
        public final String sku;
        public OutOfStockException(String sku) { super("out of stock: " + sku); this.sku = sku; }
    }

    // Repository: the only code that knows how data is stored.
    public static final class Repository {
        final Map<String, Integer> stock;
        private final List<List<Item>> orders = new ArrayList<>();
        public Repository(Map<String, Integer> stock) { this.stock = stock; }
        int create(List<Item> items) { orders.add(items); return orders.size(); }
    }

    // Service: business rules, no HTTP.
    public static final class Service {
        private final Repository repo;
        public Service(Repository repo) { this.repo = repo; }

        public int place(List<Item> items) {
            if (items.isEmpty()) throw new EmptyOrderException();
            for (Item it : items) {
                if (repo.stock.getOrDefault(it.sku(), 0) < it.quantity()) throw new OutOfStockException(it.sku());
            }
            for (Item it : items) repo.stock.merge(it.sku(), -it.quantity(), Integer::sum);
            return repo.create(items);
        }
    }

    public record Response(int status, String body) {}

    // Controller: in Spring, the catch blocks become one @RestControllerAdvice class.
    public static Response createOrder(Service service, List<Item> items) {
        try {
            return new Response(201, "{\"id\":" + service.place(items) + "}");
        } catch (EmptyOrderException e) {
            return new Response(400, e.getMessage());
        } catch (OutOfStockException e) {
            return new Response(409, e.getMessage());
        }
    }
}
