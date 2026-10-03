// Checks: the same results as every other language.
using System.Net;
using System.Net.Sockets;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

Check(Convert.ToHexStringLower(DnsWire.EncodeName("www.example.com")) == "03777777076578616d706c6503636f6d00", "name");
Check(DnsWire.BuildQuery(0xbeef, "example.com", DnsWire.A).Length == 29, "query length");

var zone = new Dictionary<string, List<Rec>>
{
    ["example.com"] = [new(DnsWire.A, 300, "93.184.216.34")],
    ["www.example.com"] = [new(DnsWire.CName, 3600, "example.com")],
    ["big.example.com"] = [.. Enumerable.Range(1, 40).Select(i => new Rec(DnsWire.A, 60, $"10.0.0.{i}"))],
};
using var server = DnsWire.Serve(zone);
var port = ((IPEndPoint)server.Client.LocalEndPoint!).Port;

async Task<Message> Ask(ushort id, string name)
{
    using var client = new UdpClient();
    await client.SendAsync(DnsWire.BuildQuery(id, name, DnsWire.A), new IPEndPoint(IPAddress.Loopback, port));
    using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(2));
    return DnsWire.Parse((await client.ReceiveAsync(timeout.Token)).Buffer);
}

var reply = await Ask(42, "www.example.com");
Check(reply.Id == 42 && reply.Authoritative, reply);
Check(reply.Answers.SequenceEqual([new Answer("www.example.com", DnsWire.CName, 3600, "example.com"), new Answer("example.com", DnsWire.A, 300, "93.184.216.34")]), string.Join(", ", reply.Answers));
Check((await Ask(43, "nope.example.com")).Rcode == 3, "NXDOMAIN");
var big = await Ask(7, "big.example.com");
Check(big.Truncated && big.Answers.Count == 0, "truncated");

string[] search = ["default.svc.cluster.local", "svc.cluster.local", "cluster.local"];
var candidates = DnsWire.SearchCandidates("api.example.com", 5, search);
Check(candidates.Count == 4 && candidates[^1] == "api.example.com", candidates.Count);
Check(DnsWire.SearchCandidates("api.example.com.", 5, search).SequenceEqual(["api.example.com"]), "trailing dot");
Console.WriteLine("all dns checks passed");
