package orders;

import java.util.HashMap;
import java.util.List;

public final class Check {
    public static void main(String[] args) {
        var stock = new HashMap<String, Integer>();
        stock.put("mug", 1);
        var service = new Orders.Service(new Orders.Repository(stock));

        assert Orders.createOrder(service, List.of()).status() == 400;
        assert Orders.createOrder(service, List.of(new Orders.Item("mug", 5)))
                .equals(new Orders.Response(409, "out of stock: mug"));
        assert Orders.createOrder(service, List.of(new Orders.Item("mug", 1)))
                .equals(new Orders.Response(201, "{\"id\":1}"));
        assert stock.get("mug") == 0;
        System.out.println("ok: domain errors mapped to 400, 409 and 201");
    }
}
