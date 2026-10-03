// Checks: the same results as every other language.
using System.Buffers.Binary;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
static byte[] PngHeader(uint w, uint h)
{
    var b = new byte[29];
    new byte[] { 0x89, (byte)'P', (byte)'N', (byte)'G', 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13, (byte)'I', (byte)'H', (byte)'D', (byte)'R' }.CopyTo(b, 0);
    BinaryPrimitives.WriteUInt32BigEndian(b.AsSpan(16), w);
    BinaryPrimitives.WriteUInt32BigEndian(b.AsSpan(20), h);
    return b;
}

static byte[] JpegHeader(ushort w, ushort h)
{
    byte[] head = [0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, (byte)'J', (byte)'F', (byte)'I', (byte)'F', 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0xff, 0xc0, 0x00, 0x11, 0x08];
    var size = new byte[4];
    BinaryPrimitives.WriteUInt16BigEndian(size, h);
    BinaryPrimitives.WriteUInt16BigEndian(size.AsSpan(2), w);
    return [.. head, .. size, 3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1];
}

Check(Multimodal.Sniff(PngHeader(1200, 800)) == new ImageInfo("image/png", 1200, 800), "png");
Check(Multimodal.Sniff(JpegHeader(4000, 3000)) == new ImageInfo("image/jpeg", 4000, 3000), "jpeg");
Check(Multimodal.Sniff([(byte)'G', (byte)'I', (byte)'F', (byte)'8', (byte)'9', (byte)'a', 0x40, 0x01, 0xf0, 0x00]) == new ImageInfo("image/gif", 320, 240), "gif");
Check(Multimodal.Sniff("#!/bin/sh\nrm -rf /\n"u8.ToArray()) is null && Multimodal.Sniff("<svg onload=alert(1)>"u8.ToArray()) is null, "refused");

Check(Multimodal.Fit(4000, 3000, Multimodal.HighRes) == new Fitted(2187, 1640, 4783), Multimodal.Fit(4000, 3000, Multimodal.HighRes));
Check(Multimodal.Fit(4000, 3000, Multimodal.Standard) == new Fitted(1264, 948, 1598), "standard");
var (sw, sh) = Multimodal.ShrinkTo(4000, 3000, 1024);
Check(Multimodal.Fit(sw, sh, Multimodal.HighRes) == new Fitted(1024, 768, 1049), "shrunk");
Check(Multimodal.Fit(1920, 1080, Multimodal.HighRes) == new Fitted(1920, 1080, 2765), "screenshot");

var png = PngHeader(4, 4);
var data = Convert.ToBase64String(png);
Check(Multimodal.ImageMessage(png, "What is this?", "anthropic")["content"]![0]!.ToJsonString() ==
    $$$"""{"type":"image","source":{"type":"base64","media_type":"image/png","data":"{{{data}}}"}}""", "anthropic");
Check(Multimodal.ImageMessage(png, "What is this?", "openai")["content"]![1]!["image_url"]!["url"]!.GetValue<string>() == $"data:image/png;base64,{data}", "openai");
Check(Multimodal.ImageMessage(png, "What is this?", "ollama").ToJsonString() == $$"""{"role":"user","content":"What is this?","images":["{{data}}"]}""", "ollama");

const string Good = """{"vendor":"Paper Co","invoice_number":"INV-7","currency":"GBP","due_date":"2026-10-15","line_items":[{"description":"A4 paper","amount_cents":1250},{"description":"Pens","amount_cents":480}],"total_cents":1730}""";
static Func<byte[], string, Task<string>> Reply(string text) => (_, _) => Task.FromResult($"Here you go: {text}");
Check((await Multimodal.ExtractInvoice(Reply(Good), png)).Invoice?.TotalCents == 1730, "good");
Check((await Multimodal.ExtractInvoice(Reply(Good.Replace("\"total_cents\":1730", "\"total_cents\":1780")), png)).Reason
    == "line items add up to 1730 cents but total_cents is 1780", "misread");
Check((await Multimodal.ExtractInvoice(Reply("""{"unreadable": "due_date"}"""), png)).Reason == "unreadable: due_date", "unreadable");
Check((await Multimodal.ExtractInvoice((_, _) => Task.FromResult("I can't see an invoice."), png)).Reason == "no JSON in the reply", "no JSON");
Check((await Multimodal.ExtractInvoice(Reply(Good), "%PDF-1.7"u8.ToArray())).Reason == "not a supported image", "pdf");

Console.WriteLine("all multimodal checks passed");
