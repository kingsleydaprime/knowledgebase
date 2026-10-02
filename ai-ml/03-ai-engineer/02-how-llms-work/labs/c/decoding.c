/* From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab. */
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char *token;
    double p; /* a score before softmax, a probability after */
} Entry;

/* mulberry32. uint32_t arithmetic wraps, exactly like JavaScript's >>> 0. */
typedef struct { uint32_t a; } Rng;

static double next_random(Rng *rng) {
    rng->a += 0x6d2b79f5u;
    uint32_t t = rng->a;
    t = (t ^ (t >> 15)) * (t | 1u);
    t ^= t + (t ^ (t >> 7)) * (t | 61u);
    return (double)(t ^ (t >> 14)) / 4294967296.0;
}

/* Softmax in place: n entries, scores in, probabilities out. */
static void softmax(Entry *e, size_t n, double temperature) {
    double top = -INFINITY, total = 0;
    for (size_t i = 0; i < n; i++) top = fmax(top, e[i].p / temperature);
    for (size_t i = 0; i < n; i++) total += e[i].p = exp(e[i].p / temperature - top);
    for (size_t i = 0; i < n; i++) e[i].p /= total;
}

static int by_probability_desc(const void *x, const void *y) {
    double px = ((const Entry *)x)->p, py = ((const Entry *)y)->p;
    return (px < py) - (px > py);
}

/* Top-p in place: sorts, keeps the smallest prefix reaching p, renormalises. Returns the new length.
   (qsort isn't stable; ties don't occur in this example.) */
static size_t top_p(Entry *e, size_t n, double p) {
    qsort(e, n, sizeof *e, by_probability_desc);
    size_t kept = 0;
    double cumulative = 0;
    while (kept < n && cumulative < p) cumulative += e[kept++].p;
    for (size_t i = 0; i < kept; i++) e[i].p /= cumulative;
    return kept;
}

static const char *sample(const Entry *e, size_t n, Rng *rng) {
    double r = next_random(rng);
    for (size_t i = 0; i < n; i++)
        if ((r -= e[i].p) < 0) return e[i].token;
    return e[n - 1].token;
}

/* --- checks --- */

static Entry scores[] = {{"Paris", 4.0}, {"a", 2.0}, {"the", 1.5}, {"Lyon", 0.5}};
#define N (sizeof scores / sizeof scores[0])

static void expect_rounded(double temperature, const double want[N]) {
    Entry e[N];
    memcpy(e, scores, sizeof scores);
    softmax(e, N, temperature);
    for (size_t i = 0; i < N; i++) assert(round(e[i].p * 1000) / 1000 == want[i]);
}

int main(void) {
    expect_rounded(1, (double[]){0.802, 0.108, 0.066, 0.024});
    expect_rounded(0.5, (double[]){0.975, 0.018, 0.007, 0.001});
    expect_rounded(2, (double[]){0.547, 0.201, 0.157, 0.095});

    Entry dist[N];
    memcpy(dist, scores, sizeof scores);
    softmax(dist, N, 1);

    Entry nucleus[N];
    memcpy(nucleus, dist, sizeof dist);
    size_t kept = top_p(nucleus, N, 0.9);
    assert(kept == 2 && strcmp(nucleus[0].token, "Paris") == 0 && strcmp(nucleus[1].token, "a") == 0);

    Rng rng = {42};
    assert(next_random(&rng) == 0.6011037519201636);
    assert(next_random(&rng) == 0.44829055899754167);
    assert(next_random(&rng) == 0.8524657934904099);

    char picks[128] = "";
    rng = (Rng){42};
    for (int i = 0; i < 10; i++) {
        if (i) strcat(picks, " ");
        strcat(picks, sample(dist, N, &rng));
    }
    assert(strcmp(picks, "Paris Paris a Paris Paris Paris Paris Paris a Paris") == 0);

    rng = (Rng){42};
    int paris = 0;
    for (int i = 0; i < 1000; i++) paris += strcmp(sample(dist, N, &rng), "Paris") == 0;
    assert(paris == 796); /* about 80.2%, as expected */

    puts("ok: decoding matches the TypeScript lab");
    return 0;
}
