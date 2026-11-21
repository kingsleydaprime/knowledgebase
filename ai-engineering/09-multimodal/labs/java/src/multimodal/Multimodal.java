package multimodal;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import invoice.Invoices;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;
import java.util.function.BiFunction;

/** What an uploaded file really is, what an image costs, the three providers' formats, and checked extraction.
 *  The same results as the TypeScript lab; reuses the structured-output lab's Invoices.parse. */
public final class Multimodal {
    private Multimodal() {}

    static final ObjectMapper JSON = new ObjectMapper();

    /** type is null when the bytes aren't a supported image; width and height are 0 when unknown. */
    public record Info(String type, int width, int height) {}

    static final byte[] PNG_SIGNATURE = {(byte) 0x89, 'P', 'N', 'G', '\r', '\n', 0x1a, '\n'};

    static boolean startsWith(byte[] b, byte... prefix) {
        return b.length >= prefix.length && Arrays.equals(Arrays.copyOf(b, prefix.length), prefix);
    }

    static boolean startsWith(byte[] b, String prefix) {
        return startsWith(b, prefix.getBytes(StandardCharsets.ISO_8859_1));
    }

    /** The type from the file's first bytes, never its name or Content-Type. */
    public static Info sniff(byte[] b) {
        if (startsWith(b, PNG_SIGNATURE) && b.length >= 24) {
            var be = ByteBuffer.wrap(b); // big-endian by default
            return new Info("image/png", be.getInt(16), be.getInt(20));
        }
        if (startsWith(b, (byte) 0xff, (byte) 0xd8, (byte) 0xff)) return jpeg(b);
        if (startsWith(b, "GIF8") && b.length >= 10) {
            var le = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN);
            return new Info("image/gif", le.getShort(6) & 0xffff, le.getShort(8) & 0xffff); // Java has no unsigned short
        }
        if (startsWith(b, "RIFF") && b.length >= 12 && new String(b, 8, 4, StandardCharsets.ISO_8859_1).equals("WEBP")) return new Info("image/webp", 0, 0);
        return new Info(null, 0, 0);
    }

    static Info jpeg(byte[] b) {
        var be = ByteBuffer.wrap(b);
        for (int i = 2; i + 9 < b.length; ) {
            if ((b[i] & 0xff) != 0xff) break;
            int marker = b[i + 1] & 0xff, length = be.getShort(i + 2) & 0xffff;
            if (marker >= 0xc0 && marker <= 0xcf && marker != 0xc4 && marker != 0xc8 && marker != 0xcc) {
                return new Info("image/jpeg", be.getShort(i + 7) & 0xffff, be.getShort(i + 5) & 0xffff);
            }
            i += 2 + length;
        }
        return new Info("image/jpeg", 0, 0);
    }

    public record Limits(double maxLongEdge, double maxTokens) {}

    public static final Limits HIGH_RES = new Limits(2576, 4784); // Anthropic, 2026-10: Opus 4.7+ and Sonnet 5+
    public static final Limits STANDARD = new Limits(1568, 1600); // earlier models

    public record Fitted(int width, int height, int tokens) {}

    /** Scaled to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation). */
    public static Fitted fit(double width, double height, Limits l) {
        double scale = Math.min(1, l.maxLongEdge() / Math.max(width, height));
        double tokens = width * scale * (height * scale) / 750;
        if (tokens > l.maxTokens()) scale *= Math.sqrt(l.maxTokens() / tokens);
        double w = Math.floor(width * scale), h = Math.floor(height * scale);
        return new Fitted((int) w, (int) h, (int) Math.ceil(w * h / 750));
    }

    public static double[] shrinkTo(double width, double height, double longEdge) {
        double s = Math.min(1, longEdge / Math.max(width, height));
        return new double[] {Math.round(width * s), Math.round(height * s)};
    }

    public static ObjectNode imageMessage(byte[] b, String question, String provider) {
        var info = sniff(b);
        if (info.type() == null) throw new IllegalArgumentException("not a supported image");
        String data = Base64.getEncoder().encodeToString(b);
        var message = JSON.createObjectNode().put("role", "user");
        switch (provider) {
            case "anthropic" -> {
                var content = message.putArray("content");
                content.addObject().put("type", "image").putObject("source").put("type", "base64").put("media_type", info.type()).put("data", data);
                content.addObject().put("type", "text").put("text", question);
            }
            case "openai" -> {
                var content = message.putArray("content");
                content.addObject().put("type", "text").put("text", question);
                content.addObject().put("type", "image_url").putObject("image_url").put("url", "data:" + info.type() + ";base64," + data);
            }
            default -> message.put("content", question).putArray("images").add(data); // Ollama's own /api/chat
        }
        return message;
    }

    public static final String EXTRACT_PROMPT = """
            Read this invoice and reply with JSON only, in the invoice schema.
            If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.""";

    /** invoice is null when the extraction failed, and reason says why. */
    public record Extracted(Invoices.Invoice invoice, String reason) {}

    /** Image in, checked data out. The structured-output lab's parse checks shape and arithmetic. */
    public static Extracted extractInvoice(BiFunction<byte[], String, String> see, byte[] b) {
        if (sniff(b).type() == null) return new Extracted(null, "not a supported image");
        String reply = see.apply(b, EXTRACT_PROMPT);
        int start = reply.indexOf('{'), end = reply.lastIndexOf('}');
        if (start == -1 || end < start) return new Extracted(null, "no JSON in the reply");
        try {
            JsonNode probe = JSON.readTree(reply.substring(start, end + 1));
            if (probe.has("unreadable")) return new Extracted(null, "unreadable: " + probe.get("unreadable").asText());
        } catch (Exception e) {
            return new Extracted(null, "no JSON in the reply");
        }
        try {
            return new Extracted(Invoices.parse(reply), null);
        } catch (IllegalArgumentException e) {
            return new Extracted(null, e.getMessage());
        }
    }
}
