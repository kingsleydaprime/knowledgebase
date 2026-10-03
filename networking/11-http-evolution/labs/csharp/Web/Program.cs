// Checks: the same results as every other language, plus HTTP/2 multiplexing.
using System.Net;
using System.Net.Sockets;
using System.Text;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var (app, http1, http2) = await Site.StartAsync();

// One connection per client at most, as on a browser's busy origin.
HttpClient Client(int port, bool http2Only) => new(new SocketsHttpHandler { MaxConnectionsPerServer = 1 })
{
    BaseAddress = new Uri($"http://127.0.0.1:{port}"),
    DefaultRequestVersion = http2Only ? HttpVersion.Version20 : HttpVersion.Version11,
    DefaultVersionPolicy = HttpVersionPolicy.RequestVersionExact, // h2c: speak HTTP/2 straight away, no upgrade
};

// Keep-alive: ten requests on one connection, unless each request asks to close it.
foreach (var (keepAlive, expected) in new[] { (false, 10), (true, 1) })
{
    Site.Connections.Clear();
    using var client = Client(http1, false);
    for (var i = 0; i < 10; i++)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, "/fast");
        request.Headers.ConnectionClose = !keepAlive;
        using var response = await client.SendAsync(request);
        Check(await response.Content.ReadAsStringAsync() == "fast", "fast");
    }
    Check(Site.Connections.Count == expected, (keepAlive, Site.Connections.Count));
}

// The slow request first, the fast one 20 ms later; record the order they finish in.
async Task<string[]> FinishOrder(HttpClient client)
{
    var order = new List<string>();
    async Task Fetch(string path, int delay)
    {
        await Task.Delay(delay);
        var body = await client.GetStringAsync(path);
        lock (order) order.Add(body);
    }
    await Task.WhenAll(Fetch("/slow", 0), Fetch("/fast", 20));
    return [.. order];
}
using (var one = Client(http1, false)) Check((await FinishOrder(one)).SequenceEqual(["slow", "fast"]), "HTTP/1.1 order");
Site.Connections.Clear();
using (var multiplexed = Client(http2, true)) Check((await FinishOrder(multiplexed)).SequenceEqual(["fast", "slow"]), "HTTP/2 order");
Check(Site.Connections.Count == 1, Site.Connections.Count);

// Revalidation.
using (var client = Client(http1, false))
{
    using var first = await client.GetAsync("/style.css");
    Check(first.StatusCode == HttpStatusCode.OK && first.Headers.CacheControl?.MaxAge == TimeSpan.FromSeconds(60), first.StatusCode);
    using var request = new HttpRequestMessage(HttpMethod.Get, "/style.css");
    request.Headers.IfNoneMatch.Add(first.Headers.ETag!);
    using var again = await client.SendAsync(request);
    Check(again.StatusCode == HttpStatusCode.NotModified && (await again.Content.ReadAsStringAsync()) == "", again.StatusCode);
}

// Chunked encoding, as bytes on the wire.
using (var socket = new TcpClient())
{
    await socket.ConnectAsync(IPAddress.Loopback, http1);
    var stream = socket.GetStream();
    await stream.WriteAsync(Encoding.ASCII.GetBytes("GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n"));
    var raw = await new StreamReader(stream, Encoding.ASCII).ReadToEndAsync();
    var split = raw.IndexOf("\r\n\r\n");
    Check(raw[..split].Contains("Transfer-Encoding: chunked"), raw[..split]);
    Check(raw[(split + 4)..] == "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n", raw[(split + 4)..]);
}
await app.StopAsync();
Console.WriteLine("all http checks passed");
