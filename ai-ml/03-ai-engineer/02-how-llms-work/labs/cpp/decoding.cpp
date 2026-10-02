// From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab,
// plus the standard library's own way to sample: <random>'s discrete_distribution.
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <ranges>
#include <string>
#include <vector>

struct Entry {
    std::string token;
    double p;  // a score before softmax, a probability after
};
using Dist = std::vector<Entry>;

// mulberry32, as a callable object. std::uint32_t arithmetic wraps like JavaScript's >>> 0.
class Mulberry32 {
public:
    explicit Mulberry32(std::uint32_t seed) : a_(seed) {}
    double operator()() {
        a_ += 0x6d2b79f5u;
        std::uint32_t t = a_;
        t = (t ^ (t >> 15)) * (t | 1u);
        t ^= t + (t ^ (t >> 7)) * (t | 61u);
        return static_cast<double>(t ^ (t >> 14)) / 4294967296.0;
    }

private:
    std::uint32_t a_;
};

Dist renormalise(Dist entries) {
    double total = 0;
    for (const auto& e : entries) total += e.p;
    for (auto& e : entries) e.p /= total;
    return entries;
}

Dist softmax(Dist scores, double temperature) {
    double top = std::ranges::max(scores | std::views::transform([&](const Entry& e) { return e.p / temperature; }));
    for (auto& e : scores) e.p = std::exp(e.p / temperature - top);
    return renormalise(std::move(scores));
}

Dist by_probability(Dist dist) {
    std::ranges::stable_sort(dist, std::greater{}, &Entry::p);
    return dist;
}

Dist top_k(const Dist& dist, std::size_t k) {
    Dist sorted = by_probability(dist);
    sorted.resize(std::min(k, sorted.size()));
    return renormalise(std::move(sorted));
}

Dist top_p(const Dist& dist, double p) {
    Dist kept;
    double cumulative = 0;
    for (const auto& e : by_probability(dist)) {
        kept.push_back(e);
        if ((cumulative += e.p) >= p) break;
    }
    return renormalise(std::move(kept));
}

template <typename Random>
std::string sample(const Dist& dist, Random& random) {
    double r = random();
    for (const auto& e : dist)
        if ((r -= e.p) < 0) return e.token;
    return dist.back().token;
}

std::vector<std::string> tokens(const Dist& dist) {
    std::vector<std::string> out;
    for (const auto& e : dist) out.push_back(e.token);
    return out;
}

int main() {
    const Dist scores{{"Paris", 4.0}, {"a", 2.0}, {"the", 1.5}, {"Lyon", 0.5}};
    auto rounded = [](const Dist& d) {
        std::vector<double> out;
        for (const auto& e : d) out.push_back(std::round(e.p * 1000) / 1000);
        return out;
    };
    assert((rounded(softmax(scores, 1)) == std::vector{0.802, 0.108, 0.066, 0.024}));
    assert((rounded(softmax(scores, 0.5)) == std::vector{0.975, 0.018, 0.007, 0.001}));
    assert((rounded(softmax(scores, 2)) == std::vector{0.547, 0.201, 0.157, 0.095}));

    const Dist dist = softmax(scores, 1);
    assert((tokens(top_k(dist, 2)) == std::vector<std::string>{"Paris", "a"}));
    assert((tokens(top_p(dist, 0.9)) == std::vector<std::string>{"Paris", "a"}));
    assert((tokens(top_p(dist, 0.97)) == std::vector<std::string>{"Paris", "a", "the"}));

    Mulberry32 r(42);
    assert(r() == 0.6011037519201636 && r() == 0.44829055899754167 && r() == 0.8524657934904099);

    Mulberry32 r2(42);
    std::string picks;
    for (int i = 0; i < 10; i++) picks += (i ? " " : "") + sample(dist, r2);
    assert(picks == "Paris Paris a Paris Paris Paris Paris Paris a Paris");
    Mulberry32 r3(42);
    int paris = 0;
    for (int i = 0; i < 1000; i++) paris += sample(dist, r3) == "Paris";
    assert(paris == 796);  // about 80.2%, as expected

    // The standard library's version: a seeded engine and a distribution over indices.
    // Same idea, different generator, so different picks, but the same share.
    std::mt19937 engine(42);
    std::discrete_distribution<std::size_t> pick({dist[0].p, dist[1].p, dist[2].p, dist[3].p});
    int std_paris = 0;
    for (int i = 0; i < 1000; i++) std_paris += pick(engine) == 0;
    assert(std_paris > 760 && std_paris < 845);

    std::cout << "ok: decoding matches the TypeScript lab; std::discrete_distribution picked Paris " << std_paris
              << " times in 1000\n";
}
