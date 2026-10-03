// DNS on the wire with BinaryPrimitives, and a tiny authoritative UDP server. The same results as the TypeScript
// lab. (.NET's Dns class always asks the operating system; DnsClient.NET can ask any server.)
using System.Buffers.Binary;
using System.Net;
using System.Net.Sockets;
using System.Text;

public record Answer(string Name, ushort Type, uint Ttl, string Data);

public record Message(ushort Id, bool Truncated, bool Authoritative, int Rcode, string Question, ushort QType, List<Answer> Answers);

public record Rec(ushort Type, uint Ttl, string Data);

public static class DnsWire
{
    public const ushort A = 1, CName = 5;

    public static byte[] EncodeName(string name)
    {
        var out_ = new List<byte>();
        foreach (var label in name.TrimEnd('.').Split('.', StringSplitOptions.RemoveEmptyEntries))
        {
            if (label.Length > 63) throw new ArgumentException($"label too long: {label}");
            out_.Add((byte)label.Length);
            out_.AddRange(Encoding.ASCII.GetBytes(label));
        }
        out_.Add(0);
        return [.. out_];
    }

    static byte[] U16(ushort v)
    {
        var b = new byte[2];
        BinaryPrimitives.WriteUInt16BigEndian(b, v); // network byte order, whatever the machine's
        return b;
    }

    public static byte[] BuildQuery(ushort id, string name, ushort type) =>
        [.. U16(id), .. U16(0x0100), .. U16(1), 0, 0, 0, 0, 0, 0, .. EncodeName(name), .. U16(type), .. U16(1)];

    public static (string Name, int End) ReadName(ReadOnlySpan<byte> buf, int offset)
    {
        var labels = new List<string>();
        var end = -1;
        for (var jumps = 0; ;)
        {
            int length = buf[offset];
            if (length == 0) return (string.Join('.', labels), end == -1 ? offset + 1 : end);
            if ((length & 0xc0) == 0xc0)
            {
                if (end == -1) end = offset + 2;
                offset = BinaryPrimitives.ReadUInt16BigEndian(buf[offset..]) & 0x3fff;
                if (++jumps > 20) throw new InvalidDataException("compression loop");
                continue;
            }
            labels.Add(Encoding.ASCII.GetString(buf.Slice(offset + 1, length)));
            offset += 1 + length;
        }
    }

    public static Message Parse(ReadOnlySpan<byte> buf)
    {
        var flags = BinaryPrimitives.ReadUInt16BigEndian(buf[2..]);
        var (qname, offset) = ReadName(buf, 12);
        var qtype = BinaryPrimitives.ReadUInt16BigEndian(buf[offset..]);
        offset += 4;
        var answers = new List<Answer>();
        for (var i = 0; i < BinaryPrimitives.ReadUInt16BigEndian(buf[6..]); i++)
        {
            var (name, next) = ReadName(buf, offset);
            var type = BinaryPrimitives.ReadUInt16BigEndian(buf[next..]);
            var ttl = BinaryPrimitives.ReadUInt32BigEndian(buf[(next + 4)..]);
            var length = BinaryPrimitives.ReadUInt16BigEndian(buf[(next + 8)..]);
            var rdata = next + 10;
            var data = type == A ? new IPAddress(buf.Slice(rdata, 4)).ToString() : ReadName(buf, rdata).Name;
            answers.Add(new Answer(name, type, ttl, data));
            offset = rdata + length;
        }
        return new Message(BinaryPrimitives.ReadUInt16BigEndian(buf), (flags & 0x0200) != 0, (flags & 0x0400) != 0, flags & 0xf, qname, qtype, answers);
    }

    /// <summary>Serves zone on 127.0.0.1 until the returned client is disposed.</summary>
    public static UdpClient Serve(IReadOnlyDictionary<string, List<Rec>> zone)
    {
        var server = new UdpClient(new IPEndPoint(IPAddress.Loopback, 0));
        _ = Task.Run(async () =>
        {
            while (true)
            {
                UdpReceiveResult received;
                try { received = await server.ReceiveAsync(); }
                catch (ObjectDisposedException) { return; }
                var buf = received.Buffer;
                var query = Parse(buf);
                var name = query.Question.ToLowerInvariant();
                var body = new List<byte>();
                var count = 0;
                void Add(string owner, Rec r)
                {
                    if (r.Type != query.QType && r.Type != CName) return;
                    byte[] rdata = r.Type == A ? IPAddress.Parse(r.Data).GetAddressBytes() : EncodeName(r.Data);
                    var ttl = new byte[4];
                    BinaryPrimitives.WriteUInt32BigEndian(ttl, r.Ttl);
                    body.AddRange([.. EncodeName(owner), .. U16(r.Type), .. U16(1), .. ttl, .. U16((ushort)rdata.Length), .. rdata]);
                    count++;
                }
                foreach (var r in zone.GetValueOrDefault(name) ?? [])
                {
                    Add(name, r);
                    if (r.Type == CName && query.QType != CName)
                        foreach (var target in zone.GetValueOrDefault(r.Data) ?? []) Add(r.Data, target);
                }
                var questionEnd = ReadName(buf, 12).End + 4; // exactly the question; anything after it (EDNS0) is dropped
                var truncated = questionEnd + body.Count > 512;
                var flags = (ushort)(0x8400 | (truncated ? 0x0200 : 0) | (zone.ContainsKey(name) ? 0 : 3));
                byte[] reply = [.. U16(query.Id), .. U16(flags), .. U16(1), .. U16((ushort)(truncated ? 0 : count)), 0, 0, 0, 0, .. buf[12..questionEnd], .. (truncated ? [] : body)];
                await server.SendAsync(reply, received.RemoteEndPoint);
            }
        });
        return server;
    }

    public static List<string> SearchCandidates(string name, int ndots, IEnumerable<string> search)
    {
        if (name.EndsWith('.')) return [name[..^1]];
        var expanded = search.Select(d => $"{name}.{d}").ToList();
        return name.Count(c => c == '.') >= ndots ? [name, .. expanded] : [.. expanded, name];
    }
}
