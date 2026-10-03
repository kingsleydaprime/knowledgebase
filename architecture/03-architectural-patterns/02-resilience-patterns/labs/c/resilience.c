// A tick-by-tick simulation of a cascade, and a bulkhead that serves waiters in order.
// The same numbers as the TypeScript lab. One tick is 100 ms. Checks run in main.
#define _POSIX_C_SOURCE 200809L // for nanosleep: plain C17 has no way to sleep
#include <assert.h>
#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <time.h>

enum kind { SEARCH, PROFILE, KINDS };
struct counts { int ok, failed, timed_out, rejected, unfinished; };
struct config { int pool_of[KINDS], pools, sizes[2], queue_limit, dependency_timeout_ticks; };
struct load { int ticks, arrivals_per_tick[KINDS], service_ticks[KINDS], client_timeout_ticks; };
struct request { enum kind kind; int arrived, ends_at, failed; };

#define MAX_QUEUE 4096 // more than 600 ticks × 5 arrivals: no request is ever dropped for lack of room

struct pool {
    struct request queue[MAX_QUEUE], running[64];
    int head, len, busy; // the queue is queue[head .. head+len)
};

static void simulate(const struct config *c, const struct load *l, struct counts out[KINDS]) {
    static struct pool pools[2]; // too big for the stack
    for (int p = 0; p < c->pools; p++) pools[p].head = pools[p].len = pools[p].busy = 0;
    for (int k = 0; k < KINDS; k++) out[k] = (struct counts){0};
    for (int t = 0; t < l->ticks; t++) {
        for (int p = 0; p < c->pools; p++) { // 1. finished work frees its worker
            struct pool *pl = &pools[p];
            int kept = 0;
            for (int i = 0; i < pl->busy; i++) {
                struct request r = pl->running[i];
                if (r.ends_at > t) pl->running[kept++] = r;
                else if (r.failed) out[r.kind].failed++;
                else out[r.kind].ok++;
            }
            pl->busy = kept;
        }
        for (int p = 0; p < c->pools; p++) { // 2. callers who waited too long give up (the oldest are at the front)
            struct pool *pl = &pools[p];
            while (pl->len > 0 && t - pl->queue[pl->head].arrived >= l->client_timeout_ticks) {
                out[pl->queue[pl->head].kind].timed_out++;
                pl->head = (pl->head + 1) % MAX_QUEUE, pl->len--;
            }
        }
        for (int k = 0; k < KINDS; k++) { // 3. new requests arrive, or are turned away
            struct pool *pl = &pools[c->pool_of[k]];
            for (int i = 0; i < l->arrivals_per_tick[k]; i++) {
                if (pl->len >= c->queue_limit) out[k].rejected++; // load shedding
                else pl->queue[(pl->head + pl->len++) % MAX_QUEUE] = (struct request){k, t, 0, 0};
            }
        }
        for (int p = 0; p < c->pools; p++) { // 4. free workers take requests, oldest first
            struct pool *pl = &pools[p];
            while (pl->busy < c->sizes[p] && pl->len > 0) {
                struct request r = pl->queue[pl->head];
                pl->head = (pl->head + 1) % MAX_QUEUE, pl->len--;
                int needs = l->service_ticks[r.kind], limit = r.kind == SEARCH ? c->dependency_timeout_ticks : INT_MAX;
                r.ends_at = t + (needs < limit ? needs : limit), r.failed = needs > limit;
                pl->running[pl->busy++] = r;
            }
        }
    }
    for (int p = 0; p < c->pools; p++) {
        for (int i = 0; i < pools[p].len; i++) out[pools[p].queue[(pools[p].head + i) % MAX_QUEUE].kind].unfinished++;
        for (int i = 0; i < pools[p].busy; i++) out[pools[p].running[i].kind].unfinished++;
    }
}

// A bulkhead: at most max_concurrent at once, at most max_queue waiting, an immediate "no" beyond that.
// Each waiter takes a ticket, like at a deli counter. A finishing call doesn't free its place: it calls
// the next ticket, so the place passes straight to the longest waiter and a latecomer can't barge in.
struct bulkhead {
    pthread_mutex_t lock;
    pthread_cond_t called;
    int max_concurrent, max_queue, active, waiting;
    unsigned long next_ticket, now_serving;
};

#define BULKHEAD_INIT(n, q) {PTHREAD_MUTEX_INITIALIZER, PTHREAD_COND_INITIALIZER, (n), (q), 0, 0, 0, 0}

// Returns 0 and runs fn, or returns -1 at once if the bulkhead is full.
static int bulkhead_run(struct bulkhead *b, void (*fn)(void *), void *arg) {
    pthread_mutex_lock(&b->lock);
    if (b->active < b->max_concurrent) {
        b->active++;
    } else if (b->waiting < b->max_queue) {
        unsigned long mine = b->next_ticket++;
        b->waiting++;
        while (b->now_serving <= mine) pthread_cond_wait(&b->called, &b->lock); // woken spuriously? wait again
    } else {
        pthread_mutex_unlock(&b->lock);
        return -1; // a fast "no" beats a slow failure
    }
    pthread_mutex_unlock(&b->lock);
    fn(arg);
    pthread_mutex_lock(&b->lock);
    if (b->waiting > 0) {
        b->waiting--;
        b->now_serving++; // hand the place over: active stays the same
        pthread_cond_broadcast(&b->called); // every waiter checks; only the one called goes
    } else {
        b->active--;
    }
    pthread_mutex_unlock(&b->lock);
    return 0;
}

static int waiting(struct bulkhead *b) {
    pthread_mutex_lock(&b->lock);
    int w = b->waiting;
    pthread_mutex_unlock(&b->lock);
    return w;
}

static void nap(long microseconds) {
    nanosleep(&(struct timespec){0, microseconds * 1000}, NULL);
}

// Test helpers: a call that holds its place until released, and records the order calls started in.
static atomic_int release_count, running_now, most, started_order[8], started;

static void hold(void *name) {
    started_order[atomic_fetch_add(&started, 1)] = (int)(long)name;
    int n = atomic_fetch_add(&running_now, 1) + 1;
    for (int m = atomic_load(&most); n > m && !atomic_compare_exchange_weak(&most, &m, n);) {}
    for (int r;;) { // wait to be released, taking one release
        r = atomic_load(&release_count);
        if (r > 0 && atomic_compare_exchange_weak(&release_count, &r, r - 1)) break;
        nap(100);
    }
    atomic_fetch_sub(&running_now, 1);
}

struct call { struct bulkhead *b; long name; int result; };
static void *caller(void *arg) {
    struct call *c = arg;
    c->result = bulkhead_run(c->b, hold, (void *)c->name);
    return NULL;
}

static void quick(void *arg) {
    int n = atomic_fetch_add(&running_now, 1) + 1;
    for (int m = atomic_load(&most); n > m && !atomic_compare_exchange_weak(&most, &m, n);) {}
    nap(50);
    atomic_fetch_sub(&running_now, 1);
    (void)arg;
}
static void *quick_caller(void *b) {
    while (bulkhead_run(b, quick, NULL) != 0) nap(10); // full? try again shortly
    return NULL;
}

int main(void) {
    const struct load healthy = {600, {2, 3}, {2, 1}, 20}, degraded = {600, {2, 3}, {50, 1}, 20};
    struct config shared = {{0, 0}, 1, {50}, INT_MAX, INT_MAX};
    struct counts out[KINDS];

    simulate(&shared, &healthy, out);
    assert(out[SEARCH].ok == 1196 && out[PROFILE].ok == 1797);
    simulate(&shared, &degraded, out);
    assert(out[PROFILE].ok == 72 && out[PROFILE].timed_out == 1668); // the cascade
    shared.dependency_timeout_ticks = 30;
    simulate(&shared, &degraded, out);
    assert(out[PROFILE].ok == 270);
    shared.dependency_timeout_ticks = 10;
    simulate(&shared, &degraded, out);
    assert(out[PROFILE].ok == 1797 && out[SEARCH].failed == 1180);
    const struct config walls = {{0, 1}, 2, {20, 30}, 10, 30};
    simulate(&walls, &degraded, out);
    assert(out[PROFILE].ok == 1797);
    assert(out[SEARCH].failed == 380 && out[SEARCH].timed_out == 190 && out[SEARCH].rejected == 600 && out[SEARCH].unfinished == 30);

    // A limit, a short queue, an immediate no, and waiters served in the order they came.
    struct bulkhead b = BULKHEAD_INIT(1, 2);
    struct call calls[3] = {{&b, 1, 9}, {&b, 2, 9}, {&b, 3, 9}};
    pthread_t threads[3];
    pthread_create(&threads[0], NULL, caller, &calls[0]);
    while (atomic_load(&started) < 1) nap(100);
    for (int i = 1; i < 3; i++) { // queue 2, then 3, in that order
        pthread_create(&threads[i], NULL, caller, &calls[i]);
        while (waiting(&b) < i) nap(100);
    }
    struct call fourth = {&b, 4, 9};
    caller(&fourth);
    assert(fourth.result == -1);
    atomic_store(&release_count, 3);
    for (int i = 0; i < 3; i++) pthread_join(threads[i], NULL), assert(calls[i].result == 0);
    assert(started_order[0] == 1 && started_order[1] == 2 && started_order[2] == 3);
    assert(b.active == 0 && b.waiting == 0);

    // Never more than the limit, however the threads interleave.
    struct bulkhead three = BULKHEAD_INIT(3, 5);
    pthread_t many[40];
    atomic_store(&most, 0);
    for (int i = 0; i < 40; i++) pthread_create(&many[i], NULL, quick_caller, &three);
    for (int i = 0; i < 40; i++) pthread_join(many[i], NULL);
    assert(atomic_load(&most) <= 3 && three.active == 0);

    puts("all resilience checks passed");
}
