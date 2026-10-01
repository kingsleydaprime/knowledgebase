//! Dependencies are fields set by the caller. A trait is the "interface"; tests pass a fake.
use std::sync::Mutex;

pub trait AuditLog: Send + Sync {
    fn add(&self, entry: String);
}

/// An in-memory log for tests. `Mutex` because many threads may write at once.
#[derive(Default)]
pub struct MemoryLog(pub Mutex<Vec<String>>);

impl AuditLog for MemoryLog {
    fn add(&self, entry: String) {
        self.0.lock().unwrap().push(entry);
    }
}

/// Compiles — the Mutex makes it free of *data* races — but it's still the scope bug:
/// one shared value holding per-request data.
pub struct BuggyService<'a> {
    pub log: &'a dyn AuditLog,
    pub current_user: Mutex<String>,
}

impl BuggyService<'_> {
    pub fn set_user(&self, user: &str) {
        *self.current_user.lock().unwrap() = user.to_string();
    }
    pub fn record(&self, action: &str) {
        let user = self.current_user.lock().unwrap().clone();
        self.log.add(format!("{user}: {action}"));
    }
}

/// The fix: request data is an argument.
pub struct Service<'a> {
    pub log: &'a dyn AuditLog,
}

impl Service<'_> {
    pub fn record(&self, user: &str, action: &str) {
        self.log.add(format!("{user}: {action}"));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::mpsc;
    use std::thread;

    #[test]
    fn a_mutex_stops_data_races_not_the_wrong_user() {
        let log = MemoryLog::default();
        let buggy = BuggyService {
            log: &log,
            current_user: Mutex::new("nobody".into()),
        };
        let (ada_set, ada_set_rx) = mpsc::channel();
        let (bayo_set, bayo_set_rx) = mpsc::channel();

        let buggy = &buggy; // share a reference; move the channel ends into their threads
        thread::scope(|s| {
            s.spawn(move || {
                buggy.set_user("ada");
                ada_set.send(()).unwrap();
                bayo_set_rx.recv().unwrap(); // wait until bayo has overwritten it
                buggy.record("viewed invoice");
            });
            s.spawn(move || {
                ada_set_rx.recv().unwrap();
                buggy.set_user("bayo");
                bayo_set.send(()).unwrap();
                buggy.record("viewed invoice");
            });
        });

        let entries = log.0.lock().unwrap();
        assert_eq!(*entries, ["bayo: viewed invoice", "bayo: viewed invoice"]);
    }

    #[test]
    fn passing_the_user_records_each_request_correctly() {
        let log = MemoryLog::default();
        let service = Service { log: &log };
        thread::scope(|s| {
            s.spawn(|| service.record("ada", "viewed invoice"));
            s.spawn(|| service.record("bayo", "viewed invoice"));
        });
        let mut entries = log.0.lock().unwrap().clone();
        entries.sort();
        assert_eq!(entries, ["ada: viewed invoice", "bayo: viewed invoice"]);
    }
}
