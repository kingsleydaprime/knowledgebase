// A tick-by-tick simulation of a cascade, and a bulkhead that hands places to waiters in order.
// The same numbers as the TypeScript lab. One tick is 100 ms. Checks run in main.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <climits>
#include <condition_variable>
#include <deque>
#include <iostream>
#include <list>
#include <map>
#include <mutex>
#include <string>
#include <thread>
#include <variant>
#include <vector>

enum class Kind { search, profile };
struct Counts {
    int ok = 0, failed = 0, timed_out = 0, rejected = 0, unfinished = 0;
    bool operator==(const Counts &) const = default;
};
struct Config {
    std::map<Kind, int> pool_of; // the pool each kind uses: the same number means a shared pool
    std::vector<int> sizes;      // workers per pool, in the order pools start work
    int queue_limit, dependency_timeout_ticks;
};
struct Load {
    int ticks;
    std::map<Kind, int> arrivals_per_tick, service_ticks;
    int client_timeout_ticks;
};

std::map<Kind, Counts> simulate(const Config &c, const Load &l) {
    struct Request { Kind kind; int arrived, ends_at = 0; bool failed = false; };
    std::map<Kind, Counts> counts{{Kind::search, {}}, {Kind::profile, {}}};
    std::vector<std::deque<Request>> queues(c.sizes.size());
    std::vector<std::vector<Request>> running(c.sizes.size());
    for (int t = 0; t < l.ticks; t++) {
        for (auto &busy : running) // 1. finished work frees its worker
            std::erase_if(busy, [&](const Request &r) {
                if (r.ends_at > t) return false;
                (r.failed ? counts[r.kind].failed : counts[r.kind].ok)++;
                return true;
            });
        for (auto &queue : queues) // 2. callers who waited too long give up
            std::erase_if(queue, [&](const Request &r) {
                bool gave_up = t - r.arrived >= l.client_timeout_ticks;
                if (gave_up) counts[r.kind].timed_out++;
                return gave_up;
            });
        for (Kind kind : {Kind::search, Kind::profile}) { // 3. new requests arrive, or are turned away
            auto &queue = queues[c.pool_of.at(kind)];
            for (int i = 0; i < l.arrivals_per_tick.at(kind); i++) {
                if (std::ssize(queue) >= c.queue_limit) counts[kind].rejected++; // load shedding
                else queue.push_back({kind, t});
            }
        }
        for (size_t pool = 0; pool < queues.size(); pool++) { // 4. free workers take requests, oldest first
            while (std::ssize(running[pool]) < c.sizes[pool] && !queues[pool].empty()) {
                Request r = queues[pool].front();
                queues[pool].pop_front();
                int needs = l.service_ticks.at(r.kind), limit = r.kind == Kind::search ? c.dependency_timeout_ticks : INT_MAX;
                r.ends_at = t + std::min(needs, limit), r.failed = needs > limit;
                running[pool].push_back(r);
            }
        }
    }
    for (auto &q : queues) for (auto &r : q) counts[r.kind].unfinished++;
    for (auto &b : running) for (auto &r : b) counts[r.kind].unfinished++;
    return counts;
}

// A bulkhead: at most max_concurrent at once, at most max_queue waiting, an immediate "no" beyond that.
// std::counting_semaphore makes no promise about who goes next, so this keeps its own line of waiters.
// A finishing call doesn't free its place: it gives it to the front of the line, so no latecomer barges in.
class Bulkhead {
    std::mutex lock_;
    std::condition_variable called_;
    std::list<bool> line_; // one entry per waiter: true once it has been given a place
    int max_concurrent_, max_queue_, active_ = 0;

public:
    Bulkhead(int max_concurrent, int max_queue) : max_concurrent_(max_concurrent), max_queue_(max_queue) {}

    enum class Refused { full, waited_too_long };

    // The result of fn, or why the call was refused.
    template <class F>
    std::variant<std::invoke_result_t<F>, Refused> run(F fn, std::chrono::milliseconds max_wait) {
        {
            std::unique_lock held(lock_);
            if (active_ < max_concurrent_) {
                active_++;
            } else if (std::ssize(line_) < max_queue_) {
                auto mine = line_.insert(line_.end(), false);
                if (!called_.wait_for(held, max_wait, [&] { return *mine; })) { // false: timed out, still not called
                    line_.erase(mine); // leave the line; no place to give back
                    return Refused::waited_too_long;
                }
                line_.erase(mine); // called: the place passed from the finishing call is ours
            } else {
                return Refused::full; // a fast "no" beats a slow failure
            }
        }
        struct Release { // gives the place back even if fn throws
            Bulkhead *b;
            ~Release() {
                std::lock_guard held(b->lock_);
                auto next = std::find(b->line_.begin(), b->line_.end(), false);
                if (next != b->line_.end()) {
                    *next = true; // hand the place over: active_ stays the same
                    b->called_.notify_all(); // every waiter checks its own entry; only the one called goes
                } else {
                    b->active_--;
                }
            }
        } release{this};
        return fn();
    }

    std::pair<int, int> active_and_waiting() {
        std::lock_guard held(lock_);
        return {active_, static_cast<int>(std::count(line_.begin(), line_.end(), false))};
    }
};

int main() {
    using namespace std::chrono_literals;
    const Load healthy{600, {{Kind::search, 2}, {Kind::profile, 3}}, {{Kind::search, 2}, {Kind::profile, 1}}, 20};
    Load degraded = healthy;
    degraded.service_ticks[Kind::search] = 50;
    auto shared = [](int timeout) { return Config{{{Kind::search, 0}, {Kind::profile, 0}}, {50}, INT_MAX, timeout}; };

    auto h = simulate(shared(INT_MAX), healthy);
    assert(h[Kind::search].ok == 1196 && h[Kind::profile].ok == 1797);
    auto cascade = simulate(shared(INT_MAX), degraded)[Kind::profile];
    assert(cascade.ok == 72 && cascade.timed_out == 1668);
    assert(simulate(shared(30), degraded)[Kind::profile].ok == 270);
    auto one = simulate(shared(10), degraded);
    assert(one[Kind::profile].ok == 1797 && one[Kind::search].failed == 1180);
    auto walls = simulate({{{Kind::search, 0}, {Kind::profile, 1}}, {20, 30}, 10, 30}, degraded);
    assert(walls[Kind::profile].ok == 1797 && (walls[Kind::search] == Counts{0, 380, 190, 600, 30}));

    { // A limit, a short queue, an immediate no, and waiters served in the order they came.
        Bulkhead b(1, 2);
        std::atomic<bool> release = false;
        std::mutex order_lock;
        std::vector<std::string> order;
        auto call = [&](std::string name) {
            return std::jthread([&, name] {
                auto result = b.run([&] {
                    { std::lock_guard held(order_lock); order.push_back(name); }
                    while (!release) std::this_thread::sleep_for(1ms);
                    return 0;
                }, 5s);
                assert(std::holds_alternative<int>(result));
            });
        };
        auto first = call("first");
        while (b.active_and_waiting().first < 1) std::this_thread::sleep_for(1ms);
        auto second = call("second");
        while (b.active_and_waiting().second < 1) std::this_thread::sleep_for(1ms);
        auto third = call("third");
        while (b.active_and_waiting().second < 2) std::this_thread::sleep_for(1ms);
        assert(std::get<Bulkhead::Refused>(b.run([] { return 0; }, 5s)) == Bulkhead::Refused::full);
        release = true;
        first.join(), second.join(), third.join();
        assert((order == std::vector<std::string>{"first", "second", "third"}));
        assert((b.active_and_waiting() == std::pair{0, 0}));
    }
    { // A caller who stops waiting leaves the line and doesn't take a place with them.
        Bulkhead b(1, 1);
        std::atomic<bool> release = false;
        std::jthread first([&] { b.run([&] { while (!release) std::this_thread::sleep_for(1ms); return 0; }, 5s); });
        while (b.active_and_waiting().first < 1) std::this_thread::sleep_for(1ms);
        assert(std::get<Bulkhead::Refused>(b.run([] { return 0; }, 20ms)) == Bulkhead::Refused::waited_too_long);
        release = true;
        first.join();
        assert((b.active_and_waiting() == std::pair{0, 0}));
    }
    { // Never more than the limit, however the threads interleave.
        Bulkhead b(3, 100);
        std::atomic<int> running = 0, most = 0;
        {
            std::vector<std::jthread> callers;
            for (int i = 0; i < 40; i++)
                callers.emplace_back([&] {
                    b.run([&] {
                        int n = ++running;
                        for (int m = most; n > m && !most.compare_exchange_weak(m, n);) {}
                        std::this_thread::sleep_for(50us);
                        return --running;
                    }, 10s);
                });
        } // jthreads join here
        assert(most <= 3 && (b.active_and_waiting() == std::pair{0, 0}));
    }
    std::cout << "all resilience checks passed\n";
}
