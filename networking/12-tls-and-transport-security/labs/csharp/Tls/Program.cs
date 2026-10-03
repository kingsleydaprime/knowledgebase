// Checks: the same results as every other language. The argument is the folder make-certs.sh filled.
using System.Net;
using System.Net.Security;
using System.Net.Sockets;
using System.Numerics;
using System.Security.Authentication;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Diffie-Hellman by hand: both sides reach 2 without ever sending it.
var (a, b) = (TlsMath.ModPow(5, 6, 23).Value, TlsMath.ModPow(5, 15, 23).Value);
Check((a, b) == (8, 19), (a, b));
Check(BigInteger.ModPow(b, 6, 23) == 2 && BigInteger.ModPow(a, 15, 23) == 2, "shared"); // the built-in agrees

// Easy forwards (23 multiplications), hard backwards (54,321 tries).
Check(TlsMath.ModPow(3, 54_321, 65_537) == (21_002, 23), "mod pow");
Check(TlsMath.DiscreteLog(3, 21_002, 65_537) == 54_321, "discrete log");
var curvePrime = BigInteger.Pow(2, 255) - 19;
Check(TlsMath.ModPow(5, curvePrime - 2, curvePrime).Multiplications == 508, "255-bit exponent");

// An RSA signature by hand: d is the inverse of e, and only its owner can make 588 from 65.
var d = TlsMath.ModInverse(17, 60 * 52);
var signature = BigInteger.ModPow(65, d, 3233);
Check((d, signature, BigInteger.ModPow(signature, 17, 3233)) == (2753, 588, 65), (d, signature));

// ECDH, then HKDF, then AES-GCM: the real pieces of a TLS 1.3 connection.
using var client = ECDiffieHellman.Create(ECCurve.NamedCurves.nistP256);
using var server = ECDiffieHellman.Create(ECCurve.NamedCurves.nistP256);
var secret = client.DeriveRawSecretAgreement(server.PublicKey);
Check(secret.SequenceEqual(server.DeriveRawSecretAgreement(client.PublicKey)) && secret.Length == 32, "ECDH");
var transcript = Encoding.ASCII.GetBytes("hash of every handshake message so far");
var c2s = TlsMath.DeriveKey(secret, "c ap traffic", transcript);
Check(!c2s.SequenceEqual(TlsMath.DeriveKey(secret, "s ap traffic", transcript)), "one key per direction");
var nonce = Enumerable.Repeat((byte)1, 12).ToArray();
byte[] header = [23, 3, 3, 0, 40];
var sealedBytes = TlsMath.Seal(c2s, nonce, Encoding.ASCII.GetBytes("GET / HTTP/1.1"), header);
Check(Encoding.ASCII.GetString(TlsMath.Open(c2s, nonce, sealedBytes, header)) == "GET / HTTP/1.1", "open");
sealedBytes[0] ^= 1;
try
{
    TlsMath.Open(c2s, nonce, sealedBytes, header);
    Check(false, "a flipped bit must fail the tag check");
}
catch (AuthenticationTagMismatchException)
{
    // the tag no longer matches
}

// A real TLS 1.3 handshake, then the three checks failing one at a time.
var certs = args[0];
Expect(await Handshake("shop.crt", "shop.test", true), "Tls13 TLS_AES_256_GCM_SHA384 h2");
Expect(await Handshake("shop.crt", "evil.test", true), "RemoteCertificateNameMismatch");
Expect(await Handshake("shop.crt", "shop.test", false), "RemoteCertificateChainErrors PartialChain");
Expect(await Handshake("expired.crt", "shop.test", true), "RemoteCertificateChainErrors NotTimeValid");
Console.WriteLine("all checks passed");

static void Expect(string got, string want) => Check(got == want, $"got \"{got}\", want \"{want}\"");

// Serves one TLS connection with `certFile` and connects to it. Returns "version cipher alpn", or what the client's
// certificate check found wrong.
async Task<string> Handshake(string certFile, string serverName, bool trustLabCa)
{
    using var cert = X509Certificate2.CreateFromPemFile(Path.Combine(certs, certFile), Path.Combine(certs, "shop.key"));
    using var listener = new TcpListener(IPAddress.Loopback, 0);
    listener.Start();
    var serving = Task.Run(async () =>
    {
        using var conn = await listener.AcceptTcpClientAsync();
        await using var tls = new SslStream(conn.GetStream());
        try
        {
            await tls.AuthenticateAsServerAsync(new SslServerAuthenticationOptions
            {
                ServerCertificate = cert,
                ApplicationProtocols = [SslApplicationProtocol.Http2, SslApplicationProtocol.Http11],
            });
        }
        catch (Exception e) when (e is AuthenticationException or IOException)
        {
            // the client hangs up when it rejects the certificate
        }
    });

    var problem = "";
    var options = new SslClientAuthenticationOptions
    {
        TargetHost = serverName,
        // .NET asks for revocation status by default, and the lab CA publishes no revocation list to ask.
        CertificateRevocationCheckMode = X509RevocationMode.NoCheck,
        ApplicationProtocols = [SslApplicationProtocol.Http2, SslApplicationProtocol.Http11],
        RemoteCertificateValidationCallback = (_, _, chain, errors) =>
        {
            var statuses = chain?.ChainStatus.Select(s => s.Status.ToString()) ?? [];
            problem = string.Join(" ", new[] { errors.ToString() }.Concat(statuses));
            return errors == SslPolicyErrors.None;
        },
    };
    if (trustLabCa)
    {
        options.CertificateChainPolicy = new X509ChainPolicy { TrustMode = X509ChainTrustMode.CustomRootTrust, RevocationMode = X509RevocationMode.NoCheck };
        options.CertificateChainPolicy.CustomTrustStore.Add(X509CertificateLoader.LoadCertificateFromFile(Path.Combine(certs, "ca.crt")));
    } // otherwise the system's trust store, which has never heard of the lab CA
    using var tcp = new TcpClient();
    await tcp.ConnectAsync(IPAddress.Loopback, ((IPEndPoint)listener.LocalEndpoint).Port);
    await using var tls = new SslStream(tcp.GetStream());
    try
    {
        await tls.AuthenticateAsClientAsync(options);
        return $"{tls.SslProtocol} {tls.NegotiatedCipherSuite} {tls.NegotiatedApplicationProtocol}";
    }
    catch (AuthenticationException)
    {
        return problem;
    }
    finally
    {
        tcp.Close();
        await serving;
    }
}
