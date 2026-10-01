package audit;

import java.util.List;
import java.util.concurrent.CountDownLatch;

// Plain-Java checks, run with assertions enabled (java -ea).
public final class Check {
    public static void main(String[] args) throws Exception {
        // The composition root for the test: build the graph by hand.
        var log = new Audit.Log();
        var buggy = new Audit.BuggyService(log);

        // Force the bad interleaving: ada sets her name, then bayo sets his, then ada records.
        var adaHasSetUser = new CountDownLatch(1);
        var bayoHasSetUser = new CountDownLatch(1);
        var ada = new Thread(() -> {
            buggy.setUser("ada");
            adaHasSetUser.countDown();
            await(bayoHasSetUser);
            buggy.record("viewed invoice");
        });
        var bayo = new Thread(() -> {
            await(adaHasSetUser);
            buggy.setUser("bayo");
            bayoHasSetUser.countDown();
            buggy.record("viewed invoice");
        });
        ada.start(); bayo.start(); ada.join(); bayo.join();
        assert log.entries.equals(List.of("bayo: viewed invoice", "bayo: viewed invoice")) : log.entries;
        System.out.println("bug reproduced: " + log.entries);

        var fixedLog = new Audit.Log();
        var service = new Audit.Service(fixedLog);
        var t1 = new Thread(() -> service.record("ada", "viewed invoice"));
        var t2 = new Thread(() -> service.record("bayo", "viewed invoice"));
        t1.start(); t2.start(); t1.join(); t2.join();
        assert fixedLog.sorted().equals(List.of("ada: viewed invoice", "bayo: viewed invoice")) : fixedLog.entries;

        var contextLog = new Audit.Log();
        var contextService = new Audit.ContextService(contextLog);
        Runnable request1 = () -> withUser("ada", () -> contextService.record("viewed invoice"));
        Runnable request2 = () -> withUser("bayo", () -> contextService.record("viewed invoice"));
        var t3 = new Thread(request1); var t4 = new Thread(request2);
        t3.start(); t4.start(); t3.join(); t4.join();
        assert contextLog.sorted().equals(List.of("ada: viewed invoice", "bayo: viewed invoice")) : contextLog.entries;
        System.out.println("both fixes record the right users");
    }

    static void withUser(String user, Runnable work) {
        Audit.CURRENT_USER.set(user);
        try { work.run(); } finally { Audit.CURRENT_USER.remove(); } // thread pools reuse threads
    }

    static void await(CountDownLatch latch) {
        try { latch.await(); } catch (InterruptedException e) { throw new RuntimeException(e); }
    }
}
