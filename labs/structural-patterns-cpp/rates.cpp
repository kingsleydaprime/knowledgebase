// rates.cpp — decorators as class templates over any type with a matching rate() (a C++20
// concept), so the whole stack is one concrete type the compiler can inline.
#include <cassert>
#include <concepts>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>

template <class T>
concept RateSource = requires(T& t, const std::string& s) { { t.rate(s, s) } -> std::same_as<long>; };

struct FlakyApi {
    int calls = 0, failures = 0;
    long rate(const std::string& base, const std::string& quote) {
        if (++calls <= failures) throw std::runtime_error("503 from rates API");
        return base == "GBP" && quote == "NGN" ? 2000 : 1;
    }
};

template <RateSource Inner>
struct Retrying {
    Inner& inner;
    int attempts;
    long rate(const std::string& base, const std::string& quote) {
        for (int i = 1;; ++i) {
            try { return inner.rate(base, quote); }
            catch (const std::runtime_error&) { if (i == attempts) throw; }
        }
    }
};

template <RateSource Inner>
struct Caching {
    Inner& inner;
    std::map<std::string, long> cache;
    long rate(const std::string& base, const std::string& quote) {
        auto key = base + "->" + quote;
        if (auto hit = cache.find(key); hit != cache.end()) return hit->second;
        return cache[key] = inner.rate(base, quote);
    }
};

int main() {
    FlakyApi api{.failures = 2};
    Retrying<FlakyApi> retry{api, 3};
    Caching<Retrying<FlakyApi>> cached{retry, {}};
    assert(cached.rate("GBP", "NGN") == 2000);
    assert(cached.rate("GBP", "NGN") == 2000);
    assert(api.calls == 3);

    FlakyApi worse{.failures = 5};
    Retrying<FlakyApi> gives_up{worse, 3};
    bool threw = false;
    try { gives_up.rate("GBP", "NGN"); } catch (const std::runtime_error&) { threw = true; }
    assert(threw);
    std::cout << "ok: template decorators constrained by a concept\n";
}
