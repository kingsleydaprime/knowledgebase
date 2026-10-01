import unittest
from datetime import date
from unittest.mock import Mock

from reminders import day_after, ending_tomorrow, send_trial_reminders

OCT_31 = date(2026, 10, 31)
USERS = [
    {"email": "ada@x.com", "trial_ends_on": date(2026, 11, 1)},
    {"email": "bayo@x.com", "trial_ends_on": date(2026, 11, 5)},
]


class ReminderTests(unittest.TestCase):
    def test_day_after_rolls_over_boundaries(self):
        self.assertEqual(day_after(OCT_31), date(2026, 11, 1))
        self.assertEqual(day_after(date(2026, 12, 31)), date(2027, 1, 1))
        self.assertEqual(day_after(date(2028, 2, 28)), date(2028, 2, 29))  # leap year

    def test_ending_tomorrow(self):
        self.assertEqual(ending_tomorrow(USERS, OCT_31), [USERS[0]])

    def test_send_with_stub_spy_and_fake_clock(self):
        users = Mock(list_on_trial=Mock(return_value=USERS))  # stub: canned answer
        mailer = Mock()                                       # spy: records calls
        sent = send_trial_reminders(users, mailer, clock=lambda: OCT_31)  # fake clock: a function
        self.assertEqual(sent, 1)
        mailer.send.assert_called_once_with("ada@x.com", "Your trial ends tomorrow")


if __name__ == "__main__":
    unittest.main()
