/* An incremental server-sent events parser: feed it bytes as they arrive from the network
   (libcurl's write callback, say), in chunks split anywhere, and it calls back once per event. */
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void (*on_event)(const char *data, void *context);

typedef struct {
    char *pending; /* bytes received but not yet a complete event */
    size_t length, capacity;
    bool done;     /* saw "data: [DONE]" */
    on_event callback;
    void *context;
} SseParser;

static void sse_init(SseParser *p, on_event callback, void *context) {
    *p = (SseParser){.callback = callback, .context = context};
}

static void sse_free(SseParser *p) { free(p->pending); }

/* Handle one complete event (the text between blank lines): join its "data:" lines. */
static void sse_dispatch(SseParser *p, char *event) {
    char data[4096] = "";
    size_t used = 0;
    for (char *line = strtok(event, "\n"); line; line = strtok(NULL, "\n")) {
        if (strncmp(line, "data:", 5) != 0) continue;
        const char *value = line + 5 + (line[5] == ' ');
        used += (size_t)snprintf(data + used, sizeof data - used, "%s%s", used ? "\n" : "", value);
        if (used >= sizeof data) used = sizeof data - 1; /* truncate rather than overflow */
    }
    if (strcmp(data, "[DONE]") == 0) p->done = true;
    else if (used) p->callback(data, p->context);
}

/* Bytes are bytes: a UTF-8 character split between two chunks is simply joined back up.
   Carriage returns are dropped on the way in, so "\r\n" line endings look like "\n". */
static void sse_feed(SseParser *p, const char *chunk, size_t n) {
    if (p->done) return;
    if (p->length + n + 1 > p->capacity) {
        p->capacity = (p->length + n + 1) * 2;
        char *grown = realloc(p->pending, p->capacity);
        if (!grown) abort();
        p->pending = grown;
    }
    for (size_t i = 0; i < n; i++)
        if (chunk[i] != '\r') p->pending[p->length++] = chunk[i];
    p->pending[p->length] = '\0';

    char *end;
    while (!p->done && (end = strstr(p->pending, "\n\n"))) { /* a blank line ends an event */
        *end = '\0';
        sse_dispatch(p, p->pending);
        size_t used = (size_t)(end + 2 - p->pending);
        memmove(p->pending, end + 2, p->length - used + 1);
        p->length -= used;
    }
}

/* --- checks --- */

typedef struct {
    char events[8][64];
    int count;
} Collected;

static void collect(const char *data, void *context) {
    Collected *c = context;
    snprintf(c->events[c->count++], sizeof c->events[0], "%s", data);
}

int main(void) {
    const char *raw = "data: {\"a\":1}\n\ndata: {\"b\":\"caf\xc3\xa9\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n";

    /* every chunk size from 1 byte up: every possible split, including inside "é" (0xC3 0xA9) */
    for (size_t size = 1; size <= strlen(raw); size++) {
        Collected got = {0};
        SseParser p;
        sse_init(&p, collect, &got);
        for (size_t at = 0; at < strlen(raw); at += size) {
            size_t n = strlen(raw) - at < size ? strlen(raw) - at : size;
            sse_feed(&p, raw + at, n);
        }
        sse_free(&p);
        assert(got.count == 2);
        assert(strcmp(got.events[0], "{\"a\":1}") == 0);
        assert(strcmp(got.events[1], "{\"b\":\"caf\xc3\xa9\"}") == 0);
    }

    /* a multi-line event, with Windows line endings */
    Collected got = {0};
    SseParser p;
    sse_init(&p, collect, &got);
    const char *multi = "data: first\r\ndata: second\r\n\r\n";
    sse_feed(&p, multi, strlen(multi));
    sse_free(&p);
    assert(got.count == 1 && strcmp(got.events[0], "first\nsecond") == 0);

    puts("ok: every split of the stream gives the same two events");
    return 0;
}
