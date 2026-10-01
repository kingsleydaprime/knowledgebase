// ASP.NET Core: a named CORS policy with an allowlist, and a small middleware for the
// security headers. (app.UseHsts() adds HSTS too, but only outside Development and over HTTPS.)
var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Services.AddCors(options => options.AddPolicy("frontend", policy => policy
    .WithOrigins("https://app.example.com")
    .AllowCredentials()
    .AllowAnyHeader()));

var app = builder.Build();
app.Use(async (context, next) =>
{
    var h = context.Response.Headers;
    h.ContentSecurityPolicy = "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'";
    h.XContentTypeOptions = "nosniff";
    h["Referrer-Policy"] = "strict-origin-when-cross-origin";
    await next();
});
app.UseCors("frontend");
app.MapGet("/me", () => new { email = "ada@x.com" });

app.Urls.Add("http://127.0.0.1:5099");
await app.StartAsync();

using var client = new HttpClient();
async Task<HttpResponseMessage> Get(string origin)
{
    var request = new HttpRequestMessage(HttpMethod.Get, "http://127.0.0.1:5099/me");
    request.Headers.Add("Origin", origin);
    return await client.SendAsync(request);
}

var ours = await Get("https://app.example.com");
var evil = await Get("https://evil.example");
Check(ours.Headers.GetValues("X-Content-Type-Options").Single() == "nosniff", "security headers");
Check(ours.Headers.GetValues("Access-Control-Allow-Origin").Single() == "https://app.example.com", "allowed origin");
Check(!evil.Headers.Contains("Access-Control-Allow-Origin"), "evil origin not allowed");
Check((await evil.Content.ReadAsStringAsync()).Contains("ada@x.com"), "CORS is not access control");
Console.WriteLine("ok: CORS policy, header middleware, and the body still reaches non-browsers");
await app.StopAsync();

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }
