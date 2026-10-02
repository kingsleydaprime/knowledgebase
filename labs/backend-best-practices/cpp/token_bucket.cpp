// token_bucket.cpp — a token bucket generic over its clock type, using std::chrono.
// Production uses std::chrono::steady_clock; the test uses a clock it can move.
#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <iostream>
#include <map>
#include <string>

using namespace std::chrono;

template <class Clock>
class TokenBucket {
public:
    TokenBucket(double capacity, double per_second) : capacity_(capacity), per_second_(per_second) {}

    // Returns 0 if allowed, otherwise whole seconds to wait.
    long take(const std::string& key) {
        const auto now = Clock::now();
        auto [it, fresh] = state_.try_emplace(key, State{capacity_, now});
        auto& s = it->second;
        const double elapsed = duration<double>(now - s.at).count();
        s.tokens = std::min(capacity_, s.tokens + elapsed * per_second_);
        s.at = now;
        if (s.tokens >= 1) { s.tokens -= 1; return 0; }
        return static_cast<long>(std::ceil((1 - s.tokens) / per_second_));
    }

private:
    struct State { double tokens; typename Clock::time_point at; };
    double capacity_, per_second_;
    std::map<std::string, State> state_;
};

// A test clock with the same interface as the standard clocks.
struct FakeClock {
    using duration = milliseconds;
    using time_point = std::chrono::time_point<FakeClock>;
    static inline time_point current{};
    static time_point now() { return current; }
};

int main() {
    TokenBucket<FakeClock> bucket(3, 0.5);
    assert(bucket.take("u1") == 0 && bucket.take("u1") == 0 && bucket.take("u1") == 0);
    assert(bucket.take("u1") == 2);
    assert(bucket.take("u2") == 0);
    FakeClock::current += seconds(2);
    assert(bucket.take("u1") == 0);
    std::cout << "ok: token bucket over a chrono clock type\n";
}
