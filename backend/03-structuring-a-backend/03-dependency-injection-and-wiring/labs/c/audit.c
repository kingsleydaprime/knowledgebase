#include "audit.h"

#include <stdio.h>

void audit_record(const audit_log *log, const char *user, const char *action) {
    char entry[128];
    snprintf(entry, sizeof entry, "%s: %s", user, action);
    log->add(log->self, entry);
}
