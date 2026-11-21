// A provider-neutral model client: the port, a fake, an OpenAI-compatible adapter and an SSE reader.
// In production .NET, Microsoft.Extensions.AI's IChatClient is the standard port, with adapters for
// OpenAI, Ollama and Azure; this is the same shape, written out so you can see what it does.
using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

public record Message(string Role, string Content); // Role: "system", "user" or "assistant"

public record Options(double? Temperature = null, int? MaxTokens = null); // null: the server's default

public record ChatResult(string Text, string FinishReason, int InputTokens, int OutputTokens); // "stop", "length" or "other"

/// <summary>The port: all the rest of the app knows about a model.</summary>
public interface IChatModel
{
    Task<ChatResult> ChatAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default);
    IAsyncEnumerable<string> StreamAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default);
}

/// <summary>The model is stateless: "memory" is the app resending every earlier turn on every call.</summary>
public class Conversation(IChatModel model, string system)
{
    public List<Message> Messages { get; } = [new("system", system)];

    public async Task<string> SayAsync(string content)
    {
        Messages.Add(new("user", content));
        var text = (await model.ChatAsync([.. Messages])).Text;
        Messages.Add(new("assistant", text));
        return text;
    }
}

/// <summary>For tests: replies from a script and records what it was sent.</summary>
public class FakeModel(params string[] replies) : IChatModel
{
    readonly Queue<string> _replies = new(replies);
    public List<List<Message>> Calls { get; } = [];

    public Task<ChatResult> ChatAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default)
    {
        Calls.Add([.. messages]);
        return Task.FromResult(new ChatResult(_replies.Dequeue(), "stop", 0, 0));
    }

    public async IAsyncEnumerable<string> StreamAsync(IReadOnlyList<Message> messages, Options? options = null,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        foreach (var word in (await ChatAsync(messages, options, ct)).Text.Split(' ')) yield return word;
    }
}

public class ModelException(int status, string body)
    : Exception($"model request failed: {status} {body[..Math.Min(200, body.Length)]}")
{
    public int Status { get; } = status;
    public bool Retryable => Status == 429 || Status >= 500; // rate limits and server errors; never a 400
}

public static class Sse
{
    /// <summary>Reads server-sent events. StreamReader holds half a character and half a line between
    /// reads, so chunk boundaries never show through.</summary>
    public static async IAsyncEnumerable<string> DataAsync(Stream body, [EnumeratorCancellation] CancellationToken ct = default)
    {
        using var reader = new StreamReader(body, Encoding.UTF8);
        var data = new List<string>();
        while (await reader.ReadLineAsync(ct) is { } line) // ReadLine also strips "\r\n"
        {
            if (line.StartsWith("data:")) data.Add(line[5..].TrimStart());
            else if (line.Length == 0 && data.Count > 0)
            {
                var ev = string.Join("\n", data); // a blank line ends the event
                data.Clear();
                if (ev == "[DONE]") yield break;
                yield return ev;
            }
        }
    }
}

/// <summary>Any server speaking the OpenAI chat completions format. Give the HttpClient a Timeout.</summary>
public class OpenAICompatibleModel(HttpClient http, string model, string? apiKey = null,
    IReadOnlyDictionary<string, object?>? extraBody = null) : IChatModel
{
    public async Task<ChatResult> ChatAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default)
    {
        using var res = await PostAsync(messages, options, stream: false, ct);
        var data = JsonNode.Parse(await res.Content.ReadAsStringAsync(ct))!;
        var choice = data["choices"]![0]!;
        var reason = (string?)choice["finish_reason"] switch { "stop" => "stop", "length" => "length", _ => "other" };
        return new ChatResult((string?)choice["message"]?["content"] ?? "", reason,
            (int?)data["usage"]?["prompt_tokens"] ?? 0, (int?)data["usage"]?["completion_tokens"] ?? 0);
    }

    public async IAsyncEnumerable<string> StreamAsync(IReadOnlyList<Message> messages, Options? options = null,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        using var res = await PostAsync(messages, options, stream: true, ct); // disposed when the caller stops
        await foreach (var data in Sse.DataAsync(await res.Content.ReadAsStreamAsync(ct), ct))
            if ((string?)JsonNode.Parse(data)!["choices"]?[0]?["delta"]?["content"] is { Length: > 0 } delta)
                yield return delta;
    }

    /// <summary>Never hard-code model names from memory: ask the server.</summary>
    public async Task<List<string>> ListModelsAsync(CancellationToken ct = default)
    {
        using var res = await SendAsync(new HttpRequestMessage(HttpMethod.Get, "models"), HttpCompletionOption.ResponseContentRead, ct);
        var data = JsonNode.Parse(await res.Content.ReadAsStringAsync(ct))!;
        return [.. data["data"]!.AsArray().Select(m => (string)m!["id"]!).Order()];
    }

    Task<HttpResponseMessage> PostAsync(IReadOnlyList<Message> messages, Options? options, bool stream, CancellationToken ct)
    {
        var body = new JsonObject
        {
            ["model"] = model,
            ["messages"] = JsonSerializer.SerializeToNode(messages.Select(m => new { role = m.Role, content = m.Content })),
            ["stream"] = stream,
        };
        foreach (var (key, value) in extraBody ?? new Dictionary<string, object?>()) body[key] = JsonSerializer.SerializeToNode(value);
        if (options?.Temperature is { } t) body["temperature"] = t;
        if (options?.MaxTokens is { } n) body["max_tokens"] = n;
        var request = new HttpRequestMessage(HttpMethod.Post, "chat/completions") { Content = JsonContent.Create(body) };
        // ResponseHeadersRead: return as soon as headers arrive, so streaming starts before the body ends
        return SendAsync(request, HttpCompletionOption.ResponseHeadersRead, ct);
    }

    async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, HttpCompletionOption completion, CancellationToken ct)
    {
        if (apiKey is not null) request.Headers.Authorization = new("Bearer", apiKey);
        var res = await http.SendAsync(request, completion, ct);
        if (res.IsSuccessStatusCode) return res;
        using (res) throw new ModelException((int)res.StatusCode, await res.Content.ReadAsStringAsync(ct));
    }
}
