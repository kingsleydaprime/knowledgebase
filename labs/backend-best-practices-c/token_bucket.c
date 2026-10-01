/* token_bucket.c — a token bucket in milli-tokens (integers, no floating point), with the
 * current time passed in by the caller. */
#include <assert.h>
#include <stdio.h>

typedef struct {
    long capacity_milli;     /* 3 tokens = 3000 */
    long refill_milli_per_s; /* 0.5 tokens/s = 500 */
    long tokens_milli;
    long at_ms;
} token_bucket;

/* Returns 0 if allowed; otherwise the seconds to wait. */
static long take(token_bucket *b, long now_ms) {
    long refilled = b->tokens_milli + (now_ms - b->at_ms) * b->refill_milli_per_s / 1000;
    b->tokens_milli = refilled < b->capacity_milli ? refilled : b->capacity_milli;
    b->at_ms = now_ms;
    if (b->tokens_milli >= 1000) {
        b->tokens_milli -= 1000;
        return 0;
    }
    long missing = 1000 - b->tokens_milli;
    return (missing * 1000 / b->refill_milli_per_s + 999) / 1000;   /* round up to whole seconds */
}

int main(void) {
    token_bucket b = {.capacity_milli = 3000, .refill_milli_per_s = 500, .tokens_milli = 3000, .at_ms = 0};
    assert(take(&b, 0) == 0 && take(&b, 0) == 0 && take(&b, 0) == 0);
    assert(take(&b, 0) == 2);       /* fourth request: wait 2 seconds */
    assert(take(&b, 2000) == 0);    /* refilled */
    puts("ok: integer token bucket");
    return 0;
}
