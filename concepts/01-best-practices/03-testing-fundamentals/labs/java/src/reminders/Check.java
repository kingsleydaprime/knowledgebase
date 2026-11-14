package reminders;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;

// In a Maven or Gradle project this is a JUnit 5 test, and the spy is usually Mockito's mock(Mailer.class).
public final class Check {
    public static void main(String[] args) {
        assert Reminders.dayAfter(LocalDate.of(2026, 10, 31)).equals(LocalDate.of(2026, 11, 1));
        assert Reminders.dayAfter(LocalDate.of(2026, 12, 31)).equals(LocalDate.of(2027, 1, 1));
        assert Reminders.dayAfter(LocalDate.of(2028, 2, 28)).equals(LocalDate.of(2028, 2, 29));

        Reminders.UserSource stub = () -> List.of(
            new Reminders.User("ada@x.com", LocalDate.of(2026, 11, 1)),
            new Reminders.User("bayo@x.com", LocalDate.of(2026, 11, 5)));
        List<String> sent = new ArrayList<>();
        Reminders.Mailer spy = (to, subject) -> sent.add(to + " | " + subject);
        Clock fixed = Clock.fixed(Instant.parse("2026-10-31T12:00:00Z"), ZoneOffset.UTC);

        assert Reminders.sendTrialReminders(stub, spy, fixed) == 1;
        assert sent.equals(List.of("ada@x.com | Your trial ends tomorrow")) : sent;
        System.out.println("ok: stub, spy and Clock.fixed");
    }
}
