package dns;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.HexFormat;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;
import javax.naming.NameNotFoundException;
import javax.naming.directory.InitialDirContext;

/** The same checks as every other language. Run with -ea. */
public final class DnsCheck {
    private DnsCheck() {}

    static Dns.Message ask(int port, int id, String name) throws Exception {
        try (var client = new DatagramSocket()) {
            byte[] query = Dns.buildQuery(id, name, Dns.A);
            client.send(new DatagramPacket(query, query.length, InetAddress.getLoopbackAddress(), port));
            byte[] buf = new byte[4096];
            var packet = new DatagramPacket(buf, buf.length);
            client.setSoTimeout(2000);
            client.receive(packet);
            return Dns.parse(buf, packet.getLength());
        }
    }

    public static void main(String[] args) throws Exception {
        assert HexFormat.of().formatHex(Dns.encodeName("www.example.com")).equals("03777777076578616d706c6503636f6d00");
        assert Dns.buildQuery(0xbeef, "example.com", Dns.A).length == 29;

        var zone = Map.of(
                "example.com", List.of(new Dns.Rec(Dns.A, 300, "93.184.216.34")),
                "www.example.com", List.of(new Dns.Rec(Dns.CNAME, 3600, "example.com")),
                "big.example.com", IntStream.rangeClosed(1, 40).mapToObj(i -> new Dns.Rec(Dns.A, 60, "10.0.0." + i)).toList());
        try (var server = Dns.serve(zone)) {
            int port = server.getLocalPort();
            var reply = ask(port, 42, "www.example.com");
            assert reply.id() == 42 && reply.authoritative();
            assert reply.answers().equals(List.of(
                    new Dns.Answer("www.example.com", Dns.CNAME, 3600, "example.com"),
                    new Dns.Answer("example.com", Dns.A, 300, "93.184.216.34"))) : reply.answers();
            assert ask(port, 43, "nope.example.com").rcode() == 3;
            var big = ask(port, 7, "big.example.com");
            assert big.truncated() && big.answers().isEmpty();

            // Java's JNDI DNS provider can query any server: the JDK's own DNS client, pointed at ours.
            var env = new Hashtable<String, String>();
            env.put("java.naming.factory.initial", "com.sun.jndi.dns.DnsContextFactory");
            env.put("java.naming.provider.url", "dns://127.0.0.1:" + port);
            var ctx = new InitialDirContext(env);
            assert ctx.getAttributes("example.com", new String[] {"A"}).get("A").get().equals("93.184.216.34");
            try {
                ctx.getAttributes("nope.example.com", new String[] {"A"});
                throw new AssertionError("expected NXDOMAIN");
            } catch (NameNotFoundException expected) {
                // NXDOMAIN, as an exception
            }
            ctx.close();
        }

        var search = List.of("default.svc.cluster.local", "svc.cluster.local", "cluster.local");
        assert Dns.searchCandidates("api.example.com", 5, search).size() == 4;
        assert Dns.searchCandidates("api.example.com", 5, search).getLast().equals("api.example.com");
        assert Dns.searchCandidates("api.example.com.", 5, search).equals(List.of("api.example.com"));
        System.out.println("all dns checks passed");
    }
}
