// Checks. The fake server is an HttpMessageHandler: HttpClient runs its whole pipeline, minus the network.
using System.Net;
using System.Text;
using System.Text.Json.Nodes;

static void Check<T>(T got, T want)
{
    if (!EqualityComparer<T>.Default.Equals(got, want)) throw new Exception($"got {got}, want {want}");
}
static void CheckAll<T>(IEnumerable<T> got, IEnumerable<T> want)
{
    if (!got.SequenceEqual(want)) throw new Exception($"got [{string.Join(", ", got)}], want [{string.Join(", ", want)}]");
}
static (OpenAICompatibleModel, FakeHandler) Serve(params (HttpStatusCode, string)[] responses)
{
    var handler = new FakeHandler(responses);
    var http = new HttpClient(handler) { BaseAddress = new Uri("http://model.test/v1/"), Timeout = TimeSpan.FromMinutes(2) };
    return (new OpenAICompatibleModel(http, "some-model", "sk-test"), handler);
}

{
    var (model, handler) = Serve((HttpStatusCode.OK,
        """{"choices":[{"message":{"content":"Paris"},"finish_reason":"stop"}],"usage":{"prompt_tokens":21,"completion_tokens":2}}"""));
    var result = await model.ChatAsync([new("user", "Capital of France?")], new(Temperature: 0, MaxTokens: 5));
    Check(result, new ChatResult("Paris", "stop", 21, 2));
    var req = handler.Requests[0];
    Check(req.Url, "http://model.test/v1/chat/completions");
    Check(req.Authorization, "Bearer sk-test");
    Check(req.Body, """{"model":"some-model","messages":[{"role":"user","content":"Capital of France?"}],"stream":false,"temperature":0,"max_tokens":5}""");
}
{
    var (model, _) = Serve((HttpStatusCode.OK, """{"choices":[{"message":{"content":"The capital of"},"finish_reason":"length"}]}"""));
    Check((await model.ChatAsync([])).FinishReason, "length");
}
{
    var (model, _) = Serve((HttpStatusCode.TooManyRequests, "slow down"), (HttpStatusCode.BadRequest, "bad model name"));
    foreach (var (status, retryable) in new[] { (429, true), (400, false) })
    {
        try { await model.ChatAsync([]); throw new Exception("expected an error"); }
        catch (ModelException e) { Check((e.Status, e.Retryable), (status, retryable)); }
    }
}
{
    var raw = "data: {\"a\":1}\n\ndata: {\"b\":\"café\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n";
    var events = new List<string>();
    await foreach (var data in Sse.DataAsync(new OneByteAtATime(Encoding.UTF8.GetBytes(raw)))) events.Add(data);
    CheckAll(events, ["{\"a\":1}", "{\"b\":\"café\"}"]);
}
{
    static string Delta(string text) => $"data: {new JsonObject { ["choices"] = new JsonArray(new JsonObject { ["delta"] = new JsonObject { ["content"] = text } }) }.ToJsonString()}\n\n";
    var (model, handler) = Serve((HttpStatusCode.OK, Delta("Hel") + Delta("lo") + Delta(", world") + "data: [DONE]\n\n"));
    var parts = new List<string>();
    await foreach (var part in model.StreamAsync([new("user", "hi")])) parts.Add(part);
    CheckAll(parts, ["Hel", "lo", ", world"]);
    Check(handler.Requests[0].Body.Contains("\"stream\":true"), true);
}
{
    var (model, handler) = Serve((HttpStatusCode.OK, """{"data":[{"id":"qwen3.5:4b"},{"id":"gemma4:latest"}]}"""));
    CheckAll(await model.ListModelsAsync(), ["gemma4:latest", "qwen3.5:4b"]);
    Check(handler.Requests[0].Url, "http://model.test/v1/models");
}
{
    var model = new FakeModel("Hi Kingsley.", "Your name is Kingsley.");
    var chat = new Conversation(model, "Be brief.");
    await chat.SayAsync("My name is Kingsley.");
    Check(await chat.SayAsync("What's my name?"), "Your name is Kingsley.");
    Check(model.Calls[0].Count, 2);
    CheckAll(model.Calls[1].Select(m => m.Role), ["system", "user", "assistant", "user"]);
}
Console.WriteLine("ok: 7 checks passed");

record Recorded(string Url, string? Authorization, string Body);

class FakeHandler((HttpStatusCode Status, string Body)[] responses) : HttpMessageHandler
{
    readonly Queue<(HttpStatusCode Status, string Body)> _responses = new(responses);
    public List<Recorded> Requests { get; } = [];

    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var body = request.Content is null ? "" : await request.Content.ReadAsStringAsync(ct);
        Requests.Add(new(request.RequestUri!.ToString(), request.Headers.Authorization?.ToString(), body));
        var (status, reply) = _responses.Dequeue();
        return new HttpResponseMessage(status) { Content = new StringContent(reply) };
    }
}

/// <summary>One byte per read: every possible split, including inside a two-byte character.</summary>
class OneByteAtATime(byte[] bytes) : MemoryStream(bytes)
{
    public override int Read(byte[] buffer, int offset, int count) => base.Read(buffer, offset, Math.Min(count, 1));
    public override int Read(Span<byte> buffer) => base.Read(buffer[..Math.Min(buffer.Length, 1)]);
    public override ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken ct = default) =>
        base.ReadAsync(buffer[..Math.Min(buffer.Length, 1)], ct);
    public override Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken ct) =>
        base.ReadAsync(buffer, offset, Math.Min(count, 1), ct);
}
