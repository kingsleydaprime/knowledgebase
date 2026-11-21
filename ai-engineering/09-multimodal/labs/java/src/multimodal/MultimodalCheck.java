package multimodal;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import multimodal.Multimodal.Fitted;
import multimodal.Multimodal.Info;

/** Checks, run with `java -ea`. The same results as every other language. */
public final class MultimodalCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    /** Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.) */
    static byte[] pngHeader(int w, int h) {
        return ByteBuffer.allocate(29).put(Multimodal.PNG_SIGNATURE)
                .putInt(13).put("IHDR".getBytes(StandardCharsets.ISO_8859_1)).putInt(w).putInt(h).put(new byte[] {8, 0, 0, 0, 0}).array();
    }

    static byte[] jpegHeader(int w, int h) {
        var b = ByteBuffer.allocate(39);
        b.put(new byte[] {(byte) 0xff, (byte) 0xd8, (byte) 0xff, (byte) 0xe0, 0, 0x10, 'J', 'F', 'I', 'F', 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, (byte) 0xff, (byte) 0xc0, 0, 0x11, 8});
        return b.putShort((short) h).putShort((short) w).put(new byte[] {3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1}).array();
    }

    public static void main(String[] args) {
        check(Multimodal.sniff(pngHeader(1200, 800)).equals(new Info("image/png", 1200, 800)), "png");
        check(Multimodal.sniff(jpegHeader(4000, 3000)).equals(new Info("image/jpeg", 4000, 3000)), Multimodal.sniff(jpegHeader(4000, 3000)));
        byte[] gif = {'G', 'I', 'F', '8', '9', 'a', 0x40, 0x01, (byte) 0xf0, 0x00}; // 320 × 240, little-endian
        check(Multimodal.sniff(gif).equals(new Info("image/gif", 320, 240)), "gif");
        check(Multimodal.sniff("#!/bin/sh\nrm -rf /\n".getBytes()).type() == null && Multimodal.sniff("<svg onload=alert(1)>".getBytes()).type() == null, "refused");

        check(Multimodal.fit(4000, 3000, Multimodal.HIGH_RES).equals(new Fitted(2187, 1640, 4783)), Multimodal.fit(4000, 3000, Multimodal.HIGH_RES));
        check(Multimodal.fit(4000, 3000, Multimodal.STANDARD).equals(new Fitted(1264, 948, 1598)), "standard");
        double[] small = Multimodal.shrinkTo(4000, 3000, 1024);
        check(Multimodal.fit(small[0], small[1], Multimodal.HIGH_RES).equals(new Fitted(1024, 768, 1049)), "shrunk");
        check(Multimodal.fit(1920, 1080, Multimodal.HIGH_RES).equals(new Fitted(1920, 1080, 2765)), "screenshot");

        byte[] png = pngHeader(4, 4);
        String data = Base64.getEncoder().encodeToString(png);
        check(Multimodal.imageMessage(png, "What is this?", "anthropic").get("content").get(0).toString()
                .equals("{\"type\":\"image\",\"source\":{\"type\":\"base64\",\"media_type\":\"image/png\",\"data\":\"" + data + "\"}}"), "anthropic");
        check(Multimodal.imageMessage(png, "What is this?", "openai").get("content").get(1).get("image_url").get("url").asText()
                .equals("data:image/png;base64," + data), "openai");
        check(Multimodal.imageMessage(png, "What is this?", "ollama").toString()
                .equals("{\"role\":\"user\",\"content\":\"What is this?\",\"images\":[\"" + data + "\"]}"), "ollama");

        String good = "{\"vendor\":\"Paper Co\",\"invoice_number\":\"INV-7\",\"currency\":\"GBP\",\"due_date\":\"2026-10-15\","
                + "\"line_items\":[{\"description\":\"A4 paper\",\"amount_cents\":1250},{\"description\":\"Pens\",\"amount_cents\":480}],\"total_cents\":1730}";
        check(Multimodal.extractInvoice((b, p) -> "Here you go: " + good, png).invoice().totalCents() == 1730, "good");
        String misread = good.replace("\"total_cents\":1730", "\"total_cents\":1780");
        check(Multimodal.extractInvoice((b, p) -> misread, png).reason().equals("line items add up to 1730 cents but total_cents is 1780"), "misread");
        check(Multimodal.extractInvoice((b, p) -> "{\"unreadable\": \"due_date\"}", png).reason().equals("unreadable: due_date"), "unreadable");
        check(Multimodal.extractInvoice((b, p) -> "I can't see an invoice.", png).reason().equals("no JSON in the reply"), "no JSON");
        check(Multimodal.extractInvoice((b, p) -> good, "%PDF-1.7".getBytes()).reason().equals("not a supported image"), "pdf");

        System.out.println("all multimodal checks passed");
    }
}
