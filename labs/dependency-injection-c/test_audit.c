/* A fake log that remembers entries — the test's stand-in for a database. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "audit.h"

typedef struct {
    char entries[4][128];
    int count;
} memory_log;

static void memory_add(void *self, const char *entry) {
    memory_log *m = self;
    snprintf(m->entries[m->count++], sizeof m->entries[0], "%s", entry);
}

int main(void) {
    memory_log memory = {0};
    audit_log log = {.self = &memory, .add = memory_add};   /* the composition root, for the test */

    audit_record(&log, "ada", "viewed invoice");
    audit_record(&log, "bayo", "viewed invoice");

    assert(memory.count == 2);
    assert(strcmp(memory.entries[0], "ada: viewed invoice") == 0);
    assert(strcmp(memory.entries[1], "bayo: viewed invoice") == 0);
    puts("ok: audit records through an injected log");
    return 0;
}
