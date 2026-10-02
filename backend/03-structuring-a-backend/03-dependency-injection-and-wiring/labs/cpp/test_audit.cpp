#include <algorithm>
#include <cassert>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

#include "audit.hpp"

// A fake Log for the test, safe to call from several threads.
class MemoryLog final : public audit::Log {
public:
    void add(std::string entry) override {
        std::lock_guard lock(mutex_);
        entries.push_back(std::move(entry));
    }
    std::vector<std::string> entries;

private:
    std::mutex mutex_;
};

int main() {
    MemoryLog log;
    audit::Service service(log);  // the composition root, for the test

    std::jthread ada([&] { service.record("ada", "viewed invoice"); });
    std::jthread bayo([&] { service.record("bayo", "viewed invoice"); });
    ada.join();
    bayo.join();

    std::ranges::sort(log.entries);
    assert((log.entries == std::vector<std::string>{"ada: viewed invoice", "bayo: viewed invoice"}));
    std::cout << "ok: each request recorded with its own user\n";
}
