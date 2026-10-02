// TimeProvider (.NET 8+) is the standard injectable clock. Production passes TimeProvider.System.
Check(TrialReminders.DayAfter(new DateOnly(2026, 10, 31)) == new DateOnly(2026, 11, 1), "month end");
Check(TrialReminders.DayAfter(new DateOnly(2026, 12, 31)) == new DateOnly(2027, 1, 1), "year end");
Check(TrialReminders.DayAfter(new DateOnly(2028, 2, 28)) == new DateOnly(2028, 2, 29), "leap day");

var stub = new StubUsers([new("ada@x.com", new DateOnly(2026, 11, 1)), new("bayo@x.com", new DateOnly(2026, 11, 5))]);
var spy = new SpyMailer();
var clock = new FixedTime(new DateTimeOffset(2026, 10, 31, 12, 0, 0, TimeSpan.Zero));

Check(TrialReminders.Send(stub, spy, clock) == 1, "one reminder sent");
Check(spy.Sent.SequenceEqual(["ada@x.com | Your trial ends tomorrow"]), "sent to ada");
Console.WriteLine("ok: stub, spy and a fixed TimeProvider");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

record User(string Email, DateOnly TrialEndsOn);
interface IUserSource { IReadOnlyList<User> ListOnTrial(); }
interface IMailer { void Send(string to, string subject); }

static class TrialReminders
{
    public static DateOnly DayAfter(DateOnly day) => day.AddDays(1);

    public static int Send(IUserSource users, IMailer mailer, TimeProvider time)
    {
        var target = DayAfter(DateOnly.FromDateTime(time.GetUtcNow().UtcDateTime));
        var due = users.ListOnTrial().Where(u => u.TrialEndsOn == target).ToList();
        foreach (var user in due) mailer.Send(user.Email, "Your trial ends tomorrow");
        return due.Count;
    }
}

// Hand-written doubles. Moq or NSubstitute generate these in real test projects, and the
// Microsoft.Extensions.TimeProvider.Testing package ships a FakeTimeProvider.
sealed class StubUsers(IReadOnlyList<User> users) : IUserSource { public IReadOnlyList<User> ListOnTrial() => users; }
sealed class SpyMailer : IMailer
{
    public List<string> Sent { get; } = [];
    public void Send(string to, string subject) => Sent.Add($"{to} | {subject}");
}
sealed class FixedTime(DateTimeOffset now) : TimeProvider { public override DateTimeOffset GetUtcNow() => now; }
