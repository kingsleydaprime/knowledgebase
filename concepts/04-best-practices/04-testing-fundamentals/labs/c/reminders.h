#ifndef REMINDERS_H
#define REMINDERS_H

#include <time.h>

typedef struct { const char *email; const char *trial_ends_on; } user;   /* dates as "YYYY-MM-DD" */

/* Collaborators as function pointers: the clock and the mailer. */
typedef time_t (*clock_fn)(void);
typedef void (*send_fn)(void *self, const char *to, const char *subject);
typedef struct { void *self; send_fn send; } mailer;

/* Writes the UTC day after `now` into out ("YYYY-MM-DD"). */
void day_after(time_t now, char out[11]);
int send_trial_reminders(const user *users, int n, const mailer *m, clock_fn clock);

#endif
