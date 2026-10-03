package tls;

import java.io.FileInputStream;
import java.math.BigInteger;
import java.net.InetAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.KeyStore;
import java.security.cert.CertificateExpiredException;
import java.security.cert.CertificateFactory;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import javax.crypto.AEADBadTagException;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLHandshakeException;
import javax.net.ssl.SSLServerSocket;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.TrustManagerFactory;

/** The same checks as every other language. Run with -ea and the certificate folder as the argument. */
public final class TlsCheck {
    private TlsCheck() {}

    static BigInteger n(long x) {
        return BigInteger.valueOf(x);
    }

    public static void main(String[] args) throws Exception {
        // Diffie-Hellman by hand: both sides reach 2 without ever sending it.
        var p = n(23);
        var a = TlsMath.modPow(n(5), n(6), p).value();
        var b = TlsMath.modPow(n(5), n(15), p).value();
        assert a.equals(n(8)) && b.equals(n(19)) : a + " " + b;
        assert b.modPow(n(6), p).equals(n(2)) && a.modPow(n(15), p).equals(n(2)); // BigInteger's modPow agrees

        // Easy forwards (23 multiplications), hard backwards (54,321 tries).
        assert TlsMath.modPow(n(3), n(54_321), n(65_537)).equals(new TlsMath.Power(n(21_002), 23));
        assert TlsMath.discreteLog(3, 21_002, 65_537) == 54_321;
        var curvePrime = BigInteger.TWO.pow(255).subtract(n(19));
        assert TlsMath.modPow(n(5), curvePrime.subtract(n(2)), curvePrime).multiplications() == 508;

        // An RSA signature by hand: d is the inverse of e, and only its owner can make 588 from 65.
        var d = n(17).modInverse(n(60 * 52));
        assert d.equals(n(2753));
        var signature = n(65).modPow(d, n(3233));
        assert signature.equals(n(588)) && signature.modPow(n(17), n(3233)).equals(n(65));

        // The hand-written HKDF matches the first test vector in RFC 5869.
        var hex = HexFormat.of();
        byte[] okm = TlsMath.hkdf(hex.parseHex("0b".repeat(22)), hex.parseHex("000102030405060708090a0b0c"), hex.parseHex("f0f1f2f3f4f5f6f7f8f9"), 42);
        assert hex.formatHex(okm).equals("3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865");

        // X25519, then HKDF, then AES-GCM: the real pieces of a TLS 1.3 connection.
        var client = TlsMath.keyPair();
        var server = TlsMath.keyPair();
        byte[] secret = TlsMath.sharedSecret(client.getPrivate(), server.getPublic());
        assert Arrays.equals(secret, TlsMath.sharedSecret(server.getPrivate(), client.getPublic())) && secret.length == 32;
        byte[] transcript = "hash of every handshake message so far".getBytes(StandardCharsets.US_ASCII);
        byte[] c2s = TlsMath.deriveKey(secret, "c ap traffic", transcript);
        assert !Arrays.equals(c2s, TlsMath.deriveKey(secret, "s ap traffic", transcript));
        byte[] nonce = new byte[12];
        Arrays.fill(nonce, (byte) 1);
        byte[] header = {23, 3, 3, 0, 40};
        byte[] sealed = TlsMath.seal(c2s, nonce, "GET / HTTP/1.1".getBytes(StandardCharsets.US_ASCII), header);
        assert new String(TlsMath.open(c2s, nonce, sealed, header), StandardCharsets.US_ASCII).equals("GET / HTTP/1.1");
        sealed[0] ^= 1;
        try {
            TlsMath.open(c2s, nonce, sealed, header);
            throw new AssertionError("a flipped bit must fail the tag check");
        } catch (AEADBadTagException expected) {
            // the tag no longer matches
        }

        // A real TLS 1.3 handshake, then the three checks failing one at a time.
        Path certs = Path.of(args[0]);
        assert handshake(certs, "shop.p12", "shop.test", true).equals("TLSv1.3 TLS_AES_256_GCM_SHA384 h2");
        assert handshake(certs, "shop.p12", "evil.test", true).contains("No subject alternative DNS name matching evil.test");
        assert handshake(certs, "shop.p12", "shop.test", false).contains("unable to find valid certification path");
        assert handshake(certs, "expired.p12", "shop.test", true).equals(CertificateExpiredException.class.getName());
        System.out.println("all checks passed");
    }

    /**
     * Serves one TLS connection from the keystore `serverStore` and connects to it as shop.test's client would. Returns
     * "version cipher alpn", or what the handshake failure says.
     */
    static String handshake(Path certs, String serverStore, String serverName, boolean trustLabCa) throws Exception {
        var keys = KeyStore.getInstance("PKCS12");
        try (var in = new FileInputStream(certs.resolve(serverStore).toFile())) {
            keys.load(in, "lab".toCharArray());
        }
        var keyManagers = KeyManagerFactory.getInstance("PKIX");
        keyManagers.init(keys, "lab".toCharArray());
        var serverContext = SSLContext.getInstance("TLS");
        serverContext.init(keyManagers.getKeyManagers(), null, null);

        var clientContext = SSLContext.getInstance("TLS");
        if (trustLabCa) {
            var trusted = KeyStore.getInstance("PKCS12");
            trusted.load(null, null);
            try (var in = new FileInputStream(certs.resolve("ca.crt").toFile())) {
                trusted.setCertificateEntry("lab", CertificateFactory.getInstance("X.509").generateCertificate(in));
            }
            var trustManagers = TrustManagerFactory.getInstance("PKIX");
            trustManagers.init(trusted);
            clientContext.init(null, trustManagers.getTrustManagers(), null);
        } else {
            clientContext.init(null, null, null); // the JDK's own trust store, which has never heard of the lab CA
        }

        try (var listener = (SSLServerSocket) serverContext.getServerSocketFactory().createServerSocket(0, 1, InetAddress.getLoopbackAddress())) {
            var params = listener.getSSLParameters();
            params.setApplicationProtocols(new String[] {"h2", "http/1.1"});
            listener.setSSLParameters(params);
            var serving = Thread.ofVirtual().start(() -> {
                try (var conn = (SSLSocket) listener.accept()) {
                    conn.startHandshake();
                } catch (Exception rejected) {
                    // the client hangs up when it rejects the certificate
                }
            });
            try (var raw = new Socket(InetAddress.getLoopbackAddress(), listener.getLocalPort());
                    var tls = (SSLSocket) clientContext.getSocketFactory().createSocket(raw, serverName, raw.getPort(), true)) {
                var clientParams = tls.getSSLParameters();
                clientParams.setEndpointIdentificationAlgorithm("HTTPS"); // check the name; off by default on a raw SSLSocket
                clientParams.setApplicationProtocols(new String[] {"h2", "http/1.1"});
                tls.setSSLParameters(clientParams);
                tls.startHandshake();
                var session = tls.getSession();
                return String.join(" ", List.of(session.getProtocol(), session.getCipherSuite(), tls.getApplicationProtocol()));
            } catch (SSLHandshakeException failed) {
                for (Throwable cause = failed; cause != null; cause = cause.getCause()) {
                    if (cause instanceof CertificateExpiredException) return cause.getClass().getName();
                }
                return failed.getMessage();
            } finally {
                serving.join();
            }
        }
    }
}
