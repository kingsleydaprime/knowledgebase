// The same small site as the TypeScript lab, on Kestrel: HTTP/1.1 on one port and HTTP/2 without TLS on another.
// Without TLS there's no ALPN to choose a version, so an h2c endpoint must speak HTTP/2 only.
using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Hosting.Server.Features;
using Microsoft.AspNetCore.Server.Kestrel.Core;

public static class Site
{
    static readonly byte[] Asset = Encoding.UTF8.GetBytes("body { color: rebeccapurple; }\n");
    static readonly string ETag = $"\"{Convert.ToHexStringLower(SHA256.HashData(Asset))[..16]}\"";

    /// <summary>Kestrel's connection IDs seen: one per TCP connection.</summary>
    public static readonly ConcurrentDictionary<string, bool> Connections = new();

    public static async Task<(WebApplication App, int Http1Port, int Http2Port)> StartAsync()
    {
        var builder = WebApplication.CreateSlimBuilder();
        builder.Logging.ClearProviders();
        builder.WebHost.ConfigureKestrel(k =>
        {
            k.Listen(System.Net.IPAddress.Loopback, 0, o => o.Protocols = HttpProtocols.Http1);
            k.Listen(System.Net.IPAddress.Loopback, 0, o => o.Protocols = HttpProtocols.Http2); // h2c: prior knowledge only
        });
        var app = builder.Build();
        app.Use(async (context, next) =>
        {
            Connections.TryAdd(context.Connection.Id, true);
            await next();
        });
        app.MapGet("/fast", () => "fast");
        app.MapGet("/slow", async () =>
        {
            await Task.Delay(200);
            return "slow";
        });
        app.MapGet("/style.css", (HttpContext context) =>
        {
            context.Response.Headers.ETag = ETag;
            if (context.Request.Headers.IfNoneMatch == ETag) return Results.StatusCode(304); // headers only
            context.Response.Headers.CacheControl = "max-age=60";
            return Results.Bytes(Asset, "text/css");
        });
        app.MapGet("/stream", async (HttpContext context) =>
        {
            await context.Response.WriteAsync("hello"); // no Content-Length: HTTP/1.1 goes chunked
            await context.Response.Body.FlushAsync();
            await Task.Delay(20);
            await context.Response.WriteAsync(" world");
        });
        await app.StartAsync();
        var ports = app.Services.GetRequiredService<Microsoft.AspNetCore.Hosting.Server.IServer>().Features.Get<IServerAddressesFeature>()!
            .Addresses.Select(a => new Uri(a).Port).ToArray();
        return (app, ports[0], ports[1]);
    }
}
