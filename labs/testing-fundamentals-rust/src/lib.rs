//! Collaborators are traits; tests pass small structs that implement them.
use chrono::{Days, NaiveDate};

pub struct User {
    pub email: String,
    pub trial_ends_on: NaiveDate,
}

pub trait UserSource {
    fn list_on_trial(&self) -> Vec<User>;
}
pub trait Mailer {
    fn send(&self, to: &str, subject: &str);
}
pub trait Clock {
    fn today(&self) -> NaiveDate;
}

pub fn day_after(day: NaiveDate) -> NaiveDate {
    day.checked_add_days(Days::new(1)).expect("date in range")
}

pub fn send_trial_reminders(
    users: &impl UserSource,
    mailer: &impl Mailer,
    clock: &impl Clock,
) -> usize {
    let target = day_after(clock.today());
    let due: Vec<User> = users
        .list_on_trial()
        .into_iter()
        .filter(|u| u.trial_ends_on == target)
        .collect();
    for user in &due {
        mailer.send(&user.email, "Your trial ends tomorrow");
    }
    due.len()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    fn d(y: i32, m: u32, day: u32) -> NaiveDate {
        NaiveDate::from_ymd_opt(y, m, day).unwrap()
    }

    #[test]
    fn day_after_rolls_over_boundaries() {
        assert_eq!(day_after(d(2026, 10, 31)), d(2026, 11, 1));
        assert_eq!(day_after(d(2026, 12, 31)), d(2027, 1, 1));
        assert_eq!(day_after(d(2028, 2, 28)), d(2028, 2, 29));
    }

    struct StubUsers;
    impl UserSource for StubUsers {
        fn list_on_trial(&self) -> Vec<User> {
            vec![
                User {
                    email: "ada@x.com".into(),
                    trial_ends_on: d(2026, 11, 1),
                },
                User {
                    email: "bayo@x.com".into(),
                    trial_ends_on: d(2026, 11, 5),
                },
            ]
        }
    }

    #[derive(Default)]
    struct SpyMailer(RefCell<Vec<String>>); // RefCell: record calls through a shared reference
    impl Mailer for SpyMailer {
        fn send(&self, to: &str, subject: &str) {
            self.0.borrow_mut().push(format!("{to} | {subject}"));
        }
    }

    struct FixedClock(NaiveDate);
    impl Clock for FixedClock {
        fn today(&self) -> NaiveDate {
            self.0
        }
    }

    #[test]
    fn sends_with_stub_spy_and_fake_clock() {
        let mailer = SpyMailer::default();
        let sent = send_trial_reminders(&StubUsers, &mailer, &FixedClock(d(2026, 10, 31)));
        assert_eq!(sent, 1);
        assert_eq!(*mailer.0.borrow(), ["ada@x.com | Your trial ends tomorrow"]);
    }
}
