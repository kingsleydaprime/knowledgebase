import pathlib
import socket
import ssl
import subprocess
import tempfile
import threading
import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tlsmath import derive_key, discrete_log, key_pair, mod_inverse, mod_pow, open_sealed, seal

LABS = pathlib.Path(__file__).resolve().parent.parent


class Maths(unittest.TestCase):
    def test_diffie_hellman_by_hand(self):
        p, g, a, b = 23, 5, 6, 15
        A, B = mod_pow(g, a, p)[0], mod_pow(g, b, p)[0]
        self.assertEqual((A, B), (8, 19))
        self.assertEqual((pow(B, a, p), pow(A, b, p)), (2, 2))  # the built-in three-argument pow agrees

    def test_easy_forwards_hard_backwards(self):
        self.assertEqual(mod_pow(3, 54_321, 65_537), (21_002, 23))
        self.assertEqual(discrete_log(3, 21_002, 65_537), (54_321, 54_321))
        self.assertEqual(mod_pow(5, 2**255 - 21, 2**255 - 19)[1], 508)  # Python's ints have no size limit

    def test_rsa_signature_by_hand(self):
        n, e = 61 * 53, 17
        d = mod_inverse(e, 60 * 52)
        self.assertEqual((n, d), (3233, 2753))
        signature = pow(65, d, n)
        self.assertEqual((signature, pow(signature, e, n)), (588, 65))

    def test_x25519_hkdf_aes_gcm(self):
        client, server = key_pair(), key_pair()
        secret = client.exchange(server.public_key())
        self.assertEqual(secret, server.exchange(client.public_key()))
        self.assertEqual(len(client.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)), 32)
        transcript = b"hash of every handshake message so far"
        c2s, s2c = derive_key(secret, "c ap traffic", transcript), derive_key(secret, "s ap traffic", transcript)
        self.assertNotEqual(c2s, s2c)
        nonce, header = bytes([1] * 12), bytes([23, 3, 3, 0, 40])
        sealed = seal(c2s, nonce, b"GET / HTTP/1.1", header)
        self.assertEqual(open_sealed(c2s, nonce, sealed, header), b"GET / HTTP/1.1")
        tampered = bytes([sealed[0] ^ 1]) + sealed[1:]
        with self.assertRaises(InvalidTag):
            open_sealed(c2s, nonce, tampered, header)


class Handshake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.certs = pathlib.Path(cls.tmp.name)
        subprocess.run(["sh", str(LABS / "shared" / "make-certs.sh"), str(cls.certs)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def handshake(self, cert: str, server_name: str, trust_ca: bool):
        """Serves one TLS connection with `cert` and connects to it; returns what the client saw, or the error."""
        server_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        server_ctx.load_cert_chain(self.certs / cert, self.certs / "shop.key")
        server_ctx.set_alpn_protocols(["h2", "http/1.1"])
        listener = socket.create_server(("127.0.0.1", 0))
        port = listener.getsockname()[1]

        def serve():
            conn, _ = listener.accept()
            try:
                with server_ctx.wrap_socket(conn, server_side=True):
                    pass
            except (ssl.SSLError, OSError):
                pass  # the client may hang up after rejecting the certificate

        thread = threading.Thread(target=serve)
        thread.start()
        client_ctx = ssl.create_default_context(cafile=self.certs / "ca.crt" if trust_ca else None)
        client_ctx.set_alpn_protocols(["h2", "http/1.1"])
        try:
            with socket.create_connection(("127.0.0.1", port)) as raw, client_ctx.wrap_socket(raw, server_hostname=server_name) as tls:
                return {"version": tls.version(), "cipher": tls.cipher()[0], "alpn": tls.selected_alpn_protocol()}
        except ssl.SSLCertVerificationError as err:
            return {"error": err.verify_message}
        finally:
            thread.join()
            listener.close()

    def test_a_real_tls_13_handshake(self):
        result = self.handshake("shop.crt", "shop.test", True)
        self.assertEqual(result, {"version": "TLSv1.3", "cipher": "TLS_AES_256_GCM_SHA384", "alpn": "h2"})

    def test_the_three_checks_each_failing_on_its_own(self):
        self.assertIn("Hostname mismatch", self.handshake("shop.crt", "evil.test", True)["error"])
        self.assertEqual(self.handshake("shop.crt", "shop.test", False)["error"], "unable to get local issuer certificate")
        self.assertEqual(self.handshake("expired.crt", "shop.test", True)["error"], "certificate has expired")


if __name__ == "__main__":
    unittest.main()
