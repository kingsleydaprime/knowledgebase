using Microsoft.Extensions.DependencyInjection;

// 1. The bug, caught at startup: a singleton that captures a per-request (scoped) service.
var captive = new ServiceCollection();
captive.AddSingleton<AuditLog>();
captive.AddScoped<RequestContext>();      // one per request
captive.AddSingleton<CaptiveAuditService>(); // one for the whole app — holding a RequestContext
try
{
    captive.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });
    throw new Exception("FAIL: the container accepted a scoped service inside a singleton");
}
catch (AggregateException e) when (e.InnerException is InvalidOperationException inner)
{
    Console.WriteLine($"caught at startup: {inner.Message}");
}

// 2. The fix: the service that needs request data is scoped too.
var services = new ServiceCollection();
services.AddSingleton<AuditLog>();
services.AddScoped<RequestContext>();
services.AddScoped<AuditService>();
using var provider = services.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });

async Task HandleRequest(string user)
{
    using var scope = provider.CreateScope();            // ASP.NET Core does this per HTTP request
    scope.ServiceProvider.GetRequiredService<RequestContext>().User = user;
    await scope.ServiceProvider.GetRequiredService<AuditService>().Record("viewed invoice");
}
await Task.WhenAll(HandleRequest("ada"), HandleRequest("bayo"));

var entries = provider.GetRequiredService<AuditLog>().Entries.Order().ToList();
if (!entries.SequenceEqual(["ada: viewed invoice", "bayo: viewed invoice"]))
    throw new Exception($"FAIL: {string.Join(", ", entries)}");
Console.WriteLine($"scoped: {string.Join(", ", entries)}");

sealed class AuditLog
{
    private readonly List<string> _entries = [];
    public void Add(string entry) { lock (_entries) _entries.Add(entry); }
    public IReadOnlyList<string> Entries { get { lock (_entries) return [.. _entries]; } }
}

sealed class RequestContext { public string User { get; set; } = "nobody"; }

sealed class CaptiveAuditService(AuditLog log, RequestContext context)
{
    public void Record(string action) => log.Add($"{context.User}: {action}");
}

sealed class AuditService(AuditLog log, RequestContext context)
{
    public async Task Record(string action)
    {
        await Task.Delay(5); // other requests run here; each still sees its own RequestContext
        log.Add($"{context.User}: {action}");
    }
}
