#pragma once
#include <string>
#include <string_view>

namespace audit {

// The interface: an abstract class. Implementations override `add`.
class Log {
public:
    virtual ~Log() = default;
    virtual void add(std::string entry) = 0;
};

// Constructor injection: the service holds a reference to whatever Log it was given.
class Service {
public:
    explicit Service(Log& log) : log_(log) {}
    void record(std::string_view user, std::string_view action) {
        log_.add(std::string(user) + ": " + std::string(action));
    }

private:
    Log& log_;
};

}  // namespace audit
