package reminders;

import java.time.Clock;
import java.time.LocalDate;
import java.util.List;

// java.time.Clock is the standard injectable clock: production passes Clock.systemUTC(),
// tests pass Clock.fixed(...).
public final class Reminders {
    public record User(String email, LocalDate trialEndsOn) {}
    public interface UserSource { List<User> listOnTrial(); }
    public interface Mailer { void send(String to, String subject); }

    public static LocalDate dayAfter(LocalDate day) { return day.plusDays(1); }

    public static int sendTrialReminders(UserSource users, Mailer mailer, Clock clock) {
        LocalDate target = dayAfter(LocalDate.now(clock));
        int sent = 0;
        for (User user : users.listOnTrial()) {
            if (user.trialEndsOn().equals(target)) {
                mailer.send(user.email(), "Your trial ends tomorrow");
                sent++;
            }
        }
        return sent;
    }
}
