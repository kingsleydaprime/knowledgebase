// histogram.cpp — a fixed-bucket histogram with std::array, sized at compile time.
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>

template <std::size_t N>
class Histogram {
public:
    explicit constexpr Histogram(std::array<double, N> bounds) : bounds_(bounds) {}

    void observe(double value) {
        // "le": the first bound >= value; past the end means the +Inf bucket
        auto it = std::lower_bound(bounds_.begin(), bounds_.end(), value);
        ++counts_[static_cast<std::size_t>(it - bounds_.begin())];
    }

    double estimate_quantile(double q) const {
        const double total = static_cast<double>(std::accumulate(counts_.begin(), counts_.end(), 0L));
        const double rank = q * total;
        double lower = 0, cumulative = 0;
        for (std::size_t i = 0; i < counts_.size(); ++i) {
            const double before = cumulative;
            cumulative += static_cast<double>(counts_[i]);
            if (cumulative >= rank) {
                if (i == N) return lower;
                return lower + (bounds_[i] - lower) * (rank - before) / (cumulative - before);
            }
            if (i < N) lower = bounds_[i];
        }
        return lower;
    }

private:
    std::array<double, N> bounds_;
    std::array<long, N + 1> counts_{};
};

int main() {
    Histogram<8> h({25, 50, 100, 250, 500, 1000, 2500, 5000});
    for (int i = 0; i < 97; ++i) h.observe(20 + i % 10);
    for (double ms : {1800.0, 2100.0, 3000.0}) h.observe(ms);
    assert(std::abs(h.estimate_quantile(0.50) - 20.83) < 0.01);   // exact: 24
    assert(h.estimate_quantile(0.99) == 2500);                    // exact: 2100
    std::cout << "ok: p50 ~ 20.83, p99 ~ 2500 from buckets\n";
}
