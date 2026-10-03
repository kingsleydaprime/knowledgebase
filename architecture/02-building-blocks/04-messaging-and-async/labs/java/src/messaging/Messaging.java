package messaging;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.LongSupplier;

/** A small in-memory message broker. The same numbers as the TypeScript lab. The bounded queue is java.util.concurrent's. */
public final class Messaging {
    private Messaging() {}

    public record Delivery(String id, String body, String key, int attempt) {}

    private static final class Stored {
        final String id;
        final String body;
        final String key;
        int attempts;
        long visibleAt;

        Stored(String id, String body, String key) {
            this.id = id;
            this.body = body;
            this.key = key;
        }
    }

    /** Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery. */
    public static final class Broker {
        private final LongSupplier now;
        private final long visibilityMs;
        private final int maxAttempts;
        private final Map<String, List<String>> subscribers = new HashMap<>();
        private final Map<String, List<Stored>> queues = new HashMap<>();
        private final Map<String, List<Stored>> dead = new HashMap<>();
        private int nextId = 1;

        public Broker(LongSupplier now, long visibilityMs, int maxAttempts) {
            this.now = now;
            this.visibilityMs = visibilityMs;
            this.maxAttempts = maxAttempts;
        }

        public void subscribe(String topic, String subscription) {
            subscribers.computeIfAbsent(topic, t -> new ArrayList<>()).add(subscription);
            queues.put(subscription, new ArrayList<>());
            dead.put(subscription, new ArrayList<>());
        }

        /** With no subscribers, nobody keeps the message. */
        public String publish(String topic, String body, String key) {
            String id = "m" + nextId++;
            for (String s : subscribers.getOrDefault(topic, List.of())) queues.get(s).add(new Stored(id, body, key));
            return id;
        }

        public Optional<Delivery> receive(String subscription) {
            var queue = queues.get(subscription);
            for (var it = queue.iterator(); it.hasNext();) {
                Stored m = it.next();
                if (m.visibleAt > now.getAsLong()) continue; // a consumer has it
                if (m.attempts >= maxAttempts) {
                    it.remove(); // poison: stop retrying it
                    dead.get(subscription).add(m);
                    continue;
                }
                m.attempts++;
                m.visibleAt = now.getAsLong() + visibilityMs;
                return Optional.of(new Delivery(m.id, m.body, m.key, m.attempts));
            }
            return Optional.empty();
        }

        public void ack(String subscription, String id) {
            queues.get(subscription).removeIf(m -> m.id.equals(id));
        }

        public int depth(String subscription) {
            return queues.get(subscription).size();
        }

        public List<String> deadLetters(String subscription) {
            return dead.get(subscription).stream().map(m -> m.body).toList();
        }
    }

    /** Skips a message ID it has already processed. */
    public static Function<Delivery, String> idempotent(Consumer<String> handle, Set<String> seen) {
        return d -> {
            if (seen.contains(d.id())) return "duplicate";
            handle.accept(d.body());
            seen.add(d.id());
            return "processed";
        };
    }

    /** The same stable hash as the TypeScript lab. String.hashCode is stable too, but clusters similar keys. */
    public static int partitionFor(String key, int partitions) {
        int h = 0x811c9dc5;
        for (int i = 0; i < key.length(); i++) h = (h ^ key.charAt(i)) * 0x01000193;
        h = (h ^ (h >>> 16)) * 0x85ebca6b;
        h = (h ^ (h >>> 13)) * 0xc2b2ae35;
        return Integer.remainderUnsigned(h ^ (h >>> 16), partitions);
    }

    /** Kafka-like: messages are kept; each consumer group has its own offset per partition. */
    public static final class PartitionedLog {
        private final List<List<String>> partitions = new ArrayList<>();
        private final Map<String, int[]> offsets = new HashMap<>();

        public PartitionedLog(int count) {
            for (int i = 0; i < count; i++) partitions.add(new ArrayList<>());
        }

        public int append(String key, String body) {
            int p = partitionFor(key, partitions.size());
            partitions.get(p).add(body);
            return p;
        }

        public Optional<String> poll(String group, int partition) {
            int offset = offsetsFor(group)[partition];
            var messages = partitions.get(partition);
            return offset < messages.size() ? Optional.of(messages.get(offset)) : Optional.empty();
        }

        public void commit(String group, int partition) {
            offsetsFor(group)[partition]++;
        }

        private int[] offsetsFor(String group) {
            return offsets.computeIfAbsent(group, g -> new int[partitions.size()]); // a new group starts at 0
        }
    }

    public record Levelled(int served, int rejected, int peakDepth, int clearedAfterSeconds, int maxWaitSeconds) {}

    public static Levelled levelLoad(int[] arrivals, int perSecond) {
        int served = 0;
        int rejected = 0;
        for (int a : arrivals) {
            served += Math.min(a, perSecond);
            rejected += Math.max(0, a - perSecond);
        }
        var waiting = new ArrayDeque<int[]>(); // {arrival second, count}, oldest first
        int depth = 0;
        int peakDepth = 0;
        int maxWait = 0;
        int cleared = 0;
        for (int second = 0; second < arrivals.length || depth > 0; second++) {
            int a = second < arrivals.length ? arrivals[second] : 0;
            if (a > 0) waiting.add(new int[] {second, a});
            depth += a;
            for (int capacity = perSecond; capacity > 0 && !waiting.isEmpty();) {
                int[] oldest = waiting.peek();
                int n = Math.min(capacity, oldest[1]);
                oldest[1] -= n;
                capacity -= n;
                depth -= n;
                maxWait = Math.max(maxWait, second - oldest[0]);
                if (oldest[1] == 0) waiting.poll();
            }
            peakDepth = Math.max(peakDepth, depth);
            if (depth > 0) cleared = second + 2;
        }
        return new Levelled(served, rejected, peakDepth, cleared, maxWait);
    }
}
