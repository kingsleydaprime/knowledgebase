// The parts of a model client that don't need an HTTP library: the port as an abstract class,
// a fake, a stateless-model conversation, and an incremental SSE parser to feed from libcurl.
#include <cassert>
#include <deque>
#include <functional>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

struct Message {
    std::string role;  // "system", "user" or "assistant"
    std::string content;
};

struct Options {
    std::optional<double> temperature;  // empty means "use the server's default"
    std::optional<int> max_tokens;
};

struct ChatResult {
    std::string text;
    std::string finish_reason;  // "stop", "length" (max tokens cut it off) or "other"
};

// The port: all the rest of the app knows about a model.
class ChatModel {
public:
    virtual ~ChatModel() = default;
    virtual ChatResult chat(const std::vector<Message>& messages, const Options& options) = 0;
};

// For tests: replies from a script and records what it was sent.
class FakeModel : public ChatModel {
public:
    explicit FakeModel(std::deque<std::string> replies) : replies_(std::move(replies)) {}
    ChatResult chat(const std::vector<Message>& messages, const Options&) override {
        calls.push_back(messages);  // a copy: later changes to the conversation don't rewrite history
        std::string reply = replies_.front();
        replies_.pop_front();
        return {reply, "stop"};
    }
    std::vector<std::vector<Message>> calls;

private:
    std::deque<std::string> replies_;
};

// The model is stateless: "memory" is the app resending every earlier turn on every call.
class Conversation {
public:
    Conversation(ChatModel& model, std::string system) : model_(model) { messages_.push_back({"system", std::move(system)}); }
    std::string say(std::string content) {
        messages_.push_back({"user", std::move(content)});
        std::string text = model_.chat(messages_, {}).text;
        messages_.push_back({"assistant", text});
        return text;
    }

private:
    ChatModel& model_;  // borrowed: the caller owns the model and must keep it alive
    std::vector<Message> messages_;
};

// Feed bytes as they arrive, split anywhere; get one callback per complete event.
class SseParser {
public:
    explicit SseParser(std::function<void(std::string_view)> on_event) : on_event_(std::move(on_event)) {}

    void feed(std::string_view chunk) {
        for (char c : chunk)
            if (c != '\r') pending_ += c;  // "\r\n" line endings become "\n"
        for (std::size_t end; !done_ && (end = pending_.find("\n\n")) != std::string::npos;) {
            dispatch(std::string_view(pending_).substr(0, end));
            pending_.erase(0, end + 2);  // keep only the unfinished tail
        }
    }

private:
    void dispatch(std::string_view event) {
        std::string data;
        while (!event.empty()) {
            std::size_t eol = event.find('\n');
            std::string_view line = event.substr(0, eol);
            event = eol == std::string_view::npos ? std::string_view{} : event.substr(eol + 1);
            if (!line.starts_with("data:")) continue;
            line.remove_prefix(line.starts_with("data: ") ? 6 : 5);
            if (!data.empty()) data += '\n';
            data += line;
        }
        if (data == "[DONE]") done_ = true;
        else if (!data.empty()) on_event_(data);
    }

    std::function<void(std::string_view)> on_event_;
    std::string pending_;
    bool done_ = false;
};

int main() {
    // Every chunk size from 1 byte up: every split, including inside "é" (0xC3 0xA9).
    const std::string raw = "data: {\"a\":1}\n\ndata: {\"b\":\"caf\xc3\xa9\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n";
    for (std::size_t size = 1; size <= raw.size(); size++) {
        std::vector<std::string> events;
        SseParser parser([&](std::string_view data) { events.emplace_back(data); });
        for (std::size_t at = 0; at < raw.size(); at += size) parser.feed(std::string_view(raw).substr(at, size));
        assert((events == std::vector<std::string>{"{\"a\":1}", "{\"b\":\"caf\xc3\xa9\"}"}));
    }

    std::vector<std::string> events;
    SseParser parser([&](std::string_view data) { events.emplace_back(data); });
    parser.feed("data: first\r\ndata: second\r\n\r\n");
    assert((events == std::vector<std::string>{"first\nsecond"}));

    FakeModel model({"Hi Kingsley.", "Your name is Kingsley."});
    Conversation chat(model, "Be brief.");
    chat.say("My name is Kingsley.");
    assert(chat.say("What's my name?") == "Your name is Kingsley.");
    assert(model.calls[0].size() == 2);
    std::vector<std::string> roles;
    for (const auto& m : model.calls[1]) roles.push_back(m.role);
    assert((roles == std::vector<std::string>{"system", "user", "assistant", "user"}));

    std::cout << "ok: every split of the stream gives the same events; the conversation resends every turn\n";
}
