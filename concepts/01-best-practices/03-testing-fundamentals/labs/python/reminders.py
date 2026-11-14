"""reminders.py — the trial-reminder emailer; every collaborator is passed in."""
from datetime import date, timedelta


def day_after(today: date) -> date:
    return today + timedelta(days=1)  # date arithmetic rolls months and years over


def ending_tomorrow(users: list[dict], today: date) -> list[dict]:
    target = day_after(today)
    return [u for u in users if u["trial_ends_on"] == target]


def send_trial_reminders(users, mailer, clock) -> int:
    due = ending_tomorrow(users.list_on_trial(), clock())
    for user in due:
        mailer.send(user["email"], "Your trial ends tomorrow")
    return len(due)
