/* rates.c — decorators in C: a struct holding a function pointer and a pointer to the
 * thing it wraps, all sharing one signature. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct rate_source rate_source;
struct rate_source {
    int (*rate)(const rate_source *self, const char *base, const char *quote, long *out); /* 0 = ok */
    const rate_source *inner;   /* what this one wraps, if anything */
    void *state;
};

/* The flaky API: fails its first `failures` calls. */
typedef struct { int calls, failures; } flaky_state;
static int flaky_rate(const rate_source *self, const char *base, const char *quote, long *out) {
    flaky_state *s = self->state;
    if (++s->calls <= s->failures) return -1;
    *out = (strcmp(base, "GBP") == 0 && strcmp(quote, "NGN") == 0) ? 2000 : 1;
    return 0;
}

/* Decorator: retries. */
static int retry_rate(const rate_source *self, const char *base, const char *quote, long *out) {
    int attempts = *(const int *)self->state;
    for (int i = 0; i < attempts; i++)
        if (self->inner->rate(self->inner, base, quote, out) == 0) return 0;
    return -1;
}

/* Proxy: a one-entry cache. */
typedef struct { int filled; char key[16]; long value; } cache_state;
static int cache_rate(const rate_source *self, const char *base, const char *quote, long *out) {
    cache_state *c = self->state;
    char key[16];
    snprintf(key, sizeof key, "%s%s", base, quote);
    if (c->filled && strcmp(c->key, key) == 0) { *out = c->value; return 0; }
    if (self->inner->rate(self->inner, base, quote, out) != 0) return -1;
    c->filled = 1; snprintf(c->key, sizeof c->key, "%s", key); c->value = *out;
    return 0;
}

int main(void) {
    flaky_state fs = {.failures = 2};
    int attempts = 3;
    cache_state cs = {0};
    rate_source api = {flaky_rate, NULL, &fs};
    rate_source retry = {retry_rate, &api, &attempts};
    rate_source cached = {cache_rate, &retry, &cs};   /* cache(retry(api)) */

    long v = 0;
    assert(cached.rate(&cached, "GBP", "NGN", &v) == 0 && v == 2000);
    assert(cached.rate(&cached, "GBP", "NGN", &v) == 0 && v == 2000);
    assert(fs.calls == 3);
    puts("ok: function-pointer decorators: two failures, then cached");
    return 0;
}
