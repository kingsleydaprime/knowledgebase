package dns;

import java.io.ByteArrayOutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** DNS on the wire with ByteBuffer, and a tiny authoritative UDP server. The same results as the TypeScript lab. */
public final class Dns {
    private Dns() {}

    public static final int A = 1;
    public static final int CNAME = 5;

    public static byte[] encodeName(String name) {
        var out = new ByteArrayOutputStream();
        for (String label : name.replaceAll("\\.$", "").split("\\.")) {
            if (label.isEmpty()) continue;
            if (label.length() > 63) throw new IllegalArgumentException("label too long: " + label);
            out.write(label.length());
            out.writeBytes(label.getBytes(StandardCharsets.US_ASCII));
        }
        out.write(0);
        return out.toByteArray();
    }

    public static byte[] buildQuery(int id, String name, int type) {
        byte[] encoded = encodeName(name);
        // ByteBuffer is big-endian by default: network byte order, as DNS wants.
        return ByteBuffer.allocate(12 + encoded.length + 4)
                .putShort((short) id).putShort((short) 0x0100).putShort((short) 1).putShort((short) 0).putShort((short) 0).putShort((short) 0)
                .put(encoded).putShort((short) type).putShort((short) 1).array();
    }

    record Name(String name, int end) {}

    static Name readName(byte[] buf, int offset) {
        var labels = new ArrayList<String>();
        int end = -1;
        for (int jumps = 0; ; ) {
            int length = buf[offset] & 0xff; // Java's byte is signed: mask to read it as 0–255
            if (length == 0) return new Name(String.join(".", labels), end == -1 ? offset + 1 : end);
            if ((length & 0xc0) == 0xc0) {
                if (end == -1) end = offset + 2;
                offset = ((length & 0x3f) << 8) | (buf[offset + 1] & 0xff);
                if (++jumps > 20) throw new IllegalStateException("compression loop");
                continue;
            }
            labels.add(new String(buf, offset + 1, length, StandardCharsets.US_ASCII));
            offset += 1 + length;
        }
    }

    public record Answer(String name, int type, long ttl, String data) {}

    public record Message(int id, boolean truncated, boolean authoritative, int rcode, String question, List<Answer> answers) {}

    public static Message parse(byte[] buf, int length) {
        var bb = ByteBuffer.wrap(buf, 0, length);
        int id = Short.toUnsignedInt(bb.getShort(0));
        int flags = Short.toUnsignedInt(bb.getShort(2));
        int count = Short.toUnsignedInt(bb.getShort(6));
        Name q = readName(buf, 12);
        int offset = q.end() + 4;
        List<Answer> answers = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            Name n = readName(buf, offset);
            int type = Short.toUnsignedInt(bb.getShort(n.end()));
            long ttl = Integer.toUnsignedLong(bb.getInt(n.end() + 4));
            int rdLength = Short.toUnsignedInt(bb.getShort(n.end() + 8));
            int rdata = n.end() + 10;
            String data = type == A
                    ? (buf[rdata] & 0xff) + "." + (buf[rdata + 1] & 0xff) + "." + (buf[rdata + 2] & 0xff) + "." + (buf[rdata + 3] & 0xff)
                    : readName(buf, rdata).name();
            answers.add(new Answer(n.name(), type, ttl, data));
            offset = rdata + rdLength;
        }
        return new Message(id, (flags & 0x0200) != 0, (flags & 0x0400) != 0, flags & 0xf, q.name(), answers);
    }

    public record Rec(int type, int ttl, String data) {}

    /** Serves `zone` on 127.0.0.1 from a virtual thread until the socket is closed. */
    public static DatagramSocket serve(Map<String, List<Rec>> zone) throws Exception {
        var socket = new DatagramSocket(0, InetAddress.getLoopbackAddress());
        Thread.ofVirtual().start(() -> {
            byte[] buf = new byte[512];
            while (!socket.isClosed()) {
                try {
                    var packet = new DatagramPacket(buf, buf.length);
                    socket.receive(packet);
                    Message query = parse(buf, packet.getLength());
                    int qtype = Short.toUnsignedInt(ByteBuffer.wrap(buf).getShort(readName(buf, 12).end()));
                    String name = query.question().toLowerCase();
                    var body = new ByteArrayOutputStream();
                    int count = 0;
                    for (Rec r : zone.getOrDefault(name, List.of())) {
                        count += write(body, name, r, qtype);
                        if (r.type() == CNAME && qtype != CNAME) {
                            for (Rec target : zone.getOrDefault(r.data(), List.of())) count += write(body, r.data(), target, qtype);
                        }
                    }
                    int questionEnd = readName(buf, 12).end() + 4; // exactly the question; anything after it (EDNS0) is dropped
                    boolean truncated = questionEnd + body.size() > 512;
                    int flags = 0x8400 | (truncated ? 0x0200 : 0) | (zone.containsKey(name) ? 0 : 3);
                    var reply = ByteBuffer.allocate(questionEnd + (truncated ? 0 : body.size()))
                            .putShort((short) query.id()).putShort((short) flags).putShort((short) 1).putShort((short) (truncated ? 0 : count))
                            .putShort((short) 0).putShort((short) 0).put(buf, 12, questionEnd - 12);
                    if (!truncated) reply.put(body.toByteArray());
                    socket.send(new DatagramPacket(reply.array(), reply.capacity(), packet.getSocketAddress()));
                } catch (Exception e) {
                    if (socket.isClosed()) return;
                }
            }
        });
        return socket;
    }

    private static int write(ByteArrayOutputStream body, String owner, Rec r, int qtype) {
        if (r.type() != qtype && r.type() != CNAME) return 0;
        byte[] rdata = r.type() == A ? ipv4(r.data()) : encodeName(r.data());
        body.writeBytes(encodeName(owner));
        body.writeBytes(ByteBuffer.allocate(10).putShort((short) r.type()).putShort((short) 1).putInt(r.ttl()).putShort((short) rdata.length).array());
        body.writeBytes(rdata);
        return 1;
    }

    private static byte[] ipv4(String address) {
        String[] parts = address.split("\\.");
        byte[] out = new byte[4];
        for (int i = 0; i < 4; i++) out[i] = (byte) Integer.parseInt(parts[i]);
        return out;
    }

    public static List<String> searchCandidates(String name, int ndots, List<String> search) {
        if (name.endsWith(".")) return List.of(name.substring(0, name.length() - 1));
        List<String> expanded = search.stream().map(d -> name + "." + d).toList();
        long dots = name.chars().filter(c -> c == '.').count();
        List<String> out = new ArrayList<>();
        if (dots >= ndots) out.add(name);
        out.addAll(expanded);
        if (dots < ndots) out.add(name);
        return out;
    }
}
