#pragma once
// C++20's <chrono> has calendar types: year_month_day, sys_days, days.
#include <chrono>
#include <functional>
#include <string>
#include <vector>

namespace reminders {

using namespace std::chrono;

struct User { std::string email; year_month_day trial_ends_on; };

inline year_month_day day_after(year_month_day day) {
    return year_month_day{sys_days{day} + days{1}};   // through sys_days: rolls months and years
}

// Collaborators as std::function — the clock returns "today".
inline int send_trial_reminders(const std::vector<User>& users,
                                const std::function<void(const std::string&, const std::string&)>& send,
                                const std::function<year_month_day()>& today) {
    const auto target = day_after(today());
    int sent = 0;
    for (const auto& user : users) {
        if (user.trial_ends_on == target) {
            send(user.email, "Your trial ends tomorrow");
            ++sent;
        }
    }
    return sent;
}

}  // namespace reminders
