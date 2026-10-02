/* audit.h — dependency injection in C: a struct of function pointers is the interface,
 * and the caller passes it in. */
#ifndef AUDIT_H
#define AUDIT_H

#include <stddef.h>

typedef struct {
    void *self;                                    /* the implementation's own state */
    void (*add)(void *self, const char *entry);    /* the one operation the audit needs */
} audit_log;

/* The fix for the scope bug is the same as everywhere: the user is an argument. */
void audit_record(const audit_log *log, const char *user, const char *action);

#endif
