#include "users.h"

#include <string.h>

static const char *known_ids[] = {"u1"}; /* static: invisible outside this file */

bool users_exists(const char *user_id) {
    for (size_t i = 0; i < sizeof known_ids / sizeof known_ids[0]; i++) {
        if (strcmp(known_ids[i], user_id) == 0) return true;
    }
    return false;
}
