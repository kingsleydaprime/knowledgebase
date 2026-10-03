package balancing;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.function.Supplier;
import java.util.stream.IntStream;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class BalancingCheck {
    private BalancingCheck() {}

    static final List<String> KEYS = IntStream.range(0, 10_000).mapToObj(i -> "user:" + i).toList();
    static final List<String> FOUR = List.of("cache-a", "cache-b", "cache-c", "cache-d");

    public static void main(String[] args) {
        var pick = Balancing.roundRobin();
        int[] queues = {5, 0, 0};
        List<Integer> turns = new ArrayList<>();
        for (int i = 0; i < 6; i++) turns.add(pick.pick(queues, null));
        assert turns.equals(List.of(0, 1, 2, 0, 1, 2)) && Balancing.LEAST_OUTSTANDING.pick(queues, null) == 1;

        var weights = new LinkedHashMap<String, Integer>();
        weights.put("a", 5);
        weights.put("b", 1);
        weights.put("c", 1);
        Supplier<String> weighted = Balancing.smoothWeighted(weights);
        var order = new StringBuilder();
        for (int i = 0; i < 7; i++) order.append(weighted.get());
        assert order.toString().equals("aabacaa") : order;

        assert Balancing.simulate(Balancing.roundRobin(), 4, 0.8, 100_000, 7).equals(new Balancing.Latency(214, 138, 1_158));
        assert Balancing.simulate(Balancing.RANDOM, 4, 0.8, 100_000, 7).equals(new Balancing.Latency(255, 159, 1_588));
        assert Balancing.simulate(Balancing.LEAST_OUTSTANDING, 4, 0.8, 100_000, 7).equals(new Balancing.Latency(68, 17, 466));
        var two = Balancing.simulate(Balancing.TWO_CHOICES, 4, 0.8, 100_000, 7);
        assert two.equals(new Balancing.Latency(96, 25, 495)) : two;

        var health = new Balancing.Health(3, 2);
        List<Boolean> states = new ArrayList<>();
        for (boolean ok : new boolean[] {false, false, true, false, false, false, true, true}) {
            health.record(ok);
            states.add(health.up());
        }
        assert states.equals(List.of(true, true, true, true, true, false, false, true)) : states;

        var servers = List.of(new Balancing.Server("app-1", new Balancing.Health(3, 2)),
                new Balancing.Server("app-2", new Balancing.Health(3, 2)), new Balancing.Server("app-3", new Balancing.Health(3, 2)));
        for (int i = 0; i < 3; i++) servers.get(1).health().record(false);
        List<String> picked = new ArrayList<>();
        for (int t = 0; t < 4; t++) picked.add(Balancing.pickHealthy(servers, t));
        assert picked.equals(List.of("app-1", "app-3", "app-1", "app-3")) : picked;
        for (var s : servers) for (int i = 0; i < 3; i++) s.health().record(false);
        try {
            Balancing.pickHealthy(servers, 0);
            throw new AssertionError("expected no healthy servers");
        } catch (IllegalStateException expected) {
            // answer 503
        }

        var five = new ArrayList<>(FOUR);
        five.add("cache-e");
        long movedByModulo = KEYS.stream().filter(k -> !Balancing.modulo(k, FOUR).equals(Balancing.modulo(k, five))).count();
        assert Math.abs(movedByModulo - 8_000) < 200 : movedByModulo;
        var ring = new Balancing.HashRing(FOUR, 100);
        var before = KEYS.stream().map(ring::serverFor).toList();
        ring.add("cache-e");
        var moved = IntStream.range(0, KEYS.size()).filter(i -> !ring.serverFor(KEYS.get(i)).equals(before.get(i))).boxed().toList();
        assert Math.abs(moved.size() - 2_000) < 300 : moved.size();
        assert moved.stream().allMatch(i -> ring.serverFor(KEYS.get(i)).equals("cache-e"));
        ring.remove("cache-e");
        assert KEYS.stream().map(ring::serverFor).toList().equals(before);

        assert busiest(1) > 1.4 && busiest(100) < 1.2 : busiest(1) + " " + busiest(100);
        System.out.println("all balancing checks passed");
    }

    private static double busiest(int replicas) {
        var ring = new Balancing.HashRing(FOUR, replicas);
        var counts = new HashMap<String, Integer>();
        for (String k : KEYS) counts.merge(ring.serverFor(k), 1, Integer::sum);
        return counts.values().stream().mapToInt(Integer::intValue).max().orElseThrow() / (KEYS.size() / 4.0);
    }
}
