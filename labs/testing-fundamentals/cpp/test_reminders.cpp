#include <cassert>
#include <iostream>

#include "reminders.hpp"

using namespace std::chrono;

int main() {
    assert(reminders::day_after(2026y / October / 31) == 2026y / November / 1);
    assert(reminders::day_after(2026y / December / 31) == 2027y / January / 1);
    assert(reminders::day_after(2028y / February / 28) == 2028y / February / 29);

    std::vector<reminders::User> users{{"ada@x.com", 2026y / November / 1}, {"bayo@x.com", 2026y / November / 5}};
    std::vector<std::string> sent;
    auto spy = [&](const std::string& to, const std::string& subject) { sent.push_back(to + " | " + subject); };
    auto fixed_today = [] { return 2026y / October / 31; };

    assert(reminders::send_trial_reminders(users, spy, fixed_today) == 1);
    assert(sent == std::vector<std::string>{"ada@x.com | Your trial ends tomorrow"});
    std::cout << "ok: chrono calendar, lambda spy and fixed clock\n";
}
