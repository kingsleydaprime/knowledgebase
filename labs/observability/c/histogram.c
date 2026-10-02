/* histogram.c — a fixed-bucket latency histogram: constant memory, one increment per
 * observation. This is how metrics libraries record latency cheaply in hot paths. */
#include <assert.h>
#include <math.h>
#include <stdio.h>

#define NBOUNDS 8
static const double bounds[NBOUNDS] = {25, 50, 100, 250, 500, 1000, 2500, 5000};

typedef struct { long counts[NBOUNDS + 1]; } histogram;   /* the last slot is +Inf */

static void observe(histogram *h, double value) {
    int i = 0;
    while (i < NBOUNDS && value > bounds[i]) i++;          /* "le": less than or equal */
    h->counts[i]++;
}

static double estimate_quantile(const histogram *h, double q) {
    long total = 0;
    for (int i = 0; i <= NBOUNDS; i++) total += h->counts[i];
    double rank = q * (double)total, lower = 0, cumulative = 0;
    for (int i = 0; i <= NBOUNDS; i++) {
        double before = cumulative;
        cumulative += (double)h->counts[i];
        if (cumulative >= rank) {
            if (i == NBOUNDS) return lower;                 /* the +Inf bucket */
            return lower + (bounds[i] - lower) * (rank - before) / (cumulative - before);
        }
        if (i < NBOUNDS) lower = bounds[i];
    }
    return lower;
}

int main(void) {
    histogram h = {0};
    for (int i = 0; i < 97; i++) observe(&h, 20 + i % 10);
    observe(&h, 1800); observe(&h, 2100); observe(&h, 3000);
    assert(fabs(estimate_quantile(&h, 0.50) - 20.83) < 0.01);   /* exact: 24 */
    assert(estimate_quantile(&h, 0.99) == 2500);                /* exact: 2100 */
    puts("ok: p50 ~ 20.83, p99 ~ 2500 from buckets");
    return 0;
}
