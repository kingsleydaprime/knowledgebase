// What an uploaded file really is, what an image costs, the three providers' formats, and checked extraction.
// The same results as the TypeScript lab; links the structured-output lab's Invoices.Parse.
using System.Buffers.Binary;
using System.Text.Json;
using System.Text.Json.Nodes;

public sealed record ImageInfo(string Type, int Width, int Height);
public sealed record Limits(double MaxLongEdge, double MaxTokens);
public sealed record Fitted(int Width, int Height, int Tokens);

public static class Multimodal
{
    static ReadOnlySpan<byte> PngSignature => [0x89, (byte)'P', (byte)'N', (byte)'G', 0x0d, 0x0a, 0x1a, 0x0a];

    /// <summary>The type from the file's first bytes, never its name or Content-Type. Null if it isn't a supported image.</summary>
    public static ImageInfo? Sniff(byte[] b)
    {
        var s = b.AsSpan();
        if (s.StartsWith(PngSignature) && s.Length >= 24)
            return new("image/png", (int)BinaryPrimitives.ReadUInt32BigEndian(s[16..]), (int)BinaryPrimitives.ReadUInt32BigEndian(s[20..]));
        if (s.StartsWith((ReadOnlySpan<byte>)[0xff, 0xd8, 0xff])) return Jpeg(s);
        if (s.StartsWith("GIF8"u8) && s.Length >= 10)
            return new("image/gif", BinaryPrimitives.ReadUInt16LittleEndian(s[6..]), BinaryPrimitives.ReadUInt16LittleEndian(s[8..]));
        if (s.StartsWith("RIFF"u8) && s.Length >= 12 && s[8..12].SequenceEqual("WEBP"u8)) return new("image/webp", 0, 0);
        return null;
    }

    static ImageInfo Jpeg(ReadOnlySpan<byte> s)
    {
        for (var i = 2; i + 9 < s.Length && s[i] == 0xff;)
        {
            var marker = s[i + 1];
            if (marker is >= 0xc0 and <= 0xcf and not (0xc4 or 0xc8 or 0xcc))
                return new("image/jpeg", BinaryPrimitives.ReadUInt16BigEndian(s[(i + 7)..]), BinaryPrimitives.ReadUInt16BigEndian(s[(i + 5)..]));
            i += 2 + BinaryPrimitives.ReadUInt16BigEndian(s[(i + 2)..]);
        }
        return new("image/jpeg", 0, 0);
    }

    public static readonly Limits HighRes = new(2576, 4784); // Anthropic, 2026-10: Opus 4.7+ and Sonnet 5+
    public static readonly Limits Standard = new(1568, 1600); // earlier models

    /// <summary>Scaled to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation).</summary>
    public static Fitted Fit(double width, double height, Limits l)
    {
        var scale = Math.Min(1, l.MaxLongEdge / Math.Max(width, height));
        var tokens = width * scale * (height * scale) / 750;
        if (tokens > l.MaxTokens) scale *= Math.Sqrt(l.MaxTokens / tokens);
        double w = Math.Floor(width * scale), h = Math.Floor(height * scale);
        return new((int)w, (int)h, (int)Math.Ceiling(w * h / 750));
    }

    /// <summary>MidpointRounding.AwayFromZero, because .NET's Math.Round rounds 0.5 to even by default.</summary>
    public static (double, double) ShrinkTo(double width, double height, double longEdge)
    {
        var s = Math.Min(1, longEdge / Math.Max(width, height));
        return (Math.Round(width * s, MidpointRounding.AwayFromZero), Math.Round(height * s, MidpointRounding.AwayFromZero));
    }

    public static JsonObject ImageMessage(byte[] b, string question, string provider)
    {
        var info = Sniff(b) ?? throw new ArgumentException("not a supported image");
        var data = Convert.ToBase64String(b);
        return provider switch
        {
            "anthropic" => new JsonObject
            {
                ["role"] = "user",
                ["content"] = new JsonArray(
                    new JsonObject { ["type"] = "image", ["source"] = new JsonObject { ["type"] = "base64", ["media_type"] = info.Type, ["data"] = data } },
                    new JsonObject { ["type"] = "text", ["text"] = question }),
            },
            "openai" => new JsonObject
            {
                ["role"] = "user",
                ["content"] = new JsonArray(
                    new JsonObject { ["type"] = "text", ["text"] = question },
                    new JsonObject { ["type"] = "image_url", ["image_url"] = new JsonObject { ["url"] = $"data:{info.Type};base64,{data}" } }),
            },
            _ => new JsonObject { ["role"] = "user", ["content"] = question, ["images"] = new JsonArray(data) }, // Ollama's own /api/chat
        };
    }

    public const string ExtractPrompt = """
        Read this invoice and reply with JSON only, in the invoice schema.
        If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.
        """;

    /// <summary>Image in, checked data out. The structured-output lab's Parse checks shape and arithmetic.</summary>
    public static async Task<(Invoice? Invoice, string? Reason)> ExtractInvoice(Func<byte[], string, Task<string>> see, byte[] b)
    {
        if (Sniff(b) is null) return (null, "not a supported image");
        var reply = await see(b, ExtractPrompt);
        int start = reply.IndexOf('{'), end = reply.LastIndexOf('}');
        if (start == -1 || end < start) return (null, "no JSON in the reply");
        try
        {
            if (JsonNode.Parse(reply[start..(end + 1)]) is JsonObject probe && probe["unreadable"]?.GetValue<string>() is { } field)
                return (null, $"unreadable: {field}");
            return (Invoices.Parse(reply), null);
        }
        catch (Exception e) when (e is FormatException or JsonException)
        {
            return (null, e.Message);
        }
    }
}
