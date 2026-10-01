#define _DEFAULT_SOURCE /* timegm: standard in C23, a GNU/BSD extension before that */
#include "reminders.h"

#include <string.h>

void day_after(time_t now, char out[11]) {
    struct tm t;
    gmtime_r(&now, &t);
    t.tm_mday += 1;          /* may produce "October 32nd"... */
    time_t next = timegm(&t); /* ...which timegm normalises to 1 November */
    gmtime_r(&next, &t);
    strftime(out, 11, "%Y-%m-%d", &t);
}

int send_trial_reminders(const user *users, int n, const mailer *m, clock_fn clock) {
    char target[11];
    day_after(clock(), target);
    int sent = 0;
    for (int i = 0; i < n; i++) {
        if (strcmp(users[i].trial_ends_on, target) == 0) {
            m->send(m->self, users[i].email, "Your trial ends tomorrow");
            sent++;
        }
    }
    return sent;
}
