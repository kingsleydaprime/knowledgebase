// A small in-memory message broker: queues, topics, redelivery, a dead-letter queue, a partitioned log and load
// levelling. The same numbers as the TypeScript lab. The bounded queue is System.Threading.Channels.

public record Delivery(string Id, string Body, string? Key, int Attempt);

/// <summary>Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery.</summary>
public sealed class Broker(Func<long> now, long visibilityMs, int maxAttempts)
{
    private sealed class Stored(string id, string body, string? key)
    {
        public string Id { get; } = id;
        public string Body { get; } = body;
        public string? Key { get; } = key;
        public int Attempts { get; set; }
        public long VisibleAt { get; set; }
    }

    private readonly Dictionary<string, List<string>> _subscribers = [];
    private readonly Dictionary<string, List<Stored>> _queues = [];
    private readonly Dictionary<string, List<Stored>> _dead = [];
    private int _nextId = 1;

    public void Subscribe(string topic, string subscription)
    {
        if (!_subscribers.TryGetValue(topic, out var list)) _subscribers[topic] = list = [];
        list.Add(subscription);
        _queues[subscription] = [];
        _dead[subscription] = [];
    }

    /// <summary>With no subscribers, nobody keeps the message.</summary>
    public string Publish(string topic, string body, string? key = null)
    {
        var id = $"m{_nextId++}";
        foreach (var s in _subscribers.GetValueOrDefault(topic) ?? []) _queues[s].Add(new Stored(id, body, key));
        return id;
    }

    public Delivery? Receive(string subscription)
    {
        var queue = _queues[subscription];
        for (var i = 0; i < queue.Count; i++)
        {
            var m = queue[i];
            if (m.VisibleAt > now()) continue; // a consumer has it
            if (m.Attempts >= maxAttempts)
            {
                queue.RemoveAt(i--); // poison: stop retrying it
                _dead[subscription].Add(m);
                continue;
            }
            m.Attempts++;
            m.VisibleAt = now() + visibilityMs;
            return new Delivery(m.Id, m.Body, m.Key, m.Attempts);
        }
        return null;
    }

    public void Ack(string subscription, string id) => _queues[subscription].RemoveAll(m => m.Id == id);

    public int Depth(string subscription) => _queues[subscription].Count;

    public IReadOnlyList<string> DeadLetters(string subscription) => _dead[subscription].Select(m => m.Body).ToList();
}

public static class Messages
{
    /// <summary>Skips a message ID it has already processed.</summary>
    public static Func<Delivery, string> Idempotent(Action<string> handle, ISet<string> seen) => d =>
    {
        if (seen.Contains(d.Id)) return "duplicate";
        handle(d.Body);
        seen.Add(d.Id);
        return "processed";
    };

    /// <summary>The same stable hash as the TypeScript lab; string.GetHashCode() changes every run.</summary>
    public static int PartitionFor(string key, int partitions)
    {
        var h = 0x811c9dc5u;
        foreach (var c in key) h = (h ^ c) * 0x01000193;
        h = (h ^ (h >> 16)) * 0x85ebca6b;
        h = (h ^ (h >> 13)) * 0xc2b2ae35;
        return (int)((h ^ (h >> 16)) % (uint)partitions);
    }

    public record Levelled(int Served, int Rejected, int PeakDepth, int ClearedAfterSeconds, int MaxWaitSeconds);

    public static Levelled LevelLoad(int[] arrivals, int perSecond)
    {
        var served = arrivals.Sum(a => Math.Min(a, perSecond));
        var rejected = arrivals.Sum(a => Math.Max(0, a - perSecond));
        var waiting = new Queue<int[]>(); // {arrival second, count}, oldest first; arrays so the count can change in place
        int depth = 0, peakDepth = 0, maxWait = 0, cleared = 0;
        for (var second = 0; second < arrivals.Length || depth > 0; second++)
        {
            var a = second < arrivals.Length ? arrivals[second] : 0;
            if (a > 0) waiting.Enqueue([second, a]);
            depth += a;
            for (var capacity = perSecond; capacity > 0 && waiting.Count > 0;)
            {
                var oldest = waiting.Peek();
                var n = Math.Min(capacity, oldest[1]);
                oldest[1] -= n;
                capacity -= n;
                depth -= n;
                maxWait = Math.Max(maxWait, second - oldest[0]);
                if (oldest[1] == 0) waiting.Dequeue();
            }
            peakDepth = Math.Max(peakDepth, depth);
            if (depth > 0) cleared = second + 2;
        }
        return new(served, rejected, peakDepth, cleared, maxWait);
    }
}

/// <summary>Kafka-like: messages are kept; each consumer group has its own offset per partition.</summary>
public sealed class PartitionedLog(int count)
{
    private readonly List<string>[] _partitions = Enumerable.Range(0, count).Select(_ => new List<string>()).ToArray();
    private readonly Dictionary<string, int[]> _offsets = [];

    public int Append(string key, string body)
    {
        var p = Messages.PartitionFor(key, _partitions.Length);
        _partitions[p].Add(body);
        return p;
    }

    public string? Poll(string group, int partition)
    {
        var offset = OffsetsFor(group)[partition];
        return offset < _partitions[partition].Count ? _partitions[partition][offset] : null;
    }

    public void Commit(string group, int partition) => OffsetsFor(group)[partition]++;

    private int[] OffsetsFor(string group) =>
        _offsets.TryGetValue(group, out var o) ? o : _offsets[group] = new int[_partitions.Length]; // a new group starts at 0
}
