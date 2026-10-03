//! A small in-memory message broker: queues, topics, redelivery, a dead-letter queue, a partitioned log and load
//! levelling. The same numbers as the TypeScript lab. The bounded queue is std's `sync_channel`.
use std::collections::{HashMap, HashSet, VecDeque};

#[derive(Debug, Clone, PartialEq)]
pub struct Delivery {
    pub id: String,
    pub body: String,
    pub key: Option<String>,
    pub attempt: u32,
}

struct Stored {
    id: String,
    body: String,
    key: Option<String>,
    attempts: u32,
    visible_at: u64,
}

/// Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery.
pub struct Broker {
    now: Box<dyn Fn() -> u64>, // milliseconds
    visibility_ms: u64,
    max_attempts: u32,
    subscribers: HashMap<String, Vec<String>>,
    queues: HashMap<String, Vec<Stored>>,
    dead: HashMap<String, Vec<Stored>>,
    next_id: u32,
}

impl Broker {
    pub fn new(now: impl Fn() -> u64 + 'static, visibility_ms: u64, max_attempts: u32) -> Self {
        Broker {
            now: Box::new(now),
            visibility_ms,
            max_attempts,
            subscribers: HashMap::new(),
            queues: HashMap::new(),
            dead: HashMap::new(),
            next_id: 1,
        }
    }

    pub fn subscribe(&mut self, topic: &str, subscription: &str) {
        self.subscribers
            .entry(topic.into())
            .or_default()
            .push(subscription.into());
        self.queues.insert(subscription.into(), Vec::new());
        self.dead.insert(subscription.into(), Vec::new());
    }

    /// With no subscribers, nobody keeps the message.
    pub fn publish(&mut self, topic: &str, body: &str, key: Option<&str>) -> String {
        let id = format!("m{}", self.next_id);
        self.next_id += 1;
        for s in self.subscribers.get(topic).into_iter().flatten() {
            let stored = Stored {
                id: id.clone(),
                body: body.into(),
                key: key.map(Into::into),
                attempts: 0,
                visible_at: 0,
            };
            self.queues.get_mut(s).expect("subscribed").push(stored);
        }
        id
    }

    pub fn receive(&mut self, subscription: &str) -> Option<Delivery> {
        let now = (self.now)();
        let queue = self.queues.get_mut(subscription)?;
        let mut i = 0;
        while i < queue.len() {
            if queue[i].visible_at > now {
                i += 1; // a consumer has it
            } else if queue[i].attempts >= self.max_attempts {
                let poison = queue.remove(i); // stop retrying it
                self.dead
                    .get_mut(subscription)
                    .expect("subscribed")
                    .push(poison);
            } else {
                let m = &mut queue[i];
                m.attempts += 1;
                m.visible_at = now + self.visibility_ms;
                return Some(Delivery {
                    id: m.id.clone(),
                    body: m.body.clone(),
                    key: m.key.clone(),
                    attempt: m.attempts,
                });
            }
        }
        None
    }

    pub fn ack(&mut self, subscription: &str, id: &str) {
        if let Some(queue) = self.queues.get_mut(subscription) {
            queue.retain(|m| m.id != id);
        }
    }

    pub fn depth(&self, subscription: &str) -> usize {
        self.queues[subscription].len()
    }

    pub fn dead_letters(&self, subscription: &str) -> Vec<&str> {
        self.dead[subscription]
            .iter()
            .map(|m| m.body.as_str())
            .collect()
    }
}

/// Skips a message ID it has already processed.
pub fn idempotent<'a>(
    mut handle: impl FnMut(&str) + 'a,
    seen: &'a mut HashSet<String>,
) -> impl FnMut(&Delivery) -> &'static str + 'a {
    move |d| {
        if seen.contains(&d.id) {
            return "duplicate";
        }
        handle(&d.body);
        seen.insert(d.id.clone());
        "processed"
    }
}

/// The same stable hash as the TypeScript lab. std's HashMap hasher is seeded randomly, so it can't choose partitions.
pub fn partition_for(key: &str, partitions: usize) -> usize {
    let mut h: u32 = 0x811c9dc5;
    for byte in key.bytes() {
        h = (h ^ u32::from(byte)).wrapping_mul(0x01000193);
    }
    h = (h ^ (h >> 16)).wrapping_mul(0x85ebca6b);
    h = (h ^ (h >> 13)).wrapping_mul(0xc2b2ae35);
    (h ^ (h >> 16)) as usize % partitions
}

/// Kafka-like: messages are kept; each consumer group has its own offset per partition.
pub struct PartitionedLog {
    partitions: Vec<Vec<String>>,
    offsets: HashMap<String, Vec<usize>>,
}

impl PartitionedLog {
    pub fn new(partitions: usize) -> Self {
        PartitionedLog {
            partitions: vec![Vec::new(); partitions],
            offsets: HashMap::new(),
        }
    }

    pub fn append(&mut self, key: &str, body: &str) -> usize {
        let p = partition_for(key, self.partitions.len());
        self.partitions[p].push(body.into());
        p
    }

    pub fn poll(&mut self, group: &str, partition: usize) -> Option<String> {
        let offset = self.offsets_for(group)[partition];
        self.partitions[partition].get(offset).cloned()
    }

    pub fn commit(&mut self, group: &str, partition: usize) {
        self.offsets_for(group)[partition] += 1;
    }

    fn offsets_for(&mut self, group: &str) -> &mut Vec<usize> {
        let count = self.partitions.len();
        self.offsets
            .entry(group.into())
            .or_insert_with(|| vec![0; count]) // a new group starts at the beginning
    }
}

#[derive(Debug, PartialEq)]
pub struct Levelled {
    pub served: u32,
    pub rejected: u32,
    pub peak_depth: u32,
    pub cleared_after_seconds: usize,
    pub max_wait_seconds: usize,
}

pub fn level_load(arrivals: &[u32], per_second: u32) -> Levelled {
    let served = arrivals.iter().map(|&a| a.min(per_second)).sum();
    let rejected = arrivals.iter().map(|&a| a.saturating_sub(per_second)).sum();
    let mut waiting: VecDeque<(usize, u32)> = VecDeque::new(); // (arrival second, count), oldest first
    let (mut depth, mut peak_depth, mut max_wait, mut cleared) = (0, 0, 0, 0);
    let mut second = 0;
    while second < arrivals.len() || depth > 0 {
        let a = arrivals.get(second).copied().unwrap_or(0);
        if a > 0 {
            waiting.push_back((second, a));
        }
        depth += a;
        let mut capacity = per_second;
        while capacity > 0 {
            let Some(oldest) = waiting.front_mut() else {
                break;
            };
            let n = capacity.min(oldest.1);
            oldest.1 -= n;
            capacity -= n;
            depth -= n;
            max_wait = max_wait.max(second - oldest.0);
            if oldest.1 == 0 {
                waiting.pop_front();
            }
        }
        peak_depth = peak_depth.max(depth);
        if depth > 0 {
            cleared = second + 2;
        }
        second += 1;
    }
    Levelled {
        served,
        rejected,
        peak_depth,
        cleared_after_seconds: cleared,
        max_wait_seconds: max_wait,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;
    use std::rc::Rc;
    use std::sync::atomic::{AtomicU32, Ordering};
    use std::sync::{Arc, mpsc};

    fn broker() -> (Rc<Cell<u64>>, Broker) {
        let clock = Rc::new(Cell::new(0));
        let read = clock.clone();
        (clock, Broker::new(move || read.get(), 30_000, 3))
    }

    fn body(d: Option<Delivery>) -> String {
        d.expect("a message").body
    }

    #[test]
    fn a_queue_gives_each_message_to_one_consumer_a_topic_copies_it() {
        let (_, mut b) = broker();
        b.subscribe("orders", "invoices");
        b.subscribe("orders", "analytics");
        b.publish("orders", "order 1", None);
        b.publish("orders", "order 2", None);
        assert_eq!(
            [body(b.receive("invoices")), body(b.receive("invoices"))],
            ["order 1", "order 2"]
        );
        assert_eq!(b.receive("invoices"), None);
        assert_eq!(
            [body(b.receive("analytics")), body(b.receive("analytics"))],
            ["order 1", "order 2"]
        );
        b.publish("refunds", "refund 1", None);
        assert_eq!(b.depth("invoices") + b.depth("analytics"), 4);
    }

    #[test]
    fn unacknowledged_comes_back_then_goes_to_the_dead_letter_queue() {
        let (clock, mut b) = broker();
        b.subscribe("orders", "invoices");
        b.publish("orders", "order 1", None);
        assert_eq!(b.receive("invoices").unwrap().attempt, 1);
        assert_eq!(b.receive("invoices"), None);
        for (now, attempt) in [(30_000, 2), (60_000, 3)] {
            clock.set(now);
            assert_eq!(b.receive("invoices").unwrap().attempt, attempt);
        }
        clock.set(90_000);
        assert_eq!(b.receive("invoices"), None);
        assert_eq!(b.dead_letters("invoices"), ["order 1"]);
        assert_eq!(b.depth("invoices"), 0);
    }

    #[test]
    fn a_crash_before_the_ack_charges_twice_unless_idempotent() {
        for safe in [false, true] {
            let (clock, mut b) = broker();
            b.subscribe("orders", "payments");
            b.publish("orders", "charge £40 for order 1", None);
            let charges = Cell::new(0);
            let mut seen = HashSet::new();
            let mut once = idempotent(|_| charges.set(charges.get() + 1), &mut seen);
            let mut handle = |d: &Delivery| {
                if safe {
                    once(d);
                } else {
                    charges.set(charges.get() + 1)
                }
            };
            handle(&b.receive("payments").unwrap()); // charged, then a crash before the ack
            clock.set(30_000);
            let again = b.receive("payments").unwrap();
            handle(&again);
            b.ack("payments", &again.id);
            assert_eq!(charges.get(), if safe { 1 } else { 2 });
        }
    }

    #[test]
    fn a_queue_absorbs_a_sale_spike() {
        let spike: Vec<u32> = [vec![300; 10], vec![20; 50]].concat();
        let two = level_load(&spike, 100);
        assert_eq!(
            two,
            Levelled {
                served: 2_000,
                rejected: 2_000,
                peak_depth: 2_000,
                cleared_after_seconds: 35,
                max_wait_seconds: 20
            }
        );
        let four = level_load(&spike, 200);
        assert_eq!(
            (
                four.peak_depth,
                four.cleared_after_seconds,
                four.max_wait_seconds
            ),
            (1_000, 16, 5)
        );
    }

    #[test]
    fn redelivery_reorders_a_partition_keeps_order_a_new_group_replays() {
        let (clock, mut b) = broker();
        b.subscribe("orders", "shipping");
        for e in ["created", "paid", "shipped"] {
            b.publish("orders", &format!("order 7 {e}"), Some("order-7"));
        }
        let mut seen = Vec::new();
        for fail in [false, true, false] {
            let d = b.receive("shipping").unwrap();
            if !fail {
                b.ack("shipping", &d.id);
                seen.push(d.body);
            }
        }
        clock.set(30_000);
        seen.push(body(b.receive("shipping")));
        assert_eq!(seen, ["order 7 created", "order 7 shipped", "order 7 paid"]);

        let mut log = PartitionedLog::new(4);
        for e in ["created", "paid", "shipped"] {
            log.append("order-7", &format!("order 7 {e}"));
        }
        let p = partition_for("order-7", 4);
        let (mut in_order, mut failed_once) = (Vec::new(), false);
        while let Some(m) = log.poll("shipping", p) {
            if m.ends_with("paid") && !failed_once {
                failed_once = true; // no commit: the same message comes back
                continue;
            }
            in_order.push(m);
            log.commit("shipping", p);
        }
        assert_eq!(
            in_order,
            ["order 7 created", "order 7 paid", "order 7 shipped"]
        );
        assert_eq!(log.poll("analytics", p).as_deref(), Some("order 7 created"));
    }

    #[test]
    fn a_key_always_lands_in_the_same_partition() {
        let mut counts = [0; 4];
        for i in 0..10_000 {
            counts[partition_for(&format!("order-{i}"), 4)] += 1;
        }
        assert!(
            counts.iter().all(|&n: &i32| (n - 2_500).abs() < 200),
            "{counts:?}"
        );
    }

    #[test]
    fn a_sync_channel_pushes_back() {
        let (tx, rx) = mpsc::sync_channel::<u32>(3);
        let accepted: Vec<bool> = (1..=4).map(|n| tx.try_send(n).is_ok()).collect(); // Err(Full) for the fourth
        assert_eq!(accepted, [true, true, true, false]);
        assert_eq!(rx.try_iter().collect::<Vec<_>>(), [1, 2, 3]);

        let puts = Arc::new(AtomicU32::new(0));
        let counted = puts.clone();
        let producer = std::thread::spawn(move || {
            for n in 1..=5 {
                tx.send(n).unwrap(); // waits while the channel is full
                counted.fetch_add(1, Ordering::SeqCst);
            }
        });
        let wait_for = |n| {
            while puts.load(Ordering::SeqCst) < n {
                std::thread::yield_now()
            }
        };
        wait_for(3); // it can't get past 3 until something is taken
        assert_eq!(rx.recv().unwrap(), 1);
        wait_for(4);
        assert_eq!(puts.load(Ordering::SeqCst), 4); // and not past 4 until the next take
        assert_eq!(rx.iter().take(4).collect::<Vec<_>>(), [2, 3, 4, 5]);
        producer.join().unwrap();
    }
}
