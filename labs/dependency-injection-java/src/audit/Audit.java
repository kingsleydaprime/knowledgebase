package audit;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public final class Audit {
    // A dependency, handed in through constructors.
    public static final class Log {
        public final List<String> entries = new CopyOnWriteArrayList<>();
        void add(String entry) { entries.add(entry); }
        public List<String> sorted() { var copy = new java.util.ArrayList<>(entries); Collections.sort(copy); return copy; }
    }

    // BUG: one instance serves every request, but holds per-request data.
    public static final class BuggyService {
        private final Log log;
        private volatile String currentUser = "nobody";
        public BuggyService(Log log) { this.log = log; }
        public void setUser(String user) { currentUser = user; }
        public void record(String action) { log.add(currentUser + ": " + action); }
    }

    // FIX 1: request data is an argument.
    public static final class Service {
        private final Log log;
        public Service(Log log) { this.log = log; }
        public void record(String user, String action) { log.add(user + ": " + action); }
    }

    // FIX 2: per-thread context — the classic servlet-era answer. Always clear it when the request ends.
    public static final ThreadLocal<String> CURRENT_USER = ThreadLocal.withInitial(() -> "nobody");

    public static final class ContextService {
        private final Log log;
        public ContextService(Log log) { this.log = log; }
        public void record(String action) { log.add(CURRENT_USER.get() + ": " + action); }
    }
}
