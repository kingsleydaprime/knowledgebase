#define _DEFAULT_SOURCE
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "reminders.h"

static time_t utc(int y, int mo, int d) {
    struct tm t = {.tm_year = y - 1900, .tm_mon = mo - 1, .tm_mday = d, .tm_hour = 12};
    return timegm(&t);
}

static time_t oct31(void) { return utc(2026, 10, 31); }   /* the fake clock */

typedef struct { char last[64]; int calls; } spy;
static void spy_send(void *self, const char *to, const char *subject) {
    spy *s = self;
    snprintf(s->last, sizeof s->last, "%s | %s", to, subject);
    s->calls++;
}

int main(void) {
    char out[11];
    day_after(utc(2026, 10, 31), out); assert(strcmp(out, "2026-11-01") == 0);
    day_after(utc(2026, 12, 31), out); assert(strcmp(out, "2027-01-01") == 0);
    day_after(utc(2028, 2, 28), out);  assert(strcmp(out, "2028-02-29") == 0);

    user users[] = {{"ada@x.com", "2026-11-01"}, {"bayo@x.com", "2026-11-05"}};
    spy s = {0};
    mailer m = {.self = &s, .send = spy_send};
    assert(send_trial_reminders(users, 2, &m, oct31) == 1);
    assert(s.calls == 1 && strcmp(s.last, "ada@x.com | Your trial ends tomorrow") == 0);
    puts("ok: function-pointer clock and spy");
    return 0;
}
